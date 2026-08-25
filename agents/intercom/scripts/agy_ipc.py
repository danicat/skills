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
agy_ipc.py — Inter-Session Multi-Agent IPC Transport Bridge
Provides Unix Domain Socket routing, NDJSON framing, and persistent session mailboxes.

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
    """Manages append-only NDJSON inbox/outbox spools with kernel advisory file locks."""

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
                        self.clients[client_session] = writer
                        # Ensure session inbox exists
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

                    # Spool and route message
                    if to_sess in ("*", "all"):
                        target_sessions: Set[str] = set(self.clients.keys())
                        for inbox_file in self.channel_dir.glob("inbox_*.ndjson"):
                            sess_id = inbox_file.stem.replace("inbox_", "")
                            target_sessions.add(sess_id)

                        target_sessions.discard(from_sess)

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
        if to_session in ("*", "all"):
            for inbox_file in channel_dir.glob("inbox_*.ndjson"):
                sess_id = inbox_file.stem.replace("inbox_", "")
                if sess_id != from_session:
                    IPCSpool(channel_dir, sess_id).append_inbox(envelope)
        else:
            spool = IPCSpool(channel_dir, to_session)
            spool.append_inbox(envelope)
        return {"status": "spooled_offline", "envelope": envelope}

    try:
        reader, writer = await asyncio.open_unix_connection(str(sock_path))
        reg_env = make_envelope("register", from_session, "hub", channel_name, {})
        writer.write((json.dumps(reg_env) + "\n").encode("utf-8"))
        await writer.drain()

        # Read welcome
        await asyncio.wait_for(reader.readline(), timeout=2.0)

        # Write actual message
        writer.write((json.dumps(envelope) + "\n").encode("utf-8"))
        await writer.drain()

        writer.close()
        await writer.wait_closed()
        return {"status": "sent", "envelope": envelope}
    except Exception as err:
        # Fallback to direct spooling
        if to_session in ("*", "all"):
            for inbox_file in channel_dir.glob("inbox_*.ndjson"):
                sess_id = inbox_file.stem.replace("inbox_", "")
                if sess_id != from_session:
                    IPCSpool(channel_dir, sess_id).append_inbox(envelope)
        else:
            spool = IPCSpool(channel_dir, to_session)
            spool.append_inbox(envelope)
        return {"status": "fallback_spooled", "error": str(err), "envelope": envelope}


async def stream_listener(channel_dir: pathlib.Path, channel_name: str, session_id: str) -> None:
    """Continuously stream incoming messages for session_id in real time to stdout."""
    ensure_daemon_running(channel_dir, channel_name)
    sock_path = channel_dir / "hub.sock"
    spool = IPCSpool(channel_dir, session_id)
    spool.ensure_inbox_exists()

    # First drain any unread spool
    unread = spool.read_unread(mark_read=True)
    for msg in unread:
        print(json.dumps(msg), flush=True)

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
                        if env.get("type") != "welcome":
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
        asyncio.run(stream_listener(chan_dir, args.channel, args.session))
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
    """Purge channel directory, sockets, and inbox spools."""
    chan_dir = get_channel_dir(args.channel, pathlib.Path(args.dir))
    for f in chan_dir.glob("*"):
        try:
            f.unlink()
        except OSError:
            pass
    print(json.dumps({"status": "cleaned", "channel": args.channel}))


def resolve_session_id(session_arg: Optional[str]) -> str:
    """Resolve session identifier or generate a random communications officer identity."""
    if session_arg and session_arg != "auto":
        return session_arg
    try:
        script_dir = pathlib.Path(__file__).parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        from namegen import get_random_officer

        return get_random_officer()["id"]
    except Exception:
        pass
    return f"officer-{uuid.uuid4().hex[:6]}"


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default=argparse.SUPPRESS, help="Base IPC root directory")
    common.add_argument("--channel", default=argparse.SUPPRESS, help="Channel name")

    parser = argparse.ArgumentParser(description="Multi-Agent Inter-Session IPC Bridge", parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("daemon", help="Run background IPC hub daemon", parents=[common])

    s_parser = sub.add_parser("send", help="Send a message to a session or channel", parents=[common])
    s_parser.add_argument("--session", default=None, help="Sender session ID (defaults to a random Comms Officer codename)")
    s_parser.add_argument("--to", default="*", help="Target session ID or '*' for broadcast")
    s_parser.add_argument("--text", default="", help="Message text content")
    s_parser.add_argument("--json-payload", help="Optional extra JSON dictionary string")

    p_parser = sub.add_parser("poll", help="Poll unread messages from session inbox", parents=[common])
    p_parser.add_argument("--session", default=None, help="Current session ID")
    p_parser.add_argument("--wait", type=float, default=0.0, help="Seconds to wait for new messages")
    p_parser.add_argument("--peek", action="store_true", help="Do not advance unread offset")

    l_parser = sub.add_parser("listen", help="Stream incoming NDJSON messages to stdout", parents=[common])
    l_parser.add_argument("--session", default=None, help="Current session ID")

    sub.add_parser("peers", help="List active sessions on channel", parents=[common])
    sub.add_parser("cleanup", help="Remove channel socket and lock artifacts", parents=[common])

    args = parser.parse_args()

    # Resolve default values if not explicitly provided
    args.dir = getattr(args, "dir", str(DEFAULT_BASE_DIR))
    args.channel = getattr(args, "channel", "default")

    if hasattr(args, "session"):
        args.session = resolve_session_id(args.session)

    dispatch = {
        "daemon": cmd_daemon,
        "send": cmd_send,
        "poll": cmd_poll,
        "listen": cmd_listen,
        "peers": cmd_peers,
        "cleanup": cmd_cleanup,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
