---
name: nano-banana
description: >
  Conversational image generation and multimodal image editing using Google
  Nano Banana models via uv run scripts/banana.py, the gemini-api CLI, and
  Google Gen AI SDKs. Generates high-resolution images (512px, 1K, 2K, 4K),
  2D game character sheets, chroma-key sprite grids, and seamless parallax
  backgrounds, performs style transfers and mask-based image edits ("banana this"),
  and maintains character or style consistency using multi-image reference inputs.
  Activate when generating illustrations, game art, sprites, editing or
  transforming images, or maintaining character consistency across scenes.
license: Apache-2.0
metadata:
  category: media
  tags: "image-generation, images, art, sprites, gamedev, generative-ai, vertex-ai, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.5.0"
  catalog: https://skills.danicat.dev
---

# Nano Banana Skill (`nano-banana`)

Generate, edit, and iterate on visual assets conversationally using Google's **Nano Banana** image generation models (`gemini-nano-banana-2.1`, `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, `gemini-3-pro-image`) via **`uv run skills/nano-banana/scripts/banana.py`** (which supports both **Vertex AI / Gemini Enterprise** Application Default Credentials and `GEMINI_API_KEY`), the **`gemini-api` CLI** (`gemini-api image`), or the **Google Gen AI SDKs**.

> [!CAUTION]
> **Fail Fast with Zero Fallbacks on Authentication or Tool Failure**:
> Never go rogue if `gemini-api` or `scripts/banana.py` fails. If `gemini-api` is unavailable or fails because only Vertex AI / Gemini Enterprise credentials are configured, run `uv run skills/nano-banana/scripts/banana.py` with Vertex AI / Application Default Credentials (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `gcloud auth application-default login`). If authentication still fails, **stop immediately**, report the exact authentication error to the user, and ask them to configure credentials (`gcloud auth application-default login` + `export GOOGLE_CLOUD_PROJECT=...`, or `export GEMINI_API_KEY=...`). Never fabricate placeholder images, switch to unauthorized fallback generators, or silently bypass errors.

---

## Available Scripts

- `scripts/banana.py`: PEP 723 standalone Python CLI tool (`uv run skills/nano-banana/scripts/banana.py`) for text-to-image generation, multimodal editing, and reference consistency anchoring with strict capability validation and first-class **Vertex AI / Gemini Enterprise** (`vertexai=True`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, ADC) and **Gemini Developer API** (`GEMINI_API_KEY`) support.
- `scripts/test_banana.py`: Automated test suite verifying CLI argument parsing, model capability guards, and fail-fast authentication checks (`python3 skills/nano-banana/scripts/test_banana.py`).

---

## Prerequisites & Authentication Setup

### Option A: `uv run skills/nano-banana/scripts/banana.py` (Recommended for Vertex AI / Gemini Enterprise & API Key)

`scripts/banana.py` uses PEP 723 inline dependency metadata (`google-genai`, `pillow`, `google-auth`) so `uv run` resolves everything automatically in an isolated environment without manual `pip install` steps.

```bash
# 1. Authenticate with Vertex AI / Gemini Enterprise (Application Default Credentials)
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
# (Or pass per-command: --vertexai --project "your-gcp-project-id" --location "us-central1")

# 2. Or authenticate with the Gemini Developer API (API Key)
export GEMINI_API_KEY="your-api-key"

# 3. Verify CLI flags and capability validation offline
uv run skills/nano-banana/scripts/banana.py --help
python3 skills/nano-banana/scripts/test_banana.py
```

### Option B: `gemini-api` CLI Setup

The `gemini-api` CLI is a zero-dependency binary that writes generated images directly to disk and prints only the output file path to `stdout`.

