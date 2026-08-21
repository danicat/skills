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
  version: "0.1.1"
  homepage: https://skills.danicat.dev/media/nano-banana/
  canonical: https://skills.danicat.dev/media/nano-banana/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/media/nano-banana
---

# Nano Banana Skill

Generate, edit, and iterate on visuals conversationally using Google's native **Nano Banana** image generation models (`gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, `gemini-3-pro-image`, `gemini-2.5-flash-image`) with Application Default Credentials (ADC) authentication.

---

## Trigger Conditions
Activate this skill whenever the user asks to:
- Generate new images or illustrations from text descriptions.
- Edit, transform, style, or combine existing images.
- Use **"banana" as a verb** (e.g., "please banana this image", "banana this character into anime style", "banana this photo into chibi style").
- Maintain character, subject, or style consistency across generated imagery using reference images.

---

## Model Selection & Capability Matrix

| Feature / Capability | Nano Banana 2 Lite (`nano-banana-2-lite`) | Nano Banana 2 (`nano-banana-2`) | Nano Banana Pro (`nano-banana-pro`) | Nano Banana Legacy (`nano-banana`) |
| :--- | :--- | :--- | :--- | :--- |
| **Model ID** | `gemini-3.1-flash-lite-image` | `gemini-3.1-flash-image` | `gemini-3-pro-image` | `gemini-2.5-flash-image` |
| **Primary Use Case** | High-velocity, budget-sensitive tasks | Generalist workhorse balance of speed & quality | Premium professional asset production | Legacy workhorse (transition to 2 Lite) |
| **Supported Resolutions** | 1K only | 512px (0.5K), 1K, 2K, 4K | 1K, 2K, 4K | 1024px (1K) |
| **Object References** | Up to 14 | Up to 10 | Up to 6 | Up to 3 |
| **Character References** | N/A | Up to 4 | Up to 5 | N/A |
| **Style References** | N/A | N/A | Up to 3 | N/A |
| **Total Ref Images** | Up to 14 | Up to 14 | Up to 14 | Up to 3 |
| **Search Grounding** | Not Supported | Web Search + Image Search | Web Search | Not Supported |
| **Thinking Mode** | Standard | `minimal` / `high` levels | Default thinking | N/A |
| **Video Context** | Not Supported | YouTube URLs & MP4 files | Not Supported | Not Supported |
| **Interleaved Output** | No | No | Supported (text + images) | No |

### Model Selection Guide
- **Nano Banana 2 Lite** (`nano-banana-2-lite` or `nano-banana-lite`): **Default model**. Ultra-fast, budget-conscious, high-volume generation (`gemini-3.1-flash-lite-image`). Ideal for rapid prototyping and high-velocity iteration.
- **Nano Banana 2** (`nano-banana-2`): The versatile, all-around workhorse (`gemini-3.1-flash-image`). Best for general tasks, multi-reference object/character composition, video-to-image, 4K output, and image search grounding.
- **Nano Banana Pro** (`nano-banana-pro`): Premium model (`gemini-3.1-pro-image`). Use for complex visual reasoning, intricate text rendering, professional marketing assets, character consistency with style references, and interleaved story illustrations.
- **Nano Banana** (`nano-banana`): Legacy pioneer model (`gemini-2.5-flash-image`). Transition users to **Nano Banana 2 Lite** for superior quality, lower cost, and lower latency.

---

## Technical Specifications & Configuration

### Resolution & Formatting Rules
- **Resolution Parameter (`image_size`)**: Must use **uppercase 'K'** (e.g. `512px`, `1K`, `2K`, `4K`). Lowercase values (e.g. `1k`) will be rejected.
- **SynthID Watermark**: All generated images automatically include an imperceptible SynthID watermark.

