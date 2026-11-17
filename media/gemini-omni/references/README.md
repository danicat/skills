# Gemini Omni reference index

This directory contains technical specifications for Google's **Gemini Omni** multimodal video generation, conversational video editing, frame interpolation, video extension, and video upscaling model via the **Interactions API**:

- **[gemini-omni-1-2-flash.md](gemini-omni-1-2-flash.md)**: Complete specification for **Gemini Omni 1.2 Flash** (`gemini-omni-1.2-flash`), covering `uv run scripts/omni.py` CLI workflows, Gemini Enterprise / Vertex AI (`global` location) and Gemini Developer API authentication, `3s` to `15s` video generation with native synchronized audio, natural-language reference binding (up to 6 to 10 reference images and up to 3 reference videos), standalone video upscaling (`task: "upscale"`), multi-turn editing and extension, and Python SDK integration. Legacy `gemini-omni-1.1-flash` and `gemini-omni-flash-preview` models are deprecated or shut down; migrate all workflows to `gemini-omni-1.2-flash`.
