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

"""Intercom CLI for cross-session and cross-project messaging via Antigravity agentapi."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

SENDER_ENV_VARS_TO_STRIP = (
    "ANTIGRAVITY_CONVERSATION_ID",
    "ANTIGRAVITY_SOURCE_METADATA",
    "ANTIGRAVITY_TRAJECTORY_ID",
)


class IntercomError(RuntimeError):
    """Raised when an Intercom or agentapi operation fails."""


def require_agentapi_bin() -> str:
    """Resolve the agentapi binary on PATH or fail fast."""
    binary = shutil.which("agentapi")
    if not binary:
        raise IntercomError(
            "FATAL: 'agentapi' binary not found on PATH. "
            "Ensure you are running inside an Antigravity session with agentapi available."
        )
    return binary


def require_summaries_db_path() -> Path:
    """Return the path to conversation_summaries.db or fail fast."""
    app_data_dir = os.environ.get("ANTIGRAVITY_APP_DATA_DIR")
    if not app_data_dir:
        raise IntercomError(
            "FATAL: ANTIGRAVITY_APP_DATA_DIR environment variable is not set."
        )
    db_path = Path(app_data_dir) / "conversation_summaries.db"
    if not db_path.is_file():
        raise IntercomError(
            f"FATAL: Antigravity conversation database not found at '{db_path}'."
        )
    return db_path


def build_cross_project_env(
    base_env: dict[str, str], target_project_id: str
) -> dict[str, str]:
    """Strip sender conversation bindings and set ANTIGRAVITY_PROJECT_ID to target_project_id."""
    if not target_project_id or not target_project_id.strip():
        raise IntercomError(
            "FATAL: target_project_id is empty; cannot construct cross-project environment."
        )
    env = dict(base_env)
    for key in SENDER_ENV_VARS_TO_STRIP:
        env.pop(key, None)
    env["ANTIGRAVITY_PROJECT_ID"] = target_project_id.strip()
    return env


def format_envelope(
    message: str,
    sender_conversation_id: str,
    sender_project_id: str,
    sender_workspace: str,
) -> str:
    """Prepend a structured return-address header so the recipient can reply across projects."""
    if not message or not message.strip():
        raise IntercomError("FATAL: Outgoing message content cannot be empty.")
    header = (
        f"[Intercom From: {sender_conversation_id} | "
        f"Project: {sender_project_id} | "
        f"Workspace: {sender_workspace}]"
    )
    return f"{header}\n\n{message}"


def run_agentapi(
    args: list[str], env: dict[str, str] | None = None
) -> dict[str, Any]:
    """Execute agentapi and parse its JSON response, failing fast on any error."""
    binary = require_agentapi_bin()
    cmd = [binary, *args]
    proc = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    raw_out = proc.stdout.strip()
    raw_err = proc.stderr.strip()

    parsed: dict[str, Any] = {}
    if raw_out:
        try:
            parsed = json.loads(raw_out)
        except json.JSONDecodeError as exc:
            raise IntercomError(
                f"FATAL: Failed to parse JSON from {' '.join(cmd)} "
                f"(exit={proc.returncode}): {exc}\nSTDOUT: {raw_out}\nSTDERR: {raw_err}"
            ) from exc

    if proc.returncode != 0 or parsed.get("error"):
        err_detail = parsed.get("error") or raw_err or raw_out or "unknown error"
        raise IntercomError(
            f"FATAL: agentapi command failed (exit={proc.returncode}): {' '.join(cmd)}\n"
            f"Error: {err_detail}"
        )

    return parsed


def inspect_conversation(conversation_id: str) -> dict[str, Any]:
    """Query live conversation metadata via agentapi get-conversation-metadata."""
    if not UUID_RE.match(conversation_id):
        raise IntercomError(
            f"FATAL: Invalid conversation UUID '{conversation_id}'. Expected 36-char UUID."
        )
    payload = run_agentapi(["get-conversation-metadata", conversation_id])
    meta = (
        payload.get("response", {})
        .get("conversationMetadata", {})
        .get("metadata")
    )
    if not isinstance(meta, dict):
        raise IntercomError(
            f"FATAL: Conversation '{conversation_id}' returned empty metadata: "
            f"{json.dumps(payload)}"
        )

    workspace_uris = meta.get("workspaceUris") or []
    return {
        "conversation_id": conversation_id,
        "project_id": meta.get("projectId") or "",
        "workspace_uris": workspace_uris,
        "root_conversation_id": meta.get("rootConversationId") or "",
        "parent_conversation_id": meta.get("parentConversationId") or "",
        "created_at": meta.get("createdAt") or "",
    }


def discover_sessions(
    workspace_filter: str | None = None,
    limit: int = 15,
    include_subagents: bool = False,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Query conversation_summaries.db for active conversations ordered by last_modified_time."""
    resolved_db = db_path if db_path is not None else require_summaries_db_path()
    uri = f"file:{quote(str(resolved_db))}?mode=ro"

    query = """
        SELECT
            conversation_id,
            project_id,
            title,
            workspace_uris,
            status,
            parent_conversation_id,
            last_modified_time
        FROM conversation_summaries
        WHERE killed = 0
    """
    params: list[Any] = []
    if not include_subagents:
        query += " AND parent_conversation_id = ''"
    if workspace_filter:
        query += " AND (LOWER(workspace_uris) LIKE ? OR LOWER(title) LIKE ?)"
        pattern = f"%{workspace_filter.lower()}%"
        params.extend([pattern, pattern])

    query += " ORDER BY last_modified_time DESC LIMIT ?"
    params.append(limit)

    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    sessions: list[dict[str, Any]] = []
    for row in rows:
        raw_uris = row["workspace_uris"] or "[]"
        try:
            uris = json.loads(raw_uris) if raw_uris.strip() else []
        except json.JSONDecodeError:
            uris = [raw_uris]
        sessions.append(
            {
                "conversation_id": row["conversation_id"],
                "project_id": row["project_id"],
                "title": row["title"],
                "workspace_uris": uris,
                "status": row["status"],
                "parent_conversation_id": row["parent_conversation_id"],
                "last_modified_time": row["last_modified_time"],
            }
        )
    return sessions


