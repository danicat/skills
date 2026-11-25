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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "omni.py")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import omni  # noqa: E402


def make_args(**overrides) -> argparse.Namespace:
    defaults = {
        "prompt": "A slow tracking shot through a neon cyberpunk alley in the rain.",
        "input": [],
        "resolution": "720p",
        "resolution_explicit": False,
        "aspect_ratio": "16:9",
        "aspect_ratio_explicit": False,
        "duration": "10s",
        "duration_explicit": False,
        "task": None,
        "seed": None,
        "delivery": "inline",
        "gcs_uri": None,
        "previous_interaction_id": None,
        "store": None,
        "background": False,
        "extract_audio": None,
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


class TestOmniSDKContracts(unittest.TestCase):
    """Validates generated Interactions API payloads directly against live google-genai Pydantic schemas."""

    def test_text_and_multimodal_payloads_validate_against_sdk_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "start.png")
            with open(img_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\nFRAME")

            args = make_args(
                resolution="1080p",
                aspect_ratio="9:16",
                duration="15s",
                task="image_to_video",
                seed=42,
                delivery="uri",
                input=[img_path],
                store=True,
            )
            model_id = omni.resolve_model("gemini-omni-1.2-flash")
            omni.validate_video_request(args, model_id)
            kwargs = omni.build_interaction_kwargs(args, model_id)

            parsed = CreateModelInteraction.model_validate(kwargs)
            self.assertEqual(parsed.response_format.resolution, "1080p")
            self.assertNotIsInstance(parsed.response_format.resolution, UnrecognizedStr)
            self.assertEqual(parsed.response_format.aspect_ratio, "9:16")
            self.assertNotIsInstance(parsed.response_format.aspect_ratio, UnrecognizedStr)
            self.assertEqual(parsed.response_format.delivery, "uri")
            self.assertNotIsInstance(parsed.response_format.delivery, UnrecognizedStr)
            self.assertEqual(parsed.generation_config.video_config.task, "image_to_video")
            self.assertNotIsInstance(parsed.generation_config.video_config.task, UnrecognizedStr)
            self.assertEqual(parsed.generation_config.seed, 42)
            self.assertTrue(parsed.store)
            self.assertEqual(len(parsed.input), 2)
            self.assertEqual(parsed.input[0].type, "image")
            self.assertEqual(parsed.input[0].mime_type, "image/png")

    def test_upscale_payload_validates_against_sdk_schema(self):
        args_upscale = make_args(
            prompt=None,
            task="upscale",
            input=["gs://my-bucket/input_360p.mp4"],
            resolution="4k",
            resolution_explicit=True,
            delivery="uri",
            gcs_uri="gs://my-bucket/upscaled/",
        )
        omni.validate_video_request(args_upscale, "gemini-omni-1.2-flash")
        kwargs = omni.build_interaction_kwargs(args_upscale, "gemini-omni-1.2-flash")

        parsed = CreateModelInteraction.model_validate(kwargs)
        self.assertEqual(parsed.response_format.resolution, "4k")
        self.assertNotIsInstance(parsed.response_format.resolution, UnrecognizedStr)
        self.assertEqual(parsed.response_format.gcs_uri, "gs://my-bucket/upscaled/")
        self.assertEqual(parsed.generation_config.video_config.task, "upscale")
        self.assertEqual(len(parsed.input), 1)
        self.assertEqual(parsed.input[0].type, "video")
        self.assertEqual(parsed.input[0].uri, "gs://my-bucket/input_360p.mp4")


class TestOmniExecutionAndExtraction(unittest.TestCase):
    """End-to-end execution tests with mocked SDK boundary covering bytes/str, steps, URI polling, GCS, and background."""

    def test_run_video_inline_output_video_str_and_bytes(self):
        raw_mp4 = b"\x00\x00\x00\x18ftypmp42FAKE_MP4"
        for payload in (base64.b64encode(raw_mp4).decode("ascii"), raw_mp4):
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = os.path.join(tmpdir, "nested", "clip.mp4")
                client = mock.Mock()
                client.interactions.create.return_value = types.SimpleNamespace(
                    id="int_vid_1",
                    status="completed",
                    output_video=types.SimpleNamespace(data=payload, gcs_uri=None, uri=None),
                    steps=[],
                )
                stdout_buf = io.StringIO()
                with contextlib.redirect_stdout(stdout_buf):
                    omni.run_video(client, make_args(), "gemini-omni-1.2-flash", out_path)

                with open(out_path, "rb") as f:
                    self.assertEqual(f.read(), raw_mp4)
                self.assertIn("Interaction ID: int_vid_1", stdout_buf.getvalue())

    def test_extract_video_uri_polling_and_failure(self):
        # Poll PROCESSING -> ACTIVE -> download bytes
        client = mock.Mock()
        client.files.get.side_effect = [
            types.SimpleNamespace(state=types.SimpleNamespace(name="PROCESSING")),
            types.SimpleNamespace(state=types.SimpleNamespace(name="ACTIVE")),
        ]
        client.files.download.return_value = b"DOWNLOADED_MP4"
        interaction = types.SimpleNamespace(
            output_video=types.SimpleNamespace(data=None, gcs_uri=None, uri="files/vid_999"),
            steps=[],
        )
        with mock.patch("omni.time.sleep") as mock_sleep:
            video_bytes, gcs_uri = omni.extract_video_from_interaction(client, interaction)
        self.assertEqual(video_bytes, b"DOWNLOADED_MP4")
        self.assertIsNone(gcs_uri)
        mock_sleep.assert_called_once_with(5)

        # FAILED state raises RuntimeError
        client_fail = mock.Mock()
        client_fail.files.get.return_value = types.SimpleNamespace(
            state=types.SimpleNamespace(name="FAILED")
        )
        with self.assertRaises(RuntimeError):
            omni.extract_video_from_interaction(client_fail, interaction)

    def test_run_video_gcs_uri_and_background_and_steps_fallback(self):
        # GCS URI skips local write
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "unused.mp4")
            client = mock.Mock()
            client.interactions.create.return_value = types.SimpleNamespace(
                id="int_gcs",
                status="completed",
                output_video=types.SimpleNamespace(
                    data=None, gcs_uri="gs://bucket/clip.mp4", uri=None
                ),
                steps=[],
            )
            stdout_buf = io.StringIO()
            with contextlib.redirect_stdout(stdout_buf):
                omni.run_video(client, make_args(), "gemini-omni-1.2-flash", out_path)
            self.assertFalse(os.path.exists(out_path))
            self.assertIn("gs://bucket/clip.mp4", stdout_buf.getvalue())

        # Background in_progress returns without failing
        client_bg = mock.Mock()
        client_bg.interactions.create.return_value = types.SimpleNamespace(
            id="int_bg", status="in_progress", output_video=None, steps=[]
        )
        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            omni.run_video(
                client_bg,
                make_args(background=True, store=True),
                "gemini-omni-1.2-flash",
                "bg.mp4",
            )
        self.assertIn("Background interaction started", stdout_buf.getvalue())

        # Steps fallback extracts video bytes
        step_mp4 = b"STEP_VIDEO_BYTES"
        inter_steps = types.SimpleNamespace(
            output_video=None,
            steps=[
                types.SimpleNamespace(
                    type="model_output",
                    content=[
                        types.SimpleNamespace(
                            type="video",
                            data=base64.b64encode(step_mp4).decode("ascii"),
                            gcs_uri=None,
                            uri=None,
                        )
                    ],
                )
            ],
        )
        self.assertEqual(omni.extract_video_from_interaction(mock.Mock(), inter_steps), (step_mp4, None))

        # Empty response fails fast
        client_empty = mock.Mock()
        client_empty.interactions.create.return_value = types.SimpleNamespace(
            id="int_empty", status="completed", output_video=None, steps=[]
        )
        with self.assertRaises(ValueError):
            omni.run_video(client_empty, make_args(), "gemini-omni-1.2-flash", "empty.mp4")


