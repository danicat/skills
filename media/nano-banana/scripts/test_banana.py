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

import os
import shutil
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "banana.py")
CMD_BASE = ["uv", "run", SCRIPT_PATH] if shutil.which("uv") else [sys.executable, SCRIPT_PATH]

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from banana import detect_mime_type, save_output_image


def run_cli(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(CMD_BASE + list(args), capture_output=True, text=True, env=env)


def test_banana_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "--prompt" in result.stdout or "-p" in result.stdout
    assert "--aspect-ratio" in result.stdout or "-a" in result.stdout
    assert "--resolution" in result.stdout or "-r" in result.stdout
    assert "--thinking-level" in result.stdout
    assert "--search" in result.stdout
    assert "--image-search" in result.stdout
    assert "--api" in result.stdout
    assert "--enterprise" in result.stdout
    assert "--vertexai" in result.stdout
    assert "--project" in result.stdout
    assert "--location" in result.stdout
    assert "global" in result.stdout
    assert "nano-banana-2.1" in result.stdout
    assert "nano-banana-2-1" in result.stdout
    assert "medium" in result.stdout


def test_nano_banana_2_1_capabilities():
    # nano-banana-2.1 supports 1K, 2K, 4K across extended ratios, --image-search,
    # --thinking-level medium, and both interactions and models APIs.
    for alias in ("nano-banana-2.1", "nano-banana-2-1"):
        for res, ratio, api in (
            ("1K", "1:4", "interactions"),
            ("2K", "8:1", "models"),
            ("4K", "16:9", "models"),
        ):
            result = run_cli(
                "-p", "test prompt",
                "-f", "out.png",
                "-m", alias,
                "-r", res,
                "-a", ratio,
                "--api", api,
                "--image-search",
                "--thinking-level", "medium",
                "--dry-run",
            )
            assert result.returncode == 0, f"Unexpected failure for {alias} {res} {ratio} ({api}): {result.stderr}"
            assert f"Model: gemini-nano-banana-2.1 ({alias})" in result.stdout
            assert f"Resolution: {res} | Aspect Ratio: {ratio}" in result.stdout


def test_512px_resolution_rules():
    # 512px / 512 is exclusive to nano-banana-2 (gemini-3.1-flash-image), not nano-banana-2.1
    for res in ("512px", "512"):
        accepted = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-2", "-r", res, "--api", "models", "--dry-run")
        assert accepted.returncode == 0, f"Expected nano-banana-2 to accept {res}: {accepted.stderr}"

        rejected = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-2.1", "-r", res, "--dry-run")
        assert rejected.returncode != 0
        assert "only supported by 'nano-banana-2'" in rejected.stderr


def test_capability_validation_guards():
    # 1. Nano Banana 2 Lite rejecting 2K, 4K, and 512px resolutions
    for invalid_res in ("2K", "4K", "512px"):
        res = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-2-lite", "-r", invalid_res, "--dry-run")
        assert res.returncode != 0
        assert invalid_res in res.stderr

    # 2. Search grounding and Image Search rejected on nano-banana-2-lite
    res = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-2-lite", "--search", "--dry-run")
    assert res.returncode != 0
    assert "Search grounding is not supported by nano-banana-2-lite" in res.stderr

    res = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-2-lite", "--image-search", "--dry-run")
    assert res.returncode != 0
    assert "Search grounding is not supported by nano-banana-2-lite" in res.stderr

    # 3. Thinking level 'medium' rejected on nano-banana-2-lite and nano-banana-2
    for model in ("nano-banana-2-lite", "nano-banana-2"):
        res = run_cli("-p", "test", "-f", "out.png", "-m", model, "--thinking-level", "medium", "--dry-run")
        assert res.returncode != 0
        assert "Thinking level 'medium' is only supported by 'nano-banana-2.1'" in res.stderr

    # 4. Extended aspect ratios (1:4, 8:1) and --image-search rejected on nano-banana-pro
    for ratio in ("1:4", "8:1"):
        res = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-pro", "-a", ratio, "--dry-run")
        assert res.returncode != 0
        assert f"Aspect ratio '{ratio}' is only supported by" in res.stderr

    res = run_cli("-p", "test", "-f", "out.png", "-m", "nano-banana-pro", "--image-search", "--dry-run")
    assert res.returncode != 0
    assert "Google Image Search Grounding (--image-search) is only supported by" in res.stderr


def test_deprecated_and_shutdown_models_rejected():
    # Legacy Nano Banana v1 must be rejected with clear migration guidance
    for legacy in ("nano-banana", "gemini-2.5-flash-image"):
        res = run_cli("-p", "test", "-f", "out.png", "-m", legacy, "--dry-run")
        assert res.returncode != 0
        assert "Legacy or retired model" in res.stderr
        assert "nano-banana-2.1" in res.stderr

    # Shut-down Imagen models must fail fast with August 17, 2026 shutdown notice
    for imagen in ("imagen-4.0-generate-001", "imagen-4.0-ultra-generate-001"):
        res = run_cli("-p", "test", "-f", "out.png", "-m", imagen, "--dry-run")
        assert res.returncode != 0
        assert "August 17, 2026" in res.stderr
        assert "nano-banana-2.1" in res.stderr


def test_fail_fast_missing_credentials():
    clean_env = {
        k: v for k, v in os.environ.items()
        if k not in (
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_CLOUD_PROJECT",
            "GCP_PROJECT",
            "GOOGLE_GENAI_USE_VERTEXAI",
            "GOOGLE_GENAI_USE_ENTERPRISE",
        )
    }
    res = run_cli("-p", "test", "-f", "out.png", env=clean_env)
    assert res.returncode != 0
    assert "GEMINI_API_KEY environment variable is not set" in res.stderr
    assert "global" in res.stderr
    assert "us-central1" not in res.stderr
    assert "CRITICAL FOR AGENTS: Fail fast." in res.stderr


def test_save_output_and_mime_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_out = os.path.join(tmpdir, "nested", "sprites", "sheet.png")
        save_output_image(nested_out, b"PNG_BYTES")
        assert os.path.isfile(nested_out)
        with open(nested_out, "rb") as f:
            assert f.read() == b"PNG_BYTES"

    assert detect_mime_type("hero.WEBP") == "image/webp"
    assert detect_mime_type("photo.heic") == "image/heic"


if __name__ == "__main__":
    test_banana_help()
    test_nano_banana_2_1_capabilities()
    test_512px_resolution_rules()
    test_capability_validation_guards()
    test_deprecated_and_shutdown_models_rejected()
    test_fail_fast_missing_credentials()
    test_save_output_and_mime_detection()
    print("All banana CLI tests passed successfully!")
