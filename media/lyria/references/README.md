# Lyria 3 references and model cards

This directory contains model cards, capability specifications, arrangement guides, and SDK integration examples for Google's **Lyria 3** music generation models.

## Model cards and technical references

- **[Lyria 3.5 (`lyria-3.5`)](lyria-3-5.md)**: Flagship music generation model for multi-minute songs, structured arrangements, expressive vocals, WAV/MP3 export, and multimodal composition.
- **[Lyria 3 Clip (`lyria-3-clip-preview`)](lyria-3-clip.md)**: Fixed 30-second MP3 music clips, short beds, and rapid style prototyping.
- **[Lyria 3 Pro (`lyria-3-pro-preview`)](lyria-3-pro.md)**: Preview full-length model (up to 184 seconds, MP3) with multi-section structures and timestamp controls.

---

## Composition quick reference

When prompting Lyria models, combine these building blocks:

1. **Genre and style**: Define the musical style (such as `lo-fi hip-hop`, `synthwave`, `chamber orchestra`, `delta blues`).
2. **Instrumentation**: Name lead and rhythm instruments (such as `Rhodes piano`, `808 bass`, `acoustic nylon guitar`, `cello section`).
3. **Tempo and key**: Set musical parameters (such as `120 BPM`, `in D minor`, `slow waltz tempo`).
4. **Vocals vs. instrumental**: Add `"Instrumental only, no vocals"` for clean background beds, or provide bracketed section lyrics (`[Verse 1]`, `[Chorus]`).
5. **Timestamps (Lyria 3.5 and Lyria 3 Pro)**: Use time ranges (`[0:00 - 0:15] Intro...`) to guide section transitions and dynamics.
