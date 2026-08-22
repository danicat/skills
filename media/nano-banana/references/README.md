# Nano Banana References & Model Cards

This directory contains technical model cards, capability specifications, resolution matrices, and guidance for storing consistency anchors and reference images.

## Model Cards & Technical References

- **[Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`)](references/nano-banana-2-lite.md)**: Ultra-low latency (<2s), high-throughput default model (1K resolution).
- **[Nano Banana 2 (`gemini-3.1-flash-image`)](references/nano-banana-2.md)**: General-purpose creative workhorse with 4K output, 14 aspect ratios, and Google Search / Image Search grounding.
- **[Nano Banana Pro (`gemini-3-pro-image`)](references/nano-banana-pro.md)**: Studio asset production, 4K rendering, multi-reference consistency (up to 14 anchors: 6 objects, 5 characters, 3 styles), and pre-generation thinking.
- **[Nano Banana (`gemini-2.5-flash-image`)](references/nano-banana.md)**: Foundational model specifications, parameters, and migration roadmap.

---

## Reference Images & Consistency Anchors

Place reusable reference images (characters, mascots, style targets, product templates) in this directory or reference them from your workspace assets.

Pass reference images to `scripts/banana.py` using `-i` or `--input-image`:

```bash
uv run scripts/banana.py \
  -p "Our mascot in a pilot jacket flying a vintage biplane" \
  -f "pilot_mascot.png" \
  -i "references/mascot.png" \
  -m "nano-banana-pro" \
  -r "4K"
```
