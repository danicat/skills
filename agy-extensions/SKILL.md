---
name: agy-extensions
description: >
  Guide, scaffold, and construct any extension for Google Antigravity across both AGY CLI and AGY 2.0 (Desktop/IDE). Use this skill when creating standalone extensions (a single hook, MCP server, skill, rule, or custom subagent) or bundled plugins encompassing one or more extensions.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2"
---

# Antigravity Extensions (`agy-extensions`)

This skill provides step-by-step procedures, templates, configuration formats, and installation standards to author, deploy, and validate any custom extension for **Antigravity CLI (AGY CLI)** and **Antigravity 2.0 (Desktop / IDE)**.

An **Antigravity Extension** can be authored and deployed in two ways:
1. **Standalone Extensions**: Individual capabilities installed directly into workspace or global configuration directories:
   - **Skills** (`SKILL.md`)
   - **Rules** (`<rule-name>.md`)
   - **Custom Subagents** (`<agent-name>.md`)
   - **Event Hooks** (`hooks.json`)
   - **MCP Servers** (`mcp_config.json`)
2. **Bundled Plugins**: A namespaced directory (`plugins/<plugin-name>/`) with a `plugin.json` manifest wrapper that bundles multiple extensions into a single package.

---

## 1. Quick Reference: Extension Target Locations Matrix

This table summarizes where to install standalone extensions and plugin bundles based on target scope and platform:

| Extension Type | Target Scope | Antigravity 2.0 (Desktop / IDE) | Antigravity CLI (AGY CLI) |
| :--- | :--- | :--- | :--- |
| **Plugin Bundle** | Workspace | `<workspace>/.agents/plugins/<plugin-name>/` | `<workspace>/.agents/plugins/<plugin-name>/` |
| **Plugin Bundle** | Global | `~/.gemini/config/plugins/<plugin-name>/` | `~/.gemini/antigravity-cli/plugins/<plugin-name>/`<br>*(also auto-discovers from `config/plugins/`)* |
| **Skill** | Workspace | `<workspace>/.agents/skills/<folder>/SKILL.md` | `<workspace>/.agents/skills/<folder>/SKILL.md` or `<name>.md` |
| **Skill** | Global | `~/.gemini/config/skills/<folder>/SKILL.md` | `~/.gemini/antigravity-cli/skills/<folder>/SKILL.md` |
| **Rule** | Workspace | `<workspace>/.agents/rules/<rule-name>.md` | `<workspace>/.agents/rules/<rule-name>.md` |
| **Rule** | Global | `~/.gemini/GEMINI.md` | `~/.gemini/GEMINI.md` |
| **Subagent** | Workspace | `<workspace>/.agents/agents/<name>.md` | `<workspace>/.agents/agents/<name>.md` |
| **Subagent** | Global | `~/.gemini/config/agents/<name>.md` | `~/.gemini/config/agents/<name>.md` |
| **MCP Server** | Workspace | `<workspace>/.agents/mcp_config.json` | `<workspace>/.agents/mcp_config.json` |
| **MCP Server** | Global | `~/.gemini/config/mcp_config.json` | `~/.gemini/antigravity-cli/mcp_config.json` |
| **Event Hooks** | Workspace | `<workspace>/.agents/hooks.json` | `<workspace>/.agents/hooks.json` |
| **Event Hooks** | Global | `~/.gemini/config/hooks.json` | `~/.gemini/antigravity-cli/hooks.json` |

> [!TIP]
> For complete technical comparisons, schema variations, and discovery rules across platforms, consult [`references/agy-cli-vs-20.md`](references/agy-cli-vs-20.md).

---

## 2. Authoring Standalone Extensions (Configuration & Installation)

Use these detailed specifications when building individual standalone extensions:

### A. Standalone Skill

**What it does**: Equips agents with procedural workflows, domain context, and instructions for specialized tasks.

#### 1. Configuration Syntax
Create a `SKILL.md` file with YAML frontmatter:
```yaml
---
name: code-reviewer
description: >
  Perform thorough pull request and code review audits for security, performance, and style.
  Trigger when the user requests code review or PR audit.
license: Apache-2.0
metadata:
  version: "1.0"
---

# Code Review Skill

Instructions for the agent...
```

