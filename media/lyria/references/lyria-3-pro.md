# Lyria 3 Pro (`lyria-3-pro-preview`) model card

## Overview

**Lyria 3 Pro** (`lyria-3-pro-preview`) is Google's full-length preview music generation model. It creates multi-section MP3 compositions (intro, verse, chorus, bridge, solo, outro) with explicit timestamp controls, dynamic intensity shaping, and multilingual vocal synthesis.

- **Model Code**: `lyria-3-pro-preview`
- **Release Date**: March 2026
- **Status**: Generative AI Preview
- **Vertex AI / Enterprise Location**: `global`
- **Documentation**: [Google Developer Music Generation](https://ai.google.dev/gemini-api/docs/music-generation)

---

## Technical specifications

| Property | Value |
| :--- | :--- |
| **Input Modalities** | Text, Image (up to 10 reference images) |
| **Output Modalities** | Audio (MP3) and Text (Lyrics / Structure) |
| **Input Token Limit** | 131,072 tokens |
| **Audio Output Duration** | **Up to 184 seconds** (about 3 minutes, controllable via prompt) |
| **Audio Quality** | 44.1 kHz stereo MP3, 192 kbps bitrate |
| **Supported MIME Types** | `audio/mp3` |
| **Supported Languages** | English, German, Spanish, French, Hindi, Japanese, Korean, Portuguese |
| **Structural Controls** | Timestamps, BPM, Key, Section Tags, Dynamic Intensity |
| **Watermarking** | SynthID (Audio) + C2PA Content Credentials |

---

## Advanced composition features

### 1. Timestamp and section arrangement control
Lyria 3 Pro interprets timestamp blocks to coordinate instrument entrances, vocal delivery, and dynamic transitions:

```text
[0:00 - 0:15] Intro: Slow atmospheric synthesizer pad in D minor with light rain sounds.
[0:15 - 0:45] Verse 1: Acoustic guitar enters with introspective male vocals singing about twilight.
[0:45 - 1:15] Chorus: Full drums and soaring electric guitar with high energy vocal harmonies.
[1:15 - 1:35] Bridge: Stripped-down piano melody building tension.
[1:35 - 2:05] Final Chorus: Maximum intensity with orchestra and choir backing.
[2:05 - 2:20] Outro: Slow guitar strumming fading to silence.
```

### 2. User-provided lyrics and section tags
You can pass original lyrics structured by section:

```text
Create a modern indie rock anthem at 125 BPM in A Major:

[Verse 1]
Midnight shadows on the pavement wall
Waiting for the summer rain to fall

[Chorus]
We run through the electric haze
Counting down the golden days
```

### 3. Multimodal image-to-song generation
Pass up to 10 images (such as concept art, character designs, or landscapes) to generate a soundtrack matching the visual mood. Note that `lyria-3-pro-preview` outputs `audio/mp3`; use `lyria-3.5` when you need uncompressed WAV output.

---

## CLI and SDK examples

### 1. Python script (`uv run scripts/lyria.py`) and `gemini-api` CLI

```bash
# Generate using the short CLI alias (-m lyria-3-pro)
uv run scripts/lyria.py \
  -p "An emotional cinematic folk song in E Minor at 90 BPM with fingerpicked acoustic guitar and cello." \
  -m lyria-3-pro \
  -f mountain_folk.mp3 \
  --lyrics-file mountain_folk_lyrics.txt

# Or pass the canonical model ID to gemini-api CLI
gemini-api music \
  -m lyria-3-pro-preview \
  -f mountain_folk_prompt.txt \
  --out mountain_folk.mp3
```

### 2. Full song with timestamps and structure (Python)

```python
import base64
from google import genai

client = genai.Client()

prompt = """
An emotional cinematic folk song in E Minor at 90 BPM with fingerpicked acoustic guitar and cello:

[0:00 - 0:20] Intro: Gentle fingerpicked acoustic guitar with subtle cello harmony.
[0:20 - 0:50] Verse 1: Warm vocals singing about distant mountains under winter skies.
[0:50 - 1:20] Chorus: Swelling strings and acoustic rhythm with resonant vocal harmonies.
[1:20 - 1:40] Outro: Soft solo cello fading out.
"""

interaction = client.interactions.create(
    model="lyria-3-pro-preview",
    input=prompt,
)

if interaction.output_audio:
    with open("mountain_folk.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))

if interaction.output_text:
    with open("mountain_folk_lyrics.txt", "w") as f:
        f.write(interaction.output_text)
```

### 3. Multimodal concept-to-soundtrack (Python)

```python
import base64
from google import genai

client = genai.Client()

def read_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

interaction = client.interactions.create(
    model="lyria-3-pro-preview",
    input=[
        {"type": "image", "data": read_b64("concept_art.jpg"), "mime_type": "image/jpeg"},
        {
            "type": "text",
            "text": "Compose a sweeping orchestral score reflecting the scale and mysterious mood of this landscape. Instrumental only, no vocals.",
        },
    ],
)

if interaction.output_audio:
    with open("film_score.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))
```
