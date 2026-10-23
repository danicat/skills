---
name: gemini-omni
description: >
  Conversational video generation, multimodal video editing, first-and-last-frame
  interpolation, multi-reference video synthesis, and video extension using
  Gemini Omni 1.1 Flash (gemini-omni-1.1-flash) via the gemini-api CLI and
  Google Gen AI SDKs. Generates 3s-10s video clips (extendable up to 40s) from
  360p to 4K with native synchronized audio, dialogue, and sound effects.
  Activate when generating videos from text, animating starting/ending frames,
  editing existing videos conversationally, or extending video clips.
license: Apache-2.0
metadata:
  category: media
  tags: "video-generation, video-editing, multimodal, generative-ai, gemini-api"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Gemini Omni Video Generation & Editing Skill

Generate, edit, interpolate, and extend high-coherence video with native synchronized audio using **Gemini Omni 1.1 Flash** (`gemini-omni-1.1-flash`) via the official **`gemini-api` CLI** (`gemini-api video`) for terminal and coding agent workflows, or the **Google Gen AI SDKs** (`client.interactions.create`) for application backends.

---

## Prerequisites: `gemini-api` CLI Setup

The `gemini-api` CLI is a zero-dependency binary that handles interaction polling automatically, writes generated MP4 videos directly to disk, and prints only the output file path to `stdout`, keeping raw base64 video payloads out of agent context windows.

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
gemini-api video --help
gemini-api video --schema
```

---

## Trigger Conditions

Activate this skill whenever the user asks to:
- Generate video clips with synchronized audio, dialogue, music, or sound effects from text prompts.
- Animate a starting image (`<FIRST_FRAME>`) or interpolate smoothly between a starting frame and an ending frame (`<FIRST_FRAME> <LAST_FRAME>`), including seamless loops.
- Generate videos guided by multiple character, object, or style reference images (`<IMAGE_REF_0>`) or reference video clips (`<VIDEO_REF_0>`).
- Edit an existing video conversationally across multiple turns (`--previous-interaction-id`) or from an uploaded source MP4 (`-i`).
- Replace or regenerate a video's audio track from scratch while preserving or editing visual elements.
- Extend a video clip in 10-second increments up to 40 seconds total.

---

## Model Specifications (`gemini-omni-1.1-flash`)

| Feature / Parameter | Specification |
| :--- | :--- |
| **Model ID (`-m`)** | `gemini-omni-1.1-flash` (Default in `gemini-api video`; GA replacement for deprecated `gemini-omni-flash-preview`) |
| **API Surface** | Interactions API (`v1beta/interactions` via `gemini-api video` or `client.interactions.create`) |
| **Input Context Window** | `1,048,576` tokens (Text, Image, Audio, Video inputs simultaneously) |
| **Resolutions (`--resolution`)** | `360p`, `720p` (default), `1080p`, `4k` |
| **Aspect Ratios (`--aspect-ratio`)** | `16:9` (landscape, default), `9:16` (portrait) |
| **Clip Duration** | `3s`–`10s` per generation (`duration`: `"3s"` to `"10s"`, default `"10s"`), extendable by `+10s` per turn up to `40s` total |
| **Frame Rate & Audio** | `24 FPS` MP4 with native synchronized dialogue, music, ambient soundscapes, and SFX |
| **Safety & Provenance** | Invisible **SynthID** watermark embedded in all generated video frames and audio |
| **Reference Guide** | [gemini-omni-1-1-flash.md](references/gemini-omni-1-1-flash.md) |

> [!IMPORTANT]
> **Deterministic Fail-Fast Rules**:
> - Never fall back to the deprecated `gemini-omni-flash-preview` model (shut down October 22, 2026); always use `gemini-omni-1.1-flash`.
> - Use `gemini-api video ... --dry-run -o json` to validate request schemas offline before launching long 1080p/4K video generations.

---

## Deep Technical References

Consult the reference directory for complete Interactions API schemas, media role tags, and advanced workflows:

- **[references/gemini-omni-1-1-flash.md](references/gemini-omni-1-1-flash.md)**: Full specification for `gemini-omni-1.1-flash`, media role binding tags (`<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_N>`, `<VIDEO_REF_N>`, `[# Sources ...]`), URI delivery polling, `ffmpeg` pre-processing, and SDK code samples.
- **[references/README.md](references/README.md)**: Index and quick reference for Gemini Omni video workflows.

---

## Core Execution Workflows

### 1. CLI Execution via `gemini-api video`

Use `gemini-api video` for terminal exploration, shell pipelines, and coding agent loops. By default it uses `gemini-omni-1.1-flash`, polls until completion, writes the MP4 file directly to disk, and prints only the saved file path to `stdout`:

```bash
# 1. Text-to-Video (1080p landscape with native synchronized audio)
gemini-api video \
  "A slow camera move through a sunlit woodworking workshop, sawdust floating in warm lightbeams, soft acoustic guitar background music and gentle chiseling sounds" \
  --resolution "1080p" \
  --aspect-ratio "16:9" \
  --out "./assets/workshop.mp4"

# 2. Custom Duration (e.g., 5s clip at 4K resolution via --body response_format)
gemini-api video \
  "Macro shot of rain droplets hitting a neon-lit puddle in slow motion, crisp water splash sound effects" \
  --resolution "4k" \
  --aspect-ratio "16:9" \
  --body '{"response_format":{"type":"video","duration":"5s","resolution":"4k","aspect_ratio":"16:9"}}' \
  --poll-timeout 15m \
  --out "./assets/rain_4k.mp4"

# 3. First-Frame-to-Video (animate a starting image)
gemini-api video \
  "<FIRST_FRAME> The camera slowly pushes in as the character looks up from the desk and smiles warmly. Use this image as the starting frame." \
  -i "start_frame.jpg" \
  --resolution "1080p" \
  --out "./assets/animated_intro.mp4"

# 4. First-and-Last-Frame Interpolation
gemini-api video \
  "<FIRST_FRAME> <LAST_FRAME> A smooth cinematic transition from a lush green forest at sunrise to a snowy forest under a starry night sky." \
  -i "forest_sunrise.jpg" \
  -i "forest_winter.jpg" \
  --resolution "1080p" \
  --out "./assets/season_transition.mp4"

# 5. Seamless Looping Video (same image bound as both first and last frame)
gemini-api video \
  "[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1] Cozy pixel-art campfire crackling gently in the wind at night. Use this image as the first frame and the last frame." \
  -i "campfire.png" \
  --resolution "720p" \
  --out "./assets/campfire_loop.mp4"

# 6. Multi-Reference Generation (combine character, object, and style anchors)
gemini-api video \
  "[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2] In the ink painting style of <IMAGE_REF_0>, the character shown in <IMAGE_REF_1> walks across a misty wooden bridge. Use the given images as references for video generation. The images should not be used as literal initial frames." \
  -i "ink_style.png" \
  -i "character_sheet.png" \
  --resolution "1080p" \
  --out "./assets/bridge_scene.mp4"

# 7. Stateful Multi-Turn Video Editing & Extension (--previous-interaction-id)
TURN1_ID=$(gemini-api video \
  "A violinist performing outdoors in an autumn park, expressive solo violin melody" \
  --resolution "720p" \
  --out "violin_v1.mp4" \
  --jq '.response_id')

# Edit the generated video while preserving unmentioned elements
gemini-api video \
  "Change the autumn trees to blooming cherry blossoms in spring. Keep everything else the same." \
  --previous-interaction-id "$TURN1_ID" \
  --out "violin_spring.mp4"

# Extend the video by +10 seconds
gemini-api video \
  "Extend this video: the camera pans up to reveal a stone pavilion as the violin melody builds into a crescendo." \
  --previous-interaction-id "$TURN1_ID" \
  --out "violin_extended.mp4"

# 8. Asynchronous Submission & Resume Polling
OP_ID=$(gemini-api video "A futuristic high-speed train gliding through a canyon at dusk" \
  --resolution "1080p" \
  --async \
  --jq '.id')
gemini-api video --resume "$OP_ID" --out "./assets/train.mp4"

# 9. Offline Request Validation (zero network calls)
gemini-api video "A drone shot of a mountain landscape" --resolution "1080p" --aspect-ratio "16:9" --dry-run -o json
```

#### `gemini-api video` Flag Reference
- `<prompt>`: Positional text prompt describing the video to generate, edit, or extend (or pass `--stdin` to read prompt text from stdin).
- `-m`, `--model`: Model ID (defaults to `gemini-omni-1.1-flash`).
- `--aspect-ratio`: Video aspect ratio: `16:9` (default), `9:16`.
- `--resolution`: Video resolution: `360p`, `720p` (default), `1080p`, `4k`.
- `-i`, `--input`: Repeatable flag accepting local file paths, `files/<id>` URIs (from `gemini-api files upload`), or YouTube URLs.
- `--mime-type`: Override detected MIME type when a single `--input` is provided.
- `--out`: Output video file path or directory (default: `./gemini-video-{timestamp}-{rand}.{ext}`).
- `--previous-interaction-id`: Continue from an earlier interaction ID (`--out <file> --jq .response_id`) to edit or extend the video it produced without re-uploading.
- `--async`: Return the operation/interaction handle immediately without waiting for completion.
- `--resume <id>`: Resume polling an existing interaction/operation ID until completion.
- `--poll-interval`, `--poll-timeout`: Configure polling backoff and deadline (default `2s` interval, `10m` timeout; increase to `15m` for `4k` or multi-reference renders).
- `--body`: Merge raw JSON into the Interactions API request (`@path` reads a file, `@-` reads stdin). Use for custom `duration` (`"3s"` to `"10s"`), `delivery: "uri"`, or `generation_config.video_config.task` (`"image_to_video"`).
- `--raw-response`: Print the raw API response JSON instead of writing the video file.
- `--schema` / `--usage` / `--dry-run`: Inspect the exact JSON Schema, KDL command specification, or validate the HTTP request offline.
- **Exit Codes**: `0` ok · `1` runtime error · `2` usage/validation error · `3` authentication/authorization error.

---

### 2. Pre-Processing & Audio Replacement Rules (`ffmpeg`)

When editing or extending existing local video files (`-i source.mp4`), apply these deterministic `ffmpeg` rules before uploading:

1. **Preserve vs. Regenerate Audio (`ffmpeg -an`)**:
   - By default, Gemini Omni 1.1 Flash preserves the original audio of an input video during edits unless you explicitly prompt for audio changes.
   - To force the model to **synthesize a brand-new audio track from scratch** matching your visual edits, strip the audio stream before passing `-i`:
     ```bash
     ffmpeg -y -i source.mp4 -c:v copy -an source_silent.mp4
     gemini-api video \
       "[# Sources <VIDEO_0>@Video1] Transform the daytime street into a rainy cyberpunk night with neon reflections, heavy rain sound effects, distant thunder, and synth ambient music. Keep everything else the same." \
       -i "source_silent.mp4" \
       --out "cyberpunk_edit.mp4"
     ```
2. **Optimize Oversized Source Videos**:
   - **Source videos for editing**: Trim to the target `<=10s` segment and downscale to `<=1080p` before uploading to avoid unnecessary upload latency:
     ```bash
     ffmpeg -y -ss 00:00:00 -to 00:00:10 -i raw_clip.mp4 \
       -vf "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2" \
       -c:v libx264 -crf 18 -preset fast -c:a aac source_ready.mp4
     ```
   - **Reference videos (`<VIDEO_REF_N>`)**: Keep reference clips around **~3 seconds** (and use at most 3 video references per request) for optimal character/object extraction.

---

### 3. Prompt Role Tags & Multi-Input Binding

When passing multiple images or videos via `-i` or the Interactions API `input` list, bind each media item to its exact role using inline tags or explicit header declarations:

| Role Tag / Header | Purpose | Example Prompt Snippet |
| :--- | :--- | :--- |
| `<FIRST_FRAME>` | Use image as the literal starting frame | `<FIRST_FRAME> A woman walks through a sunlit courtyard. Use this image as the starting frame.` |
| `<FIRST_FRAME> <LAST_FRAME>` | Interpolate smoothly from Image 1 to Image 2 | `<FIRST_FRAME> <LAST_FRAME> Smooth camera pan transitioning from dawn to dusk.` |
| `<IMAGE_REF_0>`, `<IMAGE_REF_1>` | Bind images as character, object, or style references (0-indexed) | `In the watercolor style of <IMAGE_REF_0>, the fox in <IMAGE_REF_1> leaps over a stream.` |
| `<VIDEO_REF_0>` | Bind an input video (~3s) as a motion/character reference (0-indexed) | `The person in <VIDEO_REF_0> is playing the violin on stage.` |
| `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]` | Loop a single image as both first and last frame | `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1] Gentle ocean waves lapping at the shore. Use this image as the first frame and the last frame.` |
| `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]` | Combine a literal starting frame with a reference image | `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] The character <IMAGE_REF_0> enters the room. Use Image1 as the starting frame. Use Image2 as a reference for video generation.` |

---

### 4. SDK Integration Patterns (Application Backends)

For production services in Python, TypeScript, or Go, call the **Interactions API** (`client.interactions.create`):

```python
import base64
from google import genai

client = genai.Client()

# Turn 1: Generate 1080p 16:9 video with native audio
turn1 = client.interactions.create(
    model="gemini-omni-1.1-flash",
    input="A cinematic tracking shot of a rover driving across rust-red Martian dunes at sunset, low rumbling mechanical treads and whistling wind.",
    response_format={
        "type": "video",
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "duration": "10s",
    },
)

if turn1.output_video and turn1.output_video.data:
    with open("mars_rover.mp4", "wb") as f:
        f.write(base64.b64decode(turn1.output_video.data))

# Turn 2: Stateful conversational edit using previous_interaction_id
turn2 = client.interactions.create(
    model="gemini-omni-1.1-flash",
    previous_interaction_id=turn1.id,
    input="Add a twin dust devil swirling on the horizon and shift lighting to blue twilight. Keep everything else the same.",
)

if turn2.output_video and turn2.output_video.data:
    with open("mars_rover_twilight.mp4", "wb") as f:
        f.write(base64.b64decode(turn2.output_video.data))
```

---

## Prompting Best Practices
1. **Direct Audio Explicitly**: Specify background music genre/tempo, ambient soundscapes, and exact dialogue in quotes with voice/accent descriptors (`"She says in a calm British accent: 'Systems are online.'"`). If you want no spoken words, state `"No dialogue"`.
2. **Use Timecodes for Multi-Shot Sequences**: Structure 10-second clips with bracketed timestamps (`[0-3s] Wide establishing shot... [3-7s] Cut to medium close-up... [7-10s] Slow pull-back...`). When extending a video, `0s` refers to the start of the new extended segment.
3. **Render Readable In-Scene Text**: Put desired on-screen titles, signage, or license plates in quotes (`a neon sign that says "OPEN 24/7"`).
4. **Surgical Edits**: When editing an existing video, end your prompt with `"Keep everything else the same"` to lock background geometry, lighting, and unmentioned subjects.