class TestOmniValidationAndAuth(unittest.TestCase):
    """Verifies model lifecycle, video constraints, MIME detection, and auth matrix."""

    def test_model_resolution_and_deprecated_rejection(self):
        for alias in (
            None,
            "gemini-omni-1.2-flash",
            "omni-1.2-flash",
            "omni-1.2",
            "1.2",
            "flash-1.2",
        ):
            self.assertEqual(omni.resolve_model(alias), "gemini-omni-1.2-flash")

        with self.assertRaises(ValueError) as ctx:
            omni.resolve_model("gemini-omni-flash-preview")
        self.assertIn("shut down", str(ctx.exception))

        for old in ("gemini-omni-1.1-flash", "gemini-omni-1.1-flash-preview", "1.1"):
            with self.assertRaises(ValueError) as ctx_old:
                omni.resolve_model(old)
            self.assertIn("deprecated", str(ctx_old.exception))

    def test_video_request_validation_rules(self):
        omni.validate_video_request(make_args(duration="15s"), "gemini-omni-1.2-flash")

        invalid_cases = [
            (make_args(duration="2s"), "out of range"),
            (make_args(duration="16s"), "out of range"),
            (make_args(duration="12s", task="extend"), "extension"),
            (
                make_args(duration="12s", task="image_to_video", input=["a.png", "b.png"]),
                "interpolation",
            ),
            (
                make_args(duration="12s", task="reference_to_video", input=["v1.mp4", "v2.mp4"]),
                "At most 1 reference video",
            ),
            (make_args(background=True, store=False), "cannot be combined with '--no-store'"),
            (make_args(task="upscale", input=["v.mp4"], resolution="720p", resolution_explicit=False), "explicit target --resolution"),
            (make_args(task="upscale", input=["v.mp4"], resolution="360p", resolution_explicit=True), "Invalid upscale target"),
        ]
        for bad_args, err_substr in invalid_cases:
            with self.assertRaises(ValueError) as ctx:
                omni.validate_video_request(bad_args, "gemini-omni-1.2-flash")
            self.assertIn(err_substr, str(ctx.exception))

    def test_mime_detection_and_deprecated_tags(self):
        self.assertEqual(omni.detect_mime_type("clip.mov"), "video/quicktime")
        self.assertEqual(omni.detect_mime_type("clip.mpeg"), "video/mpeg")
        self.assertEqual(omni.detect_mime_type("photo.HEIF"), "image/heif")
        self.assertEqual(omni.detect_mime_type("files/vid_123"), "application/octet-stream")
        for bad in ("local.avi", "clip.mpegs", "notes.txt"):
            with self.assertRaises(ValueError):
                omni.detect_mime_type(bad)

        self.assertIn("<FIRST_FRAME>", omni.check_deprecated_control_tags("<FIRST_FRAME> go"))
        self.assertEqual(omni.check_deprecated_control_tags("Use the first image as start frame."), [])

    def test_init_client_enterprise_quota_project_and_fail_fast(self):
        fake_creds = mock.Mock(quota_project_id="quota-gcp-proj")
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
                omni.init_client(make_args(**flag))
                fake_genai.Client.assert_called_once_with(
                    enterprise=True,
                    project="quota-gcp-proj",
                    location="global",
                    credentials=fake_creds,
                )

        stderr_buf = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.dict(
            sys.modules, fake_modules
        ), mock.patch("sys.stderr", stderr_buf):
            with self.assertRaises(SystemExit) as cm:
                omni.init_client(make_args())
            self.assertEqual(cm.exception.code, 1)
        self.assertIn("--billing-project", stderr_buf.getvalue())

    def test_cli_dry_run_and_background_no_store_rejection(self):
        ok = run_cli(
            "--prompt", "A train crossing a coastal viaduct",
            "--resolution", "1080p",
            "--duration", "15s",
            "--dry-run",
        )
        self.assertEqual(ok.returncode, 0, msg=ok.stderr)
        self.assertEqual(ok.stderr, "")
        self.assertIn('"resolution": "1080p"', ok.stdout)

        bad = run_cli("--prompt", "test", "--background", "--no-store", "--dry-run")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("cannot be combined with '--no-store'", bad.stderr)


if __name__ == "__main__":
    unittest.main()
