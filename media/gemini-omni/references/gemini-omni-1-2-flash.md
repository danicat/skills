# Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`) technical reference

**Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`) is Google's generally available (GA) multimodal model for conversational video generation, multimodal video editing, first-and-last-frame interpolation, video extension, and standalone video upscaling via the **Interactions API**.

---

## 1. Technical specifications

| Property | Value |
| :--- | :--- |
| **Canonical model ID** | `gemini-omni-1.2-flash` (GA release date: November 5, 2026; retirement: November 5, 2027 or later) |
| **CLI aliases (`scripts/omni.py`)** | `gemini-omni-1.2-flash`, `omni-1.2-flash`, `omni-1.2`, `1.2`, `flash-1.2` |
| **API surface** | Interactions API (`client.interactions.create` / `v1beta1/projects/{PROJECT_ID}/locations/global/interactions`); `GenerateContent` is not supported |
| **Vertex AI / Enterprise region** | `global` |
| **Supported modalities** | Text (input and output), Image (input only: JPEG, PNG, WebP, HEIC, HEIF), Video with synchronized speech, music, and sound effects (input and output: MP4, MOV as `video/quicktime`, WebM, MPEG, MPG, WMV, 3GP, FLV; standalone audio input/output is not supported) |
| **Maximum input tokens** | `131,072` tokens |
| **Maximum output tokens** | `65,536` tokens (`260,640` tokens on Vertex AI / Gemini Enterprise Agent Platform) |
| **Output video duration (`duration`)** | `3s` to `15s` (default `10s`, whole seconds) for text-to-video, single-image-to-video, reference-to-video, and video editing; `3s` to `10s` for 2-image first-and-last-frame interpolation |
| **Video extension (`extend`)** | `3s` to `10s` per turn (default `10s`), using up to the final `10s` of the input video as context (up to `30s` total in Gemini API; up to `40s` concatenated on Gemini Enterprise / Vertex AI) |
| **Standalone video upscaling (`upscale`)** | Upscales `360p` input videos to `720p` or `1080p`, and `720p` input videos to `1080p` or `4k` (`<= 15s` at `24 FPS`, `total_input_tokens: 0`) |
| **Reference images** | Up to `6` in Gemini API (`10` max on Gemini Enterprise / Vertex AI; up to 3 images per character for up to 2 characters) across all durations (`3s` to `15s`) |
| **Reference videos** | Up to `3` reference videos (up to `3s` each) for `3s` to `10s` output clips; at most `1` reference video (up to `3s` long) for `11s` to `15s` output clips |
| **Input video for editing / upscaling** | `1` input video up to `15s` long (`720p` or `1080p` recommended for editing; `360p` or `720p` for upscaling) |
| **Resolutions and aspect ratios** | `360p`, `720p` (default), `1080p`, `4k` at `24 FPS`; `16:9` (default), `9:16` |
| **Delivery modes** | Inline base64 (`delivery: "inline"`, default), Files API URI (`delivery: "uri"`, recommended for `> 4 MB` / `> 720p`), or Cloud Storage (`gcs_uri` on Gemini Enterprise / Vertex AI) |
| **Watermarking** | Invisible SynthID watermark embedded in generated video frames and audio |

> [!WARNING]
> **Deprecated control tags**:
> Do not include control strings such as `<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_0>`, or `<VIDEO_REF_0>` in text prompts for `gemini-omni-1.2-flash`. Describe how each image or video should be used in natural language instead, and optionally set `--task` (`generation_config.video_config.task`) if needed.

---

## 2. Gemini Enterprise / Vertex AI (`global`) and Gemini API authentication

`gemini-omni-1.2-flash` runs on the `global` location in Gemini Enterprise / Vertex AI (`https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/global/interactions`) as well as the Gemini Developer API (`GEMINI_API_KEY`). `scripts/omni.py` defaults `--location` to `global` when initializing ADC:

```bash
# Option A: Gemini Enterprise / Vertex AI (ADC)
gcloud auth application-default login --billing-project YOUR_PROJECT_ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_ENTERPRISE="true"

# Option B: Gemini Developer API
export GEMINI_API_KEY="your-api-key"

uv run scripts/omni.py \
  --enterprise \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --model "gemini-omni-1.2-flash" \
  --resolution "1080p" \
  --duration "15s" \
  --prompt "A cinematic drone shot flying over a coastal lighthouse at sunset, crashing ocean waves and warm orchestral strings." \
  --output "lighthouse_15s.mp4"
