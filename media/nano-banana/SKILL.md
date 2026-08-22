---
name: nano-banana
description: >
  Conversational image generation and multimodal image editing tool using Google
  Nano Banana models. Generates high-resolution images (1K, 2K, 4K), performs
  style transfers and image edits ("banana this"), and maintains character or
  style consistency using multi-image reference inputs. Activate when generating
  illustrations, editing or transforming images, creating visual assets, or
  maintaining character consistency across scenes.
license: Apache-2.0
metadata:
  category: media
  tags: "image-generation, images, art, generative-ai"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  canonical: https://skills.danicat.dev/media/nano-banana/
---

# Nano Banana Skill

Generate, edit, and iterate on visual imagery conversationally using Google's native **Nano Banana** image generation foundation models (`gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, `gemini-3-pro-image`, `gemini-2.5-flash-image`).

---

## Available scripts

- `scripts/banana.py`: Production CLI tool for text-to-image generation, multimodal editing, and consistency anchoring with model capability validation.
- `scripts/test_banana.py`: Test suite verifying CLI argument parsing and capability validation guards.

---

## Trigger Conditions
Activate this skill whenever the user asks to:
- Generate new images or illustrations from text prompts.
- Edit, transform, style, or combine existing images.
- Use **"banana" as a verb** (e.g., "please banana this image", "banana this character into anime style", "banana this photo into chibi style").
- Maintain character, subject, or style consistency across generated imagery using reference images.
- Create 4K high-resolution visual assets or extreme aspect-ratio banners (`1:4`, `4:1`, `1:8`, `8:1`).

---

## Model Selection & Capability Matrix

| Capability / Feature | Nano Banana 2 Lite (`nano-banana-2-lite`) | Nano Banana 2 (`nano-banana-2`) | Nano Banana Pro (`nano-banana-pro`) | Nano Banana (`nano-banana`) |
| :--- | :--- | :--- | :--- | :--- |
| **Model ID** | `gemini-3.1-flash-lite-image` | `gemini-3.1-flash-image` | `gemini-3-pro-image` | `gemini-2.5-flash-image` |
| **Primary Focus** | Ultra-low latency (<2s), high volume | Generalist workhorse, speed + 4K | Studio precision & asset production | Foundational (Retiring Oct 2026) |
| **Resolutions** | `1K` (1024px) only | `512px` (0.5K), `1K`, `2K`, `4K` | `1K`, `2K`, `4K` | `1K` (1024px) only |
| **Aspect Ratios** | 14 discrete ratios | 14 discrete ratios (incl. `1:4`, `4:1`, `1:8`, `8:1`) | 10 standard ratios | 10 standard ratios |
| **Search Grounding** | ❌ Not Supported | **Web Search + Image Search** | **Web Search** | ❌ Not Supported |
| **Thinking Mode** | Supported (`minimal`, `high`) | Supported (`minimal`, `high`) | Enabled by Default | ❌ Not Supported |
| **Video Context** | ❌ Not Supported | YouTube URLs & MP4 files | ❌ Not Supported | ❌ Not Supported |
| **Reference Anchors** | Up to 14 (Local/Single edit focus) | Up to 10 objects + 4 characters | Up to 6 objects + 5 characters + 3 styles | Up to 3 input images |
| **Function Calling**| Supported | ❌ Not Supported | ❌ Not Supported | ❌ Not Supported |
| **Reference Guide** | [nano-banana-2-lite.md](references/nano-banana-2-lite.md) | [nano-banana-2.md](references/nano-banana-2.md) | [nano-banana-pro.md](references/nano-banana-pro.md) | [nano-banana.md](references/nano-banana.md) |

---

## Deep Technical References

Consult dedicated reference cards in `references/` for full specs, exact token counts, and pixel dimensions:

- **[references/nano-banana-2-lite.md](references/nano-banana-2-lite.md)**: Consult when building real-time UI tools, fast prototyping, or cost-critical high-frequency pipelines.
- **[references/nano-banana-2.md](references/nano-banana-2.md)**: Consult for 4K generation, Google Image Search Grounding, video-to-image workflows, and ultra-wide/tall banners (`1:4`, `4:1`, `1:8`, `8:1`).
- **[references/nano-banana-pro.md](references/nano-banana-pro.md)**: Consult for studio asset production, multi-reference consistency across 14 anchors (objects + characters + artistic style), and storyboards.
- **[references/nano-banana.md](references/nano-banana.md)**: Consult for `gemini-2.5-flash-image` specifications and migration paths.
- **[references/README.md](references/README.md)**: Index and guidelines for storing project-specific visual consistency anchors.

