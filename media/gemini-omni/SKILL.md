---
name: gemini-omni
description: >
  Generate, animate, edit, interpolate, extend, and upscale video clips (3 to
  15 seconds, 360p to 4K at 24 FPS) with native synchronized audio using Gemini
  Omni 1.2 Flash (gemini-omni-1.2-flash) via uv run scripts/omni.py and the
  Google Gen AI Interactions API across Gemini Enterprise / Vertex AI (global)
  and Gemini API. Activate when creating videos from text or images, editing or
  extending clips, or upscaling video resolution.
license: Apache-2.0
metadata:
  category: media
  tags: "video, animation, upscale, generative, media"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# Gemini Omni 1.2 Flash video generation and editing (`gemini-omni`)

Generate, edit, interpolate, extend, and upscale video (`360p` to `4k` MP4 at `24 FPS`) with native synchronized audio (speech, dialogue, music, and sound effects) using **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`) via `uv run scripts/omni.py` and the **Google Gen AI Interactions API** (`client.interactions.create`).

> [!CAUTION]
> **Strict fail-fast authentication policy**:
> - Run `uv run scripts/omni.py` using Gemini Enterprise / Vertex AI Application Default Credentials (`gcloud auth application-default login --billing-project YOUR_PROJECT_ID`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION="global"`, `GOOGLE_GENAI_USE_ENTERPRISE="true"`) or a Gemini Developer API key (`GEMINI_API_KEY`).
> - If authentication fails in `scripts/omni.py`, stop immediately, report the exact authentication error message to the user, and ask them to configure their credentials (`gcloud auth application-default login --billing-project YOUR_PROJECT_ID` + `export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"` or `export GEMINI_API_KEY="your-api-key"`).
> - Never generate placeholder `.mp4` files, never silently swap providers or models, and never inspect local credential stores outside standard environment variables and ADC.

---

## Available scripts

- **[scripts/omni.py](scripts/omni.py)**: PEP 723 standalone Python CLI (`uv run scripts/omni.py`) for **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`, with aliases `omni-1.2-flash`, `omni-1.2`, `1.2`, `flash-1.2`). Supports text-to-video, image-to-video, first-and-last-frame interpolation, multi-reference video generation, conversational video editing (`--previous-interaction-id` or `-i video.mp4`), video extension (`--task extend`), standalone video upscaling (`--task upscale`), seeds (`--seed`), Cloud Storage output (`--gcs-uri`), URI delivery polling (`--delivery uri`), optional 44.1 kHz stereo WAV audio extraction (`--extract-audio`), and both Gemini Enterprise / Vertex AI ADC (`--enterprise`, `--vertexai`) and Gemini API Key (`GEMINI_API_KEY`).
- **[scripts/test_omni.py](scripts/test_omni.py)**: Automated unit and CLI test suite verifying `gemini-omni-1.2-flash` resolution, duration rules, `upscale` and `extend` constraints, MIME detection (`video/quicktime` for `.mov`, unsupported format rejection), reference limits, deprecated control tag detection, and fail-fast credential checks.

---

## Prerequisites: `uv` (`scripts/omni.py`) setup

`scripts/omni.py` declares inline PEP 723 metadata (`requires-python = ">=3.12"`, `dependencies = ["google-genai>=3.3.0", "google-auth>=2.0.0"]`) so `uv run` resolves dependencies automatically in an isolated environment.

```bash
# 1a. Authenticate with Gemini Enterprise / Vertex AI (Application Default Credentials)
gcloud auth application-default login --billing-project YOUR_PROJECT_ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_ENTERPRISE="true"

# 1b. Or authenticate with the Gemini Developer API
export GEMINI_API_KEY="your-api-key"

