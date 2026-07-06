---
name: google-blog-style
description: >
  Official style guide and compliance rules for the Google Developers Blog. Activate to draft, edit, and validate technical articles to ensure they meet legal standards, the correct professional tone, and readability targets (Gunning Fog Index).
---

# Google Blog Style Guide

Use this skill to draft, edit, and validate technical articles for official Google Developer blogs.

## Core Mandates
1. **Readability First**: Always check your work with `scripts/fog.cjs`. Target a Gunning Fog Index between **12 and 15** (Professional/Technical).
2. **Deterministic Tooling**: Run the sanitization scripts to ensure code safety and legal compliance.
3. **Inclusive Language**: Avoid niche jargon unless it is widely understood globally. See `references/style_guide/jargon.md`.
4. **Legal Safety**: Do not make unsubstantiated claims or discuss future roadmaps. Follow `references/legal_guidelines.md`.

## Workflow

### 1. Plan & Outline
**Before writing:**
1. **Define Goals**: Identify the key takeaway and target audience.
2. **Consult Guides**:
   - `references/writing_guide.md` (Tone and Structure).
   - `references/nomenclature_tags.md` (Correct tagging).
3. **Outline**: Use `assets/template.md` as a structural starting point.

### 2. Draft & Edit
1. **Write**: Focus on clarity, enthusiasm, and technical accuracy.
   - Use sentence case for all headings.
   - Use `references/style_guide/` for terms and formatting.
2. **Modularize**: Keep `SKILL.md` brief by putting detailed docs in the `references/` folder.
3. **Refine**: Ensure the call to action is clear and all placeholder links use `example.com`.

### 3. Review & Validate (Mandatory)
1. **Readability Check**: Run `node scripts/fog.cjs <path-to-draft>` on the draft. If the index is over 16, shorten sentences and simplify complex words.
2. **Sanitization**: Run the script to find secrets, personal data, and legal risks:
   ```bash
   node scripts/sanitize_blog.cjs <path-to-file>
   ```
3. **Legal Review**: Manually check against `references/legal_guidelines.md`:
   - Do not mention unreleased features or future timelines.
   - Do not use superlatives ("best", "fastest") or possessives on product names.

## Resources
- **Template**: `assets/template.md`
- **Sanitizer**: `scripts/sanitize_blog.cjs`
- **Guides**:
  - `references/writing_guide.md`
  - `references/legal_guidelines.md` (CRITICAL)
  - `references/style_guide/` (Comprehensive style reference)
  - `references/nomenclature_tags.md`