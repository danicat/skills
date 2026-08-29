---
name: intercom
description: >
  Inter-session communication mesh connecting independent terminal sessions on
  the same host via Unix Domain Sockets and dedicated Comms Subagents. Features
  sticky project identities, zero impersonation, non-blocking duplex messaging,
  crash-resilient mailbox spooling, and automatic clean restart lifecycles.
  Activate when coordinating multi-agent workflows across separate workspaces,
  delegating tasks between independent terminal sessions, relaying test failures
  or code diffs, or establishing a local agent mesh network.
license: Apache-2.0
metadata:
  category: agents
  tags: "ipc, mesh, multi-agent, subagents, sockets, comms"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  catalog: https://skills.danicat.dev
---

# Intercom: Inter-Session Multi-Agent Comms Mesh

`intercom` establishes zero-configuration, bidirectional inter-session communication between independent agent CLI sessions running on the same host using Unix Domain Sockets and dedicated Comms Subagents.

## Available scripts & assets

- **`scripts/agy_ipc.py`** — Zero-dependency Unix Domain Socket transport, message router, auto-elected hub daemon, and sticky identity manager.
- **`scripts/namegen.py`** — Sci-fi communications officer identity generator with sticky project persistence and channel collision protection.
- **`scripts/test_ipc.py`** — Unit and integration test suite validating socket transport, leader election, NDJSON message framing, sticky identities, and clean restart lifecycles.
- **`assets/agents/comms-officer.md`** — Dedicated subagent template for the Communications Officer.
- **`references/comms-officer.md`** — Comprehensive guide to the Comms Officer subagent pattern and unblocked execution.
- **`references/protocol.md`** — Low-level wire protocol, message envelope specification, socket framing, and persistence architecture.

---

## ⚡ Core Operational Mandates

To ensure maximum responsiveness, zero user friction, and context hygiene, all Intercom mesh operations MUST adhere to these five core rules:

1. **One Sticky Comms Agent per Project Workspace:**
   - Every project directory maintains **one and only one sticky Communications Officer identity** (persisted in `.intercom/session.json`).
   - The identity is automatically resolved and bound when initializing comms. Across restarts and tool runs, the project always speaks under its established officer codename (e.g., `nyota-uhura`).
2. **Zero Impersonation & Collision Prevention:**
   - When claiming or validating an identity, the runtime checks active channel peers (`peers.json` and active socket connections).
   - If another running project is already actively connected under that officer name, the system automatically assigns the next available officer from the roster, preventing name collisions and impersonation.
3. **Mandatory Comms Officer Subagent (Unblocked Main Session):**
   - The Main Agent Session (ROOT) is the pair-programming interface to the user and **MUST NEVER** block itself running background listener scripts or managing raw socket streams.
   - The Main Agent **ALWAYS spawns a dedicated `comms-officer` subagent** via `invoke_subagent`.
   - The Comms Officer manages the background bridge, receives incoming socket events, and relays high-signal updates to the Main Agent via `send_message`.
4. **Smart Script Usage (Zero User Confirmation Spam):**
   - **NEVER** run `agy_ipc.py poll` in a tight loop or scheduled cron job. Polling loops repeatedly prompt the user for script authorization.
   - The Comms Officer subagent starts the background listener **ONCE** upon activation:
     ```bash
     python3 scripts/agy_ipc.py listen --channel <chan> --session <id> --fresh
     ```
   - Running as a single background task authorized once, it streams incoming messages and reactively awakens the subagent without polling overhead.
5. **Clean Restarts & Dead Comms Cleanup (Zero Context Contamination):**
   - When restarting or initializing a session (`agy_ipc.py init` or `agy_ipc.py listen --fresh`), the session mailbox is automatically reset to the current stream head.
   - Stale historical messages from dead sessions or yesterday's runs are never replayed into the LLM context.
   - Channel broadcasts route exclusively to **currently active connected peers**, preventing message buildup in orphaned zombie mailboxes.

---

## 1. Mesh Topology & Architecture

