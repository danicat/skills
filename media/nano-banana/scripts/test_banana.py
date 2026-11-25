# Copyright 2026 Daniela Petruzalek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-genai>=3.3.0",
#     "pillow>=10.0.0",
#     "google-auth>=2.0.0",
# ]
# ///

import argparse
import base64
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

from google.genai._gaos.types.basemodel import UnrecognizedStr
from google.genai._gaos.types.interactions import CreateModelInteraction
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "banana.py")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import banana  # noqa: E402


def make_args(**overrides) -> argparse.Namespace:
    defaults = {
        "prompt": "A 2D side-scrolling pixel art forest background",
        "filename": "out.png",
        "input_image": [],
        "model": "nano-banana-2.1",
        "resolution": "1K",
        "aspect_ratio": "1:1",
        "thinking_level": None,
        "search": False,
        "image_search": False,
        "previous_interaction_id": None,
        "store": None,
        "api": "interactions",
        "dry_run": False,
        "enterprise": False,
        "vertexai": False,
        "project": None,
        "location": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, SCRIPT_PATH, *args],
        capture_output=True,
        text=True,
        env=env,
    )


class TestBananaSDKContracts(unittest.TestCase):
    """Validates generated request payloads directly against live google-genai Pydantic schemas."""

    def test_interactions_payload_validates_against_sdk_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ref_path = os.path.join(tmpdir, "ref.png")
            Image.new("RGB", (4, 4), color=(10, 20, 30)).save(ref_path)

            args = make_args(
                model="nano-banana-2.1",
                resolution="4K",
                aspect_ratio="4:1",
                thinking_level="medium",
                image_search=True,
                input_image=[ref_path],
                previous_interaction_id="int_turn_1",
                store=True,
            )
            model_id = banana.resolve_model(args.model)
            banana.validate_capabilities(args, model_id)
            image_size = banana.normalize_image_size(args.resolution, args.api)
            kwargs = banana.build_interaction_kwargs(args, model_id, image_size)

            parsed = CreateModelInteraction.model_validate(kwargs)
            self.assertEqual(parsed.model, "gemini-nano-banana-2.1")
            self.assertEqual(parsed.response_format.image_size, "4K")
            self.assertNotIsInstance(parsed.response_format.image_size, UnrecognizedStr)
            self.assertEqual(parsed.response_format.aspect_ratio, "4:1")
            self.assertNotIsInstance(parsed.response_format.aspect_ratio, UnrecognizedStr)
            self.assertEqual(parsed.generation_config.thinking_level, "medium")
            self.assertEqual(parsed.previous_interaction_id, "int_turn_1")
            self.assertTrue(parsed.store)
            self.assertEqual(len(parsed.input), 2)
            self.assertEqual(parsed.input[0].type, "image")
            self.assertEqual(parsed.input[0].mime_type, "image/png")

    def test_512_resolution_matches_each_api_contract(self):
        # Interactions API expects literal "512" (NOT "512px")
        for raw_res in ("512", "512px"):
            args_int = make_args(model="nano-banana-2", resolution=raw_res, api="interactions")
            model_id = banana.resolve_model(args_int.model)
            banana.validate_capabilities(args_int, model_id)
            size_int = banana.normalize_image_size(args_int.resolution, "interactions")
            self.assertEqual(size_int, "512")

            kwargs = banana.build_interaction_kwargs(args_int, model_id, size_int)
            parsed = CreateModelInteraction.model_validate(kwargs)
            self.assertEqual(parsed.response_format.image_size, "512")
            self.assertNotIsInstance(parsed.response_format.image_size, UnrecognizedStr)

            # Models API ImageConfig uses "512px"
            size_models = banana.normalize_image_size(raw_res, "models")
            self.assertEqual(size_models, "512px")
            cfg = banana.build_models_config(args_int, size_models)
            self.assertEqual(cfg.image_config.image_size, "512px")

    def test_models_config_builds_search_and_thinking(self):
        args = make_args(
            model="nano-banana-2.1",
            resolution="2K",
            aspect_ratio="16:9",
            thinking_level="high",
            image_search=True,
            api="models",
        )
        cfg = banana.build_models_config(args, "2K")
        self.assertEqual(cfg.response_modalities, ["TEXT", "IMAGE"])
        self.assertEqual(cfg.image_config.aspect_ratio, "16:9")
        self.assertEqual(cfg.image_config.image_size, "2K")
        self.assertEqual(cfg.thinking_config.thinking_level.value, "HIGH")
        self.assertIsNotNone(cfg.tools[0].google_search.search_types.image_search)


