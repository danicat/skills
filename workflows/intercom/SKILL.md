---
name: intercom
description: >
  Cross-project and cross-session collaboration between Antigravity agents using
  the agentapi CLI and conversation_summaries.db. Finds active peer sessions
  across workspaces, looks up target project IDs, routes messages to other
  projects with return-address headers, and starts new sessions across
  workspaces. Activate when collaborating between agents in different projects,
  handing off tasks across workspaces, finding peer session IDs, or sending
  cross-project messages with agentapi.
license: Apache-2.0
metadata:
  category: workflows
  tags: "agentapi, cross-project, multi-agent, sessions, coordination, handoff"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.2"
  catalog: https://skills.danicat.dev
---

# Intercom: cross-project agent collaboration with `agentapi`

`intercom` lets Antigravity agents in separate project workspaces talk to each other and share work. It uses the built-in `agentapi` CLI and `sqlite3` so agents on the same host can work as a team across projects.

---

## How cross-project messaging works

The built-in `send_message` tool only reaches agents in the same project workspace. To work with an agent in another project, use the `agentapi` CLI.

When a session runs a command, Antigravity sets shell variables for the current workspace:

| Shell variable | Purpose |
| :--- | :--- |
| `ANTIGRAVITY_CONVERSATION_ID` | ID of your current agent session. |
| `ANTIGRAVITY_PROJECT_ID` | ID of your current project. |
| `ANTIGRAVITY_TRAJECTORY_ID` | ID of your active run. |
| `ANTIGRAVITY_SOURCE_METADATA` | JSON linking the command to your session and step. |
| `ANTIGRAVITY_LS_ADDRESS` | Local server address. |
| `ANTIGRAVITY_CSRF_TOKEN` | Local server auth token. |
| `ANTIGRAVITY_APP_DATA_DIR` | Path to `~/.gemini/antigravity`. |

By default, `agentapi` reads these variables and connects to your current project. If you pass a session ID from another project while your own session variables are still set, the project IDs won't match.

### The 3-step cross-project handshake

1. **Look up the target `projectId`**:
   Query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` or run `agentapi get-conversation-metadata <target_conversation_id>` to get the other session's `projectId`.
2. **Scope `agentapi` to the target project**:
   Set `ANTIGRAVITY_PROJECT_ID="<target_project_id>"` and clear `ANTIGRAVITY_CONVERSATION_ID`, `ANTIGRAVITY_SOURCE_METADATA`, and `ANTIGRAVITY_TRAJECTORY_ID` with `env -u` for that command. This connects `agentapi` to the other agent's project workspace.
3. **Add a return-address header**:
   Clearing `ANTIGRAVITY_CONVERSATION_ID` means the CLI call doesn't send your session ID on its own. Include your `$ANTIGRAVITY_CONVERSATION_ID`, `$ANTIGRAVITY_PROJECT_ID`, and workspace path `$PWD` in `--title` and at the top of the message body so the other agent knows who wrote and how to reply.

---

## 1. Find active sessions across workspaces

When the user names a target session by workspace or topic instead of an ID, such as *"send this to the socials session,"* query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db`:

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

# Filter for the most recently active root session in a specific workspace (for example, 'socials')
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

## 2. Check target session metadata

Query `agentapi` to check the target session's live `projectId` and workspace paths:

```bash
TARGET_CONV_ID="7566dedc-5206-4975-bb23-7a879a542f93"

agentapi get-conversation-metadata "$TARGET_CONV_ID" | jq '{
  projectId: .response.conversationMetadata.metadata.projectId,
  workspaceUris: .response.conversationMetadata.metadata.workspaceUris,
  rootConversationId: .response.conversationMetadata.metadata.rootConversationId
}'
```

---

## 3. Send a cross-project message

Get `TARGET_PROJECT_ID`, add your return header, and run `agentapi send-message` for the target project:

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

## 4. Start a new session in another project

Run `agentapi new-conversation` to start a new root session in another project:

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

## 5. Usage rules and common pitfalls

1. **No polling or listener subagents**:
   - `agentapi send-message` delivers your note straight to the other session's inbox and wakes it up.
   - Never run polling loops, `sleep` timers, or listener subagents. Once you send a message and need a reply, stop calling tools to end your turn. Antigravity resumes your session when the other agent replies.
2. **Never loop `agentapi` over `brain/` folders**:
   - Don't loop through `$ANTIGRAVITY_APP_DATA_DIR/brain/*` to run `agentapi get-conversation-metadata`. Old or deleted runs fail with `trajectory not found` and waste time.
   - Query `$ANTIGRAVITY_APP_DATA_DIR/conversation_summaries.db` with `sqlite3` first, then call `agentapi` on the single target session ID.
3. **Always include your return address**:
   - Because `env -u ANTIGRAVITY_CONVERSATION_ID` clears your session ID from the CLI call, the other agent only knows who wrote if you put `$ANTIGRAVITY_CONVERSATION_ID`, `$ANTIGRAVITY_PROJECT_ID`, and `$PWD` in the message header.
4. **Fail fast with clear errors**:
   - Never ignore `agentapi` errors. Check the JSON output from `agentapi` and report any `"error"` field right away.
