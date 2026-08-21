---
name: skill-optimizer
description: >
  Comprehensive guide to develop and improve Agent Skill performance. Contains
  best practices for skill formatting (frontmatter and metadata), naming,
  descriptions, fine-tuning activation triggers, evaluations,
  production-readiness and open sourcing. Activate when developing new skills
  or refining existing ones.
license: Apache-2.0
metadata:
  category: agents
  tags: "skills, agent-skills, optimization, standards"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
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
  Concise definition of the skill and tangible topics covered. Mentions key
  architecture or superpower. Activate when encountering primary use case or
  problem conditions.
license: Apache-2.0
metadata:
  category: coding
  tags: "coding, go, quality, refactoring"
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
- `description` (required): 1-1024 characters. Non-empty. Follows the 3-Part Skill Description Formula (Definition & Scope + Superpower + Human Triggers). Do NOT include internal algorithms or implementation plumbing.
- `license` (required): Short SPDX license identifier (e.g., `Apache-2.0`, `MIT`) or path to a bundled license.
- `compatibility` (optional): Max 500 characters. Environment or tool requirements. Omit if standard.
- `allowed-tools` (optional): Space-separated list of pre-approved tools (experimental).

#### 2. Full Provenance & Version Control (`metadata` Block)
- `category` (required): Functional taxonomy domain (`agents`, `coding`, `game-dev`, `media`, `writing`, `analytics`, `standards`, `gateway`). Must match the parent category folder name.
- `tags` (required): 3 to 6 high-level domain anchors for search and categorization. Avoid redundant synonym stuffing.
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

### Stage 2: Description, Trigger & Tag Optimization

The frontmatter `description` is the **only** piece of text loaded by the orchestrator at startup to determine whether to activate the skill. Craft every `description` and `metadata.tags` against this core blueprint:

#### The 3-Part Skill Description Blueprint

```
[1. Concrete Definition & Scope] + [2. Architectural Superpower / Key Topics] + [3. Natural, Decisive Trigger]
```

1. **Concrete Definition & Scope (Simple English, No Jargon, No Play-by-Play Choreography)**:
   - State **what the skill is** in one clear sentence using plain English.
   - Enumerate the **tangible artifacts, formats, and topics** covered (e.g., *"formatting (frontmatter and metadata), naming, descriptions, evaluations..."*) instead of abstract process fluff (*"enforces quantitative optimization gates..."*).
   - Use **universal mental models** (e.g., *"Divide to Conquer approach"*) rather than internal mechanical org-charts or role labels.
   - Do NOT narrate an internal step-by-step checklist disguised as a paragraph.
2. **Key Architecture / Superpower (Why Use It)**:
   - State the technical mechanism or value proposition plainly and directly (e.g., *"uses parallel subagents to ensure context isolation"*, *"follows the process: Inception -> Discovery -> Definition -> Development and Delivery"*).
   - Explain **why** the architecture is chosen (e.g., *"guarantees context isolation for orthogonal subproblems like concurrent frontend and backend development"*).
   - Use **illustrative examples rather than closed lists** when referencing supported services or formats (e.g., *"connected channels (such as LinkedIn, X/Twitter, Bluesky, and others)"*).
   - NEVER waste description tokens explaining internal code plumbing, algorithms, or private data structures (e.g., do *not* mention BM25, AST parsing, regex, SQLite).
3. **Decisive, Human Triggers**:
   - **Explicit terms**: When the user requests the skill by name, methodology, or key domain terms.
   - **Problem-state traits & natural phrasing**: A concise, universal trigger tied to what the user is trying to achieve (e.g., *"when tackling problems that require out of the box thinking"*, *"when developing new skills or refining existing ones"*, *"or to employ multiple agents to perform a task"*), avoiding cluttered laundry lists of minor edge cases.

#### Tag Taxonomy Strategy
- Choose **3 to 6 high-level domain anchors** that classify the skill in search and discovery indices.
- Prioritize **primary domain concepts, standards, and user intent** (e.g., `skills, agent-skills, optimization, standards` or `analytics, traffic, metrics, optimization`).
- **Omit internal implementation details** from tags if they are already in the description (e.g., omit `sqlite` when `sql` and `analytics` are present) to keep search signals clean.

---

#### Case Studies: Before & After Optimization

##### Case Study 1: `double-diamond` (Architecture & Process)

* **Anti-Pattern (AI Slop / Procedural Choreography ❌)**:
  ```yaml
  description: >
    Orchestrate complex engineering initiatives using the Double Diamond framework
    (Inception -> Discover -> Define -> Develop -> Deliver). Researches codebase constraints
    before writing code to resolve ambiguity, establish scope, and prevent architectural mistakes.
    Produces a technical specification for user review, then parallelizes development across
    independent subagents with automated compiler and test quality gates. Activate for high-ambiguity
    spikes, major refactors, multi-agent coding swarms, or explicit research-then-implement
    workflows. Do not use for single-file edits or simple bug fixes.
  tags: "agents, double-diamond, agile, swarm, orchestration, architecture, planning, research, problem-framing, parallel-coding, subagents, quality-gates"
  ```
