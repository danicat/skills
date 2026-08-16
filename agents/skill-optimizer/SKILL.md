---
name: skill-optimizer
description: >
  Analyze, author, and optimize Agent Skills according to the official Agent Skills specification. Activate when creating new skills, auditing existing skills, optimizing trigger descriptions, designing eval suites (evals.json), bundling self-contained scripts, configuring the agentskills MCP server (https://agentskills.io/mcp), or organizing progressive disclosure structures (scripts/, references/, assets/, evals/). Use whenever reviewing, refactoring, or grading skills.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
---

# Agent Skill Optimizer

Procedures, evaluation loops, and standards for creating and optimizing agent skills according to the Agent Skills specification.

---

## Skill Architecture & Progressive Disclosure

Skills use progressive disclosure to minimize context overhead:
1. Metadata (~100 tokens): `name` and `description` in YAML frontmatter, loaded at startup for all skills.
2. Instructions (< 5,000 tokens / < 500 lines): The main `SKILL.md` body, loaded only when the skill activates.
3. Resources (on-demand): Subdirectories loaded only when explicitly referenced:
   - `scripts/`: Executable code for automation and repetitive tasks.
   - `references/`: Domain documentation, schemas, and API guides (referenced relative to skill root).
   - `assets/`: Static templates, examples, and data files.
   - `evals/`: Test cases and assertion datasets (`evals.json`).

---

## Frontmatter Specification & Rules

Every skill requires valid YAML frontmatter:

```yaml
---
name: my-skill
description: >
  Use this skill when...
license: Apache-2.0
compatibility: Requires Node.js 20+ and git
metadata:
  author: organization-or-name
  version: "1.0.0"
allowed-tools: Bash(git:*) Read
---
```

Constraints:
- `name` (required): 1-64 characters, lowercase alphanumeric and single hyphens (`a-z`, `0-9`, `-`). No consecutive hyphens (`--`), no leading/trailing hyphens. Must match directory name exactly.
- `description` (required): 1-1024 characters. Non-empty. Must define what the skill does and under what specific conditions to activate.
- `license` (optional): Short license identifier (e.g., `Apache-2.0`, `MIT`).
- `compatibility` (optional): Max 500 characters. Environment or tool requirements. Omit if standard.
- `metadata` (optional): Key-value string map for custom metadata.
- `allowed-tools` (optional): Space-separated list of pre-approved tools.

---

## Agent Skills MCP Server Setup

Connect the official Agent Skills MCP server to query live specifications, documentation, and best practice guides directly during development.

### Endpoint
- Server URL: `https://agentskills.io/mcp`

### Configuration

Add the server to your agent's MCP configuration file (e.g., `~/.gemini/config/mcp_config.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agentskills": {
      "url": "https://agentskills.io/mcp"
    }
  }
}
```

### Available MCP Tools
- `search_agent_skills`: Search the Agent Skills knowledge base with natural language queries to locate relevant guides and examples.
- `query_docs_filesystem_agent_skills`: Run shell commands (`tree /`, `cat /specification.mdx`, `rg`, `head`) against the virtual documentation filesystem.
- `submit_feedback`: Report doc issues or omissions directly to the Agent Skills documentation team.

---

## Skill Audit & Optimization Workflow

Follow this 5-stage procedure when reviewing or refining skills:

### Stage 1: Specification & Structure Audit
- Confirm `name` matches folder name and adheres to naming rules.
- Verify `SKILL.md` line count is under 500 lines.
- Ensure large documentation (> 100 lines) or static data is moved to `references/` or `assets/`.
- Ensure all intra-skill file links use paths relative to the skill root (e.g., `references/guide.md`, `scripts/run.py`).

### Stage 2: Description & Trigger Optimization
Review the frontmatter `description` against these principles:
- Imperative framing: Start with "Use this skill when..." or "Activate this skill whenever...".
- Intent-focused: Describe user objectives rather than internal code mechanics.
- Pushy boundary definition: Explicitly capture implied intent (e.g., "even if the user does not explicitly mention...").
- Concise: Pack high-signal keywords and trigger triggers within the 1024-character budget.

### Stage 3: Instruction Density & Context Calibration
- Omit baseline knowledge: Cut explanations of standard technologies (HTTP, JSON, Git, basic syntax).
- Add domain delta: Keep project conventions, specific API patterns, and non-obvious constraints.
- Provide defaults, not menus: Pick one recommended tool or approach as the default; mention alternatives only as fallback escapes.
- Procedures over declarations: Teach reusable problem-solving workflows rather than hardcoded single-instance solutions.
- Match specificity to fragility: Allow freedom for flexible review tasks; use strict, numbered sequences for fragile or destructive operations.

### Stage 4: Script Design & Bundling
When bundling scripts into `scripts/`:
- Non-interactive execution: Never prompt for TTY input; accept flags, environment variables, or stdin.
- Self-contained dependencies: Declare dependencies inline using standard runtimes:
  - Python: PEP 723 script metadata (`# /// script ... # ///`) executed via `uv run` or `pipx`.
  - TypeScript/JavaScript: Deno (`deno run`) with `npm:` specifiers or Bun (`bun run`).
  - Ruby: `bundler/inline` (`require 'bundler/inline'`).
