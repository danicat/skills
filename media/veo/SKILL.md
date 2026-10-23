---
name: veo
description: >
  Cinematic video generation with native synchronized audio, first-and-last-frame
  interpolation, multi-image asset direction, and scene extension using Google
  Veo models (veo-3.1-generate-preview, veo-3.1-fast-generate-preview,
  veo-3.1-lite-generate-preview, veo-3.0-generate-001) and the gemini-api CLI
  or Google Gen AI SDKs. Generates 4s, 6s, or 8s clips at 720p, 1080p, or 4K
  (extendable up to 148s). Activate when generating cinematic Veo videos,
  interpolating keyframes, directing scenes with up to 3 asset references, or
  extending Veo clips.
license: Apache-2.0
metadata:
  category: media
  tags: "video-generation, veo, animation, generative-ai, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Veo Video Generation Skill

Generate high-definition cinematic video (`720p`, `1080p`, `4k`) with native synchronized dialogue, sound effects, keyframe interpolation (`last_frame`), multi-image asset direction (`reference_images`), and multi-hop scene extension using Google's **Veo** foundation models (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-3.1-lite-generate-preview`, `veo-3.0-generate-001`) via the **Google Gen AI SDKs** (`client.models.generate_videos`) and the **`gemini-api` CLI**.

---

## Prerequisites: `gemini-api` CLI Setup

Ensure the `gemini-api` CLI is installed for terminal video generation, file management (`gemini-api files`), and credential configuration:

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

