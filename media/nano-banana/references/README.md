# Nano Banana references and model cards

This directory contains technical model cards, resolution grids, and reference-anchor guidance for Google's Nano Banana models.

## Model cards and technical references

- **[Nano Banana 2.1 (`gemini-nano-banana-2.1`)](nano-banana-2-1.md)**: Primary recommended creative workhorse (`1K`/`2K`/`4K`, 14 aspect ratios with panoramic seam elimination, `minimal`/`medium` [default]/`high` thinking levels, Google Web + Image Search grounding, conversational multi-turn regional editing, and up to 14 reference anchors).
- **[Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`)](nano-banana-2-lite.md)**: Low-latency (<2s), high-throughput model (`1K` resolution across 14 aspect ratios, video-to-image input supported, function calling supported).
- **[Nano Banana 2 (`gemini-3.1-flash-image`)](nano-banana-2.md)**: Previous-generation multimodal model with `512px`/`1K`/`2K`/`4K` output, 14 aspect ratios, and Google Web + Image Search grounding.
- **[Nano Banana Pro (`gemini-3-pro-image`)](nano-banana-pro.md)**: Studio asset production, 4K rendering, multi-reference consistency (up to 14 anchors: 6 objects, 5 characters, 3 styles), and default pre-generation thinking.

---

## Reference images and two-step sprite consistency anchors

Pass reusable reference images (turnaround character sheets, style targets, or tileset templates) to `uv run scripts/banana.py` or `gemini-api image` using repeatable `-i` (`--input-image` / `--input`) flags.

Generate a Step 1 character reference sheet first, then pass `-i character_sheet.png` to lock proportions and color ramps across Step 2 `4x4` chroma-key sprite grids:

```bash
# Using uv run scripts/banana.py (supports Vertex AI / Gemini Enterprise ADC and GEMINI_API_KEY)
uv run scripts/banana.py \
  -p "Keep the exact character identity and 4-step color swatches from the reference image: generate a uniform 4x4 sprite sheet grid on a flat unlit #00FF00 background with at least 15% empty #00FF00 margin inside every cell, no grid lines, and no labels." \
  -i "character_sheet.png" \
  -f "raw_grid_part1.png" \
  -m "nano-banana-2.1" \
  -r "2K" \
  -a "1:1" \
  --thinking-level "high"

# Or using gemini-api image
gemini-api image "Keep the exact character identity and 4-step color swatches from the reference image: generate a uniform 4x4 sprite sheet grid on a flat unlit #00FF00 background with at least 15% empty #00FF00 margin inside every cell, no grid lines, and no labels." \
  -m gemini-nano-banana-2.1 \
  -i character_sheet.png \
  --image-size 2K \
  --aspect-ratio 1:1 \
  --body '{"generation_config":{"thinking_level":"high"}}' \
  --out raw_grid_part1.png
```
