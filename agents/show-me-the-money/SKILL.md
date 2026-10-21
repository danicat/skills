---
name: show-me-the-money
description: >
  Mine project conversation history and git logs using a Map-Reduce workflow
  with parallel Flash/Flash-Lite agy CLI workers to recover unimplemented
  features. Scans all sessions in the current project by default, running one
  worker per session in the Map step and resolving the latest snapshot in the
  Reduce step. Activate when looking for forgotten features, mining past
  sessions for unfinished work, or asking "what did I forget to build?".
license: Apache-2.0
metadata:
  category: agents
  tags: "backlog, transcripts, map-reduce, productivity, discovery, prioritization"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Backlog finder

Find features from past sessions that never shipped, without burning frontier quota. Scan all sessions in the current project by default using a Map-Reduce flow:

1. **Map**: Run one fast `agy` Flash worker per session. Each worker lists every feature discussed as `IMPLEMENTED` or `NOT IMPLEMENTED`.
2. **Reduce**: Compare all worker reports by date against `git log` to find the latest snapshot of open work.

## 1. Select scope

Query `$HOME/.gemini/antigravity/conversation_summaries.db` with `sqlite3` to list root sessions where `parent_conversation_id = ''`. Always skip the active session.

- **Single-project sweep by default**: Scan all sessions for the current workspace across all time, ordered from oldest to newest.

```bash
WORKSPACE_PATH=$(pwd)
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
    AND workspace_uris LIKE '%file://${WORKSPACE_PATH}\"%'
  ORDER BY last_modified_time ASC;
"
```

- **Optional time sweep**: Wait for the user to ask for a time window across all projects. Then swap the `workspace_uris` filter for `AND last_modified_time >= datetime('now', '-N days')`.

## 2. Map: one `agy` Flash worker per session

Check your agent tier in the system prompt. When running on a frontier tier such as **Gemini 4 Argon** or **Pro**:

- **Never read raw `transcript.jsonl` files in the main session.**
- **Never call `invoke_subagent` for transcript mining.** Subagents inherit your frontier tier and burn high-cost quota.
- **Always spawn one headless `agy` CLI worker per session** pinned to a fast Flash tier such as `flash-lite` or `flash-low`.

Select the fastest Flash tier from `agy models`:

```bash
FLASH_MODEL=$(agy models | awk '/flash-lite|flash.*low/ {print $1; exit}')
```

Read only the chat turns and git commits. Skip tool logs, `ask_question` prompts, system notes, and scratch files.

For each session, extract the non-empty `USER_INPUT` and `PLANNER_RESPONSE` messages from `transcript.jsonl`, plus the last 100 commits from `git log` when the workspace uses git. Pass both inside `-p="..."` because `agy -p` ignores `stdin` in text mode:

```bash
FLOW=$(jq -r '
  select((.type == "USER_INPUT" or .type == "PLANNER_RESPONSE") and (.content | length > 0))
  | "[\(.step_index) \(.type)]: \(.content)"
' "$HOME/.gemini/antigravity/brain/${CONV_ID}/.system_generated/logs/transcript.jsonl")

GIT_LOG=$(git -C "$WORKSPACE_PATH" log --oneline -n 100 2>/dev/null)

agy --model "$FLASH_MODEL" --disable-slash-commands -p="Do not call any tools.
Read the conversation and git log below, and output a single message listing all features discussed with a binary status (IMPLEMENTED or NOT IMPLEMENTED).
For each feature, include:
- Status: IMPLEMENTED or NOT IMPLEMENTED
- Feature: short title and description
- Reasoning: why it was discussed
- Last known status: what happened to it in the conversation or git log
- Expected value: High, Medium, or Low (and why)

Session: ${TITLE} (${CONV_ID}) | Last active: ${LAST_ACTIVE}
Git log:
${GIT_LOG}

Conversation:
${FLOW}" > "/tmp/smtm-${CONV_ID}.md"
```

Run up to six `agy` workers in parallel background jobs using `&` and `wait`.

## 3. Reduce: compute the latest snapshot

After all Map workers finish, read `/tmp/smtm-*.md` by date and check `git log` to build the latest snapshot:

1. **Drop finished items**: If a later session or commit in `git log` shipped a feature from an older session, drop it.
2. **Drop rejected ideas**: If the user rejected an idea or replaced it with a newer design later, drop it.
3. **Merge repeated items**: Combine repeated mentions of the same open feature into one row linked to the latest session.

Score each remaining item by user impact, time saved, and system payoff:
- **High**: Solves a recurring pain point, fixes a bug, unblocks a core workflow, or delivers high return for low effort.
- **Medium**: Adds useful polish, speeds up a manual step, or delivers a solid feature with clear payoff.
- **Low**: Covers minor cleanup, cosmetic tweaks, or optional polish.

## 4. Render the backlog table

Output one compact Markdown table per project, sorted from `High` to `Low`. Keep each cell under 15 words in plain English—no commit hashes, step numbers, or file paths:

```markdown
## <Project Name>

| Value | Item | Why | Status | Benefit |
| :--- | :--- | :--- | :--- | :--- |
| **High** | **<Short title>** ([chat](conversation://<id>)) — <1-line summary> | <Why it came up> | <Where it stopped> | <Payoff if built> |
```