# 3. Verify credentials and inspect CLI video capabilities
gemini-api whoami
gemini-api models
gemini-api video --help
gemini-api video --schema
```

> [!WARNING]
> **Platform Routing & Gemini API Deprecation Notice**:
> - In the **Gemini API**, the Veo 3.1 Preview endpoints (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, and `veo-3.1-lite-generate-preview`) reached their scheduled deprecation date (**October 22, 2026**).
> - For **terminal and coding agent video generation** on the Gemini API, `gemini-api video` defaults to **`gemini-omni-1.1-flash`** via the Interactions API (see the `gemini-omni` skill).
> - Use the **Veo `generate_videos` (`predictLongRunning`) API** documented below when targeting **GA Veo 3.1 models on Vertex AI / Gemini Enterprise Agent Platform**, **Veo 3 Stable (`veo-3.0-generate-001`, `veo-3.0-fast-generate-001`)**, or existing Veo 3.1 pipelines requiring `GenerateVideosConfig` (`last_frame`, `reference_images`, `negative_prompt`, or 20-hop `+7s` video extensions).

---

## Trigger Conditions

Activate this skill whenever the user asks to:
- Generate cinematic videos specifically using **Veo** (`veo-3.1` or `veo-3.0`) or `client.models.generate_videos` / `ai.models.generateVideos`.
- Interpolate between a starting image (`image`) and an ending constraint frame (`config.last_frame`) using Veo 3.1.
- Guide video generation with up to 3 subject, character, or product asset reference images (`config.reference_images` with `reference_type="asset"`).
- Extend a Veo-generated video in 7-second increments up to 20 times (up to 148 seconds total).
- Control video generation with `negative_prompt`, `person_generation`, or deterministic `seed` values.

---

## Model Selection & Parameter Matrix

| Capability / Constraint | Veo 3.1 Flagship | Veo 3.1 Fast | Veo 3.1 Lite | Veo 3.0 Stable / Fast |
| :--- | :--- | :--- | :--- | :--- |
| **Model ID** | `veo-3.1-generate-preview` (or GA `veo-3.1-generate-001` on Vertex AI) | `veo-3.1-fast-generate-preview` (or GA `veo-3.1-fast-generate-001`) | `veo-3.1-lite-generate-preview` | `veo-3.0-generate-001` / `veo-3.0-fast-generate-001` |
| **Audio** | Native synchronized audio (always on) | Native synchronized audio (always on) | Native synchronized audio (always on) | Native synchronized audio (always on) |
| **Aspect Ratios** | `16:9` (default), `9:16` | `16:9` (default), `9:16` | `16:9` (default), `9:16` | `16:9` (default), `9:16` |
| **Durations (`duration_seconds`)** | `4`, `6`, `8` (default `8`) | `4`, `6`, `8` (default `8`) | `4`, `6`, `8` (default `8`) | `4`, `6`, `8` (default `8`) |
| **Resolutions (`resolution`)** | `720p` (default), `1080p` (`8s` only), `4k` (`8s` only) | `720p` (default), `1080p` (`8s` only), `4k` (`8s` only) | `720p` (default), `1080p` (`8s` only) (`4k` unsupported) | `720p` (default), `1080p` (`16:9` only) |
| **First + Last Frame (`last_frame`)** | Supported (requires `8s`) | Supported (requires `8s`) | Supported (requires `8s`) | ❌ Not Supported |
| **Reference Images (`reference_images`)** | Up to 3 `asset` images (requires `8s`) | Up to 3 `asset` images (requires `8s`) | ❌ Not Supported | ❌ Not Supported |
| **Scene Extension (`video`)** | `+7s` per hop, up to 20 hops (`720p` only) | `+7s` per hop, up to 20 hops (`720p` only) | `+7s` per hop (`720p` only) | ❌ Not Supported |
| **Deterministic `seed`** | ❌ Not Supported | ❌ Not Supported | ❌ Not Supported | Supported (slightly improves determinism) |
| **Reference Guide** | [veo-3-1.md](references/veo-3-1.md) | [veo-3-1.md](references/veo-3-1.md) | [veo-3-1.md](references/veo-3-1.md) | [veo-3-1.md](references/veo-3-1.md) |

> [!IMPORTANT]
> **Strict Parameter Combination Rules (Fail-Fast Validation)**:
> 1. **`1080p` and `4k` Resolution**: Must use `duration_seconds=8` when using reference images, interpolation, or high resolution on Veo 3.1.
> 2. **Video Extension (`video` input)**: Only supports `resolution="720p"`, accepts input videos up to `141s` strictly from a prior Veo generation, and extends by `7s` (up to `148s` total across 20 hops).
> 3. **2-Day Server Retention**: Generated videos are retained on the server for **2 days (48 hours)**. Always download (`client.files.download`) and save the MP4 to disk immediately when `operation.done` becomes `True`.

---

## Deep Technical References

Consult `references/` for full multi-language SDK patterns, REST `predictLongRunning` polling scripts, and cinematic prompting guides:

- **[references/veo-3-1.md](references/veo-3-1.md)**: Complete technical specification for Veo 3.1 and Veo 3.0, including Python/TypeScript/Go/REST examples for text-to-video, image-to-video, first-and-last-frame interpolation, 3-image asset references, and 7-second scene extensions.
- **[references/README.md](references/README.md)**: Index of Veo reference documentation.

---

## Core Execution Workflows

### 1. Terminal Video Generation via `gemini-api` CLI & REST Polling

For fast terminal video generation and coding agent execution rails on the Gemini API, use `gemini-api video`:

```bash
# Generate a 1080p 16:9 video directly to disk (prints only the saved file path to stdout)
gemini-api video \
  "A cinematic wide shot of a snow leopard stalking across a rocky Himalayan ridge at dusk, howling wind and crunching snow" \
  --resolution "1080p" \
  --aspect-ratio "16:9" \
  --out "./assets/snow_leopard.mp4"

# Animate a starting frame generated with gemini-api image (Nano Banana -> Video pipeline)
START_IMG=$(gemini-api image "An origami paper boat resting on a mossy forest stream, macro photography" --aspect-ratio "16:9" --out "./assets/boat_frame.png")
gemini-api video \
  "<FIRST_FRAME> The paper boat drifts gently downstream through dappled sunlight, babbling brook water sounds. Use this image as the starting frame." \
  -i "$START_IMG" \
  --resolution "1080p" \
  --out "./assets/origami_boat.mp4"
```

When calling Veo's dedicated `:predictLongRunning` endpoint directly from the shell (e.g., for `negativePrompt`, `referenceImages`, or Veo 3.0/3.1 operations), poll the long-running operation until `.done == true` and download the resulting MP4 URI:

```bash
BASE_URL="https://generativelanguage.googleapis.com/v1beta"

OP_NAME=$(curl -sf "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "instances": [{
      "prompt": "A close-up shot of a vintage brass espresso machine pulling a rich crema shot in a sunlit Italian cafe, hissing steam and clinking porcelain cups."
    }],
    "parameters": {
      "aspectRatio": "16:9",
      "resolution": "1080p",
      "durationSeconds": 8,
      "negativePrompt": "cartoon, drawing, low quality, blurry"
    }
  }' | jq -r '.name')