- Clean interfaces: Provide `--help` with brief options and examples.
- Structured output: Write clean machine-readable data (JSON/CSV) to stdout; write logs and progress to stderr.
- Actionable errors: Explain what failed, expected formats, and recovery steps.
- Safe operations: Support `--dry-run` and idempotent execution for stateful or destructive commands.

### Stage 5: Instruction Patterns
Enhance skills with proven structural patterns:
- Gotchas: Document environment quirks, schema oddities, or non-obvious failure modes in `SKILL.md`.
- Output Templates: Provide concrete Markdown or JSON structures for expected outputs.
- Workflow Checklists: Use markdown task lists (`- [ ] Step 1...`) for multi-stage processes.
- Validation Loops: Require the agent to run a validator script or checklist, inspect errors, fix issues, and iterate until passing.
- Plan-Validate-Execute: For batch or high-risk tasks, require generating a structured plan file, validating against schema/truth, and executing only after validation passes.

---

## Trigger Evaluation & Description Tuning

To systematically test and optimize triggering accuracy:

1. Build Query Dataset: Create ~20 realistic user queries (split 60% train / 40% validation):
   - Should-trigger (8-10): Varied phrasing, detail levels, casual prompts, and implicit tasks without explicit keywords.
   - Should-not-trigger (8-10): Near-miss queries that share keywords but require different capabilities.
2. Run Eval Loop: Execute queries across multiple runs (3x per query) to compute trigger rates.
3. Optimize on Train Set: Broaden scope if positives fail; add boundary exclusions if negatives false-trigger.
4. Validate Generalization: Test final candidate against the untouched validation split. Ensure character count remains $\le 1024$.

---

## Output Quality Evaluation (`evals/evals.json`)

Structure output quality evals inside `evals/evals.json`:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Realistic prompt with context and file paths",
      "expected_output": "Description of success",
      "files": ["evals/files/input.csv"],
      "assertions": [
        "The output file exists and contains valid JSON",
        "The summary table contains exactly 4 columns",
        "The generated report includes actionable recommendations"
      ]
    }
  ]
}
```

Evaluation Principles:
- Baseline comparison: Run test cases with skill (`with_skill/`) vs without skill or prior version (`without_skill/` / `old_skill/`).
- Objective assertions: Grade against concrete, verifiable criteria with quoted evidence for passes and fails.
- Delta analysis: Calculate pass rate gain versus token overhead and latency cost.
- Human review: Inspect execution transcripts to remove wasted agent turns or clarify ambiguous instructions.

---

## Skill Review Output Template

When reporting a skill review or optimization proposal:

```markdown
# Optimization Proposal for `[skill-name]`

## 1. Frontmatter & Trigger Review
**Current Description:**
`[Insert current description]`

**Critique & Improvements:**
- `[Trigger accuracy, boundary clarity, character count]`

**Proposed Frontmatter:**
```yaml
name: [skill-name]
description: >
  [Imperative, pushy, intent-focused description <= 1024 chars]
```

## 2. Progressive Disclosure & Structure
- **Current Layout:** `[Files and line counts]`
- **Proposed Layout:** `[Move large docs to references/, scripts to scripts/, templates to assets/]`

## 3. Instruction & Content Refinement
- **Omissions:** `[Basic knowledge to trim]`
- **Defaults & Procedures:** `[Defaults established, reusable workflows]`
- **Patterns Added:** `[Gotchas, checklists, validation loops, output templates]`

## 4. Scripts & Tooling
- `[Script dependency declarations, CLI flags, output formatting]`
```
