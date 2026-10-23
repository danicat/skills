# Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`) Technical Reference

`gemini-omni-1.1-flash` is Google's generally available (GA) multimodal foundation model for fast video generation, multi-reference synthesis, frame interpolation, and stateful conversational video editing via the **Interactions API**.

---

## 1. Technical Specifications

| Property | Value |
| :--- | :--- |
| **Model Code** | `gemini-omni-1.1-flash` (replaces deprecated `gemini-omni-flash-preview`) |
| **Supported Inputs** | Text, Image (`image/jpeg`, `image/png`, `image/webp`), Audio, Video (`video/mp4`) |
| **Supported Outputs** | Video (`video/mp4` with synchronized stereo audio) |
| **Input Token Limit** | `1,048,576` tokens |
| **Output Clip Duration** | `3s` to `10s` per generation (`duration`: `"3s"`, `"4s"`, `"5s"`, `"6s"`, `"7s"`, `"8s"`, `"9s"`, `"10s"`, default `"10s"`) |
| **Video Extension** | `+10s` per extension turn, up to `40s` total duration (uses the final `10s` of the prior clip as context) |
| **Resolutions** | `360p`, `720p` (default), `1080p`, `4k` |
| **Aspect Ratios** | `16:9` (default), `9:16` |
| **Frame Rate** | `24 FPS` |
| **Delivery Modes** | Inline base64 (`delivery: "inline"`, default) or Files API URI (`delivery: "uri"`) |
| **Watermarking** | Invisible SynthID watermark embedded in video frames and audio |

> [!NOTE]
> **Regional Availability for Video Uploads**: Uploading input videos for video editing or video extension is not available in the European Economic Area (EEA), Switzerland, the United Kingdom, and certain US states.

---

## 2. `gemini-api video` CLI Recipes

### Text-to-Video with Timecoded Cuts & Dialogue
```bash
gemini-api video \
  '[0-4s] Medium shot of a robotics engineer in a brightly lit lab inspecting a bipedal robot arm. She says in a crisp voice: "Actuators calibrated." [4-10s] Cut to close-up as the metallic fingers pick up a delicate glass sphere with soft servo whirring sounds.' \
  --resolution "1080p" \
  --aspect-ratio "16:9" \
  --out "robotics_lab.mp4"
```

### Uploading Large Media via `gemini-api files upload`
For large source videos or reusable reference assets, upload once via the Files API and pass the returned `files/<id>` URI to `-i`:

```bash
# Upload reference video and character sheet once
REF_VIDEO=$(gemini-api files upload "dancer_ref_3s.mp4")
CHAR_IMAGE=$(gemini-api files upload "character_concept.png")

gemini-api video \
  "[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1] The character shown in <IMAGE_REF_0> performs the dance choreography from <VIDEO_REF_0> on a rooftop at sunset, upbeat funk bassline. Use Image1 as a character reference and Video1 as a motion reference." \
  -i "$CHAR_IMAGE" \
  -i "$REF_VIDEO" \
  --resolution "1080p" \
  --out "rooftop_dance.mp4"
```

### Multi-Turn Extension Up to 40 Seconds
```bash
# Segment 1 (0s - 10s)
ID_1=$(gemini-api video \
  "FPV drone flight entering a bioluminescent crystal cavern, echoing water drops and ethereal synth pad" \
  --resolution "1080p" \
  --out "cavern_10s.mp4" \
  --jq '.response_id')

# Segment 2 (10s - 20s)
ID_2=$(gemini-api video \
  "Extend this video: the drone dives through a narrow crystal arch into an underground subterranean lake as the synth music swells." \
  --previous-interaction-id "$ID_1" \
  --out "cavern_20s.mp4" \
  --jq '.response_id')

# Segment 3 (20s - 30s)
ID_3=$(gemini-api video \
  "Extend this video: after 2s the camera skims across the mirror-like water surface toward a glowing monolith." \
  --previous-interaction-id "$ID_2" \
  --out "cavern_30s.mp4" \
  --jq '.response_id')
```

---

## 3. SDK Patterns Across Languages

