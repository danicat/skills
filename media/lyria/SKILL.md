---
name: lyria
description: >
  Generative music and audio synthesis from text prompts or reference images
  using Google Lyria models via uv run scripts/lyria.py, the gemini-api CLI, and
  Google Gen AI SDKs. Generates 44.1 kHz stereo music clips, full songs with
  custom lyrics, and instrumental game soundtracks using lyria-3.5 and
  lyria-3-clip-preview, with first-class support for Vertex AI / Gemini
  Enterprise (ADC) and Gemini API Key authentication, multimodal image inputs,
  MP3/WAV export, and Ebitengine audio integration. Activate when composing
  background music, generating songs, creating game soundtracks from concept
  art, or producing AI audio clips.
license: Apache-2.0
metadata:
  category: media
  tags: "music, audio, game-dev, bgm, soundtrack, generative-ai, sound, gemini-api, vertex-ai"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.5.0"
  catalog: https://skills.danicat.dev
---

# Lyria Music Generation Skill (`lyria`)

Generate **44.1 kHz stereo audio**, full songs with structured lyrics, instrumental game soundtracks, and thematic compositions from text prompts or visual reference images using Google's **Lyria** models (`lyria-3.5`, `lyria-3-clip-preview`, and `lyria-3-pro-preview`) via **`uv run scripts/lyria.py`** (supporting both **Vertex AI / Gemini Enterprise** and **Gemini Developer API**), the **`gemini-api` CLI** (`gemini-api music`), or the **Google Gen AI SDKs** for application backends.

> [!CAUTION]
> **Strict Fail-Fast Authentication Policy (Never Go Rogue)**:
> **Never go rogue if `gemini-api` or `scripts/lyria.py` fails.**
> - If `gemini-api` fails, is not installed, or lacks Vertex AI authentication, run `uv run scripts/lyria.py` (or `uv run skills/lyria/scripts/lyria.py`) with Vertex AI / Application Default Credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `gcloud auth application-default login`) or `GEMINI_API_KEY`.
> - If authentication still fails in `scripts/lyria.py`, **stop immediately**, report the exact authentication error message to the user, and ask them to configure their credentials (`gcloud auth application-default login` + `export GOOGLE_CLOUD_PROJECT=...` or `export GEMINI_API_KEY=...`).
> - Never attempt unauthorized workarounds, never synthesize fake or mock audio files, never silently substitute procedural audio when the user asked for Lyria, and never probe local credential stores outside standard environment variables and ADC.

---

## Available Scripts

- **[scripts/lyria.py](scripts/lyria.py)**: PEP 723 standalone Python CLI tool (`uv run scripts/lyria.py`) for text-to-music and image-to-music generation, lyric export, and MP3/WAV audio format output using `google-genai`. Supports both **Vertex AI / Gemini Enterprise** (`--vertexai`, `--project`, `--location`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, ADC) and **Gemini Developer API** (`GEMINI_API_KEY`).
- **[scripts/test_lyria.py](scripts/test_lyria.py)**: Automated test suite verifying CLI argument parsing, model aliases, multimodal input limit enforcement, and fail-fast credential checks.

---

## Prerequisites: `uv` + `python3` (`scripts/lyria.py`) & `gemini-api` CLI Setup

You can execute Lyria music generation using either the bundled Python script (`uv run scripts/lyria.py`, recommended whenever using **Vertex AI / Gemini Enterprise** or `uv`) or the `gemini-api` CLI binary.

### Option A: `uv` + `python3` (`scripts/lyria.py`) with Vertex AI or Gemini API Key

`scripts/lyria.py` includes inline PEP 723 dependencies (`google-genai>=1.68.0`, `pillow>=10.0.0`, `google-auth>=2.0.0`) so `uv run` resolves an isolated environment automatically without manual `pip install` steps.

```bash
# 1a. Authenticate with Vertex AI / Gemini Enterprise (Application Default Credentials)
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"

# 1b. Or authenticate with the Gemini Developer API
export GEMINI_API_KEY="your-api-key"

# 2. Verify CLI flags and fail-fast test suite
uv run scripts/lyria.py --help
python3 scripts/test_lyria.py
```

### Option B: `gemini-api` CLI Setup

The `gemini-api` CLI is a zero-dependency binary that writes generated audio files directly to disk and prints only the output file path to `stdout`.