### Supported Aspect Ratios
- **Nano Banana 2 Lite**: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`.
- **Nano Banana 2**: `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`.
- **Nano Banana Pro**: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`.
- **Nano Banana Legacy**: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`.

---

## Multi-Image Character & Style Consistency

To enforce visual consistency across multiple generations:
- **Character Consistency**: Pass 1–5 reference images of the subject via `-i` / `--input-image`. Describe consistent features in your prompt (hair, clothing, facial features, color scheme).
- **Style Consistency**: Attach reference images depicting the desired artistic style (e.g. cel-shaded anime, watercolor, 3D claymation, pixel art).
- **Custom Project References**: Store local reference images in `{baseDir}/references/` or any local asset directory for reusable visual anchors.

---

## Prompting Strategies & Templates

### Text-to-Image Generation

#### 1. Photorealistic Scenes
- **Template**: `A photorealistic [type of shot] of a [subject description] in a [setting description]. [Lighting description]. Shot from a [camera angle] with a [lens type]. [Aspect ratio].`
- **Example**: `A photorealistic wide-angle shot of a vibrant coral reef teeming with tropical fish. Crystal-clear turquoise water with sunbeams filtering down from the surface, illuminating a sea turtle gliding gracefully over the coral. Shot from a low perspective with a wide-angle lens. Aspect ratio 16:9.`

#### 2. Stylized Illustrations & Stickers
- **Template**: `A [style] of a [subject with details] doing [activity]. Features [bold outlines, cel-shading, etc.] and [color/background preference].`
- **Example**: `A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat, munching on a green bamboo leaf. Bold clean outlines, simple cel-shading, vibrant colors. Solid white background.`

#### 3. Accurate Text Rendering
- **Template**: `Create a [image type] for [brand/concept] with the text "[exact text]" in a [font style]. The design should be [style description], with a [color scheme].`
- **Example**: `Create a modern minimalist logo for a coffee shop called 'The Daily Grind'. The text should be in a clean bold sans-serif font. Black and white color scheme inside a circle, incorporating a coffee bean.`

#### 4. Product Mockups & Commercial Photography
- **Template**: `A high-resolution studio-lit product photograph of a [product] on a [surface/background]. Lighting is [lighting setup] to [purpose]. Camera angle is [angle] with sharp focus on [key detail].`
- **Example**: `A high-resolution studio-lit product photo of a minimalist matte black ceramic coffee mug on polished concrete. Three-point softbox lighting, soft diffused highlights. 45-degree angle shot with sharp focus on rising steam.`

#### 5. Minimalist & Negative Space Design
- **Template**: `A minimalist composition featuring a single [subject] positioned in the [corner/side]. The background is a vast, empty [color] canvas with negative space. Soft lighting.`
- **Example**: `A minimalist composition featuring a delicate red maple leaf in the bottom-right frame. Vast empty off-white canvas with negative space for text overlay. Soft diffused light.`

#### 6. Sequential Art & Storyboarding
- **Template**: `Make a [N]-panel comic in a [art style] featuring [character/setting].`
- **Example**: `Make a 3-panel comic in a gritty noir art style with high-contrast black and white inks showing a humorous detective scene.`

#### 7. Grounded Search Generation
- **Usage**: Enable `google_search` tool to pull real-time weather, sporting events, or live data into visual graphics.
- **Example**: `Visualize the current 5-day weather forecast for San Francisco as a clean modern weather chart with attire suggestions for each day.`

---

### Image Editing & Multimodal Transformations

#### 1. Adding and Removing Elements
- **Template**: `Using the provided image of [subject], please [add/remove/modify] [element]. Ensure the change [integration description].`
- **Example**: `Using the provided image of my cat, please add a small knitted wizard hat on its head. Ensure it sits comfortably and matches the soft lighting.`

#### 2. Inpainting (Semantic Masking)
- **Template**: `Using the provided image, change only [specific element] to [new element]. Keep everything else in the image exactly the same, preserving original style and lighting.`
- **Example**: `Using the provided image of a living room, change only the blue sofa to a vintage brown leather chesterfield sofa. Keep all other room elements unchanged.`

#### 3. Style Transfer
- **Template**: `Transform the provided photograph of [subject] into the artistic style of [artist/style]. Preserve the original composition but render with [stylistic details].`
- **Example**: `Transform the provided photograph of a modern city street into the style of Van Gogh's Starry Night with swirling impasto brushstrokes and deep blue/yellow palette.`