```bash
# 1. Verify or install gemini-api CLI on macOS and Linux
command -v gemini-api >/dev/null 2>&1 || (curl -fsSL https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.sh | bash)

# 2a. Authenticate with a Gemini API Key (environment variable or OS keychain)
export GEMINI_API_KEY="your-api-key"
gemini-api configure --api-key "your-api-key"

# 2b. Or authenticate with a Google Cloud Project / ADC (OAuth2 bearer token)
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language"
export GEMINI_ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
export GEMINI_USER_PROJECT="your-gcp-project-id"

# 3. Verify credentials and inspect CLI schemas
gemini-api whoami
gemini-api image --help
```

---

## Trigger Conditions

Activate this skill whenever the user asks to:
- Generate new images, 2D character turnaround sheets, raw sprite animation grids, parallax backgrounds, title screens, dialogue portraits, or illustrations from text prompts.
- Edit, transform, restyle, or combine existing images.
- Use **"banana" as a verb** (for example: "please banana this image", "banana this character into anime style", or "banana this photo into 16-bit pixel art").
- Maintain character, subject, or style consistency across scenes and sprite sheets using reference images (`-i`).
- Create 4K visual assets or seamless extreme aspect-ratio banners and parallax strips (`1:4`, `4:1`, `1:8`, `8:1`).

---

## Role in `agy-game-studio`: Game Asset Generation Pipeline

In `agy-game-studio`, `nano-banana` is the generative 2D art engine that works alongside the studio skills:

- **`game-design`**: Turns Game Design Document (GDD) art pillars and visual palettes into concept art, title screens, dialogue portraits, and Step 1 character reference sheets.
- **`sprite-design`**: Consumes `nano-banana` outputs in the **2-Step Character Sheet to Sprite Grid Pipeline**. `nano-banana` generates the Step 1 character sheet and Step 2 raw `4x4` chroma-key sprite grids (`-i character_sheet.png`), which `sprite-design` then cleans, splits, grounds, and exports via `go run . normalize` (or samples into 4-step material ramps via `go run . extract-palette`).
- **`vibe-game-developer`**: Coordinates `nano-banana` art generation with Ebitengine gameplay loops, `sprite-design` animation state machines, and procedural audio.
- **`game-dev-studio`**: Opens the **Game Dev Studio** visual side-panel workbench (`sidecar://agy-game-studio/studio/sprite` for the **Sprite Editor** and `sidecar://agy-game-studio/studio/playtest` for the **Playtest tab**) to inspect normalized `.sprite` and `.aseprite` sheets and playtest animations in live WebAssembly builds.

### The 2-Step Character Sheet to Sprite Grid Workflow (with `sprite-design`)

Single-step sprite generation often struggles because it tries to invent a character's visual identity while keeping frame-to-frame proportions stable across a grid. Splitting character design from animation grid generation solves this:

#### Step 1: Generate the Character Turnaround & Palette Sheet
Generate a single character reference sheet first (`1:1` or `16:9`, `2K` resolution) and enforce four prompt rules:
1. **Readable 2D Game Proportions**: Specify a `1:2` to `1:3` head-to-body ratio so facial expressions, silhouettes, and limbs remain clear at gameplay scale.
2. **Genre Camera Projection**: Match the exact camera angle of the game (`2D side-profile` for platformers, `3/4 top-down orthographic` for RPGs, `isometric 2:1` for tactics, or `front-facing orthographic` for puzzle and card games).
3. **Limb & Prop Separation**: Keep arms, legs, tails, capes, and weapons slightly separated from the torso so silhouette joints are clean.
4. **Printed 4-Step Color Swatch Bar**: Ask for a solid 4-step color ramp bar (`Shadow -> Base -> Light -> Specular`) for each main material so Step 2 locks exact colors (and `sprite-design` can run `extract-palette`).

