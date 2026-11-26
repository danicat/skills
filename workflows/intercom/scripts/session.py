#!/usr/bin/env python3
# Copyright 2026 Daniela Petruzalek
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
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Intercom session bridge for cross-project and cross-session collaboration
between Antigravity agents.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from typing import Any

SCOPED_UNSET_VARS = (
    "ANTIGRAVITY_CONVERSATION_ID",
    "ANTIGRAVITY_SOURCE_METADATA",
    "ANTIGRAVITY_TRAJECTORY_ID",
)


class SessionError(Exception):
    """Raised on validation, environment, database, or agentapi failures."""


def require_non_empty(value: str, flag_name: str) -> str:
    """Validate that a required string argument is non-empty after trimming."""
    cleaned = value.strip()
    if not cleaned:
        raise SessionError(f"{flag_name} must not be empty")
    return cleaned


def require_agentapi() -> str:
    """Ensure the agentapi binary exists in PATH."""
    exe = shutil.which("agentapi")
    if not exe:
        raise SessionError("required host binary 'agentapi' not found in PATH")
    return exe


def resolve_db_path() -> Path:
    """Locate conversation_summaries.db via ANTIGRAVITY_APP_DATA_DIR or ~/.gemini/antigravity."""
    raw = os.environ.get("ANTIGRAVITY_APP_DATA_DIR")
    if raw is None or raw.strip() == "":
        app_data_dir = Path.home() / ".gemini" / "antigravity"
    else:
        app_data_dir = Path(raw).expanduser()

    db_path = app_data_dir / "conversation_summaries.db"
    if not db_path.is_file():
        raise SessionError(f"conversation database not found: {db_path}")
    return db_path


def ensure_session_not_killed(conversation_id: str) -> None:
    """Fail fast if conversation_id exists in conversation_summaries.db with killed == 1."""
    db_path = resolve_db_path()
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    try:
        with sqlite3.connect(uri, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT killed FROM conversation_summaries WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
    except sqlite3.Error as exc:
        raise SessionError(f"failed to query conversation database {db_path}: {exc}") from exc

    if row is not None and bool(row["killed"]):
        raise SessionError(f"target conversation '{conversation_id}' is killed")


def build_return_context(message: str) -> tuple[str, str]:
    """Build title and full message with [Intercom From: ...] header from caller context."""
    caller_conv_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "").strip() or "unknown"
    caller_project_id = os.environ.get("ANTIGRAVITY_PROJECT_ID", "").strip() or "unknown"
    cwd = os.getcwd()
    cwd_name = Path(cwd).name or cwd

    title = f"Intercom from {caller_conv_id} ({cwd_name})"
    header = f"[Intercom From: {caller_conv_id} | Project: {caller_project_id} | Workspace: {cwd}]"
    full_message = f"{header}\n\n{message}"
    return title, full_message


def build_scoped_env(target_project_id: str) -> dict[str, str]:
    """Scope child agentapi invocation to target_project_id without caller session vars."""
    scoped_env = os.environ.copy()
    for var in SCOPED_UNSET_VARS:
        scoped_env.pop(var, None)
    scoped_env["ANTIGRAVITY_PROJECT_ID"] = target_project_id
    return scoped_env


def format_subprocess_output(proc: subprocess.CompletedProcess[str]) -> str:
    """Format captured stderr and stdout for fail-fast error reporting."""
    parts = [f"exit code {proc.returncode}"]
    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    if stderr:
        parts.append(f"stderr: {stderr}")
    if stdout:
        parts.append(f"stdout: {stdout}")
    return "; ".join(parts)


def run_agentapi_json(
    cmd: list[str],
    *,
    env: dict[str, str],
    action: str,
) -> dict[str, Any]:
    """Run an agentapi command, validate exit status and JSON, and reject error payloads."""
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise SessionError(f"{action} failed ({format_subprocess_output(proc)})")

    raw_stdout = (proc.stdout or "").strip()
    if not raw_stdout:
        raise SessionError(f"{action} returned empty stdout ({format_subprocess_output(proc)})")

    try:
        payload = json.loads(raw_stdout)
    except json.JSONDecodeError as exc:
        raise SessionError(
            f"{action} returned invalid JSON ({exc}); {format_subprocess_output(proc)}"
        ) from exc

    if not isinstance(payload, dict):
        raise SessionError(f"{action} returned non-object JSON: {raw_stdout}")

    if "error" in payload and payload["error"] not in (None, ""):
        raise SessionError(f"{action} returned error payload ({format_subprocess_output(proc)})")

    return payload


def resolve_target_project_id(agentapi_exe: str, conversation_id: str) -> str:
    """Resolve target projectId via agentapi get-conversation-metadata in caller env."""
    payload = run_agentapi_json(
        [agentapi_exe, "get-conversation-metadata", conversation_id],
        env=os.environ.copy(),
        action="agentapi get-conversation-metadata",
    )
    response = payload.get("response")
    conv_meta = response.get("conversationMetadata") if isinstance(response, dict) else None
    meta = conv_meta.get("metadata") if isinstance(conv_meta, dict) else None
    project_id = meta.get("projectId") if isinstance(meta, dict) else None

    if not isinstance(project_id, str) or not project_id.strip():
        raise SessionError(
            "agentapi get-conversation-metadata missing response.conversationMetadata.metadata.projectId"
        )
    return project_id.strip()


def cmd_new(args: argparse.Namespace) -> int:
    """Start a new conversation in a target project ID."""
    target_project_id = require_non_empty(args.project, "--project")
    message = require_non_empty(args.message, "--message")
    agentapi_exe = require_agentapi()

    title, full_message = build_return_context(message)
    scoped_env = build_scoped_env(target_project_id)

    payload = run_agentapi_json(
        [agentapi_exe, "new-conversation", f"--title={title}", full_message],
        env=scoped_env,
        action="agentapi new-conversation",
    )
    print(json.dumps(payload, indent=2))
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    """Send a message to an existing live conversation ID."""
    conversation_id = require_non_empty(args.id, "--id")
    message = require_non_empty(args.message, "--message")
    agentapi_exe = require_agentapi()

    ensure_session_not_killed(conversation_id)
    target_project_id = resolve_target_project_id(agentapi_exe, conversation_id)

    title, full_message = build_return_context(message)
    scoped_env = build_scoped_env(target_project_id)

    payload = run_agentapi_json(
        [agentapi_exe, "send-message", f"--title={title}", conversation_id, full_message],
        env=scoped_env,
        action="agentapi send-message",
    )

    response = payload.get("response")
    send_message = response.get("sendMessage") if isinstance(response, dict) else None
    recipient_id = send_message.get("recipientId") if isinstance(send_message, dict) else None
    if not isinstance(recipient_id, str) or not recipient_id.strip():
        raise SessionError(
            f"agentapi send-message missing response.sendMessage.recipientId: {json.dumps(payload)}"
        )

    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the strictly minimal CLI parser for session.py."""
    parser = argparse.ArgumentParser(
        prog="session.py",
        description="Start or message Antigravity agent sessions across projects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser(
        "new",
        help="Start a new conversation in a target project ID.",
    )
    new_parser.add_argument("--project", required=True, help="Target project ID.")
    new_parser.add_argument("--message", required=True, help="Initial message text.")
    new_parser.set_defaults(func=cmd_new)

    send_parser = subparsers.add_parser(
        "send",
        help="Send a message to an existing conversation ID.",
    )
    send_parser.add_argument("--id", required=True, help="Target conversation ID.")
    send_parser.add_argument("--message", required=True, help="Message text to send.")
    send_parser.set_defaults(func=cmd_send)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except SessionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
