# Veo 3.1 & Veo 3.0 Technical Reference

Google's **Veo 3.1** (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-3.1-lite-generate-preview`) and **Veo 3.0** (`veo-3.0-generate-001`, `veo-3.0-fast-generate-001`) models generate high-definition 24 FPS video with native synchronized audio through the asynchronous `generate_videos` (`predictLongRunning`) operation API.

---

## 1. Full Model & Parameter Specifications

| Parameter | Veo 3.1 (`generate` & `fast`) | Veo 3.1 Lite | Veo 3.0 (`generate-001` & `fast-001`) |
| :--- | :--- | :--- | :--- |
| **Text-to-Video** | Supported | Supported | Supported |
| **Image-to-Video (`image`)** | Supported | Supported | Supported |
| **First & Last Frame (`last_frame`)** | Supported (requires `8s`) | Supported (requires `8s`) | ❌ Unsupported |
| **Reference Images (`reference_images`)** | Up to 3 `asset` images (requires `8s`) | ❌ Unsupported | ❌ Unsupported |
| **Video Extension (`video`)** | `+7s` up to 20 hops (`720p` only) | `+7s` (`720p` only) | ❌ Unsupported |
| **Aspect Ratios (`aspect_ratio`)** | `"16:9"` (default), `"9:16"` | `"16:9"` (default), `"9:16"` | `"16:9"`, `"9:16"` |
| **Resolutions (`resolution`)** | `"720p"`, `"1080p"` (`8s`), `"4k"` (`8s`) | `"720p"`, `"1080p"` (`8s`) | `"720p"`, `"1080p"` (`16:9` only) |
| **Durations (`duration_seconds`)** | `4`, `6`, `8` | `4`, `6`, `8` | `4`, `6`, `8` |
| **Frame Rate** | `24 FPS` | `24 FPS` | `24 FPS` |
| **Audio Generation** | Native synchronized audio (always on) | Native synchronized audio (always on) | Native synchronized audio (always on) |
| **`negative_prompt`** | Supported (string) | Supported (string) | Supported (string) |
| **`seed`** | ❌ Unsupported | ❌ Unsupported | Supported (`int`, slightly improves determinism) |
| **Watermarking** | SynthID watermark embedded | SynthID watermark embedded | SynthID watermark embedded |

### `person_generation` Safety Controls
| Generation Mode | Veo 3.1 Allowed Values | Veo 3.0 Allowed Values |
| :--- | :--- | :--- |
| **Text-to-Video** | `"allow_all"` only | `"allow_all"` only |
| **Image-to-Video / Interpolation / Reference Images** | `"allow_adult"` only | `"allow_adult"` only |

> [!NOTE]
> Regional restrictions: In the EU, UK, Switzerland, and MENA regions, the only allowed value for `person_generation` is `"allow_adult"` across all modes.

---

## 2. Multi-Language SDK Code Samples

### Python: Image-to-Video Pipeline (Nano Banana + Veo 3.1)
Generate a high-precision starting keyframe with Nano Banana (`gemini-nano-banana-2.1` or `gemini-2.5-flash-image`), then animate it with Veo:

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

# Step 1: Generate starting keyframe image
img_response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A panoramic shot of a calico kitten sleeping in a sunlit garden surrounded by lavender.",
    config={"response_modalities": ["IMAGE"]},
)
starting_image = img_response.parts[0].as_image()

# Step 2: Animate the keyframe with Veo 3.1
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="The calico kitten wakes up, stretches its paws lazily, and yawns in the warm sunlight, gentle birdsong in the garden.",
    image=starting_image,
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="1080p",
        duration_seconds=8,
    ),
)

while not operation.done:
    print("Waiting for Veo video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("calico_kitten.mp4")
```

### TypeScript (`@google/genai`): Reference Images & Interpolation
```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

// 1. Reference-Guided Video Generation (up to 3 asset references)
let operation = await ai.models.generateVideos({
  model: "veo-3.1-generate-preview",
  prompt:
    "The woman walks with serene confidence through shallow turquoise water wearing the flamingo dress and heart-shaped sunglasses, gentle ocean waves lapping.",
  config: {
    aspectRatio: "16:9",
    durationSeconds: 8,
    referenceImages: [
      { image: dressImage, referenceType: "asset" },
      { image: glassesImage, referenceType: "asset" },
      { image: womanImage, referenceType: "asset" },
    ],
  },
});

while (!operation.done) {
  await new Promise((resolve) => setTimeout(resolve, 10000));
  operation = await ai.operations.getVideosOperation({ operation });
}

await ai.files.download({
  file: operation.response!.generatedVideos![0].video!,
  downloadPath: "flamingo_fashion.mp4",
});
```

### Go (`google.golang.org/genai`): Text-to-Video & Extension
```go
package main

import (
	"context"
	"log"
	"os"
	"time"

	"google.golang.org/genai"
)

func main() {
	ctx := context.Background()
	client, err := genai.NewClient(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}

	// Step 1: Generate 720p base video (required for extension)
	op, err := client.Models.GenerateVideos(
		ctx,
		"veo-3.1-generate-preview",
		"An origami butterfly flaps its wings and flies out through French doors into a sunlit garden.",
		nil,
		&genai.GenerateVideosConfig{
			AspectRatio: "16:9",
			Resolution:  "720p",
		},
	)
	if err != nil {
		log.Fatal(err)
	}

	for !op.Done {
		time.Sleep(10 * time.Second)
		op, err = client.Operations.GetVideosOperation(ctx, op, nil)
		if err != nil {
			log.Fatal(err)
		}
	}

	baseVideo := op.Response.GeneratedVideos[0]
	if _, err := client.Files.Download(ctx, baseVideo.Video, nil); err != nil {
		log.Fatal(err)
	}
	if err := os.WriteFile("butterfly_base.mp4", baseVideo.Video.VideoBytes, 0644); err != nil {
		log.Fatal(err)
	}

	// Step 2: Extend the generated video by +7 seconds at 720p
	extOp, err := client.Models.GenerateVideos(
		ctx,
		"veo-3.1-generate-preview",
		"Track the origami butterfly as it lands on an orange flower while a white puppy runs up.",
		nil,
		&genai.GenerateVideosConfig{
			NumberOfVideos: 1,
			Resolution:     "720p",
		},
	)
	_ = extOp
}
```

---

## 3. Veo Video Extension Constraints

When extending Veo videos (`video=previous_video`):
- **Source Restriction**: Input videos **must** be a Veo-generated video handle from a previous `generate_videos` operation (arbitrary external MP4 files are rejected by Veo's extension endpoint; use `gemini-omni-1.1-flash` via `gemini-api video` if you need to extend arbitrary uploaded MP4s).
- **Resolution & Aspect Ratio**: Only `"720p"` in `"16:9"` or `"9:16"` is supported for extensions.
- **Length & Hop Limits**: Input videos can be up to `141` seconds long. Each extension adds `7` seconds, up to **20 extensions** (`148` seconds maximum combined duration).
- **Audio Continuity**: Veo uses the final 1 second (24 frames) of the prior video to maintain visual and audio continuity; ensure smooth background audio exists in the final second of the input clip.
