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
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "lyria.py")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import lyria  # noqa: E402


def make_args(**overrides) -> argparse.Namespace:
    defaults = {
        "prompt": "Atmospheric synthwave at 110 BPM in D minor. Instrumental only, no vocals.",
        "filename": "track.mp3",
        "model": "lyria-3.5",
        "input_image": [],
        "format": None,
        "lyrics_file": None,
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


class TestLyriaSDKContracts(unittest.TestCase):
    """Validates Lyria request payloads directly against live google-genai Pydantic schemas."""

    def test_wav_and_multimodal_payload_validates_against_sdk_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "concept.png")
            Image.new("RGB", (4, 4), color=(0, 128, 255)).save(img_path)

            args = make_args(
                filename="stage_theme.wav",
                model="lyria-3.5",
                input_image=[img_path],
            )
            model_id = lyria.resolve_model(args.model)
            audio_format = lyria.validate_capabilities(args, model_id)
            self.assertEqual(audio_format, "wav")

            kwargs = lyria.build_interaction_kwargs(args, model_id, audio_format)
            parsed = CreateModelInteraction.model_validate(kwargs)
            self.assertEqual(parsed.model, "lyria-3.5")
            self.assertEqual(parsed.response_format.type, "audio")
            self.assertEqual(parsed.response_format.mime_type, "audio/wav")
            self.assertNotIsInstance(parsed.response_format.mime_type, UnrecognizedStr)
            self.assertEqual(len(parsed.input), 2)
            self.assertEqual(parsed.input[0].type, "text")
            self.assertEqual(parsed.input[1].type, "image")
            self.assertEqual(parsed.input[1].mime_type, "image/png")

    def test_mp3_payload_omits_response_format_and_models_config_validates(self):
        args = make_args(filename="loop.mp3", model="lyria-3-clip")
        model_id = lyria.resolve_model(args.model)
        audio_format = lyria.validate_capabilities(args, model_id)
        kwargs = lyria.build_interaction_kwargs(args, model_id, audio_format)

        parsed = CreateModelInteraction.model_validate(kwargs)
        self.assertEqual(parsed.model, "lyria-3-clip-preview")
        self.assertIsNone(parsed.response_format)

        cfg = lyria.build_models_config()
        self.assertEqual(cfg.response_modalities, ["AUDIO", "TEXT"])


class TestLyriaExecutionAndExtraction(unittest.TestCase):
    """End-to-end execution tests with mocked SDK boundary verifying audio/lyrics writes and error handling."""

    def test_run_music_interactions_output_audio_str_and_bytes_with_lyrics(self):
        raw_wav = b"RIFF\x24\x00\x00\x00WAVEfmt "
        for payload in (base64.b64encode(raw_wav).decode("ascii"), raw_wav):
            with tempfile.TemporaryDirectory() as tmpdir:
                out_audio = os.path.join(tmpdir, "nested", "theme.wav")
                out_lyrics = os.path.join(tmpdir, "nested", "lyrics.txt")
                args = make_args(filename=out_audio, lyrics_file=out_lyrics)

                client = mock.Mock()
                client.interactions.create.return_value = types.SimpleNamespace(
                    output_audio=types.SimpleNamespace(data=payload),
                    output_text="[Intro]\nWarm analog pads\n",
                    steps=[],
                )

                with contextlib.redirect_stdout(io.StringIO()):
                    lyria.run_music(client, args, "lyria-3.5", "wav")
                with open(out_audio, "rb") as f:
                    self.assertEqual(f.read(), raw_wav)
                with open(out_lyrics, "r", encoding="utf-8") as f:
                    self.assertEqual(f.read(), "[Intro]\nWarm analog pads\n")

    def test_extract_audio_and_lyrics_from_steps_fallback(self):
        raw_mp3 = b"ID3\x03\x00FAKE_MP3"
        interaction = types.SimpleNamespace(
            output_audio=None,
            output_text=None,
            steps=[
                types.SimpleNamespace(
                    type="model_output",
                    content=[
                        types.SimpleNamespace(type="text", text="[Verse 1]"),
                        types.SimpleNamespace(
                            type="audio",
                            data=base64.b64encode(raw_mp3).decode("ascii"),
                        ),
                        types.SimpleNamespace(type="text", text="[Chorus]"),
                    ],
                )
            ],
        )
        audio_bytes, lyrics = lyria.extract_audio_and_lyrics_from_interaction(interaction)
        self.assertEqual(audio_bytes, raw_mp3)
        self.assertEqual(lyrics, "[Verse 1]\n[Chorus]")

    def test_run_music_models_api_writes_audio_and_lyrics(self):
        raw_mp3 = b"ID3_MODELS_MP3"
        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "cover.png")
            out_audio = os.path.join(tmpdir, "song.mp3")
            out_lyrics = os.path.join(tmpdir, "song.txt")
            Image.new("RGB", (4, 4), color=(50, 50, 50)).save(img_path)

            args = make_args(
                filename=out_audio,
                lyrics_file=out_lyrics,
                input_image=[img_path],
                api="models",
            )
            client = mock.Mock()
            client.models.generate_content.return_value = types.SimpleNamespace(
                candidates=[
                    types.SimpleNamespace(
                        content=types.SimpleNamespace(
                            parts=[
                                types.SimpleNamespace(
                                    inline_data=types.SimpleNamespace(data=raw_mp3),
                                    text=None,
                                ),
                                types.SimpleNamespace(
                                    inline_data=None,
                                    text="[Outro]\nFade out",
                                ),
                            ]
                        )
                    )
                ]
            )

            with contextlib.redirect_stdout(io.StringIO()):
                lyria.run_music(client, args, "lyria-3.5", "mp3", models_config=lyria.build_models_config())
            with open(out_audio, "rb") as f:
                self.assertEqual(f.read(), raw_mp3)
            with open(out_lyrics, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "[Outro]\nFade out")

    def test_empty_audio_response_fails_fast(self):
        client = mock.Mock()
        client.interactions.create.return_value = types.SimpleNamespace(
            output_audio=None, output_text=None, steps=[]
        )
        with self.assertRaises(ValueError):
            lyria.run_music(client, make_args(), "lyria-3.5", "mp3")


