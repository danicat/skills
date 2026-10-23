---
name: nano-banana
description: >
  Conversational image generation and multimodal image editing using Google
  Nano Banana models via the gemini-api CLI and Google Gen AI SDKs. Generates
  high-resolution images (512px, 1K, 2K, 4K), performs style transfers and
  mask-based image edits ("banana this"), and maintains character or style
  consistency using multi-image reference inputs. Activate when generating
  illustrations, editing or transforming images, creating visual assets, or
  maintaining character consistency across scenes.
license: Apache-2.0
metadata:
  category: media
  tags: "image-generation, images, art, generative-ai, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# Nano Banana Skill

Generate, edit, and iterate on visual imagery conversationally using Google's native **Nano Banana** image generation foundation models (`gemini-nano-banana-2.1`, `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, `gemini-3-pro-image`) via the official **`gemini-api` CLI** (`gemini-api image`) for terminal and coding agent workflows, or the **Google Gen AI SDKs** for application backends.

---

## Prerequisites: `gemini-api` CLI Setup

The `gemini-api` CLI is a zero-dependency binary that writes generated images directly to disk and prints only the output file path to `stdout`, keeping raw base64 payloads out of agent context windows.

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
gemini-api image --help
gemini-api image --schema
```

---

## Trigger Conditions
Activate this skill whenever the user asks to:
- Generate new images, sprites, tilesets, or illustrations from text prompts.
- Edit, transform, style, or combine existing images.
- Use **"banana" as a verb** (e.g., "please banana this image", "banana this character into anime style", "banana this photo into chibi style").
- Maintain character, subject, or style consistency across generated imagery using reference images (including the bundled Dani reference anchors).
- Create 4K high-resolution visual assets or seamless extreme aspect-ratio banners (`1:4`, `4:1`, `1:8`, `8:1`).

---

## Model Selection & Capability Matrix

| Capability / Feature | Nano Banana 2.1 (Default) | Nano Banana 2 Lite | Nano Banana 2 | Nano Banana Pro |
| :--- | :--- | :--- | :--- | :--- |
| **Model ID (`-m`)** | `gemini-nano-banana-2.1` | `gemini-3.1-flash-lite-image` | `gemini-3.1-flash-image` | `gemini-3-pro-image` |
| **Architecture** | Gemini 3.6 Flash (Oct 2026) | Gemini 3.1 Flash Lite | Gemini 3.1 Flash | Gemini 3 Pro |
| **Primary Focus** | **Primary recommended workhorse**; speed, 4K, seamless panoramas, mask editing | Ultra-low latency (<2s), high volume | Generalist multimodal generation + 4K | Studio precision & multi-style asset production |
| **Image Sizes (`--image-size`)** | `512` (512px), `1K`, `2K`, `4K` | `1K` (1024px) only | `512` (512px), `1K`, `2K`, `4K` | `1K`, `2K`, `4K` |
| **Aspect Ratios (`--aspect-ratio`)** | All 14 discrete ratios (improved seam/tiling elimination on `1:4`, `4:1`, `1:8`, `8:1`) | 14 discrete ratios | 14 discrete ratios (incl. `1:4`, `4:1`, `1:8`, `8:1`) | 10 standard ratios |
| **Search Grounding** | **Web Search + Image Search** | ❌ Not Supported | **Web Search + Image Search** | **Web Search** |
| **Thinking Mode** | Supported (`minimal`, `medium`, `high`) | Supported (`minimal`, `high`) | Supported (`minimal`, `high`) | Enabled by Default |
| **Video Context** | YouTube URLs & MP4 files | ❌ Not Supported | YouTube URLs & MP4 files | ❌ Not Supported |
| **Reference Anchors (`-i`)** | Up to 14 (up to 10 objects + 4 characters) + mask editing | Up to 14 (Local/Single edit focus) | Up to 10 objects + 4 characters | Up to 6 objects + 5 characters + 3 styles |
| **Function Calling**| ❌ Not Supported | Supported | ❌ Not Supported | ❌ Not Supported |
| **Reference Guide** | [nano-banana-2-1.md](references/nano-banana-2-1.md) | [nano-banana-2-lite.md](references/nano-banana-2-lite.md) | [nano-banana-2.md](references/nano-banana-2.md) | [nano-banana-pro.md](references/nano-banana-pro.md) |

---

## Deep Technical References

Consult dedicated reference cards in `references/` for full specs, exact token counts, and pixel dimensions:

- **[references/nano-banana-2-1.md](references/nano-banana-2-1.md)**: Consult for the primary workhorse (`gemini-nano-banana-2.1`), `medium` thinking level, seamless `1:4`/`4:1`/`1:8`/`8:1` panoramas, mask-based conversational editing, and CLI/SDK patterns.
- **[references/nano-banana-2-lite.md](references/nano-banana-2-lite.md)**: Consult when building real-time UI tools, fast prototyping, or cost-critical high-frequency pipelines (`1K` resolution).
- **[references/nano-banana-2.md](references/nano-banana-2.md)**: Consult for `gemini-3.1-flash-image` 4K generation, Google Image Search Grounding, and video-to-image workflows.
- **[references/nano-banana-pro.md](references/nano-banana-pro.md)**: Consult for studio asset production, multi-reference consistency across 14 anchors (6 objects + 5 characters + 3 artistic styles), and storyboards.
- **[references/README.md](references/README.md)**: Index and guidelines for using the bundled Dani character consistency reference anchors.

---

## Bundled Dani Character Consistency Reference Anchors

The `references/` directory includes 4 ready-to-use PNG reference anchors for **Dani** that can be passed via `-i` / `--input` to `gemini-api image` to maintain character identity or transfer visual style across scenes:

- `references/chibi-dani.png`: Full-body 2D chibi illustration (primary character identity & proportion anchor).
- `references/celebrating-dani.png`: Expressive celebratory pose (facial expression & color palette anchor).
- `references/speaker-dani.png`: Conference speaker pose at podium (wardrobe & upper-body angle anchor).
- `references/chibi_dani_manga.png`: Monochrome manga ink illustration (line-art / manga style transfer anchor).

```bash
# Multi-reference character consistency across 3 Dani anchors with Nano Banana 2.1
gemini-api image \
  "banana this character: render Chibi Dani as a 16-bit pixel-art space captain on a starship bridge, keeping her exact glasses, purple hair, and proportions" \
  -i "references/chibi-dani.png" \
  -i "references/celebrating-dani.png" \
  -i "references/speaker-dani.png" \
  --model "gemini-nano-banana-2.1" \
  --image-size "2K" \
  --aspect-ratio "16:9" \
  --body '{"generation_config":{"thinking_level":"medium"}}' \
  --out "dani_space_captain.png"

