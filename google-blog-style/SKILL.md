---
name: google-blog-style
description: >
  Official style guide and compliance rules for the Google Developers Blog. Activate to draft, edit, and validate technical articles to ensure they meet legal standards, the correct professional tone, and readability targets (Gunning Fog Index).
---

# Google Blog Style Guide

This skill assists in creating high-quality technical blog posts for official Google Developer channels.

## Core Mandates
1. **Readability First**: Always check your work with the `scripts/fog.cjs` script. Target a Gunning Fog Index between **12 and 15** (Professional/Technical).
2. **Deterministic Tooling**: Use the provided sanitization scripts to ensure code safety and legal compliance.
3. **Inclusive Language**: Avoid niche jargon (like gaming metaphors) unless they are widely understood in a global engineering context. Refer to `references/style_guide/jargon.md`.
4. **Legal Safety**: Never make unsubstantiated claims or discuss future roadmaps. Strictly follow `references/legal_guidelines.md`.

## Workflow

### 1. Plan & Outline
**Before writing:**
1. **Define Goals**: Identify the key takeaway and the target technical audience.
2. **Consult Guides**:
   - `references/writing_guide.md` (Tone and Structure).
   - `references/nomenclature_tags.md` (Correct tagging).
3. **Outline**: Use `assets/template.md` as a structural starting point.

### 2. Draft & Edit
1. **Write**: Focus on clarity, enthusiasm, and technical accuracy.
   - Use sentence case for all headings (H2, H3, etc.).
   - Use `references/style_guide/` for terminology and formatting.
2. **Modularize**: Keep the `SKILL.md` clean by moving detailed documentation to the `references/` folder.
3. **Refine**: Ensure the "Call to Action" is clear and all links (using `example.com` for placeholders) are working.

### 3. Review & Validate (Mandatory)
1. **Readability Check**: Run `node scripts/fog.cjs <path-to-draft>` on the draft. If the index is > 16, shorten sentences and simplify complex words.
2. **Sanitization**: Run the script to catch secrets, personal data, and legal risks.
   ```bash
   node scripts/sanitize_blog.cjs <path-to-file>
   ```
3. **Legal Review**: Manually verify against `references/legal_guidelines.md`:
   - No "coming soon" or future roadmaps.
   - No superlatives ("best", "fastest") or possessives on product names.

## Resources
- **Template**: `assets/template.md`
- **Sanitizer**: `scripts/sanitize_blog.cjs`
- **Guides**:
  - `references/writing_guide.md`
  - `references/legal_guidelines.md` (CRITICAL)
  - `references/style_guide/` (Comprehensive style reference)
  - `references/nomenclature_tags.md`