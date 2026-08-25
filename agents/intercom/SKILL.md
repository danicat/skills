---
name: intercom
description: >
  Inter-session communication mesh connecting independent terminal sessions on
  the same host via Unix Domain Sockets and dedicated Comms Subagents. Features
  zero-config discovery, non-blocking duplex messaging, crash-resilient mailbox
  spooling, and automatic leader election via kernel advisory locks. Activate
  when coordinating multi-agent workflows across separate workspaces, delegating
  tasks between independent terminal sessions, relaying test failures or code
  diffs, or establishing a local agent mesh network.
license: Apache-2.0
metadata:
  category: agents
  tags: "ipc, mesh, multi-agent, subagents, sockets, comms"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Intercom: Inter-Session Multi-Agent Comms Mesh

`intercom` establishes zero-configuration, bidirectional inter-session communication between independent agent CLI sessions running on the same host using Unix Domain Sockets and dedicated Comms Subagents.

## Available scripts

- **`scripts/agy_ipc.py`** — Zero-dependency Unix Domain Socket transport, message router, and auto-elected hub daemon.
- **`scripts/namegen.py`** — Deterministic and random sci-fi communications officer identity generator.
- **`scripts/test_ipc.py`** — Unit and integration test suite validating socket transport, leader election, NDJSON message framing, and spooling.

---

## 1. Architecture & Mesh Topography

```
┌────────────────────────────────────┐          ┌────────────────────────────────────┐
│       SESSION ALPHA (Terminal 1)   │          │       SESSION BETA (Terminal 2)    │
│                                    │          │                                    │
│  ┌──────────────────────────────┐  │          │  ┌──────────────────────────────┐  │
│  │       Parent Agent A         │  │          │  │       Parent Agent B         │  │
│  └──────────────┬───────────────┘  │          │  └──────────────┬───────────────┘  │
│                 │ send_message     │          │                 │ send_message     │
│                 ▼                  │          │                 ▼                  │
│  ┌──────────────────────────────┐  │          │  ┌──────────────────────────────┐  │
│  │  Comms Officer (e.g. Uhura)  │  │          │  │  Comms Officer (e.g. Seven)  │  │
│  └──────────────┬───────────────┘  │          │  └──────────────┬───────────────┘  │
│                 │ agy_ipc.py       │          │                 │ agy_ipc.py       │
└─────────────────┼──────────────────┘          └─────────────────┼──────────────────┘
                  │                                               │
                  ▼                                               ▼
        ┌───────────────────────────────────────────────────────────────┐
        │             Intercom Unix Domain Socket Hub & Spool           │
        │              /tmp/agy-ipc/<channel_name>/hub.sock             │
        │      (Auto Leader-Election, NDJSON Framing, Zero-Config)      │
        └───────────────────────────────────────────────────────────────┘
```

---

## 2. Quickstart: Connecting Two Sessions

Follow this workflow to link two independent terminal sessions:

### Step 1: Agree on a Channel Name
Both sessions coordinate on a common channel name (e.g., `collab` or `mesh-1`).

### Step 2: Spawn the Comms Subagent in Both Sessions
Each session spawns its own dedicated `Comms Subagent` using `invoke_subagent`:

```python
# In Session A (e.g., role="Backend Lead"):
invoke_subagent(
    Subagents=[
        {
            "TypeName": "self",
            "Role": "Comms Officer Subagent",
            "Prompt": """You are the Comms Subagent for channel "collab".
Identity: Run `python3 scripts/namegen.py --id-only` or use your assigned role.

Operational Loop:
1. Announce presence:
   python3 scripts/agy_ipc.py send --channel collab --session <your_id> --to * --text "SESSION_JOINED"
2. Continuous Watcher:
   In a continuous loop, watch for incoming messages:
   python3 scripts/agy_ipc.py poll --channel collab --session <your_id> --wait 10
   When messages arrive from a remote peer, relay them immediately to your parent agent via send_message:
   send_message(Recipient="<parent_id>", Message="[IPC INCOMING from " + msg.from_session + "]: " + msg.payload.text)
3. Directives from Parent:
   When your parent sends you instructions via send_message:
   - "SEND(<target>): <text>" -> execute python3 scripts/agy_ipc.py send --channel collab --session <your_id> --to <target> --text "<text>", then resume watching.
   - "BROADCAST: <text>" -> execute python3 scripts/agy_ipc.py send --channel collab --session <your_id> --to * --text "<text>", then resume watching.
   - "STATUS" -> execute python3 scripts/agy_ipc.py peers --channel collab, report active peers to parent, then resume watching.
"""
        }
    ]
)
```

