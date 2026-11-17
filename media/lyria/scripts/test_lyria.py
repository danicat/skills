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

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "lyria.py")
sys.path.insert(0, SCRIPT_DIR)
import lyria  # noqa: E402

CMD_BASE = (
    ["uv", "run", SCRIPT_PATH]
    if shutil.which("uv")
    else [sys.executable, SCRIPT_PATH]
)


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        CMD_BASE + list(args),
        capture_output=True,
        text=True,
        env=env,
    )


class TestLyriaUnit(unittest.TestCase):
    def test_resolve_model_aliases_and_retired(self):
        self.assertEqual(lyria.resolve_model("lyria-3.5"), "lyria-3.5")
        self.assertEqual(lyria.resolve_model("3.5"), "lyria-3.5")
        self.assertEqual(lyria.resolve_model("lyria-3-clip"), "lyria-3-clip-preview")
        self.assertEqual(lyria.resolve_model("lyria-3-pro"), "lyria-3-pro-preview")
        self.assertEqual(lyria.resolve_model("pro"), "lyria-3-pro-preview")

        for bad in ("lyria-002", "lyria-realtime-exp", "unknown-lyria-model"):
            stderr_buf = io.StringIO()
            with contextlib.redirect_stderr(stderr_buf), self.assertRaises(SystemExit) as cm:
                lyria.resolve_model(bad)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn(bad, stderr_buf.getvalue())

    def test_resolve_audio_format_rules(self):
        self.assertEqual(
            lyria.resolve_audio_format("track.wav", None, "lyria-3.5", "interactions"),
            "wav",
        )
        self.assertEqual(
            lyria.resolve_audio_format("track.mp3", None, "lyria-3.5", "interactions"),
            "mp3",
        )
        self.assertEqual(
            lyria.resolve_audio_format("out.ogg", None, "lyria-3.5", "interactions"),
            "mp3",
        )

        invalid_cases = [
            ("out.wav", "mp3", "lyria-3.5", "interactions"),
            ("out.mp3", "wav", "lyria-3.5", "interactions"),
            ("clip.wav", None, "lyria-3-clip-preview", "interactions"),
            ("song.wav", "wav", "lyria-3-pro-preview", "interactions"),
            ("track.wav", None, "lyria-3.5", "models"),
        ]
        for filename, explicit_fmt, model_id, api_mode in invalid_cases:
            stderr_buf = io.StringIO()
            with contextlib.redirect_stderr(stderr_buf), self.assertRaises(SystemExit) as cm:
                lyria.resolve_audio_format(filename, explicit_fmt, model_id, api_mode)
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("Error:", stderr_buf.getvalue())

    def test_detect_mime_type(self):
        self.assertEqual(lyria.detect_mime_type("cover.png"), "image/png")
        self.assertEqual(lyria.detect_mime_type("cover.jpg"), "image/jpeg")
        self.assertEqual(lyria.detect_mime_type("cover.jpeg"), "image/jpeg")
        self.assertEqual(lyria.detect_mime_type("cover.webp"), "image/webp")
        self.assertEqual(lyria.detect_mime_type("cover.heic"), "image/heic")
        self.assertEqual(lyria.detect_mime_type("cover.HEIF"), "image/heif")

        with self.assertRaises(ValueError) as ctx:
            lyria.detect_mime_type("animated.gif")
        self.assertIn("Unsupported input image format", str(ctx.exception))

    def test_save_nested_output_and_lyrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "nested", "audio", "theme.mp3")
            lyrics_path = os.path.join(tmpdir, "nested", "lyrics", "theme.txt")
            lyria.save_binary_file(audio_path, b"ID3-test-bytes")
            lyria.save_text_file(lyrics_path, "[Verse]\nTest lyrics\n")
            with open(audio_path, "rb") as f:
                self.assertEqual(f.read(), b"ID3-test-bytes")
            with open(lyrics_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "[Verse]\nTest lyrics\n")


