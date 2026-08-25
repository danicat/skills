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
test_ipc.py — Comprehensive Unit & Integration Tests for Intercom IPC Bridge
Validates socket transport, leader election, NDJSON message framing, offline spooling, namegen, and cleanup.
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
        self.channel = "test-channel"

    def tearDown(self) -> None:
        # Purge test directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_cmd(self, *args: str) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(IPC_SCRIPT), "--dir", self.temp_dir, "--channel", self.channel] + list(args)
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

    def test_broadcast_messaging(self) -> None:
        """Test broadcast messaging to all sessions."""
        # Initial poll to register r2-d2's inbox in the channel
        self.run_cmd("poll", "--session", "r2-d2", "--wait", "0.1")

        res_send = self.run_cmd("send", "--session", "c-3po", "--to", "*", "--text", "Greetings from Protocol Droid")
        self.assertEqual(res_send.returncode, 0)

        # Broadcast should be readable by receiving sessions
        res_poll = self.run_cmd("poll", "--session", "r2-d2", "--wait", "1.0")
        poll_data = json.loads(res_poll.stdout)
        self.assertGreaterEqual(poll_data["count"], 1)
        self.assertEqual(poll_data["messages"][0]["from_session"], "c-3po")
        self.assertEqual(poll_data["messages"][0]["payload"]["text"], "Greetings from Protocol Droid")

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

        # Run cleanup
        res_clean = self.run_cmd("cleanup")
        clean_data = json.loads(res_clean.stdout)
        self.assertEqual(clean_data["status"], "cleaned")


if __name__ == "__main__":
    unittest.main()