```
┌────────────────────────────────────────────────────────┐          ┌────────────────────────────────────────────────────────┐
│               PROJECT A (Terminal 1)                   │          │               PROJECT B (Terminal 2)                   │
│                                                        │          │                                                        │
│  ┌──────────────────────────────────────────────────┐  │          │  ┌──────────────────────────────────────────────────┐  │
│  │           Main Agent Session (ROOT)              │  │          │  │           Main Agent Session (ROOT)              │  │
│  │       (Unblocked, pairing with the user)         │  │          │  │       (Unblocked, pairing with the user)         │  │
│  └────────────────────────▲─────────────────────────┘  │          │  └────────────────────────▲─────────────────────────┘  │
│                           │ send_message (Relay)       │          │                           │ send_message (Relay)       │
│                           ▼                            │          │                           ▼                            │
│  ┌──────────────────────────────────────────────────┐  │          │  ┌──────────────────────────────────────────────────┐  │
│  │        Comms Officer Subagent (nyota-uhura)      │  │          │  │       Comms Officer Subagent (seven-of-nine)     │  │
│  │   (Runs background listener, isolates network)   │  │          │  │   (Runs background listener, isolates network)   │  │
│  └────────────────────────┬─────────────────────────┘  │          │  └────────────────────────┬─────────────────────────┘  │
│                           │ agy_ipc.py send / listen   │          │                           │ agy_ipc.py send / listen   │
└───────────────────────────┼────────────────────────────┘          └───────────────────────────┼────────────────────────────┘
                            │                                                                   │
                            ▼                                                                   ▼
                  ┌───────────────────────────────────────────────────────────────────────────────────┐
                  │                        Intercom Unix Domain Socket Hub & Spool                    │
                  │                         /tmp/agy-ipc/<channel_name>/hub.sock                      │
                  │                 (Auto Leader-Election, Live Peer Routing, Zero-Config)            │
                  └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Quickstart: Connecting Two Sessions

Follow this streamlined 3-step workflow to connect independent agent sessions:

### Step 1: Initialize Project Comms & Claim Sticky Identity
Run `init` to establish the project's sticky identity, start the hub daemon, and reset mailbox state:

```bash
python3 scripts/agy_ipc.py init --channel collab
```

*Output:*
```json
{
  "status": "ready",
  "channel": "collab",
  "session_id": "nyota-uhura",
  "name": "Nyota Uhura",
  "title": "Chief Communications Officer",
  "is_sticky": true,
  "inbox_reset": true
}
```

### Step 2: Spawn the Dedicated Comms Officer Subagent
The Main Agent uses `invoke_subagent` to launch the Comms Officer in the background:

```python
invoke_subagent(
    Subagents=[{
        "TypeName": "comms-officer",
        "Role": "Communications Officer",
        "Prompt": "You are our dedicated Comms Officer (nyota-uhura) for channel 'collab'. Run the background listener with 'python3 scripts/agy_ipc.py listen --channel collab --session nyota-uhura --fresh' and relay any incoming messages to this main session."
    }]
)
```

### Step 3: Communicate Asynchronously
- **Sending Outgoing Messages:** The Main Agent sends a directive to the Comms Officer via `send_message`:
  ```python
  send_message(
      Recipient="<comms_subagent_conv_id>",
      Message="SEND TO seven-of-nine: Please review the newly generated auth schema."
  )
  ```
  The Comms Officer executes `python3 scripts/agy_ipc.py send --channel collab --session nyota-uhura --to seven-of-nine --text "Please review the newly generated auth schema."` and acknowledges.

- **Receiving Incoming Messages:** When the remote peer responds, the background listener outputs the event, and the Comms Officer immediately notifies the Main Agent:
  ```python
  send_message(
      Recipient="<main_agent_conv_id>",
      Message="[INTERCOM INCOMING from seven-of-nine]: Schema review passed with 0 warnings. Ready to merge."
  )
  ```

---

## 3. Communication Commands Matrix

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Initialize Comms** | `python3 scripts/agy_ipc.py init --channel <chan>` | Resolves sticky project identity, auto-spawns hub, resets inbox |
| **Start Listener** | `python3 scripts/agy_ipc.py listen --channel <chan> --session <id> --fresh` | Persistent stream listener running in Comms Officer background |
| **Direct Message** | `python3 scripts/agy_ipc.py send --channel <chan> --session <id> --to <peer> --text "<msg>"` | Direct point-to-point transmission to a specific officer |
| **Broadcast** | `python3 scripts/agy_ipc.py send --channel <chan> --session <id> --to "*" --text "<msg>"` | Channel-wide announcement delivered only to live connected peers |
| **Query Peers** | `python3 scripts/agy_ipc.py peers --channel <chan>` | Enumerates currently connected active sessions |
| **Clean Stale State** | `python3 scripts/agy_ipc.py cleanup --channel <chan> --stale` | Prunes dead sockets and locks without interrupting active channel |
| **Full Reset** | `python3 scripts/agy_ipc.py cleanup --channel <chan>` | Completely purges channel socket, locks, and spool directory |

---

## 4. Script Reference & CLI Options

All scripts require **zero external dependencies** and execute on Python 3.10+ standard libraries (`asyncio`, `socket`, `fcntl`, `json`).

### `scripts/agy_ipc.py`
```bash
# Initialize project comms (idempotent, sticky, zero-collision)
python3 scripts/agy_ipc.py init --channel main

# Send direct message with structured JSON payload
python3 scripts/agy_ipc.py send --channel main --session nyota-uhura --to seven-of-nine --text "Diff ready" --json-payload '{"files": ["auth.go"]}'

# Stream incoming messages (runs continuously in background subagent)
python3 scripts/agy_ipc.py listen --channel main --session nyota-uhura --fresh

# List live peers
python3 scripts/agy_ipc.py peers --channel main

# Purge stale dead artifacts
python3 scripts/agy_ipc.py cleanup --channel main --stale
```

### `scripts/namegen.py`
```bash
# Claim or retrieve sticky identity for current project without collisions
python3 scripts/namegen.py --claim --channel main --json

# Generate raw single officer ID
python3 scripts/namegen.py --id-only

# Display full roster
python3 scripts/namegen.py --all
```

---

## 5. Antipatterns & Operational Gotchas

1. **The Polling Loop Trap:** Running `agy_ipc.py poll` inside a `while` loop or scheduled timer. This spams the user with approval prompts. **Solution:** Launch `listen` once as a persistent background task.
2. **The Main Session Blocking Trap:** Running `listen` directly inside the Main Session. This blocks the main chat and prevents the user from pairing with the assistant. **Solution:** Always delegate comms to a dedicated `comms-officer` subagent.
3. **The Identity Clash Trap:** Hardcoding session names (e.g. `session="agent1"`) instead of using `init` / `namegen.py --claim`. **Solution:** Always let `init` resolve the sticky, collision-free identity.
4. **The Stale History Contamination Trap:** Restarting an agent and reading old inbox backlogs without `--fresh`. **Solution:** Always pass `--fresh` on restart so the agent only reads new messages from the current conversation.

---

## 6. Progressive Disclosure & References

- **[Comms Officer Subagent Guide](references/comms-officer.md)**: Deep dive into the Comms Officer subagent pattern, lifecycle management, and message relaying.
- **[Comms Officer Subagent Template](assets/agents/comms-officer.md)**: Ready-to-use subagent prompt definition.
- **[Protocol & Framing Specification](references/protocol.md)**: Wire protocol, message envelope schema, socket framing, and persistence architecture.
