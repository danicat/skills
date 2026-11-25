---
name: nano-banana
description: >
  Conversational image generation and multimodal editing with Google Nano
  Banana models via uv run scripts/banana.py, the gemini-api CLI, and Google
  Gen AI SDKs. Generates up to 4K visuals, panoramas, character sheets, and
  chroma-key sprite grids with multi-image reference consistency and Search
  grounding. Activate when generating or editing images, sprites, or art, or
  when asked to "banana" an image.
license: Apache-2.0
metadata:
  category: media
  tags: "image-generation, image-editing, sprites, generative-ai, vertex-ai, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.6.1"
  catalog: https://skills.danicat.dev
---

# Nano Banana image generation

Generate, edit, and iterate on visual assets conversationally with Google's **Nano Banana** models (`gemini-nano-banana-2.1`, `gemini-3.1-flash-lite-image`, `gemini-3.1-flash-image`, and `gemini-3-pro-image`) using **`uv run scripts/banana.py`** (which supports both **Vertex AI / Gemini Enterprise** Application Default Credentials and `GEMINI_API_KEY`), the **`gemini-api` CLI** (`gemini-api image`), or the **Google Gen AI SDKs**.

> [!CAUTION]
> **Fail fast with zero fallbacks on authentication or tool errors**:
> Never improvise workarounds if `gemini-api` or `scripts/banana.py` fails. If `gemini-api` is missing or fails because only Vertex AI / Gemini Enterprise credentials are present, run `uv run scripts/banana.py` with Application Default Credentials (`gcloud auth application-default login --billing-project YOUR_PROJECT_ID`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION="global"`, `GOOGLE_GENAI_USE_ENTERPRISE="true"`). If authentication still fails, **stop at once**, report the exact error to the user, and ask them to configure credentials. Never invent placeholder images or fall back to unauthorized generators.

---

## Available scripts

- **[scripts/banana.py](scripts/banana.py)**: PEP 723 standalone Python CLI (`uv run scripts/banana.py`) for text-to-image generation, multimodal editing, multi-turn `--previous-interaction-id` iteration, and reference consistency with capability guards and first-class **Vertex AI / Gemini Enterprise** (`enterprise=True`, `GOOGLE_CLOUD_PROJECT` or ADC billing project, `GOOGLE_CLOUD_LOCATION="global"`, ADC) and **Gemini Developer API** (`GEMINI_API_KEY`) support.
- **[scripts/test_banana.py](scripts/test_banana.py)**: Automated contract and execution test suite validating Interactions API payloads directly against `google-genai` Pydantic schemas, end-to-end mocked image writes (including thought-part filtering and steps fallback), ADC/quota-project authentication, capability guards, and retired model rejection (`uv run scripts/test_banana.py`).

---

## Authentication and setup

### Option A: `uv run scripts/banana.py` (Vertex AI / Gemini Enterprise and API key)

`scripts/banana.py` uses PEP 723 inline dependencies (`google-genai>=3.3.0`, `pillow>=10.0.0`, `google-auth>=2.0.0`), so `uv run` sets up an isolated environment automatically.

```bash
# 1. Authenticate with Vertex AI / Gemini Enterprise (Application Default Credentials)
gcloud auth application-default login --billing-project YOUR_PROJECT_ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_ENTERPRISE="true"
# (Or pass per command: --enterprise --project "YOUR_PROJECT_ID" --location "global")

# 2. Or authenticate with the Gemini Developer API (API key)
export GEMINI_API_KEY="your-api-key"

# 3. Verify CLI flags and capability checks offline
uv run scripts/banana.py --help
uv run scripts/test_banana.py
```

### Option B: `gemini-api` CLI setup

```bash
# 1. Verify or install gemini-api CLI on macOS and Linux
command -v gemini-api >/dev/null 2>&1 || (curl -fsSL https://raw.githubusercontent.com/google-gemini/gemini-api-cli/main/scripts/install.sh | bash)

# 2a. Configure a Gemini Developer API key
export GEMINI_API_KEY="your-api-key"
gemini-api configure --api-key "your-api-key"

# 2b. Or pass an OAuth2 bearer token for Google Cloud / ADC
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language"
export GEMINI_ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"
export GEMINI_USER_PROJECT="your-gcp-project-id"

gemini-api whoami
gemini-api image --help
```

---

## Trigger conditions

Activate this skill whenever the user asks to:
- Generate illustrations, key art, UI assets, character sheets, sprite animation grids, or panoramic backgrounds (`1:4`, `4:1`, `1:8`, `8:1`) up to `4K`.
- Edit, restyle, translate, or combine existing images conversationally.
- Use **"banana" as a verb** (such as "banana this image" or "banana this photo into 16-bit pixel art").
- Keep character, object, or style consistency across scenes with reference images (`-i`).

---

## Model selection and capability matrix

| Capability / Feature | Nano Banana 2.1 (`nano-banana-2.1`) | Nano Banana 2 Lite (`nano-banana-2-lite`) | Nano Banana 2 (`nano-banana-2`) | Nano Banana Pro (`nano-banana-pro`) |
| :--- | :--- | :--- | :--- | :--- |
| **Model ID (`-m`)** | `gemini-nano-banana-2.1` | `gemini-3.1-flash-lite-image` | `gemini-3.1-flash-image` | `gemini-3-pro-image` |
| **Primary Focus** | **Primary workhorse**: speed, 4K, panoramas, Search grounding, multi-turn editing | Latency under 2 seconds and high throughput at low cost | **Deprecated** (Oct 6, 2026; migrate to `nano-banana-2.1`); retains `512` (`512px`) output | Studio precision, interleaved storyboards, style references |
| **Resolutions (`-r`)** | `1K`, `2K`, `4K` | `1K` (1024px) only | `512` (`512px` in Models API), `1K`, `2K`, `4K` | `1K`, `2K`, `4K` |
| **Aspect Ratios (`-a`)** | All 14 discrete ratios (panoramic seam elimination on `1:4`, `4:1`, `1:8`, `8:1`) | All 14 discrete ratios | All 14 discrete ratios (incl. `1:4`, `4:1`, `1:8`, `8:1`) | 10 standard ratios |
| **Search Grounding** | **Web Search + Image Search** | Not supported | **Web Search + Image Search** | **Web Search** |
| **Thinking Mode** | `minimal`, `medium` (**default**), `high` | `minimal` (**default**), `high` | `minimal` (**default**), `high` | Enabled by default |
| **Video Context** | YouTube URLs and MP4 files | YouTube URLs and MP4 files | YouTube URLs and MP4 files | Not supported |
| **Reference Anchors (`-i`)** | Up to 14 (up to 10 objects + 4 characters) + conversational regional edits | Up to 14 (best for single-image local edits) | Up to 14 (up to 10 objects + 4 characters) | Up to 14 (up to 6 objects + 5 characters + 3 styles) |
| **Function Calling** | Not supported | Supported | Not supported | Not supported |
| **Reference Guide** | [nano-banana-2-1.md](references/nano-banana-2-1.md) | [nano-banana-2-lite.md](references/nano-banana-2-lite.md) | [nano-banana-2.md](references/nano-banana-2.md) | [nano-banana-pro.md](references/nano-banana-pro.md) |

> [!IMPORTANT]
> **Vertex AI `global` endpoint, unsupported parameters, and retired models**:
> - **Use `global` on Vertex AI / Gemini Enterprise**: `gemini-nano-banana-2.1` runs on the `global` endpoint (`us-central1` returns `404`).
> - **Do not pass sampling parameters to `gemini-nano-banana-2.1`**: `seed`, `temperature`, `topP`, `topK`, and `logprobs` are unsupported and return an HTTP `400` API error.
> - **Retired and deprecated models**: All `imagen-4.0*` and `imagen-3.0*` models shut down on August 17, 2026, legacy `gemini-2.5-flash-image` is deprecated, and `gemini-3.1-flash-image` (`nano-banana-2`) was deprecated on October 6, 2026 (no shutdown date announced). Migrate to `gemini-nano-banana-2.1`, `gemini-3.1-flash-lite-image`, or `gemini-3-pro-image`.

---

## Technical reference cards

Consult the model cards in `references/` for full resolution grids, token budgets (note `4K` output uses `2,520` tokens on the Gemini Developer API and `3,780` tokens on Vertex AI / Agent Platform), and SDK examples in Python, JavaScript, Java, and Go:
- **[references/nano-banana-2-1.md](references/nano-banana-2-1.md)**
- **[references/nano-banana-2-lite.md](references/nano-banana-2-lite.md)**
- **[references/nano-banana-2.md](references/nano-banana-2.md)**
- **[references/nano-banana-pro.md](references/nano-banana-pro.md)**
- **[references/README.md](references/README.md)**

---

## Core workflows

### 1. Python CLI via `uv run scripts/banana.py`

```bash
# Seamless 4:1 parallax strip with Nano Banana 2.1, medium thinking, and Image Search
uv run scripts/banana.py \
  -p "A seamless 2D side-scrolling pixel-art parallax background of a synthwave city skyline" \
  -f "synthwave_parallax.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "4:1" \
  --thinking-level "medium" \
  --image-search

# Explicit Vertex AI / Gemini Enterprise call on the global endpoint
uv run scripts/banana.py \
  -p "A minimalist flat illustration of a potion bottle icon on a dark UI card" \
  -f "potion_icon_lite.png" \
  -m "nano-banana-2-lite" \
  -a "1:1" \
  --enterprise \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --location "${GOOGLE_CLOUD_LOCATION:-global}"

# Multimodal reference edit ("banana this")
uv run scripts/banana.py \
  -p "banana this character: place the character from the first image into the retro space suit from the second image on a lunar base" \
  -i "assets/hero_sheet.png" \
  -i "assets/spacesuit_ref.png" \
  -f "astronaut_hero.png" \
  -m "nano-banana-2.1" \
  -r "2K"

# Validate flags and capability rules offline
uv run scripts/banana.py -p "Treasure chest icon" -f "chest.png" -m "nano-banana-2.1" -r "2K" --dry-run
```

#### `scripts/banana.py` argument reference
- `-p`, `--prompt`: Generation or edit instructions (required).
- `-f`, `--filename`, `-o`, `--out`, `--output`: Output image path (required; parent directories are created automatically).
- `-i`, `--input-image`: Input or reference image path (repeat up to 14 times; `.png`, `.jpg`, `.jpeg`, `.webp`, `.heic`, `.heif`).
- `-m`, `--model`: `nano-banana-2.1` (default, alias `nano-banana-2-1`), `nano-banana-2-lite`, `nano-banana-2`, `nano-banana-pro`.
- `-r`, `--resolution`: `512` (`512px`, `nano-banana-2` only; sends `"512"` on Interactions API and `"512px"` on Models API), `1K` (default), `2K`, `4K`.
- `-a`, `--aspect-ratio`: `1:1` (default), `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`.
- `--thinking-level`: `minimal`, `medium` (`nano-banana-2.1` only), or `high`.
- `--search` / `--image-search`: Enable Google Web Search (`2.1`, `2`, `pro`) or Web + Image Search (`2.1`, `2`).
- `--previous-interaction-id`, `--store` / `--no-store`: Multi-turn conversational editing state (`--api interactions` only; prints `Interaction ID:` on response).
- `--api`: `interactions` (default) or `models` (`generate_content` with `GenerateContentConfig`).
- `--enterprise` / `--vertexai`, `--project`, `--location`: Vertex AI / Gemini Enterprise ADC (`GOOGLE_CLOUD_PROJECT` or ADC billing project; `GOOGLE_CLOUD_LOCATION` defaults to `global`).
- `--dry-run`: Validate model capabilities, input formats, and Interactions API JSON payload offline without calling the API.

### 2. CLI execution via `gemini-api image`

```bash
# Single-turn generation with Nano Banana 2.1 and medium thinking
gemini-api image \
  "A seamless 2D side-scrolling pixel-art parallax background of a synthwave city skyline" \
  --model "gemini-nano-banana-2.1" \
  --image-size "2K" \
  --aspect-ratio "4:1" \
  --body '{"generation_config":{"thinking_level":"medium"}}' \
  --out "synthwave_parallax.png"

# Multi-turn conversational edit using --previous-interaction-id
TURN1_ID=$(gemini-api image "A cozy pixel-art developer desk with warm lamp lighting" \
  --aspect-ratio "16:9" --image-size "2K" --out "studio_v1.png" --jq '.response_id')

gemini-api image "Change the window view to a rainy cyberpunk night and keep the desk untouched" \
  --previous-interaction-id "$TURN1_ID" \
  --out "studio_v2.png"
```

### 3. Two-step character sheet to sprite grid workflow

Splitting character design from animation grid generation keeps proportions and colors stable across frames:

1. **Step 1 (Reference sheet)**: Generate a `1:1` (`2K`) character turnaround sheet with readable silhouette proportions (`1:2` to `1:3` head-to-body), the target camera projection (`2D side-profile`, `top-down orthographic`, or `2:1 isometric`), clear limb separation from the torso, and a printed 4-step color swatch bar (`Shadow`, `Base`, `Light`, `Specular`) on a flat neutral gray background.
2. **Step 2 (`-i` Chroma-key sprite grid)**: Pass `-i character_sheet.png` with `--thinking-level high` to generate a uniform `4x4` grid (`16` frames) on a flat, unlit `#00FF00` bright green (or `#FF00FF` magenta) background with zero grid lines, borders, shadows, or labels, leaving at least `15%` empty margin inside every cell so poses do not touch cell edges. For jump cycles, name all four phases (`crouch anticipation`, `upward launch`, `rising ascent`, `mid-air apex`).

```bash
uv run scripts/banana.py \
  -p "Keep the exact character proportions and color swatches from the reference sheet. Uniform 4x4 sprite sheet grid in 2D side-profile facing right on a flat unlit #00FF00 background, no grid lines or labels, at least 15% empty #00FF00 margin inside every cell. Row 1: idle. Row 2: walk. Row 3: run. Row 4: 4-phase jump arc (crouch anticipation, launch, rising ascent, mid-air apex)." \
  -i "character_sheet.png" \
  -f "raw_grid_part1.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "1:1" \
  --thinking-level "high"
```

### 4. SDK integration patterns

#### Interactions API (`client.interactions.create`, recommended)

```python
import base64
from google import genai

# Uses GEMINI_API_KEY, or pass enterprise=True, project=..., location="global"
client = genai.Client()

interaction = client.interactions.create(
    model="gemini-nano-banana-2.1",
    input="An infographic chart showing the timeline of space exploration milestones",
    tools=[{"type": "google_search", "search_types": ["web_search", "image_search"]}],
    generation_config={"thinking_level": "medium"},
    response_format={"type": "image", "aspect_ratio": "16:9", "image_size": "4K"},
)

if interaction.output_image:
    with open("space_milestones.png", "wb") as f:
        f.write(base64.b64decode(interaction.output_image.data))
```

#### Models API (`client.models.generate_content`)

```python
from google import genai
from google.genai import types
from PIL import Image

client = genai.Client()
img = Image.open("character_sheet.png")

response = client.models.generate_content(
    model="gemini-nano-banana-2.1",
    contents=[img, "Place this character at a cozy pixel-art developer desk with warm lighting."],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    ),
)

for part in response.candidates[0].content.parts:
    if not getattr(part, "thought", False) and part.inline_data:
        with open("hero_studio.png", "wb") as f:
            f.write(part.inline_data.data)
        break
```

---

## Prompting best practices

1. **Specify materials and camera**: Name surface textures, lighting direction, and camera projection (`strict 2D side-profile orthographic`, `2:1 isometric`, `16-bit pixel art`, `cel-shaded 2D art with dark outlines`).
2. **Enforce sprite grid geometry**: State exact rows/columns (`4x4 grid`), unlit solid key background (`#00FF00`), zero borders or text labels, and `15%` empty cell margin.
3. **Anchor identity with `-i`**: Always pass your Step 1 character sheet via `-i` when generating animation sheets or scene variations.
4. **Target edits precisely**: In multi-turn edits, name both what changes and what stays untouched (`"Change only the armor trim to gold. Keep the pose, expression, and background unchanged."`).
5. **Frame scenes positively**: Describe what appears instead of negations (`"an empty, quiet cobblestone street"` rather than `"no cars"`).
