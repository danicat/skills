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
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.68.0",
#     "google-auth>=2.0.0",
#     "pytest>=8.0.0",
# ]
# ///

import argparse
import io
import os
import shutil
import subprocess
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omni  # noqa: E402

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "omni.py")
CMD_BASE = (
    ["uv", "run", SCRIPT_PATH]
    if shutil.which("uv")
    else [sys.executable, SCRIPT_PATH]
)


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
        "vertexai": False,
        "project": None,
        "location": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class TestOmniUnit(unittest.TestCase):
    def test_model_alias_resolution_omni_1_2_flash(self):
        self.assertEqual(omni.resolve_model(None), "gemini-omni-1.2-flash")
        self.assertEqual(
            omni.resolve_model("gemini-omni-1.2-flash"), "gemini-omni-1.2-flash"
        )
        self.assertEqual(
            omni.resolve_model("omni-1.2-flash"), "gemini-omni-1.2-flash"
        )
        self.assertEqual(omni.resolve_model("omni-1.2"), "gemini-omni-1.2-flash")
        self.assertEqual(omni.resolve_model("1.2"), "gemini-omni-1.2-flash")
        self.assertEqual(omni.resolve_model("flash-1.2"), "gemini-omni-1.2-flash")
        self.assertEqual(
            omni.resolve_model("gemini-omni-flash-1.2"), "gemini-omni-1.2-flash"
        )
        self.assertEqual(
            omni.resolve_model("gemini-omni-flash-1.2-preview"),
            "gemini-omni-1.2-flash",
        )

    def test_model_alias_resolution_omni_1_1_flash(self):
        self.assertEqual(
            omni.resolve_model("gemini-omni-1.1-flash"), "gemini-omni-1.1-flash"
        )
        self.assertEqual(
            omni.resolve_model("gemini-omni-1.1"), "gemini-omni-1.1-flash"
        )
        self.assertEqual(omni.resolve_model("1.1"), "gemini-omni-1.1-flash")
        self.assertEqual(
            omni.resolve_model("gemini-omni-1.1-flash-preview"),
            "gemini-omni-1.1-flash-preview",
        )

    def test_deprecated_and_unknown_models_fail_fast(self):
        with self.assertRaises(ValueError) as ctx:
            omni.resolve_model("gemini-omni-flash-preview")
        self.assertIn("shut down", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            omni.resolve_model("non-existent-model-xyz")
        self.assertIn("Unsupported model", str(ctx2.exception))

    def test_duration_validation_1_2_vs_1_1(self):
        # 15s is valid on gemini-omni-1.2-flash
        args_15s = make_args(duration="15s", duration_explicit=True)
        omni.validate_video_request(args_15s, "gemini-omni-1.2-flash")

        # 15s fails on gemini-omni-1.1-flash (max 10s)
        with self.assertRaises(ValueError) as ctx:
            omni.validate_video_request(args_15s, "gemini-omni-1.1-flash")
        self.assertIn("gemini-omni-1.2-flash", str(ctx.exception))

        # 12s fails on --task extend (max 10s per extension turn)
        args_extend_12s = make_args(duration="12s", task="extend")
        with self.assertRaises(ValueError) as ctx2:
            omni.validate_video_request(args_extend_12s, "gemini-omni-1.2-flash")
        self.assertIn("extension", str(ctx2.exception))

        # 12s fails on 2-image interpolation (max 10s)
        args_interp_12s = make_args(
            duration="12s",
            task="image_to_video",
            input=["gs://b/first.png", "gs://b/last.png"],
        )
        with self.assertRaises(ValueError) as ctx3:
            omni.validate_video_request(args_interp_12s, "gemini-omni-1.2-flash")
        self.assertIn("interpolation", str(ctx3.exception))

    def test_reference_video_limits(self):
        # 3 reference videos allowed for 10s clip
        args_3_vids_10s = make_args(
            duration="10s",
            task="reference_to_video",
            input=["gs://b/v1.mp4", "gs://b/v2.mp4", "gs://b/v3.mp4"],
        )
        omni.validate_video_request(args_3_vids_10s, "gemini-omni-1.2-flash")

        # 2 reference videos rejected for 12s clip (max 1 reference video for 11s-15s)
        args_2_vids_12s = make_args(
            duration="12s",
            task="reference_to_video",
            input=["gs://b/v1.mp4", "gs://b/v2.mp4"],
        )
        with self.assertRaises(ValueError) as ctx:
            omni.validate_video_request(args_2_vids_12s, "gemini-omni-1.2-flash")
        self.assertIn("At most 1 reference video", str(ctx.exception))

    def test_upscale_validation_and_payload(self):
        # Valid upscale request on gemini-omni-1.2-flash
        args_upscale = make_args(
            prompt=None,
            task="upscale",
            input=["gs://my-bucket/input_360p.mp4"],
            resolution="1080p",
            resolution_explicit=True,
            gcs_uri="gs://my-bucket/upscaled/",
        )
        omni.validate_video_request(args_upscale, "gemini-omni-1.2-flash")
        kwargs = omni.build_interaction_kwargs(args_upscale, "gemini-omni-1.2-flash")
        self.assertEqual(kwargs["model"], "gemini-omni-1.2-flash")
        self.assertEqual(
            kwargs["generation_config"], {"video_config": {"task": "upscale"}}
        )
        self.assertEqual(
            kwargs["response_format"],
            {
                "type": "video",
                "resolution": "1080p",
                "gcs_uri": "gs://my-bucket/upscaled/",
            },
        )
        self.assertEqual(
            kwargs["input"],
            [
                {
                    "type": "video",
                    "uri": "gs://my-bucket/input_360p.mp4",
                    "mime_type": "video/mp4",
                }
            ],
        )

        # Upscale rejected on gemini-omni-1.1-flash
        with self.assertRaises(ValueError):
            omni.validate_video_request(args_upscale, "gemini-omni-1.1-flash")

        # Upscale rejected without explicit target resolution
        args_no_res = make_args(
            task="upscale",
            input=["gs://my-bucket/input_360p.mp4"],
            resolution="720p",
            resolution_explicit=False,
        )
        with self.assertRaises(ValueError):
            omni.validate_video_request(args_no_res, "gemini-omni-1.2-flash")

        # Upscale rejected for 360p target resolution
        args_360p = make_args(
            task="upscale",
            input=["gs://my-bucket/input_360p.mp4"],
            resolution="360p",
            resolution_explicit=True,
        )
        with self.assertRaises(ValueError):
            omni.validate_video_request(args_360p, "gemini-omni-1.2-flash")

    def test_deprecated_control_tags_detection(self):
        tags = omni.check_deprecated_control_tags(
            "<FIRST_FRAME> <IMAGE_REF_0> Animate this scene."
        )
        self.assertIn("<FIRST_FRAME>", tags)
        self.assertIn("<IMAGE_REF_", tags)
        self.assertEqual(
            omni.check_deprecated_control_tags(
                "Use the first image as the starting frame."
            ),
            [],
        )

    def test_init_client_vertex_ai_default_global_and_api_key(self):
        fake_creds = mock.Mock(quota_project_id="quota-gcp-proj")
        args_vertex = make_args(vertexai=True, project=None, location=None)
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch(
            "omni.google.auth.default", return_value=(fake_creds, None)
        ), mock.patch("omni.genai.Client") as mock_client:
            omni.init_client(args_vertex)
            mock_client.assert_called_once_with(
                vertexai=True,
                project="quota-gcp-proj",
                location="global",
                credentials=fake_creds,
            )

        args_api_key = make_args(vertexai=False, project=None, location=None)
        with mock.patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "test-gemini-key"},
            clear=True,
        ), mock.patch("omni.genai.Client") as mock_client:
            omni.init_client(args_api_key)
            mock_client.assert_called_once_with(api_key="test-gemini-key")

    def test_init_client_fail_fast_missing_auth(self):
        args_none = make_args(vertexai=False, project=None, location=None)
        stderr_buf = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch(
            "sys.stderr", stderr_buf
        ):
            with self.assertRaises(SystemExit) as cm:
                omni.init_client(args_none)
            self.assertEqual(cm.exception.code, 1)
        err_out = stderr_buf.getvalue()
        self.assertIn("GOOGLE_CLOUD_PROJECT", err_out)
        self.assertIn("Do NOT attempt rogue workarounds", err_out)

    def test_cli_help_and_dry_run(self):
        help_res = subprocess.run(
            CMD_BASE + ["--help"], capture_output=True, text=True
        )
        self.assertEqual(help_res.returncode, 0)
        unwrapped_help = " ".join(help_res.stdout.split()).replace("- ", "-")
        self.assertIn("gemini-omni-1.2-flash", unwrapped_help)
        self.assertIn("--task", help_res.stdout)
        self.assertIn("--duration", help_res.stdout)
        self.assertIn("--vertexai", help_res.stdout)

        for alias in (
            "gemini-omni-1.2-flash",
            "omni-1.2-flash",
            "omni-1.2",
            "1.2",
            "flash-1.2",
        ):
            dry_res = subprocess.run(
                CMD_BASE
                + [
                    "--prompt",
                    "A knight walking across a bridge at sunset with orchestral strings.",
                    "--model",
                    alias,
                    "--resolution",
                    "1080p",
                    "--duration",
                    "15s",
                    "--seed",
                    "42",
                    "--output",
                    "knight.mp4",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry_res.returncode, 0, msg=dry_res.stderr)
            self.assertIn("Model: gemini-omni-1.2-flash", dry_res.stdout)
            self.assertIn("Duration: 15s", dry_res.stdout)
            self.assertIn("Dry run validation succeeded.", dry_res.stdout)


if __name__ == "__main__":
    unittest.main()
