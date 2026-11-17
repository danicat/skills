---
name: buffer
description: >
  Manage, draft, schedule, and publish social media content across connected
  channels (LinkedIn, X/Twitter, Bluesky, Threads, and Instagram) using the
  Buffer CLI (@bufferapp/cli). Covers channel discovery, dry-run validation,
  approval-gated queue scheduling, draft ideas, and live schema inspection.
  Activate when scheduling social media posts, inspecting Buffer channels,
  or automating social publishing workflows.
license: Apache-2.0
metadata:
  category: writing
  tags: "buffer, social-media, scheduling, publishing, cli"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Buffer CLI playbook

Procedures, command workflows, and safety gates for scheduling social media posts, managing channels, and automating publication workflows through the Buffer CLI (`@bufferapp/cli`).

---

## Architecture and progressive disclosure

To reduce token overhead, `SKILL.md` keeps core operational commands, safety gates, and high-risk pitfalls directly in the body. Load specialized references on demand:

- **Automation workflows**: Read [references/workflows.md](references/workflows.md) for shell scripting patterns, timezone checks, approval gates, and bounded pagination.
- **Rate limits and retry rules**: Read [references/rate_limits.md](references/rate_limits.md) for `429` wait intervals, retry matrices, and duplicate-post prevention.

---

## 1. Bootstrapping and installation

The Buffer CLI wraps Buffer's public `GraphQL` API and returns structured JSON with predictable exit codes.

### Agent bootstrap sequence

When running in a new environment or container, run this verification sequence (requires `Node.js 20+`):

```bash
# 1. Check whether the Buffer CLI is installed (requires Node.js 20+)
if ! command -v buffer >/dev/null; then
  echo "Buffer CLI not found. Run via npx or ask user confirmation before global install:" >&2
  npx --yes @bufferapp/cli --version
else
  buffer --version
fi

# 2. Diagnose config, API token, and network reachability
buffer doctor
```

> [!TIP]
> To install the CLI globally after confirming with the user, run `npm install -g @bufferapp/cli`. In ephemeral sandboxes where global installation is restricted, invoke commands with `npx --yes @bufferapp/cli`.

### Authentication modes

1. **Environment variable (recommended for CI and headless runs):**
   ```bash
   export BUFFER_API_KEY="your-api-key"
   ```
2. **Global configuration (`buffer init`):**
   ```bash
   buffer init
   ```
   *Writes the API token, default organization, and timezone to `$XDG_CONFIG_HOME/buffer/config.json` (or `~/.config/buffer/config.json`).*

---

## 2. Core operational workflows

> [!IMPORTANT]
> Always pass `--output json` in automated scripts so machine parsers receive structured output without terminal formatting.

### Workflow A: Channel discovery and account inspection

Always inspect available channels before dispatching posts to resolve target `channelId` values:

```bash
# Inspect account details and default organization
buffer account --output json

# List all connected social channels (LinkedIn, X, Bluesky, Threads, Instagram, etc.)
buffer channels list --output json

# Get detailed metadata and posting schedule for a specific channel
buffer channels get --id "<channel-id>" --output json
```

---

### Workflow B: Safe post creation and scheduling

Always run `--dry-run` first to validate the payload structure locally before requesting live publication:

```bash
# Step 1: Dry-run validation
buffer posts create \
  --channel-id "<channel-id>" \
  --scheduling-type automatic \
  --mode addToQueue \
  --text "Your post content here" \
  --dry-run
```

> [!IMPORTANT]
> **Human-in-the-loop dispatch gate**: Never run a live `buffer posts create` command without explicit user approval. After `--dry-run` succeeds, present a concise summary of the target channel name and `channelId`, exact post text, `assets` array count and public media URLs matching intended attachments, and scheduling mode (`addToQueue`, `shareNow`, `shareNext`, or `customScheduled` with local `dueAt` offset). Wait for confirmation before running Step 2.

```bash
# Step 2: Live creation after explicit user confirmation
buffer posts create \
  --channel-id "<channel-id>" \
  --scheduling-type automatic \
  --mode addToQueue \
  --text "Your post content here" \
  --output json
```

#### Media hosting requirement (no local file uploads)

> [!WARNING]
> **Buffer does not support direct file uploads**: Buffer's API and CLI reject raw binary attachments or local file paths (such as `path/to/image.png`).
> To attach images or videos, host the files at a public HTTP or HTTPS URL (such as S3, Google Cloud Storage, GitHub raw content, or a CDN) so Buffer can fetch them during post ingestion.

Pass hosted media URLs through the `assets` array in a JSON payload:

```json
{
  "channelId": "channel_123",
  "schedulingType": "automatic",
  "mode": "addToQueue",
  "text": "Announcing our new open-source release!",
  "assets": [
    {
      "image": {
        "url": "https://cdn.example.com/images/architecture-diagram.png",
        "metadata": {
          "altText": "Architecture diagram illustrating worker pool"
        }
      }
    }
  ]
}
```

For videos, pass the public video URL:
```json
{
  "channelId": "channel_123",
  "schedulingType": "automatic",
  "mode": "addToQueue",
  "text": "Watch the terminal recording in action:",
  "assets": [
    {
      "video": {
        "url": "https://cdn.example.com/videos/demo.mp4"
      }
    }
  ]
}
```

#### Passing payloads via JSON or file

For multi-line text, media attachments, or nested channel options:

```bash
# Inline JSON payload with hosted media
buffer posts create --json '{
  "channelId": "channel_123",
  "schedulingType": "automatic",
  "mode": "addToQueue",
  "text": "Line 1\n\nLine 2 with links",
  "assets": [
    {
      "image": {
        "url": "https://cdn.example.com/diagram.png",
        "metadata": { "altText": "Architecture diagram" }
      }
    }
  ]
}' --output json

# Read payload from file
buffer posts create --input post_payload.json --output json

# Pipe payload from stdin
cat post_payload.json | buffer posts create --input - --output json
```

