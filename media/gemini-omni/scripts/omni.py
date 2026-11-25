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
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Any
from urllib.parse import urlsplit
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module=r"google\.genai.*")

DEFAULT_MODEL = "gemini-omni-1.2-flash"
DEFAULT_LOCATION = "global"

MODEL_MAP = {
    "gemini-omni-1.2-flash": "gemini-omni-1.2-flash",
    "omni-1.2-flash": "gemini-omni-1.2-flash",
    "omni-1.2": "gemini-omni-1.2-flash",
    "1.2": "gemini-omni-1.2-flash",
    "flash-1.2": "gemini-omni-1.2-flash",
    "gemini-omni-flash-1.2": "gemini-omni-1.2-flash",
    "gemini-omni-flash-1.2-preview": "gemini-omni-1.2-flash",
    "omni-flash-1.2": "gemini-omni-1.2-flash",
}

DEPRECATED_MODELS = {
    "gemini-omni-flash-preview",
}

DEPRECATED_1_1_MODELS = {
    "gemini-omni-1.1-flash",
    "gemini-omni-1.1",
    "omni-1.1-flash",
    "omni-1.1",
    "flash-1.1",
    "1.1",
    "gemini-omni-1.1-flash-preview",
    "gemini-omni-flash-1.1-preview",
}

VALID_RESOLUTIONS = ["360p", "720p", "1080p", "4k"]
VALID_UPSCALE_RESOLUTIONS = ["720p", "1080p", "4k"]
VALID_ASPECT_RATIOS = ["16:9", "9:16"]
VALID_DURATIONS_1_2 = [f"{s}s" for s in range(3, 16)]
VALID_TASKS = [
    "text_to_video",
    "image_to_video",
    "reference_to_video",
    "edit",
    "extend",
    "upscale",
]

DEPRECATED_CONTROL_TAGS = (
    "<FIRST_FRAME>",
    "<LAST_FRAME>",
    "<IMAGE_REF_",
    "<VIDEO_REF_",
    "[# Sources",
    "[# References",
)

IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif",
}

VIDEO_MIME_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpg",
    ".wmv": "video/wmv",
    ".3gp": "video/3gpp",
    ".3gpp": "video/3gpp",
    ".flv": "video/x-flv",
}

AUTH_HELP_MESSAGE = (
    "Authenticate using Gemini Enterprise / Vertex AI (Application Default Credentials):\n"
    "  gcloud auth application-default login --billing-project YOUR_PROJECT_ID\n"
    "  export GOOGLE_CLOUD_PROJECT=\"YOUR_PROJECT_ID\"\n"
    "  export GOOGLE_CLOUD_LOCATION=\"global\"\n"
    "  export GOOGLE_GENAI_USE_ENTERPRISE=\"true\"\n"
    "  (or pass --enterprise --project \"YOUR_PROJECT_ID\" --location \"global\")\n\n"
    "Or authenticate with a Gemini Developer API key:\n"
    "  export GEMINI_API_KEY=\"your-api-key\"\n\n"
    "AGENT INSTRUCTION: Fail fast with zero fallbacks. Do NOT attempt rogue workarounds, "
    "mock video files, or silent fallbacks. Stop immediately, report this exact "
    "authentication error to the user, and ask them to configure credentials."
)


def resolve_model(model_name: str | None) -> str:
    """Resolve a model alias or canonical ID to a supported Gemini Omni model string."""
    if not model_name:
        return DEFAULT_MODEL
    key = model_name.strip()
    if key in DEPRECATED_MODELS:
        raise ValueError(
            f"Model '{key}' was shut down on October 22, 2026 "
            "(deprecated on Agent Platform November 6, 2026). "
            f"Use '{DEFAULT_MODEL}'."
        )
    if key in DEPRECATED_1_1_MODELS:
        raise ValueError(
            f"Model '{key}' is deprecated. Migrate to '{DEFAULT_MODEL}'."
        )
    if key not in MODEL_MAP:
        supported = ", ".join(sorted(MODEL_MAP.keys()))
        raise ValueError(
            f"Unsupported model '{key}'. Supported models and aliases: {supported}"
        )
    return MODEL_MAP[key]


