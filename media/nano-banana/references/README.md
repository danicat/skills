# Reference Images & Consistency Anchors

This directory stores reference images for character, subject, and style consistency when generating or editing images with Nano Banana models.

## Usage
Place reference images (characters, mascots, brand assets, style examples) in this directory or reference them from your local project paths.

Pass reference images to `scripts/banana.py` using `-i` or `--input-image`:

```bash
uv run scripts/banana.py \
  -p "Our mascot in a pilot jacket flying a vintage biplane" \
  -f "pilot_mascot.png" \
  -i "references/mascot.png" \
  -m "nano-banana-pro"
```