#### 4. Advanced Multi-Image Composition
- **Template**: `Create a composite image combining elements from the provided images. Take [element from Image 1] and place it on/with [element from Image 2].`
- **Example**: `Take the blue floral dress from the first image and have the woman from the second image wear it in an outdoor e-commerce fashion shot.`

#### 5. Sketch-to-Photo (Bringing Drawings to Life)
- **Template**: `Turn this rough [medium] sketch of a [subject] into a [style] photo. Keep [sketch lines/profile] but add [materials/lighting].`
- **Example**: `Turn this rough pencil sketch of a futuristic car into a polished photo of a concept car in a showroom with metallic blue paint and neon rim lighting.`

---

## Professional Prompting Best Practices
1. **Be Hyper-Specific**: Describe materials, lighting setups, camera lenses, and exact textures (e.g. "ornate elven plate armor etched with silver leaf patterns, high pauldrons shaped like falcon wings").
2. **Specify Intent & Context**: Framing the purpose improves composition (e.g. "e-commerce product shot for high-end skincare" vs "bottle photo").
3. **Iterate Conversationally**: Use multi-turn follow-ups to fine-tune details ("Keep everything the same, but make the background light warmer").
4. **Positive Framing for Negative Prompts**: Instead of saying "no cars", describe the scene positively as "an empty, deserted street with no signs of traffic".
5. **Cinematic Camera Controls**: Use photographic terms like `wide-angle shot`, `macro shot`, `low-angle perspective`, `three-point softbox setup`.

---

## Code Integration Guide (Google GenAI SDK)

### Python SDK (`google-genai`)

```python
from google import genai
import base64

client = genai.Client()

# Text-to-Image Generation
interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="A futuristic city inside a floating glass bottle in space",
    generation_config={"thinking_level": "high"},
    response_format={
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "2K"
    }
)

with open("output.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))
```

### Multimodal Image Editing with Base64

```python
with open("input.png", "rb") as f:
    img_bytes = f.read()

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=[
        {"type": "text", "text": "Add a glowing blue wizard hat to the cat"},
        {
            "type": "image",
            "data": base64.b64encode(img_bytes).decode('utf-8'),
            "mime_type": "image/png"
        }
    ]
)
```

---

## Usage & Execution via CLI

Note: `{baseDir}` refers to the root directory of the installed skill.

Use `uv run` to execute the image generation script at `{baseDir}/scripts/banana.py`.

### CLI Arguments
- `-p`, `--prompt`: Text prompt describing the image to generate or edit (required).
- `-f`, `--filename`: Output image filename (required).
- `-i`, `--input-image`: Path to input/reference image(s). Specified up to 14 times.
- `-m`, `--model`: Model selection (`nano-banana-2-lite`, `nano-banana-2`, `nano-banana-pro`, `nano-banana`). Default: `nano-banana-pro`.
- `-r`, `--resolution`: Output resolution (`1K`, `2K`, `4K`). Default: `1K`.
- `--project`: GCP Project ID for Vertex AI (optional).
- `--location`: GCP Location for Vertex AI (optional, default: `us-central1`).

### Examples

```bash
# Ultra-fast generation with Nano Banana 2 Lite
uv run {baseDir}/scripts/banana.py -p "A minimalist tech workspace with a laptop and coffee cup" -f "workspace_lite.png" -m "nano-banana-2-lite"

# High-resolution 4K generation with Nano Banana 2
uv run {baseDir}/scripts/banana.py -p "A photorealistic macro shot of a Monarch butterfly on a flower" -f "butterfly_4k.png" -m "nano-banana-2" -r "4K"

# Character Consistency Generation with Nano Banana Pro
uv run {baseDir}/scripts/banana.py -p "Character mascot presenting a technical keynote speech" -f "keynote_mascot.png" -i "references/character_front.png" -i "references/character_side.png" -m "nano-banana-pro"

# Image Editing ("banana this")
uv run {baseDir}/scripts/banana.py -p "banana this character into chibi 3D figurine style" -i "character.png" -f "chibi_output.png" -m "nano-banana-2"
```
