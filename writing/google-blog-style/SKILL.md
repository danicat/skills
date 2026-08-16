---
name: google-blog-style
description: >
  Official style guide and compliance rules for the Google Developers Blog. Activate to draft, edit, review, and validate technical blog posts, articles, and reviews to ensure they meet legal standards, the correct professional tone, and readability targets.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
---

# Google Blog Style Guide

Use this skill to strictly focus on drafting, editing, and validating technical blog posts, articles, and reviews for official Google Developer blogs.

## Core Mandates
1. **Readability First**: Target a Gunning Fog Index between **12 and 15** (Professional/Technical).
2. **Deterministic Tooling**: Run the validation scripts to ensure code safety and legal compliance.
3. **Inclusive Language**: Avoid niche jargon unless it is widely understood globally. See `references/style_guide/jargon.md`.
4. **Legal Safety**: Do not make unsubstantiated claims or discuss future roadmaps. Follow `references/legal_guidelines.md`.

## Workflow: Strict Plan-Validate-Execute

### 1. Plan
**Before writing:**
1. **Define Goals**: Identify the key takeaway and target audience.
2. **Consult Guides**:
   - `references/writing_guide.md` (Tone and Structure).
   - `references/nomenclature_tags.md` (Correct tagging).
3. **Outline**: Use `assets/template.md` as a structural starting point.
4. **Style Guide Search**: Always use `grep_search` progressively within `references/style_guide/` to confirm specific formatting or brand rules before making assumptions.

### 2. Execute
1. **Write**: Focus on clarity, enthusiasm, and technical accuracy.
   - Use sentence case for all headings.
   - Adhere to rules found via `grep_search` in `references/style_guide/`.
2. **Modularize**: Keep `SKILL.md` brief by putting detailed docs in the `references/` folder.
3. **Refine**: Ensure the call to action is clear and all placeholder links use `example.com`.

### 3. Validate (Mandatory)
> **GOTCHA:** If the `speedgrapher` MCP server is available, you MUST use Speedgrapher's tools and skills (`speedgrapher.vale`, `speedgrapher.fog`, `speedgrapher.slop`) to validate drafts instead of the custom local scripts.

If `speedgrapher` is unavailable, use the following validation scripts:
1. **All-in-One Validation**: Run `node scripts/validate_all.cjs <path-to-draft>` to run style linting, fog checks, and legal checks in one step, outputting a concise Markdown report.
2. **Standalone Checks**:
   - **Linting**: `node scripts/lint_style.cjs <path-to-draft>` (Uses Vale).
   - **Readability**: Run `node scripts/fog.cjs <path-to-draft>`.
   - **Sanitization**: `node scripts/sanitize_blog.cjs <path-to-draft>`.
3. **Legal Review**: Manually check against `references/legal_guidelines.md`.

## Resources
- **Template**: `assets/template.md`
- **Validation**: `scripts/validate_all.cjs`
- **Guides**:
  - `references/writing_guide.md`
  - `references/legal_guidelines.md` (CRITICAL)
  - `references/style_guide/` (Comprehensive style reference)
  - `references/nomenclature_tags.md`