while true; do
  STATUS_JSON=$(curl -sf -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${OP_NAME}")
  if [ "$(echo "$STATUS_JSON" | jq -r '.done')" = "true" ]; then
    VIDEO_URI=$(echo "$STATUS_JSON" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    curl -sfL -H "x-goog-api-key: $GEMINI_API_KEY" -o "./assets/espresso.mp4" "$VIDEO_URI"
    echo "./assets/espresso.mp4"
    break
  fi
  sleep 10
done
```

---

### 2. SDK Integration Patterns (`client.models.generate_videos`)

#### Text-to-Video with Native Dialogue & Negative Prompt (Python)
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

prompt = (
    "A medium two-shot inside an antique clockmaker's workshop. "
    "An elderly clockmaker holds a brass magnifying loupe and whispers, "
    "\"Every gear remembers the century it was forged.\" "
    "Soft ticking of dozens of wall clocks and a warm chime in the background."
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="1080p",
        duration_seconds=8,
        negative_prompt="modern electronics, neon lights, blurry, watermark",
    ),
)

while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("clockmaker.mp4")
```

#### First-and-Last-Frame Interpolation (`image` + `config.last_frame`)
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

first_image = types.Image.from_file(location="first_frame.png")
last_image = types.Image.from_file(location="last_frame.png")

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A smooth camera dolly-in as the wooden treasure chest slowly creaks open, revealing a warm golden glow inside.",
    image=first_image,
    config=types.GenerateVideosConfig(
        last_frame=last_image,
        duration_seconds=8,
        aspect_ratio="16:9",
    ),
)

while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("chest_interpolation.mp4")
```

#### Reference-Guided Asset Direction (Up to 3 Reference Images)
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

character_ref = types.VideoGenerationReferenceImage(
    image=types.Image.from_file(location="hero_character.png"),
    reference_type="asset",
)
vehicle_ref = types.VideoGenerationReferenceImage(
    image=types.Image.from_file(location="hoverbike.png"),
    reference_type="asset",
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Medium tracking shot of the hero riding the hoverbike across a salt flat at golden hour, turbine engine hum and rushing wind.",
    config=types.GenerateVideosConfig(
        reference_images=[character_ref, vehicle_ref],
        duration_seconds=8,
        aspect_ratio="16:9",
    ),
)

while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("hoverbike_scene.mp4")
```

#### Scene Extension (`+7s` per hop at `720p`)
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

# Pass `video.video` from a completed Veo generation operation
extension_op = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=video.video,
    prompt="The hoverbike banks sharply around a sandstone spire and accelerates into a canyon.",
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        resolution="720p",
    ),
)

while not extension_op.done:
    time.sleep(10)
    extension_op = client.operations.get(extension_op)

extended_video = extension_op.response.generated_videos[0]
client.files.download(file=extended_video.video)
extended_video.video.save("hoverbike_extended.mp4")
```

---

## Cinematic Prompting Formula

Structure Veo prompts across five core cinematic dimensions:
1. **Subject**: Specific character, wardrobe, creature, or object appearance (`a weathered deep-sea diver in a brass helmet`).
2. **Action**: Physics-grounded movement and interaction (`slowly wiping condensation from a submarine porthole`).
3. **Style & Ambiance**: Film stock, lighting, and color palette (`35mm anamorphic film, chiaroscuro bioluminescent lighting, teal and amber palette`).
4. **Camera Positioning & Motion**: Explicit shot framing and rig motion (`dolly zoom`, `low-angle tracking shot`, `overhead crane shot`, `shallow depth of field with rack focus`).
5. **Audio Direction**:
   - **Dialogue**: Wrap spoken lines in double quotes (`She says, "We found the trench."`).
   - **Sound Effects (SFX)**: Explicitly name foley cues (`creaking hull metal`, `sonar ping every two seconds`).
   - **Ambient Noise**: Describe the acoustic environment (`muffled deep-ocean rumble`).
   - **Negative Prompts**: Pass unwanted visual traits via `negative_prompt` (`"cartoon, drawing, low quality, distorted hands"`) rather than instructive `"no ..."` phrases in the positive prompt.