**Directory Layout**:
```text
<skill-folder>/
├── SKILL.md          # Primary instruction file (Required)
├── references/       # Optional supporting schemas & API documentation
├── scripts/          # Optional helper scripts
└── templates/        # Optional code blueprints
```

#### 2. Where to Install
- **Workspace Scope** (applies only to current repository):
  - AGY 2.0 & CLI: `<workspace>/.agents/skills/<skill-folder>/SKILL.md`
- **Global Scope** (applies across all projects):
  - AGY 2.0 (Desktop): `~/.gemini/config/skills/<skill-folder>/SKILL.md`
  - AGY CLI: `~/.gemini/antigravity-cli/skills/<skill-folder>/SKILL.md`

---

### B. Standalone Rule

**What it does**: Enforces persistent guidelines, architectural constraints, and coding standards.

#### 1. Configuration Syntax
Create a Markdown file (`<rule-name>.md`) with optional frontmatter:
```markdown
---
description: Enforce strict TypeScript typing and zero `any` usage.
alwaysOn: false
glob: "src/**/*.ts"
---

# Strict TypeScript Rule

- Never use `any` type annotations.
- Always handle `undefined` or `null` return types explicitly.
```

**Activation Modes**:
- `alwaysOn: true` — Active on every conversation turn.
- `manual: true` — Activated explicitly when referenced via `@rule-name`.
- `glob: "pattern"` — Activated when working on files matching the glob pattern.
- Model Decision — Default; model activates rule when relevant based on `description`.

*Constraint*: Maximum **12,000 characters** per rule file.

#### 2. Where to Install
- **Workspace Scope**:
  - AGY 2.0 & CLI: `<workspace>/.agents/rules/<rule-name>.md` or `<workspace>/GEMINI.md`
- **Global Scope**:
  - AGY 2.0 & CLI: `~/.gemini/GEMINI.md` or `~/.gemini/config/rules/<rule-name>.md`

---

### C. Standalone Custom Subagent

**What it does**: Defines a specialized, autonomous subagent with tailored tools, prompts, and permissions that can be invoked via `invoke_subagent`.

#### 1. Configuration Syntax
Create a Markdown file (`<agent-name>.md`) with YAML frontmatter:
```yaml
---
name: database-debugger
description: Specialized database administrator subagent to inspect SQL schemas and query performance.
tools:
  - view_file
  - grep_search
  - run_command
subagent: true
mainAgent: false
model: inherit           # Model tier: inherit, flash, or pro
commandExecutionPolicy: sandbox  # Options: off, auto, eager, sandbox
---

# Database Debugger Subagent

You are a specialized DB subagent. Follow these instructions...
```

**Key Fields**:
- `name` *(Required)*: Unique identifier used in `invoke_subagent`.
- `description` *(Required)*: Used by planner to determine delegation.
- `tools`: List of permitted tool names. Must match exact native/MCP tool names.
- `subagent`: Set to `true` to allow invocation.

#### 2. Where to Install
- **Workspace Scope**:
  - AGY 2.0 & CLI: `<workspace>/.agents/agents/<agent-name>.md`
- **Global Scope**:
  - AGY 2.0 & CLI: `~/.gemini/config/agents/<agent-name>.md`

---

### D. Standalone Event Hooks

**What it does**: Intercepts agent execution lifecycle events to perform pre-flight validation, auto-formatting, logging, or completion audits.

#### 1. Configuration Syntax
Create a `hooks.json` configuration file:
```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": "run_command|write_to_file",
      "command": "/path/to/security_guard.py",
      "timeoutMs": 5000
    },
    {
      "event": "PostToolUse",
      "matcher": "replace_file_content",
      "command": "npx prettier --write $CHANGED_FILE"
    }
  ]
}
```

**Key Configuration Fields**:
- `event`: Lifecycle event (`PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`).
- `matcher`: Regular expression matching tool names (e.g. `"run_command"`, `"write_to_file|replace_file_content"`).
- `command`: Absolute path or executable command to invoke.
- `timeoutMs`: Execution timeout in milliseconds.

