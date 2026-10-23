---
name: lyria
description: >
  Generative music and audio synthesis from text prompts or reference images
  using Google Lyria models via the gemini-api CLI and Google Gen AI SDKs.
  Generates 44.1 kHz stereo music clips, full songs with custom lyrics, and
  instrumental soundtracks using lyria-3.5 and lyria-3-clip-preview, with
  support for multimodal image inputs and MP3/WAV export. Activate when
  composing background music, generating songs, creating soundtracks from
  images, or producing AI audio clips.
license: Apache-2.0
metadata:
  category: media
  tags: "music, audio, generative-ai, sound, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# Lyria Music Generation Skill

Generate high-fidelity **44.1 kHz stereo audio**, full songs with structured lyrics, instrumental soundtracks, and thematic compositions from text prompts or visual reference images using Google's **Lyria** foundation models (`lyria-3.5`, `lyria-3-clip-preview`, and `lyria-3-pro-preview`) via the official **`gemini-api` CLI** (`gemini-api music`) for terminal and coding agent workflows, or the **Google Gen AI SDKs** for application backends.

---

## Prerequisites: `gemini-api` CLI Setup

The `gemini-api` CLI is a zero-dependency binary that writes generated audio files directly to disk and prints only the output file path to `stdout`, avoiding raw base64 audio payloads in agent context windows.

```bash
# 1. Verify or install gemini-api CLI on macOS and Linux
command -v gemini-api >/dev/null 2>&1 || (curl -fsSL https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.sh | bash)
# Windows (PowerShell): iwr -useb https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.ps1 | iex

# 2a. Authenticate with a Gemini API Key (environment variable or OS keychain)
export GEMINI_API_KEY="your-api-key"
# Or store credentials in the OS keychain:
gemini-api configure --api-key "your-api-key"

# 2b. Or authenticate with a Google Cloud Project / ADC (OAuth2 bearer token)
# Note: gemini-api does NOT auto-discover application_default_credentials.json, and
# generativelanguage.googleapis.com requires the 'generative-language' OAuth scope
# (standard 'gcloud auth application-default login' fails with HTTP 403 ACCESS_TOKEN_SCOPE_INSUFFICIENT).
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language"
export GEMINI_ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
export GEMINI_USER_PROJECT="your-gcp-project-id"
# (Or pass per-command: --access-token "$(gcloud auth application-default print-access-token)" --user-project "your-gcp-project-id")

# 3. Verify credentials and inspect CLI schemas offline
gemini-api whoami
gemini-api models
gemini-api music --help
gemini-api music --schema
```

---

## Trigger Conditions
Activate this skill whenever the user asks to:
- Generate music, songs, soundtracks, game audio beds, or background music.
- Compose musical themes inspired by artwork, concept photos, or screenshots.
- Create 30-second audio loops or multi-minute structured songs with verses, choruses, and custom lyrics.
- Synthesize instrumental audio tracks (`"Instrumental only, no vocals"`).

---

## Model Selection & Comparison Matrix

| Model | Model ID (`-m`) | Primary Use Case | Duration | Audio Format | Reference Guide |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lyria 3.5 (Default)** | `lyria-3.5` | Flagship: full songs, expressive vocals, multi-section arrangements, film/game scoring | Controllable (up to ~3m / 184s) | MP3, WAV | [lyria-3-5.md](references/lyria-3-5.md) |
| **Lyria 3 Clip** | `lyria-3-clip-preview` | Short clips, seamless 30s loops, previews, rapid style testing | Exactly 30s | MP3, WAV | [lyria-3-clip.md](references/lyria-3-clip.md) |
| **Lyria 3 Pro** | `lyria-3-pro-preview` | Full-length preview endpoint with explicit timestamp controls and multi-section arrangements | Up to 184s (~3m) | MP3, WAV | [lyria-3-pro.md](references/lyria-3-pro.md) |

### Model Selection & Deterministic Execution Policy
- **Full Song Production**: Use **Lyria 3.5** (`lyria-3.5`, default for `gemini-api music`) for complete tracks with timestamped transitions (`[0:00 - 0:15] Intro...`), multi-verse vocal delivery, or cinematic thematic development.
- **Rapid Prototyping & Loops**: Start with **Lyria 3 Clip** (`-m lyria-3-clip-preview`) to iterate quickly on genre combinations, tempos, and 30-second loops.
- **Deterministic Fail-Fast Execution**: `gemini-api music` validates inputs against the Interactions API schema and exits with deterministic status codes (`0` ok, `1` runtime error, `2` usage/validation error, `3` authentication/authorization error). Use `--dry-run -o json` to preview and verify request payloads offline without network calls.

---

## Deep Technical References

Consult dedicated reference cards in `references/` for detailed audio parameters, timing controls, and API schemas:

- **[references/lyria-3-5.md](references/lyria-3-5.md)**: Flagship specifications for full-length songs, rich vocal synthesis, and arrangements (`lyria-3.5`).
- **[references/lyria-3-clip.md](references/lyria-3-clip.md)**: Specifications for 30-second clips, loops, and rapid prototyping (`lyria-3-clip-preview`).
- **[references/lyria-3-pro.md](references/lyria-3-pro.md)**: Specifications for full-length preview endpoint (`lyria-3-pro-preview`), timestamp controls, and scoring.
- **[references/README.md](references/README.md)**: Musical composition prompt reference and index.

