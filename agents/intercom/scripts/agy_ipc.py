#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
agy_ipc.py: Inter-Session Multi-Agent IPC Transport Bridge
Provides Unix Domain Socket routing, NDJSON framing, sticky project identities,
zero-impersonation allocation, and clean restart lifecycles.

Zero external dependencies. Works out-of-the-box on macOS and Linux.
"""

import argparse
import asyncio
import datetime
import fcntl
import json
import os
import pathlib
import signal
import socket
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Set

DEFAULT_BASE_DIR = pathlib.Path(os.environ.get("AGY_IPC_DIR", "/tmp/agy-ipc"))
BUFFER_SIZE = 65536


def get_channel_dir(channel: str, base_dir: pathlib.Path = DEFAULT_BASE_DIR) -> pathlib.Path:
    """Resolve and securely initialize the filesystem path for a specific mesh channel."""
    clean_channel = "".join(c for c in channel if c.isalnum() or c in ("-", "_")).lower()
    if not clean_channel:
        clean_channel = "default"
    chan_dir = base_dir / clean_channel
    chan_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    return chan_dir


def make_envelope(
    msg_type: str,
    from_session: str,
    to_session: str,
    channel: str,
    payload: Dict[str, Any],
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct a standardized NDJSON message envelope with unique ID and timestamp."""
    return {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "type": msg_type,
        "from_session": from_session,
        "to_session": to_session,
        "channel": channel,
        "reply_to": reply_to,
        "payload": payload,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


class IPCSpool:
    """Manages append-only NDJSON inbox spools with kernel advisory file locks."""

    def __init__(self, channel_dir: pathlib.Path, session_id: str) -> None:
        self.channel_dir = channel_dir
        self.session_id = session_id
        self.inbox_path = channel_dir / f"inbox_{session_id}.ndjson"
        self.offset_path = channel_dir / f"offset_{session_id}.json"

    def ensure_inbox_exists(self) -> None:
        """Create inbox file if it does not already exist."""
        if not self.inbox_path.exists():
            with open(self.inbox_path, "a", encoding="utf-8"):
                pass

    def reset_inbox(self) -> None:
        """Purge all prior messages from inbox and reset read offset to prevent stale context contamination."""
        with open(self.inbox_path, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.truncate(0)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        with open(self.offset_path, "w", encoding="utf-8") as f:
            json.dump({"offset": 0, "updated_at": time.time(), "reset_at": time.time()}, f)

    def seek_to_end(self) -> None:
        """Advance offset to current file size so only future incoming messages are delivered."""
        self.ensure_inbox_exists()
        size = self.inbox_path.stat().st_size
        with open(self.offset_path, "w", encoding="utf-8") as f:
            json.dump({"offset": size, "updated_at": time.time()}, f)

    def append_inbox(self, envelope: Dict[str, Any]) -> None:
        """Atomically append a message envelope to the session inbox file."""
        line = json.dumps(envelope, separators=(",", ":")) + "\n"
        with open(self.inbox_path, "a", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(line)
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def read_unread(self, mark_read: bool = True) -> List[Dict[str, Any]]:
        """Read unread messages from inbox file based on persistent byte offset."""
        if not self.inbox_path.exists():
            return []

        offset = 0
        if self.offset_path.exists():
            try:
                with open(self.offset_path, "r", encoding="utf-8") as f:
                    offset = json.load(f).get("offset", 0)
            except Exception:
                offset = 0

        messages: List[Dict[str, Any]] = []
        new_offset = offset

        with open(self.inbox_path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                f.seek(offset)
                while True:
                    line = f.readline()
                    if not line:
                        break
                    line_str = line.strip()
                    if line_str:
                        try:
                            messages.append(json.loads(line_str))
                        except json.JSONDecodeError:
                            pass
                new_offset = f.tell()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        if mark_read and new_offset != offset:
            with open(self.offset_path, "w", encoding="utf-8") as f:
                json.dump({"offset": new_offset, "updated_at": time.time()}, f)

        return messages


class IPCHubServer:
    """Unix Domain Socket Hub Server for multi-session routing and leader election."""

    def __init__(self, channel_dir: pathlib.Path, channel_name: str) -> None:
        self.channel_dir = channel_dir
        self.channel_name = channel_name
        self.sock_path = channel_dir / "hub.sock"
        self.lock_path = channel_dir / "hub.lock"
        self.peers_path = channel_dir / "peers.json"
        self.clients: Dict[str, asyncio.StreamWriter] = {}
        self.lock_fd: Optional[int] = None
        self.server: Optional[asyncio.AbstractServer] = None
        self._running = True

    def acquire_hub_lock(self) -> bool:
        """Attempt non-blocking advisory file lock for automatic leader election."""
        try:
            self.lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (BlockingIOError, OSError):
            if self.lock_fd is not None:
                try:
                    os.close(self.lock_fd)
                except OSError:
                    pass
                self.lock_fd = None
            return False

    def update_peers_file(self) -> None:
        """Persist current active channel sessions to peers.json atomically."""
        data = {
            "channel": self.channel_name,
            "hub_pid": os.getpid(),
            "active_sessions": list(self.clients.keys()),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        temp_path = self.peers_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, self.peers_path)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming connection from an agent session over Unix Domain Socket."""
        client_session: Optional[str] = None
        buffer = ""

        try:
            while self._running:
                data = await reader.read(BUFFER_SIZE)
                if not data:
                    break

                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        envelope = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg_type = envelope.get("type")
                    from_sess = envelope.get("from_session", "unknown")
                    to_sess = envelope.get("to_session", "*")

                    if msg_type in ("announce", "register") or client_session is None:
                        client_session = from_sess
                        # Check for collision with an existing active connection
                        if client_session in self.clients and self.clients[client_session] is not writer:
                            old_writer = self.clients[client_session]
                            if not old_writer.is_closing():
                                # Collision detected: Session ID is already actively in use
                                collision_env = make_envelope(
                                    "error",
                                    "hub",
                                    client_session,
                                    self.channel_name,
                                    {
                                        "code": "SESSION_COLLISION",
                                        "message": f"Session ID '{client_session}' is already actively connected on this channel.",
                                    },
                                )
                                writer.write((json.dumps(collision_env) + "\n").encode("utf-8"))
                                await writer.drain()
                                writer.close()
                                await writer.wait_closed()
                                return

                        self.clients[client_session] = writer
                        IPCSpool(self.channel_dir, client_session).ensure_inbox_exists()
                        self.update_peers_file()
                        welcome = make_envelope(
                            "welcome",
                            "hub",
                            client_session,
                            self.channel_name,
                            {"peers": list(self.clients.keys()), "status": "connected"},
                        )
                        raw = (json.dumps(welcome) + "\n").encode("utf-8")
                        writer.write(raw)
                        await writer.drain()

                    # Route and spool message
                    if msg_type == "chat":
                        if to_sess in ("*", "all"):
                            # Broadcast ONLY to currently active connected sessions to prevent zombie contamination
                            target_sessions: Set[str] = set(self.clients.keys()) - {from_sess}
                            for target_sess in target_sessions:
                                spool = IPCSpool(self.channel_dir, target_sess)
                                spool.append_inbox(envelope)
                                if target_sess in self.clients:
                                    try:
                                        raw = (json.dumps(envelope) + "\n").encode("utf-8")
                                        self.clients[target_sess].write(raw)
                                        await self.clients[target_sess].drain()
                                    except Exception:
                                        pass
                        else:
                            # Direct Message
                            spool = IPCSpool(self.channel_dir, to_sess)
                            spool.append_inbox(envelope)
                            if to_sess in self.clients:
                                target_writer = self.clients[to_sess]
                                try:
                                    raw = (json.dumps(envelope) + "\n").encode("utf-8")
                                    target_writer.write(raw)
                                    await target_writer.drain()
                                except Exception:
                                    pass

        except (asyncio.CancelledError, ConnectionResetError):
            pass
        finally:
            if client_session and client_session in self.clients:
                if self.clients[client_session] is writer:
                    del self.clients[client_session]
                    self.update_peers_file()
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def start(self) -> None:
        """Start the IPC Hub server listening on the channel Unix Domain Socket."""
        if not self.acquire_hub_lock():
            raise RuntimeError(f"Another Hub is already running for channel: {self.channel_name}")

        if self.sock_path.exists():
            try:
                probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                probe.connect(str(self.sock_path))
                probe.close()
                raise RuntimeError(f"Socket {self.sock_path} is active by another process.")
            except (ConnectionRefusedError, FileNotFoundError):
                self.sock_path.unlink(missing_ok=True)

        self.server = await asyncio.start_unix_server(self.handle_client, path=str(self.sock_path))
        self.update_peers_file()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
            except NotImplementedError:
                pass

        async with self.server:
            await self.server.serve_forever()

    async def shutdown(self) -> None:
        """Gracefully terminate Hub server and clean up socket/lock files."""
        self._running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.sock_path.unlink(missing_ok=True)
        self.peers_path.unlink(missing_ok=True)
        if self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
            except OSError:
                pass
            self.lock_path.unlink(missing_ok=True)


def ensure_daemon_running(channel_dir: pathlib.Path, channel_name: str) -> None:
    """Verify hub daemon is active; auto-spawn background daemon process if needed."""
    sock_path = channel_dir / "hub.sock"
    if sock_path.exists():
        try:
            probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            probe.connect(str(sock_path))
            probe.close()
            return
        except (ConnectionRefusedError, FileNotFoundError):
            sock_path.unlink(missing_ok=True)

    import subprocess

    script_path = pathlib.Path(__file__).resolve()
    try:
        subprocess.Popen(
            [sys.executable, str(script_path), "--dir", str(channel_dir.parent), "--channel", channel_name, "daemon"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        deadline = time.time() + 1.5
        while time.time() < deadline:
            if sock_path.exists():
                break
            time.sleep(0.05)
    except Exception:
        pass


async def send_message_uds(
    channel_dir: pathlib.Path,
    channel_name: str,
    from_session: str,
    to_session: str,
    text: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send an NDJSON message envelope over Unix Domain Socket or direct spool fallback."""
    ensure_daemon_running(channel_dir, channel_name)
    envelope_payload = payload.copy() if payload else {}
    envelope_payload["text"] = text
    envelope = make_envelope("chat", from_session, to_session, channel_name, envelope_payload)

    # Ensure sender's inbox is ready
    IPCSpool(channel_dir, from_session).ensure_inbox_exists()

    sock_path = channel_dir / "hub.sock"
    if not sock_path.exists():
        # Fallback to direct spooling if hub is temporarily down
        spool = IPCSpool(channel_dir, to_session)
        spool.append_inbox(envelope)
        return {"status": "spooled_offline", "envelope": envelope}

    try:
        reader, writer = await asyncio.open_unix_connection(str(sock_path))
        reg_env = make_envelope("register", from_session, "hub", channel_name, {})
        writer.write((json.dumps(reg_env) + "\n").encode("utf-8"))
        await writer.drain()

        # Read welcome or collision
        welcome_raw = await asyncio.wait_for(reader.readline(), timeout=2.0)
        if welcome_raw:
            try:
                resp = json.loads(welcome_raw.decode("utf-8").strip())
                if resp.get("type") == "error" and resp.get("payload", {}).get("code") == "SESSION_COLLISION":
                    writer.close()
                    await writer.wait_closed()
                    return {"status": "error", "error": "SESSION_COLLISION", "message": resp["payload"].get("message")}
            except Exception:
                pass

        # Write actual message
        writer.write((json.dumps(envelope) + "\n").encode("utf-8"))
        await writer.drain()

        writer.close()
        await writer.wait_closed()
        return {"status": "sent", "envelope": envelope}
    except Exception as err:
        # Fallback to direct spooling
        spool = IPCSpool(channel_dir, to_session)
        spool.append_inbox(envelope)
        return {"status": "fallback_spooled", "error": str(err), "envelope": envelope}


async def stream_listener(
    channel_dir: pathlib.Path,
    channel_name: str,
    session_id: str,
    fresh: bool = True,
) -> None:
    """
    Continuously stream incoming messages for session_id in real time to stdout.
    Also listens on stdin to enable bidirectional background bridging without spawning separate shell processes.
    """
    ensure_daemon_running(channel_dir, channel_name)
    sock_path = channel_dir / "hub.sock"
    spool = IPCSpool(channel_dir, session_id)
    spool.ensure_inbox_exists()

    if fresh:
        # Avoid reading stale context from previous runs
        spool.seek_to_end()

    # Drain any unread spool arriving during initialization
    unread = spool.read_unread(mark_read=True)
    for msg in unread:
        print(json.dumps(msg), flush=True)

    async def handle_stdin(writer_ref: List[Optional[asyncio.StreamWriter]]) -> None:
        """Read NDJSON commands from stdin to allow sending messages via running listener."""
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        try:
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        except Exception:
            return

        while True:
            line_bytes = await reader.readline()
            if not line_bytes:
                break
            line_str = line_bytes.decode("utf-8").strip()
            if not line_str:
                continue
            try:
                cmd_obj = json.loads(line_str)
                action = cmd_obj.get("action")
                if action == "send":
                    to_target = cmd_obj.get("to", "*")
                    text_val = cmd_obj.get("text", "")
                    payload_val = cmd_obj.get("payload", {})
                    await send_message_uds(
                        channel_dir=channel_dir,
                        channel_name=channel_name,
                        from_session=session_id,
                        to_session=to_target,
                        text=text_val,
                        payload=payload_val,
                    )
            except Exception as stdin_err:
                print(json.dumps({"type": "stdin_error", "error": str(stdin_err)}), file=sys.stderr, flush=True)

    stdin_task: Optional[asyncio.Task] = None
    try:
        stdin_task = asyncio.create_task(handle_stdin([None]))
    except Exception:
        pass

    while True:
        try:
            if not sock_path.exists():
                await asyncio.sleep(0.5)
                unread = spool.read_unread(mark_read=True)
                for msg in unread:
                    print(json.dumps(msg), flush=True)
                continue

            reader, writer = await asyncio.open_unix_connection(str(sock_path))
            announce = make_envelope("announce", session_id, "hub", channel_name, {})
            writer.write((json.dumps(announce) + "\n").encode("utf-8"))
            await writer.drain()

            buffer = ""
            while True:
                data = await reader.read(BUFFER_SIZE)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        env = json.loads(line)
                        if env.get("type") not in ("welcome", "heartbeat"):
                            print(json.dumps(env), flush=True)
                    except json.JSONDecodeError:
                        pass
        except (ConnectionRefusedError, FileNotFoundError, ConnectionResetError):
            await asyncio.sleep(1.0)
        except Exception as e:
            print(json.dumps({"type": "error", "message": str(e)}), file=sys.stderr, flush=True)
            await asyncio.sleep(1.0)


def cmd_daemon(args: argparse.Namespace) -> None:
    """Execute daemon server process for channel."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    hub = IPCHubServer(chan_dir, args.channel)
    try:
        asyncio.run(hub.start())
    except RuntimeError as e:
        print(f"[DAEMON INFO] {e}", file=sys.stderr)
        sys.exit(0)


def cmd_init(args: argparse.Namespace) -> None:
    """
    Initialize sticky project comms identity, prune stale channel state,
    and guarantee clean context on startup.
    """
    project_dir = pathlib.Path(args.project_dir) if args.project_dir else pathlib.Path.cwd()
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))

    # Resolve sticky identity
    script_dir = pathlib.Path(__file__).parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    from namegen import resolve_sticky_identity

    identity = resolve_sticky_identity(
        project_dir=project_dir,
        channel=args.channel,
        base_dir=pathlib.Path(args.dir),
        force_new=args.force_new,
    )
    session_id = identity["id"]

    # Ensure daemon is running
    ensure_daemon_running(chan_dir, args.channel)

    # Reset inbox spool if fresh requested
    if args.fresh:
        spool = IPCSpool(chan_dir, session_id)
        spool.reset_inbox()

    output = {
        "status": "ready",
        "channel": args.channel,
        "session_id": session_id,
        "name": identity.get("name"),
        "title": identity.get("title"),
        "ship": identity.get("ship"),
        "quote": identity.get("quote"),
        "is_sticky": identity.get("is_sticky", True),
        "project_dir": str(project_dir.resolve()),
        "inbox_reset": args.fresh,
    }
    print(json.dumps(output, indent=2))


def cmd_send(args: argparse.Namespace) -> None:
    """Send an NDJSON message envelope to a peer or channel broadcast."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    payload: Dict[str, Any] = {}
    if args.json_payload:
        try:
            payload = json.loads(args.json_payload)
        except json.JSONDecodeError as err:
            print(f"Error parsing --json-payload: {err}", file=sys.stderr)
            sys.exit(1)

    result = asyncio.run(
        send_message_uds(
            channel_dir=chan_dir,
            channel_name=args.channel,
            from_session=args.session,
            to_session=args.to,
            text=args.text or "",
            payload=payload,
        )
    )
    print(json.dumps(result, indent=2))


def cmd_poll(args: argparse.Namespace) -> None:
    """Poll unread messages from session inbox with timeout."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    ensure_daemon_running(chan_dir, args.channel)
    spool = IPCSpool(chan_dir, args.session)
    spool.ensure_inbox_exists()
    deadline = time.time() + args.wait

    while True:
        messages = spool.read_unread(mark_read=not args.peek)
        if messages or time.time() >= deadline:
            print(json.dumps({"count": len(messages), "messages": messages}, indent=2))
            return
        time.sleep(0.2)


def cmd_listen(args: argparse.Namespace) -> None:
    """Stream incoming NDJSON messages in real time."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    try:
        asyncio.run(stream_listener(chan_dir, args.channel, args.session, fresh=args.fresh))
    except KeyboardInterrupt:
        pass


def cmd_peers(args: argparse.Namespace) -> None:
    """List active sessions connected to channel."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    ensure_daemon_running(chan_dir, args.channel)
    peers_path = chan_dir / "peers.json"
    if peers_path.exists():
        with open(peers_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(json.dumps({"channel": args.channel, "active_sessions": []}))


def cmd_cleanup(args: argparse.Namespace) -> None:
    """Purge channel directory, sockets, or stale artifacts."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    if args.stale:
        # Clean only dead sockets, dead locks, and inactive inboxes
        sock_path = chan_dir / "hub.sock"
        if sock_path.exists():
            try:
                probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                probe.connect(str(sock_path))
                probe.close()
            except (ConnectionRefusedError, FileNotFoundError):
                sock_path.unlink(missing_ok=True)

        lock_path = chan_dir / "hub.lock"
        if lock_path.exists():
            try:
                fd = os.open(lock_path, os.O_RDWR)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    # If we acquired lock, no daemon is running; remove it
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    lock_path.unlink(missing_ok=True)
                except (BlockingIOError, OSError):
                    os.close(fd)
            except Exception:
                pass
        print(json.dumps({"status": "stale_cleaned", "channel": args.channel}))
        return

    for f in chan_dir.glob("*"):
        try:
            f.unlink()
        except OSError:
            pass
    print(json.dumps({"status": "cleaned", "channel": args.channel}))


def resolve_session_id(
    session_arg: Optional[str],
    project_dir: Optional[pathlib.Path] = None,
    channel: str = "default",
    base_dir: pathlib.Path = DEFAULT_BASE_DIR,
) -> str:
    """Resolve sticky session identifier or generate a non-colliding identity."""
    if session_arg and session_arg not in ("auto", ""):
        return session_arg
    try:
        script_dir = pathlib.Path(__file__).parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        from namegen import resolve_sticky_identity

        identity = resolve_sticky_identity(project_dir=project_dir, channel=channel, base_dir=base_dir)
        return identity["id"]
    except Exception:
        pass
    return f"officer-{uuid.uuid4().hex[:6]}"


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default=argparse.SUPPRESS, help="Base IPC root directory")
    common.add_argument("--channel", default=argparse.SUPPRESS, help="Channel name")
    common.add_argument("--project-dir", default=argparse.SUPPRESS, help="Project directory root")

    parser = argparse.ArgumentParser(description="Multi-Agent Inter-Session IPC Bridge", parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("daemon", help="Run background IPC hub daemon", parents=[common])

    # init command
    i_parser = sub.add_parser("init", help="Initialize sticky project comms identity and mesh hub", parents=[common])
    i_parser.add_argument("--fresh", action="store_true", default=True, help="Reset session mailbox to prevent stale context contamination")
    i_parser.add_argument("--no-fresh", dest="fresh", action="store_false", help="Preserve unread messages in mailbox")
    i_parser.add_argument("--force-new", action="store_true", help="Force new identity allocation")

    # send command
    s_parser = sub.add_parser("send", help="Send a message to a session or channel", parents=[common])
    s_parser.add_argument("--session", default=None, help="Sender session ID (defaults to sticky project Comms Officer)")
    s_parser.add_argument("--to", default="*", help="Target session ID or '*' for broadcast")
    s_parser.add_argument("--text", default="", help="Message text content")
    s_parser.add_argument("--json-payload", help="Optional extra JSON dictionary string")

    # poll command
    p_parser = sub.add_parser("poll", help="Poll unread messages from session inbox", parents=[common])
    p_parser.add_argument("--session", default=None, help="Current session ID")
    p_parser.add_argument("--wait", type=float, default=0.0, help="Seconds to wait for new messages")
    p_parser.add_argument("--peek", action="store_true", help="Do not advance unread offset")

    # listen command
    l_parser = sub.add_parser("listen", help="Stream incoming NDJSON messages to stdout", parents=[common])
    l_parser.add_argument("--session", default=None, help="Current session ID")
    l_parser.add_argument("--fresh", action="store_true", default=True, help="Do not replay old unread messages from prior runs")
    l_parser.add_argument("--no-fresh", dest="fresh", action="store_false", help="Replay unread messages from inbox backlog")

    # peers command
    sub.add_parser("peers", help="List active sessions on channel", parents=[common])

    # cleanup command
    c_parser = sub.add_parser("cleanup", help="Remove channel socket, lock artifacts, or stale state", parents=[common])
    c_parser.add_argument("--stale", action="store_true", help="Clean only dead sockets and locks without purging live channel")

    args = parser.parse_args()

    # Resolve default values if not explicitly provided
    args.dir = getattr(args, "dir", str(DEFAULT_BASE_DIR))
    args.channel = getattr(args, "channel", "default")
    project_dir = pathlib.Path(args.project_dir) if getattr(args, "project_dir", None) else pathlib.Path.cwd()

    if hasattr(args, "session"):
        args.session = resolve_session_id(
            session_arg=args.session,
            project_dir=project_dir,
            channel=args.channel,
            base_dir=pathlib.Path(args.dir),
        )

    dispatch = {
        "daemon": cmd_daemon,
        "init": cmd_init,
        "send": cmd_send,
        "poll": cmd_poll,
        "listen": cmd_listen,
        "peers": cmd_peers,
        "cleanup": cmd_cleanup,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