**I/O Contract**:
Hook scripts receive JSON on `stdin` (containing tool arguments or execution context) and MUST return JSON on `stdout` with exit code 0. Consult [`references/hooks-and-tools-reference.md`](references/hooks-and-tools-reference.md) for payload schemas.

#### 2. Where to Install
- **Workspace Scope**:
  - AGY 2.0 & CLI: `<workspace>/.agents/hooks.json`
- **Global Scope**:
  - AGY 2.0: `~/.gemini/config/hooks.json`
  - AGY CLI: `~/.gemini/antigravity-cli/hooks.json`

---

### E. Standalone MCP Server Configuration

**What it does**: Connects Antigravity agents to external Model Context Protocol (MCP) tool servers.

#### 1. Configuration Syntax
Create an `mcp_config.json` configuration file:
```json
{
  "mcpServers": {
    "sqlite-db": {
      "command": "uvx",
      "args": [
        "mcp-server-sqlite",
        "--db-path",
        "./data/app.db"
      ]
    },
    "github-tools": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
      }
    }
  }
}
```

#### 2. Where to Install
- **Workspace Scope**:
  - AGY 2.0 & CLI: `<workspace>/.agents/mcp_config.json`
- **Global Scope**:
  - AGY 2.0: `~/.gemini/config/mcp_config.json`
  - AGY CLI: `~/.gemini/antigravity-cli/mcp_config.json`
  - Programmatic installation via CLI:
    ```bash
    agy mcp add <server-name> -- <command> [args...]
    ```

---

## 3. Authoring Bundled Plugins

When packaging multiple extensions into a single redistributable unit:

### Standard Plugin Layout
```text
plugins/<plugin-name>/
├── plugin.json                 # Required package manifest marker
├── mcp_config.json             # Optional Model Context Protocol servers
├── hooks.json                  # Optional event hook definitions
├── skills/                     # Optional specialized skills directory
│   └── <skill-name>/
│       └── SKILL.md
├── agents/                     # Optional subagent templates
│   └── <agent-name>.md
└── rules/                      # Optional custom codebase rules
    └── <rule-name>.md
```

### Plugin Authoring & Installation Workflow
1. **Initialize Manifest (`plugin.json`)**:
   - Create `plugins/<plugin-name>/plugin.json` using [`templates/plugin.json`](templates/plugin.json).
   - Set `"$schema"` to `"https://antigravity.google/schemas/v1/plugin.json"`.
   - Ensure `name` contains only alphanumeric characters, hyphens, and underscores (`^[a-zA-Z0-9-_]+$`).
   - Consult [`references/manifest-and-schemas.md`](references/manifest-and-schemas.md) for full JSON schema specifications.
2. **Add Component Extensions**: Place skills under `skills/`, rules under `rules/`, subagents under `agents/`, hooks in `hooks.json`, and MCP servers in `mcp_config.json`.
3. **Where to Install Plugin Bundles**:
   - **Workspace Scope**: Place in `<workspace>/.agents/plugins/<plugin-name>/`.
   - **Global Scope (AGY 2.0)**: Place in `~/.gemini/config/plugins/<plugin-name>/`.
   - **Global Scope (AGY CLI)**: Place in `~/.gemini/antigravity-cli/plugins/<plugin-name>/` or install programmatically:
     ```bash
     agy plugin install /path/to/plugins/<plugin-name>
     agy plugin list
     ```

---

## 4. Quality & Pre-Flight Validation Checklist

Before finalizing any extension or plugin bundle, verify:

- [ ] **Target Scope Defined**: Placed in correct Workspace (`.agents/`) or Global (`~/.gemini/`) directory.
- [ ] **Manifest Compliant** (Plugin bundles): `plugin.json` exists at root, valid JSON, `name` matches `^[a-zA-Z0-9-_]+$`.
- [ ] **Tool Identifiers Validated**: All tool names in subagent `tools` or hook `matcher` regex match official native or MCP tool identifiers.
- [ ] **Hook Contracts Verified**: Hook scripts process JSON from `stdin` and output valid JSON to `stdout`.
- [ ] **Skill Descriptions Concise**: `SKILL.md` frontmatter descriptions are imperative and < 1024 characters.
- [ ] **Rule Character Limits Honored**: All `.md` files in `rules/` are under 12,000 characters.
