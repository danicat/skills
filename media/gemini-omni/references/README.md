# Gemini Omni Reference Index

This directory contains technical documentation for Google's **Gemini Omni** multimodal video generation, conversational video editing, frame interpolation, video extension, and video upscaling models via the **Interactions API**:

- **[gemini-omni-1-2-flash.md](gemini-omni-1-2-flash.md)**: Complete specification for **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`), covering `uv run scripts/omni.py` CLI workflows, Vertex AI / Gemini Enterprise (`global` location) ADC authentication, `3s` to `15s` video generation with native synchronized audio, natural-language reference binding (up to 6 to 10 reference images and up to 3 reference videos), standalone video upscaling (`task: "upscale"`), multi-turn editing and extension, and Python SDK integration.
- **[gemini-omni-1-1-flash.md](gemini-omni-1-1-flash.md)**: Technical specification and migration guide for `gemini-omni-1.1-flash` (`3s` to `10s` clips, transitioning automatically to `gemini-omni-1.2-flash` on December 3, 2026).
