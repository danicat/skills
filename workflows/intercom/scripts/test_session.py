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

"""Unit and subprocess contract tests for workflows/intercom/scripts/session.py."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCRIPT_PATH = SCRIPT_DIR / "session.py"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"

CONVERSATION_SUMMARIES_DDL = """
CREATE TABLE conversation_summaries (
  conversation_id text PRIMARY KEY,
  title text NOT NULL DEFAULT "",
  preview text NOT NULL DEFAULT "",
  step_count integer NOT NULL DEFAULT 0,
  last_modified_time datetime NOT NULL DEFAULT "",
  workspace_uris text NOT NULL DEFAULT "",
  status text NOT NULL DEFAULT "",
  source text NOT NULL DEFAULT "",
  project_id text NOT NULL DEFAULT "",
  agent_name text NOT NULL DEFAULT "",
  parent_conversation_id text NOT NULL DEFAULT "",
  nesting_depth integer NOT NULL DEFAULT 0,
  battle_id text NOT NULL DEFAULT "",
  winning_conversation_id text NOT NULL DEFAULT "",
  not_fully_idle numeric NOT NULL DEFAULT false,
  killed numeric NOT NULL DEFAULT false
);
"""

MOCK_AGENTAPI_SOURCE = """#!/usr/bin/env python3
import json
import os
import pathlib
import sys

log_path = os.environ.get("MOCK_AGENTAPI_LOG")
if log_path:
    entry = {
        "argv": sys.argv[1:],
        "env": {
            "ANTIGRAVITY_PROJECT_ID": os.environ.get("ANTIGRAVITY_PROJECT_ID"),
            "ANTIGRAVITY_CONVERSATION_ID": os.environ.get("ANTIGRAVITY_CONVERSATION_ID"),
            "ANTIGRAVITY_SOURCE_METADATA": os.environ.get("ANTIGRAVITY_SOURCE_METADATA"),
            "ANTIGRAVITY_TRAJECTORY_ID": os.environ.get("ANTIGRAVITY_TRAJECTORY_ID"),
            "ANTIGRAVITY_LS_ADDRESS": os.environ.get("ANTIGRAVITY_LS_ADDRESS"),
            "ANTIGRAVITY_CSRF_TOKEN": os.environ.get("ANTIGRAVITY_CSRF_TOKEN"),
            "ANTIGRAVITY_APP_DATA_DIR": os.environ.get("ANTIGRAVITY_APP_DATA_DIR"),
        },
    }
    with pathlib.Path(log_path).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\\n")

cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "get-conversation-metadata":
    raw = os.environ.get("MOCK_METADATA_STDOUT")
    if raw is not None:
        print(raw)
        sys.exit(int(os.environ.get("MOCK_METADATA_EXIT", "0")))
    conv_id = sys.argv[2]
    payload = {
        "response": {
            "conversationMetadata": {
                "metadata": {
                    "projectId": os.environ.get("MOCK_TARGET_PROJECT_ID", "target-proj-123"),
                    "rootConversationId": conv_id,
                }
            }
        }
    }
    print(json.dumps(payload))
    sys.exit(0)

if cmd == "new-conversation":
    raw = os.environ.get("MOCK_NEW_STDOUT")
    if raw is not None:
        print(raw)
        sys.exit(int(os.environ.get("MOCK_NEW_EXIT", "0")))
    payload = {"response": {"newConversation": {"conversationId": "new-conv-456"}}}
    print(json.dumps(payload))
    sys.exit(0)

if cmd == "send-message":
    raw = os.environ.get("MOCK_SEND_STDOUT")
    if raw is not None:
        print(raw)
        sys.exit(int(os.environ.get("MOCK_SEND_EXIT", "0")))
    recipient_id = sys.argv[-2]
    payload = {"response": {"sendMessage": {"recipientId": recipient_id}}}
    print(json.dumps(payload))
    sys.exit(0)

