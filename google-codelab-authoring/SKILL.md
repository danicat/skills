---
name: google-codelab-authoring
description: >
  Definitive guide for authoring high-quality Google Codelabs. Activate to enforce the .lab.md format specifications, metadata requirements (duration, authors), and provide validation tools for structural correctness.
---

# Google Codelab Authoring

Use this skill to write high-quality Google Codelabs (`.lab.md`).

## Core Rules
1. **Target Readability**: Keep the Gunning Fog Index below 12. Run `scripts/fog.cjs` to check it.
2. **Validate Structure**: Run `scripts/validate_codelab.cjs` before you finish.
3. **Use Simple Words**: Avoid jargon. See `references/style_guide/jargon.md` and `references/style_guide/inclusive-documentation.md`.
4. **Action-Oriented Steps**: Give clear, active steps. Do not use words like "just" or "simply".

## Workflow

### 1. Plan
**Before you write:**
1. **Scope**: Check `references/content_recommendations.md`.
2. **Audience**: See `references/writing_guide.md` for tone.
3. **Language**: Choose **Polyglot** (best) or **Block Includes**. See `references/polyglot.md`.

### 2. Start
1. **Template**: Read `assets/template.lab.md`.
2. **Create File**: Write your `.lab.md` using that template.
3. **Metadata**: Add `id`, `description`, `authors`, and `duration` to the frontmatter.

### 3. Write
Follow Google Developer style guides.
- **Layout**: Follow `references/formatting_guide.md` for titles and step times (`Duration: MM:SS`).
- **Style**: Use `references/style_guide/` (e.g., `voice.md`, `procedures.md`).
- **Markup**: Use `> aside positive/negative` for notes and `console` code blocks for terminal output.

### 4. Verify
**You must validate your work before you finish.**
1. **Check Fog**: Run `node scripts/fog.cjs <file>`. If the score is over 12, simplify the text.
2. **Check Structure**: Run `node scripts/validate_codelab.cjs <file>`.
3. **Fix Errors**: Correct any issues the scripts find.
4. **Final Check**: Review `references/review.md`.

## Common Tasks

- **Step Time**: Put `Duration: MM:SS` right after a `## Step Title`.
- **Alerts**: Use `> aside positive` (tips) or `> aside negative` (warnings).
- **Terminal**: Use fenced code blocks with the `console` language.
- **Code**: Use standard fenced code blocks (e.g., `java`, `python`).

## Files
- **Template**: `assets/template.lab.md`
- **Checkers**: 
  - `scripts/validate_codelab.cjs` (Structure)
  - `scripts/fog.cjs` (Readability)
- **Guides**:
  - `references/formatting_guide.md` (Syntax)
  - `references/writing_guide.md` (Tone)
  - `references/style_guide/` (Google Style Guide)
  - `references/review.md` (Review Lists)
  - `references/polyglot.md` (Multi-language)