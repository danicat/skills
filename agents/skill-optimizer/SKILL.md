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
  version: "0.5.0"
  canonical: https://skills.danicat.dev/agents/skill-optimizer/
---

# Agent Skill Optimizer

Procedures, authoring principles, and quality standards for creating, auditing, and optimizing Agent Skills according to the Agent Skills specification and open-source best practices.

## Available scripts

- **`scripts/count_tokens.py`** — Audits skills and categories against Tier 1, 2, and 3 token limits using Vertex AI ADC, Gemini API, or offline heuristic.

---

## Skill Architecture & Progressive Disclosure Limits

Skills use a 3-tier progressive disclosure model to minimize token consumption:

1. **Tier 1 — Routing & Discovery Metadata** (~50–100 words / $\le 150$ tokens):
   - **Fields**: `name` (1–64 characters) and `description` (1–1024 characters).
   - **Runtime behavior**: Injected into the model's system prompt at startup for all available skills so the orchestrator can route tasks accurately.
   - **Budget limit**: Keep routing tokens $\le 150$ (ideal ~100 tokens). Keep description $\le 1024$ characters.

2. **Tier 2 — Skill Instructions & Body** (< 5,000 tokens / < 500 lines):
   - **Scope**: The main `SKILL.md` body (excluding frontmatter).
   - **Runtime behavior**: Loaded into active context only when the skill is explicitly activated.
   - **Budget limit**: Strict limit of $\le 5,000$ tokens and $\le 500$ lines. Move detailed API tables, expansive guides, and catalogs into Tier 3.

3. **Tier 3 — On-Demand Resources & References**:
   - **Scope**: Subdirectories loaded only when explicitly requested by instructions:
     - `references/`: Domain guides, schemas, cheat sheets, and syntax rules.
     - `scripts/`: Executable helper tools and automation scripts.
     - `assets/`: Static templates, seed data, or boilerplate files.

---

## Frontmatter Specification & Metadata Guidelines

Every skill must provide valid YAML frontmatter containing core identifiers, licensing, and an authoritative canonical URL:

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
  tags: "go, refactoring, testing, quality"
  author: Maintainer Name (maintainer@example.com)
  version: "1.0.0"
  canonical: https://skills.example.com/coding/my-skill/
compatibility: Requires Go 1.22+
allowed-tools: Bash(go:*) Read
---
```

### Field Rules & Single-URL Provenance

#### 1. Core Top-Level Fields
- `name` (required): 1-64 characters, lowercase alphanumeric and single hyphens (`a-z`, `0-9`, `-`). No consecutive hyphens (`--`), no leading/trailing hyphens. Must match directory name exactly.
- `description` (required): 1-1024 characters. Non-empty. Follows the 3-Part Skill Description Blueprint (Definition & Scope + Superpower + Human Triggers). Do not include internal implementation plumbing.
- `license` (required): Short SPDX license identifier (e.g., `Apache-2.0`, `MIT`) or path to a bundled license.
- `compatibility` (optional): Environment or tool requirements (e.g., `Requires Python 3.11+`). Omit if standard.
- `allowed-tools` (optional): Space-separated list of pre-approved tools (experimental).

#### 2. Metadata Block (`metadata`)
- `category` (recommended): Functional taxonomy domain (e.g., `coding`, `agents`, `devops`, `media`, `writing`, `analytics`). Recommended to match the parent category folder name in structured repositories.
- `tags` (recommended): 3 to 6 high-level domain anchors for search and categorization. Avoid redundant synonym stuffing.
- `author` (recommended): Maintainer attribution string (e.g., `Author Name (email@example.com)` or organization name).
- `version` (recommended): Semantic Versioning SemVer 2.0.0 (`MAJOR.MINOR.PATCH`).
- `canonical` (recommended): The authoritative web URL pointing to the skill's published documentation (e.g., `https://skills.example.com/<category>/<skill-name>/`).
  - **Single Canonical URL Standard**: Avoid duplicating `homepage` and `repository` fields in frontmatter when a single canonical URL suffices. This reduces metadata overhead by ~60–80 tokens per skill while maintaining full provenance.

#### 3. Zero Contamination Gate
All public skills must be strictly generic, modular, and platform-agnostic:
- **No local machine specifics**: Never include personal machine paths or local home directory structures.
- **No internal corporate knowledge**: Never include internal project names, private channel names, or proprietary infrastructure URLs.
- **No credentials or tokens**: Never leak API keys, personal access tokens, or private secrets.

