---
name: show-me-the-money
description: >
  Mine local conversation history and git logs using parallel Flash/Flash-Lite
  agy CLI workers to recover high-value features that were discussed and never
  implemented. Runs one fast Flash worker per conversation to list all features
  with a binary implemented/not-implemented flag, protecting frontier quota.
  Activate when looking for forgotten features, mining past sessions for
  unfinished work, or asking "what did I forget to build?".
license: Apache-2.0
metadata:
  category: agents
  tags: "backlog, transcripts, productivity, discovery, roadmap, prioritization"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Backlog recovery

Recover high-value features discussed in past sessions that never shipped, without burning frontier quota. Run one fast `agy` Flash worker per session to read the full dialogue and `git log`. Each worker outputs a single message listing every feature discussed as `IMPLEMENTED` or `NOT IMPLEMENTED`, so you can keep the unfinished winners.

## 1. Offload reading to `agy` Flash workers

Check your agent tier in the system prompt. When running on a frontier tier such as **Gemini 4 Argon** or **Pro**:

- **Never read raw `transcript.jsonl` files in the main session.**
- **Never call `invoke_subagent` for transcript mining.** Subagents inherit your frontier tier and burn high-cost quota.
- **Always spawn one headless `agy` CLI worker per session** pinned to a fast Flash tier such as `flash-lite` or `flash-low`.

Select the fastest Flash tier from `agy models`:

```bash
FLASH_MODEL=$(agy models | awk '/flash-lite|flash.*low/ {print $1; exit}')
```

## 2. List root sessions

Query `$HOME/.gemini/antigravity/conversation_summaries.db` with `sqlite3` to list root sessions where `parent_conversation_id = ''` from the last **30 days** across all workspaces. Skip the current session.

```bash
sqlite3 -json "$HOME/.gemini/antigravity/conversation_summaries.db" "
  SELECT
    conversation_id,
    title,
    workspace_uris,
    step_count,
    datetime(last_modified_time) AS last_active
  FROM conversation_summaries
  WHERE parent_conversation_id = ''
    AND killed = 0
    AND step_count > 4
    AND last_modified_time >= datetime('now', '-30 days')
  ORDER BY workspace_uris, last_modified_time DESC;
"
```

## 3. Run one worker per session

Focus only on the human-agent dialogue and git history. Ignore tool call logs, `ask_question` choices, system messages, and scratch files.

For each session, extract the non-empty `USER_INPUT` and `PLANNER_RESPONSE` messages from `transcript.jsonl`, plus the last 50 commits from `git log` when the workspace exists on disk. Pass both inside `-p="..."` because `agy -p` ignores `stdin` in text mode. Ask the worker to return a single message listing all features discussed as `IMPLEMENTED` or `NOT IMPLEMENTED`:

```bash
FLOW=$(jq -r '
  select((.type == "USER_INPUT" or .type == "PLANNER_RESPONSE") and (.content | length > 0))
  | "[\(.step_index) \(.type)]: \(.content)"
' "$HOME/.gemini/antigravity/brain/${CONV_ID}/.system_generated/logs/transcript.jsonl")

GIT_LOG=$(git -C "$WORKSPACE_PATH" log --oneline -n 50 2>/dev/null)

agy --model "$FLASH_MODEL" --disable-slash-commands -p="Do not call any tools.
Read the conversation and git log below, and output a single message listing all features discussed with a binary status (IMPLEMENTED or NOT IMPLEMENTED).
For each feature, include:
- Status: IMPLEMENTED or NOT IMPLEMENTED
- Feature: short title and description
- Reasoning: why it was discussed
- Last known status: what happened to it in the conversation or git log
- Expected value: High, Medium, or Low (and why)

Session: ${TITLE} (${CONV_ID})
Git log:
${GIT_LOG}

Conversation:
${FLOW}" > "/tmp/smtm-${CONV_ID}.md"
```

Run up to six `agy` workers in parallel background jobs using `&` and `wait`, then read `/tmp/smtm-*.md` in the main session.

## 4. Filter and rank the backlog

Review the `NOT IMPLEMENTED` items across all worker reports. Keep features left behind when the topic shifted or the session ended early, and drop ideas that the user rejected or replaced with a better design.

Score each remaining item by user impact, time saved, and system payoff:
- **💎 High**: Solves a recurring pain point, fixes a bug, unblocks a core workflow, or delivers high return for low effort.
- **💰 Medium**: Adds useful polish, speeds up a manual step, or delivers a solid feature with clear payoff.
- **🪙 Low**: Covers minor cleanup, cosmetic tweaks, or optional polish.

Group items by project and put the highest-value project first. Rank items within each project from `💎 High` down to `🪙 Low`, and link every item to its source session via `conversation://<id>`:

```markdown
## 📁 <Project / Workspace Name> (`<workspace_path>`)

### 1. [💎 High] <Short item title>
- **Source**: [<Conversation Title>](conversation://<conversation-id>) (`YYYY-MM-DD`, step `<N>`)
- **Description**: <1–2 sentences describing the feature or fix that was left behind.>
- **Why it exists**: <What problem, goal, or insight triggered the idea during the session.>
- **Last known status**: <Where the thread stopped and why the feature remained unbuilt.>
- **Expected benefit**: <Concrete user, product, or engineering payoff if built.>
```