# 2. Verify CLI flags and run the offline test suite
uv run scripts/omni.py --help
uv run scripts/test_omni.py
```

---

## Trigger conditions

Activate this skill when the user asks to:
- Generate `3s` to `15s` video clips with synchronized dialogue, music, and sound effects from text prompts (`gemini-omni-1.2-flash`).
- Animate a starting image or interpolate smoothly between a starting frame and an ending frame (`3s` to `10s`), including smooth looping scenes.
- Generate videos guided by up to 6 to 10 character, object, or style reference images and up to 3 short reference video clips (around 3 seconds each).
- Edit an existing video conversationally across multiple turns (`--previous-interaction-id` or `-i source.mp4`) while preserving unmentioned visual and audio elements.
- Extend a video clip in `3s` to `10s` increments (using up to the final `10s` as reference footage, up to `30s` total in the Gemini API or `40s` on Gemini Enterprise / Vertex AI).
- Upscale an existing `360p` video to `720p` or `1080p`, or a `720p` video to `1080p` or `4k` (`--task upscale`).

---

## Model specifications (`gemini-omni-1.2-flash`)

| Feature / parameter | Gemini Omni 1.2 Flash |
| :--- | :--- |
| **Canonical model ID** | `gemini-omni-1.2-flash` (GA November 5, 2026) |
| **CLI short aliases** | `omni-1.2-flash`, `omni-1.2`, `1.2`, `flash-1.2` |
| **API surface** | Interactions API (`client.interactions.create`; `GenerateContent` not supported) |
| **Vertex AI / Enterprise region** | `global` |
| **Input / output token limits** | `131,072` input / `65,536` output (`260,640` on Enterprise) |
| **Supported input formats** | Images: `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.heif`; Video: `.mp4`, `.mov` (`video/quicktime`), `.webm`, `.mpeg`, `.mpg`, `.wmv`, `.3gp`, `.flv` |
| **Video duration (`duration`)** | `3s` to `15s` (default `10s`, whole seconds); `3s` to `10s` for 2-frame interpolation |
| **Video extension (`extend`)** | `3s` to `10s` per turn (`10s` reference window; up to `30s` Gemini API / `40s` Enterprise) |
| **Standalone video upscaling** | Supported (`task: "upscale"`; `360p -> 720p/1080p`, `720p -> 1080p/4k`, zero input tokens) |
| **Reference images** | Up to `6` in Gemini API / `10` on Enterprise (up to 3 per character for 2 characters) across `3s` to `15s` |
| **Reference videos** | Up to `3` (around `3s` each) for `3s` to `10s` clips; `1` (around `3s`) for `11s` to `15s` clips |
| **Resolutions and aspect ratios** | `360p`, `720p` (default), `1080p`, `4k` at `24 FPS`; `16:9` (default), `9:16` |
| **Lifecycle** | Active GA model (retirement November 5, 2027 or later); `1.1` and preview models are deprecated or shut down |
| **Watermarking** | Invisible **SynthID** watermark embedded in video frames and audio |
| **Reference guide** | [gemini-omni-1-2-flash.md](references/gemini-omni-1-2-flash.md) |

> [!IMPORTANT]
> **Key rules for Gemini Omni 1.2 Flash**:
> 1. **Use natural language instead of control tags**: Do not include deprecated control tags (`<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_0>`, `<VIDEO_REF_0>`) in prompts for `gemini-omni-1.2-flash`. Describe how each image or video works in plain natural language (`"Use the first image as the starting frame and the second image as the ending frame"`).
> 2. **Optional task fallback (`--task`)**: `gemini-omni-1.2-flash` infers the task from natural language. Pass `--task` (`text_to_video`, `image_to_video`, `reference_to_video`, `edit`, `extend`, or `upscale`) when forcing a mode. `--task upscale` is always required when upscaling.
> 3. **Never use deprecated or shut-down models**: `gemini-omni-1.1-flash`, `gemini-omni-1.1-flash-preview`, and `gemini-omni-flash-preview` are deprecated or shut down; `scripts/omni.py` rejects them immediately and requires `gemini-omni-1.2-flash`.

---

## Deep technical references

Consult the `references/` directory for API schemas, task configurations, and SDK examples:

- **[references/gemini-omni-1-2-flash.md](references/gemini-omni-1-2-flash.md)**: Full specification for **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`), covering `3s` to `15s` video generation, natural-language reference binding, standalone video upscaling (`task: "upscale"`), conversational editing, extension, Gemini Enterprise (`global`) / Gemini API workflows, and Python SDK patterns.
- **[references/README.md](references/README.md)**: Index and quick reference for Gemini Omni workflows.