def parse_duration_seconds(duration_str: str) -> int:
    """Parse a duration string such as '10s' into integer seconds."""
    cleaned = duration_str.strip().lower()
    if not cleaned.endswith("s") or not cleaned[:-1].isdigit():
        raise ValueError(
            f"Invalid duration '{duration_str}'. Expected whole seconds between '3s' and '15s' (for example '10s')."
        )
    return int(cleaned[:-1])


def check_deprecated_control_tags(prompt: str | None) -> list[str]:
    """Return any deprecated <FIRST_FRAME>/<IMAGE_REF_0> style control tags present in the prompt."""
    if not prompt:
        return []
    return [tag for tag in DEPRECATED_CONTROL_TAGS if tag in prompt]


def detect_mime_type(path: str) -> str:
    """Detect media MIME type from file extension or URI, failing fast on unsupported formats."""
    cleaned = path.strip()
    lower = cleaned.lower()
    if "youtube.com" in lower or "youtu.be" in lower:
        return "video/mp4"

    path_part = urlsplit(lower).path if "://" in lower else lower
    _, ext = os.path.splitext(path_part)
    if ext in IMAGE_MIME_TYPES:
        return IMAGE_MIME_TYPES[ext]
    if ext in VIDEO_MIME_TYPES:
        return VIDEO_MIME_TYPES[ext]

    if cleaned.startswith(("files/", "http://", "https://", "gs://")) and ext == "":
        return "application/octet-stream"

    supported = ", ".join(sorted([*IMAGE_MIME_TYPES.keys(), *VIDEO_MIME_TYPES.keys()]))
    raise ValueError(
        f"Unsupported input media format '{ext or '(none)'}' for '{path}'. Supported extensions: {supported}."
    )


def classify_input_media(inputs: list[str], task: str | None = None) -> tuple[list[str], list[str]]:
    """Classify input paths/URIs into (images, videos)."""
    images: list[str] = []
    videos: list[str] = []
    for item in inputs:
        mime = detect_mime_type(item)
        if mime.startswith("video/") or (
            mime == "application/octet-stream" and task in ("upscale", "edit", "extend")
        ):
            videos.append(item)
        else:
            images.append(item)
    return images, videos


def validate_video_request(args, model_id: str) -> None:
    """Validate CLI arguments against Gemini Omni 1.2 Flash constraints."""
    seconds = parse_duration_seconds(args.duration)

    if seconds < 3 or seconds > 15:
        raise ValueError(
            f"Duration '{args.duration}' is out of range for '{model_id}'. "
            "Supported durations are '3s' to '15s' (whole seconds)."
        )

    images, videos = classify_input_media(args.input or [], getattr(args, "task", None))

    if len(images) > 10:
        raise ValueError(
            f"Too many input images ({len(images)}). Gemini Omni supports up to 6 reference images "
            "in the Gemini API and up to 10 images on Vertex AI / Gemini Enterprise."
        )

    if args.task == "extend" and seconds > 10:
        raise ValueError(
            f"Duration '{args.duration}' is invalid for video extension (--task extend). "
            "Each extension turn supports '3s' to '10s'."
        )

    if args.task == "image_to_video" and len(images) == 2 and seconds > 10:
        raise ValueError(
            f"Duration '{args.duration}' is invalid for first-and-last-frame interpolation (2 input images). "
            "First-and-last-frame interpolation supports '3s' to '10s'."
        )

    if args.task == "reference_to_video":
        if seconds <= 10 and len(videos) > 3:
            raise ValueError(
                f"Too many reference videos ({len(videos)}) for a {args.duration} clip. "
                "Up to 3 reference videos (up to 3s each) are supported for 3s to 10s output videos."
            )
        if seconds > 10 and len(videos) > 1:
            raise ValueError(
                f"Too many reference videos ({len(videos)}) for a {args.duration} clip. "
                "At most 1 reference video (up to 3s long) is supported for 11s to 15s output videos."
            )

    if getattr(args, "background", False) and getattr(args, "store", None) is False:
        raise ValueError(
            "Background execution (--background) requires stored state and cannot be combined with '--no-store'."
        )

    if args.task == "upscale":
        if model_id != "gemini-omni-1.2-flash":
            raise ValueError(
                f"Video upscaling (--task upscale) is only supported by 'gemini-omni-1.2-flash', not '{model_id}'."
            )
        if not videos and not args.previous_interaction_id:
            raise ValueError(
                "Video upscaling (--task upscale) requires an input video (--input <video.mp4>) "
                "or --previous-interaction-id."
            )
        if not getattr(args, "resolution_explicit", False):
            raise ValueError(
                "Video upscaling (--task upscale) requires an explicit target --resolution "
                "('720p', '1080p', or '4k')."
            )
        if args.resolution not in VALID_UPSCALE_RESOLUTIONS:
            raise ValueError(
                f"Invalid upscale target resolution '{args.resolution}'. "
                "Supported upscale targets are '720p', '1080p', and '4k' "
                "(360p -> 720p/1080p; 720p -> 1080p/4k)."
            )


