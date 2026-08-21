---
name: skill-optimizer
description: >
  Use this skill to author, audit, evaluate, and optimize Agent Skills for maximum reliability, accurate triggering, and high-quality task execution. Activate whenever creating new skills, refining existing instructions, tuning activation descriptions, designing evaluation suites, or auditing skill structures for progressive disclosure. Trigger even if the user does not explicitly mention skill-optimizer.
license: Apache-2.0
metadata:
  category: agents
  tags: "agents, skill-optimizer, evals, benchmarks, testing, authoring, specification"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.3"
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

## Frontmatter Specification, Provenance & Version Control

Every skill must provide valid YAML frontmatter containing complete provenance, versioning, and catalog metadata:

```yaml
---
name: my-skill
description: >
  Use this skill when...
license: Apache-2.0
metadata:
  category: coding
  tags: "coding, golang, refactoring, quality"
  author: Author Name (email@example.com)
  version: "1.0.0"
  homepage: https://skills.danicat.dev/coding/my-skill/
  canonical: https://skills.danicat.dev/coding/my-skill/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/coding/my-skill
compatibility: Requires Go 1.22+
allowed-tools: Bash(go:*) Read
---
```

### Validation & Provenance Rules

#### 1. Core Top-Level Fields
- `name` (required): 1-64 characters, lowercase alphanumeric and single hyphens (`a-z`, `0-9`, `-`). No consecutive hyphens (`--`), no leading/trailing hyphens. Must match directory name exactly.
- `description` (required): 1-1024 characters. Non-empty. Must define what capabilities the skill unlocks and under what specific conditions to activate. Do NOT include internal algorithms or implementation plumbing.
- `license` (required): Short SPDX license identifier (e.g., `Apache-2.0`, `MIT`) or path to a bundled license.
- `compatibility` (optional): Max 500 characters. Environment or tool requirements. Omit if standard.
- `allowed-tools` (optional): Space-separated list of pre-approved tools (experimental).

#### 2. Full Provenance & Version Control (`metadata` Block)
- `category` (required): Functional taxonomy domain (`agents`, `coding`, `game-dev`, `media`, `writing`, `analytics`, `standards`, `gateway`). Must match the parent category folder name.
- `tags` (required): Comma-separated keyword list for search, discovery, and boolean tag filtering.
- `author` (required): Provenance attribution string (e.g., `Author Name (email@domain.com)` or organization name).
- `version` (required): Strict Semantic Versioning SemVer 2.0.0 (`MAJOR.MINOR.PATCH`, e.g., `1.0.0`, `0.3.3`).
  - **Patch (`0.0.X`)**: Clarifications, wording improvements, typo fixes, or internal doc tweaks.
  - **Minor (`0.X.0`)**: Added reference guides, new companion scripts, expanded evals, or new activation triggers.
  - **Major (`X.0.0`)**: Breaking restructuring, incompatible workflow shifts, or major tool replacements.
- `homepage` (required): Canonical web landing page (`https://skills.danicat.dev/<category>/<name>/`).
- `canonical` (required): Authoritative direct URL to the source `SKILL.md` (`https://skills.danicat.dev/<category>/<name>/SKILL.md` or git repository path).
- `repository` (required): Direct link to the source directory in the git repository (`https://github.com/danicat/skills/tree/main/<category>/<name>`).

#### 3. Zero Contamination Gate (Mandatory)
All public skills must be strictly generic, open-source clean, and platform-agnostic:
- **No local machine specifics**: Never include personal machine paths (e.g., hardcoded user directories or home folders).
- **No internal corporate knowledge**: Never include internal project names, internal team/chat references, or proprietary infrastructure URLs.
- **No credentials or tokens**: Never leak API keys, personal access tokens, or private secrets.

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

### Stage 1: Specification, Provenance & Structure Audit
- **Name & Category Alignment**: Confirm `name` matches the folder name and `metadata.category` matches the parent category directory.
- **Provenance Integrity**: Verify `version` adheres to SemVer, and URLs (`homepage`, `canonical`, `repository`) are consistent and accessible.
- **Zero Contamination**: Scan for hardcoded local user paths, internal infrastructure names, or private credentials.
- **Size Constraints**: Verify `SKILL.md` line count is under 500 lines and under 5,000 tokens.
- **Progressive Disclosure**: Ensure large documentation (> 100 lines) or static data is moved to `references/` or `assets/`.
- **Intra-Skill Links**: Verify all intra-skill file links use paths relative to the skill root (e.g., `references/guide.md`, `scripts/run.py`).
- **Conditional Triggers**: Ensure instructions clearly tell the agent *when* to load each reference file.

### Stage 2: Description & Trigger Optimization

The frontmatter `description` is the **only** piece of text loaded by the orchestrator at startup to determine whether to activate the skill. Review and craft the `description` against these core principles:

- **Benefits & Capabilities Over Implementation Details**:
  - Focus strictly on *what capability, superpowers, or problem-solving outcomes* the skill provides.
  - **NEVER** waste description tokens explaining internal code mechanics, algorithms, underlying libraries, or data structures (e.g., do *not* mention "uses BM25 ranking", "implements AST tree walking", "executes regex matching", or "queries SQLite underneath").
  - The orchestrator and user do not care *how* the skill works internally; they care *what user goals it accomplishes* (e.g., "dynamically loads specialized knowledge on demand", "refactors and eliminates Go code smells", "generates procedural chiptune audio").
- **Concrete Activation Criteria & Use Cases**:
  - State specific triggering conditions: user tasks, explicit slash commands (e.g., `/<command>`), implicit intents, and domain scenarios.
- **Pushy Boundary Definition**:
  - Explicitly capture implied intent so the skill triggers whenever relevant (e.g., "Activate this skill whenever the user asks to..., even if they do not explicitly mention <skill-name>").
- **Imperative / Action-Oriented Framing**:
  - Begin directly with "Use this skill when..." or "Activate this skill whenever...".
- **Concise Token Budget**:
  - Pack high-signal keywords and trigger phrases within the 1024-character budget.

#### Contrastive Examples

| Anti-Pattern (Implementation-Heavy ❌) | Best Practice (Outcome & Trigger Focused ✅) |
|---|---|
| *"A CLI tool that uses pure Go BM25 and TF-IDF search algorithms to parse JSON manifests and index markdown files in memory."* | *"Activate this skill to acquire knowledge about anything immediately. Use when the user asks to perform tasks using unknown skills, executes unmapped slash commands, or needs up-to-date domain instructions."* |
| *"Uses AST parser to walk syntax trees, calculate cyclomatic complexity metrics, and run mutation testing."* | *"Use this skill when auditing Go code quality, refactoring complex code, eliminating technical debt, or verifying test suite thoroughness with mutation testing."* |
| *"Runs python-docx and regex to parse docx files into XML AST nodes and data frames."* | *"Use this skill whenever working with Word (.docx) documents, including extracting text and tables, summarizing report contents, or converting documents into clean markdown."* |
| *"Integrates game loops, OpenGL shaders, and linear algebra matrices for physics calculation."* | *"Use this skill when designing or building 2D games, implementing character movement, creating collision physics, or tuning gameplay mechanics."* |
| *"Scrapes DOM trees, queries JSON-LD objects, and computes readability formulas."* | *"Use this skill to audit webpage SEO, validate search engine snippets, diagnose ranking drops, and improve article readability."* |

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
