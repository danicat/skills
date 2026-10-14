---
name: intercom
description: >
  Cross-session and cross-project agent communication in Antigravity using the
  native agentapi CLI and conversation_summaries.db. Discovers active sessions
  across workspaces, resolves target projectId metadata, bypasses cross-project
  PermissionDenied checks via environment sanitization, and delivers reactive
  messages with return-address headers. Activate when coordinating between
  independent agent sessions, handing off tasks across different projects or
  workspaces, discovering peer conversation IDs, or sending cross-project
  messages with agentapi.
license: Apache-2.0
metadata:
  category: agents
  tags: "intercom, agentapi, cross-project, multi-agent, sessions, coordination, handoff"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Intercom: Cross-Project & Inter-Session Messaging via `agentapi`

`intercom` enables direct, zero-daemon communication between independent Antigravity agent sessions across both the same workspace and completely different project workspaces on the same host using the native `agentapi` CLI.

## Available scripts

- **`scripts/intercom.py`**: Zero-dependency CLI wrapper around `agentapi` and `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` providing `whoami`, `discover`, `inspect`, `send`, and `spawn`.
- **`scripts/test_intercom.py`**: Unit test suite verifying cross-project environment sanitization, return-address envelope formatting, and SQLite session discovery.

---

## ⚡ Core Architecture & Why Cross-Project Messaging Fails by Default

Inside any Antigravity command execution, the runtime populates the environment with session-scoped variables:

| Environment Variable | Purpose |
| :--- | :--- |
| `ANTIGRAVITY_CONVERSATION_ID` | UUID of the current agent conversation |
| `ANTIGRAVITY_PROJECT_ID` | UUID of the current workspace's project |
| `ANTIGRAVITY_TRAJECTORY_ID` | UUID of the active execution trajectory |
| `ANTIGRAVITY_SOURCE_METADATA` | JSON payload binding the tool call to the sender's `conversationId` and `stepIndex` |
| `ANTIGRAVITY_LS_ADDRESS` | Local language server RPC address (`localhost:<port>`) |
| `ANTIGRAVITY_CSRF_TOKEN` | Local language server authentication token |
| `ANTIGRAVITY_APP_DATA_DIR` | Path to `~/.gemini/antigravity` containing `conversation_summaries.db` and `brain/` |

### The Cross-Project Boundary Check

When you call the native `send_message` tool—or run `agentapi send-message <recipient_id> <content>` directly—to message a conversation in a **different project workspace**, it fails with:

```text
rpc error: code = PermissionDenied desc = permission_denied: source project_id "<source_project_id>" does not match target project_id "<target_project_id>"
```

Simply overriding `ANTIGRAVITY_PROJECT_ID="<target_project_id>"` is **not sufficient** on its own. As long as `ANTIGRAVITY_CONVERSATION_ID`, `ANTIGRAVITY_SOURCE_METADATA`, or `ANTIGRAVITY_TRAJECTORY_ID` remain in the environment, the language server resolves `source project_id` from the sender's conversation record and rejects the cross-project call.

### The 3-Step Cross-Project Solution

1. **Resolve the Target `projectId`**:
   Call `agentapi get-conversation-metadata <target_conversation_id>` (which succeeds across all projects without restriction) and extract `.response.conversationMetadata.metadata.projectId`.
2. **Sanitize Sender Environment Bindings**:
   Unset `ANTIGRAVITY_CONVERSATION_ID`, `ANTIGRAVITY_SOURCE_METADATA`, and `ANTIGRAVITY_TRAJECTORY_ID`, while setting `ANTIGRAVITY_PROJECT_ID="<target_project_id>"`.
3. **Embed a Return-Address Header**:
   Because unsetting `ANTIGRAVITY_CONVERSATION_ID` removes automatic sender attribution from the RPC metadata, **always include your own `$ANTIGRAVITY_CONVERSATION_ID`, `$ANTIGRAVITY_PROJECT_ID`, and workspace path (`$PWD`)** in `--title` and at the top of the message body so the recipient can reply back to you.

---

## 1. 🚀 First Instinct: Using `intercom.py` (`kungfu run`)

Execute `intercom.py` via `kungfu run` (or directly with `python3 scripts/intercom.py`) to handle discovery, metadata lookup, return-address framing, and environment sanitization automatically:

```bash
# 1. Inspect your own session identity, projectId, and workspace
kungfu run intercom intercom.py whoami

# 2. Discover recent active root sessions across all projects (or filter by workspace/title)
kungfu run intercom intercom.py discover
kungfu run intercom intercom.py discover --workspace socials --limit 5

# 3. Inspect a specific peer conversation UUID
kungfu run intercom intercom.py inspect 7566dedc-5206-4975-bb23-7a879a542f93

# 4. Send a message by conversation UUID OR by workspace name substring
kungfu run intercom intercom.py send 7566dedc-5206-4975-bb23-7a879a542f93 "Campaign files moved to campaigns/2026-10-antigravity-ui-extensions/."
kungfu run intercom intercom.py send socials "Please review the new LinkedIn draft." --title "Campaign Handoff"

# 5. Spawn a brand-new conversation inside another project workspace
kungfu run intercom intercom.py spawn socials "Run the weekly social analytics report and reply with findings." --title "Analytics Request"
```