# Character + manga style transfer using chibi-dani.png and chibi_dani_manga.png
gemini-api image \
  "Render the character from the first image coding furiously at a multi-monitor setup in the exact black-and-white manga ink style of the second image" \
  -i "references/chibi-dani.png" \
  -i "references/chibi_dani_manga.png" \
  --model "gemini-nano-banana-2.1" \
  --image-size "2K" \
  --aspect-ratio "3:4" \
  --out "dani_manga_coder.png"
```

---

## Core Execution Workflows

### 1. CLI Execution via `gemini-api image`

Use `gemini-api image` for terminal exploration, shell pipelines, and coding agent workflows. It defaults to `gemini-nano-banana-2.1`, writes the image straight to disk, and prints the saved file path to `stdout`:

```bash
# Primary creative workhorse generation with Nano Banana 2.1 (default model), medium thinking & Image Search grounding
gemini-api image \
  "A seamless 2D side-scrolling pixel-art parallax background of a synthwave city skyline" \
  --image-size "2K" \
  --aspect-ratio "4:1" \
  --body '{"generation_config":{"thinking_level":"medium"},"tools":[{"type":"google_search","search_types":["web_search","image_search"]}]}' \
  --out "synthwave_parallax.png"

# High-velocity 1K generation with Nano Banana 2 Lite
gemini-api image \
  "A minimalist flat illustration of a coffee cup on a wooden table" \
  --model "gemini-3.1-flash-lite-image" \
  --aspect-ratio "1:1" \
  --image-size "1K" \
  --out "coffee_lite.png"

# Studio-quality 4K generation with Nano Banana Pro and Google Web Search grounding
gemini-api image \
  "An authentic architectural photograph of a modern library atrium with skylights" \
  --model "gemini-3-pro-image" \
  --image-size "4K" \
  --aspect-ratio "16:9" \
  --body '{"tools":[{"type":"google_search"}]}' \
  --out "library_4k.png"

# Single-Turn Multimodal Image Editing ("banana this") with Reference Anchors
gemini-api image \
  "banana this character: place the character into an astronaut suit on Mars" \
  -i "references/chibi-dani.png" \
  -i "references/celebrating-dani.png" \
  --image-size "2K" \
  --out "astronaut_dani.png"