---

## Core Execution Workflows

### 1. CLI Execution via `gemini-api music`

Use `gemini-api music` for terminal workflows, shell scripts, and coding agents. By default, it runs `lyria-3.5`, writes the audio straight to disk, and prints only the saved file path to `stdout`:

```bash
# Generate a full song with Lyria 3.5 (default model)
gemini-api music \
  "An energetic pop-rock song with driving drums and upbeat vocals" \
  --out "song.mp3"

# Generate a structured song by reading lyrics or timestamped arrangements from a file (-f)
gemini-api music \
  "Compose an uplifting indie rock anthem at 128 BPM in G Major" \
  -f "lyrics.txt" \
  --out "anthem.mp3"

# Generate a 30-second chiptune arcade loop with Lyria 3 Clip
gemini-api music \
  "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals." \
  --model "lyria-3-clip-preview" \
  --out "chiptune.mp3"

# Export uncompressed WAV audio via --body response_format
gemini-api music \
  "Lo-fi ambient background track for a focus app. Instrumental only, no vocals." \
  --body '{"response_format":{"type":"audio","mime_type":"audio/wav"}}' \
  --out "./assets/focus_track.wav"

# Multimodal Image-to-Music: upload reference image via Files API (no base64 context bloat) and pass to gemini-api music
FILE_ID=$(gemini-api files upload "landscape.jpg")
gemini-api music \
  --model "lyria-3.5" \
  --out "landscape_theme.mp3" \
  --body "{\"input\":[{\"type\":\"image\",\"uri\":\"$FILE_ID\",\"mime_type\":\"image/jpeg\"},{\"type\":\"text\",\"text\":\"Ambient relaxing soundscape matching the mood of this landscape. Instrumental only, no vocals.\"}]}"

# Offline Request Validation (no network calls)
gemini-api music "Upbeat synthwave with a driving bassline" --out "synthwave.mp3" --dry-run -o json
```

#### `gemini-api music` Flag Reference
- `<prompt>`: Positional text prompt describing style, genre, instruments, BPM, and structure.
- `-f`, `--file`: Read prompt text (such as lyrics or multi-section timestamp cues) from a file, sent before the positional prompt if both are provided.
- `--stdin`: Read prompt text from stdin to EOF instead of a JSON body.
- `-m`, `--model`: `lyria-3.5` (default), `lyria-3-clip-preview`, or `lyria-3-pro-preview`.
- `--out`: Output audio file path or target directory (default: `./gemini-music-{timestamp}-{rand}.{ext}`).
- `--body`: Request body as JSON merged with CLI flags (`@path` reads a file, `@-` reads stdin). Use to specify `{"response_format":{"type":"audio","mime_type":"audio/wav"}}` or multimodal `input` arrays with uploaded `files/<id>` URIs (up to 10 reference images).
- `--raw-response`: Print the raw API response JSON (including generated lyric transcriptions and `outputs` metadata) instead of writing the audio to a file.
- `--schema` / `--usage` / `--dry-run`: Inspect the exact JSON Schema, KDL command specification, or preview the HTTP request offline without making network calls.
- **Exit Codes**: `0` ok · `1` runtime error · `2` usage/validation error · `3` authentication/authorization error.

---

### 2. SDK Integration Patterns (Application Backends)

For embedding Lyria music generation into production services, use the typed Google Gen AI SDKs:

#### Interactions API (`client.interactions.create`) — Recommended

```python
import base64
from google import genai

client = genai.Client()

# Generate full-length song with timestamp structure
prompt = """
An atmospheric lo-fi beat in D Minor at 80 BPM:
[0:00 - 0:15] Intro: Dusty vinyl crackle and mellow electric piano chords.
[0:15 - 0:45] Verse: Warm boom-bap drum groove enters with subtle bassline.
[0:45 - 1:15] Chorus: Full melodic progression with saxophone accents.
[1:15 - 1:30] Outro: Slow fade out with piano alone.
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

#### Multimodal Image-to-Audio (Python)

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
        {"type": "text", "text": "Compose an ethereal cyberpunk synth soundtrack matching this neon cityscape. Instrumental only."},
    ],
)

if interaction.output_audio:
    with open("cyberpunk_theme.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))
```

---

## Prompting Best Practices
1. **Genre & Subgenre**: Be specific (e.g. `synthwave`, `delta blues`, `chamber pop`, `lo-fi hip-hop`).
2. **Instrumentation**: Name specific instruments (`Fender Rhodes`, `TR-808 drums`, `nylon-string guitar`, `cello`).
3. **Tempo & Key**: Include BPM and musical key (`120 BPM`, `in A Minor`).
4. **Vocal Control**: For instrumental tracks, explicitly specify `"Instrumental only, no vocals"`. For vocals, provide bracketed lyrics (`[Verse]`, `[Chorus]`).
5. **Timestamp Arrangements**: For `lyria-3.5` and `lyria-3-pro-preview`, use bracketed timestamps (`[0:00 - 0:20]`) to direct transitions and builds.
