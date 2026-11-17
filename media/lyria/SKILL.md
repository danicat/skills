---
name: lyria
description: >
  Generate 44.1 kHz stereo music, full songs with lyrics, and instrumental
  tracks from text prompts or reference images using Google Lyria models
  (lyria-3.5, lyria-3-clip-preview, lyria-3-pro-preview) via uv run
  scripts/lyria.py, the gemini-api CLI, or Google Gen AI SDKs across Gemini
  Enterprise / Vertex AI (global) and Gemini API. Activate when composing
  soundtracks, generating songs, or creating audio from images.
license: Apache-2.0
metadata:
  category: media
  tags: "music, audio, soundtrack, generative-ai, vertex-ai, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.6.0"
  catalog: https://skills.danicat.dev
---

# Lyria music generation (`lyria`)

Generate 44.1 kHz stereo music, full songs with structured lyrics, and instrumental audio tracks from text prompts or reference images using Google's **Lyria** models (`lyria-3.5`, `lyria-3-clip-preview`, and `lyria-3-pro-preview`) via `uv run scripts/lyria.py`, the `gemini-api` CLI (`gemini-api music`), or Google Gen AI SDKs across **Gemini Enterprise / Vertex AI** (`global` location) and the **Gemini Developer API**.

> [!CAUTION]
> **Strict fail-fast authentication policy**:
> - If `gemini-api` fails, is not installed, or lacks Vertex AI authentication, run `uv run scripts/lyria.py` with Vertex AI / Application Default Credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION="global"`, `GOOGLE_GENAI_USE_ENTERPRISE="true"`, and `gcloud auth application-default login`) or `GEMINI_API_KEY`.
> - If authentication still fails in `scripts/lyria.py`, stop immediately, report the exact authentication error to the user, and ask them to configure credentials (`gcloud auth application-default login` + `export GOOGLE_CLOUD_PROJECT=...` or `export GEMINI_API_KEY=...`).
> - Never synthesize placeholder audio files, never silently swap models, and never inspect credential stores outside standard environment variables and ADC.

---

## Available scripts

- **[scripts/lyria.py](scripts/lyria.py)**: PEP 723 standalone Python CLI (`uv run scripts/lyria.py`) for text-to-music and image-to-music generation, lyric export, and MP3/WAV output via `google-genai`. Supports **Gemini Enterprise / Vertex AI** (`--enterprise`, `--vertexai`, `--project`, `--location`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, ADC) and **Gemini Developer API** (`GEMINI_API_KEY`).
- **[scripts/test_lyria.py](scripts/test_lyria.py)**: Automated unit and CLI test suite verifying model resolution, MP3/WAV format constraints, MIME detection, nested directory creation, offline `--dry-run` checks, and fail-fast credential errors.

---

## Prerequisites: `uv` (`scripts/lyria.py`) and `gemini-api` setup

You can run Lyria music generation with either the bundled Python script (`uv run scripts/lyria.py`, recommended for Gemini Enterprise / Vertex AI) or the `gemini-api` CLI binary.

### Option A: `uv` (`scripts/lyria.py`) with Gemini Enterprise / Vertex AI or Gemini API key

`scripts/lyria.py` declares inline PEP 723 dependencies (`requires-python = ">=3.12"`, `google-genai>=3.3.0`, `pillow>=10.0.0`, `google-auth>=2.0.0`) so `uv run` resolves an isolated environment automatically without manual `pip install` steps.

```bash
# 1a. Authenticate with Gemini Enterprise / Vertex AI (Application Default Credentials)
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_ENTERPRISE="true"

# 1b. Or authenticate with the Gemini Developer API
export GEMINI_API_KEY="your-api-key"

# 2. Verify CLI flags and run the offline test suite
uv run scripts/lyria.py --help
uv run scripts/test_lyria.py
```

### Option B: `gemini-api` CLI setup

The `gemini-api` CLI writes generated audio files directly to disk and prints only the output path to `stdout`.

```bash
# 1. Verify or install gemini-api CLI on macOS and Linux
command -v gemini-api >/dev/null 2>&1 || (curl -fsSL https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.sh | bash)
# Windows (PowerShell): iwr -useb https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.ps1 | iex

# 2a. Authenticate with a Gemini API Key (environment variable or OS keychain)
export GEMINI_API_KEY="your-api-key"
gemini-api configure --api-key "your-api-key"