class TestBananaExecutionAndExtraction(unittest.TestCase):
    """End-to-end execution tests with mocked SDK boundary verifying real file outputs and error handling."""

    def test_run_image_interactions_output_image_str_and_bytes(self):
        raw_png = b"\x89PNG\r\n\x1a\nFAKE_IMAGE_DATA"
        for payload in (base64.b64encode(raw_png).decode("ascii"), raw_png):
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "nested", "hero.png")
                args = make_args(filename=out_path, store=True)
                fake_interaction = types.SimpleNamespace(
                    id="int_abc123",
                    output_image=types.SimpleNamespace(data=payload),
                    steps=[],
                )
                client = mock.Mock()
                client.interactions.create.return_value = fake_interaction

                stdout_buf = io.StringIO()
                with contextlib.redirect_stdout(stdout_buf):
                    banana.run_image(client, args, "gemini-nano-banana-2.1", "1K")

                with open(out_path, "rb") as f:
                    self.assertEqual(f.read(), raw_png)
                self.assertIn("Interaction ID: int_abc123", stdout_buf.getvalue())

    def test_extract_image_from_steps_stops_on_first_image(self):
        first_png = b"PNG_FIRST"
        second_png = b"PNG_SECOND"
        interaction = types.SimpleNamespace(
            output_image=None,
            steps=[
                types.SimpleNamespace(
                    type="model_output",
                    content=[
                        types.SimpleNamespace(type="text", text="thinking"),
                        types.SimpleNamespace(
                            type="image",
                            data=base64.b64encode(first_png).decode("ascii"),
                        ),
                    ],
                ),
                types.SimpleNamespace(
                    type="model_output",
                    content=[
                        types.SimpleNamespace(
                            type="image",
                            data=base64.b64encode(second_png).decode("ascii"),
                        ),
                    ],
                ),
            ],
        )
        self.assertEqual(banana.extract_image_from_interaction(interaction), first_png)

    def test_run_image_models_skips_thought_parts_and_writes_real_image(self):
        thought_bytes = b"THOUGHT_IMAGE_IGNORED"
        final_bytes = b"FINAL_PNG_BYTES"
        with tempfile.TemporaryDirectory() as tmpdir:
            ref_path = os.path.join(tmpdir, "ref.png")
            out_path = os.path.join(tmpdir, "out.png")
            Image.new("RGB", (4, 4), color=(255, 0, 0)).save(ref_path)

            args = make_args(filename=out_path, input_image=[ref_path], api="models")
            fake_response = types.SimpleNamespace(
                candidates=[
                    types.SimpleNamespace(
                        content=types.SimpleNamespace(
                            parts=[
                                types.SimpleNamespace(
                                    thought=True,
                                    inline_data=types.SimpleNamespace(data=thought_bytes),
                                ),
                                types.SimpleNamespace(
                                    thought=False,
                                    inline_data=types.SimpleNamespace(data=final_bytes),
                                ),
                            ]
                        )
                    )
                ]
            )
            client = mock.Mock()
            client.models.generate_content.return_value = fake_response

            banana.run_image(client, args, "gemini-nano-banana-2.1", "1K", models_config=None)
            with open(out_path, "rb") as f:
                self.assertEqual(f.read(), final_bytes)

    def test_empty_response_fails_fast(self):
        client = mock.Mock()
        client.interactions.create.return_value = types.SimpleNamespace(
            id="int_empty", output_image=None, steps=[]
        )
        with self.assertRaises(ValueError):
            banana.run_image(client, make_args(), "gemini-nano-banana-2.1", "1K")