---

### Workflow C: Drafting ideas

Create draft ideas in Buffer without assigning them to a channel queue yet:

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

### Workflow D: Inspecting and monitoring scheduled posts

```bash
# List recent posts on a channel
buffer posts list --channel-id "<channel-id>" --output json

# Fetch specific post status
buffer posts get --id "<post-id>" --output json
```

---

## 3. Field selection (`--fields`)

To reduce payload sizes and save tokens, filter responses using comma-separated dot-notation paths or brace expansion:

```bash
# Select top-level and nested properties
buffer posts get --id "<post-id>" --fields id,text,channel.name --output json

# Brace expansion for list connections
buffer posts list --channel-id "<channel-id>" --fields 'items.{id,text,status},pageInfo.endCursor' --output json

# Retrieve complete upstream payload
buffer posts get --id "<post-id>" --fields all --output json
```

---

## 4. Live schema inspection

When building payloads with unfamiliar parameters or allowed values, inspect the live schema directly:

```bash
# List all available command groups
buffer schema list

# Inspect exact input types, enum values, and output shapes for a command
buffer schema describe posts create
```

---

## 5. Global flags and exit codes

### Global flags

| Flag | Description | Best Practice |
| :--- | :--- | :--- |
| `--output <json\|pretty\|auto>` | Output renderer format | Always pass `--output json` in automation |
| `--dry-run` | Validates input locally without network calls | Always run before stateful mutations |
| `--quiet` | Suppress spinners and `stderr` notices | Use only when `stderr` noise breaks JSON pipelines |
| `--verbose` | Print rate-limit summary after requests | Useful for inspecting throughput headroom |
| `--timeout <ms>` | Command timeout in milliseconds (default: `30000`) | Raise for slow connections or large responses |

### Exit code reference

| Exit Code | Classification | Cause and Remediation |
| :---: | :--- | :--- |
| **`0`** | Success | Command completed without errors. |
| **`1`** | General Error | Runtime failure. Inspect the error message on `stderr`. |
| **`2`** | Usage / Validation Error | Missing required flags, invalid JSON, or schema mismatch. Run `buffer schema describe <group> <cmd>`. |
| **`3`** | API Error | Upstream API error or rate limit exhaustion. Inspect returned error details. |
| **`4`** | Authentication Error | Missing or invalid token. Run `buffer doctor` or export `BUFFER_API_KEY`. |

---

## 6. Critical pitfalls and payload rules

Review these high-risk failure modes before building commands and JSON payloads:

### 1. Media hosting and file attachments
- **No local file uploads**: You cannot attach local file paths. Every item in `assets` (`assets[].image.url` or `assets[].video.url`) **must use a public HTTP or HTTPS URL**.
- **Empty `text` without assets fails**: Most channels reject posts that contain neither text nor a media asset.
- **Asset parity**: Verify `len(assets)` matches the number of intended attachments before dispatch.

### 2. Scheduling modes and notification traps
- **`mode: addToQueue` is queued, not immediate**: Use `mode: shareNow` to publish at once. Use `mode: shareNext` to jump to the front of the queue. Use `mode: customScheduled` with an explicit `dueAt` timestamp.
- **`schedulingType: notification` does not auto-publish**: It sends a reminder notification to the Buffer mobile app instead of publishing automatically. Always use `schedulingType: automatic` for hands-off scheduling.
- **`addToQueue` on a channel with no schedule**: Lands in an unscheduled queue state without a publish slot. Inspect the schedule with `buffer channels get --id "<channel-id>"` first.
- **All times must be ISO-8601 with offset**: `dueAt` requires a timezone offset (such as `2026-05-06T17:00:00-05:00`). Read the configured offset from `buffer account --fields timezone` rather than assuming UTC.

### 3. Identifier integrity
- **Never guess channel IDs**: Always resolve valid IDs from `buffer channels list --output json`. Invalid IDs can pass local parsing and fail upstream with unclear errors.
- **IDs stay scoped to one organization**: A `channelId` from Organization A cannot be used while authenticated to Organization B.

### 4. Input and formatting constraints
- **`--json` overrides CLI flags**: When both `--json` and flat flags are passed, the CLI ignores flat flags. Use one style or the other.
- **Nested fields need `--json` or `--input`**: Service options under `metadata.*` and `assets.*` cannot be expressed with flat CLI flags.
- **Strip control characters**: ASCII control characters (`U+0000` to `U+001F` except whitespace) cause payload rejections.

### 5. Per-service requirements, length caps, and threading
- **X / Twitter**: `280` characters per post on standard queues and thread items. Long-form posts (`800` to `2,500` characters) require a confirmed X Premium channel; verify channel tier and run `--dry-run` before dispatching. When chaining posts via `metadata.twitter.thread`, the top-level `text` **must** match the first thread item's `text`:
  ```json
  {
    "channelId": "ch_123",
    "text": "First tweet in thread",
    "metadata": {
      "twitter": {
        "thread": [
          { "text": "First tweet in thread" },
          { "text": "Second tweet in thread" }
        ]
      }
    }
  }
  ```
- **`Bluesky`**: `300` graphemes per post; requires `text` or media assets.
- **Threads**: `500` characters per post; requires `text` or media assets.
- **`Mastodon`**: Requires `text` or media assets (`500` characters on standard instances).
- **LinkedIn**: `3,000` characters per post; accepts `text` or `assets`, and document posts require `metadata.linkedin.linkAttachment`.
- **Instagram**: `2,200` characters per caption; requires at least one image or video asset, plus `metadata.instagram.type` and `metadata.instagram.shouldShareToFeed`.