```bash
# Step 1 (via uv run scripts/banana.py - works with Vertex AI ADC or GEMINI_API_KEY):
uv run skills/nano-banana/scripts/banana.py \
  -p "2D game character reference sheet of an agile cyber-ninja cat in strict 2D side-profile view for a platformer. 1:2.5 head-to-body arcade proportions, clean cel-shaded outlines, arms and tail clearly separated from the torso, plus a printed 4-step color swatch bar (Shadow, Base, Light, Specular) in the corner. Solid flat neutral gray background." \
  -f "character_sheet.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "1:1" \
  --thinking-level "medium"

# Or via gemini-api CLI:
gemini-api image \
  "2D game character reference sheet of an agile cyber-ninja cat in strict 2D side-profile view for a platformer. 1:2.5 head-to-body arcade proportions, clean cel-shaded outlines, arms and tail clearly separated from the torso, plus a printed 4-step color swatch bar (Shadow, Base, Light, Specular) in the corner. Solid flat neutral gray background." \
  --model "gemini-nano-banana-2.1" \
  --aspect-ratio "1:1" \
  --image-size "2K" \
  --body '{"generation_config":{"thinking_level":"medium"}}' \
  --out "character_sheet.png"
```

#### Step 2: Generate Uniform `4x4` Chroma-Key Sprite Grids with `-i` Reference Lock
Pass `-i character_sheet.png` into `scripts/banana.py` or `gemini-api image` to generate uniform `4x4` animation grids (`1:1` aspect ratio at `1K` or `2K` so each cell is `256x256` or `512x512`). For 8 motions (`32` frames), generate two `4x4` grids (`4` rows of `4` frames per grid) using the same `-i character_sheet.png` anchor:

1. **Flat Key Background & Zero Chrome**: Require a flat, unlit `#00FF00` bright green (or `#FF00FF` solid magenta, chosen so it never conflicts with the character palette) background with **no grid lines, no cell borders, no ground shadows, no lighting gradients, and no text labels**.
2. **10% to 15% Cell Boundary Margin**: Require at least **10% to 15% (`25px+` on a `256x256` cell) of empty chroma-key margin** on all four sides of every pose inside its grid cell so feet, tails, or weapons never touch or bleed into neighboring rows or columns.
3. **Complete 4-Frame Parabolic Jump Arc**: When prompting for a 4-frame `jump` row, explicitly list all four phases so it transitions cleanly into `fall`:
   - Frame 1: `crouch anticipation` (coiled low on the ground).
   - Frame 2: `upward launch` (springing steeply upward with extended legs).
   - Frame 3: `rising ascent` (airborne rising pose, arms reaching up).
   - Frame 4: `mid-air peak / apex suspension` (horizontal floating body at the top of the jump arc with legs tucked underneath before falling).

```bash
# Step 2 (via uv run scripts/banana.py):
uv run skills/nano-banana/scripts/banana.py \
  -p "Using the exact character identity, proportions, and color swatches from the reference image, generate a uniform 4x4 sprite sheet grid (4 rows, 4 columns, 16 frames total) in strict 2D side-profile view facing right on a flat unlit solid #00FF00 bright green chroma-key background. No grid lines, no borders, no drop shadows, and no text labels. Keep at least 15% empty #00FF00 margin around every character inside each cell so no limbs touch cell boundaries. Row 1 (frames 1-4): breathing idle cycle. Row 2 (frames 5-8): 4-step walk cycle. Row 3 (frames 9-12): fast leaning run cycle. Row 4 (frames 13-16): 4-phase jump arc (frame 13 coiled crouch anticipation, frame 14 upward launch, frame 15 rising ascent, frame 16 mid-air apex suspension with legs tucked)." \
  -i "character_sheet.png" \
  -f "raw_grid_part1.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "1:1" \
  --thinking-level "high"

# Or via gemini-api CLI:
gemini-api image \
  "Using the exact character identity, proportions, and color swatches from the reference image, generate a uniform 4x4 sprite sheet grid (4 rows, 4 columns, 16 frames total) in strict 2D side-profile view facing right on a flat unlit solid #00FF00 bright green chroma-key background. No grid lines, no borders, no drop shadows, and no text labels. Keep at least 15% empty #00FF00 margin around every character inside each cell so no limbs touch cell boundaries. Row 1 (frames 1-4): breathing idle cycle. Row 2 (frames 5-8): 4-step walk cycle. Row 3 (frames 9-12): fast leaning run cycle. Row 4 (frames 13-16): 4-phase jump arc (frame 13 coiled crouch anticipation, frame 14 upward launch, frame 15 rising ascent, frame 16 mid-air apex suspension with legs tucked)." \
  -i "character_sheet.png" \
  --model "gemini-nano-banana-2.1" \
  --aspect-ratio "1:1" \
  --image-size "2K" \
  --body '{"generation_config":{"thinking_level":"high"}}' \
  --out "raw_grid_part1.png"
```