class TestBananaAuthAndValidation(unittest.TestCase):
    """Verifies ADC/Enterprise/API-key auth matrix and capability/lifecycle guards."""

    def test_init_client_enterprise_quota_project_and_api_key(self):
        fake_creds = mock.Mock(quota_project_id="billing-proj-123")
        fake_auth = types.ModuleType("google.auth")
        fake_auth.default = mock.Mock(return_value=(fake_creds, None))
        fake_genai = types.ModuleType("google.genai")
        fake_genai.Client = mock.Mock()
        fake_google = types.ModuleType("google")
        fake_google.auth = fake_auth
        fake_google.genai = fake_genai
        fake_modules = {
            "google": fake_google,
            "google.auth": fake_auth,
            "google.genai": fake_genai,
        }

        for flag in ({"enterprise": True}, {"vertexai": True}):
            fake_genai.Client.reset_mock()
            with mock.patch.dict(os.environ, {}, clear=True), mock.patch.dict(
                sys.modules, fake_modules
            ):
                banana.init_client(make_args(**flag))
                fake_genai.Client.assert_called_once_with(
                    enterprise=True,
                    project="billing-proj-123",
                    location="global",
                    credentials=fake_creds,
                )

        # Missing credentials fails fast
        stderr_buf = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.dict(
            sys.modules, fake_modules
        ), mock.patch("sys.stderr", stderr_buf):
            with self.assertRaises(SystemExit) as cm:
                banana.init_client(make_args())
            self.assertEqual(cm.exception.code, 1)
        self.assertIn("--billing-project", stderr_buf.getvalue())
        self.assertIn("global", stderr_buf.getvalue())

        # API key path
        fake_genai.Client.reset_mock()
        with mock.patch.dict(
            os.environ, {"GEMINI_API_KEY": "key-xyz"}, clear=True
        ), mock.patch.dict(sys.modules, fake_modules):
            banana.init_client(make_args())
            fake_genai.Client.assert_called_once_with(api_key="key-xyz")

    def test_validation_guards_and_retired_models(self):
        # Unsupported input image extension rejected offline in validate_capabilities
        for bad_args, err_substr in (
            (make_args(input_image=["bad.bmp"]), "Unsupported input image format"),
            (make_args(input_image=[f"img{i}.png" for i in range(15)]), "Maximum of 14"),
            (make_args(model="nano-banana-2.1", resolution="512"), "only supported by 'nano-banana-2'"),
            (make_args(model="nano-banana-2-lite", resolution="2K"), "not supported by nano-banana-2-lite"),
            (make_args(model="nano-banana-2-lite", search=True), "Search grounding is not supported"),
            (make_args(model="nano-banana-2", thinking_level="medium"), "only supported by 'nano-banana-2.1'"),
            (make_args(model="nano-banana-pro", aspect_ratio="1:4"), "Aspect ratio '1:4'"),
            (make_args(model="nano-banana-pro", image_search=True), "--image-search"),
            (make_args(api="models", previous_interaction_id="int_1"), "--previous-interaction-id"),
            (make_args(api="models", store=True), "--store"),
        ):
            stderr_buf = io.StringIO()
            with contextlib.redirect_stderr(stderr_buf), self.assertRaises(SystemExit) as cm:
                model_id = banana.resolve_model(bad_args.model)
                banana.validate_capabilities(bad_args, model_id)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn(err_substr, stderr_buf.getvalue())

        for retired, err_substr in (
            ("imagen-4.0-generate-001", "August 17, 2026"),
            ("gemini-2.5-flash-image", "Legacy or retired model"),
            ("nano-banana", "Legacy or retired model"),
        ):
            stderr_buf = io.StringIO()
            with contextlib.redirect_stderr(stderr_buf), self.assertRaises(SystemExit) as cm:
                banana.resolve_model(retired)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn(err_substr, stderr_buf.getvalue())

    def test_cli_output_aliases_and_offline_dry_run_rejects_bad_image(self):
        # Verify -o alias works and prints SDK-valid Interactions JSON on --dry-run
        ok = run_cli("-p", "pixel sword", "-o", "sword.png", "-m", "nano-banana-2", "-r", "512", "--dry-run")
        self.assertEqual(ok.returncode, 0, msg=ok.stderr)
        self.assertEqual(ok.stderr, "")
        self.assertIn('"image_size": "512"', ok.stdout)

        # Verify bad extension fails fast in --dry-run
        bad = run_cli("-p", "pixel sword", "-o", "sword.png", "-i", "bad.bmp", "--dry-run")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Unsupported input image format", bad.stderr)


if __name__ == "__main__":
    unittest.main()
