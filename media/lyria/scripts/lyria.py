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
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module=r"google\.genai.*")

MODEL_MAP = {
    "lyria-3.5": "lyria-3.5",
    "3.5": "lyria-3.5",
    "lyria-3-clip": "lyria-3-clip-preview",
    "lyria-3-clip-preview": "lyria-3-clip-preview",
    "clip": "lyria-3-clip-preview",
    "lyria-clip": "lyria-3-clip-preview",
    "lyria-3-pro": "lyria-3-pro-preview",
    "lyria-3-pro-preview": "lyria-3-pro-preview",
    "pro": "lyria-3-pro-preview",
    "lyria-pro": "lyria-3-pro-preview",
}

RETIRED_MODELS = {
    "lyria-002",
    "lyria-realtime-exp",
}

IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif",
}

AUTH_HELP_MESSAGE = (
    "Authenticate using one of the following methods:\n"
    "  1. Vertex AI / Gemini Enterprise (ADC):\n"
    "     gcloud auth application-default login\n"
    "     export GOOGLE_CLOUD_PROJECT=\"your-gcp-project-id\"\n"
    "     export GOOGLE_CLOUD_LOCATION=\"global\"\n"
    "     export GOOGLE_GENAI_USE_ENTERPRISE=\"true\"\n"
    "     (or pass --enterprise --project \"your-gcp-project-id\" --location \"global\")\n"
    "  2. Gemini Developer API:\n"
    "     export GEMINI_API_KEY=\"your-api-key\"\n\n"
    "AGENT INSTRUCTION: Do NOT attempt rogue workarounds, mock audio files, or silent fallbacks. "
    "Stop immediately, report this exact authentication error to the user, and ask them to configure credentials."
)


