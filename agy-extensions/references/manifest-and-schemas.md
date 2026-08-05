# Antigravity Manifests & Schemas Reference

This reference covers the complete specifications and schemas for all core Antigravity plugin assets: `plugin.json`, `mcp_config.json`, Subagents (`.md`), Skills (`SKILL.md`), and Rules (`.md`).

---

## 1. Plugin Manifest (`plugin.json`)

`plugin.json` must be placed at the root of the plugin directory.

### Full JSON Schema
```json
{
  "$schema": "https://antigravity.google/schemas/v1/plugin.json",
  "title": "Antigravity Plugin Manifest",
  "description": "Schema for Antigravity CLI plugin manifest files (plugin.json)",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "The unique, machine-readable name of the plugin. Must contain only alphanumeric characters, hyphens, and underscores.",
      "pattern": "^[a-zA-Z0-9-_]+$"
    },
    "description": {
      "type": "string",
      "description": "A brief human-readable description of the plugin's purpose and capabilities."
    }
  },
  "required": [
    "name"
  ],
  "additionalProperties": false
}
```

### Compliant Example
```json
{
  "$schema": "https://antigravity.google/schemas/v1/plugin.json",
  "name": "developer-productivity-pack",
  "description": "Bundles code review skills, linter hooks, and security audit subagents."
}
```

---

## 2. Model Context Protocol Configuration (`mcp_config.json`)

`mcp_config.json` connects Antigravity to local or remote MCP servers.

### Example
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

---

## 3. Custom Subagents (`agents/<name>.md`)

Custom subagents are defined in Markdown files with YAML frontmatter.

### Frontmatter Field Reference

| Field | Type | Default | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | - | **Yes** | Unique identifier for the subagent. |
| `description` | string | - | **Yes** | Detailed description used by the planner to determine delegation. |
| `tools` | string[] | `[]` | No | List of permitted tools (e.g. `view_file`, `grep_search`, `run_command`). |
| `mainAgent` | boolean | `true` | No | If `true`, permits selection as the primary agent in chat. |
| `subagent` | boolean | `true` | No | If `true`, permits invocation via `invoke_subagent`. |
| `model` | string | `inherit` | No | Model tier (`inherit`, `flash`, `pro`). |
| `commandExecutionPolicy` | string | `sandbox` | No | Command policy (`off`, `auto`, `eager`, `sandbox`). |
| `mcpServers` | object[] | `[]` | No | MCP server overrides for this subagent. |
| `skills` / `plugins` | string[] | `[]` | No | Dependent skills (e.g., `skills/security-checklist`) or plugins. |

> [!WARNING]
> **Known Issue (Tool Validation)**: Specifying an unmapped or misspelled tool name in `tools` can cause the subagent process to hang during execution. Always double-check exact tool names against the tool registry.

### Nesting Limits & Lifecycle States
- **Nesting Depth Limit**: Maximum nesting depth of **10 levels** is strictly enforced.
- **States**:
  1. `Running`: Actively calling tools and generating responses.
  2. `Idle`: Finished task, sent result to parent agent, waiting for new messages (re-awakens upon message receipt while keeping context).
  3. `Killed`: Permanently terminated; temporary Git worktrees cleaned up.

---

## 4. Skills (`skills/<skill-name>/SKILL.md`)

Skills extend capabilities through instructions, progressive disclosure references, and optional templates.

### Frontmatter Fields
```yaml
---
name: skill-name
description: Imperative, intent-focused description explaining when and why the agent should activate this skill. Maximum 1024 characters.
---
```

### Folder Structure
```text
skills/<skill-name>/
├── SKILL.md          # Core instructions and workflow (Required)
├── references/       # In-depth schemas, tables, and API docs (Optional)
├── templates/        # Reusable code and asset blueprints (Optional)
└── examples/         # Reference implementations (Optional)
```

---

## 5. Rules (`rules/<rule-name>.md`)

Rules define persistent constraints and guidelines for agent behavior.

### Rule Limits & Activation Modes
- **Character Limit**: Maximum 12,000 characters per rule file.
- **Activation Modes**:
  1. **Manual**: Activated explicitly via `@rule-name` in user prompt.
  2. **Always On**: Applied persistently to all turns.
  3. **Model Decision**: Applied when model determines relevance based on rule description.
  4. **Glob**: Applied to files matching specified glob patterns (e.g. `src/**/*.ts`).

### `@` Mention Resolution
- Relative path `@file.md`: Resolved relative to the Rule file directory.
- Root path `@/path/to/file.md`: Resolved against true absolute path first; falls back to workspace path.