# 2b. Or authenticate with a Google Cloud Project / ADC (OAuth2 bearer token)
# For native Gemini Enterprise / Vertex AI ADC without manual token export,
# use 'uv run scripts/lyria.py --enterprise --project your-gcp-project-id' instead.
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language"
export GEMINI_ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
export GEMINI_USER_PROJECT="your-gcp-project-id"

# 3. Verify credentials and inspect CLI schemas offline
gemini-api whoami
gemini-api music --help
gemini-api music --schema
```

---

## Trigger conditions

Activate this skill when the user asks to:
- Generate songs, background music, soundtracks, or short audio clips from text prompts.
- Compose musical themes inspired by concept art, illustrations, photos, or screenshots (up to 10 reference images).
- Create fixed 30-second audio clips or multi-minute structured songs with verses, choruses, timestamps, and custom lyrics.
- Synthesize clean instrumental tracks (`"Instrumental only, no vocals"`).

---

## Model selection and comparison matrix

| Model | Model ID (`-m`) | CLI aliases (`scripts/lyria.py`) | Primary use case | Duration | Audio format | Reference guide |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lyria 3.5 (Default)** | `lyria-3.5` | `lyria-3.5`, `3.5` | Flagship: full songs, expressive vocals, multi-section arrangements, film and ambient scoring | Controllable (up to about 3 minutes) | MP3, WAV | [lyria-3-5.md](references/lyria-3-5.md) |
| **Lyria 3 Clip** | `lyria-3-clip-preview` | `lyria-3-clip`, `clip`, `lyria-clip`, `lyria-3-clip-preview` | Short 30-second clips, social audio, rapid genre and style prototyping | Fixed 30 seconds | MP3 | [lyria-3-clip.md](references/lyria-3-clip.md) |
| **Lyria 3 Pro** | `lyria-3-pro-preview` | `lyria-3-pro`, `pro`, `lyria-pro`, `lyria-3-pro-preview` | Full-length preview endpoint with explicit timestamp controls and multi-section arrangements | Up to 184 seconds (about 3 minutes) | MP3 | [lyria-3-pro.md](references/lyria-3-pro.md) |

### Format rules and fail-fast policy
- **Full song and WAV production**: Use **Lyria 3.5** (`lyria-3.5`, default) for complete tracks, timestamped transitions (`[0:00 - 0:15] Intro...`), multi-verse vocal delivery, or uncompressed WAV export (`-f track.wav` automatically selects WAV on `lyria-3.5`).
- **MP3-only preview models**: `lyria-3-clip-preview` (30 seconds) and `lyria-3-pro-preview` (up to 184 seconds) output MP3 only. `scripts/lyria.py` fails fast when you request WAV output on those models.
- **Zero silent fallbacks**: `scripts/lyria.py` and `gemini-api music` never fall back across models or authentication providers. Missing credentials, retired models (`lyria-002`), extension/format mismatches, unsupported image extensions, more than 10 reference images, or empty audio responses stop with descriptive `stderr` diagnostics and exit code 1.

---

## Deep technical references

Consult the reference cards in `references/` for model limits, timing controls, and SDK patterns:

- **[references/lyria-3-5.md](references/lyria-3-5.md)**: Flagship specifications for multi-minute songs, WAV/MP3 output, vocals, and section timestamps (`lyria-3.5`).
- **[references/lyria-3-clip.md](references/lyria-3-clip.md)**: Specifications for 30-second MP3 clips and fast style iteration (`lyria-3-clip-preview`).
- **[references/lyria-3-pro.md](references/lyria-3-pro.md)**: Specifications for the full-length preview endpoint (`lyria-3-pro-preview`).
- **[references/README.md](references/README.md)**: Musical composition prompt reference and index.

---

## Core execution workflows

### 1. Python script via `uv run scripts/lyria.py`

Use `scripts/lyria.py` across **Gemini Enterprise / Vertex AI** (`global` location) and the **Gemini Developer API**:

```bash
# Generate a full song with Lyria 3.5 (default model)
uv run scripts/lyria.py \
  -p "An energetic pop-rock song with driving drums and upbeat vocals" \
  -f "song.mp3" \
  -m "lyria-3.5" \
  --lyrics-file "lyrics.txt"