---

## 3. Communication Protocol

### Parent $\to$ Comms Subagent Directives
When the Parent Agent wants to interact with peer sessions, it sends instructions to its Comms Subagent using `send_message`:

| Directive | Description | Example |
| :--- | :--- | :--- |
| `SEND(<peer>): <text>` | Sends a direct message to a specific peer session | `SEND(seven-of-nine): Run unit tests on auth/jwt.go` |
| `BROADCAST: <text>` | Broadcasts message to all connected sessions | `BROADCAST: Schema migration 005 applied` |
| `STATUS` | Queries active peers connected to the channel | `STATUS` |

### Comms Subagent $\to$ Parent Notifications
When a message arrives from a remote peer, the Comms Subagent formats and delivers it directly to the Parent Agent:

```text
[IPC INCOMING from seven-of-nine]: Test suite passed (42 tests, 0 failures).
```

The Parent Agent receives this as a standard incoming message and reactively wakes up to continue its workflow without busy-wait polling.

---

## 4. Bundled Scripts & CLI Usage

All bundled scripts in `scripts/` require **zero external dependencies** and run on Python 3.10+ standard libraries (`asyncio`, `socket`, `fcntl`, `json`).

### `scripts/agy_ipc.py`
Zero-dependency Unix Domain Socket transport and auto-elected hub.

```bash
# Send a message (auto-spawns background hub daemon if not already active)
python3 scripts/agy_ipc.py send --channel collab --session nyota-uhura --to seven-of-nine --text "Telemetry received"

# Poll inbox for unread messages (long-poll with timeout in seconds)
python3 scripts/agy_ipc.py poll --channel collab --session nyota-uhura --wait 10

# Stream incoming messages in real time to stdout
python3 scripts/agy_ipc.py listen --channel collab --session nyota-uhura

# Query active peers on channel
python3 scripts/agy_ipc.py peers --channel collab

# Clean up socket and mailbox spool files
python3 scripts/agy_ipc.py cleanup --channel collab
```

### `scripts/namegen.py`
Deterministic and random sci-fi communications officer identity generator.

```bash
# Generate a single random officer codename
python3 scripts/namegen.py

# Generate only the sanitized identifier (e.g., "nyota-uhura")
python3 scripts/namegen.py --id-only

# List full officer roster
python3 scripts/namegen.py --all
```

### `scripts/test_ipc.py`
Automated test suite verifying socket transport, leader election, NDJSON framing, and mailbox persistence.

```bash
python3 scripts/test_ipc.py
```

---

## 5. Operational Safeguards & Troubleshooting

| Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **Both sessions try to start Hub** | Simultaneous initialization | Kernel advisory lock (`fcntl.flock`) automatically elects the first session as Hub leader; second session falls back to client mode. |
| **Session offline during long build** | Subagent busy with tool calls | Messages are spooled in `/tmp/agy-ipc/<channel>/inbox_<session>.ndjson`. All unread messages are delivered on next poll. |
| **Stale socket after unexpected crash** | Socket file remains on disk | `ensure_daemon_running()` automatically probes the socket with a test connection, unlinks stale sockets, and spawns a fresh Hub. |
| **Clean slate reset** | Need to purge old channel state | Run `python3 scripts/agy_ipc.py cleanup --channel <chan>`. |

---

## 6. Progressive Disclosure & References

- **[Protocol & Framing Specification](references/protocol.md)**: Deep wire protocol, message envelope specification, socket framing, and persistence architecture.
