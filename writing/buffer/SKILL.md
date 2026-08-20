---
name: buffer
description: >
  Manage, draft, schedule, and publish social media content across connected
  channels using the Buffer CLI (@bufferapp/cli). Use this skill when listing
  connected Buffer social channels, inspecting accounts, creating ideas,
  scheduling posts to queues, validating payloads via --dry-run, querying post
  statuses, introspecting Buffer GraphQL schemas, or diagnosing Buffer
  authentication and environment issues. Activate whenever interacting with
  Buffer or automating cross-platform social publishing from the terminal.
license: Apache-2.0
metadata:
  category: writing
  tags: "writing, social-media, buffer, publishing, automation, cli"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  homepage: https://skills.danicat.dev/writing/buffer/
  canonical: https://skills.danicat.dev/writing/buffer/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/writing/buffer
---

# Buffer CLI Playbook

Procedures, command workflows, and safety gates for scheduling social media posts, managing channels, and automating publication workflows via the Buffer CLI (`@bufferapp/cli`).

---

## Architecture & Progressive Disclosure

To minimize context consumption, `SKILL.md` contains core operational commands and safety rules. Load specialized references on demand:

- **Pitfalls & Service Schemas**: Read [references/pitfalls.md](references/pitfalls.md) before composing payloads for complex networks (Instagram, Pinterest, YouTube, Twitter Threads).
- **Automation Workflows**: Read [references/workflows.md](references/workflows.md) for shell scripting patterns, timezone math, and Relay cursor pagination.
- **Rate Limits & Idempotency**: Read [references/rate_limits.md](references/rate_limits.md) for 429 backoff algorithms, retry matrices, and duplicate-post prevention.

---

## 1. Bootstrapping & Installation

The Buffer CLI is generated from Buffer's public GraphQL schema, returning structured JSON with predictable error handling.

### Agent Bootstrap Sequence

When running in a new environment or container, follow this self-bootstrapping sequence:

```bash
# 1. Check if the Buffer CLI is already installed
if ! command -v buffer &> /dev/null; then
  echo "Buffer CLI not found. Installing globally via npm (requires Node.js 18+)..."
  npm install -g @bufferapp/cli
fi

# 2. Verify installation version
buffer --version

# 3. Diagnose environment, config, API token, and network reachability
buffer doctor
```

> [!TIP]
> In ephemeral sandbox environments where global npm installation is restricted, you can invoke the CLI on the fly using `npx`:
> ```bash
> npx -y @bufferapp/cli doctor
> ```

### Authentication Modes

1. **Environment Variable (Recommended for CI / Ephemeral Agents):**
   ```bash
   export BUFFER_API_KEY="your-api-key"
   ```
2. **Global Configuration (`buffer init`):**
   ```bash
   buffer init
   ```
   *Writes API token, default organization, and timezone to `$XDG_CONFIG_HOME/buffer/config.json` (or `~/.config/buffer/config.json`).*

---

## 2. Core Operational Workflows

> [!IMPORTANT]
> Always use `--output json` when invoking commands within automated scripts or agent subshells to ensure clean machine parsing.

### Workflow A: Channel Discovery & Account Inspection

Always inspect available channels before dispatching posts to resolve target `channelId`s:

```bash
# Inspect account details and default organization
buffer account --output json

# List all connected social channels (LinkedIn, X, Bluesky, Threads, Instagram, etc.)
buffer channels list --output json

# Get detailed metadata for a specific channel
buffer channels get --id "<channel-id>" --output json
```

---

### Workflow B: Safe Post Creation & Scheduling

Always execute with `--dry-run` first to validate the payload structure before sending live mutations:

```bash
# Step 1: Dry run validation
buffer posts create \
  --channel-id "<channel-id>" \
  --scheduling-type automatic \
  --mode addToQueue \
  --text "Your post content here" \
  --dry-run

# Step 2: Live creation (Add to channel queue)
buffer posts create \
  --channel-id "<channel-id>" \
  --scheduling-type automatic \
  --mode addToQueue \
  --text "Your post content here" \
  --output json
```

#### Passing Payloads via JSON or File

For complex multi-line text, media attachments, or structured objects:

```bash
# Inline JSON payload
buffer posts create --json '{
  "channelId": "channel_123",
  "schedulingType": "automatic",
  "mode": "addToQueue",
  "text": "Line 1\n\nLine 2 with links"
}' --output json

# Read payload from file
buffer posts create --input post_payload.json --output json

# Pipe payload from stdin
cat post_payload.json | buffer posts create --input - --output json
```

---

### Workflow C: Drafting Ideas

Create draft thoughts and ideas in Buffer without assigning them immediately to a channel queue:

```bash
# Create an idea in an organization
buffer ideas create \
  --organization-id "<org-id>" \
  --text "Draft angle for next week's release" \
  --output json

# Create an idea with structured JSON
buffer ideas create --json '{
  "organizationId": "org_123",
  "content": { "text": "Architectural breakdown draft" }
}' --output json
```

---

### Workflow D: Inspecting & Monitoring Scheduled Posts

```bash
# List recent posts on a channel
buffer posts list --channel-id "<channel-id>" --output json

# Fetch specific post status
buffer posts get --id "<post-id>" --output json
```

---

## 3. Field Selection (`--fields`)

To minimize payload sizes and optimize context tokens, filter responses using comma-separated dot-notation paths or brace expansion:

```bash
# Select top-level and nested properties
buffer posts get --id "<post-id>" --fields id,text,channel.name --output json

# Brace expansion for list connections
buffer posts list --channel-id "<channel-id>" --fields 'items.{id,text,status},pageInfo.endCursor' --output json

# Retrieve complete GraphQL payload
buffer posts get --id "<post-id>" --fields all --output json
```

---

## 4. Dynamic Schema Introspection

When crafting payloads with unknown parameters or enums, query the live schema directly:

```bash
# List all available command groups
buffer schema list

# Inspect exact input types, enum values, and output shapes for a command
buffer schema describe posts create
```

---

## 5. Global Flags & Exit Codes

### Global Flags

| Flag | Description | Best Practice |
| :--- | :--- | :--- |
| `--output <json\|pretty\|auto>` | Output renderer format | Always specify `--output json` in agent tooling |
| `--dry-run` | Validates input locally without network calls | Always run before stateful mutations |
| `--quiet` | Suppress spinners and stderr notices | Recommended for headless execution |
| `--verbose` | Print rate-limit summary after requests | Useful for debugging throughput limits |
| `--timeout <ms>` | Command timeout in milliseconds (default: 30000) | Set appropriately for large batch requests |

### Exit Code Reference

| Exit Code | Classification | Cause & Agent Remediation |
| :---: | :--- | :--- |
| **`0`** | Success | Command completed successfully. |
| **`1`** | General Error | Runtime failure. Check error message on stderr. |
| **`2`** | Usage / Validation Error | Missing required flags, invalid JSON, or schema mismatch. Run `buffer schema describe <group> <cmd>`. |
| **`3`** | API Error | GraphQL upstream error or rate limit exhaustion. Inspect returned error details. |
| **`4`** | Authentication Error | Missing or invalid token. Run `buffer doctor` or export `BUFFER_API_KEY`. |