def resolve_model(model_arg: str) -> str:
    """Resolve CLI model alias to canonical Lyria model ID and fail fast on invalid or retired models."""
    normalized = model_arg.strip()
    if normalized in RETIRED_MODELS:
        print(
            f"Error: Legacy or retired model '{normalized}' is not supported. "
            "Use 'lyria-3.5', 'lyria-3-clip-preview', or 'lyria-3-pro-preview'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if normalized not in MODEL_MAP:
        valid_choices = ", ".join(MODEL_MAP.keys())
        print(
            f"Error: Unsupported model '{normalized}'. Valid choices: {valid_choices}.",
            file=sys.stderr,
        )
        sys.exit(1)

    return MODEL_MAP[normalized]


def detect_mime_type(img_path: str) -> str:
    """Map supported input image file extensions to MIME types, failing fast otherwise."""
    _, ext = os.path.splitext(img_path.lower())
    if ext not in IMAGE_MIME_TYPES:
        supported = ", ".join(sorted(IMAGE_MIME_TYPES.keys()))
        raise ValueError(
            f"Unsupported input image format '{ext or '(none)'}' for '{img_path}'. Supported: {supported}."
        )
    return IMAGE_MIME_TYPES[ext]


def resolve_audio_format(
    filename: str,
    explicit_format: str | None,
    model_id: str,
    api_mode: str,
) -> str:
    """Resolve output audio container format and enforce model, extension, and API constraints."""
    lower_name = filename.lower()
    if explicit_format is None:
        resolved = "wav" if lower_name.endswith(".wav") else "mp3"
    else:
        resolved = explicit_format
        if explicit_format == "mp3" and lower_name.endswith(".wav"):
            print(
                f"Error: Output filename '{filename}' ends with '.wav' but '--format mp3' was explicitly requested. "
                "Remove '--format mp3' or use a '.mp3' filename.",
                file=sys.stderr,
            )
            sys.exit(1)
        if explicit_format == "wav" and lower_name.endswith(".mp3"):
            print(
                f"Error: Output filename '{filename}' ends with '.mp3' but '--format wav' was explicitly requested. "
                "Use a '.wav' filename or pass '--format mp3'.",
                file=sys.stderr,
            )
            sys.exit(1)

    if resolved == "wav" and model_id != "lyria-3.5":
        print(
            f"Error: WAV output is only supported on 'lyria-3.5', not '{model_id}'. "
            f"'{model_id}' outputs MP3 audio only.",
            file=sys.stderr,
        )
        sys.exit(1)

    if resolved == "wav" and api_mode == "models":
        print(
            "Error: WAV output via response_format requires '--api interactions' (not '--api models').",
            file=sys.stderr,
        )
        sys.exit(1)

    return resolved


def validate_capabilities(args, model_id: str) -> str:
    """Validate CLI inputs against Lyria constraints and return the resolved audio format."""
    if len(args.input_image) > 10:
        print("Error: Maximum of 10 input images allowed for Lyria 3.", file=sys.stderr)
        sys.exit(1)

    for img_path in args.input_image:
        try:
            detect_mime_type(img_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    return resolve_audio_format(args.filename, args.format, model_id, args.api)


def save_binary_file(filename: str, data: bytes) -> None:
    """Write binary output bytes to disk after creating parent directories."""
    out_dir = os.path.dirname(os.path.abspath(filename))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(filename, "wb") as f:
        f.write(data)


def save_text_file(filename: str, text: str) -> None:
    """Write UTF-8 text output to disk after creating parent directories."""
    out_dir = os.path.dirname(os.path.abspath(filename))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def build_models_config():
    """Build GenerateContentConfig requesting audio and text modalities."""
    from google.genai import types

    return types.GenerateContentConfig(response_modalities=["AUDIO", "TEXT"])


def init_client(args):
    """Initialize Google GenAI Client with explicit API Key or Gemini Enterprise / Vertex AI ADC."""
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
        args.vertexai
        or args.enterprise
        or args.project is not None
        or args.location is not None
        or env_enterprise
        or env_vertex
        or (env_project and not api_key)
    )

    if use_enterprise:
        try:
            credentials, default_project = google.auth.default()
        except Exception as e:
            print(
                f"Error: Failed to load Google Cloud Application Default Credentials for Vertex AI / Gemini Enterprise: {e}\n\n"
                f"{AUTH_HELP_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        project = args.project or env_project or default_project
        location = (
            args.location
            or os.environ.get("GOOGLE_CLOUD_LOCATION")
            or "global"
        )

        if not project:
            print(
                "Error: Vertex AI / Gemini Enterprise requested (--enterprise, --vertexai, --project, "
                "or GOOGLE_GENAI_USE_ENTERPRISE=true), but no GCP Project ID was found. "
                "Pass --project <PROJECT_ID> or set GOOGLE_CLOUD_PROJECT.\n\n"
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
            "Error: GEMINI_API_KEY environment variable is not set, and Vertex AI / Gemini Enterprise credentials "
            "(GOOGLE_CLOUD_PROJECT / ADC) are not configured.\n\n"
            f"{AUTH_HELP_MESSAGE}",
            file=sys.stderr,
        )
        sys.exit(1)

    return genai.Client(api_key=api_key)


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate music, soundtrack themes, and songs using Google Lyria foundation models.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--prompt",
        required=True,
        help="Text prompt describing the music to generate",
    )
    parser.add_argument(
        "-f",
        "--filename",
        "--out",
        "-o",
        dest="filename",
        default="music.mp3",
        help="Output audio filename (default: music.mp3)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="lyria-3.5",
        help=(
            "Model selection (default: lyria-3.5):\n"
            "  lyria-3.5 (alias 3.5)\n"
            "  lyria-3-clip-preview (aliases lyria-3-clip, clip, lyria-clip)\n"
            "  lyria-3-pro-preview (aliases lyria-3-pro, pro, lyria-pro)"
        ),
    )
    parser.add_argument(
        "-i",
        "--input-image",
        action="append",
        default=[],
        help="Path to input image(s) for visual mood inspiration (up to 10)",
    )
    parser.add_argument(
        "--format",
        choices=["mp3", "wav"],
        default=None,
        help="Audio output format (default: inferred from .wav filename, otherwise mp3; wav requires lyria-3.5)",
    )
    parser.add_argument(
        "--lyrics-file",
        help="Path to save generated lyrics and song structure text",
    )
    parser.add_argument(
        "--api",
        choices=["interactions", "models"],
        default="interactions",
        help="Underlying API method: 'interactions' (Interactions API, default) or 'models' (generate_content)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate model selection, audio format, and inputs without calling the API",
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
        help="GCP Project ID for Vertex AI / Gemini Enterprise (defaults to GOOGLE_CLOUD_PROJECT)",
    )
    parser.add_argument(
        "--location",
        default=None,
        help="GCP Location for Vertex AI / Gemini Enterprise (defaults to GOOGLE_CLOUD_LOCATION or 'global')",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    model_id = resolve_model(args.model)
    audio_format = validate_capabilities(args, model_id)

    print(f"Model: {model_id} ({args.model})")
    print(f"Output: {args.filename} (Format: {audio_format})")
    if args.input_image:
        print(f"Reference Images ({len(args.input_image)}): {args.input_image}")
    print(f"Prompt: {args.prompt}")

    models_config = build_models_config() if args.api == "models" else None

    if args.dry_run:
        print("Dry run validation succeeded.")
        return

    client = init_client(args)

    from google.genai.errors import APIError
    from PIL import Image

    audio_bytes = None
    lyrics_text = None

    try:
        if args.api == "interactions":
            if args.input_image:
                input_payload = [{"type": "text", "text": args.prompt}]
                for img_path in args.input_image:
                    mime_type = detect_mime_type(img_path)
                    with open(img_path, "rb") as img_file:
                        b64_data = base64.b64encode(img_file.read()).decode("utf-8")
                    input_payload.append(
                        {
                            "type": "image",
                            "mime_type": mime_type,
                            "data": b64_data,
                        }
                    )
            else:
                input_payload = args.prompt

            kwargs = {"model": model_id, "input": input_payload}
            if audio_format == "wav":
                kwargs["response_format"] = {
                    "type": "audio",
                    "mime_type": "audio/wav",
                }

            interaction = client.interactions.create(**kwargs)

            gen_audio = getattr(interaction, "output_audio", None)
            if gen_audio and getattr(gen_audio, "data", None):
                raw_audio = gen_audio.data
                audio_bytes = (
                    base64.b64decode(raw_audio)
                    if isinstance(raw_audio, str)
                    else raw_audio
                )

            lyrics_text = getattr(interaction, "output_text", None)

            if not audio_bytes and hasattr(interaction, "steps"):
                lyrics_parts = []
                for step in getattr(interaction, "steps", []):
                    if getattr(step, "type", None) == "model_output":
                        for block in getattr(step, "content", []):
                            b_type = getattr(block, "type", None)
                            if b_type == "audio" and getattr(block, "data", None):
                                raw_block = block.data
                                audio_bytes = (
                                    base64.b64decode(raw_block)
                                    if isinstance(raw_block, str)
                                    else raw_block
                                )
                            elif b_type == "text" and getattr(block, "text", None):
                                lyrics_parts.append(block.text)
                if not lyrics_text and lyrics_parts:
                    lyrics_text = "\n".join(lyrics_parts)
        else:
            contents = [args.prompt]
            for img_path in args.input_image:
                with Image.open(img_path) as img:
                    img.load()
                    contents.append(img.copy())

            response = client.models.generate_content(
                model=model_id,
                contents=contents,
                config=models_config,
            )

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        raw_data = part.inline_data.data
                        audio_bytes = (
                            base64.b64decode(raw_data)
                            if isinstance(raw_data, str)
                            else raw_data
                        )
                    elif part.text:
                        lyrics_text = part.text

        if not audio_bytes:
            raise ValueError(f"No audio data returned from Lyria 3 model {model_id}.")

        save_binary_file(args.filename, audio_bytes)
        print(f"Success! Audio saved to {args.filename}")

        if lyrics_text:
            print("\nGenerated Lyrics / Structure:")
            print(lyrics_text)
            if args.lyrics_file:
                save_text_file(args.lyrics_file, lyrics_text)
                print(f"Lyrics saved to {args.lyrics_file}")

    except APIError as e:
        print(
            f"API Error generating music with {model_id}: {e}\n\n"
            f"{AUTH_HELP_MESSAGE}",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(
            f"Error generating music with {model_id}: {e}\n"
            "AGENT INSTRUCTION: Do NOT attempt rogue workarounds or silent fallbacks. Report this exact error to the user.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
