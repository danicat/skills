# Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`) Technical Reference & Migration Guide

`gemini-omni-1.1-flash` is the prior generation Gemini Omni video generation and editing model on the **Interactions API**.

> [!IMPORTANT]
> **Transition to `gemini-omni-1.2-flash` (December 3, 2026 Automatic Routing)**:
> - **Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** is now the default GA model (released November 5, 2026) with `3s` to `15s` clip durations, standalone video upscaling (`task: "upscale"`), improved visual and audio quality, and lower per-token pricing.
> - `gemini-omni-1.1-flash` remains available during a 4-week transition window for backward compatibility. Effective **December 3, 2026**, all requests to `gemini-omni-1.1-flash` automatically route to `gemini-omni-1.2-flash` and are billed at the lower `1.2` rates.
> - On Vertex AI / Gemini Enterprise Agent Platform, `gemini-omni-1.1-flash-preview` is deprecated (`Supported regions: global`); migrate to `gemini-omni-1.2-flash`.

---

## 1. Technical Specifications (`gemini-omni-1.1-flash` vs. `gemini-omni-1.2-flash`)

| Property | `gemini-omni-1.1-flash` | `gemini-omni-1.2-flash` (Recommended) |
| :--- | :--- | :--- |
| **Model IDs** | `gemini-omni-1.1-flash`, `gemini-omni-1.1-flash-preview` | `gemini-omni-1.2-flash` |
| **Supported Region (Vertex AI)** | `global` | `global` |
| **Maximum Input Tokens** | `131,072` tokens | `131,072` tokens |
| **Maximum Output Tokens** | `65,536` tokens (`173,760` on Enterprise) | `65,536` tokens (`260,640` on Enterprise) |
| **Output Clip Duration** | `3s` to `10s` (default `10s`, whole seconds) | `3s` to `15s` (default `10s`, whole seconds; `3s` to `10s` for 2-image interpolation) |
| **Video Extension** | `3s` to `10s` per turn (up to `30s` Gemini API / `40s` Enterprise) | `3s` to `10s` per turn (up to `30s` Gemini API / `40s` Enterprise) |
| **Standalone Video Upscaling** | Not supported | Supported (`task: "upscale"`, `360p -> 720p/1080p`, `720p -> 1080p/4k`) |
| **Reference Images** | Up to `6` in Gemini API (`10` on Enterprise) | Up to `6` in Gemini API (`10` on Enterprise) across `3s` to `15s` |
| **Reference Videos** | Up to `3` (~3s each) for `3s` to `10s` clips | Up to `3` (~3s each) for `3s` to `10s` clips; `1` for `11s` to `15s` clips |
| **Prompt Reference Binding** | Legacy `<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_0>` tags or natural language | Natural language + optional `generation_config.video_config.task` (control tags deprecated) |

---

## 2. Migrating Prompts & Code from `1.1` to `1.2`

1. **Update the Model ID**:
   Replace `"gemini-omni-1.1-flash"` or `"gemini-omni-1.1-flash-preview"` with `"gemini-omni-1.2-flash"` (the default in `uv run scripts/omni.py`).
2. **Replace Angle-Bracket Control Tags with Natural Language**:
   - **Before (`1.1` legacy tags)**:
     `"<FIRST_FRAME> <LAST_FRAME> Smooth camera pan transitioning from dawn to dusk."`
   - **After (`1.2` natural language)**:
     `"Use the first image as the starting frame and the second image as the ending frame. Smooth camera pan transitioning from dawn to dusk."`
3. **Take Advantage of `11s` to `15s` Durations and `--task upscale`**:
   - Set `--duration 15s` for longer single-turn cutscenes without needing multi-turn extension.
   - Use `--task upscale --resolution 1080p` (or `4k`) to upscale `360p` or `720p` drafts.

---

## 3. Running `gemini-omni-1.1-flash` via `scripts/omni.py`

If you need to pin `gemini-omni-1.1-flash` during the transition window before December 3, 2026, pass `--model gemini-omni-1.1-flash` (or `-m 1.1`) with a duration between `3s` and `10s`:

```bash
uv run scripts/omni.py \
  --vertexai \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --model "gemini-omni-1.1-flash" \
  --resolution "1080p" \
  --aspect-ratio "16:9" \
  --duration "10s" \
  --prompt "An aerial tracking shot over glacial fjords at golden hour with gentle orchestral strings." \
  --output "fjords_10s.mp4"
```
