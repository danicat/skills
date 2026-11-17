---
name: skill-optimizer
description: >
  Comprehensive guide to develop and improve Agent Skill performance. Contains
  best practices for skill formatting (frontmatter and metadata), naming,
  descriptions, fine-tuning activation triggers, evaluations,
  production-readiness and open sourcing. Activate when developing new skills or
  refining existing ones.
license: Apache-2.0
metadata:
  category: workflows
  tags: "skills, agent-skills, optimization, standards"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.6.0"
  catalog: https://skills.danicat.dev
---

# Agent Skill Optimizer

Procedures, authoring principles, and quality standards for creating, auditing, and optimizing Agent Skills according to the Agent Skills specification and open-source best practices.

## Available scripts

- **`scripts/count_tokens.py`**: Audits skills and categories against Tier 1, 2, and 3 token limits using Gemini Enterprise / Vertex AI ADC, Gemini API, or an offline heuristic.

---

## Skill Architecture & Progressive Disclosure Limits

Skills use a 3-tier progressive disclosure model to minimize token consumption:

1. **Tier 1: Routing & Discovery Metadata** (~50–100 words / <= 150 tokens):
   - **Fields**: `name` (1–64 characters) and `description` (1–1024 characters).
   - **Runtime behavior**: Injected into the model's system prompt at startup for all available skills so the orchestrator can route tasks accurately.
   - **Budget limit**: Keep routing tokens <= 150 (ideal ~100 tokens). Keep description <= 1024 characters.

2. **Tier 2: Skill Instructions & Body** (< 5,000 tokens / < 500 lines):
   - **Scope**: The main `SKILL.md` body (excluding frontmatter).
   - **Runtime behavior**: Loaded into active context only when the skill is explicitly activated.
   - **Budget limit**: Strict limit of <= 5,000 tokens and <= 500 lines. Move detailed API tables, expansive guides, and catalogs into Tier 3.

3. **Tier 3: On-Demand Resources & References**:
   - **Scope**: Subdirectories loaded only when explicitly requested by instructions:
     - `references/`: Domain guides, schemas, cheat sheets, and syntax rules stored as focused Markdown files for progressive disclosure.
     - `scripts/`: Executable helper tools and automation scripts.
     - `assets/`: Static templates, seed data, or boilerplate files.

---

## Frontmatter Specification & Metadata Guidelines

Every skill must provide valid YAML frontmatter containing core identifiers, licensing, and a catalog URL:

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
  catalog: https://skills.example.com
compatibility: Requires Go 1.22+
allowed-tools: Bash(go:*) Read
---
```

### Field Rules & Single-URL Provenance

#### 1. Core Top-Level Fields
- `name` (required): 1-64 characters, lowercase alphanumeric and single hyphens (`a-z`, `0-9`, `-`). No consecutive hyphens (`--`), no leading/trailing hyphens. Must match directory name exactly.
- `description` (required): 1-1024 characters. Non-empty. Follows the 3-Part Skill Description Blueprint (Definition & Scope + Superpower + Human Triggers). Do not include internal implementation plumbing.
- `license` (required): Short SPDX license identifier (e.g., `Apache-2.0`, `MIT`) or path to a bundled license.
- `compatibility` (optional): Plain string stating environment or runtime requirements per the Agent Skills specification (e.g., `Requires Python 3.12+ and uv`, max 500 characters). Never use a nested YAML mapping or list. Omit if standard.
- `allowed-tools` (optional): Space-separated list of pre-approved tools (experimental).

#### 2. Metadata Block (`metadata`)
- `category` (recommended): Functional taxonomy domain (e.g., `coding`, `agents`, `devops`, `media`, `writing`, `analytics`). Recommended to match the parent category folder name in structured repositories.
- `tags` (recommended): 3 to 6 high-level domain anchors for search and categorization. Avoid redundant synonym stuffing.
- `author` (recommended): Maintainer attribution string (e.g., `Author Name (email@example.com)` or organization name).
- `version` (recommended): Semantic Versioning SemVer 2.0.0 (`MAJOR.MINOR.PATCH`).
- `catalog` (recommended): Base URL of the published Agent Skills catalog hosting the skill (e.g., `https://skills.example.com`, serving `.well-known/agent-skills/index.json`).
  - **Single Catalog URL Standard**: Avoid duplicating `homepage` and `repository` fields in frontmatter when a single `catalog` URL suffices. This reduces metadata overhead by ~60 to 80 tokens per skill while preserving provenance.

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
- **Tier 1 & Tier 2 Limits**: Verify routing budget (<= 150 tokens, <= 1024 chars) and body budget (<= 5,000 tokens, <= 500 lines) using `scripts/count_tokens.py`.
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
uv run scripts/count_tokens.py path/to/my-skill/SKILL.md

