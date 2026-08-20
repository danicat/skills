---
name: skill-optimizer
description: >
  Analyze, author, evaluate, and optimize Agent Skills according to the official
  Agent Skills specification. Activate when creating new skills, auditing
  existing skills, installing reference tools like skill-creator via npx skills
  add, optimizing trigger descriptions with train/validation splits, designing
  eval suites (evals.json), setting up blind comparisons, bundling
  self-contained scripts (PEP 723 / Deno / Bun), configuring the agentskills MCP
  server (https://agentskills.io/mcp), or organizing progressive disclosure
  structures (scripts/, references/, assets/, evals/). Use whenever reviewing,
  refactoring, or grading skills.
license: Apache-2.0
metadata:
  category: agents
  tags: "agents, skill-optimizer, evals, benchmarks, testing, authoring, specification"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.2"
  homepage: https://skills.danicat.dev/agents/skill-optimizer/
  canonical: https://skills.danicat.dev/agents/skill-optimizer/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/agents/skill-optimizer
---

# Agent Skill Optimizer

Procedures, evaluation loops, and standards for authoring, auditing, and optimizing Agent Skills according to the Agent Skills specification and official best practices.

---

## Skill Architecture & Progressive Disclosure

Skills use progressive disclosure to minimize context consumption:
1. **Metadata** (~100 tokens): `name` and `description` in YAML frontmatter, loaded at startup for all skills.
2. **Instructions** (< 5,000 tokens / < 500 lines): The main `SKILL.md` body, loaded only when the skill activates.
3. **Resources** (Loaded on demand): Subdirectories loaded only when explicitly triggered by instructions:
   - `scripts/`: Executable code for automation and repetitive tasks.
   - `references/`: Domain documentation, schemas, and API guides (kept 1 level deep from skill root).
   - `assets/`: Static templates, examples, and data files.
   - `evals/`: Test cases, assertion datasets (`evals.json`), and test fixtures (`evals/files/`).

---

## Installing Skills via `npx skills` CLI

The official and standard package manager for agent skills is the **`skills`** CLI ([skills.sh](https://skills.sh)):

### Quick Commands

```bash
# Install a specific skill from a repository (project-level)
npx skills add anthropics/skills --skill skill-creator

# Install a skill globally (user-level)
npx skills add anthropics/skills --skill skill-creator -g

# Install non-interactively (skip confirmation prompts)
npx skills add anthropics/skills --skill skill-creator -g -y

# List available skills inside a repository without installing
npx skills add anthropics/skills --list

# Interactively search for skills
npx skills find

# List currently installed skills
npx skills list -g
```

---

## Official Reference Skill: `skill-creator`

The official reference implementation for skill creation and automated evaluation from Anthropic is **`skill-creator`** ([anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator)).

### 1-Line Installation
```bash
# Global installation (recommended)
npx skills add anthropics/skills --skill skill-creator -g -y

# Local workspace installation
npx skills add anthropics/skills --skill skill-creator -y
```

*(Alternatively in Claude Code: `/plugin install skill-creator@claude-plugins-official`)*

### How `skill-creator` Works
- **Scaffolding**: Prompts interactively to generate new skill skeletons conforming to naming and directory conventions.
- **Eval Runner**: Executes test prompts against `evals/evals.json`, runs blind comparisons across iterations, and computes pass rates in HTML/JSON reports.
- **Description Optimizer**: Automates description evaluations with train/validation splits to tune trigger rates.

---

## Frontmatter Specification & Hard Constraints

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

### Validation Rules
- `name` (required): 1-64 characters, lowercase alphanumeric and single hyphens (`a-z`, `0-9`, `-`). No consecutive hyphens (`--`), no leading/trailing hyphens. Must match directory name exactly.
- `description` (required): 1-1024 characters. Non-empty. Must define what the skill does and under what specific conditions to activate.
- `license` (optional): Short license identifier (e.g., `Apache-2.0`, `MIT`) or path to a bundled license.
- `compatibility` (optional): Max 500 characters. Environment or tool requirements. Omit if standard.
- `metadata` (optional): Key-value string map for custom metadata.
- `allowed-tools` (optional): Space-separated list of pre-approved tools (experimental).

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

## 5-Stage Skill Audit & Optimization Workflow

Follow this procedure when reviewing or refining skills:

### Stage 1: Specification & Structure Audit
- Confirm `name` matches folder name and adheres to naming rules.
- Verify `SKILL.md` line count is under 500 lines and under 5,000 tokens.
- Ensure large documentation (> 100 lines) or static data is moved to `references/` or `assets/`.
- Verify all intra-skill file links use paths relative to the skill root (e.g., `references/guide.md`, `scripts/run.py`).
- Ensure conditional triggers tell the agent *when* to load each reference file (e.g., "Read `references/api-errors.md` if the API returns a non-200 status code").

### Stage 2: Description & Trigger Optimization
Review the frontmatter `description` against these principles:
- **Imperative framing**: Start with "Use this skill when..." or "Activate this skill whenever...".
- **Intent-focused**: Describe user objectives rather than internal code mechanics.
- **Pushy boundary definition**: Explicitly capture implied intent (e.g., "even if the user does not explicitly mention...").
- **Concise**: Pack high-signal keywords and triggers within the 1024-character budget.

### Stage 3: Instruction Density & Context Calibration
- **Omit baseline knowledge**: Cut explanations of standard technologies (HTTP, JSON, Git, basic language syntax).
- **Add domain delta**: Keep project conventions, specific API patterns, and non-obvious constraints.
- **Provide defaults, not menus**: Pick one recommended tool or approach as the default; mention alternatives only as fallback escapes.
- **Procedures over declarations**: Teach reusable problem-solving workflows rather than hardcoded single-instance solutions.
- **Match specificity to fragility**: Allow freedom for flexible review tasks; use strict, numbered sequences for fragile or destructive operations.

### Stage 4: Script Design & Bundling
When bundling scripts into `scripts/`:
- **Non-interactive execution**: Never prompt for TTY input; accept flags, environment variables, or stdin.
- **Self-contained dependencies**: Declare dependencies inline using standard runtimes:
  - Python: PEP 723 script metadata (`# /// script ... # ///`) executed via `uv run` or `pipx`.
  - TypeScript/JavaScript: Deno (`deno run`) with `npm:` specifiers or Bun (`bun run`).
  - Ruby: `bundler/inline` (`require 'bundler/inline'`).
- **Clean interfaces**: Provide `--help` with brief options and examples.
- **Structured output**: Write clean machine-readable data (JSON/CSV) to stdout; write logs and progress to stderr.
- **Actionable errors**: Explain what failed, expected formats, and recovery steps.
- **Safe operations**: Support `--dry-run` and idempotent execution for stateful or destructive commands.

### Stage 5: Proven Instruction Patterns
Enhance skills with proven structural patterns:
- **Gotchas sections**: Document environment quirks, schema oddities, or non-obvious failure modes in `SKILL.md`.
- **Output Templates**: Provide concrete Markdown or JSON structures for expected outputs.
- **Workflow Checklists**: Use markdown task lists (`- [ ] Step 1...`) for multi-stage processes.
- **Validation Loops**: Require the agent to run a validator script or checklist, inspect errors, fix issues, and iterate until passing.
- **Plan-Validate-Execute**: For batch or high-risk tasks, require generating a structured plan file, validating against schema/truth, and executing only after validation passes.

---

## Trigger Evaluation & Description Tuning (Train/Val Splits)

To systematically test and optimize triggering accuracy without overfitting:

1. **Build Query Dataset**: Create ~20 realistic user queries:
   - **Should-trigger (8-10)**: Varied phrasing, casual prompts, complex multi-step workflows, and implicit tasks without explicit keywords.
   - **Should-not-trigger (8-10)**: Near-miss queries that share keywords or concepts but require different capabilities.
2. **Train/Validation Split**:
   - **Train Set (~60%)**: Used to identify failures and guide description tweaks.
   - **Validation Set (~40%)**: Set aside and used exclusively to check if improvements generalize.
3. **Run Trigger Eval**:
   - Execute queries 3x each to compute **Trigger Rate** ($\text{triggers} / \text{runs}$).
   - A should-trigger query passes if trigger rate $\ge 0.5$.
   - A should-not-trigger query passes if trigger rate $< 0.5$.
4. **Optimize on Train Set Only**: Broaden scope if positives fail; add boundary exclusions if negatives false-trigger. Avoid keyword stuffing.
5. **Verify on Validation Set**: Select the iteration with highest validation pass rate. Ensure description stays $\le 1024$ characters.

---

## Output Quality Evaluation (`evals/evals.json`) & Blind Comparison

Structure test cases inside `evals/evals.json`:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Realistic user prompt with specific context and paths",
      "expected_output": "Description of what success looks like",
      "files": ["evals/files/input_sample.json"],
      "assertions": [
        "The output file exists and contains valid JSON",
        "The summary table contains exactly 4 columns",
        "The generated report includes actionable recommendations"
      ]
    }
  ]
}
```

### Eval Workspace Directory Structure

```
my-skill-workspace/
└── iteration-1/
    ├── eval-case-1/
    │   ├── with_skill/
    │   │   ├── outputs/       # Generated files
    │   │   ├── timing.json    # {"total_tokens": 84000, "duration_ms": 22000}
    │   │   └── grading.json   # Assertion results with quoted evidence
    │   └── without_skill/     # (or old_skill/ for version comparisons)
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    └── benchmark.json         # Aggregated pass rates, tokens, latency, and delta
```

### Grading & Blind Comparison Principles
- **Require Concrete Evidence for PASS**: Never give the benefit of the doubt. Cite or quote the exact output text/file in `grading.json`.
- **Blind Comparison for Qualitative Nuance**: When comparing two skill versions (e.g. `old_skill` vs `new_skill`), present both outputs to an LLM judge without revealing which version produced which output. The judge evaluates holistic criteria (depth, clarity, ergonomics, formatting) without bias.
- **Delta Analysis**: Calculate delta in pass rate vs token and duration overhead in `benchmark.json`.