After generating `raw_grid_part1.png` (and optional `raw_grid_part2.png`), hand the files to `sprite-design`'s normalizer (`cd skills/sprite-design/scripts && go run . normalize -cols 4 -rows 4 ...`) to strip the chroma key, prune any stray border fragments, align baselines, and export `.png`, `.json`, `.aseprite`, and per-motion `.gif` previews.

---

## Model Selection & Capability Matrix

| Capability / Feature | Nano Banana 2.1 (`nano-banana-2.1`) | Nano Banana 2 Lite (`nano-banana-2-lite`) | Nano Banana 2 (`nano-banana-2`) | Nano Banana Pro (`nano-banana-pro`) |
| :--- | :--- | :--- | :--- | :--- |
| **Model ID (`-m`)** | `gemini-nano-banana-2.1` | `gemini-3.1-flash-lite-image` | `gemini-3.1-flash-image` | `gemini-3-pro-image` |
| **Architecture** | Gemini 3.6 Flash (Oct 2026) | Gemini 3.1 Flash Lite | Gemini 3.1 Flash | Gemini 3 Pro |
| **Primary Focus** | **Primary recommended workhorse**; speed, 4K, sprite grids, seamless panoramas, mask editing | Low latency (<2s), high volume | Generalist multimodal generation + 4K | Studio precision & multi-style asset production |
| **Resolutions (`-r` / `--image-size`)** | `512px` (`512`), `1K`, `2K`, `4K` | `1K` (1024px) only | `512px` (`512`), `1K`, `2K`, `4K` | `1K`, `2K`, `4K` |
| **Aspect Ratios (`-a` / `--aspect-ratio`)** | All 14 discrete ratios (seam and tiling elimination on `1:4`, `4:1`, `1:8`, `8:1`) | 14 discrete ratios | 14 discrete ratios (incl. `1:4`, `4:1`, `1:8`, `8:1`) | 10 standard ratios |
| **Search Grounding** | **Web Search + Image Search** | Not Supported | **Web Search + Image Search** | **Web Search** |
| **Thinking Mode** | Supported (`minimal`, `medium`, `high`) | Supported (`minimal`, `high`) | Supported (`minimal`, `high`) | Enabled by Default |
| **Video Context** | YouTube URLs & MP4 files | Not Supported | YouTube URLs & MP4 files | Not Supported |
| **Reference Anchors (`-i`)** | Up to 14 (up to 10 objects + 4 characters) + mask editing | Up to 14 (local/single edit focus) | Up to 10 objects + 4 characters | Up to 6 objects + 5 characters + 3 styles |
| **Function Calling**| Not Supported | Supported | Not Supported | Not Supported |
| **Reference Guide** | [nano-banana-2-1.md](references/nano-banana-2-1.md) | [nano-banana-2-lite.md](references/nano-banana-2-lite.md) | [nano-banana-2.md](references/nano-banana-2.md) | [nano-banana-pro.md](references/nano-banana-pro.md) |

---

## Technical Reference Cards

Consult the model cards in `references/` for full specifications, token tables, and pixel dimensions:

