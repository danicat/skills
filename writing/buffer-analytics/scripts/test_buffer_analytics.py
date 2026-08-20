#!/usr/bin/env python3
"""
Test Suite for buffer-analytics
Validates:
1. SQLite schema DDL, indexes, and analytical view definitions (v_posts_summary).
2. Data insertion and relationship consistency.
3. Every SQL query used as an example in SKILL.md, references/queries.md, and references/inquiry_playbook.md.
4. Pre-packaged reports in scripts/buffer_analytics.py.
5. Dynamic extraction and execution of all SQL code blocks in markdown documentation.
6. CLI argument parsing and help interface.
"""

import os
import re
import sqlite3
import subprocess
import sys
import unittest

# Locate directory roots
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", ".."))

# Import target module
sys.path.insert(0, SCRIPT_DIR)
import buffer_analytics


class TestBufferAnalyticsSchema(unittest.TestCase):
    """Validates DDL, table structures, and analytical views."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(buffer_analytics.SCHEMA_DDL)

    def tearDown(self):
        self.conn.close()

    def test_tables_exist(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')")
        names = {row["name"] for row in cursor.fetchall()}
        expected_tables = {
            "channels",
            "posts",
            "post_metrics",
            "post_assets",
            "post_tags",
            "sync_history",
            "v_posts_summary",
        }
        for table in expected_tables:
            self.assertIn(table, names, f"Expected table or view '{table}' to exist in schema.")

    def test_view_posts_summary_columns(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(v_posts_summary)")
        columns = {row["name"] for row in cursor.fetchall()}
        expected_columns = {
            "post_id",
            "service",
            "channel_name",
            "status",
            "sent_at",
            "sent_date",
            "year_month",
            "day_of_week",
            "hour_of_day",
            "char_count",
            "word_count",
            "has_link",
            "has_media",
            "thread_count",
            "external_link",
            "text",
            "impressions",
            "reach",
            "reactions",
            "comments",
            "reposts",
            "clicks",
            "engagement_rate",
        }
        for col in expected_columns:
            self.assertIn(col, columns, f"Expected column '{col}' in view 'v_posts_summary'.")


class TestBufferAnalyticsQueries(unittest.TestCase):
    """Populates realistic fixture data and executes all example and report queries."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.row_factory = sqlite3.Row
        cls.conn.executescript(buffer_analytics.SCHEMA_DDL)
        cls._populate_fixture_data(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    @classmethod
    def _populate_fixture_data(cls, conn: sqlite3.Connection):
        """Populates rich synthetic fixture rows for LinkedIn, Twitter, and Bluesky."""
        # Channels
        channels = [
            ("ch_li_1", "org_1", "Jane Doe", "linkedin", "Jane Doe (LinkedIn)", "UTC", 0, "{}", "2026-08-20T00:00:00Z"),
            ("ch_tw_1", "org_1", "janedev", "twitter", "@janedev (X)", "UTC", 0, "{}", "2026-08-20T00:00:00Z"),
            ("ch_bs_1", "org_1", "jane.bsky.social", "bluesky", "Jane on Bluesky", "UTC", 0, "{}", "2026-08-20T00:00:00Z"),
        ]
        conn.executemany(
            "INSERT INTO channels (id, organization_id, name, service, display_name, timezone, is_disconnected, raw_json, synced_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            channels,
        )

        # Posts: various days of week, hours, lengths, link/media presence
        posts = [
            ("p_li_1", "org_1", "ch_li_1", "linkedin", "sent", "Announcing our new distributed architecture overhaul! Details in link: https://example.com/arch #topic1", "https://linkedin.com/feed/update/1", "2026-08-10T14:00:00Z", "2026-08-10T14:00:00Z", 102, 13, 1, 1, 1),
            ("p_li_2", "org_1", "ch_li_1", "linkedin", "sent", "Why clean code standards matter more than AI-generated boilerplate in high-scale systems. #topic2", "https://linkedin.com/feed/update/2", "2026-08-11T13:00:00Z", "2026-08-11T13:00:00Z", 95, 13, 0, 0, 1),
            ("p_li_3", "org_1", "ch_li_1", "linkedin", "sent", "Short tip on Go channels and concurrency patterns.", "https://linkedin.com/feed/update/3", "2026-08-12T14:00:00Z", "2026-08-12T14:00:00Z", 52, 8, 0, 0, 1),
            ("p_li_4", "org_1", "ch_li_1", "linkedin", "sent", "A deep dive into SQLite performance tuning and PRAGMA settings. Long form post with detailed benchmarks.", "https://linkedin.com/feed/update/4", "2026-08-17T14:00:00Z", "2026-08-17T14:00:00Z", 850, 120, 1, 1, 1),
            ("p_li_5", "org_1", "ch_li_1", "linkedin", "sent", "Quick note on productivity tools for engineers.", "https://linkedin.com/feed/update/5", "2026-08-18T15:00:00Z", "2026-08-18T15:00:00Z", 48, 7, 0, 0, 1),
            ("p_tw_1", "org_1", "ch_tw_1", "twitter", "sent", "Just open sourced our new Agent Skills catalog! Check it out: https://example.com/catalog #topic1", "https://x.com/janedev/status/1", "2026-08-10T15:00:00Z", "2026-08-10T15:00:00Z", 98, 14, 1, 1, 1),
            ("p_tw_2", "org_1", "ch_tw_1", "twitter", "sent", "Thread: 5 lessons learned from building LLM developer workflows (1/5)", "https://x.com/janedev/status/2", "2026-08-13T16:00:00Z", "2026-08-13T16:00:00Z", 70, 10, 0, 0, 5),
            ("p_bs_1", "org_1", "ch_bs_1", "bluesky", "sent", "Excited to share our technical specification RFC for local agent VCS.", "https://bsky.app/profile/jane/post/1", "2026-08-14T11:00:00Z", "2026-08-14T11:00:00Z", 68, 10, 0, 0, 1),
            ("p_draft_1", "org_1", "ch_li_1", "linkedin", "draft", "Draft post about future roadmap.", None, None, "2026-08-25T14:00:00Z", 34, 5, 0, 0, 1),
        ]
        for p in posts:
            conn.execute(
                """INSERT INTO posts (
                    id, organization_id, channel_id, channel_service, status, text,
                    external_link, sent_at, due_at, char_count, word_count, has_link,
                    has_media, thread_count, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                p,
            )

        # Metrics
        metrics = [
            ("p_li_1", "linkedin", "impressions", 12500),
            ("p_li_1", "linkedin", "reach", 11000),
            ("p_li_1", "linkedin", "reactions", 450),
            ("p_li_1", "linkedin", "comments", 65),
            ("p_li_1", "linkedin", "reposts", 30),
            ("p_li_1", "linkedin", "clicks", 320),
            ("p_li_1", "linkedin", "engagementRate", 4.36),
            ("p_li_2", "linkedin", "impressions", 8200),
            ("p_li_2", "linkedin", "reach", 7500),
            ("p_li_2", "linkedin", "reactions", 310),
            ("p_li_2", "linkedin", "comments", 45),
            ("p_li_2", "linkedin", "reposts", 15),
            ("p_li_2", "linkedin", "clicks", 50),
            ("p_li_2", "linkedin", "engagementRate", 4.51),
            ("p_li_3", "linkedin", "impressions", 3400),
            ("p_li_3", "linkedin", "reach", 3100),
            ("p_li_3", "linkedin", "reactions", 120),
            ("p_li_3", "linkedin", "comments", 14),
            ("p_li_3", "linkedin", "reposts", 5),
            ("p_li_3", "linkedin", "clicks", 0),
            ("p_li_3", "linkedin", "engagementRate", 4.09),
            ("p_li_4", "linkedin", "impressions", 15400),
            ("p_li_4", "linkedin", "reach", 14000),
            ("p_li_4", "linkedin", "reactions", 680),
            ("p_li_4", "linkedin", "comments", 92),
            ("p_li_4", "linkedin", "reposts", 54),
            ("p_li_4", "linkedin", "clicks", 410),
            ("p_li_4", "linkedin", "engagementRate", 5.36),
            ("p_li_5", "linkedin", "impressions", 2900),
            ("p_li_5", "linkedin", "reach", 2600),
            ("p_li_5", "linkedin", "reactions", 95),
            ("p_li_5", "linkedin", "comments", 8),
            ("p_li_5", "linkedin", "reposts", 2),
            ("p_li_5", "linkedin", "clicks", 0),
            ("p_li_5", "linkedin", "engagementRate", 3.62),
            ("p_tw_1", "twitter", "impressions", 6500),
            ("p_tw_1", "twitter", "reach", 5800),
            ("p_tw_1", "twitter", "reactions", 210),
            ("p_tw_1", "twitter", "comments", 25),
            ("p_tw_1", "twitter", "reposts", 45),
            ("p_tw_1", "twitter", "clicks", 180),
            ("p_tw_1", "twitter", "engagementRate", 4.31),
            ("p_tw_2", "twitter", "impressions", 4200),
            ("p_tw_2", "twitter", "reach", 3900),
            ("p_tw_2", "twitter", "reactions", 140),
            ("p_tw_2", "twitter", "comments", 18),
            ("p_tw_2", "twitter", "reposts", 22),
            ("p_tw_2", "twitter", "clicks", 35),
            ("p_tw_2", "twitter", "engagementRate", 4.29),
            ("p_bs_1", "bluesky", "impressions", 1800),
            ("p_bs_1", "bluesky", "reach", 1600),
            ("p_bs_1", "bluesky", "reactions", 85),
            ("p_bs_1", "bluesky", "comments", 12),
            ("p_bs_1", "bluesky", "reposts", 18),
            ("p_bs_1", "bluesky", "clicks", 10),
            ("p_bs_1", "bluesky", "engagementRate", 6.39),
        ]
        for m in metrics:
            conn.execute(
                "INSERT INTO post_metrics (post_id, channel_service, metric_type, value, synced_at) VALUES (?, ?, ?, ?, '2026-08-20T00:00:00Z')",
                m,
            )

        conn.commit()

    def test_quickstart_adhoc_query(self):
        sql = "SELECT service, AVG(impressions), AVG(reactions) FROM v_posts_summary WHERE status = 'sent' GROUP BY service"
        rows = self.conn.execute(sql).fetchall()
        self.assertGreater(len(rows), 0)
        services = {r[0] for r in rows}
        self.assertIn("linkedin", services)

    def test_cookbook_queries_skill_md(self):
        queries = [
            # Best Day of Week
            """
            SELECT
                service,
                day_of_week,
                COUNT(*) AS posts,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions,
                ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
            FROM v_posts_summary
            WHERE status = 'sent' AND day_of_week IS NOT NULL
            GROUP BY service, day_of_week
            ORDER BY service, avg_impressions DESC;
            """,
            # Best Posting Hours
            """
            SELECT
                service,
                hour_of_day || ':00 UTC' AS hour,
                COUNT(*) AS posts,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions
            FROM v_posts_summary
            WHERE status = 'sent' AND impressions > 0
            GROUP BY service, hour_of_day
            HAVING COUNT(*) >= 1
            ORDER BY avg_impressions DESC;
            """,
            # Impact of Links in Body
            """
            SELECT
                service,
                CASE WHEN has_link = 1 THEN 'Link in Body' ELSE 'No Link / First Comment' END AS placement,
                COUNT(*) AS posts,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions
            FROM v_posts_summary
            WHERE status = 'sent' AND service = 'linkedin'
            GROUP BY placement;
            """,
        ]
        for idx, sql in enumerate(queries, 1):
            with self.subTest(query_index=idx):
                cursor = self.conn.execute(sql)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Query #{idx} returned empty result.")

    def test_recipes_in_queries_md(self):
        queries = [
            # 1. Top Performing Posts by Reach & Impressions
            """
            SELECT
                service,
                sent_date,
                CAST(impressions AS INTEGER) AS impressions,
                CAST(reactions AS INTEGER) AS reactions,
                CAST(comments AS INTEGER) AS comments,
                engagement_rate,
                SUBSTR(text, 1, 90) AS opening_hook
            FROM v_posts_summary
            WHERE status = 'sent' AND impressions > 0
            ORDER BY impressions DESC
            LIMIT 15;
            """,
            # 2. Best Days of the Week to Post
            """
            SELECT
                service,
                day_of_week,
                COUNT(*) AS total_posts,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions,
                ROUND(AVG(comments), 1) AS avg_comments,
                ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
            FROM v_posts_summary
            WHERE status = 'sent' AND day_of_week IS NOT NULL
            GROUP BY service, day_of_week
            ORDER BY service, avg_impressions DESC;
            """,
            # 3. Best Hours of the Day (UTC)
            """
            SELECT
                service,
                hour_of_day || ':00 UTC' AS posting_hour,
                COUNT(*) AS total_posts,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions,
                ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
            FROM v_posts_summary
            WHERE status = 'sent' AND impressions > 0
            GROUP BY service, hour_of_day
            HAVING COUNT(*) >= 1
            ORDER BY avg_impressions DESC;
            """,
            # 4. Impact of External Links
            """
            SELECT
                service,
                CASE WHEN has_link = 1 THEN 'Link in Body' ELSE 'No Link / Link in Comment' END AS link_placement,
                COUNT(*) AS post_count,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions,
                ROUND(AVG(comments), 1) AS avg_comments,
                ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
            FROM v_posts_summary
            WHERE status = 'sent' AND impressions > 0
            GROUP BY service, has_link;
            """,
            # 5. Post Length vs Performance
            """
            SELECT
                service,
                CASE
                    WHEN char_count < 280 THEN 'Short (<280 chars)'
                    WHEN char_count BETWEEN 280 AND 800 THEN 'Medium (280-800 chars)'
                    ELSE 'Long-form (>800 chars)'
                END AS post_length_cohort,
                COUNT(*) AS post_count,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions,
                ROUND(AVG(comments), 1) AS avg_comments,
                ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
            FROM v_posts_summary
            WHERE status = 'sent' AND impressions > 0
            GROUP BY service, post_length_cohort
            ORDER BY service, avg_impressions DESC;
            """,
            # 6. Topic Cohort Performance
            """
            SELECT
                CASE
                    WHEN LOWER(text) LIKE '%#topic1%' OR LOWER(text) LIKE '%keyword1%' THEN 'Topic 1'
                    WHEN LOWER(text) LIKE '%#topic2%' OR LOWER(text) LIKE '%keyword2%' THEN 'Topic 2'
                    ELSE 'General / Other'
                END AS topic_cohort,
                COUNT(*) AS total_posts,
                ROUND(AVG(impressions), 0) AS avg_impressions,
                ROUND(AVG(reactions), 1) AS avg_reactions,
                ROUND(AVG(comments), 1) AS avg_comments,
                ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
            FROM v_posts_summary
            WHERE status = 'sent'
            GROUP BY topic_cohort
            ORDER BY avg_impressions DESC;
            """,
            # 7. Monthly Performance & Growth Trajectory
            """
            SELECT
                year_month,
                service,
                COUNT(*) AS total_posts,
                ROUND(SUM(impressions), 0) AS total_impressions,
                ROUND(SUM(reactions), 0) AS total_reactions,
                ROUND(SUM(comments), 0) AS total_comments,
                ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate
            FROM v_posts_summary
            WHERE status = 'sent'
            GROUP BY year_month, service
            ORDER BY year_month DESC, total_impressions DESC;
            """,
        ]
        for idx, sql in enumerate(queries, 1):
            with self.subTest(recipe_index=idx):
                cursor = self.conn.execute(sql)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Recipe #{idx} returned empty result.")

    def test_prepackaged_cli_reports(self):
        for name, sql in buffer_analytics.REPORTS.items():
            with self.subTest(report_name=name):
                cursor = self.conn.execute(sql)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Report '{name}' returned empty result.")

    def test_markdown_query_extraction(self):
        """Extracts and executes every ```sql block found across all markdown docs in skill."""
        md_files = [
            os.path.join(SKILL_DIR, "SKILL.md"),
            os.path.join(SKILL_DIR, "references", "queries.md"),
            os.path.join(SKILL_DIR, "references", "inquiry_playbook.md"),
        ]
        total_executed = 0
        for md_path in md_files:
            if not os.path.exists(md_path):
                continue
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            sql_blocks = re.findall(r"```sql\s*\n([\s\S]*?)\n```", content)
            for block in sql_blocks:
                query = block.strip()
                if not query:
                    continue
                try:
                    cursor = self.conn.execute(query)
                    rows = cursor.fetchall()
                    self.assertIsNotNone(rows)
                    total_executed += 1
                except Exception as e:
                    self.fail(f"Failed to execute SQL block extracted from {os.path.basename(md_path)}:\n{query}\nError: {e}")
        self.assertGreaterEqual(total_executed, 10, "Expected at least 10 markdown SQL blocks to be tested.")


class TestBufferAnalyticsCLI(unittest.TestCase):
    """Tests CLI entry points and argument parsing."""

    def test_cli_help(self):
        script_path = os.path.join(SCRIPT_DIR, "buffer_analytics.py")
        cmd = [sys.executable, script_path, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Buffer Analytics CLI", result.stdout)
        self.assertIn("sync", result.stdout)
        self.assertIn("report", result.stdout)
        self.assertIn("query", result.stdout)
        self.assertIn("schema", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
