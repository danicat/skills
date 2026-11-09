---
name: gemini-omni
description: >
  Conversational video generation, multimodal video editing, first-and-last-frame
  interpolation, video extension, and standalone video upscaling with native
  synchronized audio using Gemini Omni 1.2 Flash (gemini-omni-1.2-flash) and
  Gemini Omni 1.1 Flash (gemini-omni-1.1-flash) via uv run scripts/omni.py and
  the Google Gen AI SDKs (Interactions API). Supports Vertex AI / Gemini
  Enterprise (Application Default Credentials), 3s to 15s video clips at 360p
  to 4K (24 FPS), up to 6-10 reference images and 3 reference videos, and 2D
  game cutscene integration. Activate when generating game cutscenes, title
  animations, promotional videos, or editing and extending video clips.
license: Apache-2.0
metadata:
  category: media
  tags: "video-generation, video-editing, video-upscaling, multimodal, generative-ai, interactions-api, vertex-ai, game-dev"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Gemini Omni 1.2 Flash Video Generation & Editing Skill (`gemini-omni`)

Generate, edit, interpolate, extend, and upscale high-coherence video (`360p` to `4k` MP4 at `24 FPS`) with native synchronized audio (speech, dialogue, music, and sound effects) using **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`) via **`uv run scripts/omni.py`** and the **Google Gen AI Interactions API** (`client.interactions.create`).

> [!CAUTION]
> **Strict Fail-Fast Authentication Policy (Never Go Rogue)**:
> **Never go rogue if `scripts/omni.py` fails.**
> - Run `uv run scripts/omni.py` (or `uv run skills/gemini-omni/scripts/omni.py`) using Vertex AI / Gemini Enterprise Application Default Credentials (`gcloud auth application-default login --billing-project YOUR_PROJECT_ID`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION="global"`).
> - If authentication fails in `scripts/omni.py`, **stop immediately**, report the exact authentication error message to the user, and ask them to configure their credentials (`gcloud auth application-default login --billing-project YOUR_PROJECT_ID` and `export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"`).
> - Never attempt unauthorized workarounds, never generate empty or mock `.mp4` files, and never probe local credential stores outside standard environment variables and ADC.

---

## Available Scripts

- **[scripts/omni.py](scripts/omni.py)**: PEP 723 standalone Python CLI (`uv run scripts/omni.py`) centered on **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`, with short aliases `omni-1.2-flash`, `omni-1.2`, `1.2`, `flash-1.2`) and transitional `gemini-omni-1.1-flash` (`1.1`). Supports text-to-video, image-to-video, first-and-last-frame interpolation, multi-reference video generation, conversational video editing (`--previous-interaction-id` or `-i video.mp4`), video extension (`--task extend`), standalone video upscaling (`--task upscale`), reproducible seeds (`--seed`), Cloud Storage output (`--gcs-uri`), URI delivery polling (`--delivery uri`), optional `44.1 kHz` stereo WAV audio extraction (`--extract-audio`), and Vertex AI / Gemini Enterprise ADC authentication.
- **[scripts/test_omni.py](scripts/test_omni.py)**: Automated unit and CLI test suite verifying `gemini-omni-1.2-flash` model resolution, `3s` to `15s` duration rules, `upscale` and `extend` task constraints, reference video limits, deprecated control tag warnings, and fail-fast Vertex AI ADC initialization.

---

## Prerequisites: Vertex AI / Gemini Enterprise Setup (`uv` + `scripts/omni.py`)

`scripts/omni.py` declares inline PEP 723 metadata (`requires-python = ">=3.10"`, `dependencies = ["google-genai>=1.68.0", "google-auth>=2.0.0"]`) so `uv run` resolves dependencies automatically in an isolated environment.

```bash
# 1. Authenticate with Vertex AI / Gemini Enterprise (Application Default Credentials)
gcloud auth application-default login --billing-project YOUR_PROJECT_ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI="true"