- **[references/nano-banana-2-1.md](references/nano-banana-2-1.md)**: Primary workhorse (`gemini-nano-banana-2.1`), `medium` thinking level, seamless `1:4`/`4:1`/`1:8`/`8:1` panoramas, mask-based conversational editing, and CLI/SDK patterns.
- **[references/nano-banana-2-lite.md](references/nano-banana-2-lite.md)**: Real-time UI tools, rapid prototyping, and cost-efficient `1K` pipelines.
- **[references/nano-banana-2.md](references/nano-banana-2.md)**: `gemini-3.1-flash-image` 4K generation, Google Image Search grounding, and video-to-image workflows.
- **[references/nano-banana-pro.md](references/nano-banana-pro.md)**: Studio asset production, multi-reference consistency across 14 anchors (6 objects + 5 characters + 3 artistic styles), and storyboards.
- **[references/README.md](references/README.md)**: Index of model cards and reference anchor guidelines.

---

## Core Execution Workflows

### 1. Python CLI Execution via `uv run skills/nano-banana/scripts/banana.py`

Run `skills/nano-banana/scripts/banana.py` with `uv run` for full **Vertex AI / Gemini Enterprise** (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, ADC) and **Gemini Developer API** (`GEMINI_API_KEY`) support, strict model capability validation, and dual API selection (`--api interactions` or `--api models`):

```bash
# Seamless 4:1 parallax background strip with Nano Banana 2.1 (Default), medium thinking & Image Search
uv run skills/nano-banana/scripts/banana.py \
  -p "A seamless 2D side-scrolling pixel-art parallax background of a synthwave city skyline" \
  -f "synthwave_parallax.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "4:1" \
  --thinking-level "medium" \
  --image-search

# Explicit Vertex AI / Gemini Enterprise execution using Application Default Credentials
uv run skills/nano-banana/scripts/banana.py \
  -p "A minimalist flat illustration of a potion bottle icon on a dark UI card" \
  -f "potion_icon_lite.png" \
  -m "nano-banana-2-lite" \
  -a "1:1" \
  --vertexai \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "${GOOGLE_CLOUD_LOCATION:-us-central1}"

# Studio-quality 4K key art with Nano Banana Pro and Google Web Search grounding
uv run skills/nano-banana/scripts/banana.py \
  -p "An authentic architectural photograph of a modern library atrium with skylights" \
  -f "library_4k.png" \
  -m "nano-banana-pro" \
  -r "4K" \
  -a "16:9" \
  --search

# Multimodal Image Editing ("banana this") with Multi-Reference Consistency
uv run skills/nano-banana/scripts/banana.py \
  -p "banana this character: place the character from the first image into the retro space suit from the second image on a lunar base" \
  -i "assets/hero_sheet.png" \
  -i "assets/spacesuit_ref.png" \
  -f "astronaut_hero.png" \
  -m "nano-banana-2.1" \
  -r "2K"

# Offline capability validation without network or credential calls
uv run skills/nano-banana/scripts/banana.py \
  -p "Isometric icon of a treasure chest" \
  -f "chest_icon.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "1:1" \
  --dry-run
```

#### `scripts/banana.py` Argument Reference
- `-p`, `--prompt`: Text prompt describing generation or edit instructions (required).
- `-f`, `--filename`: Output file path for generated PNG/JPEG (required).
- `-i`, `--input-image`: Path to input/reference image(s). Can be specified up to 14 times.
- `-m`, `--model`: `nano-banana-2.1` (default, alias `nano-banana-2-1` / `gemini-nano-banana-2.1`), `nano-banana-2` (`gemini-3.1-flash-image`), `nano-banana-2-lite` (alias `nano-banana-lite` / `gemini-3.1-flash-lite-image`), `nano-banana-pro` (`gemini-3-pro-image`).
- `-r`, `--resolution`: `512px` (`512`), `1K` (default), `2K`, `4K`.
- `-a`, `--aspect-ratio`: `1:1` (default), `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`.
- `--thinking-level`: `minimal`, `medium` (Nano Banana 2.1 only), or `high`.
- `--search`: Enable Google Web Search Grounding (`nano-banana-2.1`, `nano-banana-2`, `nano-banana-pro`).
- `--image-search`: Enable Google Image Search Grounding (`nano-banana-2.1` and `nano-banana-2`).
- `--api`: `interactions` (default, Interactions API) or `models` (`generate_content`).
- `--vertexai`: Force Vertex AI / Gemini Enterprise authentication via Application Default Credentials.
- `--project`: Google Cloud Project ID for Vertex AI (defaults to `GOOGLE_CLOUD_PROJECT` or `GCP_PROJECT`).
- `--location`: Google Cloud Location for Vertex AI (defaults to `GOOGLE_CLOUD_LOCATION` or `us-central1`).
- `--dry-run`: Validate model capabilities and CLI arguments without calling the API.

