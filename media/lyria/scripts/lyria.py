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
#     "pillow>=10.0.0",
#     "google-auth>=2.0.0",
# ]
# ///

import argparse
import base64
import os
import sys
from PIL import Image
import google.auth
from google import genai
from google.genai.errors import APIError

MODEL_MAP = {
    "lyria-3.5": "lyria-3.5",
    "3.5": "lyria-3.5",
    "lyria-3-clip": "lyria-3-clip-preview",
    "lyria-3-clip-preview": "lyria-3-clip-preview",
    "lyria-3-pro-preview": "lyria-3-pro-preview",
    "clip": "lyria-3-clip-preview",
    "pro": "lyria-3-pro-preview",
    "lyria-clip": "lyria-3-clip-preview",
    "lyria-pro": "lyria-3-pro-preview",
}

AUTH_HELP_MESSAGE = (
    "Authenticate using one of the following methods:\n"
    "  1. Vertex AI / Gemini Enterprise (ADC):\n"
    "     gcloud auth application-default login\n"
    "     export GOOGLE_CLOUD_PROJECT=\"your-gcp-project-id\"\n"
    "     export GOOGLE_CLOUD_LOCATION=\"us-central1\"\n"
    "     (or pass --vertexai --project \"your-gcp-project-id\" --location \"us-central1\")\n"
    "  2. Gemini Developer API:\n"
    "     export GEMINI_API_KEY=\"your-api-key\"\n\n"
    "AGENT INSTRUCTION: Do NOT attempt rogue workarounds, mock audio files, or silent fallbacks. "
    "Stop immediately, report this exact authentication error to the user, and ask them to configure credentials."
)


def init_client(args):
    """Initialize Google GenAI Client with explicit API Key or Vertex AI ADC (fail-fast, no silent fallbacks)."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    env_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").strip().lower() in (
        "true",
        "1",
        "yes",
    )
    env_project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")

    use_vertex = bool(
        args.vertexai
        or args.project is not None
        or env_vertex
        or (env_project and not api_key)
    )

    if use_vertex:
        try:
            credentials, default_project = google.auth.default()
        except Exception as e:
            print(
                f"Error: Failed to load Google Cloud Application Default Credentials for Vertex AI: {e}\n\n"
                f"{AUTH_HELP_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        project = args.project or env_project or default_project
        location = (
            args.location
            or os.environ.get("GOOGLE_CLOUD_LOCATION")
            or "us-central1"
        )

        if not project:
            print(
                "Error: Vertex AI requested (--vertexai, --project, or GOOGLE_GENAI_USE_VERTEXAI=true), "
                "but no GCP Project ID was found. Pass --project <PROJECT_ID> or set GOOGLE_CLOUD_PROJECT.\n\n"
                f"{AUTH_HELP_MESSAGE}",
                file=sys.stderr,
            )
            sys.exit(1)

        return genai.Client(
            vertexai=True,
            project=project,
            location=location,
            credentials=credentials,
        )

    if not api_key:
        print(
            "Error: GEMINI_API_KEY environment variable is not set, and Vertex AI credentials (GOOGLE_CLOUD_PROJECT / ADC) are not configured.\n\n"
            f"{AUTH_HELP_MESSAGE}",
            file=sys.stderr,
        )
        sys.exit(1)

    return genai.Client(api_key=api_key)


def main():
    parser = argparse.ArgumentParser(
        description="Generate music, soundtrack themes, and songs using Google Lyria foundation models."
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
        choices=list(MODEL_MAP.keys()),
        default="lyria-3.5",
        help="Model selection ('lyria-3.5' / '3.5', 'lyria-3-clip' / 'clip' / 'lyria-3-clip-preview', or 'pro' / 'lyria-3-pro-preview', default: lyria-3.5)",
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
        default="mp3",
        help="Audio output format (default: mp3)",
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
        "--vertexai",
        action="store_true",
        help="Use Vertex AI / Gemini Enterprise with Application Default Credentials (ADC)",
    )
    parser.add_argument(
        "--project",
        help="GCP Project ID for Vertex AI (defaults to GOOGLE_CLOUD_PROJECT)",
    )
    parser.add_argument(
        "--location",
        default=None,
        help="GCP Location for Vertex AI (defaults to GOOGLE_CLOUD_LOCATION or 'us-central1')",
    )

    args = parser.parse_args()

    if len(args.input_image) > 10:
        print("Error: Maximum of 10 input images allowed for Lyria 3.", file=sys.stderr)
        sys.exit(1)

    model_id = MODEL_MAP[args.model]
    client = init_client(args)

    print(f"Model: {model_id} ({args.model})")
    print(f"Output: {args.filename} (Format: {args.format})")
    if args.input_image:
        print(f"Reference Images ({len(args.input_image)}): {args.input_image}")
    print(f"Prompt: {args.prompt}")

    audio_bytes = None
    lyrics_text = None

    try:
        if args.api == "interactions":
            if args.input_image:
                input_payload = [{"type": "text", "text": args.prompt}]
                for img_path in args.input_image:
                    with open(img_path, "rb") as img_file:
                        b64_data = base64.b64encode(img_file.read()).decode("utf-8")
                    mime_type = (
                        "image/png"
                        if img_path.lower().endswith(".png")
                        else "image/jpeg"
                    )
                    input_payload.append(
                        {
                            "type": "image",
                            "mime_type": mime_type,
                            "data": b64_data,
                        }
                    )
            else:
                input_payload = args.prompt

            response_format = {"type": "audio"} if args.format == "wav" else None
            kwargs = {"model": model_id, "input": input_payload}
            if response_format:
                kwargs["response_format"] = response_format

            interaction = client.interactions.create(**kwargs)

            gen_audio = getattr(interaction, "output_audio", None)
            if gen_audio and hasattr(gen_audio, "data"):
                audio_bytes = base64.b64decode(gen_audio.data)

            lyrics_text = getattr(interaction, "output_text", None)

            if not audio_bytes and hasattr(interaction, "steps"):
                lyrics_parts = []
                for step in getattr(interaction, "steps", []):
                    if getattr(step, "type", None) == "model_output":
                        for block in getattr(step, "content", []):
                            b_type = getattr(block, "type", None)
                            if b_type == "audio" and hasattr(block, "data"):
                                audio_bytes = base64.b64decode(block.data)
                            elif b_type == "text" and hasattr(block, "text"):
                                lyrics_parts.append(block.text)
                if not lyrics_text and lyrics_parts:
                    lyrics_text = "\n".join(lyrics_parts)
        else:
            contents = [args.prompt]
            for img_path in args.input_image:
                contents.append(Image.open(img_path))

            response = client.models.generate_content(
                model=model_id,
                contents=contents,
            )

            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        audio_bytes = part.inline_data.data
                    elif part.text:
                        lyrics_text = part.text

        if not audio_bytes:
            raise ValueError(f"No audio data returned from Lyria 3 model {model_id}.")

        out_dir = os.path.dirname(os.path.abspath(args.filename))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(args.filename, "wb") as f:
            f.write(audio_bytes)
        print(f"Success! Audio saved to {args.filename}")

        if lyrics_text:
            print("\nGenerated Lyrics / Structure:")
            print(lyrics_text)
            if args.lyrics_file:
                with open(args.lyrics_file, "w", encoding="utf-8") as lf:
                    lf.write(lyrics_text)
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