### Python: First-and-Last-Frame Interpolation
```python
import base64
from pathlib import Path
from google import genai

client = genai.Client()

first_b64 = base64.b64encode(Path("first_frame.jpg").read_bytes()).decode("utf-8")
last_b64 = base64.b64encode(Path("last_frame.jpg").read_bytes()).decode("utf-8")

interaction = client.interactions.create(
    model="gemini-omni-1.1-flash",
    input=[
        {"type": "image", "data": first_b64, "mime_type": "image/jpeg"},
        {"type": "image", "data": last_b64, "mime_type": "image/jpeg"},
        {
            "type": "text",
            "text": "<FIRST_FRAME> <LAST_FRAME> A smooth time-lapse transition from daytime construction to an illuminated skyscraper at night.",
        },
    ],
    response_format={
        "type": "video",
        "resolution": "1080p",
        "aspect_ratio": "16:9",
    },
)

if interaction.output_video and interaction.output_video.data:
    Path("interpolation.mp4").write_bytes(base64.b64decode(interaction.output_video.data))
```

### Python: URI Delivery Mode (`delivery: "uri"`) for Large Outputs
When generating high-bitrate `1080p` or `4k` videos in backend services, request `delivery: "uri"` to stream the resulting file via `client.files.download` instead of transferring base64 in the JSON body:

```python
import time
from pathlib import Path
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-omni-1.1-flash",
    input="An aerial tracking shot over glacial fjords at golden hour.",
    response_format={
        "type": "video",
        "resolution": "4k",
        "aspect_ratio": "16:9",
        "delivery": "uri",
    },
)

uri = interaction.output_video.uri
file_name = "files/" + uri.split("/")[-1]

while True:
    file_info = client.files.get(name=file_name)
    if file_info.state.name == "ACTIVE":
        break
    if file_info.state.name == "FAILED":
        raise RuntimeError(f"Video processing failed for {file_name}")
    time.sleep(5)

video_bytes = client.files.download(file=uri)
Path("fjords_4k.mp4").write_bytes(video_bytes)
```

### TypeScript (`@google/genai`): Uploaded Video Editing & Extension
```typescript
import { GoogleGenAI } from '@google/genai';
import * as fs from 'fs';

const ai = new GoogleGenAI({});

let videoFile = await ai.files.upload({
  file: 'source_clip.mp4',
  mimeType: 'video/mp4',
});

while (videoFile.state === 'PROCESSING') {
  await new Promise((r) => setTimeout(r, 5000));
  videoFile = await ai.files.get({ name: videoFile.name! });
}

const interaction = await ai.interactions.create({
  model: 'gemini-omni-1.1-flash',
  input: [
    { type: 'video', uri: videoFile.uri! },
    {
      type: 'text',
      text: '[# Sources <VIDEO_0>@Video1] Replace the clear blue sky with an aurora borealis and add gentle arctic wind sounds. Keep everything else the same.',
    },
  ],
  response_format: {
    type: 'video',
    resolution: '1080p',
  },
});

if (interaction.output_video?.data) {
  fs.writeFileSync('aurora_edit.mp4', Buffer.from(interaction.output_video.data, 'base64'));
}
```

### Go (`google.golang.org/genai`): Text-to-Video Generation
```go
package main

import (
	"context"
	"encoding/base64"
	"log"
	"os"

	"google.golang.org/genai"
	"google.golang.org/genai/interactions/models/interactions"
	"google.golang.org/genai/interactions/models/operations"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}

	videoFormat := interactions.VideoResponseFormat{
		Resolution:  interactions.ResolutionOneThousandAndEightyp.ToPointer(),
		AspectRatio: interactions.VideoResponseFormatAspectRatioSixteen9.ToPointer(),
	}

	res, err := client.Interactions.Create(ctx, operations.CreateInteractionRequest{
		Body: operations.NewCreateInteractionRequestBody(interactions.CreateModelInteraction{
			Model: interactions.Model("gemini-omni-1.1-flash"),
			Input: interactions.NewInteractionsInput("A drone shot of a mountain landscape at sunrise."),
			ResponseFormat: genai.Ptr(interactions.NewCreateModelInteractionResponseFormat(
				interactions.NewResponseFormat(videoFormat),
			)),
		}),
	})
	if err != nil {
		log.Fatal(err)
	}

	if res.Interaction.OutputVideo != nil && res.Interaction.OutputVideo.Data != nil {
		videoBytes, err := base64.StdEncoding.DecodeString(*res.Interaction.OutputVideo.Data)
		if err != nil {
			log.Fatal(err)
		}
		if err := os.WriteFile("sunrise.mp4", videoBytes, 0644); err != nil {
			log.Fatal(err)
		}
	}
}
```