print(json.dumps({"error": f"unexpected mock subcommand: {cmd}"}))
sys.exit(1)
"""


def create_test_db(app_data_dir: Path, rows: list[tuple[str, str, int]]) -> Path:
    db_path = app_data_dir / "conversation_summaries.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(CONVERSATION_SUMMARIES_DDL)
        conn.executemany(
            """
            INSERT INTO conversation_summaries (conversation_id, project_id, killed)
            VALUES (?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def install_mock_agentapi(bin_dir: Path) -> Path:
    exe_path = bin_dir / "agentapi"
    exe_path.write_text(MOCK_AGENTAPI_SOURCE, encoding="utf-8")
    exe_path.chmod(exe_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return exe_path


class TestSessionCLI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.app_data_dir = self.root / "antigravity"
        self.app_data_dir.mkdir()
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.workspace_dir = self.root / "caller-workspace"
        self.workspace_dir.mkdir()
        self.mock_log = self.root / "agentapi_calls.jsonl"
        install_mock_agentapi(self.bin_dir)

        create_test_db(
            self.app_data_dir,
            [
                ("conv-live-1", "proj-target-abc", 0),
                ("conv-killed-1", "proj-killed", 1),
            ],
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def make_env(self, include_bin: bool = True, **overrides: str | None) -> dict[str, str]:
        env = {
            "PATH": f"{self.bin_dir}:{os.environ.get('PATH', '')}" if include_bin else "",
            "HOME": str(self.root),
            "ANTIGRAVITY_APP_DATA_DIR": str(self.app_data_dir),
            "ANTIGRAVITY_CONVERSATION_ID": "caller-conv-999",
            "ANTIGRAVITY_PROJECT_ID": "caller-proj-888",
            "ANTIGRAVITY_SOURCE_METADATA": '{"tool":{"conversationId":"caller-conv-999"}}',
            "ANTIGRAVITY_TRAJECTORY_ID": "traj-777",
            "ANTIGRAVITY_LS_ADDRESS": "localhost:64235",
            "ANTIGRAVITY_CSRF_TOKEN": "csrf-secret-token",
            "MOCK_AGENTAPI_LOG": str(self.mock_log),
            "MOCK_TARGET_PROJECT_ID": "proj-target-abc",
        }
        for key, val in overrides.items():
            if val is None:
                env.pop(key, None)
            else:
                env[key] = val
        return env

    def run_cli(
        self,
        *args: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT_PATH), *args],
            env=env if env is not None else self.make_env(),
            cwd=str(self.workspace_dir),
            capture_output=True,
            text=True,
            check=False,
        )

    def read_mock_calls(self) -> list[dict]:
        if not self.mock_log.exists():
            return []
        return [
            json.loads(line)
            for line in self.mock_log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_new_scopes_env_builds_header_and_calls_new_conversation(self):
        res = self.run_cli("new", "--project", "proj-new-777", "--message", "Start build review")
        self.assertEqual(res.returncode, 0, res.stderr)

        out = json.loads(res.stdout)
        self.assertEqual(out["response"]["newConversation"]["conversationId"], "new-conv-456")

        calls = self.read_mock_calls()
        self.assertEqual(len(calls), 1)
        call = calls[0]

        expected_cwd = str(self.workspace_dir.resolve())
        expected_title = f"Intercom from caller-conv-999 ({self.workspace_dir.name})"
        expected_prompt = (
            "[Intercom From: caller-conv-999 | Project: caller-proj-888 | "
            f"Workspace: {expected_cwd}]\n\nStart build review"
        )
        self.assertEqual(
            call["argv"],
            ["new-conversation", f"--title={expected_title}", expected_prompt],
        )
        self.assertEqual(call["env"]["ANTIGRAVITY_PROJECT_ID"], "proj-new-777")
        self.assertIsNone(call["env"]["ANTIGRAVITY_CONVERSATION_ID"])
        self.assertIsNone(call["env"]["ANTIGRAVITY_SOURCE_METADATA"])
        self.assertIsNone(call["env"]["ANTIGRAVITY_TRAJECTORY_ID"])
        self.assertEqual(call["env"]["ANTIGRAVITY_LS_ADDRESS"], "localhost:64235")
        self.assertEqual(call["env"]["ANTIGRAVITY_CSRF_TOKEN"], "csrf-secret-token")
        self.assertEqual(call["env"]["ANTIGRAVITY_APP_DATA_DIR"], str(self.app_data_dir))

    def test_send_checks_liveness_resolves_project_and_scopes_env(self):
        res = self.run_cli("send", "--id", "conv-live-1", "--message", "Tests pass")
        self.assertEqual(res.returncode, 0, res.stderr)

        out = json.loads(res.stdout)
        self.assertEqual(out["response"]["sendMessage"]["recipientId"], "conv-live-1")

        calls = self.read_mock_calls()
        self.assertEqual(len(calls), 2)
        meta_call, send_call = calls

        self.assertEqual(meta_call["argv"], ["get-conversation-metadata", "conv-live-1"])
        self.assertEqual(meta_call["env"]["ANTIGRAVITY_PROJECT_ID"], "caller-proj-888")
        self.assertEqual(meta_call["env"]["ANTIGRAVITY_CONVERSATION_ID"], "caller-conv-999")

        expected_cwd = str(self.workspace_dir.resolve())
        expected_title = f"Intercom from caller-conv-999 ({self.workspace_dir.name})"
        expected_body = (
            "[Intercom From: caller-conv-999 | Project: caller-proj-888 | "
            f"Workspace: {expected_cwd}]\n\nTests pass"
        )
        self.assertEqual(
            send_call["argv"],
            ["send-message", f"--title={expected_title}", "conv-live-1", expected_body],
        )
        self.assertEqual(send_call["env"]["ANTIGRAVITY_PROJECT_ID"], "proj-target-abc")
        self.assertIsNone(send_call["env"]["ANTIGRAVITY_CONVERSATION_ID"])
        self.assertIsNone(send_call["env"]["ANTIGRAVITY_SOURCE_METADATA"])
        self.assertIsNone(send_call["env"]["ANTIGRAVITY_TRAJECTORY_ID"])
        self.assertEqual(send_call["env"]["ANTIGRAVITY_LS_ADDRESS"], "localhost:64235")
        self.assertEqual(send_call["env"]["ANTIGRAVITY_CSRF_TOKEN"], "csrf-secret-token")

    def test_missing_caller_env_defaults_to_unknown(self):
        env = self.make_env(ANTIGRAVITY_CONVERSATION_ID=None, ANTIGRAVITY_PROJECT_ID=None)
        res = self.run_cli("new", "--project", "proj-new-777", "--message", "Manual ping", env=env)
        self.assertEqual(res.returncode, 0, res.stderr)

        calls = self.read_mock_calls()
        self.assertEqual(len(calls), 1)
        title_arg = calls[0]["argv"][1]
        prompt_arg = calls[0]["argv"][2]
        self.assertTrue(title_arg.startswith("--title=Intercom from unknown ("))
        self.assertIn("[Intercom From: unknown | Project: unknown | Workspace:", prompt_arg)

    def test_rejects_unexpected_flags_and_subcommands(self):
        for bad_args in (
            ("list",),
            ("inspect", "conv-live-1"),
            ("send", "--id", "conv-live-1", "--message", "hi", "--json"),
            ("send", "--id", "conv-live-1", "--message", "hi", "--dry-run"),
            ("send", "--id", "conv-live-1", "--file", "msg.txt"),
            ("new", "--project", "proj-1", "--message", "hi", "--title", "custom"),
        ):
            res = self.run_cli(*bad_args)
            self.assertEqual(res.returncode, 2, f"expected argparse rejection for {bad_args}")

    def test_fail_fast_errors(self):
        # Missing agentapi binary
        res_no_bin = self.run_cli(
            "new", "--project", "proj-1", "--message", "hi", env=self.make_env(include_bin=False)
        )
        self.assertEqual(res_no_bin.returncode, 1)
        self.assertIn("agentapi", res_no_bin.stderr.lower())

        # Empty/whitespace inputs
        for args in (
            ("new", "--project", "   ", "--message", "hi"),
            ("new", "--project", "proj-1", "--message", "   "),
            ("send", "--id", "   ", "--message", "hi"),
            ("send", "--id", "conv-live-1", "--message", "   "),
        ):
            res_empty = self.run_cli(*args)
            self.assertEqual(res_empty.returncode, 1, f"expected fail-fast for {args}")

        # Killed session rejected before calling agentapi
        res_killed = self.run_cli("send", "--id", "conv-killed-1", "--message", "wake up")
        self.assertEqual(res_killed.returncode, 1)
        self.assertIn("killed", res_killed.stderr.lower())
        self.assertEqual(self.read_mock_calls(), [])

        # Missing DB fails fast on send
        res_no_db = self.run_cli(
            "send",
            "--id",
            "conv-live-1",
            "--message",
            "hi",
            env=self.make_env(ANTIGRAVITY_APP_DATA_DIR=str(self.root / "missing-db-dir")),
        )
        self.assertEqual(res_no_db.returncode, 1)
        self.assertIn("conversation_summaries.db", res_no_db.stderr)

        # Non-zero exit prints stderr/stdout
        res_exit = self.run_cli(
            "new",
            "--project",
            "proj-1",
            "--message",
            "hi",
            env=self.make_env(MOCK_NEW_STDOUT='{"error":"rpc failure"}', MOCK_NEW_EXIT="1"),
        )
        self.assertEqual(res_exit.returncode, 1)
        self.assertIn("rpc failure", res_exit.stderr)

        # Invalid JSON from agentapi
        res_bad_json = self.run_cli(
            "new",
            "--project",
            "proj-1",
            "--message",
            "hi",
            env=self.make_env(MOCK_NEW_STDOUT="not-json", MOCK_NEW_EXIT="0"),
        )
        self.assertEqual(res_bad_json.returncode, 1)
        self.assertIn("not-json", res_bad_json.stderr)

        # JSON error payload even on exit 0
        res_json_err = self.run_cli(
            "send",
            "--id",
            "conv-live-1",
            "--message",
            "hi",
            env=self.make_env(
                MOCK_SEND_STDOUT='{"response":{},"error":"PermissionDenied"}',
                MOCK_SEND_EXIT="0",
            ),
        )
        self.assertEqual(res_json_err.returncode, 1)
        self.assertIn("PermissionDenied", res_json_err.stderr)

        # Missing projectId from metadata
        res_no_proj = self.run_cli(
            "send",
            "--id",
            "conv-live-1",
            "--message",
            "hi",
            env=self.make_env(
                MOCK_METADATA_STDOUT='{"response":{"conversationMetadata":{"metadata":{}}}}',
                MOCK_METADATA_EXIT="0",
            ),
        )
        self.assertEqual(res_no_proj.returncode, 1)
        self.assertIn("projectId", res_no_proj.stderr)

    def test_skill_md_has_no_antigravity_env_or_internal_leaks(self):
        content = SKILL_MD_PATH.read_text(encoding="utf-8")
        self.assertNotIn("ANTIGRAVITY_", content)
        self.assertNotIn("env -u", content)
        self.assertNotIn("::", content)
        self.assertLess(len(content.encode("utf-8")), 6000)


if __name__ == "__main__":
    unittest.main()