```bash
# 1. Verify or install gemini-api CLI on macOS and Linux
command -v gemini-api >/dev/null 2>&1 || (curl -fsSL https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.sh | bash)
# Windows (PowerShell): iwr -useb https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.ps1 | iex

# 2a. Authenticate with a Gemini API Key (environment variable or OS keychain)
export GEMINI_API_KEY="your-api-key"
# Or store credentials in the OS keychain:
gemini-api configure --api-key "your-api-key"

# 2b. Or authenticate with a Google Cloud Project / ADC (OAuth2 bearer token)
# Note: For direct Vertex AI / Gemini Enterprise ADC support without manual token export,
# use 'uv run scripts/lyria.py --vertexai --project your-gcp-project-id' instead.
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

## Trigger Conditions

Activate this skill whenever the user asks to:
- Generate music, songs, soundtracks, game audio beds, or background music (BGM).
- Compose musical themes inspired by artwork, `nano-banana` concept art, character sheets, or screenshots.
- Create 30-second audio loops or multi-minute structured songs with verses, choruses, and custom lyrics.
- Synthesize instrumental audio tracks (`"Instrumental only, no vocals"`).

---

## Role in `agy-game-studio`: Game Soundtracks & Hybrid Audio Pipeline

In `agy-game-studio`, `lyria` is the generative studio music engine that complements the procedural audio and engine skills orchestrated by `vibe-game-developer`:

- **`lyria` vs. `procedural-music` (AI Studio Audio vs. Deterministic `.music` DSL)**:
  - Choose **`lyria`** when you want studio-recorded acoustic, orchestral, ambient, lo-fi, synthwave, or vocal tracks (`.wav` or `.mp3`), or when you want to score a level directly from visual concept art (multimodal image-to-music).
  - Choose **`procedural-music`** when you want deterministic note-by-note `.music` scores (8 to 12+ channels, verified `|` barlines, `~` cross-bar ties), sample-exact seamless looping with tiny plain-text files (`5 KB` to `20 KB`), pure-Go SEGA Mega Drive YM2612 + SN76489 chiptune synthesis, macOS CoreAudio (`-apple` / `gs_instruments.dls`) General MIDI rendering, or per-track stem soloing and muting in the Sound tab in Game Dev Studio (`[Sound Editor](sidecar://agy-game-studio/studio/sound)`).
- **`lyria` + `procedural-sfx` (Hybrid Game Audio)**:
  - Pair `lyria` BGM tracks with `procedural-sfx` (`.sfx` DSL) for low-latency, zero-asset gameplay sound effects (jumps, lasers, sword hits, pickups, UI clicks). Both share a single Ebitengine `audio.Context` at `44,100 Hz`.
- **`nano-banana` to `lyria` (Visual-to-Audio Co-Creation)**:
  - Feed title screens, biome parallax backgrounds, or character reference sheets generated by `nano-banana` into `scripts/lyria.py` (`-i biome_concept.png`) or `gemini-api music` so the soundtrack matches the visual mood and setting defined in `game-design` (`GDD.md`).

### Ebitengine (`ebitengineer`) WAV & MP3 Integration with 4-Byte Alignment (`&^ 3`)

When loading `lyria` `.wav` or `.mp3` files into an Ebitengine (`github.com/hajimehoshi/ebiten/v2`) game, decode the audio stream once at startup or scene load (never inside `Update()` or `Draw()`) and mask the PCM buffer length and loop offsets with `&^ 3` (4-byte stereo sample frame alignment: 2 bytes Left + 2 bytes Right). Ebitengine's `audio.NewInfiniteLoop`, `audio.NewInfiniteLoopWithIntro`, and `Seek` panic at runtime if given an unaligned byte count.

```go
package audio

import (
	"bytes"
	_ "embed"
	"fmt"
	"io"

	"github.com/hajimehoshi/ebiten/v2/audio"
	"github.com/hajimehoshi/ebiten/v2/audio/mp3"
	"github.com/hajimehoshi/ebiten/v2/audio/wav"
)

const SampleRate = 44100

//go:embed assets/stage_theme.wav
var stageThemeWAV []byte

// DecodeWAVLoop decodes an embedded 44.1 kHz WAV file into a 4-byte aligned InfiniteLoop player.
func DecodeWAVLoop(ctx *audio.Context, wavBytes []byte) (*audio.Player, error) {
	stream, err := wav.DecodeWithSampleRate(SampleRate, bytes.NewReader(wavBytes))
	if err != nil {
		return nil, fmt.Errorf("decode wav: %w", err)
	}
	pcm, err := io.ReadAll(stream)
	if err != nil {
		return nil, fmt.Errorf("read wav pcm: %w", err)
	}
	alignedLen := int64(len(pcm) &^ 3)
	loop := audio.NewInfiniteLoop(bytes.NewReader(pcm[:alignedLen]), alignedLen)
	return ctx.NewPlayer(loop)
}

// DecodeMP3WithIntro decodes an MP3 with an intro section (introSec) followed by a seamless loop.
func DecodeMP3WithIntro(ctx *audio.Context, mp3Bytes []byte, introSec float64) (*audio.Player, error) {
	stream, err := mp3.DecodeWithSampleRate(SampleRate, bytes.NewReader(mp3Bytes))
	if err != nil {
		return nil, fmt.Errorf("decode mp3: %w", err)
	}
	pcm, err := io.ReadAll(stream)
	if err != nil {
		return nil, fmt.Errorf("read mp3 pcm: %w", err)
	}
	alignedTotal := int64(len(pcm) &^ 3)
	introBytes := int64(introSec*float64(SampleRate)*4) &^ 3
	if introBytes >= alignedTotal {
		introBytes = 0
	}
	loopLength := (alignedTotal - introBytes) &^ 3
	loop := audio.NewInfiniteLoopWithIntro(bytes.NewReader(pcm[:alignedTotal]), introBytes, loopLength)
	return ctx.NewPlayer(loop)
}
```

---

## Model Selection & Comparison Matrix

| Model | Model ID (`-m`) | CLI Aliases (`scripts/lyria.py`) | Primary Use Case | Duration | Audio Format | Reference Guide |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lyria 3.5 (Default)** | `lyria-3.5` | `lyria-3.5`, `3.5` | Flagship: full songs, expressive vocals, multi-section arrangements, film and game scoring | Controllable (up to ~3m / 184s) | MP3, WAV | [lyria-3-5.md](references/lyria-3-5.md) |
| **Lyria 3 Clip** | `lyria-3-clip-preview` | `lyria-3-clip`, `clip`, `lyria-clip`, `lyria-3-clip-preview` | Short clips, 30s stage loops, menu beds, rapid style testing | Exactly 30s | MP3, WAV | [lyria-3-clip.md](references/lyria-3-clip.md) |
| **Lyria 3 Pro** | `lyria-3-pro-preview` | `pro`, `lyria-pro`, `lyria-3-pro-preview` | Full-length preview endpoint with explicit timestamp controls and multi-section arrangements | Up to 184s (~3m) | MP3, WAV | [lyria-3-pro.md](references/lyria-3-pro.md) |

### Model Selection & Deterministic Fail-Fast Policy
- **Full Song & Multi-Phase BGM Production**: Use **Lyria 3.5** (`lyria-3.5`, default) for complete tracks with timestamped transitions (`[0:00 - 0:15] Intro...`), multi-verse vocal delivery, or boss-phase thematic escalation.
- **Rapid Prototyping & 30s Loops**: Start with **Lyria 3 Clip** (`-m lyria-3-clip` or `-m lyria-3-clip-preview`) to iterate quickly on genre combinations, tempos, and 30-second stage or menu loops.
- **Zero Silent Fallbacks**: `scripts/lyria.py` and `gemini-api music` never silently fall back between models, API endpoints, or authentication providers. Missing `GEMINI_API_KEY` or Vertex AI credentials (`GOOGLE_CLOUD_PROJECT` / ADC), invalid model names, more than 10 reference images, or empty audio responses fail immediately with descriptive `stderr` diagnostics and a non-zero exit code.

---

## Deep Technical References

Consult the reference cards in `references/` for audio parameters, timing controls, and API schemas:

- **[references/lyria-3-5.md](references/lyria-3-5.md)**: Flagship specifications for full-length songs, vocal synthesis, and multi-section arrangements (`lyria-3.5`).
- **[references/lyria-3-clip.md](references/lyria-3-clip.md)**: Specifications for 30-second clips, loops, and rapid prototyping (`lyria-3-clip-preview`).
- **[references/lyria-3-pro.md](references/lyria-3-pro.md)**: Specifications for the full-length preview endpoint (`lyria-3-pro-preview`), timestamp controls, and scoring.
- **[references/README.md](references/README.md)**: Musical composition prompt reference and index.

---

## Core Execution Workflows

### 1. Python Script Execution via `uv run scripts/lyria.py` (Vertex AI & Gemini API)

Execute `scripts/lyria.py` with `uv run` for full support across both **Vertex AI / Gemini Enterprise (ADC)** and **Gemini Developer API**:

```bash
# Generate a full song with Lyria 3.5 (default model)
uv run scripts/lyria.py \
  -p "An energetic pop-rock song with driving drums and upbeat vocals" \
  -f "song.mp3" \
  -m "lyria-3.5" \
  --lyrics-file "lyrics.txt"

# Generate using Vertex AI / Gemini Enterprise (Application Default Credentials)
uv run scripts/lyria.py \
  --vertexai \
  --project "${GOOGLE_CLOUD_PROJECT}" \
  --location "${GOOGLE_CLOUD_LOCATION:-us-central1}" \
  -p "Atmospheric synthwave exploration theme at 110 BPM in D minor with warm analog pads. Instrumental only, no vocals." \
  -f "./assets/stage_theme.wav" \
  --format "wav"

# Generate a 30-second chiptune arcade loop with Lyria 3 Clip
uv run scripts/lyria.py \
  -p "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals." \
  -f "chiptune.mp3" \
  -m "lyria-3-clip"

# Multimodal Image-to-Music (compose music inspired by a nano-banana concept image)
uv run scripts/lyria.py \
  -p "Ambient relaxing soundscape matching the mood of this landscape. Instrumental only, no vocals." \
  -i "biome_concept.png" \
  -f "biome_theme.mp3" \
  -m "lyria-3.5"
```

#### `scripts/lyria.py` CLI Argument Reference
- `-p`, `--prompt`: Text prompt describing style, genre, instruments, BPM, and structure (required).
- `-f`, `--filename`, `--out`, `-o`: Output audio file path (default: `music.mp3`).
- `-m`, `--model`: `lyria-3.5` / `3.5` (default), `lyria-3-clip` / `clip` / `lyria-3-clip-preview`, or `pro` / `lyria-3-pro-preview`.
- `-i`, `--input-image`: Path to input image(s) for visual mood inspiration (up to 10).
- `--format`: Audio container format (`mp3` or `wav`, default: `mp3`).
- `--lyrics-file`: Optional path to write generated lyric transcription and structure text.
- `--api`: `interactions` (default) or `models`.
- `--vertexai`: Enable Vertex AI / Gemini Enterprise authentication using Application Default Credentials (`gcloud auth application-default login`). Also enabled automatically when `GOOGLE_GENAI_USE_VERTEXAI=true` or when `GOOGLE_CLOUD_PROJECT` is set without `GEMINI_API_KEY`.
- `--project`: Google Cloud Project ID for Vertex AI (defaults to `GOOGLE_CLOUD_PROJECT` or `GCP_PROJECT`).
- `--location`: Google Cloud Location for Vertex AI (defaults to `GOOGLE_CLOUD_LOCATION` or `us-central1`).

---

### 2. CLI Execution via `gemini-api music`

You can also use `gemini-api music` for terminal workflows when `gemini-api` is installed and configured:

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

# Export uncompressed 44.1 kHz WAV audio for Ebitengine via --body response_format
gemini-api music \
  "Atmospheric synthwave exploration theme at 110 BPM in D minor with warm analog pads and arpeggiated bass. Instrumental only, no vocals." \
  --body '{"response_format":{"type":"audio","mime_type":"audio/wav"}}' \
  --out "./assets/stage_theme.wav"

# Multimodal Image-to-Music: upload a nano-banana concept or biome image via Files API (no base64 bloat) and pass to gemini-api music
FILE_ID=$(gemini-api files upload "biome_concept.png")
gemini-api music \
  --model "lyria-3.5" \
  --out "biome_theme.mp3" \
  --body "{\"input\":[{\"type\":\"image\",\"uri\":\"$FILE_ID\",\"mime_type\":\"image/png\"},{\"type\":\"text\",\"text\":\"Ambient relaxing soundscape matching the mood of this landscape. Instrumental only, no vocals.\"}]}"

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

### 3. SDK Integration Patterns (Application Backends)

For embedding Lyria music generation into backend services, use the typed Google Gen AI SDKs with either `GEMINI_API_KEY` or Vertex AI (`vertexai=True`):

#### Interactions API (`client.interactions.create`, Recommended)

```python
import base64
import os
from google import genai

# Supports GEMINI_API_KEY or Vertex AI (GOOGLE_GENAI_USE_VERTEXAI=true, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION)
if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1"):
    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
else:
    client = genai.Client()

# Generate full-length song with timestamp structure
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
        {"type": "text", "text": "Compose an ethereal cyberpunk synth soundtrack matching this neon cityscape. Instrumental only, no vocals."},
    ],
)

if interaction.output_audio:
    with open("cyberpunk_theme.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))
```

---

## Prompting Best Practices for Songs & Game Soundtracks

1. **Genre & Subgenre**: Be specific (`synthwave`, `delta blues`, `chamber orchestra`, `lo-fi hip-hop`, `symphonic metal`).
2. **Instrumentation & Mix Space**: Name specific lead and rhythm instruments (`Fender Rhodes`, `TR-808 drums`, `nylon-string guitar`, `cello section`). For gameplay BGM, leave mid-to-high frequency headroom so transient `.sfx` cues remain clear.
3. **Tempo & Key**: Include BPM and musical key (`120 BPM`, `in A Minor`) so menu themes, exploration stages, and boss tracks contrast cleanly across scenes.
4. **Vocal Control**: For gameplay loops and background beds, explicitly include `"Instrumental only, no vocals"`. For vocal title or credits songs, provide bracketed lyrics (`[Verse]`, `[Chorus]`).
5. **Timestamp Arrangements & Loop Boundaries**: For `lyria-3.5` and `lyria-3-pro-preview`, use bracketed timestamps (`[0:00 - 0:15] Intro`, `[0:15 - 1:30] Main Loop`) to direct transitions and match `DecodeMP3WithIntro` loop points in Ebitengine.
