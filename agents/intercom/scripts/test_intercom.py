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

"""Unit tests for the Intercom cross-project agentapi CLI."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import intercom


class TestIntercom(unittest.TestCase):
    def test_build_cross_project_env_strips_sender_bindings(self) -> None:
        base_env = {
            "PATH": "/usr/bin:/bin",
            "ANTIGRAVITY_LS_ADDRESS": "localhost:54216",
            "ANTIGRAVITY_CSRF_TOKEN": "token-123",
            "ANTIGRAVITY_CONVERSATION_ID": "3cf578b3-76ca-4dbd-a22d-9c80ed25796c",
            "ANTIGRAVITY_SOURCE_METADATA": '{"tool":{"conversationId":"3cf578b3"}}',
            "ANTIGRAVITY_TRAJECTORY_ID": "a016d323-f5e9-4d6d-b304-023611c924f2",
            "ANTIGRAVITY_PROJECT_ID": "2be94033-91de-45ca-a685-d2ebb4f98a9f",
        }
        target_proj = "5fa83577-83a6-420f-bbc5-ff497847ae63"
        sanitized = intercom.build_cross_project_env(base_env, target_proj)

        self.assertEqual(sanitized["ANTIGRAVITY_PROJECT_ID"], target_proj)
        self.assertEqual(sanitized["ANTIGRAVITY_LS_ADDRESS"], "localhost:54216")
        self.assertNotIn("ANTIGRAVITY_CONVERSATION_ID", sanitized)
        self.assertNotIn("ANTIGRAVITY_SOURCE_METADATA", sanitized)
        self.assertNotIn("ANTIGRAVITY_TRAJECTORY_ID", sanitized)

    def test_build_cross_project_env_fails_fast_on_empty_project(self) -> None:
        with self.assertRaises(intercom.IntercomError):
            intercom.build_cross_project_env({}, "   ")

    def test_format_envelope_includes_return_address(self) -> None:
        msg = intercom.format_envelope(
            message="Please take over the campaign.",
            sender_conversation_id="3cf578b3-76ca-4dbd-a22d-9c80ed25796c",
            sender_project_id="2be94033-91de-45ca-a685-d2ebb4f98a9f",
            sender_workspace="~/projects/blog",
        )
        self.assertIn(
            "[Intercom From: 3cf578b3-76ca-4dbd-a22d-9c80ed25796c | "
            "Project: 2be94033-91de-45ca-a685-d2ebb4f98a9f | "
            "Workspace: ~/projects/blog]",
            msg,
        )
        self.assertTrue(msg.endswith("\n\nPlease take over the campaign."))

    def test_format_envelope_fails_fast_on_empty_message(self) -> None:
        with self.assertRaises(intercom.IntercomError):
            intercom.format_envelope(
                message="  ",
                sender_conversation_id="3cf578b3-76ca-4dbd-a22d-9c80ed25796c",
                sender_project_id="2be94033-91de-45ca-a685-d2ebb4f98a9f",
                sender_workspace="~/projects/blog",
            )

    def test_discover_sessions_filters_by_workspace_and_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "conversation_summaries.db"
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE conversation_summaries (
                        conversation_id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        workspace_uris TEXT NOT NULL,
                        status TEXT NOT NULL,
                        parent_conversation_id TEXT NOT NULL,
                        killed NUMERIC NOT NULL,
                        last_modified_time DATETIME NOT NULL
                    )
                    """
                )
                conn.executemany(
                    """
                    INSERT INTO conversation_summaries VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            "7566dedc-5206-4975-bb23-7a879a542f93",
                            "5fa83577-83a6-420f-bbc5-ff497847ae63",
                            "Social Media Post Preparation",
                            '["file:///workspace/socials"]',
                            "CASCADE_RUN_STATUS_IDLE",
                            "",
                            0,
                            "2026-10-13 22:41:45+00:00",
                        ),
                        (
                            "11111111-2222-3333-4444-555555555555",
                            "5fa83577-83a6-420f-bbc5-ff497847ae63",
                            "Subagent Worker",
                            '["file:///workspace/socials"]',
                            "CASCADE_RUN_STATUS_IDLE",
                            "7566dedc-5206-4975-bb23-7a879a542f93",
                            0,
                            "2026-10-13 22:45:00+00:00",
                        ),
                        (
                            "3cf578b3-76ca-4dbd-a22d-9c80ed25796c",
                            "2be94033-91de-45ca-a685-d2ebb4f98a9f",
                            "Blog Post Review",
                            '["file:///workspace/blog"]',
                            "CASCADE_RUN_STATUS_RUNNING",
                            "",
                            0,
                            "2026-10-13 22:50:00+00:00",
                        ),
                    ],
                )

            roots = intercom.discover_sessions(
                workspace_filter="socials", limit=5, db_path=db_path
            )
            self.assertEqual(len(roots), 1)
            self.assertEqual(
                roots[0]["conversation_id"],
                "7566dedc-5206-4975-bb23-7a879a542f93",
            )
            self.assertEqual(
                roots[0]["workspace_uris"], ["file:///workspace/socials"]
            )

            with_subs = intercom.discover_sessions(
                workspace_filter="socials",
                limit=5,
                include_subagents=True,
                db_path=db_path,
            )
            self.assertEqual(len(with_subs), 2)

    def test_inspect_conversation_rejects_non_uuid(self) -> None:
        with self.assertRaises(intercom.IntercomError):
            intercom.inspect_conversation("not-a-valid-uuid")


if __name__ == "__main__":
    unittest.main()
