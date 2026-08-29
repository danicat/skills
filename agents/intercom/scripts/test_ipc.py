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
test_ipc.py: Comprehensive Unit & Integration Tests for Intercom IPC Bridge
Validates socket transport, leader election, NDJSON message framing, offline spooling,
sticky project identity persistence, collision prevention, clean restart lifecycles, and cleanup.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT_DIR = pathlib.Path(__file__).parent
IPC_SCRIPT = SCRIPT_DIR / "agy_ipc.py"
NAMEGEN_SCRIPT = SCRIPT_DIR / "namegen.py"


class TestIntercomIPC(unittest.TestCase):
    """Integration test suite for Intercom Unix Domain Socket communication."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="intercom_test_")
        self.project_dir = tempfile.mkdtemp(prefix="project_test_")
        self.channel = "test-channel"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def run_cmd(self, *args: str, project_dir: str = None) -> subprocess.CompletedProcess:
        proj = project_dir or self.project_dir
        cmd = [sys.executable, str(IPC_SCRIPT), "--dir", self.temp_dir, "--channel", self.channel, "--project-dir", proj] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, check=True)

    def test_namegen_script(self) -> None:
        """Test namegen officer generation and id-only output."""
        res_default = subprocess.run([sys.executable, str(NAMEGEN_SCRIPT)], capture_output=True, text=True, check=True)
        self.assertIn("Designated Comms Officer", res_default.stdout)

        res_id = subprocess.run([sys.executable, str(NAMEGEN_SCRIPT), "--id-only"], capture_output=True, text=True, check=True)
        officer_id = res_id.stdout.strip()
        self.assertTrue(len(officer_id) > 0)
        self.assertRegex(officer_id, r"^[a-z0-9-]+$")

        res_all = subprocess.run([sys.executable, str(NAMEGEN_SCRIPT), "--all"], capture_output=True, text=True, check=True)
        self.assertIn("nyota-uhura", res_all.stdout)
        self.assertIn("seven-of-nine", res_all.stdout)

    def test_sticky_identity_persistence(self) -> None:
        """Test that a project directory obtains and retains a single sticky Comms Officer identity."""
        res_claim1 = subprocess.run(
            [sys.executable, str(NAMEGEN_SCRIPT), "--claim", "--project-dir", self.project_dir, "--channel", self.channel, "--dir", self.temp_dir, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data1 = json.loads(res_claim1.stdout)
        id1 = data1["id"]
        self.assertTrue(data1.get("is_sticky"))

        session_file = pathlib.Path(self.project_dir) / ".intercom" / "session.json"
        self.assertTrue(session_file.exists())

        # Second claim should return the exact same identity
        res_claim2 = subprocess.run(
            [sys.executable, str(NAMEGEN_SCRIPT), "--claim", "--project-dir", self.project_dir, "--channel", self.channel, "--dir", self.temp_dir, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data2 = json.loads(res_claim2.stdout)
        self.assertEqual(data2["id"], id1)

    def test_collision_avoidance(self) -> None:
        """Test that two separate projects connecting to the same channel do not collide or impersonate each other."""
        proj2 = tempfile.mkdtemp(prefix="project_test2_")
        try:
            # Init project 1
            res_init1 = self.run_cmd("init", project_dir=self.project_dir)
            data1 = json.loads(res_init1.stdout)
            id1 = data1["session_id"]

            # Mock project 1 as active peer in peers.json
            chan_dir = pathlib.Path(self.temp_dir) / self.channel
            peers_path = chan_dir / "peers.json"
            with open(peers_path, "w", encoding="utf-8") as f:
                json.dump({"channel": self.channel, "active_sessions": [id1]}, f)

            # Init project 2 - must NOT claim id1!
            res_init2 = self.run_cmd("init", project_dir=proj2)
            data2 = json.loads(res_init2.stdout)
            id2 = data2["session_id"]

            self.assertNotEqual(id1, id2, "Project 2 should avoid claiming the active identity of Project 1")
        finally:
            shutil.rmtree(proj2, ignore_errors=True)

    def test_init_command_and_clean_context(self) -> None:
        """Test agy_ipc.py init sets up sticky identity, starts daemon, and clears stale inboxes."""
        res_init = self.run_cmd("init")
        init_data = json.loads(res_init.stdout)
        self.assertEqual(init_data["status"], "ready")
        self.assertEqual(init_data["channel"], self.channel)
        self.assertTrue(init_data.get("is_sticky"))
        self.assertTrue(init_data.get("inbox_reset"))

    def test_direct_message_and_poll(self) -> None:
        """Test sending a direct message to a target session and polling."""
        res_send = self.run_cmd("send", "--session", "nyota-uhura", "--to", "seven-of-nine", "--text", "Telemetry online")
        send_data = json.loads(res_send.stdout)
        self.assertIn(send_data.get("status"), ("sent", "spooled_offline", "fallback_spooled"))

        # Poll inbox for recipient
        res_poll = self.run_cmd("poll", "--session", "seven-of-nine", "--wait", "1.0")
        poll_data = json.loads(res_poll.stdout)
        self.assertEqual(poll_data["count"], 1)
        msg = poll_data["messages"][0]
        self.assertEqual(msg["from_session"], "nyota-uhura")
        self.assertEqual(msg["to_session"], "seven-of-nine")
        self.assertEqual(msg["payload"]["text"], "Telemetry online")

        # Second poll should return 0 (offset advanced)
        res_poll_empty = self.run_cmd("poll", "--session", "seven-of-nine", "--wait", "0.1")
        poll_empty_data = json.loads(res_poll_empty.stdout)
        self.assertEqual(poll_empty_data["count"], 0)

    def test_clean_restart_purges_stale_inbox(self) -> None:
        """Test that init / fresh reset purges stale backlog from prior runs so context isn't contaminated."""
        # 1. Initialize project to establish its sticky identity
        res_init1 = self.run_cmd("init")
        data_init = json.loads(res_init1.stdout)
        sticky_id = data_init["session_id"]

        # 2. Send a message to this sticky session
        self.run_cmd("send", "--session", "c-3po", "--to", sticky_id, "--text", "Yesterday's stale message")

        # 3. Poll peek to verify message is in spool
        res_poll1 = self.run_cmd("poll", "--session", sticky_id, "--peek", "--wait", "0.5")
        data1 = json.loads(res_poll1.stdout)
        self.assertEqual(data1["count"], 1)

        # 4. Run init with --fresh to simulate new session startup
        self.run_cmd("init", "--fresh")

        # 5. Poll should now return 0 because inbox was cleanly reset for the new session
        res_poll2 = self.run_cmd("poll", "--session", sticky_id, "--wait", "0.1")
        data2 = json.loads(res_poll2.stdout)
        self.assertEqual(data2["count"], 0, "Stale messages must be purged on session restart")

    def test_offline_spool_and_json_payload(self) -> None:
        """Test structured JSON payload transmission and persistent mailbox spooling."""
        payload = json.dumps({"diff": "+func TestNew()", "files": 1})
        res_send = self.run_cmd("send", "--session", "kaylee-frye", "--to", "data", "--text", "Engine diff", "--json-payload", payload)
        self.assertEqual(res_send.returncode, 0)

        res_poll = self.run_cmd("poll", "--session", "data", "--wait", "1.0")
        poll_data = json.loads(res_poll.stdout)
        self.assertEqual(poll_data["count"], 1)
        msg = poll_data["messages"][0]
        self.assertEqual(msg["payload"]["text"], "Engine diff")
        self.assertEqual(msg["payload"]["files"], 1)
        self.assertEqual(msg["payload"]["diff"], "+func TestNew()")

    def test_peers_and_cleanup(self) -> None:
        """Test peer discovery output and cleanup."""
        res_peers = self.run_cmd("peers")
        peers_data = json.loads(res_peers.stdout)
        self.assertEqual(peers_data["channel"], self.channel)

        # Run stale cleanup
        res_stale = self.run_cmd("cleanup", "--stale")
        stale_data = json.loads(res_stale.stdout)
        self.assertEqual(stale_data["status"], "stale_cleaned")

        # Run full cleanup
        res_clean = self.run_cmd("cleanup")
        clean_data = json.loads(res_clean.stdout)
        self.assertEqual(clean_data["status"], "cleaned")


if __name__ == "__main__":
    unittest.main()