* **Best Practice (Clean, Human, Context-Isolated ✅)**:
  ```yaml
  description: >
    Development methodology to perform tasks using the Double Diamond framework,
    following the process: Inception -> Discovery -> Definition -> Development and
    Delivery. Uses parallel subagents to perform the tasks ensuring context
    isolation for optimal results. Activate when the user requests to use the
    Double Diamond methodology, when they mention terms like inception and
    discovery, or when tackling problems that require out of the box thinking,
    reducing ambiguity and/or enterprise grade quality levels.
  tags: "inception, delivery, agile, planning, research, subagents"
  ```
* **Why it works**: Replaces artificial procedural narration with a direct definition, highlights the real architectural superpower (**context isolation**), anchors triggers to human problem traits, and reduces 12 redundant tags to 6 high-signal anchors.

##### Case Study 2: `skill-optimizer` (Standards & Meta-Skill)

* **Anti-Pattern (Abstract Jargon & Laundry List ❌)**:
  ```yaml
  description: >
    Standards, validation procedures, and evaluation workflows for authoring and
    optimizing Agent Skills. Enforces progressive disclosure, metadata schema
    compliance, and zero-contamination security gates, using quantitative trigger
    tuning and eval benchmarks to ensure high activation reliability and task
    execution quality. Activate when authoring new skills, refining existing
    instructions, diagnosing skill activation misfires, writing evaluation suites
    in evals.json, or auditing skills for public open-source distribution.
  tags: "agent-skills, meta-skill, authoring, evals, benchmarks, optimization, quality-gates"
  ```
* **Best Practice (Concrete Scope & Universal Trigger ✅)**:
  ```yaml
  description: >
    Comprehensive guide to develop and improve Agent Skill performance. Contains
    best practices for skill formatting (frontmatter and metadata), naming,
    descriptions, fine-tuning activation triggers, evaluations,
    production-readiness and open sourcing. Activate when developing new skills
    or refining existing ones.
  tags: "skills, agent-skills, optimization, standards"
  ```
* **Why it works**: Replaces heavy abstract nouns with a concrete enumeration of covered topics (formatting, naming, descriptions, triggers, evals, open-sourcing) and replaces a wordy sub-scenario laundry list with a crisp, universal activation trigger.

##### Case Study 3: `swarm-coding` (Divide to Conquer & Orthogonal Subproblems)

* **Anti-Pattern (Mechanical Hierarchy & Jargon ❌)**:
  ```yaml
  description: >
    Hierarchical multi-agent coordination framework for executing large-scale,
    multi-component engineering projects. Structures subagents into a three-tier
    team (Coordinator -> Domain Leads -> Specialists) with strict vertical
    communication, disjoint file allocations to prevent write collisions, and
    persistent agent reuse to preserve context. Activate when the user requests
    swarm coding or mentions "swarm", or when executing complex full-stack
    initiatives, multi-service migrations, or large refactorings across parallel
    agents.
  tags: "swarm, multi-agent, parallel-coding, coordination, architecture"
  ```
* **Best Practice (Divide to Conquer & Orthogonal Problems ✅)**:
  ```yaml
  description: >
    Orchestration strategy based on a Divide to Conquer approach. Breaks down
    complex problems into subproblems and assigns each subproblem to a specialised
    team. Contains instructions for efficient coordination of the swarm so that
    each agent performs at its top capacity. Activate when the user requests swarm
    coding or to employ multiple agents to perform a task. You should also
    activate it when dealing with orthogonal problems in the same task, like for
    example implementing backend and frontend at the same time, as the swarm will
    guarantee context isolation and optimal results.
  tags: "swarm, subagents, parallel, orchestration, strategy, complexity, coordination"
  ```
* **Why it works**: Leads with the universal mental model ("Divide to Conquer"), provides a relatable scenario ("orthogonal problems like backend and frontend"), explains the architectural benefit ("guarantee context isolation"), and captures natural user phrasing ("to employ multiple agents").

##### Case Study 4: `buffer-analytics` & `google-analytics` (Open Examples & Simple English)

* **Anti-Pattern (Inflated Modifiers & Rigid Lists ❌)**:
  ```yaml
  description: >
    Ingest raw Buffer social post and channel data into a local SQLite analytics
    database (without loss), run backfills and incremental syncs, execute ad-hoc
    SQL queries, and perform deep performance crunching across LinkedIn,
    Twitter/X, and Bluesky. Activate whenever analyzing social post performance,
    auditing historical metrics, finding best days/hours to post, running SQL
    queries over social archives, or evaluating campaign engagement.
  tags: "analytics, buffer, social-metrics, sqlite, engagement, sql"
  ```
* **Best Practice (Open Examples & Goal-Oriented Tags ✅)**:
  ```yaml
  description: >
    Collect and analyze social media data from Buffer in a local SQLite database.
    Stores your full post history and metrics across connected channels (such as
    LinkedIn, X/Twitter, Bluesky, and others) so you can run SQL queries or view
    reports on engagement, clicks, and views. Activate when you need to analyze
    social media performance, find the best days or times to post, identify
    top-performing content, or query Buffer data with SQL.
  tags: "buffer, social-media, analytics, sql, metrics, optimization"
  ```
* **Why it works**: Replaces inflated adjectives ("without loss", "deep performance crunching") with simple, direct verbs, uses open illustrative phrasing for channels, drops redundant implementation tags (`sqlite`), and adds user-intent tags (`optimization`).

---

#### Contrastive Anti-Patterns vs Best Practices

| Anti-Pattern (Implementation-Heavy or Procedural Slop ❌) | Best Practice (Outcome, Superpower & Clean Trigger ✅) |
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