---

## Optional Reference: Agent Skills MCP Server

To query live specifications and documentation during development, you can connect the Agent Skills MCP server:

- **Server URL**: `https://agentskills.io/mcp`
- **MCP Configuration** (e.g., `~/.gemini/config/mcp_config.json` or `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "agentskills": {
      "url": "https://agentskills.io/mcp"
    }
  }
}
```

---

## 5-Stage Skill Audit & Optimization Process

Follow this procedure when creating, reviewing, or refining skills:

### Stage 1: Structure & File Layout
- **Name Alignment**: Confirm `name` in frontmatter matches the directory name exactly.
- **Tier 1 & Tier 2 Limits**: Verify routing budget ($\le 150$ tokens, $\le 1024$ chars) and body budget ($\le 5,000$ tokens, $\le 500$ lines) using `scripts/count_tokens.py`.
- **Progressive Disclosure**: Move extensive documentation (> 100 lines), schemas, or static data into `references/` or `assets/`.
- **Clean Relative Paths from Skill Root**: All internal file and script references in `SKILL.md` MUST use relative paths starting from the skill root directory (e.g., `scripts/process.py`, `references/guide.md`, `assets/template.md`).
  - **No category prefixes**: Use `scripts/tool.py`, never `category/skill-name/scripts/tool.py`.
  - **No placeholders**: Use `scripts/tool.py`, never `{skillDir}/scripts/tool.py` or `{baseDir}/scripts/tool.py`.
  - **No absolute paths**: The agent harness resolves relative paths against the skill base directory automatically.
- **Available Scripts Discovery**: List bundled scripts in an `## Available scripts` section in `SKILL.md` so the agent immediately discovers available tools.
- **Conditional Loading**: Clearly state *when* the agent should read each reference file.

#### Auditing Skills with Bundled `scripts/count_tokens.py`
Audit skills against Tier 1, Tier 2, and Tier 3 limits using the self-contained PEP 723 Python script:

```bash
# 1. Audit a single skill
uv run scripts/count_tokens.py ../../coding/godoctor/SKILL.md

# 2. Audit a category directory of skills
uv run scripts/count_tokens.py ../../coding/

# 3. Fast offline audit (uses ~4 chars/token heuristic, no API or network calls)
uv run scripts/count_tokens.py ../../agents/ --heuristic-only

# 4. Machine-readable JSON output (for CI/CD pipelines)
uv run scripts/count_tokens.py ../../coding/godoctor/SKILL.md --json
```

**Authentication & Models**:
- **Vertex AI ADC (Default)**: Automatically detects Application Default Credentials (`gcloud auth application-default login`) with model `gemini-3.7-flash` and location `global`.
- **Gemini Developer API**: Set `export GEMINI_API_KEY="..."` to authenticate directly via Gemini API.
- **Offline Fallback**: Automatically falls back to an offline ~4 chars/token heuristic if no network or credentials are available.

### Stage 2: Description, Trigger & Tag Optimization

The frontmatter `description` is the primary text loaded by orchestrators at startup to determine activation. Craft every `description` against this 3-part blueprint:

```
[1. Concrete Definition & Scope] + [2. Architectural Superpower / Key Topics] + [3. Natural, Decisive Trigger]
```

1. **Concrete Definition & Scope**:
   - State what the skill does in plain, direct English.
   - Enumerate tangible topics, formats, and artifacts covered.
   - Use universal mental models (e.g., *"Divide to Conquer approach"*).
   - Avoid narrating a play-by-play checklist in the description.
2. **Key Architecture / Superpower**:
   - State the technical capability plainly (e.g., *"uses parallel subagents to ensure context isolation"*).
   - Explain why the approach matters for quality and reliability.
   - Use open, illustrative examples (e.g., *"connected channels (such as LinkedIn, X/Twitter, Bluesky, and others)"*).
   - Do not waste tokens explaining internal algorithms or private code plumbing (e.g., AST parsing, regex, SQLite internals).
3. **Decisive Triggers**:
   - Include explicit domain terms and tool names.
   - Anchor triggers to user intent and problem characteristics (e.g., *"when tackling problems that require out of the box thinking"*, *"when developing new skills or refining existing ones"*).

#### Trigger Discipline (The Anti-Pushy Rule)
- **Eliminate Artificial Coercion**: Avoid phrases like *"Activate even if the user does not explicitly mention..."* or *"Trigger whenever anything related is requested"*. Overly aggressive trigger language causes false positives and pollutes the context window during multi-turn chats.
- **Describe Problem Traits, Not Model Behavior**: Guide the orchestrator by detailing the **problem symptoms**, **task objectives**, and **domain vocabulary** that uniquely require this skill. Let clear architectural boundaries drive routing decisions naturally.

#### Tag Taxonomy Guidelines
- Choose **3 to 6 high-level domain anchors** for search indices.
- **Do NOT repeat the skill name as a tag**: The `name` is already indexed. Repeating it wastes tag budget.
- **Avoid generic noise tags**: Words like `cli` or `hierarchy` convey minimal context. Use domain-specific anchors like `management` or `structure`.
- **Omit implementation details**: Skip low-level tags (`sqlite`) when high-level intent tags (`sql`, `analytics`) are present.
- **Include brand/ecosystem anchors** when scoped specifically (e.g., `google` for Google-specific standards).

### Stage 3: Core Principles for Skill Body Design

Every skill body must adhere to these 6 instructional standards:

1. **Teach Practices, Not Passive Declarations**:
   - Provide concrete, repeatable workflows, architectural patterns, commands, and debugging steps.
   - Focus on what the agent should *do*, *check*, and *produce*, rather than reciting encyclopedia definitions.

2. **Readability & Clear Scannability**:
   - Maintain clear sentence structure and high scannability (aim for Fog Index ~12–15 with leeway for technical syntax).
   - Avoid dense walls of text; organize multi-step procedures into structured checklists (`- [ ] Step 1...`).

3. **Zero Marketing, Buzzwords & Fake Qualifiers**:
   - Never use marketing buzzwords (*"vibrant"*, *"cutting-edge"*, *"blazing-fast"*, *"world-class"*, *"bespoke"*, *"game-changing"*).
   - Never use fake technical qualifiers (*"high signal SQLite WAL Engine"* ❌). State capabilities plainly (*"SQLite database"* ✅).

4. **Usability Over Implementation Plumbing**:
   - Emphasize the interface the agent interacts with (e.g., `SQLite` tells the agent to query via SQL).
   - Omit internal runtime trivia that does not affect agent interaction (e.g., disk page size, WAL flushing mechanics, internal cache layouts).

5. **Self-Contained with Explicit Installation for Optional Skills**:
   - Skills must function independently and provide complete baseline instructions.
   - When referencing a companion or guest skill (e.g., `godoctor`, `pyhd`, `buffer`), always provide its exact installation command:
     ```bash
     npx skills add <owner>/<repo> --skill <skill-name> -y
     ```
   - Always treat guest skills as **strictly optional** with graceful fallbacks if the companion skill is not installed in the workspace.

6. **Zero Contamination**:
   - Ensure all instructions, examples, and scripts are 100% generic, platform-agnostic, and safe for public open-source distribution.

### Stage 4: Script Design & Bundling
When bundling helper scripts into `scripts/`:
- **Relative Path Invocations**: In `SKILL.md`, all execution examples must use relative paths from the skill root directory (e.g., `uv run scripts/analyze.py input.json`). Never prefix with category directories or template variables (`{skillDir}`, `{baseDir}`).
- **Discovery in `## Available scripts`**: List all bundled scripts in an `## Available scripts` section in `SKILL.md` with brief functional descriptions so the agent discovers them up front.
- **Mandatory Invocation & Auth Documentation**: Every bundled script must be documented with concrete execution examples, runtime requirements (`uv`, `deno`, `bun`), expected arguments, and its authorization model (e.g., Vertex AI ADC, API keys, OAuth, or offline fallback).
- **Non-interactive execution**: Accept arguments via flags, environment variables, or stdin; never prompt for TTY input.
- **Self-contained dependencies**: Declare dependencies inline using standard runtimes:
  - Python: PEP 723 script metadata (`# /// script ... # ///`) executed via `uv run` or `pipx`.
  - TypeScript/JavaScript: Deno (`deno run`) or Bun (`bun run`).
  - Ruby: `bundler/inline` (`require 'bundler/inline'`).
- **Clean interfaces**: Provide `--help` with clear options and usage examples.
- **Structured output**: Write machine-readable output (JSON/CSV) to stdout; write logs and progress to stderr.
- **Actionable errors**: Output specific failure causes, expected inputs, and recovery steps.
- **Safe operations**: Support `--dry-run` and idempotent execution for stateful or destructive operations.

### Stage 5: Operational Patterns & Failure Recovery
Enhance skills with proven structural patterns:
- **Gotchas & Edge Cases**: Document environment quirks, schema oddities, or non-obvious failure recovery steps.
- **Output Templates**: Provide concrete Markdown, YAML, or JSON templates for expected outputs.
- **Workflow Checklists**: Use markdown task lists (`- [ ] Step 1...`) for multi-stage processes.
- **Validation Loops**: Require running a validator script or checklist, inspecting errors, and iterating until passing.
- **Plan-Validate-Execute**: For batch or high-risk tasks, require generating a plan file, validating against schema, and executing only after validation passes.

---

## Case Studies: 3 Representative Before & After Optimizations

The following 3 case studies demonstrate how to apply these principles across three major skill archetypes:

### Case Study 1: `double-diamond` (Process, Agents & Context Isolation)

* **Scenario**: Complex orchestration and multi-phase methodologies.
* **Anti-Pattern (AI Slop & Procedural Choreography ❌)**:
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
* **Best Practice (Clean Definition & Architectural Superpower ✅)**:
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

---

### Case Study 2: `godoctor` (Developer Tooling & Safety Gates)

* **Scenario**: Language tooling, linters, code quality, and testing frameworks.
* **Anti-Pattern (Generic Linter Jargon & Self-Referential Tags ❌)**:
  ```yaml
  description: >
    Developer tooling for Go that enforces language style, idioms, code formatting,
    testing standards, and complexity limits. Includes automated AST validation,
    rollback guards for broken changes, Selene mutation testing to expose blind spots,
    and multi-tiered testing loops. Activate when authoring or refactoring Go code,
    debugging compilation issues, auditing test suite strength, reducing cyclomatic
    complexity, or ensuring strict adherence to idiomatic Go conventions.
  tags: "godoctor, go, golang, ast, selene, mutation-testing, testing, refactoring, quality"
  ```
* **Best Practice (Concrete Safety Mechanisms & Value Framing ✅)**:
  ```yaml
  description: >
    Developer tooling and architectural safety rules for Go. Automatically
    validates AST integrity, guards against regressions with compiler rollback
    gates, eliminates blind spots via Selene mutation testing, and isolates
    test databases with TestQuery SQL transactions. Activate when writing or
    refactoring Go code, fixing compilation or test failures, auditing test
    thoroughness with mutation testing, or enforcing idiomatic Go standards.
  tags: "go, golang, testing, refactoring, quality, mutation-testing"
  ```
* **Why it works**: Highlights the architectural safety mechanisms (**compiler rollback gates** and **isolated SQL transactions**), removes self-referential tag noise (`godoctor`), and frames value around preventing broken builds.

---

### Case Study 3: `google-oss` (Ecosystem Scoping & Organizational Standards)

* **Scenario**: Brand-specific or organizationally bounded guidelines.
* **Anti-Pattern (Vague General Purpose Claims ❌)**:
  ```yaml
  description: >
    Standards, compliance verification, and licensing automation for Google
    open-source software and personal projects by Googlers. Ensures proper
    application of the Apache 2.0 license, license headers using addlicense,
    copyright attributions, repository disclaimers, and open-source release
    readiness. Activate when preparing a repository for public open-source
    release, auditing license headers, checking copyright statements, or ensuring
    compliance with open-source policies.
  tags: "standards, google-oss, license, apache-2-0, compliance, addlicense, disclaimer"
  ```
* **Best Practice (Explicit Organizational Boundaries & Brand Tag ✅)**:
  ```yaml
  description: >
    Compliance guide and licensing automation strictly for Google Open Source
    projects and personal projects created by Googlers. Applies Apache 2.0
    license headers via addlicense, verifies copyright attributions, and
    configures mandatory repository disclaimers. Activate when preparing Google
    open-source or Googler personal repositories for public release, auditing
    license headers, or verifying open-source policy compliance.
  tags: "google, open-source, licensing, compliance, standards, copyright"
  ```
* **Why it works**: Explicitly defines the organizational boundary ("strictly for Google Open Source projects and personal projects created by Googlers") to prevent misuse on generic third-party open-source, and adds the essential `google` ecosystem tag.
