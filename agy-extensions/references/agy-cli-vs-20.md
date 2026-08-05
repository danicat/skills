# Antigravity CLI vs Antigravity 2.0 Technical Reference

This document details filesystem path mappings, schema requirements, discovery mechanisms, and runtime execution differences across **Antigravity CLI (AGY CLI)** and **Antigravity 2.0 (AGY 2.0 Desktop/IDE)**.

---

## 1. Directory & Path Mapping

| Customization Component | Antigravity 2.0 (Desktop / IDE) | Antigravity CLI (AGY CLI) |
| :--- | :--- | :--- |
| **Global Plugins Directory** | `~/.gemini/config/plugins/<plugin-name>/` | `~/.gemini/antigravity-cli/plugins/<plugin_name>/`<br>*(also auto-discovers from `~/.gemini/config/plugins/`)* |
| **Workspace Plugins Directory** | `<workspace>/.agents/plugins/<plugin-name>/`<br>*or* `<workspace>/_agents/plugins/<plugin-name>/` | `<workspace>/.agents/plugins/<plugin-name>/` |
| **Global Skills Directory** | `~/.gemini/config/skills/<skill-folder>/SKILL.md` | `~/.gemini/antigravity-cli/skills/` *(supports `.md` files or subdirectories)* |
| **Workspace Skills Directory** | `<workspace>/.agents/skills/<skill-folder>/SKILL.md` | `<workspace>/.agents/skills/<skill-name>.md` or `<workspace>/.agents/skills/<folder>/SKILL.md` |
| **Global Rules Location** | `~/.gemini/GEMINI.md` | `~/.gemini/GEMINI.md` |
| **Workspace Rules Directory** | `<workspace>/.agents/rules/<rule-name>.md` | `<workspace>/.agents/rules/<rule-name>.md` |
| **Custom Subagents Directory** | `<workspace>/.agents/agents/<name>.md`<br>`~/.gemini/config/agents/<name>.md`<br>`plugins/<plugin_name>/agents/<name>.md` | Same discovery locations |
| **Transcript Logs Directory** | `~/.gemini/antigravity/brain/<conversationId>/.system_generated/logs/transcript.jsonl` | `~/.gemini/antigravity-cli/brain/<conversationId>/.system_generated/logs/transcript.jsonl` |

---

## 2. Plugin Manifest (`plugin.json`) Specifications

| Requirement / Field | Antigravity 2.0 | Antigravity CLI |
| :--- | :--- | :--- |
| **Schema Validation** | Permissive | Strict against `https://antigravity.google/schemas/v1/plugin.json` |
| **`name` field** | Optional (defaults to parent directory name) | **Required** (pattern: `^[a-zA-Z0-9-_]+$`) |
| **`description` field** | Optional string | Optional string |
| **`additionalProperties`** | Ignored | Enforced `false` |

> [!TIP]
> **Cross-Platform Compatibility Standard**: Always specify `"$schema": "https://antigravity.google/schemas/v1/plugin.json"`, a valid `name` conforming to `^[a-zA-Z0-9-_]+$`, and a `description`.

---

## 3. Plugin Deployment & CLI Management Pipeline

In AGY CLI, plugins can be inspected and managed programmatically via terminal subcommands:

```bash
# List installed plugins and loaded components
agy plugin list

# Stage and install a local plugin bundle
agy plugin install /path/to/plugin-directory

# Suspend plugin capabilities without deleting assets
agy plugin disable <plugin_name>

# Re-enable a suspended plugin
agy plugin enable <plugin_name>

# Purge plugin directory and unregister components
agy plugin uninstall <plugin_name>
```

---

## 4. Component Component Matrix

| Component | Directory Location inside Plugin | Supported in 2.0 | Supported in CLI |
| :--- | :--- | :---: | :---: |
| **Skills** | `skills/<skill-name>/SKILL.md` | Yes | Yes |
| **Rules** | `rules/<rule-name>.md` | Yes | Yes |
| **MCP Servers** | `mcp_config.json` | Yes | Yes |
| **Hooks** | `hooks.json` | Yes | Yes |
| **Custom Subagents** | `agents/<agent-name>.md` | Yes | Yes |
