# Nano Banana References & Model Cards

This directory contains technical model cards, capability specifications, resolution matrices, and guidance for using reference anchors in multimodal and 2D game asset pipelines.

## Model Cards & Technical References

- **[Nano Banana 2.1 (`gemini-nano-banana-2.1`)](nano-banana-2-1.md)**: Primary recommended creative workhorse built on Gemini 3.6 Flash (`512px`/`1K`/`2K`/`4K`, 14 aspect ratios with panoramic seam elimination, `minimal`/`medium`/`high` thinking levels, Google Web + Image Search grounding, mask-based editing, and up to 14 reference anchors).
- **[Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`)](nano-banana-2-lite.md)**: Low-latency (<2s), high-throughput model (`1K` resolution across 14 aspect ratios).
- **[Nano Banana 2 (`gemini-3.1-flash-image`)](nano-banana-2.md)**: Multimodal creative model with `512px`/`1K`/`2K`/`4K` output, 14 aspect ratios, and Google Web + Image Search grounding.
- **[Nano Banana Pro (`gemini-3-pro-image`)](nano-banana-pro.md)**: Studio asset production, 4K rendering, multi-reference consistency (up to 14 anchors: 6 objects, 5 characters, 3 styles), and default pre-generation thinking.

---

## Reference Images & 2-Step Game Sprite Consistency Anchors

Pass reusable reference images (Step 1 character turnaround sheets, style targets, or tileset templates) to `uv run skills/nano-banana/scripts/banana.py` or `gemini-api image` using repeatable `-i` (`--input-image` / `--input`) flags.

In `agy-game-studio`, pair `nano-banana` with `sprite-design` by generating a Step 1 character reference sheet first, then passing `-i character_sheet.png` to lock character identity, proportions, and color ramps across Step 2 `4x4` chroma-key sprite grids:

```bash
# Using uv run skills/nano-banana/scripts/banana.py (supports Vertex AI ADC and GEMINI_API_KEY)
uv run skills/nano-banana/scripts/banana.py \
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
