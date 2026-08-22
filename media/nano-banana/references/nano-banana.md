# Nano Banana (`gemini-2.5-flash-image`) Model Card

## Overview
**Nano Banana** (`gemini-2.5-flash-image`) is Google's foundational image generation model in the Gemini family. It introduced conversational image generation and editing at a fixed 1024px resolution.

- **Model Code**: `gemini-2.5-flash-image`
- **Release Date**: October 2, 2025 (GA)
- **Retirement Date**: October 2, 2026 *(Migration recommended to Nano Banana 2 Lite)*
- **Status**: General Availability (GA)

---

## Technical Specifications

| Property | Value |
| :--- | :--- |
| **Input Modalities** | Text, Images (up to 3), PDF (up to 3 pages) |
| **Output Modalities** | Image and Text |
| **Input Token Limit** | 65,536 tokens |
| **Output Token Limit** | 32,768 tokens |
| **Image Generation Cost** | Fixed at **1,290 tokens** per image |
| **Max Resolution** | **1K only** (1024px bounding box; 2K/4K unsupported) |
| **Aspect Ratios** | 10 standard ratios |
| **Thinking Mode** | ❌ Not Supported |
| **Search Grounding** | ❌ Not Supported |
| **Video Context** | ❌ Not Supported |
| **Function Calling** | ❌ Not Supported |
| **Watermarking** | SynthID (Always On) + C2PA Metadata |

---

## Supported Aspect Ratios & Output Dimensions (1K Fixed)

| Aspect Ratio | Output Dimensions | Token Cost |
| :---: | :---: | :---: |
| **`1:1`** | 1024 × 1024 | 1,290 |
| **`2:3`** | 832 × 1248 | 1,290 |
| **`3:2`** | 1248 × 832 | 1,290 |
| **`3:4`** | 864 × 1184 | 1,290 |
| **`4:3`** | 1184 × 864 | 1,290 |
| **`4:5`** | 896 × 1152 | 1,290 |
| **`5:4`** | 1152 × 896 | 1,290 |
| **`9:16`** | 768 × 1344 | 1,290 |
| **`16:9`** | 1344 × 768 | 1,290 |
| **`21:9`** | 1536 × 672 | 1,290 |

---

## Model Comparison: Nano Banana vs Banana 2 Family

| Feature | Nano Banana (`gemini-2.5-flash-image`) | Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`) | Nano Banana 2 (`gemini-3.1-flash-image`) |
| :--- | :--- | :--- | :--- |
| **Latency** | ~4–6s | **< 2s** | ~3–5s |
| **Resolutions** | 1K only | 1K only | **512px, 1K, 2K, 4K** |
| **Aspect Ratios** | 10 standard | 14 discrete | 14 discrete |
| **Search Grounding** | ❌ None | ❌ None | **Web & Image Search** |
| **Reference Images** | Up to 3 | Up to 14 | Up to 14 |
| **Thinking Support** | ❌ None | **`minimal`, `high`** | **`minimal`, `high`** |

---

## API Code Example

```python
import base64
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-2.5-flash-image",
    input="A high-contrast ink sketch of a mountain pass at dawn",
    response_format={
        "type": "image",
        "mime_type": "image/png",
        "aspect_ratio": "16:9",
    },
)

if interaction.output_image:
    with open("mountain.png", "wb") as f:
        f.write(base64.b64decode(interaction.output_image.data))
```
