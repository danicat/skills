---
name: intercom
description: >
  Cross-project and cross-session collaboration between Antigravity agents using
  scripts/session.py. Messages active peer sessions or starts new sessions in
  another project with automatic return-address headers. Activate when
  collaborating between agents in different projects, handing off tasks across
  workspaces, or messaging another session.
license: Apache-2.0
metadata:
  category: workflows
  tags: "cross-project, multi-agent, sessions, coordination, handoff"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.5.0"
  catalog: https://skills.danicat.dev
---

# Intercom: cross-project agent collaboration

`intercom` lets Antigravity agents in separate workspaces exchange messages or start new sessions in another project via `scripts/session.py`.

---

## 1. Message an existing session (`send`)

Read the target session ID from the user's prompt or an incoming `[Intercom From: ...]` message header. If no target session ID was provided, ask the user for it before running the command.

```bash
kungfu run intercom session.py send --id <session-id> --message "<message>"
```

---

## 2. Start a new session in another project (`new`)

Only use `new` when the user explicitly asks to start a new conversation in another project. If no target project ID was provided, ask the user for it before running the command.

```bash
kungfu run intercom session.py new --project <project-id> --message "<message>"
```

---

## 3. Operational rules

1. **Ask for missing IDs**: Never guess a session ID or project ID. Ask the user if either ID is missing from the prompt.
2. **No unsolicited conversations**: Never run `new` unless the user explicitly asks to start a new session.
3. **No polling or listener subagents**: `send` wakes the target session directly. Never run polling loops, `sleep` timers, or listener subagents; stop calling tools after sending when waiting for a reply.
4. **Fail fast on errors**: If `session.py` exits non-zero, stop and report the error immediately.
