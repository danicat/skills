---
name: nano-banana
description: Generate or edit images using Nano Banana models (gemini-2.5-flash-image, gemini-3.1-pro-image, gemini-3.1-flash-image) with ADC auth. Supports "banana" as a verb (e.g., "please banana this") and Anime Dani / Chibi Dani character consistency.
---

# Nano Banana Skill

Generate or edit images using Google's Nano Banana models (`gemini-2.5-flash-image`, `gemini-3.1-pro-image`, `gemini-3.1-flash-image`) with Application Default Credentials (ADC) authentication.

## Trigger Conditions
- When the user asks to generate or edit images using Nano Banana models.
- When the user uses **"banana" as a verb** (e.g., "please banana this image", "banana me as an anime character", "banana this into chibi style").

## Supported Models
- **Nano Banana** (`gemini-2.5-flash-image`): Fast, standard image generation and editing.
- **Nano Banana Pro** (`gemini-3.1-pro-image`): High quality, detailed image generation and editing (default).
- **Nano Banana 2** (`gemini-3.1-flash-image`): Next-gen fast Flash image model.

## Character Consistency (Anime Dani, Daniela & Chibi Dani)
When requested to generate or edit images featuring **Anime Dani**, **Daniela**, or **Chibi Dani**, pass the corresponding reference image(s) from `{baseDir}/references/` as input (`-i`) to maintain visual consistency:

### Anime Dani / Daniela
- **Style Instructions**: Anime style, vibrant colors, expressive eyes, cel-shaded, detailed linework.
- **Reference Image**: Pass `{baseDir}/references/speaker-dani.png` and `{baseDir}/references/celebrating-dani.png` via `-i`.

### Chibi Dani
- **Style Instructions**: Super-deformed (SD) chibi style, oversized head, cute proportions, simplified outlines, kawaii aesthetic.
- **Reference Image**: Pass `{baseDir}/references/chibi-dani.png` via `-i`.

## Usage & Execution
**Note on `{baseDir}`**: `{baseDir}` refers to the root directory of the installed skill (e.g. `~/.agents/skills/nano-banana`). When executing commands, the agent resolves `{baseDir}` to the absolute path of this directory.

Use `uv run` to execute the image generation script at `{baseDir}/scripts/banana.py`.

### CLI Options
- `--prompt` / `-p`: Text prompt describing the image to generate or edit (required).
- `--filename` / `-f`: Output image filename (required).
- `--input-image` / `-i`: Path to input/reference image(s). Can be specified up to 14 times for editing or multi-image composition.
- `--model` / `-m`: Model selection (`nano-banana`, `nano-banana-pro`, `nano-banana-2`). Default: `nano-banana-pro`.
- `--resolution` / `-r`: Output resolution (`1K`, `2K`, `4K`). Default: Auto-detected or `1K`.
- `--project`: GCP Project ID for Vertex AI (optional).
- `--location`: GCP Location for Vertex AI (optional, default: `us-central1`).

### Authentication
Uses Application Default Credentials (ADC). Ensure ADC is configured via `gcloud auth application-default login` or environment variables `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION`.

### Examples
```bash
# Text-to-Image Generation
uv run {baseDir}/scripts/banana.py -p "Anime Dani studying at a futuristic desk" -f "anime_dani_desk.png" -i "{baseDir}/references/speaker-dani.png" -i "{baseDir}/references/celebrating-dani.png" -m "nano-banana-pro"

# Image Editing ("banana this")
uv run {baseDir}/scripts/banana.py -p "banana this into chibi style, super deformed kawaii" -i "input_photo.png" -i "{baseDir}/references/chibi-dani.png" -f "chibi_result.png" -m "nano-banana-2"
```
