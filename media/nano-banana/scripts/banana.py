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
import json
import os
import sys
from typing import Any
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module=r"google\.genai.*")

DEFAULT_LOCATION = "global"

MODEL_MAP = {
    "nano-banana-2.1": "gemini-nano-banana-2.1",
    "nano-banana-2-1": "gemini-nano-banana-2.1",
    "nano-banana-2": "gemini-3.1-flash-image",
    "nano-banana-2-lite": "gemini-3.1-flash-lite-image",
    "nano-banana-lite": "gemini-3.1-flash-lite-image",
    "nano-banana-pro": "gemini-3-pro-image",
    "gemini-nano-banana-2.1": "gemini-nano-banana-2.1",
    "gemini-3.1-flash-image": "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image": "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image": "gemini-3-pro-image",
}

VALID_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3",
    "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

EXTENDED_ASPECT_RATIOS = {"1:4", "4:1", "1:8", "8:1"}

IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif",
}

AUTH_REMEDIATION_MESSAGE = (
    "Authentication guidance:\n"
    "  Option 1: Vertex AI / Gemini Enterprise (Application Default Credentials):\n"
    "    gcloud auth application-default login --billing-project YOUR_PROJECT_ID\n"
    "    export GOOGLE_CLOUD_PROJECT=\"YOUR_PROJECT_ID\"\n"
    "    export GOOGLE_CLOUD_LOCATION=\"global\"\n"
    "    export GOOGLE_GENAI_USE_ENTERPRISE=\"true\"\n"
    "  Option 2: Gemini Developer API (API Key):\n"
    "    export GEMINI_API_KEY=\"your-api-key\"\n"
    "CRITICAL FOR AGENTS: Fail fast. Always default to location='global' unless explicitly asked otherwise. "
    "Do NOT attempt unauthorized workarounds, fallback image generators, "
    "or procedural placeholder files. Stop immediately, report this exact authentication error to the user, "
    "and ask them to configure credentials."
)