---

## Core execution workflows (`uv run scripts/omni.py`)

All examples below work with either `GEMINI_API_KEY` set in the environment or Gemini Enterprise / Vertex AI ADC (`--enterprise --project "$GOOGLE_CLOUD_PROJECT"`, with `--vertexai` accepted as an alias).

### 1. Text-to-video (`3s` to `15s` with native synchronized audio)

```bash
# Generate a 15-second 1080p video with synchronized dialogue, music, and sound effects
uv run scripts/omni.py \
  --enterprise \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --model "gemini-omni-1.2-flash" \
  --resolution "1080p" \
  --aspect-ratio "16:9" \
  --duration "15s" \
  --seed 42 \
  --prompt '[0-5s] Wide establishing shot of a sunlit woodworking workshop with sawdust floating in warm lightbeams and soft acoustic guitar music. [5-10s] Medium shot of a craftsman planing a maple board with crisp wood-shaving sound effects. [10-15s] He looks up and says warmly: "Every piece tells a story."' \
  --output "./output/workshop_15s.mp4"
```

### 2. Image-to-video and first-and-last-frame interpolation (`3s` to `10s`)

Describe image roles in natural language instead of deprecated angle-bracket tags:

```bash
# 1. Animate a single starting frame (3s to 15s)
uv run scripts/omni.py \
  --input "./frames/portrait_start.png" \
  --resolution "1080p" \
  --duration "8s" \
  --prompt "Use this image as the starting frame. The camera pushes in slowly as evening mist drifts across the harbor, accompanied by gentle cello music." \
  --output "./output/harbor_intro.mp4"

# 2. Interpolate between a starting frame and an ending frame (3s to 10s max)
uv run scripts/omni.py \
  --input "./frames/forest_sunrise.jpg" \
  --input "./frames/forest_winter.jpg" \
  --task "image_to_video" \
  --resolution "1080p" \
  --duration "10s" \
  --prompt "Use the first image as the starting frame and the second image as the ending frame. Transition smoothly from the green forest at sunrise to the snow-covered forest under a starry night sky with gentle wind chimes." \
  --output "./output/season_transition.mp4"
```

### 3. Subject and style reference video generation (`reference_to_video`)

Pass up to 6 reference images (up to 10 on Gemini Enterprise / Vertex AI; up to 3 images per subject for 2 subjects) and up to 3 short reference videos (around 3 seconds each for `3s` to `10s` clips, or 1 reference video for `11s` to `15s` clips):

```bash
uv run scripts/omni.py \
  --input "./refs/ink_painting_style.png" \
  --input "./refs/traveler_front.png" \
  --input "./refs/traveler_side.png" \
  --task "reference_to_video" \
  --resolution "1080p" \
  --duration "12s" \
  --prompt "Use the first image as the ink-wash painting style reference, and use the second and third images as character references for the traveler. Do not use the images as literal starting frames. The traveler walks across a misty wooden mountain bridge at dawn with bamboo flute music and rushing river sounds." \
  --output "./output/bridge_scene.mp4"
```

### 4. Multi-turn conversational editing and video extension (`edit` and `extend`)

Store the initial interaction (`--store`) so you can pass its `Interaction ID` to `--previous-interaction-id` on follow-up turns, or pass an existing video (`.mp4`, `.mov`, `.webm`, and related supported containers) directly via `--input`:

```bash
# Turn 1: Generate initial 10s video and store interaction state
uv run scripts/omni.py \
  --store \
  --resolution "720p" \
  --duration "10s" \
  --prompt "A violinist performing outdoors in an autumn park, expressive solo violin melody." \
  --output "./output/violin_v1.mp4"

# Turn 2: Edit the video conversationally while locking unmentioned details
uv run scripts/omni.py \
  --store \
  --previous-interaction-id "$TURN1_ID" \
  --task "edit" \
  --duration "10s" \
  --prompt "Change the autumn trees to blooming cherry blossoms in spring. Keep everything else the same." \
  --output "./output/violin_spring.mp4"

# Turn 3: Extend the video by 10 seconds (3s to 10s per extension turn)
uv run scripts/omni.py \
  --previous-interaction-id "$TURN2_ID" \
  --task "extend" \
  --duration "10s" \
  --prompt "Extend this video: the camera pans up to reveal a stone pavilion as the violin melody builds into a warm orchestral finale." \
  --output "./output/violin_extended.mp4"
```

### 5. Standalone video upscaling (`--task upscale`)

`gemini-omni-1.2-flash` upscales `360p` clips to `720p` or `1080p`, and `720p` clips to `1080p` or `4k` (up to `15s` at `24 FPS`) with zero text input token cost (`total_input_tokens: 0`):

```bash
# Iterate quickly at 360p or 720p, then upscale the approved clip to 1080p or 4K
uv run scripts/omni.py \
  --input "./output/violin_spring.mp4" \
  --task "upscale" \
  --resolution "4k" \
  --delivery "uri" \
  --output "./output/violin_spring_4k.mp4"
```

### 6. Offline validation (`--dry-run`)

Validate model aliases, durations, media formats, and inspect the Interactions API JSON payload offline without network calls:

```bash
uv run scripts/omni.py \
  --model "gemini-omni-1.2-flash" \
  --resolution "1080p" \
  --duration "15s" \
  --seed 7 \
  --prompt "A vintage train crossing a stone viaduct above coastal cliffs as seabirds call." \
  --output "viaduct.mp4" \
  --dry-run
```

---

## Pre-processing and audio handling (`ffmpeg`)

1. **Preserve vs. regenerate video audio (`ffmpeg -an`)**:
   - By default, Gemini Omni 1.2 Flash preserves the original audio of an input video during edits unless you explicitly prompt for audio changes.
   - To force the model to generate a new audio track from scratch matching your visual edits, strip the audio stream before passing `--input`:
     ```bash
     ffmpeg -y -i source.mp4 -c:v copy -an source_silent.mp4
     uv run scripts/omni.py \
       --input "source_silent.mp4" \
       --task "edit" \
       --prompt "Transform the daytime street into a rainy neon night with reflections, heavy rain sound effects, distant thunder, and synth ambient music. Keep everything else the same." \
       --output "neon_rain_edit.mp4"
     ```
2. **Extract synchronized stereo WAV audio (`--extract-audio`)**:
   - Pass `--extract-audio ./output/audio/soundtrack.wav` to extract the generated video's audio stream via `ffmpeg` as a 44.1 kHz 16-bit stereo PCM WAV (`pcm_s16le`) track for downstream editing or playback.

---

## Prompting best practices

1. **Describe media roles in plain language**: State which input image is the starting frame, ending frame, character reference, or style reference (`"Use the first image as the starting frame"`), and avoid deprecated `<FIRST_FRAME>` or `<IMAGE_REF_0>` tags.
2. **Direct synchronized audio explicitly**: Specify background music genre, ambient soundscapes, and exact quoted dialogue (`"She says in a calm voice: 'All relays are online.'"` or `"No dialogue, only ambient wind and footsteps"`).
3. **Use timestamps for multi-shot sequences**: Structure `10s` to `15s` clips with bracketed timestamps (`[0-5s] Wide establishing shot... [5-10s] Cut to medium close-up... [10-15s] Slow pull-back...`).
4. **Keep video edits surgical**: When editing an existing video, end your prompt with `"Keep everything else the same"` to lock background geometry, lighting, and unmentioned subjects.