```

---

## 3. Task modes (`generation_config.video_config.task`)

By default, `gemini-omni-1.2-flash` infers the video task from your natural-language prompt and input media. Pass `--task` on the CLI or set `generation_config.video_config.task` when you want to pin the task (and always when running `upscale`):

| Task value | Description | Duration range | Required inputs |
| :--- | :--- | :--- | :--- |
| `text_to_video` | Generate a new video with synchronized audio from a text prompt | `3s` to `15s` (default `10s`) | Text prompt |
| `image_to_video` | Animate 1 starting image (`3s` to `15s`) or interpolate between 2 frames (`3s` to `10s`) | `3s` to `15s` (1 image) / `3s` to `10s` (2 images) | 1 or 2 images + prompt |
| `reference_to_video` | Generate a new video guided by character, object, style, or motion references | `3s` to `15s` | Up to 6-10 images and/or up to 3 videos (`<=10s`) or 1 video (`11s-15s`) + prompt |
| `edit` | Edit an existing video while preserving unmentioned visual and audio elements | `3s` to `15s` | 1 input video (or `--previous-interaction-id`) + up to 2 ref images + prompt |
| `extend` | Extend the end of an existing video using up to its final `10s` as context | `3s` to `10s` per turn | 1 input video (or `--previous-interaction-id`) + up to 2 ref images + prompt |
| `upscale` | Upscale a `360p` video to `720p`/`1080p` or a `720p` video to `1080p`/`4k` | Preserves input duration (`<= 15s`) | 1 input video (or `--previous-interaction-id`) + target `--resolution` |

---

## 4. Python SDK (`google-genai`) patterns for `gemini-omni-1.2-flash`

The SDK examples below initialize `genai.Client(enterprise=True, location="global", ...)`; omit those arguments to use `GEMINI_API_KEY` via `genai.Client()`.

### Text-to-video (15 seconds with synchronized dialogue and audio)

```python
import base64
from pathlib import Path
import google.auth
from google import genai

credentials, project_id = google.auth.default()
client = genai.Client(
    enterprise=True,
    project=project_id,
    location="global",
    credentials=credentials,
)

interaction = client.interactions.create(
    model="gemini-omni-1.2-flash",
    input=(
        "[0-5s] Wide shot of an observatory dome opening under a starry desert sky with low mechanical hum. "
        "[5-10s] Medium shot of an astronomer looking through a brass eyepiece. "
        '[10-15s] She smiles and says in a hushed voice: "There it is, right on schedule."'
    ),
    response_format={
        "type": "video",
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "duration": "15s",
    },
    generation_config={
        "seed": 42,
    },
)

if interaction.output_video and interaction.output_video.data:
    Path("observatory_15s.mp4").write_bytes(
        base64.b64decode(interaction.output_video.data)
    )
```

### First-and-last-frame interpolation (`3s` to `10s`)

```python
import base64
from pathlib import Path
from google import genai

client = genai.Client(enterprise=True, location="global")

first_b64 = base64.b64encode(Path("first_frame.jpg").read_bytes()).decode("utf-8")
last_b64 = base64.b64encode(Path("last_frame.jpg").read_bytes()).decode("utf-8")

interaction = client.interactions.create(
    model="gemini-omni-1.2-flash",
    input=[
        {"type": "image", "data": first_b64, "mime_type": "image/jpeg"},
        {"type": "image", "data": last_b64, "mime_type": "image/jpeg"},
        {
            "type": "text",
            "text": (
                "Use the first image as the starting frame and the second image as the ending frame. "
                "Create a smooth time-lapse transition from daytime construction to an illuminated skyscraper at night."
            ),
        },
    ],
    response_format={
        "type": "video",
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "duration": "10s",
    },
    generation_config={
        "video_config": {
            "task": "image_to_video",
        },
    },
)

if interaction.output_video and interaction.output_video.data:
    Path("interpolation.mp4").write_bytes(
        base64.b64decode(interaction.output_video.data)
    )
```

### Standalone video upscaling (`task: "upscale"`)

```python
import base64
from pathlib import Path
from google import genai

client = genai.Client(enterprise=True, location="global")

source_b64 = base64.b64encode(Path("draft_720p.mp4").read_bytes()).decode("utf-8")

interaction = client.interactions.create(
    model="gemini-omni-1.2-flash",
    input=[
        {"type": "video", "data": source_b64, "mime_type": "video/mp4"},
    ],
    response_format={
        "type": "video",
        "resolution": "4k",
        "delivery": "uri",
    },
    generation_config={
        "video_config": {
            "task": "upscale",
        },
    },
)
```

---

## 5. Performance and latency optimization tips

1. **Iterate at `360p` or `720p`, then upscale**: Draft and refine camera movement, dialogue timing, and scene edits at `360p` or `720p`, then run `--task upscale --resolution 1080p` (or `4k`) on the final clip. Upscaling bypasses text reasoning (`total_input_tokens: 0`) and preserves the exact motion and audio of your draft.
2. **Use stateless unary mode (`--no-store`) for single-turn renders**: When you do not need follow-up conversational turns (`--previous-interaction-id`), pass `--no-store` (`store=False, background=False, stream=False`) to enable server-side unary optimization and avoid multi-hop continuation prefill overhead.
3. **Use `delivery: "uri"` or `--gcs-uri` for high-resolution clips**: Videos above `720p` or `10s` often exceed `4 MB`; pass `--delivery uri` or `--gcs-uri gs://your-bucket/out/` to avoid large inline base64 payloads.