class TestLyriaAuthAndValidation(unittest.TestCase):
    """Verifies ADC/Enterprise/API-key auth matrix and capability/format/lifecycle guards."""

    def test_init_client_enterprise_quota_project_and_api_key(self):
        fake_creds = mock.Mock(quota_project_id="lyria-billing-proj")
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
                lyria.init_client(make_args(**flag))
                fake_genai.Client.assert_called_once_with(
                    enterprise=True,
                    project="lyria-billing-proj",
                    location="global",
                    credentials=fake_creds,
                )

        # Missing credentials fails fast with --billing-project and global guidance
        stderr_buf = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.dict(
            sys.modules, fake_modules
        ), mock.patch("sys.stderr", stderr_buf):
            with self.assertRaises(SystemExit) as cm:
                lyria.init_client(make_args())
            self.assertEqual(cm.exception.code, 1)
        self.assertIn("--billing-project", stderr_buf.getvalue())
        self.assertIn("global", stderr_buf.getvalue())
        self.assertNotIn("us-central1", stderr_buf.getvalue())

        # API key path
        fake_genai.Client.reset_mock()
        with mock.patch.dict(
            os.environ, {"GEMINI_API_KEY": "lyria-key"}, clear=True
        ), mock.patch.dict(sys.modules, fake_modules):
            lyria.init_client(make_args())
            fake_genai.Client.assert_called_once_with(api_key="lyria-key")

    def test_retired_models_and_format_constraints_fail_fast(self):
        for retired in ("lyria-002", "lyria-realtime-exp", "unknown-lyria-model"):
            stderr_buf = io.StringIO()
            with contextlib.redirect_stderr(stderr_buf), self.assertRaises(SystemExit) as cm:
                lyria.resolve_model(retired)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn(retired, stderr_buf.getvalue())

        invalid_cases = [
            (make_args(input_image=[f"i{n}.png" for n in range(11)]), "Maximum of 10"),
            (make_args(input_image=["bad.gif"]), "Unsupported input image format"),
            (make_args(filename="out.wav", format="mp3"), "ends with '.wav'"),
            (make_args(filename="out.mp3", format="wav"), "ends with '.mp3'"),
            (make_args(filename="clip.wav", model="lyria-3-clip"), "only supported on 'lyria-3.5'"),
            (make_args(filename="song.wav", model="lyria-3-pro"), "only supported on 'lyria-3.5'"),
            (make_args(filename="track.wav", api="models"), "requires '--api interactions'"),
        ]
        for bad_args, expected_err in invalid_cases:
            stderr_buf = io.StringIO()
            with contextlib.redirect_stderr(stderr_buf), self.assertRaises(SystemExit) as cm:
                model_id = lyria.resolve_model(bad_args.model)
                lyria.validate_capabilities(bad_args, model_id)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn(expected_err, stderr_buf.getvalue())

    def test_cli_dry_run_emits_wav_response_format(self):
        res = run_cli("-p", "Ambient loop", "--output", "theme.wav", "-m", "lyria-3.5", "--dry-run")
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertEqual(res.stderr, "")
        self.assertIn('"mime_type": "audio/wav"', res.stdout)


if __name__ == "__main__":
    unittest.main()