# Export uncompressed 44.1 kHz WAV via Gemini Enterprise / Vertex AI (auto-inferred from .wav)
uv run scripts/lyria.py \
  --enterprise \
  --project "${GOOGLE_CLOUD_PROJECT}" \
  --location "${GOOGLE_CLOUD_LOCATION:-global}" \
  -p "Atmospheric synthwave exploration theme at 110 BPM in D minor with warm analog pads. Instrumental only, no vocals." \
  -f "./assets/stage_theme.wav"

# Generate a 30-second chiptune loop with Lyria 3 Clip
uv run scripts/lyria.py \
  -p "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals." \
  -f "chiptune.mp3" \
  -m "lyria-3-clip"

# Multimodal image-to-music (compose audio inspired by concept art)
uv run scripts/lyria.py \
  -p "Ambient relaxing soundscape matching the mood of this landscape. Instrumental only, no vocals." \
  -i "concept_landscape.png" \
  -f "landscape_theme.mp3" \
  -m "lyria-3-pro"

# Offline validation without network calls
uv run scripts/lyria.py \
  -p "Acoustic guitar instrumental in E minor at 90 BPM" \
  -f "out.wav" \
  --dry-run
```

#### `scripts/lyria.py` CLI argument reference
- `-p`, `--prompt`: Text prompt describing style, genre, instruments, BPM, and structure (required).
- `-f`, `--filename`, `--out`, `-o`: Output path (default: `music.mp3`). Ending in `.wav` automatically selects WAV when you omit `--format`.
- `-m`, `--model`: `lyria-3.5` (`3.5`, default), `lyria-3-clip-preview` (`lyria-3-clip`, `clip`, `lyria-clip`), or `lyria-3-pro-preview` (`lyria-3-pro`, `pro`, `lyria-pro`).
- `-i`, `--input-image`: Path to reference images for mood inspiration (`.png`, `.jpg`, `.jpeg`, `.webp`, `.heic`, `.heif`, up to 10).
- `--format`: Explicit audio container format (`mp3` or `wav`). Must match the output filename extension; `wav` requires `lyria-3.5` and `--api interactions`.
- `--lyrics-file`: Optional path to save generated lyrics and structure text.
- `--api`: `interactions` (default) or `models` (`generate_content`).
- `--dry-run`: Validate model choice, image extensions, and audio format offline before initializing credentials.
- `--enterprise`, `--vertexai`: Enable Gemini Enterprise / Vertex AI authentication via Application Default Credentials. Enabled automatically when `GOOGLE_GENAI_USE_ENTERPRISE=true`, `GOOGLE_GENAI_USE_VERTEXAI=true`, `--project` is passed, or `GOOGLE_CLOUD_PROJECT` is set without `GEMINI_API_KEY`.
- `--project`: Google Cloud Project ID (defaults to `GOOGLE_CLOUD_PROJECT` or `GCP_PROJECT`).
- `--location`: Google Cloud Location (defaults to `GOOGLE_CLOUD_LOCATION` or `global`).

---

### 2. CLI execution via `gemini-api music`

You can also use `gemini-api music` when `gemini-api` is installed:

```bash
# Generate a full song with Lyria 3.5 (default model)
gemini-api music \
  "An energetic pop-rock song with driving drums and upbeat vocals" \
  --out "song.mp3"

# Generate a structured song by reading lyrics or timestamp cues from a file (-f)
gemini-api music \
  "Compose an uplifting indie rock anthem at 128 BPM in G Major" \
  -f "lyrics.txt" \
  --out "anthem.mp3"

# Generate a 30-second MP3 clip with Lyria 3 Clip
gemini-api music \
  "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals." \
  --model "lyria-3-clip-preview" \
  --out "chiptune.mp3"

# Export uncompressed 44.1 kHz WAV audio via --body response_format (lyria-3.5 only)
gemini-api music \
  "Atmospheric synthwave exploration theme at 110 BPM in D minor with warm analog pads. Instrumental only, no vocals." \
  --body '{"response_format":{"type":"audio","mime_type":"audio/wav"}}' \
  --out "./assets/stage_theme.wav"

