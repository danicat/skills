# Lyria 3 Clip (`lyria-3-clip-preview`) model card

## Overview

**Lyria 3 Clip** (`lyria-3-clip-preview`) is Google's high-speed music generation model optimized for short 30-second MP3 clips, social audio, background beds, and rapid style prototyping. It produces fixed 30-second stereo MP3 tracks along with synchronized lyric transcriptions and musical structure from text prompts or visual reference images.

- **Model Code**: `lyria-3-clip-preview`
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
| **Audio Output Duration** | **Fixed 30 seconds** |
| **Audio Quality** | 44.1 kHz stereo MP3, 192 kbps bitrate |
| **Supported MIME Types** | `audio/mp3` |
| **Supported Languages** | English, German, Spanish, French, Hindi, Japanese, Korean, Portuguese |
| **Capabilities** | Text-to-Music, Image-to-Music, Vocal generation, Instrumental mode, User lyrics |
| **Watermarking** | SynthID (Audio) + C2PA Content Credentials |

---

## Capabilities and limitations

### Strengths
1. **Fast prototyping**: Low-latency generation suited for iterating on musical genres, chord progressions, and tempos.
2. **Multimodal composition**: Composes audio beds reflecting the palette, lighting, and mood of up to 10 input images.
3. **Instrumental isolation**: Produces clean instrumental backing tracks when prompted with `"Instrumental only, no vocals"`.
4. **Synchronized lyrics**: Returns lyric structure in the `output_text` field.

### Limitations
- **Fixed 30-second MP3 output**: Always produces 30-second MP3 tracks (`audio/mp3` only). For uncompressed WAV export or multi-minute compositions, use **Lyria 3.5** (`lyria-3.5`).
- **Single-turn**: Does not support sequential multi-turn audio inpainting or stem editing.

---

## CLI and SDK examples

### 1. Python script (`uv run scripts/lyria.py`) and `gemini-api` CLI

```bash
# Generate a 30-second chiptune clip via uv run scripts/lyria.py (supports GEMINI_API_KEY or Gemini Enterprise / Vertex AI ADC)
uv run scripts/lyria.py \
  -p "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals." \
  -m lyria-3-clip \
  -f chiptune.mp3

# Or generate with gemini-api CLI
gemini-api music "An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals." \
  -m lyria-3-clip-preview \
  --out chiptune.mp3
```

### 2. Python SDK (`google-genai`, Interactions API)

```python
import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="lyria-3-clip-preview",
    input="An energetic 8-bit chiptune arcade melody at 140 BPM in C major. Instrumental only, no vocals.",
)

if interaction.output_audio:
    with open("chiptune.mp3", "wb") as f:
        f.write(base64.b64decode(interaction.output_audio.data))

if interaction.output_text:
    print("Song Structure / Lyrics:\n", interaction.output_text)
```

### 3. JavaScript / TypeScript SDK (`@google/genai`)

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({});

async function generateClip() {
  const interaction = await ai.interactions.create({
    model: "lyria-3-clip-preview",
    input: "A 30-second lo-fi hip-hop beat with vinyl crackle and mellow electric piano at 85 BPM. Instrumental only, no vocals.",
  });

  if (interaction.output_audio) {
    fs.writeFileSync("lofi_loop.mp3", Buffer.from(interaction.output_audio.data, "base64"));
  }
}

generateClip();
```

### 4. REST / cURL

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "lyria-3-clip-preview",
    "input": "A bright bossa nova guitar piece in F major. Instrumental only, no vocals."
  }'
```
