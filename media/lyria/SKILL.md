---
name: lyria
description: >
  Generative music and audio synthesis from text prompts or reference images
  using Google Lyria 3 models. Generates 44.1 kHz stereo music clips, full songs
  with custom lyrics, and instrumental soundtracks using lyria-3-clip-preview
  and lyria-3-pro-preview, with support for multimodal image inputs and MP3/WAV
  export. Activate when composing background music, generating songs, creating
  soundtracks from images, or producing AI audio clips.
license: Apache-2.0
metadata:
  category: media
  tags: "music, audio, generative-ai, sound"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  canonical: https://skills.danicat.dev/media/lyria/
---

# Lyria Music Generation Skill

Generate high-fidelity **44.1 kHz stereo audio**, full songs with structured lyrics, instrumental soundtracks, and thematic compositions from text prompts or visual reference images using Google's **Lyria 3** foundation models (`lyria-3-clip-preview` and `lyria-3-pro-preview`).

---

## Available scripts

- `scripts/lyria.py`: CLI tool for text-to-music and image-to-music generation, lyric export, and audio format conversion.
- `scripts/test_lyria.py`: Test suite verifying Lyria argument parsing and multimodal input limit enforcement.

---

## Trigger Conditions
Activate this skill whenever the user asks to:
- Generate music, songs, soundtracks, game audio beds, or background music.
- Compose musical themes inspired by artwork, concept photos, or screenshots.
- Create 30-second audio loops or multi-minute structured songs with verses, choruses, and custom lyrics.
- Synthesize instrumental audio tracks (`"Instrumental only, no vocals"`).

---

## Model Selection & Comparison Matrix

| Model | Model ID | CLI Name | Primary Use Case | Duration | Audio Format | Reference Guide |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Lyria 3 Clip** | `lyria-3-clip-preview` | `clip` | Short clips, loops, previews, rapid style testing | Exactly 30s | MP3, WAV | [lyria-3-clip.md](references/lyria-3-clip.md) |
| **Lyria 3 Pro** | `lyria-3-pro-preview` | `pro` | Full songs, multi-section arrangements, film scoring | Up to 184s | MP3, WAV | [lyria-3-pro.md](references/lyria-3-pro.md) |

### Model Selection Guide
- **Rapid Prototyping**: Start with **Lyria 3 Clip** (`clip`) to iterate quickly on genre combinations, tempos, and instrumentation.
- **Full Song Production**: Select **Lyria 3 Pro** (`pro`) when requiring timestamped transitions (`[0:00 - 0:15] Intro...`), multi-verse vocal delivery, or multi-minute thematic development.

---

## Deep Technical References

Consult dedicated reference cards in `references/` for detailed audio parameters, timing controls, and API schemas:

- **[references/lyria-3-clip.md](references/lyria-3-clip.md)**: Specifications for 30-second clips, loops, and rapid prototyping.
- **[references/lyria-3-pro.md](references/lyria-3-pro.md)**: Specifications for full-length song arrangement, timestamp controls, and multimodal scoring.
- **[references/README.md](references/README.md)**: Musical composition prompt reference and index.

---

## Core Execution Workflows

### 1. CLI Execution via `scripts/lyria.py`

Execute `scripts/lyria.py` with `uv run`:

```bash
# Generate a 30-second chiptune arcade loop with Lyria 3 Clip
uv run scripts/lyria.py \
  -p "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only." \
  -f "chiptune.mp3" \
  -m "clip"

# Generate a full orchestral soundtrack with Lyria 3 Pro
uv run scripts/lyria.py \
  -p "An epic cinematic orchestral theme building from quiet strings to a triumphant brass finale" \
  -f "soundtrack.mp3" \
  -m "pro" \
  --lyrics-file "structure.txt"

# Multimodal Image-to-Music (compose music inspired by an image)
uv run scripts/lyria.py \
  -p "Ambient relaxing soundscape matching the mood of this landscape. Instrumental only." \
  -i "landscape.jpg" \
  -f "landscape_theme.mp3" \
  -m "pro"
```

#### CLI Argument Reference
- `-p`, `--prompt`: Text prompt describing style, genre, instruments, BPM, and structure (required).
- `-f`, `--filename`: Output audio file path (default: `music.mp3`).
- `-m`, `--model`: `clip` / `lyria-3-clip-preview` or `pro` / `lyria-3-pro-preview` (default: `pro`).
- `-i`, `--input-image`: Path to input image(s) for visual mood inspiration (up to 10).
- `--format`: Audio container format (`mp3` or `wav`).
- `--lyrics-file`: Optional path to write generated lyric transcription / structure text.
- `--api`: `interactions` (default) or `models`.

---

### 2. Dual SDK Integration Patterns

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
    model="lyria-3-pro-preview",
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
    model="lyria-3-pro-preview",
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
5. **Timestamp Arrangements**: For Pro models, use bracketed timestamps (`[0:00 - 0:20]`) to direct transitions and builds.
