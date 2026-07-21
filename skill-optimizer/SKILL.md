---
name: skill-optimizer
description: >
  Analyze, write, and optimize Agent Skills (SKILL.md files, frontmatter descriptions, and folder structures). Use this skill when reviewing existing skills, drafting new skills, or troubleshooting triggering issues, even if the user just asks to "improve" or "review" their skills.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
---

# Agent Skill Optimizer

This skill provides step-by-step procedures, templates, and gotchas to analyze, write, and optimize Agent Skills. 

## Quick Reference
Before starting any optimization or creation task, review the core specifications:
- `SKILL.md` must have valid YAML frontmatter containing `name`, `description`, and optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`).
- The `name` must be 1-64 characters, lowercase alphanumeric + hyphens, and match the parent directory name exactly.
- The `description` has a hard limit of 1024 characters.

---

## Workflow for Skill Analysis and Optimization

Follow this step-by-step procedure to analyze and optimize any skill:

### Step 1: Scan and Audit Folder Structure
Examine the skill's root directory. A well-designed skill should structure its assets for **progressive disclosure**:
1. **Metadata** (loaded at startup): `name` and `description` in frontmatter.
2. **Core Instructions** (< 500 lines / 5,000 tokens): Standard inline guidelines inside `SKILL.md`.
3. **Deep References** (loaded on-demand): Detailed documentation in `references/` or `assets/`.
4. **Logic & Automation**: Scripts in `scripts/` to handle repetitive tasks.

### Step 2: Audit and Optimize the Description
Check the YAML frontmatter `description` field against these rules:
- [ ] Is it written in **imperative phrasing**? (e.g., *"Use this skill when..."* instead of *"This skill does..."*)
- [ ] Does it focus on **user intent** rather than implementation details?
- [ ] Is it **pushy and explicit** about boundaries? (e.g., *"Use this skill even if they don't explicitly mention 'CSV' or 'analysis'."*)
- [ ] Is it concise and strictly under the **1024-character** limit?

### Step 3: Trim Over-Verbose Instructions
Look for sections explaining concepts the agent already knows:
- Cut definitions of standard technologies, file formats, or APIs (e.g., explaining what JSON, HTTP, Git, or SQL is).
- Keep only project-specific guidelines, schemas, and non-obvious rules.
- Ask: *"Would the agent get this wrong without this instruction?"* If the answer is no, delete it.

### Step 4: Calibrate Control and Options
Verify that the skill does not confuse the agent with too many choices:
- Ensure the instructions provide **clear defaults** rather than open-ended menus (e.g., *"Use pdfplumber for text extraction"* instead of *"You can use pdfplumber, pypdf, or PyMuPDF"*).
- Ensure the instructions focus on **procedures over declarations** (how to approach a class of problems, not specific answers for a single instance).

### Step 5: Incorporate Best Instruction Patterns
Determine if the skill would benefit from:
- **Gotchas Section**: Real, project-specific, non-obvious quirks that defy reasonable assumptions (soft deletes, ID naming variations across services, mock behaviors).
- **Checklists**: Explicit markdown checklists for multi-step workflows.
- **Output Format Templates**: Concrete markdown or JSON templates of what to produce.
- **Validation Loops**: Instructions directing the agent to do work, run a validation command/script, fix errors, and repeat.

---

## Gotchas in Skill Design

- **The Kitchen Sink Trap**: Do not inline massive tables, API schemas, or multi-page documentation in the main `SKILL.md`. Always move them to `references/` or `assets/` and use progressive disclosure to tell the agent *exactly* when to read them.
- **Passive Descriptions**: Descriptions that begin with *"This skill helps with..."* or *"A collection of scripts..."* fail to trigger. Change them to *"Use this skill when the user wants to..."* or *"Activate this skill when..."*.
- **Over-constraining the Agent**: Do not prescribe rigid, multi-command bash sequences for flexible tasks where multiple approaches are valid. Only use highly prescriptive instructions for fragile, destructive, or highly consistent workflows (e.g., DB migrations).
- **Naming Discrepancies**: The `name` field in the frontmatter must perfectly match the name of the folder on disk.

---

## Skill Review Output Template

When providing an optimization proposal report to a user, format it using the following template to maintain clean, professional, and readable structure:

```markdown
# Optimization Proposal for `[skill-name]`

## 1. Frontmatter & Trigger Description Review
**Current Description:**
`[Insert current description]`

**Critique:**
- `[Critique point 1 (e.g., passive tone, lacks user intent, near-miss concerns)]`
- `[Critique point 2]`

**Proposed Description:**
```yaml
description: >
  [Insert newly written, imperative, pushy, and intent-focused description]
```

---

## 2. Structure & Progressive Disclosure Review
- **Current Structure:** `[List directories/files found]`
- **Proposed Reorganization:**
  - `[Recommendation for moving large sections to references/ if applicable]`
  - `[Recommendation for bundling repetitive agent logic into scripts/ if applicable]`

---

## 3. Instruction & Content Optimization
- **What to Trim:**
  - `[Specific sections or explanations to remove because the agent already knows them]`
- **What to Refine:**
  - `[Where to match specificity to fragility, provide defaults over menus, or use procedures over declarations]`

---

## 4. Recommended Instruction Patterns
- **Gotchas:**
  - `[Propose specific gotchas that should be added to prevent agent errors]`
- **Templates / Checklists / Validation Loops:**
  - `[Draft any recommended checklists, validation loops, or output format templates]`
```

---

## Validation Loop for Skill Creators

1. Draft the `SKILL.md` frontmatter and instructions.
2. If the `skills-ref` utility is available locally, run validation:
   ```bash
   skills-ref validate ./[skill-name]
   ```
3. Read the output. If validation fails or reports schema warnings:
   - Correct the YAML structure or naming mismatch.
   - Run validation again.
4. Review the drafted description against the 1024-character limit:
   ```bash
   wc -c << 'EOF'
   [Your description content here]
   EOF
   ```
