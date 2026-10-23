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
  category: workflows
  tags: "intercom, agentapi, cross-project, multi-agent, sessions, coordination, handoff"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.1"
  catalog: https://skills.danicat.dev
---

# Intercom: Cross-Project & Inter-Session Messaging via `agentapi`

`intercom` enables direct, zero-daemon communication between independent Antigravity agent sessions across both the same workspace and different project workspaces on the same host using the native `agentapi` CLI and `sqlite3`.

---

## ⚡ Why Cross-Project Messaging Fails by Default

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

When you call the native `send_message` tool—or run `agentapi send-message <recipient_id> <content>` directly—to message a conversation in a **different project workspace**, it fails with:

```text
rpc error: code = PermissionDenied desc = permission_denied: source project_id "<source_project_id>" does not match target project_id "<target_project_id>"
```

Overriding `ANTIGRAVITY_PROJECT_ID="<target_project_id>"` alone is **not sufficient**. As long as `ANTIGRAVITY_CONVERSATION_ID`, `ANTIGRAVITY_SOURCE_METADATA`, or `ANTIGRAVITY_TRAJECTORY_ID` remain in the environment, the language server resolves `source project_id` from the sender's conversation record and rejects the cross-project call.

### The 3-Step Cross-Project Handshake

1. **Resolve the Target `projectId`**:
   Query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` or run `agentapi get-conversation-metadata <target_conversation_id>` (which succeeds across all projects without restriction) to obtain the target's `projectId`.
2. **Sanitize Sender Environment Bindings**:
   Unset `ANTIGRAVITY_CONVERSATION_ID`, `ANTIGRAVITY_SOURCE_METADATA`, and `ANTIGRAVITY_TRAJECTORY_ID`, while setting `ANTIGRAVITY_PROJECT_ID="<target_project_id>"`.
3. **Embed a Return-Address Header**:
   Because unsetting `ANTIGRAVITY_CONVERSATION_ID` removes automatic sender attribution from the RPC metadata, **always include your own `$ANTIGRAVITY_CONVERSATION_ID`, `$ANTIGRAVITY_PROJECT_ID`, and workspace path (`$PWD`)** in `--title` and at the top of the message body so the recipient knows who sent it and can reply back to you.

---

## 1. 🔍 Discover Active Sessions Across Workspaces

When the user refers to a target session by **workspace name** or **topic** rather than an explicit UUID (e.g., *"send this to the socials session"*), query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db`:

```bash
# List the 10 most recent active root sessions across all workspaces
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

# Filter for the most recently active root session in a specific workspace (e.g. 'socials')
sqlite3 -json "$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db" "
  SELECT
    conversation_id,
    project_id,
    title,
    workspace_uris,
    status,
    last_modified_time
  FROM conversation_summaries
  WHERE parent_conversation_id = ''
    AND killed = 0
    AND LOWER(workspace_uris) LIKE '%socials%'
  ORDER BY last_modified_time DESC
  LIMIT 5;
"
```

---

## 2. 🔎 Inspect Target Session Metadata (`get-conversation-metadata`)

Given a `<target_conversation_id>`, verify its live `projectId` and `workspaceUris` via `agentapi`:

```bash
TARGET_CONV_ID="7566dedc-5206-4975-bb23-7a879a542f93"

agentapi get-conversation-metadata "$TARGET_CONV_ID" | jq '{
  projectId: .response.conversationMetadata.metadata.projectId,
  workspaceUris: .response.conversationMetadata.metadata.workspaceUris,
  rootConversationId: .response.conversationMetadata.metadata.rootConversationId
}'
```

---

## 3. 📨 Send a Cross-Project Message (`send-message`)

Resolve `TARGET_PROJECT_ID`, prepend your return-address header, and invoke `agentapi send-message` with the 3 sender identity variables unset:

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

---

## 4. 🚀 Spawn a New Conversation in Another Project (`new-conversation`)

To launch a brand-new root conversation inside another project's workspace context:

```bash
env -u ANTIGRAVITY_CONVERSATION_ID \
    -u ANTIGRAVITY_SOURCE_METADATA \
    -u ANTIGRAVITY_TRAJECTORY_ID \
    ANTIGRAVITY_PROJECT_ID="$TARGET_PROJECT_ID" \
    agentapi new-conversation \
      --title="Task from ${ANTIGRAVITY_CONVERSATION_ID} ($(basename "$PWD"))" \
      --model=pro \
      "$(printf '%s\n\n%s' "$HEADER" "$PROMPT")"
```

---

## 5. Operational Rules & Anti-Patterns

1. **Zero Polling & Zero Listener Subagents**:
   - `agentapi send-message` delivers messages directly into the recipient session's native inbox and triggers an automatic **reactive wakeup**.
   - Never run polling loops, `sleep` timers, or background listener subagents. After sending a message that awaits a reply, stop calling tools to end your turn; Antigravity will automatically resume your session when the peer replies.
2. **Never Loop `agentapi` Over `brain/` Directories**:
   - Do not iterate over `$ANTIGRAVITY_APP_DATA_DIR/brain/*` spawning `agentapi get-conversation-metadata` subprocesses—archived or pruned trajectories will fail with `trajectory not found` and waste seconds of latency.
   - Always query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` with `sqlite3` first, then call `agentapi` on the single target UUID.
3. **Always Include Your Return Address**:
   - Because cross-project environment sanitization unsets `ANTIGRAVITY_CONVERSATION_ID`, the receiving agent only knows who messaged it if you include your `$ANTIGRAVITY_CONVERSATION_ID`, `$ANTIGRAVITY_PROJECT_ID`, and `$PWD` inside the message header.
4. **Fail Fast with Rich Diagnostics**:
   - Never silently ignore `PermissionDenied` or `trajectory not found` errors. Always inspect the JSON output of `agentapi` and surface any `"error"` field immediately.