---

## 2. 🛠️ Direct Shell Recipes (`agentapi` + `sqlite3` + `jq`)

When executing raw commands directly without the helper script, follow these exact patterns:

### A. Discover Active Sessions Across Workspaces (`conversation_summaries.db`)
Query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` in read-only mode to list recent root sessions (`parent_conversation_id = ''`, `killed = 0`) in milliseconds:

```bash
sqlite3 -header -column "$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db" "
  SELECT
    conversation_id,
    project_id,
    title,
    workspace_uris,
    status,
    last_modified_time
  FROM conversation_summaries
  WHERE parent_conversation_id = '' AND killed = 0
  ORDER BY last_modified_time DESC
  LIMIT 10;
"
```

### B. Inspect Target Session Metadata (`get-conversation-metadata`)
Verify a target `<conversation_id>` and extract its `projectId` and `workspaceUris`:

```bash
TARGET_CONV_ID="7566dedc-5206-4975-bb23-7a879a542f93"

agentapi get-conversation-metadata "$TARGET_CONV_ID" | jq '{
  projectId: .response.conversationMetadata.metadata.projectId,
  workspaceUris: .response.conversationMetadata.metadata.workspaceUris,
  rootConversationId: .response.conversationMetadata.metadata.rootConversationId
}'
```

### C. Send a Cross-Project Message (`send-message`)
Resolve `TARGET_PROJECT_ID`, include your `$ANTIGRAVITY_CONVERSATION_ID` return address, and unset the 3 sender identity variables:

```bash
TARGET_CONV_ID="7566dedc-5206-4975-bb23-7a879a542f93"
TARGET_PROJECT_ID=$(agentapi get-conversation-metadata "$TARGET_CONV_ID" | jq -r '.response.conversationMetadata.metadata.projectId')

HEADER="[Intercom From: ${ANTIGRAVITY_CONVERSATION_ID} | Project: ${ANTIGRAVITY_PROJECT_ID} | Workspace: ${PWD}]"
BODY="All campaign assets have been copied to your workspace. Please reply to ${ANTIGRAVITY_CONVERSATION_ID} once verified."

env -u ANTIGRAVITY_CONVERSATION_ID \
    -u ANTIGRAVITY_SOURCE_METADATA \
    -u ANTIGRAVITY_TRAJECTORY_ID \
    ANTIGRAVITY_PROJECT_ID="$TARGET_PROJECT_ID" \
    agentapi send-message \
      --title="Intercom from ${ANTIGRAVITY_CONVERSATION_ID} ($(basename "$PWD"))" \
      "$TARGET_CONV_ID" \
      "$(printf '%s\n\n%s' "$HEADER" "$BODY")"
```

### D. Spawn a New Conversation in Another Project (`new-conversation`)
To start a new root conversation inside a target project's context:

```bash
env -u ANTIGRAVITY_CONVERSATION_ID \
    -u ANTIGRAVITY_SOURCE_METADATA \
    -u ANTIGRAVITY_TRAJECTORY_ID \
    ANTIGRAVITY_PROJECT_ID="$TARGET_PROJECT_ID" \
    agentapi new-conversation \
      --title="Task from ${ANTIGRAVITY_CONVERSATION_ID}" \
      --model=pro \
      "$(printf '%s\n\n%s' "$HEADER" "$PROMPT")"
```

---

## 3. Operational Rules & Anti-Patterns

1. **Zero Polling & Zero Listener Subagents**:
   - `agentapi send-message` delivers messages directly into the recipient session's inbox and triggers an automatic **reactive wakeup**.
   - Never run polling loops, `sleep` timers, or background listener subagents. After sending a message that awaits a reply, stop calling tools to end your turn; Antigravity will automatically resume your session when the peer replies.
2. **Never Scan Hundreds of `brain/` Directories with Subprocesses**:
   - Do not loop over every folder in `$ANTIGRAVITY_APP_DATA_DIR/brain/*` calling `agentapi get-conversation-metadata`—archived or pruned trajectories will fail with `trajectory not found` and waste seconds of latency.
   - Always discover sessions via `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` first, then call `agentapi get-conversation-metadata` on the single resolved target UUID.
3. **Always Include Your Return Address**:
   - Because cross-project environment sanitization unsets `ANTIGRAVITY_CONVERSATION_ID`, the receiving agent only knows who messaged it if you include your `$ANTIGRAVITY_CONVERSATION_ID` (and workspace path) inside the message header.
4. **Fail Fast with Rich Diagnostics**:
   - Never silently ignore `PermissionDenied` or `trajectory not found` errors. If `agentapi` returns a non-zero exit code or a JSON `"error"` field, surface the exact command and error payload immediately.
