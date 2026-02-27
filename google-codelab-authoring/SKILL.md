---
name: google-codelab-authoring
description: >
  Definitive guide for authoring high-quality Google Codelabs. Activate to enforce the .lab.md format specifications, metadata requirements (duration, authors), and provide validation tools for structural correctness.
---

# Google Codelab Authoring

This skill guides the end-to-end creation of high-quality Google Codelabs (`.lab.md`).

## Core Mandates
1. **Readability First**: Always check your work with the `scripts/fog.cjs` script. Target a Gunning Fog Index < 12 (General Audience).
2. **Deterministic Tooling**: Use `scripts/validate_codelab.cjs` to catch structural errors before finalizing.
3. **Inclusive Language**: Avoid niche jargon. Refer to `references/style_guide/jargon.md` and `references/style_guide/inclusive-documentation.md`.
4. **Step-by-Step Clarity**: Every instruction must be actionable. Avoid "just" or "simply".

## Workflow

### 1. Plan & Design
**Before generating any code or text:**
1. **Define Scope**: Consult `references/content_recommendations.md`.
2. **Identify Audience**: Use `references/writing_guide.md` to set the tone.
3. **Choose Language Strategy**: Decide between **Polyglot** (preferred) or **Block Includes**. See `references/polyglot.md`.

### 2. Initialize
1. **Read Template**: Load `assets/template.lab.md`.
2. **Create File**: Generate the `.lab.md` file using the template as a base.
3. **Configure Metadata**: Fill in `id`, `description`, `authors`, and `duration` in the YAML frontmatter.

### 3. Write & Format
Refer to the guides to ensure compliance with Google Developer standards.
- **Structure**: Follow `references/formatting_guide.md` for headings, steps, and duration (`Duration: MM:SS`).
- **Style**: Consult `references/style_guide/` for specific questions (e.g., `voice.md`, `procedures.md`).
- **Components**: Use `> aside positive/negative` for notes and `console` code blocks for terminal output.

### 4. Review & Validate (Mandatory)
**Never mark a task as complete without validation.**
1. **Readability Check**: Run `node scripts/fog.cjs <path-to-file>`. If > 12, simplify the language.
2. **Structural Check**: Run `node scripts/validate_codelab.cjs <path-to-file>`.
3. **Self-Correction**: Fix any errors reported by the scripts.
4. **Quality Review**: Check against `references/review.md`.

## Common Tasks

- **Add Duration**: `Duration: MM:SS` goes *immediately* after a `## Step Title`.
- **Info Boxes**: Use `> aside positive` (tips) or `> aside negative` (warnings).
- **Terminal Output**: Use fenced code blocks with the `console` language identifier.
- **Code Snippets**: Use fenced code blocks with the appropriate language (e.g., `java`, `python`).

## Resources
- **Template**: `assets/template.lab.md`
- **Validators**: 
  - `scripts/validate_codelab.cjs` (Structure)
  - `scripts/fog.cjs` (Readability)
- **Guides**:
  - `references/formatting_guide.md` (Syntax & Structure)
  - `references/writing_guide.md` (Tone & Audience)
  - `references/style_guide/` (Official Google Developer Style Guide)
  - `references/review.md` (Quality Checklists)
  - `references/polyglot.md` (Multilanguage Support)