def resolve_target(target: str) -> dict[str, Any]:
    """Resolve either an explicit conversation UUID or a workspace/title query to live metadata."""
    if UUID_RE.match(target):
        return inspect_conversation(target)

    matches = discover_sessions(workspace_filter=target, limit=5)
    if not matches:
        raise IntercomError(
            f"FATAL: No active root conversation found matching workspace or title '{target}'."
        )
    chosen = matches[0]
    live_info = inspect_conversation(chosen["conversation_id"])
    live_info["title"] = chosen.get("title", "")
    live_info["status"] = chosen.get("status", "")
    return live_info


def cmd_whoami() -> int:
    """Print the current session's Intercom identity and workspace metadata."""
    conv_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    proj_id = os.environ.get("ANTIGRAVITY_PROJECT_ID")
    if not conv_id or not proj_id:
        raise IntercomError(
            "FATAL: ANTIGRAVITY_CONVERSATION_ID or ANTIGRAVITY_PROJECT_ID is not set in environment."
        )
    info = inspect_conversation(conv_id)
    info["cwd"] = os.getcwd()
    print(json.dumps(info, indent=2))
    return 0


def cmd_inspect(conversation_id: str) -> int:
    """Inspect a specific conversation ID and output JSON metadata."""
    info = inspect_conversation(conversation_id)
    print(json.dumps(info, indent=2))
    return 0


def cmd_discover(
    workspace: str | None, limit: int, include_subagents: bool
) -> int:
    """List recent active sessions across workspaces."""
    sessions = discover_sessions(
        workspace_filter=workspace,
        limit=limit,
        include_subagents=include_subagents,
    )
    print(json.dumps({"sessions": sessions, "count": len(sessions)}, indent=2))
    return 0


def cmd_send(target: str, message: str, title: str | None) -> int:
    """Send a message to a target conversation (same-project or cross-project)."""
    sender_conv_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    sender_proj_id = os.environ.get("ANTIGRAVITY_PROJECT_ID")
    if not sender_conv_id or not sender_proj_id:
        raise IntercomError(
            "FATAL: ANTIGRAVITY_CONVERSATION_ID or ANTIGRAVITY_PROJECT_ID is missing from environment."
        )

    target_info = resolve_target(target)
    target_conv_id = target_info["conversation_id"]
    target_proj_id = target_info["project_id"]
    if not target_proj_id:
        raise IntercomError(
            f"FATAL: Target conversation '{target_conv_id}' has no projectId in metadata."
        )

    cwd = os.getcwd()
    effective_title = (
        title
        if title
        else f"Intercom from {sender_conv_id} ({Path(cwd).name})"
    )
    framed_message = format_envelope(
        message=message,
        sender_conversation_id=sender_conv_id,
        sender_project_id=sender_proj_id,
        sender_workspace=cwd,
    )

    sanitized_env = build_cross_project_env(
        dict(os.environ), target_project_id=target_proj_id
    )
    result = run_agentapi(
        [
            "send-message",
            f"--title={effective_title}",
            target_conv_id,
            framed_message,
        ],
        env=sanitized_env,
    )

    output = {
        "status": "sent",
        "sender_conversation_id": sender_conv_id,
        "sender_project_id": sender_proj_id,
        "target_conversation_id": target_conv_id,
        "target_project_id": target_proj_id,
        "target_workspaces": target_info["workspace_uris"],
        "title": effective_title,
        "agentapi_response": result.get("response", {}),
    }
    print(json.dumps(output, indent=2))
    return 0


