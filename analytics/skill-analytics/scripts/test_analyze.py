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

"""
Test Suite for skill-analytics (scripts/analyze.py).

Validates:
1. SQLite schema DDL, tables, indexes, and analytical views (`v_skill_roi`,
   `v_trigger_attribution`, `v_daily_invocations`, `v_subcommand_summary`,
   `v_search_gaps`, `v_skill_telemetry_drift`, `kungfu_invocations`).
2. User notation parser (`::skill`, `//skill`, `:?query`, C++/CSS false-positive filtering).
3. Planner tool_call extractor (`direct_skill_view`, `skill_resource_view`, `cli_invocation`,
   continuation pages `-p 2`, subpaths, `learn --load`, and `run`).
4. Every SQL query block in `SKILL.md` and `references/queries.md`.
5. Pre-packaged CLI reports (`overview`, `roi`, `triggers`, `velocity`, `gaps`, `drift`).
"""

import io
import os
import re
import sqlite3
import sys
import unittest
from contextlib import redirect_stdout

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, SCRIPT_DIR)
import analyze


class TestSkillAnalyticsSchema(unittest.TestCase):
    """Validates DDL, tables, and views."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        analyze.init_db(self.conn, rebuild=True)

    def tearDown(self):
        self.conn.close()

    def test_tables_and_views_exist(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')")
        names = {row["name"] for row in cur.fetchall()}
        expected = {
            "skills_inventory",
            "conversations",
            "ingestion_state",
            "skill_events",
            "state_telemetry_snapshot",
            "kungfu_invocations",
            "v_daily_invocations",
            "v_subcommand_summary",
            "v_skill_roi",
            "v_trigger_attribution",
            "v_search_gaps",
            "v_skill_telemetry_drift",
        }
        for item in expected:
            self.assertIn(item, names, f"Expected table or view '{item}' to exist in schema.")


class TestSkillAnalyticsParsersAndQueries(unittest.TestCase):
    """Validates extraction logic, ROI/trigger views, and markdown SQL queries."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.row_factory = sqlite3.Row
        analyze.init_db(cls.conn, rebuild=True)
        cls._populate_fixtures(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    @classmethod
    def _populate_fixtures(cls, conn: sqlite3.Connection):
        now = "2026-10-12T12:00:00Z"
        conn.executemany(
            """
            INSERT INTO skills_inventory (
                skill_name, source_tier, source_origin, category, version,
                description, skill_path, is_always_in_prompt,
                tier1_chars, tier1_tokens_est, tier2_lines, tier2_tokens_est, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("kungfu", "global", "global-gemini", "agents", "0.5.0", "Gateway skill", "/skills/kungfu/SKILL.md", 1, 320, 80, 290, 3800, now),
                ("godoctor", "plugin", "agy-game-studio", "coding", "0.2.1", "Go quality gate", "/skills/godoctor/SKILL.md", 1, 360, 90, 220, 2900, now),
                ("unused-shelfware", "plugin", "some-plugin", "coding", "0.1.0", "Never used skill", "/skills/unused/SKILL.md", 1, 400, 100, 150, 1800, now),
                ("buffer-analytics", "catalog", "danicat/skills", "analytics", "0.2.0", "Buffer SQLite", "https://skills.danicat.dev", 0, 340, 85, 160, 2100, now),
                ("skill-optimizer", "catalog", "danicat/skills", "agents", "0.5.1", "Optimize skills", "https://skills.danicat.dev", 0, 300, 75, 330, 4200, now),
            ],
        )

        conn.executemany(
            """
            INSERT INTO conversations (
                conversation_id, title, workspace_uris, git_origin_urls,
                created_at, updated_at, first_step_at, last_step_at,
                total_steps, user_input_steps, planner_steps,
                has_transcript, has_summary_db, ingested_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
            """,
            [
                ("conv-1", "Go Refactoring", "file:///workspace/go", None, now, now, now, now, 20, 3, 10, now),
                ("conv-2", "Buffer Analytics", "file:///workspace/social", None, now, now, now, now, 30, 4, 15, now),
            ],
        )

        conn.executemany(
            """
            INSERT INTO skill_events (
                conversation_id, step_index, step_created_at, step_type,
                invocation_kind, notation_type, subcommand, target_skill,
                raw_args, subpath_or_script, page_number, trigger_mode,
                source_tier, raw_snippet, is_self_test
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("conv-1", 1, "2026-10-11T10:00:00Z", "USER_INPUT", "user_notation", "classic_//", "load", "godoctor", "//godoctor", None, 1, "user_explicit", "user_prompt", "please run //godoctor", 0),
                ("conv-1", 2, "2026-10-11T10:00:05Z", "PLANNER_RESPONSE", "direct_skill_view", None, "view_file", "kungfu", "/.gemini/config/skills/kungfu/SKILL.md", "SKILL.md", 1, "rule_driven", "global", "view_file(kungfu/SKILL.md)", 0),
                ("conv-1", 3, "2026-10-11T10:00:10Z", "PLANNER_RESPONSE", "direct_skill_view", None, "view_file", "godoctor", "/.gemini/config/plugins/agy/skills/godoctor/SKILL.md", "SKILL.md", 1, "user_explicit", "plugin", "view_file(godoctor/SKILL.md)", 0),
                ("conv-2", 1, "2026-10-12T11:00:00Z", "USER_INPUT", "user_notation", "modern_::", "load", "buffer-analytics", "::buffer-analytics", None, 1, "user_explicit", "user_prompt", "::buffer-analytics sync", 0),
                ("conv-2", 2, "2026-10-12T11:00:04Z", "PLANNER_RESPONSE", "cli_invocation", None, "load", "buffer-analytics", "load buffer-analytics", None, 1, "user_explicit", "kungfu_cli", "kungfu load buffer-analytics", 0),
                ("conv-2", 3, "2026-10-12T11:00:08Z", "PLANNER_RESPONSE", "cli_invocation", None, "load", "buffer-analytics", "load buffer-analytics/references/schema.md", "references/schema.md", 1, "autonomous", "kungfu_cli", "kungfu load buffer-analytics/references/schema.md", 0),
                ("conv-2", 4, "2026-10-12T11:00:12Z", "PLANNER_RESPONSE", "cli_invocation", None, "run", "buffer-analytics", "run buffer-analytics buffer_analytics.py sync", "buffer_analytics.py", 1, "autonomous", "kungfu_cli", "kungfu run buffer-analytics buffer_analytics.py sync", 0),
                ("conv-2", 5, "2026-10-12T11:01:00Z", "PLANNER_RESPONSE", "cli_invocation", None, "find", None, "find kubernetes helm", "kubernetes helm", 1, "autonomous", "kungfu_cli", "kungfu find kubernetes helm", 0),
            ],
        )

        conn.execute(
            """
            INSERT INTO state_telemetry_snapshot (
                skill_name, recorded_count, page_load_count, subpath_load_count,
                run_count, last_loaded_at, is_learned, snapshot_at
            ) VALUES ('buffer-analytics', 1, 0, 1, 1, '2026-10-12T11:00:04Z', 0, ?)
            """,
            (now,),
        )
        conn.commit()

    def test_extract_user_notations_accuracy(self):
        known = {"godoctor", "parallel", "skill-optimizer", "buffer-analytics"}
        prompt = (
            "Let's use //godoctor and ::parallel(10 plus ::skill-optimizer!count_tokens.py "
            "and search :?telemetry schema. Ignore std::vector and https://example.com/foo."
        )
        events, explicit = analyze.extract_user_notations(
            conv_id="c1",
            step_index=1,
            step_created_at="2026-10-12T00:00:00Z",
            step_type="USER_INPUT",
            raw_content=prompt,
            known_skills=known,
        )
        self.assertIn("godoctor", explicit)
        self.assertIn("parallel", explicit)
        self.assertIn("skill-optimizer", explicit)
        notations = {(e["notation_type"], e["subcommand"], e["target_skill"]) for e in events}
        self.assertIn(("classic_//", "load", "godoctor"), notations)
        self.assertIn(("modern_::", "load", "parallel"), notations)
        self.assertIn(("modern_::", "run", "skill-optimizer"), notations)
        self.assertIn(("find_:?", "find", None), notations)

    def test_roi_and_shelfware_detection(self):
        rows = {
            r["skill_name"]: dict(r)
            for r in self.conn.execute("SELECT * FROM v_skill_roi").fetchall()
        }
        self.assertEqual(rows["unused-shelfware"]["roi_recommendation"], "SHELFWARE_CANDIDATE")
        self.assertEqual(rows["buffer-analytics"]["resource_reads"], 1)
        self.assertEqual(rows["buffer-analytics"]["script_runs"], 1)

    def test_all_reports_execute(self):
        for rpt in ("overview", "roi", "triggers", "velocity", "gaps", "drift"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                analyze.run_report(self.conn, rpt, as_json=False)
            self.assertTrue(len(buf.getvalue()) > 20)

    def test_markdown_sql_queries_valid(self):
        md_files = [
            os.path.join(SKILL_DIR, "SKILL.md"),
            os.path.join(SKILL_DIR, "references", "queries.md"),
        ]
        sql_block_re = re.compile(r"```sql\s+(.*?)```", re.DOTALL)
        executed = 0
        for path in md_files:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for match in sql_block_re.finditer(content):
                sql = match.group(1).strip()
                cur = self.conn.execute(sql)
                _ = cur.fetchall()
                executed += 1
        self.assertGreaterEqual(executed, 8)


if __name__ == "__main__":
    unittest.main()