def build_interaction_kwargs(args, model_id: str) -> dict:
    """Build the request dictionary for client.interactions.create."""
    if args.task == "upscale":
        response_format: dict = {
            "type": "video",
            "resolution": args.resolution,
        }
        if args.delivery == "uri":
            response_format["delivery"] = "uri"
    else:
        response_format = {
            "type": "video",
            "resolution": args.resolution,
            "aspect_ratio": args.aspect_ratio,
            "duration": args.duration,
            "delivery": args.delivery,
        }

    if getattr(args, "gcs_uri", None):
        response_format["gcs_uri"] = args.gcs_uri

    if args.input:
        input_payload: list[dict] | str = []
        for media_path in args.input:
            mime = detect_mime_type(media_path)
            if mime == "application/octet-stream":
                media_type = (
                    "video"
                    if getattr(args, "task", None) in ("upscale", "edit", "extend")
                    else "image"
                )
            else:
                media_type = "video" if mime.startswith("video/") else "image"

            if media_path.startswith(("files/", "http://", "https://", "gs://")):
                entry: dict = {"type": media_type, "uri": media_path}
                if media_path.startswith("gs://") and mime != "application/octet-stream":
                    entry["mime_type"] = mime
                input_payload.append(entry)
            else:
                with open(media_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                input_payload.append(
                    {"type": media_type, "data": b64_data, "mime_type": mime}
                )
        if args.prompt:
            input_payload.append({"type": "text", "text": args.prompt})
    else:
        input_payload = args.prompt or ""

    kwargs: dict = {
        "model": model_id,
        "input": input_payload,
        "response_format": response_format,
    }

    gen_config: dict = {}
    if getattr(args, "task", None):
        gen_config["video_config"] = {"task": args.task}
    if getattr(args, "seed", None) is not None:
        gen_config["seed"] = args.seed
    if gen_config:
        kwargs["generation_config"] = gen_config

    if getattr(args, "previous_interaction_id", None):
        kwargs["previous_interaction_id"] = args.previous_interaction_id

    if getattr(args, "store", None) is not None:
        kwargs["store"] = args.store

    if getattr(args, "background", False):
        kwargs["background"] = True

    return kwargs


def init_client(args) -> Any:
    """Initialize Google GenAI Client with Gemini Enterprise / Vertex AI ADC or Gemini API Key."""
    import google.auth
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    env_enterprise = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").strip().lower() in (
        "true",
        "1",
        "yes",
    )
    env_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").strip().lower() in (
        "true",
        "1",
        "yes",
    )
    env_project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")

    use_enterprise = bool(
        getattr(args, "enterprise", False)
        or getattr(args, "vertexai", False)
        or getattr(args, "project", None) is not None
        or getattr(args, "location", None) is not None
        or env_enterprise
        or env_vertex
        or (env_project and not api_key)
    )

    if use_enterprise:
        try:
            credentials, default_project = google.auth.default()
        except Exception as e:
            print(
                f"Error: Failed to load Google Cloud Application Default Credentials for Gemini Enterprise / Vertex AI: {e}\n\n"
                f"{AUTH_HELP_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        quota_project = getattr(credentials, "quota_project_id", None)
        project = (
            getattr(args, "project", None)
            or env_project
            or default_project
            or quota_project
        )
        location = (
            getattr(args, "location", None)
            or os.environ.get("GOOGLE_CLOUD_LOCATION")
            or DEFAULT_LOCATION
        )

        if not project:
            print(
                "Error: Gemini Enterprise / Vertex AI requested (--enterprise, --vertexai, --project, "
                "or GOOGLE_GENAI_USE_ENTERPRISE=true), but no GCP Project ID was found. "
                "Pass --project <PROJECT_ID>, set GOOGLE_CLOUD_PROJECT, "
                "or run 'gcloud auth application-default login --billing-project <PROJECT_ID>'.\n\n"
                f"{AUTH_HELP_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        return genai.Client(
            enterprise=True,
            project=project,
            location=location,
            credentials=credentials,
        )

    if not api_key:
        print(
            "Error: Missing credentials. Neither Gemini Enterprise / Vertex AI "
            "(GOOGLE_CLOUD_PROJECT / --enterprise / ADC) nor GEMINI_API_KEY is configured.\n\n"
            f"{AUTH_HELP_MESSAGE}",
            file=sys.stderr,
        )
        sys.exit(1)

    return genai.Client(api_key=api_key)


def extract_video_from_interaction(client: Any, interaction) -> tuple[bytes | None, str | None]:
    """Extract video bytes or a Cloud Storage URI from an Interaction response."""
    output_video = getattr(interaction, "output_video", None)
    if output_video:
        if getattr(output_video, "data", None):
            raw = output_video.data
            return (base64.b64decode(raw) if isinstance(raw, str) else raw), None
        if getattr(output_video, "gcs_uri", None):
            return None, output_video.gcs_uri
        if getattr(output_video, "uri", None):
            uri = output_video.uri
            if uri.startswith("gs://"):
                return None, uri
            file_name = "files/" + uri.split("/")[-1] if not uri.startswith("files/") else uri
            for _ in range(120):
                file_info = client.files.get(name=file_name)
                state_name = getattr(getattr(file_info, "state", None), "name", "ACTIVE")
                if state_name == "ACTIVE":
                    break
                if state_name == "FAILED":
                    raise RuntimeError(f"Video file processing failed for {file_name}")
                time.sleep(5)
            return client.files.download(file=uri), None

    for step in getattr(interaction, "steps", []) or []:
        if getattr(step, "type", None) == "model_output":
            for block in getattr(step, "content", []) or []:
                if getattr(block, "type", None) == "video":
                    if getattr(block, "data", None):
                        raw = block.data
                        return (base64.b64decode(raw) if isinstance(raw, str) else raw), None
                    if getattr(block, "gcs_uri", None):
                        return None, block.gcs_uri
                    if getattr(block, "uri", None):
                        uri = block.uri
                        if uri.startswith("gs://"):
                            return None, uri
                        file_name = "files/" + uri.split("/")[-1] if not uri.startswith("files/") else uri
                        for _ in range(120):
                            file_info = client.files.get(name=file_name)
                            state_name = getattr(getattr(file_info, "state", None), "name", "ACTIVE")
                            if state_name == "ACTIVE":
                                break
                            if state_name == "FAILED":
                                raise RuntimeError(f"Video file processing failed for {file_name}")
                            time.sleep(5)
                        return client.files.download(file=uri), None

    return None, None


def extract_audio_track_to_wav(video_path: str, wav_path: str, sample_rate: int = 44100) -> None:
    """Extract synchronized audio from an MP4 video into a 44.1 kHz 16-bit stereo WAV file via ffmpeg."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError(
            "Error: '--extract-audio' requires 'ffmpeg' on PATH to extract the audio stream."
        )
    out_dir = os.path.dirname(os.path.abspath(wav_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ar",
        str(sample_rate),
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        wav_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed: {res.stderr.strip()}")


def run_video(client: Any, args, model_id: str, output_path: str) -> None:
    """Execute video generation, editing, extension, or upscaling via the Interactions API."""
    kwargs = build_interaction_kwargs(args, model_id)
    interaction = client.interactions.create(**kwargs)

    interaction_id = getattr(interaction, "id", None)
    if interaction_id:
        print(f"Interaction ID: {interaction_id}")

    if getattr(args, "background", False) and getattr(interaction, "status", None) in (
        "in_progress",
        "processing",
    ):
        print(f"Background interaction started (status: {interaction.status}).")
        return

    video_bytes, gcs_uri = extract_video_from_interaction(client, interaction)
    if gcs_uri and not video_bytes:
        print(f"Success! Video written to Cloud Storage: {gcs_uri}")
        return

    if not video_bytes:
        raise ValueError(
            f"No video data returned from Interactions API for model '{model_id}'."
        )

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(video_bytes)
    print(f"Success! Video saved to {output_path}")

    if getattr(args, "extract_audio", None):
        extract_audio_track_to_wav(output_path, args.extract_audio)
        print(f"Success! Synchronized stereo audio extracted to {args.extract_audio}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Gemini Omni CLI (scripts/omni.py): Generate, edit, interpolate, extend, and upscale "
            "videos with native synchronized audio using Gemini Omni 1.2 Flash (gemini-omni-1.2-flash) "
            "via the Interactions API."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "prompt_pos",
        nargs="?",
        default=None,
        help="Positional text prompt describing the video and synchronized audio (alternative to --prompt)",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        default=None,
        help="Text prompt describing the video scene, camera movement, dialogue, music, and sound effects",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="prompt_file",
        default=None,
        help="Read the video prompt from a text file",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--out",
        "--filename",
        dest="output",
        default=None,
        help="Output MP4 video file path (default: output.mp4)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=(
            f"Model ID or alias (default: {DEFAULT_MODEL}). "
            "Supported aliases: gemini-omni-1.2-flash, omni-1.2-flash, omni-1.2, 1.2, flash-1.2."
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        action="append",
        default=[],
        help=(
            "Input image (.jpg, .jpeg, .png, .webp, .heic, .heif) or video (.mp4, .mov [video/quicktime], "
            ".webm, .mpeg, .mpg, .wmv, .3gp, .flv) path, Files API URI (files/...), or Cloud Storage URI "
            "(gs://...) for frame animation, interpolation, reference generation, editing, extension, or "
            "upscaling (repeatable)."
        ),
    )
    parser.add_argument(
        "-r",
        "--resolution",
        choices=VALID_RESOLUTIONS,
        default=None,
        help="Video output resolution: 360p, 720p (default), 1080p, 4k",
    )
    parser.add_argument(
        "-a",
        "--aspect-ratio",
        choices=VALID_ASPECT_RATIOS,
        default=None,
        help="Video aspect ratio: 16:9 (default), 9:16",
    )
    parser.add_argument(
        "-d",
        "--duration",
        choices=VALID_DURATIONS_1_2,
        default=None,
        help="Video clip duration: 3s to 15s for gemini-omni-1.2-flash (default: 10s; 3s to 10s for extend or 2-frame interpolation)",
    )
    parser.add_argument(
        "-t",
        "--task",
        choices=VALID_TASKS,
        default=None,
        help=(
            "Optional task mode in generation_config.video_config.task: "
            "text_to_video, image_to_video, reference_to_video, edit, extend, or upscale"
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional integer seed in generation_config.seed for reproducible video generation",
    )
    parser.add_argument(
        "--delivery",
        choices=["inline", "uri"],
        default="inline",
        help="Video delivery mode: 'inline' (default) or 'uri' (recommended for videos > 4 MB / > 720p)",
    )
    parser.add_argument(
        "--gcs-uri",
        default=None,
        help="Optional Cloud Storage destination URI (gs://bucket/path/) for Vertex AI / Gemini Enterprise output",
    )
    parser.add_argument(
        "--previous-interaction-id",
        default=None,
        help="Continue from a prior interaction ID for stateful multi-turn video editing, extension, or upscaling",
    )
    parser.add_argument(
        "--store",
        dest="store",
        action="store_true",
        default=None,
        help="Store interaction state on the server (required for follow-up --previous-interaction-id turns)",
    )
    parser.add_argument(
        "--no-store",
        dest="store",
        action="store_false",
        help="Run a stateless synchronous request (store=false) to enable server-side unary optimization",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run interaction asynchronously in the background (background=true, requires store=true)",
    )
    parser.add_argument(
        "--extract-audio",
        default=None,
        help="Optional output WAV path to extract the generated video's synchronized audio as 44.1 kHz 16-bit stereo PCM via ffmpeg",
    )
    parser.add_argument(
        "--enterprise",
        action="store_true",
        help="Use Gemini Enterprise / Vertex AI with Application Default Credentials (ADC)",
    )
    parser.add_argument(
        "--vertexai",
        action="store_true",
        help="Alias for --enterprise (Vertex AI Application Default Credentials)",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="GCP Project ID for Gemini Enterprise / Vertex AI (defaults to GOOGLE_CLOUD_PROJECT or ADC billing project)",
    )
    parser.add_argument(
        "--location",
        default=None,
        help=f"GCP Location for Gemini Enterprise / Vertex AI (defaults to GOOGLE_CLOUD_LOCATION or '{DEFAULT_LOCATION}')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate model, media inputs, durations, and print the Interactions API request payload without calling the network",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    prompt_text = args.prompt or args.prompt_pos
    if args.prompt_file:
        with open(args.prompt_file, "r", encoding="utf-8") as pf:
            file_text = pf.read().strip()
        prompt_text = f"{file_text}\n{prompt_text}".strip() if prompt_text else file_text

    if not prompt_text and args.task != "upscale":
        print(
            "Error: A text prompt is required (except when running '--task upscale'). "
            "Pass --prompt \"...\", a positional prompt, or --file <prompt.txt>.",
            file=sys.stderr,
        )
        sys.exit(2)
    args.prompt = prompt_text

    try:
        model_id = resolve_model(args.model)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    args.resolution_explicit = args.resolution is not None
    if args.resolution is None:
        args.resolution = "720p"

    args.aspect_ratio_explicit = args.aspect_ratio is not None
    if args.aspect_ratio is None:
        args.aspect_ratio = "16:9"

    args.duration_explicit = args.duration is not None
    if args.duration is None:
        args.duration = "10s"

    try:
        validate_video_request(args, model_id)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    found_tags = check_deprecated_control_tags(args.prompt)
    if found_tags:
        print(
            f"Warning: Deprecated control tags detected in prompt ({', '.join(found_tags)}). "
            "Gemini Omni 1.2 Flash deprecates <FIRST_FRAME>, <LAST_FRAME>, <IMAGE_REF_0>, and <VIDEO_REF_0> "
            "tags; describe how each image or video should be used in natural language instead "
            "(and optionally set --task).",
            file=sys.stderr,
        )

    output_path = args.output or "output.mp4"
    print(f"Model: {model_id} ({args.model})")
    if args.task == "upscale":
        print(f"Task: upscale | Target Resolution: {args.resolution}")
    else:
        task_label = args.task or "auto (inferred from prompt)"
        print(
            f"Task: {task_label} | Resolution: {args.resolution} | "
            f"Aspect Ratio: {args.aspect_ratio} | Duration: {args.duration}"
        )
    if args.input:
        print(f"Input Media ({len(args.input)}): {args.input}")
    print(f"Output: {output_path}")

    if args.dry_run:
        preview_kwargs = build_interaction_kwargs(args, model_id)
        print(json.dumps(preview_kwargs, indent=2))
        print("Dry run validation succeeded.")
        return 0

    client = init_client(args)
    from google.genai.errors import APIError

    try:
        run_video(client, args, model_id, output_path)
        return 0
    except APIError as e:
        print(
            f"API Error running video generation with {model_id}: {e}\n\n"
            f"{AUTH_HELP_MESSAGE}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(
            f"Error running video generation with {model_id}: {e}\n"
            "AGENT INSTRUCTION: Do NOT attempt rogue workarounds or silent fallbacks. Report this exact error to the user.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