---

### 2. CLI Execution via `gemini-api image`

You can also run `gemini-api image` when `GEMINI_API_KEY` or `GEMINI_ACCESS_TOKEN` is configured:

```bash
# Seamless 4:1 parallax background strip with Nano Banana 2.1 (default model) & medium thinking
gemini-api image \
  "A seamless 2D side-scrolling pixel-art parallax background of a synthwave city skyline" \
  --image-size "2K" \
  --aspect-ratio "4:1" \
  --body '{"generation_config":{"thinking_level":"medium"}}' \
  --out "synthwave_parallax.png"

# Single-Turn Multimodal Image Editing ("banana this") with Reference Anchors
gemini-api image \
  "banana this character: place the character from the first image into the retro space suit from the second image on a lunar base" \
  -i "assets/hero_sheet.png" \
  -i "assets/spacesuit_ref.png" \
  --image-size "2K" \
  --out "astronaut_hero.png"

# Multi-Turn Conversational Editing using --previous-interaction-id
TURN1_ID=$(gemini-api image "A cozy pixel-art game developer studio with warm desk lighting" \
  --aspect-ratio "16:9" \
  --image-size "2K" \
  --out "studio_v1.png" \
  --jq '.response_id')

gemini-api image "Change the window view to a rainy cyberpunk night and add a sleeping cat on the desk" \
  --previous-interaction-id "$TURN1_ID" \
  --out "studio_v2.png"
```

---

### 3. SDK Integration Patterns (Application Backends)

For embedding Nano Banana into backend services, use the typed Google Gen AI SDKs:

#### Interactions API (`client.interactions.create`) (Recommended)
Best for multi-turn editing, search grounding, controllable thinking, and stateful iteration:

```python
import base64
from google import genai

# Automatically uses GEMINI_API_KEY, or pass vertexai=True, project=..., location=... for Vertex AI
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

img = Image.open("character_sheet.png")
response = client.models.generate_content(
    model="gemini-nano-banana-2.1",
    contents=[img, "Place this character in a cozy pixel-art game developer studio with warm desk lighting."],
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("hero_studio.png", "wb") as f:
            f.write(part.inline_data.data)
        break
```

---

## Prompting Best Practices

1. **Be Specific About Materials & Camera**: Define surface textures, lighting setups, and camera projection (`strict 2D side-profile orthographic`, `2:1 dimetric isometric`, `16-bit SNES pixel art`, `clean cel-shaded 2D HD with dark outer outlines`).
2. **State Functional Intent & Chroma Key Constraints**: When generating game sprites, explicitly state the grid layout (`uniform 4x4 sprite sheet grid`), solid key background (`flat unlit #00FF00 bright green background, no shadows, no grid lines, no labels`), and cell safety margins (`at least 15% empty #00FF00 margin around every pose inside each cell`).
3. **Lock Identity with Reference Inputs (`-i`)**: Always pass your Step 1 character sheet via `-i` when generating Step 2 animation grids, additional motion packs, or dialogue portraits so proportions and colors stay consistent.
4. **Conversational Inpainting**: When editing an image, describe what to change while instructing the model to keep everything else intact (`"Change only the armor trim to gold. Keep the pose, facial expression, and #00FF00 background untouched."`).
5. **Positive Framing**: Describe what should appear rather than listing negative words (`"a clean, empty cobblestone street"` rather than `"no cars"`).