def resolve_model(model_arg: str) -> str:
    """Resolve CLI model alias to canonical model ID and reject retired or shut-down models."""
    normalized = model_arg.strip()
    if normalized.startswith("imagen-"):
        print(
            f"Error: Imagen models ('{normalized}') shut down on August 17, 2026. "
            "Migrate to 'nano-banana-2.1' (gemini-nano-banana-2.1) or 'nano-banana-pro' (gemini-3-pro-image).",
            file=sys.stderr,
        )
        sys.exit(1)

    if normalized in ("nano-banana", "gemini-2.5-flash-image") or normalized.endswith("-preview"):
        print(
            f"Error: Legacy or retired model '{normalized}' is not supported. "
            "Migrate to 'nano-banana-2.1' (gemini-nano-banana-2.1) or 'nano-banana-2-lite' (gemini-3.1-flash-lite-image).",
            file=sys.stderr,
        )
        sys.exit(1)

    if normalized not in MODEL_MAP:
        print(
            f"Error: Unsupported model '{normalized}'. Valid choices: {', '.join(MODEL_MAP.keys())}.",
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


def save_output_image(filename: str, img_bytes: bytes) -> None:
    """Write image bytes to disk after ensuring parent directories exist."""
    out_dir = os.path.dirname(os.path.abspath(filename))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(filename, "wb") as f:
        f.write(img_bytes)


def normalize_image_size(resolution: str, api_mode: str = "interactions") -> str:
    """Normalize resolution flag to the exact value expected by Interactions API vs. Models API."""
    if resolution in ("512", "512px"):
        return "512" if api_mode == "interactions" else "512px"
    return resolution


def validate_capabilities(args, model_id: str) -> None:
    """Validate requested CLI arguments against model and API capability constraints."""
    if len(args.input_image) > 14:
        print("Error: Maximum of 14 input/reference images allowed.", file=sys.stderr)
        sys.exit(1)

    for img_path in args.input_image:
        try:
            detect_mime_type(img_path)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if args.api == "models":
        if getattr(args, "previous_interaction_id", None):
            print(
                "Error: '--previous-interaction-id' requires '--api interactions' (not '--api models').",
                file=sys.stderr,
            )
            sys.exit(1)
        if getattr(args, "store", None) is not None:
            print(
                "Error: '--store' / '--no-store' requires '--api interactions' (not '--api models').",
                file=sys.stderr,
            )
            sys.exit(1)

    if args.resolution in ("2K", "4K") and model_id == "gemini-3.1-flash-lite-image":
        print(
            f"Error: Resolution '{args.resolution}' is not supported by {args.model}. "
            "2K and 4K output requires 'nano-banana-2.1', 'nano-banana-2', or 'nano-banana-pro'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.resolution in ("512px", "512") and model_id != "gemini-3.1-flash-image":
        print(
            f"Error: Resolution '{args.resolution}' is only supported by 'nano-banana-2' (gemini-3.1-flash-image), "
            f"not '{args.model}' ({model_id}). Use '1K', '2K', or '4K'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.aspect_ratio in EXTENDED_ASPECT_RATIOS and model_id == "gemini-3-pro-image":
        print(
            f"Error: Aspect ratio '{args.aspect_ratio}' is only supported by "
            "'nano-banana-2.1', 'nano-banana-2', and 'nano-banana-2-lite'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if (args.search or args.image_search) and model_id == "gemini-3.1-flash-lite-image":
        print(
            f"Error: Search grounding is not supported by {args.model}. "
            "Use 'nano-banana-2.1', 'nano-banana-2', or 'nano-banana-pro' for Google Search grounding.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.image_search and model_id not in ("gemini-nano-banana-2.1", "gemini-3.1-flash-image"):
        print(
            "Error: Google Image Search Grounding (--image-search) is only supported by "
            "'nano-banana-2.1' and 'nano-banana-2'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.thinking_level == "medium" and model_id != "gemini-nano-banana-2.1":
        print(
            f"Error: Thinking level 'medium' is only supported by 'nano-banana-2.1' (gemini-nano-banana-2.1), "
            f"not {args.model}.",
            file=sys.stderr,
        )
        sys.exit(1)


def build_interaction_kwargs(
    args,
    model_id: str,
    image_size: str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Build the request dictionary for client.interactions.create."""
    response_format = {
        "type": "image",
        "aspect_ratio": args.aspect_ratio,
        "image_size": image_size,
    }

    tools: list[dict[str, Any]] = []
    if args.image_search:
        tools.append({"type": "google_search", "search_types": ["web_search", "image_search"]})
    elif args.search:
        tools.append({"type": "google_search"})

    generation_config: dict[str, Any] = {}
    if args.thinking_level:
        generation_config["thinking_level"] = args.thinking_level

    if args.input_image:
        input_payload: list[dict[str, Any]] | str = []
        for img_path in args.input_image:
            mime = detect_mime_type(img_path)
            if dry_run and not os.path.isfile(img_path):
                b64_data = base64.b64encode(b"dry-run-placeholder").decode("utf-8")
            else:
                with open(img_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
            input_payload.append({"type": "image", "data": b64_data, "mime_type": mime})
        input_payload.append({"type": "text", "text": args.prompt})
    else:
        input_payload = args.prompt

    kwargs: dict[str, Any] = {
        "model": model_id,
        "input": input_payload,
        "response_format": response_format,
    }
    if tools:
        kwargs["tools"] = tools
    if generation_config:
        kwargs["generation_config"] = generation_config
    if getattr(args, "previous_interaction_id", None):
        kwargs["previous_interaction_id"] = args.previous_interaction_id
    if getattr(args, "store", None) is not None:
        kwargs["store"] = args.store

    return kwargs


def build_models_config(args, image_size: str):
    """Build GenerateContentConfig for Models API requests."""
    from google.genai import types

    config_kwargs: dict[str, Any] = {
        "response_modalities": ["TEXT", "IMAGE"],
        "image_config": types.ImageConfig(
            aspect_ratio=args.aspect_ratio,
            image_size=image_size,
        ),
    }

    if args.thinking_level:
        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_level=args.thinking_level)

    if args.image_search:
        config_kwargs["tools"] = [
            types.Tool(
                google_search=types.GoogleSearch(
                    search_types=types.SearchTypes(
                        web_search=types.WebSearch(),
                        image_search=types.ImageSearch(),
                    )
                )
            )
        ]
    elif args.search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    return types.GenerateContentConfig(**config_kwargs)


def decode_media_bytes(raw: str | bytes) -> bytes:
    """Decode base64 string or pass through raw bytes safely."""
    return base64.b64decode(raw) if isinstance(raw, str) else raw


def extract_image_from_interaction(interaction) -> bytes | None:
    """Extract output image bytes from an Interactions API response."""
    output_image = getattr(interaction, "output_image", None)
    if output_image and getattr(output_image, "data", None):
        return decode_media_bytes(output_image.data)

    for step in getattr(interaction, "steps", None) or []:
        if getattr(step, "type", "") == "model_output":
            for block in getattr(step, "content", None) or []:
                if getattr(block, "type", "") == "image" and getattr(block, "data", None):
                    return decode_media_bytes(block.data)

    return None


def extract_image_from_models_response(response) -> bytes | None:
    """Extract the first non-thought inline image from a generate_content response."""
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    content = getattr(candidates[0], "content", None)
    parts = getattr(content, "parts", None) or []
    for part in parts:
        if getattr(part, "thought", False):
            continue
        inline_data = getattr(part, "inline_data", None)
        if inline_data and getattr(inline_data, "data", None):
            return decode_media_bytes(inline_data.data)
    return None


def init_client(args):
    """Initialize Google Gen AI client with Enterprise/Vertex AI ADC or Gemini API Key."""
    import google.auth
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    env_enterprise = os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").strip().lower() in ("true", "1", "yes")
    env_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").strip().lower() in ("true", "1", "yes")
    env_project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")

    use_enterprise = (
        args.vertexai
        or args.enterprise
        or args.project is not None
        or args.location is not None
        or env_enterprise
        or env_vertex
        or (not api_key and bool(env_project))
    )

    if use_enterprise:
        try:
            credentials, default_project = google.auth.default()
        except Exception as e:
            print(
                f"Error: Failed to load Google Cloud Application Default Credentials for Vertex AI / Gemini Enterprise: {e}\n"
                f"{AUTH_REMEDIATION_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        quota_project = getattr(credentials, "quota_project_id", None)
        project = args.project or env_project or default_project or quota_project
        location = args.location or os.environ.get("GOOGLE_CLOUD_LOCATION") or DEFAULT_LOCATION

        if not project:
            print(
                "Error: Vertex AI / Gemini Enterprise requested or inferred, but no GCP Project ID was found. "
                "Pass --project <PROJECT_ID>, set GOOGLE_CLOUD_PROJECT, "
                "or run 'gcloud auth application-default login --billing-project <PROJECT_ID>'.\n"
                f"{AUTH_REMEDIATION_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        return genai.Client(enterprise=True, project=project, location=location, credentials=credentials)

    if not api_key:
        print(
            "Error: GEMINI_API_KEY environment variable is not set and Vertex AI / Gemini Enterprise is not configured.\n"
            f"{AUTH_REMEDIATION_MESSAGE}",
            file=sys.stderr,
        )
        sys.exit(1)

    return genai.Client(api_key=api_key)


def run_image(client: Any, args, model_id: str, image_size: str, models_config: Any = None) -> None:
    """Execute image generation or editing against Interactions API or Models API and write output."""
    if args.api == "interactions":
        kwargs = build_interaction_kwargs(args, model_id, image_size)
        interaction = client.interactions.create(**kwargs)
        interaction_id = getattr(interaction, "id", None)
        if interaction_id:
            print(f"Interaction ID: {interaction_id}")

        img_bytes = extract_image_from_interaction(interaction)
        if not img_bytes:
            raise ValueError("No image returned from Interactions API response.")
        save_output_image(args.filename, img_bytes)
    else:
        from PIL import Image

        contents: list[Any] = []
        for img_path in args.input_image:
            detect_mime_type(img_path)
            with Image.open(img_path) as img:
                img.load()
                contents.append(img.copy())
        contents.append(args.prompt)

        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=models_config,
        )
        img_bytes = extract_image_from_models_response(response)
        if not img_bytes:
            raise ValueError("No image data found in generate_content response candidates.")
        save_output_image(args.filename, img_bytes)

    print(f"Success! Image saved to {args.filename}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate, edit, and transform images using Google Nano Banana foundation models.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-p", "--prompt", required=True, help="Text prompt describing the image to generate or edit")
    parser.add_argument(
        "-f",
        "--filename",
        "-o",
        "--out",
        "--output",
        dest="filename",
        required=True,
        help="Output image filename (such as output.png)",
    )
    parser.add_argument("-i", "--input-image", action="append", default=[], help="Path to input/reference image(s) (up to 14)")
    parser.add_argument(
        "-m",
        "--model",
        default="nano-banana-2.1",
        help=(
            "Model selection (default: nano-banana-2.1, alias nano-banana-2-1):\n"
            "  nano-banana-2.1, nano-banana-2-lite, nano-banana-2, nano-banana-pro"
        ),
    )
    parser.add_argument(
        "-r",
        "--resolution",
        choices=["512px", "512", "1K", "2K", "4K"],
        default="1K",
        help="Output resolution (default: 1K; 512 / 512px is only supported on nano-banana-2)",
    )
    parser.add_argument(
        "-a",
        "--aspect-ratio",
        choices=VALID_ASPECT_RATIOS,
        default="1:1",
        help="Output aspect ratio (default: 1:1)",
    )
    parser.add_argument(
        "--thinking-level",
        choices=["minimal", "medium", "high"],
        help="Thinking process level: minimal, medium (Nano Banana 2.1 only, default), or high",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Enable Google Search grounding (Banana 2.1, Banana 2, and Banana Pro)",
    )
    parser.add_argument(
        "--image-search",
        action="store_true",
        help="Enable Google Image Search grounding (Banana 2.1 and Banana 2)",
    )
    parser.add_argument(
        "--previous-interaction-id",
        default=None,
        help="Continue from a prior interaction ID for multi-turn conversational image editing (Interactions API only)",
    )
    parser.add_argument(
        "--store",
        dest="store",
        action="store_true",
        default=None,
        help="Store interaction state on the server for follow-up --previous-interaction-id turns",
    )
    parser.add_argument(
        "--no-store",
        dest="store",
        action="store_false",
        help="Run a stateless request (store=false)",
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
        help="Validate model capabilities and configuration without calling the API",
    )
    parser.add_argument(
        "--enterprise",
        action="store_true",
        help="Force Gemini Enterprise / Vertex AI authentication via Application Default Credentials",
    )
    parser.add_argument(
        "--vertexai",
        action="store_true",
        help="Alias for --enterprise (Vertex AI Application Default Credentials)",
    )
    parser.add_argument("--project", help="GCP Project ID for Vertex AI / Gemini Enterprise (defaults to GOOGLE_CLOUD_PROJECT or ADC billing project)")
    parser.add_argument("--location", help=f"GCP Location for Vertex AI / Gemini Enterprise (default: GOOGLE_CLOUD_LOCATION or {DEFAULT_LOCATION})")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    model_id = resolve_model(args.model)

    validate_capabilities(args, model_id)
    image_size = normalize_image_size(args.resolution, args.api)

    print(f"Model: {model_id} ({args.model})")
    print(f"Resolution: {args.resolution} (API: {image_size}) | Aspect Ratio: {args.aspect_ratio}")
    if args.input_image:
        print(f"Reference Images ({len(args.input_image)}): {args.input_image}")
    print(f"Output: {args.filename}")

    models_config = build_models_config(args, image_size) if args.api == "models" else None

    if args.dry_run:
        if args.api == "interactions":
            preview = build_interaction_kwargs(args, model_id, image_size, dry_run=True)
            print(json.dumps(preview, indent=2))
        print("Dry run validation succeeded.")
        return 0

    client = init_client(args)
    from google.genai.errors import APIError

    try:
        run_image(client, args, model_id, image_size, models_config)
        return 0
    except APIError as e:
        print(f"API Error generating image with {model_id}: {e}\n{AUTH_REMEDIATION_MESSAGE}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating image with {model_id}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