# 2. Verify CLI flags and run the unit test suite
uv run scripts/omni.py --help
uv run scripts/test_omni.py
```

---

## Trigger Conditions

Activate this skill whenever the user asks to:
- Generate `3s` to `15s` video clips with synchronized dialogue, music, and sound effects from text prompts (`gemini-omni-1.2-flash`).
- Animate a starting image or interpolate smoothly between a starting frame and an ending frame (`3s` to `10s`), including seamless looping scenes.
- Generate videos guided by up to 6 to 10 character, object, or style reference images and up to 3 reference video clips (~3s each).
- Edit an existing video conversationally across multiple turns (`--previous-interaction-id` or `-i source.mp4`) while preserving unmentioned visual and audio elements.
- Extend a video clip in `3s` to `10s` increments (using up to the final `10s` as context, up to `30s` total in the Gemini API or `40s` on Vertex AI / Gemini Enterprise).
- Upscale an existing `360p` video to `720p` or `1080p`, or a `720p` video to `1080p` or `4k` (`--task upscale`).

---

## Companion Skills & Game Dev Studio Integration

In `agy-game-studio`, `gemini-omni` serves as the cutscene, animated intro, boss reveal, and trailer generation engine alongside the companion game development skills:

- **`vibe-game-developer` & `game-design` (`GDD.md`)**:
  - During game co-creation, `game-design` defines cutscene storyboards, boss intro sequences, and visual art direction in `GDD.md`, while `vibe-game-developer` routes video cutscene tasks to `gemini-omni`.
- **`nano-banana` + `sprite-design` -> `gemini-omni` (Consistent Character Cutscenes)**:
  - Pass character turnaround sheets or keyframe illustrations generated by `nano-banana` into `uv run scripts/omni.py -i character_sheet.png` so game cutscenes use the exact same character designs and environment palette as in-game sprites.
- **`ebitengineer` Audio Extraction (`--extract-audio`)**:
  - `gemini-omni-1.2-flash` generates MP4 videos with native synchronized audio (spoken dialogue, ambient music, and sound effects).
  - Pass `--extract-audio ./assets/audio/cutscene.wav` to extract the video's audio track as a `44,100 Hz` 16-bit stereo PCM `.wav` file ready for Ebitengine's shared `44.1 kHz` `audio.Context`.

---

## Model Specifications (`gemini-omni-1.2-flash` vs. `gemini-omni-1.1-flash`)

| Feature / Parameter | Gemini Omni 1.2 Flash (Default) | Gemini Omni 1.1 Flash (Transition) |
| :--- | :--- | :--- |
| **Canonical Model ID** | `gemini-omni-1.2-flash` (GA November 5, 2026) | `gemini-omni-1.1-flash`, `gemini-omni-1.1-flash-preview` |
| **CLI Short Aliases** | `omni-1.2-flash`, `omni-1.2`, `1.2`, `flash-1.2` | `omni-1.1-flash`, `omni-1.1`, `1.1`, `flash-1.1` |
| **API Surface** | Interactions API (`client.interactions.create`; `GenerateContent` not supported) | Interactions API (`client.interactions.create`) |
| **Supported Region (Vertex AI)** | `global` | `global` |
| **Input / Output Token Limits** | `131,072` input tokens / `65,536` output tokens (`260,640` on Enterprise) | `131,072` input tokens / `65,536` output tokens (`173,760` on Enterprise) |
| **Modalities** | Text (In/Out), Image (In), Video with synchronized speech, music, and SFX (In/Out) | Text (In/Out), Image (In), Video with synchronized audio (In/Out) |
| **Video Duration (`duration`)** | `3s` to `15s` (default `10s`, whole seconds); `3s` to `10s` for 2-frame interpolation | `3s` to `10s` (default `10s`, whole seconds) |
| **Video Extension (`extend`)** | `3s` to `10s` per turn (10s lookback window; up to `30s` Gemini API / `40s` Enterprise) | `3s` to `10s` per turn (up to `30s` Gemini API / `40s` Enterprise) |
| **Standalone Video Upscaling** | Supported (`task: "upscale"`; `360p -> 720p/1080p`, `720p -> 1080p/4k`, zero input tokens) | Not supported |
| **Reference Images** | Up to `6` in Gemini API / `10` on Enterprise (up to 3 per character for 2 characters) across `3s` to `15s` | Up to `6` in Gemini API / `10` on Enterprise (`3s` to `10s`) |
| **Reference Videos** | Up to `3` (~3s each) for `3s` to `10s` clips; `1` (~3s) for `11s` to `15s` clips | Up to `3` (~3s each) for `3s` to `10s` clips |
| **Resolutions & Aspect Ratios** | `360p`, `720p` (default), `1080p`, `4k` at `24 FPS`; `16:9` (default), `9:16` | `360p`, `720p` (default), `1080p`, `4k` at `24 FPS`; `16:9` (default), `9:16` |
| **Lifecycle & Auto-Routing** | Active GA model (retirement November 5, 2027 or later) | Routes automatically to `gemini-omni-1.2-flash` starting December 3, 2026 |
| **Watermarking** | Invisible **SynthID** watermark embedded in video frames and audio | Invisible **SynthID** watermark embedded in video frames and audio |
| **Reference Guides** | [gemini-omni-1-2-flash.md](references/gemini-omni-1-2-flash.md) | [gemini-omni-1-1-flash.md](references/gemini-omni-1-1-flash.md) |

> [!IMPORTANT]
> **Key Rules for Gemini Omni 1.2 Flash**:
> 1. **Use Natural Language Instead of Control Tags**: Do not include deprecated control tags (`<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_0>`, `<VIDEO_REF_0>`) in prompts for `gemini-omni-1.2-flash`. Describe how each image or video should be used in natural language (`"Use the first image as the starting frame and the second image as the ending frame"`).
> 2. **Optional Task Fallback (`--task`)**: `gemini-omni-1.2-flash` automatically infers the task from natural language. If a prompt does not trigger the expected mode, pass `--task` (`text_to_video`, `image_to_video`, `reference_to_video`, `edit`, `extend`, or `upscale`). Note that `--task upscale` is always required when upscaling.
> 3. **Never Use Shut-Down `gemini-omni-flash-preview`**: `gemini-omni-flash-preview` was shut down on October 22, 2026; `scripts/omni.py` rejects it immediately with a fail-fast validation error.

---

## Deep Technical References

Consult the `references/` directory for complete API schemas, task configurations, and SDK examples:

- **[references/gemini-omni-1-2-flash.md](references/gemini-omni-1-2-flash.md)**: Complete reference for **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`), covering `3s` to `15s` video generation, natural-language multi-reference prompting, standalone video upscaling (`task: "upscale"`), conversational editing, extension, Vertex AI / Gemini Enterprise (`global` endpoint) workflows, and Python SDK patterns.
- **[references/gemini-omni-1-1-flash.md](references/gemini-omni-1-1-flash.md)**: Reference for `gemini-omni-1.1-flash` and migration guidance to `gemini-omni-1.2-flash` ahead of the December 3, 2026 automatic routing cutover.
- **[references/README.md](references/README.md)**: Index and quick reference for all Gemini Omni workflows.