---

## Core Execution Workflows

### 1. CLI Execution via `scripts/banana.py`

Run `scripts/banana.py` with `uv run` to generate or edit images:

```bash
# High-velocity 1K generation with Nano Banana 2 Lite (Default)
uv run scripts/banana.py \
  -p "A minimalist flat illustration of a coffee cup on a wooden table" \
  -f "coffee_lite.png" \
  -m "nano-banana-2-lite" \
  -a "1:1"

# Studio-quality 4K generation with Nano Banana Pro
uv run scripts/banana.py \
  -p "An authentic architectural photograph of a modern library atrium with skylights" \
  -f "library_4k.png" \
  -m "nano-banana-pro" \
  -r "4K" \
  -a "16:9" \
  --search

# Ultra-wide banner (4:1) with Nano Banana 2 and Image Search Grounding
uv run scripts/banana.py \
  -p "A panorama header of the Swiss Alps at sunrise with fresh snow" \
  -f "alps_banner.png" \
  -m "nano-banana-2" \
  -r "2K" \
  -a "4:1" \
  --image-search

# Conversational Image Editing ("banana this") with Multi-Reference Consistency
uv run scripts/banana.py \
  -p "banana this character: place the character into an astronaut suit on Mars" \
  -i "references/mascot_front.png" \
  -i "references/suit_concept.png" \
  -f "astronaut_mascot.png" \
  -m "nano-banana-2" \
  -r "2K"
```

#### CLI Argument Reference
- `-p`, `--prompt`: Text prompt describing generation or edit instructions (required).
- `-f`, `--filename`: Output file path for generated PNG/JPEG (required).
- `-i`, `--input-image`: Path to input/reference image(s). Can be specified up to 14 times.
- `-m`, `--model`: `nano-banana-2-lite` (default), `nano-banana-2`, `nano-banana-pro`, `nano-banana`.
- `-r`, `--resolution`: `512px`, `1K` (default), `2K`, `4K`.
- `-a`, `--aspect-ratio`: `1:1` (default), `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`.
- `--thinking-level`: `minimal` or `high` (Banana 2 & Banana 2 Lite).
- `--search`: Enable Google Search Grounding (Banana 2 & Banana Pro).
- `--image-search`: Enable Google Image Search Grounding (Banana 2 only).
- `--api`: `interactions` (default, Interactions API) or `models` (`generate_content`).

---

### 2. Dual SDK Integration Patterns

#### Interactions API (`client.interactions.create`) — Recommended
Best for multi-turn editing, search grounding, and stateful iteration:

```python
import base64
from google import genai

client = genai.Client()

# Text-to-Image Generation with 4K Resolution & Search Grounding
interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="An infographic chart showing the timeline of space exploration milestones",
    tools=[{"type": "google_search"}],
    generation_config={"thinking_level": "high"},
    response_format={
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "4K",
    },
)

if interaction.output_image:
    with open("space_milestones.png", "wb") as f:
        f.write(base64.b64decode(interaction.output_image.data))
```

#### Models API (`client.models.generate_content`)
Direct stateless multimodal generation:

```python
from google import genai
from PIL import Image

client = genai.Client()

img = Image.open("references/product.png")
response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=[img, "Place this product on a sleek marble countertop with soft studio lighting."],
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("product_studiolit.png", "wb") as f:
            f.write(part.inline_data.data)
        break
```

---

## Prompting Best Practices
1. **Be Hyper-Specific**: Define materials, surface textures, lighting setups, and camera angles (`three-point softbox`, `macro lens`, `shallow depth of field`).
2. **Context & Intent**: State the functional purpose (`e-commerce hero banner`, `editorial illustration`, `app store icon`).
3. **Conversational Inpainting**: When editing, clearly describe what to modify while instructing to preserve unchanged surroundings (`"Change only the sofa to brown vintage leather. Keep all lighting and room decor untouched."`).
4. **Positive Framing**: Describe what should appear instead of using negative constraints (`"an empty street with no signs of vehicles"` rather than `"no cars"`).