class TestLyriaCLI(unittest.TestCase):
    def test_help_flags_and_models(self):
        res = run_cli("--help")
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertEqual(res.stderr, "")
        for token in (
            "--prompt",
            "--model",
            "lyria-3.5",
            "lyria-3-pro",
            "lyria-3-pro-preview",
            "lyria-3-clip",
            "lyria-3-clip-preview",
            "--format",
            "--lyrics-file",
            "--api",
            "--dry-run",
            "--enterprise",
            "--vertexai",
            "--project",
            "--location",
            "global",
        ):
            self.assertIn(token, res.stdout)

    def test_dry_run_valid_combinations(self):
        cases = [
            (["-p", "Acoustic folk", "-f", "song.mp3", "-m", "lyria-3.5", "--dry-run"], "Format: mp3"),
            (["-p", "Ambient loop", "-f", "track.wav", "-m", "lyria-3.5", "--dry-run"], "Format: wav"),
            (["-p", "Orchestral score", "-f", "score.mp3", "-m", "lyria-3-pro", "--dry-run"], "lyria-3-pro-preview"),
            (["-p", "8-bit arcade loop", "-f", "loop.mp3", "-m", "lyria-3-clip", "--dry-run"], "lyria-3-clip-preview"),
            (["-p", "Jazz trio", "-f", "jazz.mp3", "--api", "models", "--dry-run"], "Dry run validation succeeded."),
        ]
        for args, expected in cases:
            res = run_cli(*args)
            self.assertEqual(res.returncode, 0, msg=f"args={args} stderr={res.stderr}")
            self.assertEqual(res.stderr, "")
            self.assertIn(expected, res.stdout)

    def test_cli_fail_fast_validation_errors(self):
        too_many_images = ["-p", "test", "-f", "out.mp3", "--dry-run"]
        for i in range(11):
            too_many_images.extend(["-i", f"img_{i}.png"])
        res = run_cli(*too_many_images)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Maximum of 10 input images allowed", res.stderr)

        bad_cases = [
            (["-p", "test", "-i", "bad.gif", "--dry-run"], "Unsupported input image format"),
            (["-p", "test", "-f", "out.wav", "--format", "mp3", "--dry-run"], "ends with '.wav'"),
            (["-p", "test", "-f", "out.mp3", "--format", "wav", "--dry-run"], "ends with '.mp3'"),
            (["-p", "test", "-m", "lyria-3-clip", "-f", "loop.wav", "--dry-run"], "WAV output is only supported on 'lyria-3.5'"),
            (["-p", "test", "-m", "lyria-3-pro", "-f", "song.wav", "--dry-run"], "WAV output is only supported on 'lyria-3.5'"),
            (["-p", "test", "--api", "models", "-f", "out.wav", "--dry-run"], "requires '--api interactions'"),
            (["-p", "test", "-m", "lyria-002", "--dry-run"], "Legacy or retired model"),
        ]
        for args, expected_err in bad_cases:
            res = run_cli(*args)
            self.assertNotEqual(res.returncode, 0, msg=f"args={args} unexpectedly succeeded")
            self.assertIn(expected_err, res.stderr)

    def test_fail_fast_missing_credentials(self):
        env = dict(os.environ)
        for key in (
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_GENAI_USE_VERTEXAI",
            "GOOGLE_GENAI_USE_ENTERPRISE",
            "GOOGLE_CLOUD_PROJECT",
            "GCP_PROJECT",
        ):
            env.pop(key, None)

        res = run_cli("-p", "test", "-m", "lyria-3.5", env=env)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("GEMINI_API_KEY", res.stderr)
        self.assertIn("GOOGLE_CLOUD_PROJECT", res.stderr)
        self.assertIn("global", res.stderr)
        self.assertNotIn("us-central1", res.stderr)
        self.assertIn("Do NOT attempt rogue workarounds", res.stderr)


if __name__ == "__main__":
    unittest.main()