---

## Core Execution Workflows (`uv run scripts/omni.py`)

### 1. Text-to-Video (3s to 15s with Native Synchronized Audio)

```bash
# Generate a 15-second 1080p video with synchronized dialogue, music, and sound effects
uv run scripts/omni.py \
  --vertexai \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --model "gemini-omni-1.2-flash" \
  --resolution "1080p" \
  --aspect-ratio "16:9" \
  --duration "15s" \
  --seed 42 \
  --prompt '[0-5s] Wide establishing shot of a sunlit woodworking workshop with sawdust floating in warm lightbeams and soft acoustic guitar music. [5-10s] Medium shot of a craftsman planing a maple board with crisp wood-shaving sound effects. [10-15s] He looks up and says warmly: "Every piece tells a story."' \
  --output "./assets/video/workshop_15s.mp4"
```

### 2. Image-to-Video & First-and-Last-Frame Interpolation (3s to 10s)

Describe image roles in natural language instead of using deprecated angle-bracket tags:

```bash
# 1. Animate a single starting frame (3s to 15s)
uv run scripts/omni.py \
  --vertexai \
  --input "./assets/sprites/knight_idle.png" \
  --resolution "1080p" \
  --duration "8s" \
  --prompt "Use this image as the starting frame. The camera slowly pushes in as the knight raises the glowing sword and wind whips across the cloak, accompanied by a low orchestral brass swell." \
  --output "./assets/video/knight_intro.mp4"

# 2. Interpolate between a starting frame and an ending frame (3s to 10s max)
uv run scripts/omni.py \
  --vertexai \
  --input "./assets/scenes/forest_sunrise.jpg" \
  --input "./assets/scenes/forest_winter.jpg" \
  --task "image_to_video" \
  --resolution "1080p" \
  --duration "10s" \
  --prompt "Use the first image as the starting frame and the second image as the ending frame. Transition smoothly from the lush green forest at sunrise to the snow-covered forest under a starry night sky with gentle wind chimes." \
  --output "./assets/video/season_transition.mp4"
```

### 3. Subject & Style Reference Video Generation (`reference_to_video`)

Pass up to 6 reference images (up to 10 on Vertex AI / Gemini Enterprise; up to 3 images per character for 2 characters) and up to 3 short reference videos (~3s each for `3s` to `10s` clips, or 1 reference video for `11s` to `15s` clips):

```bash
uv run scripts/omni.py \
  --vertexai \
  --input "./assets/art/ink_painting_style.png" \
  --input "./assets/characters/hero_front.png" \
  --input "./assets/characters/hero_side.png" \
  --task "reference_to_video" \
  --resolution "1080p" \
  --duration "12s" \
  --prompt "Use the first image as the ink-wash painting style reference, and use the second and third images as character references for our hero. Do not use the images as literal starting frames. The hero walks across a misty wooden mountain bridge at dawn with bamboo flute music and rushing river sounds." \
  --output "./assets/video/bridge_cutscene.mp4"
```