# Upload a reference image via Files API and compose matching music
FILE_ID=$(gemini-api files upload "concept_landscape.png")
gemini-api music \
  --model "lyria-3.5" \
  --out "landscape_theme.mp3" \
  --body "{\"input\":[{\"type\":\"image\",\"uri\":\"$FILE_ID\",\"mime_type\":\"image/png\"},{\"type\":\"text\",\"text\":\"Ambient relaxing soundscape matching the mood of this landscape. Instrumental only, no vocals.\"}]}"

# Offline request validation
gemini-api music "Upbeat synthwave with a driving bassline" --out "synthwave.mp3" --dry-run -o json
```

#### `gemini-api music` flag reference
- `<prompt>`: Positional text prompt describing style, genre, instruments, BPM, and structure.
- `-f`, `--file`: Read prompt text (such as lyrics or multi-section cues) from a file.
- `--stdin`: Read prompt text from stdin instead of a JSON body.
- `-m`, `--model`: `lyria-3.5` (default), `lyria-3-clip-preview`, or `lyria-3-pro-preview`.
- `--out`: Output path or directory (default: `./gemini-music-{timestamp}-{rand}.{ext}`).
- `--body`: Request body JSON merged with CLI flags (`@path` reads a file, `@-` reads stdin). Specify `{"response_format":{"type":"audio","mime_type":"audio/wav"}}` for WAV on `lyria-3.5` or multimodal `input` arrays with `files/<id>` URIs (up to 10 images).
- `--raw-response`: Print the raw API JSON response (including generated lyric text and `outputs` metadata) instead of saving audio.
- `--schema` / `--usage` / `--dry-run`: Inspect the JSON Schema, KDL command specification, or HTTP request offline.

---

### 3. SDK integration patterns (application backends)

Use the Google Gen AI SDK (`google-genai>=3.3.0`) with either `GEMINI_API_KEY` or `enterprise=True` (`location="global"`):

#### Interactions API (`client.interactions.create`, recommended)

```python
import base64
import os
from google import genai

# Supports GEMINI_API_KEY or Gemini Enterprise / Vertex AI (global location)
if os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() in ("true", "1"):
    client = genai.Client(
        enterprise=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
else:
    client = genai.Client()

prompt = """
An atmospheric lo-fi beat in D Minor at 80 BPM:
[0:00 - 0:15] Intro: Dusty vinyl crackle and mellow electric piano chords.
[0:15 - 0:45] Verse: Warm boom-bap drum groove enters with subtle bassline.
[0:45 - 1:15] Chorus: Full melodic progression with saxophone accents.
[1:15 - 1:30] Outro: Slow fade out with piano alone.
Instrumental only, no vocals.
"""

interaction = client.interactions.create(
    model="lyria-3.5",
    input=prompt,
)

if interaction.output_audio:
    with open("lofi_track.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))

if interaction.output_text:
    print("Generated Lyrics / Structure:\n", interaction.output_text)
```

#### Multimodal image-to-audio in Python

```python
import base64
from google import genai

client = genai.Client()

with open("art_concept.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

interaction = client.interactions.create(
    model="lyria-3.5",
    input=[
        {"type": "image", "data": img_b64, "mime_type": "image/png"},
        {"type": "text", "text": "Compose an ethereal cyberpunk synth soundtrack matching this neon cityscape. Instrumental only, no vocals."},
    ],
)

if interaction.output_audio:
    with open("cyberpunk_theme.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))
```

---

## Prompting best practices

1. **Genre and subgenre**: Name the style explicitly (`synthwave`, `delta blues`, `chamber orchestra`, `lo-fi hip-hop`, `symphonic metal`).
2. **Instrumentation and mix space**: Specify lead and rhythm instruments (`Fender Rhodes`, `TR-808 drums`, `nylon-string guitar`, `cello section`). For background beds, specify warm or sparse textures so dialogue or sound effects stay clear.
3. **Tempo and key**: Include BPM and musical key (`120 BPM`, `in A Minor`) to keep cues consistent across a project.
4. **Vocal control**: Add `"Instrumental only, no vocals"` when you want a clean backing track, or provide bracketed section lyrics (`[Verse]`, `[Chorus]`) for songs with singing.
5. **Timestamp arrangements**: For `lyria-3.5` and `lyria-3-pro-preview`, use bracketed timestamps (`[0:00 - 0:15] Intro`, `[0:15 - 1:30] Main theme`) to structure section transitions.