def cmd_spawn(
    target: str, prompt: str, title: str | None, model: str | None
) -> int:
    """Spawn a new conversation in a target project using cross-project env sanitization."""
    sender_conv_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    sender_proj_id = os.environ.get("ANTIGRAVITY_PROJECT_ID")
    if not sender_conv_id or not sender_proj_id:
        raise IntercomError(
            "FATAL: ANTIGRAVITY_CONVERSATION_ID or ANTIGRAVITY_PROJECT_ID is missing from environment."
        )

    target_info = resolve_target(target)
    target_proj_id = target_info["project_id"]
    if not target_proj_id:
        raise IntercomError(
            f"FATAL: Resolved target '{target}' has no projectId in metadata."
        )

    cwd = os.getcwd()
    effective_title = (
        title
        if title
        else f"Spawned by {sender_conv_id} ({Path(cwd).name})"
    )
    framed_prompt = format_envelope(
        message=prompt,
        sender_conversation_id=sender_conv_id,
        sender_project_id=sender_proj_id,
        sender_workspace=cwd,
    )

    args = ["new-conversation", f"--title={effective_title}"]
    if model:
        args.append(f"--model={model}")
    args.append(framed_prompt)

    sanitized_env = build_cross_project_env(
        dict(os.environ), target_project_id=target_proj_id
    )
    result = run_agentapi(args, env=sanitized_env)
    print(
        json.dumps(
            {
                "status": "spawned",
                "sender_conversation_id": sender_conv_id,
                "target_project_id": target_proj_id,
                "target_workspaces": target_info["workspace_uris"],
                "title": effective_title,
                "agentapi_response": result.get("response", {}),
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intercom.py",
        description="Cross-session and cross-project messaging via Antigravity agentapi.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("whoami", help="Print current session identity and project metadata.")

    inspect_p = sub.add_parser(
        "inspect", help="Inspect conversation metadata by UUID."
    )
    inspect_p.add_argument("conversation_id", help="Target conversation UUID.")

    disc_p = sub.add_parser(
        "discover", help="Discover recent root sessions across workspaces."
    )
    disc_p.add_argument(
        "--workspace",
        "-w",
        default=None,
        help="Optional workspace path or conversation title substring filter.",
    )
    disc_p.add_argument(
        "--limit",
        "-n",
        type=int,
        default=15,
        help="Maximum number of sessions to return (default: 15).",
    )
    disc_p.add_argument(
        "--include-subagents",
        action="store_true",
        help="Include child subagent conversations in output.",
    )

    send_p = sub.add_parser(
        "send",
        help="Send a message to a peer conversation UUID or workspace name.",
    )
    send_p.add_argument(
        "target",
        help="Recipient conversation UUID or workspace/title substring.",
    )
    send_p.add_argument("message", help="Message content to send.")
    send_p.add_argument(
        "--title", "-t", default=None, help="Optional message notification title."
    )

    spawn_p = sub.add_parser(
        "spawn",
        help="Spawn a new conversation in the project of a target UUID or workspace.",
    )
    spawn_p.add_argument(
        "target",
        help="Reference conversation UUID or workspace substring whose projectId will be used.",
    )
    spawn_p.add_argument("prompt", help="Initial prompt for the new conversation.")
    spawn_p.add_argument(
        "--title", "-t", default=None, help="Optional conversation title."
    )
    spawn_p.add_argument(
        "--model",
        "-m",
        choices=["flash_lite", "flash", "pro"],
        default=None,
        help="Optional model selection.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "whoami":
            return cmd_whoami()
        if args.command == "inspect":
            return cmd_inspect(args.conversation_id)
        if args.command == "discover":
            return cmd_discover(
                workspace=args.workspace,
                limit=args.limit,
                include_subagents=args.include_subagents,
            )
        if args.command == "send":
            return cmd_send(
                target=args.target, message=args.message, title=args.title
            )
        if args.command == "spawn":
            return cmd_spawn(
                target=args.target,
                prompt=args.prompt,
                title=args.title,
                model=args.model,
            )
        raise IntercomError(f"FATAL: Unhandled command '{args.command}'.")
    except IntercomError as err:
        print(str(err), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