### 4. Multi-Turn Conversational Editing & Video Extension (`edit` & `extend`)

Store the initial interaction (`--store`) so you can pass its `Interaction ID` to `--previous-interaction-id` on follow-up turns, or pass an existing `.mp4` file directly via `--input`:

```bash
# Turn 1: Generate initial 10s video and store interaction state
uv run scripts/omni.py \
  --vertexai \
  --store \
  --resolution "720p" \
  --duration "10s" \
  --prompt "A violinist performing outdoors in an autumn park, expressive solo violin melody." \
  --output "./assets/video/violin_v1.mp4"

# Turn 2: Edit the video conversationally while locking unmentioned details
uv run scripts/omni.py \
  --vertexai \
  --store \
  --previous-interaction-id "$TURN1_ID" \
  --task "edit" \
  --duration "10s" \
  --prompt "Change the autumn trees to blooming cherry blossoms in spring. Keep everything else the same." \
  --output "./assets/video/violin_spring.mp4"

# Turn 3: Extend the video by 10 seconds (3s to 10s per extension turn)
uv run scripts/omni.py \
  --vertexai \
  --previous-interaction-id "$TURN2_ID" \
  --task "extend" \
  --duration "10s" \
  --prompt "Extend this video: the camera pans up to reveal a stone pavilion as the violin melody builds into a warm orchestral finale." \
  --output "./assets/video/violin_extended.mp4"
```

### 5. Standalone Video Upscaling (`--task upscale`)

`gemini-omni-1.2-flash` supports standalone video upscaling (`360p -> 720p` or `1080p`; `720p -> 1080p` or `4k`) for clips up to `15s` at `24 FPS` with zero text input token cost (`total_input_tokens: 0`):

```bash
# Iterate quickly at 360p or 720p, then upscale the approved clip to 1080p or 4K
uv run scripts/omni.py \
  --vertexai \
  --input "./assets/video/violin_spring.mp4" \
  --task "upscale" \
  --resolution "4k" \
  --delivery "uri" \
  --output "./assets/video/violin_spring_4k.mp4"
```

### 6. Offline Validation (`--dry-run`)

Validate model aliases, durations, media counts, and inspect the exact Interactions API JSON payload without making network calls:

```bash
uv run scripts/omni.py \
  --model "gemini-omni-1.2-flash" \
  --resolution "1080p" \
  --duration "15s" \
  --seed 7 \
  --prompt "Pixel-art starship launching from an orbital dock with retro thruster roar." \
  --output "launch.mp4" \
  --dry-run
```

---

## Pre-Processing & Audio Handling (`ffmpeg`)

1. **Preserve vs. Regenerate Video Audio (`ffmpeg -an`)**:
   - By default, Gemini Omni 1.2 Flash preserves the original audio of an input video during edits unless you explicitly prompt for audio changes.
   - To force the model to synthesize a brand-new audio track from scratch matching your visual edits, strip the audio stream before passing `--input`:
     ```bash
     ffmpeg -y -i source.mp4 -c:v copy -an source_silent.mp4
     uv run scripts/omni.py \
       --vertexai \
       --input "source_silent.mp4" \
       --task "edit" \
       --prompt "Transform the daytime street into a rainy cyberpunk night with neon reflections, heavy rain sound effects, distant thunder, and synth ambient music. Keep everything else the same." \
       --output "cyberpunk_edit.mp4"
     ```
2. **Extract Synchronized Cutscene Audio for Ebitengine (`--extract-audio`)**:
   - When using a generated video cutscene in an Ebitengine 2D game, pass `--extract-audio ./assets/audio/cutscene.wav` to extract a `44,100 Hz` 16-bit stereo PCM `.wav` file aligned to Ebitengine's 4-byte stereo sample frames.

---

## Prompting Best Practices
1. **Describe Media Roles in Natural Language**: Clearly state which input image is the starting frame, ending frame, character reference, or style reference (`"Use the first image as the starting frame"`), and avoid deprecated `<FIRST_FRAME>` or `<IMAGE_REF_0>` tags.
2. **Direct Synchronized Audio Explicitly**: Specify background music genre, ambient soundscapes, and exact quoted dialogue (`"She says in a calm voice: 'All relays are online.'"` or `"No dialogue, only ambient wind and footsteps"`).
3. **Use Timecodes for Multi-Shot Sequences**: Structure `10s` to `15s` clips with bracketed timestamps (`[0-5s] Wide establishing shot... [5-10s] Cut to medium close-up... [10-15s] Slow pull-back...`).
4. **Surgical Video Edits**: When editing an existing video, end your prompt with `"Keep everything else the same"` to lock background geometry, lighting, and unmentioned subjects.