# Multi-Turn Conversational Editing using --previous-interaction-id
TURN1_ID=$(gemini-api image "A cozy pixel-art game developer studio with warm desk lighting" \
  --aspect-ratio "16:9" \
  --image-size "2K" \
  --out "studio_v1.png" \
  --jq '.response_id')

gemini-api image "Change the window view to a rainy cyberpunk night and add a sleeping cat on the desk" \
  --previous-interaction-id "$TURN1_ID" \
  --out "studio_v2.png"

# Offline Request Validation (no network or keychain calls)
gemini-api image "Isometric icon of a distributed database" --aspect-ratio "1:1" --image-size "2K" --out "./assets/db_icon.png" --dry-run -o json
```

#### `gemini-api image` Flag Reference
- `<prompt>`: Positional text prompt describing the image to generate or edit (or pass `--stdin` to read prompt text from stdin).
- `-m`, `--model`: `gemini-nano-banana-2.1` (default), `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, `gemini-3-pro-image`, `nano-banana-pro-preview`.
- `--out`: Output file path or target directory (default: `./gemini-image-{timestamp}-{rand}.{ext}`).
- `--image-size`: `512` (512px, supported on `gemini-nano-banana-2.1` and `gemini-3.1-flash-image`), `1K`, `2K`, `4K` (`2K`/`4K` unsupported on `gemini-3.1-flash-lite-image`).
- `--aspect-ratio`: `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9` (`1:4`, `4:1`, `1:8`, `8:1` unsupported on `gemini-3-pro-image`).
- `-i`, `--input`: Repeatable local file path, `files/<id>`, or YouTube URL to include as reference input (up to 14 images).
- `--mime-type`: Override the detected MIME type (when a single `--input` is provided).
- `--output-mime-type`: Output image MIME type (e.g., `image/jpeg`).
- `--previous-interaction-id`: Interaction ID from a prior turn (`--out <file> --jq .response_id` or `--raw-response --jq .id`) for stateful multi-turn image editing.
- `--body`: Advanced Interactions API request JSON merged with CLI flags (`@path` reads a file, `@-` reads stdin). Use for:
  - Thinking level: `'{"generation_config":{"thinking_level":"medium"}}'` (`minimal`, `medium` [Nano Banana 2.1 only], `high`).
  - Web Search grounding: `'{"tools":[{"type":"google_search"}]}'`.
  - Web + Image Search grounding: `'{"tools":[{"type":"google_search","search_types":["web_search","image_search"]}]}'` (Nano Banana 2.1 and Nano Banana 2 only).
- `--raw-response`: Print the raw API response JSON instead of writing the image file.
- `--schema` / `--usage` / `--dry-run`: Inspect the exact JSON Schema, KDL command specification, or preview the HTTP request offline without making network calls.
- **Exit Codes**: `0` ok · `1` runtime error · `2` usage/validation error · `3` authentication/authorization error.

---

### 2. Dual SDK Integration Patterns (Application Backends)

For embedding Nano Banana into production backend services, use the typed Google Gen AI SDKs:

#### Interactions API (`client.interactions.create`) — Recommended
Best for multi-turn editing, search grounding, controllable thinking, and stateful iteration:

```python
import base64
from google import genai

client = genai.Client()

# Text-to-Image Generation with Nano Banana 2.1, 4K Resolution, Medium Thinking & Search Grounding
interaction = client.interactions.create(
    model="gemini-nano-banana-2.1",
    input="An infographic chart showing the timeline of space exploration milestones",
    tools=[{"type": "google_search", "search_types": ["web_search", "image_search"]}],
    generation_config={"thinking_level": "medium"},
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

img = Image.open("references/chibi-dani.png")
response = client.models.generate_content(
    model="gemini-nano-banana-2.1",
    contents=[img, "Place this character in a cozy pixel-art game developer studio with warm desk lighting."],
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("dani_studio.png", "wb") as f:
            f.write(part.inline_data.data)
        break
```

---

## Prompting Best Practices
1. **Be Hyper-Specific**: Define materials, surface textures, lighting setups, and camera angles (`three-point softbox`, `macro lens`, `shallow depth of field`, `16-bit SNES pixel art`).
2. **Context & Intent**: State the functional purpose (`2D game sprite sheet with solid #FF00FF chroma key background`, `seamless 4:1 parallax background`, `app store icon`).
3. **Conversational Inpainting**: When editing, clearly describe what to modify while instructing to preserve unchanged surroundings (`"Change only the sofa to brown vintage leather. Keep all lighting and room decor untouched."`).
4. **Positive Framing**: Describe what should appear instead of using negative constraints (`"an empty street with no signs of vehicles"` rather than `"no cars"`).