# 2. Audit a category directory of skills
uv run scripts/count_tokens.py ../../coding/

# 3. Fast offline audit (uses ~4 chars/token heuristic, no API or network calls)
uv run scripts/count_tokens.py ../../workflows/ --heuristic-only

# 4. Machine-readable JSON output (for CI/CD pipelines)
uv run scripts/count_tokens.py path/to/my-skill/SKILL.md --json
```

**Authentication & Models**:
- **Gemini Enterprise / Vertex AI ADC (Default)**: Automatically detects Application Default Credentials (`gcloud auth application-default login`, or `GOOGLE_GENAI_USE_ENTERPRISE=true` / `GOOGLE_GENAI_USE_VERTEXAI=true`) with model `gemini-4-hydrogen` and location `global`.
- **Gemini Developer API**: Set `export GEMINI_API_KEY="..."` to authenticate directly via Gemini API.
- **Offline Fallback**: Pass `--heuristic-only` (or let the script fall back automatically when offline) to estimate ~4 chars/token without network calls.

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
- **Respect Native Slash Commands & Modes**: Never register triggers that collide with built-in host commands or workflows (such as `/swarm`, `/grill-me`, `/boost`, `/teamwork`, or `/plan`). Keep Tier 1 descriptions tight: warm turns benefit from implicit prefix caching, while parallel subagent spawns and Orchestrator model switches pay full uncached system-prompt prefill.

#### Tag Taxonomy Guidelines
- Choose **3 to 6 high-level domain anchors** for search indices.
- **Do NOT repeat the skill name as a tag**: The `name` is already indexed. Repeating it wastes tag budget.
- **Avoid generic noise tags**: Words like `cli` or `hierarchy` convey minimal context. Use domain-specific anchors like `management` or `structure`.
- **Omit implementation details**: Skip low-level tags (`sqlite`) when high-level intent tags (`sql`, `analytics`) are present.
- **Include brand/ecosystem anchors** when scoped specifically (e.g., `google` for Google-specific standards).

### Stage 3: Core Principles for Skill Body Design

Every skill body must adhere to these 7 instructional standards:

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

5. **Self-Contained & Independent by Default**:
   - Skills must function independently and provide complete baseline instructions without referencing or depending on other skills.
   - Do not cross-reference companion skills unless the skill is explicitly designed as a multi-skill orchestrator.

6. **Zero Contamination**:
   - Ensure all instructions, examples, and scripts are 100% generic, platform-agnostic, and safe for public open-source distribution.

7. **Design for Native Reasoning & Plan-Execute Split**:
   - Modern reasoning models (such as Gemini 4 Carbon, Argon, and Hydrogen) plan and think natively across configurable effort levels (`low`, `medium`, `high`, `xhigh`). Do not bloat Tier 2 bodies with step-by-step chain-of-thought scripts or basic language tutorials the model already knows.
   - Spend tokens on non-obvious domain invariants, breaking API constraints, failure traps, and exact verification commands so both read-only planning models and fast execution models succeed on the first pass.

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
