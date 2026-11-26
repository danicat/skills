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
Test Suite for google-analytics
Validates:
1. SQLite schema DDL, indexes, and all 7 analytical views (v_daily_summary, v_page_performance,
   v_channel_performance, v_geo_breakdown, v_events_summary, v_outbound_links, v_milestone_impact).
2. Data insertion, weighted bounce/dwell rollups, and cohort computations.
3. Every SQL query used as an example in SKILL.md and references/queries.md.
4. Pre-packaged reports in scripts/google_analytics.py (full-history default and optional --days).
5. Multi-page RunReportRequest offset pagination.
6. Dynamic extraction and execution of all SQL code blocks in markdown documentation.
7. CLI argument parsing, help interface, and validation.
"""

import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

# Locate directory roots
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", ".."))

# Import target module
sys.path.insert(0, SCRIPT_DIR)
import google_analytics


class TestGoogleAnalyticsSchema(unittest.TestCase):
    """Validates DDL, table structures, and analytical views."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(google_analytics.SCHEMA_DDL)

    def tearDown(self):
        self.conn.close()

    def test_tables_and_views_exist(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')")
        names = {row["name"] for row in cursor.fetchall()}
        expected_items = {
            "properties",
            "daily_pages",
            "daily_traffic",
            "daily_events",
            "outbound_clicks",
            "site_milestones",
            "sync_history",
            "v_daily_summary",
            "v_page_performance",
            "v_channel_performance",
            "v_geo_breakdown",
            "v_events_summary",
            "v_outbound_links",
            "v_milestone_impact",
        }
        for item in expected_items:
            self.assertIn(item, names, f"Expected table or view '{item}' to exist in schema.")

    def test_view_page_performance_columns(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(v_page_performance)")
        columns = {row["name"] for row in cursor.fetchall()}
        expected_columns = {
            "page_path",
            "page_title",
            "total_views",
            "total_users",
            "total_sessions",
            "avg_dwell_sec",
            "total_dwell_min",
            "avg_bounce_pct",
        }
        for col in expected_columns:
            self.assertIn(col, columns, f"Expected column '{col}' in view 'v_page_performance'.")

    def test_view_channel_performance_columns(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(v_channel_performance)")
        columns = {row["name"] for row in cursor.fetchall()}
        expected_columns = {
            "channel_group",
            "source_medium",
            "total_sessions",
            "total_users",
            "total_new_users",
            "total_engaged_sessions",
            "engagement_rate_pct",
            "avg_dwell_sec",
            "engaged_dwell_sec",
            "total_dwell_min",
            "avg_bounce_pct",
        }
        for col in expected_columns:
            self.assertIn(col, columns, f"Expected column '{col}' in view 'v_channel_performance'.")


class TestGoogleAnalyticsQueries(unittest.TestCase):
    """Populates realistic fixture data and executes all example and report queries."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.row_factory = sqlite3.Row
        cls.conn.executescript(google_analytics.SCHEMA_DDL)
        cls._populate_fixture_data(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    @classmethod
    def _populate_fixture_data(cls, conn: sqlite3.Connection):
        """Populates rich synthetic fixture rows for GA4 analytics."""
        # 1. Properties
        conn.execute(
            "INSERT INTO properties (property_id, name, display_name, industry_category, time_zone, currency_code, service_level, raw_json, last_synced_at) "
            "VALUES ('prop_123', 'properties/123456789', 'Developer Documentation & Blog', 'TECHNOLOGY', 'UTC', 'USD', 'STANDARD', '{}', '2026-08-20T00:00:00Z')"
        )

        # 2. Daily Pages (Pre and Post Milestone dates)
        pages_data = [
            # prop, date, path, title, country, device, source_medium, views, users, sessions, duration_sec, bounce_rate
            ('prop_123', '2026-08-01', '/', 'Home Page', 'United States', 'desktop', 'google / organic', 500, 420, 460, 23000.0, 0.25),
            ('prop_123', '2026-08-01', '/docs/getting-started', 'Getting Started Guide', 'United States', 'desktop', 'google / organic', 350, 280, 310, 37200.0, 0.18),
            ('prop_123', '2026-08-01', '/blog/sqlite-analytics-guide', 'High Performance SQLite', 'United Kingdom', 'desktop', 'twitter / social', 220, 190, 205, 26600.0, 0.20),
            ('prop_123', '2026-08-02', '/tutorials/building-agent-skills', 'Building Agent Skills', 'Germany', 'desktop', 'github.com / referral', 180, 150, 165, 19800.0, 0.15),
            ('prop_123', '2026-08-15', '/', 'Home Page', 'United States', 'mobile', 'direct / none', 620, 510, 580, 29000.0, 0.28),
            ('prop_123', '2026-08-15', '/docs/getting-started', 'Getting Started Guide', 'Canada', 'desktop', 'google / organic', 410, 340, 380, 45600.0, 0.16),
            ('prop_123', '2026-08-15', '/blog/sqlite-analytics-guide', 'High Performance SQLite', 'United States', 'desktop', 'google / organic', 480, 400, 430, 57600.0, 0.14),
            ('prop_123', '2026-08-16', '/tutorials/building-agent-skills', 'Building Agent Skills', 'Japan', 'desktop', 'direct / none', 290, 240, 260, 31200.0, 0.19),
        ]
        for p in pages_data:
            conn.execute(
                """INSERT INTO daily_pages (
                    property_id, date, page_path, page_title, country, device_category,
                    source_medium, screen_page_views, active_users, sessions,
                    user_engagement_duration, bounce_rate, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                p,
            )

        # 3. Daily Traffic
        traffic_data = [
            ('prop_123', '2026-08-01', 'google / organic', 'Organic Search', 'United States', 'desktop', 520, 450, 280, 420, 45000.0, 0.20),
            ('prop_123', '2026-08-01', 'direct / none', 'Direct', 'United States', 'desktop', 210, 180, 40, 170, 18000.0, 0.25),
            ('prop_123', '2026-08-01', 'github.com / referral', 'Referral', 'United Kingdom', 'desktop', 150, 130, 90, 125, 16000.0, 0.16),
            ('prop_123', '2026-08-01', 'chatgpt.com / referral', 'Referral', 'United States', 'desktop', 80, 72, 65, 55, 6600.0, 0.31),
            ('prop_123', '2026-08-15', 'google / organic', 'Organic Search', 'United States', 'desktop', 680, 590, 380, 560, 62000.0, 0.18),
            ('prop_123', '2026-08-15', 'direct / none', 'Direct', 'United States', 'mobile', 310, 270, 60, 240, 24000.0, 0.26),
            ('prop_123', '2026-08-15', 'direct / none', 'Direct', 'Ireland', 'desktop', 120, 118, 118, 4, 80.0, 0.96),
            ('prop_123', '2026-08-15', 'twitter.com / referral', 'Organic Social', 'Canada', 'desktop', 190, 160, 110, 150, 19000.0, 0.21),
        ]
        for t in traffic_data:
            conn.execute(
                """INSERT INTO daily_traffic (
                    property_id, date, session_source_medium, session_default_channel_group,
                    country, device_category, sessions, active_users, new_users,
                    engaged_sessions, user_engagement_duration, bounce_rate, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                t,
            )

        # 4. Daily Events
        events_data = [
            ('prop_123', '2026-08-01', 'page_view', '/', 'United States', 'desktop', 500, 420),
            ('prop_123', '2026-08-01', 'scroll', '/docs/getting-started', 'United States', 'desktop', 310, 250),
            ('prop_123', '2026-08-01', 'code_copy', '/docs/getting-started', 'United States', 'desktop', 95, 80),
            ('prop_123', '2026-08-01', 'click', '/blog/sqlite-analytics-guide', 'United Kingdom', 'desktop', 85, 70),
            ('prop_123', '2026-08-15', 'page_view', '/blog/sqlite-analytics-guide', 'United States', 'desktop', 480, 400),
            ('prop_123', '2026-08-15', 'scroll', '/blog/sqlite-analytics-guide', 'United States', 'desktop', 410, 350),
            ('prop_123', '2026-08-15', 'code_copy', '/blog/sqlite-analytics-guide', 'United States', 'desktop', 120, 105),
            ('prop_123', '2026-08-15', 'click', '/blog/sqlite-analytics-guide', 'United States', 'desktop', 140, 115),
        ]
        for e in events_data:
            conn.execute(
                """INSERT INTO daily_events (
                    property_id, date, event_name, page_path, country, device_category,
                    event_count, total_users, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                e,
            )

        # 5. Outbound Clicks
        outbound_data = [
            ('prop_123', '2026-08-01', 'https://github.com/example/agent-skills', '/docs/getting-started', 'United States', 45, 40),
            ('prop_123', '2026-08-01', 'https://sqlite.org/wal.html', '/blog/sqlite-analytics-guide', 'United Kingdom', 28, 25),
            ('prop_123', '2026-08-15', 'https://github.com/example/agent-skills', '/tutorials/building-agent-skills', 'United States', 62, 55),
            ('prop_123', '2026-08-15', 'https://news.ycombinator.com', '/blog/sqlite-analytics-guide', 'United States', 35, 30),
        ]
        for o in outbound_data:
            conn.execute(
                """INSERT INTO outbound_clicks (
                    property_id, date, link_url, page_path, country, event_count, total_users, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                o,
            )

        # 6. Site Milestones
        conn.execute(
            """INSERT INTO site_milestones (
                commit_hash, event_date, title, description, category, scope, author, created_at
            ) VALUES ('c1a2b3d', '2026-08-10', 'Major Architecture & Content Overhaul', 'Complete refresh of site documentation', 'ARCHITECTURE', 'SITE_WIDE', 'Engineering Team', '2026-08-10T00:00:00Z')"""
        )

        conn.commit()

    def test_quickstart_adhoc_query(self):
        sql = "SELECT page_path, total_views, total_users, avg_dwell_sec, avg_bounce_pct FROM v_page_performance LIMIT 10"
        rows = self.conn.execute(sql).fetchall()
        self.assertGreater(len(rows), 0)

    def test_cookbook_queries_skill_md(self):
        queries = [
            # Recipe 1: Top Landing Pages by Active Dwell Time
            """
            SELECT
                page_path,
                page_title,
                total_views,
                total_users,
                avg_dwell_sec || 's' AS avg_dwell,
                total_dwell_min || 'm' AS total_dwell,
                avg_bounce_pct || '%' AS bounce_pct
            FROM v_page_performance
            ORDER BY total_dwell_min DESC
            LIMIT 15;
            """,
            # Recipe 2: Category / Subdirectory Rollup
            """
            SELECT
                CASE
                    WHEN page_path LIKE '/docs/%' THEN 'Docs'
                    WHEN page_path LIKE '/blog/%' THEN 'Blog'
                    WHEN page_path = '/' THEN 'Homepage'
                    ELSE 'Other'
                END AS category,
                COUNT(DISTINCT page_path) AS page_count,
                SUM(total_views) AS total_views,
                SUM(total_users) AS total_users,
                ROUND(SUM(total_dwell_min), 1) AS total_dwell_min
            FROM v_page_performance
            GROUP BY category
            ORDER BY total_views DESC;
            """,
        ]
        for idx, sql in enumerate(queries, 1):
            with self.subTest(query_index=idx):
                cursor = self.conn.execute(sql)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Skill cookbook query #{idx} returned empty result.")

    def test_recipes_in_queries_md(self):
        queries = [
            # 1. Top Articles by Reading Depth & Active Dwell Time
            """
            SELECT
                page_path,
                page_title,
                total_views,
                total_users,
                avg_dwell_sec || 's' AS avg_dwell,
                total_dwell_min || 'm' AS total_dwell,
                avg_bounce_pct || '%' AS bounce_pct
            FROM v_page_performance
            ORDER BY total_dwell_min DESC
            LIMIT 15;
            """,
            # 2. Path & Subdirectory Performance Comparison
            """
            SELECT
                CASE
                    WHEN page_path LIKE '/docs/%' THEN 'Documentation'
                    WHEN page_path LIKE '/blog/%' OR page_path LIKE '/posts/%' THEN 'Articles / Blog'
                    WHEN page_path LIKE '/tutorials/%' THEN 'Tutorials'
                    WHEN page_path = '/' THEN 'Homepage'
                    ELSE 'Other'
                END AS content_category,
                COUNT(DISTINCT page_path) AS page_count,
                SUM(total_views) AS total_page_views,
                SUM(total_users) AS unique_readers,
                ROUND(SUM(total_dwell_min), 1) AS total_dwell_minutes,
                ROUND(SUM(total_dwell_min) * 60.0 / MAX(SUM(total_users), 1), 1) AS avg_dwell_per_user_sec,
                ROUND(SUM(avg_bounce_pct * total_sessions) / MAX(SUM(total_sessions), 1), 1) AS avg_bounce_pct
            FROM v_page_performance
            GROUP BY content_category
            ORDER BY total_page_views DESC;
            """,
            # 3. Geographic Audience Distribution
            """
            SELECT
                country,
                SUM(sessions) AS total_sessions,
                SUM(active_users) AS total_users,
                SUM(screen_page_views) AS total_page_views,
                ROUND(SUM(user_engagement_duration) / MAX(SUM(active_users), 1), 1) AS avg_dwell_sec,
                ROUND(SUM(bounce_rate * sessions) * 100.0 / MAX(SUM(sessions), 1), 1) AS avg_bounce_pct
            FROM daily_pages
            WHERE country IS NOT NULL AND country != '' AND country != '(not set)'
            GROUP BY country
            ORDER BY total_sessions DESC
            LIMIT 10;
            """,
            # 4. Top Traffic Channels & Conversion Engagement Rate
            """
            SELECT
                channel_group,
                source_medium,
                SUM(total_sessions) AS sessions,
                SUM(total_users) AS users,
                SUM(total_new_users) AS new_users,
                ROUND(SUM(total_engaged_sessions) * 100.0 / MAX(SUM(total_sessions), 1), 1) || '%' AS avg_engagement_rate,
                ROUND(SUM(total_dwell_min) * 60.0 / MAX(SUM(total_sessions), 1), 1) || 's' AS avg_dwell,
                CASE WHEN SUM(total_engaged_sessions) > 0 THEN ROUND(SUM(total_dwell_min) * 60.0 / SUM(total_engaged_sessions), 1) ELSE 0.0 END || 's' AS engaged_dwell,
                ROUND(SUM(total_dwell_min), 1) AS total_dwell_min
            FROM v_channel_performance
            GROUP BY channel_group, source_medium
            HAVING SUM(total_sessions) >= 50
            ORDER BY sessions DESC;
            """,
            # 5. Day-of-the-Week Traffic Trends
            """
            SELECT
                CASE CAST(strftime('%w', date) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END AS day_of_week,
                COUNT(DISTINCT date) AS day_count,
                ROUND(AVG(total_sessions), 0) AS avg_sessions,
                ROUND(AVG(total_active_users), 0) AS avg_users,
                ROUND(AVG(total_page_views), 0) AS avg_page_views,
                ROUND(AVG(total_engagement_min), 1) AS avg_dwell_min
            FROM v_daily_summary
            GROUP BY strftime('%w', date)
            ORDER BY avg_sessions DESC;
            """,
            # 6. Month-over-Month Growth Trajectory
            """
            SELECT
                strftime('%Y-%m', date) AS month,
                SUM(screen_page_views) AS views,
                SUM(sessions) AS sessions,
                SUM(active_users) AS users,
                ROUND(SUM(user_engagement_duration) / 60.0, 1) AS total_dwell_min
            FROM daily_pages
            GROUP BY month
            ORDER BY month DESC;
            """,
            # 7. Outbound Exit Clicks
            """
            SELECT
                link_url,
                total_clicks,
                total_users,
                referring_pages_count
            FROM v_outbound_links
            ORDER BY total_clicks DESC
            LIMIT 15;
            """,
        ]
        for idx, sql in enumerate(queries, 1):
            with self.subTest(recipe_index=idx):
                cursor = self.conn.execute(sql)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Recipe #{idx} returned empty result.")

    def test_prepackaged_cli_reports(self):
        for name in google_analytics.VALID_REPORTS:
            with self.subTest(report_name=name):
                _, sql, params = google_analytics.build_report_query(name)
                cursor = self.conn.execute(sql, params)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Report '{name}' returned empty result.")

    def test_weighted_bounce_and_milestone_dwell(self):
        """Verifies session-weighted bounce rate and user-weighted milestone dwell time."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(google_analytics.SCHEMA_DDL)
        conn.execute(
            "INSERT INTO site_milestones (commit_hash, event_date, title) VALUES ('m1', '2026-08-10', 'Release')"
        )
        # 1000 sessions at 10% bounce + 10 sessions at 90% bounce -> weighted bounce = 109 / 1010 = 10.8%
        # 100 users with 5000s + 10 users with 500s -> weighted avg engagement = 5500 / 110 = 50.0s
        conn.executemany(
            """INSERT INTO daily_pages (
                property_id, date, page_path, page_title, country, device_category, source_medium,
                screen_page_views, active_users, sessions, user_engagement_duration, bounce_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("p1", "2026-08-01", "/", "Home", "United States", "desktop", "google / organic", 1100, 100, 1000, 5000.0, 0.10),
                ("p1", "2026-08-01", "/", "Home", "Canada", "mobile", "direct / none", 12, 10, 10, 500.0, 0.90),
            ],
        )
        daily = conn.execute("SELECT avg_bounce_pct FROM v_daily_summary WHERE date = '2026-08-01'").fetchone()
        page = conn.execute("SELECT avg_bounce_pct FROM v_page_performance WHERE page_path = '/'").fetchone()
        milestone = conn.execute("SELECT avg_engagement_sec, avg_bounce_pct FROM v_milestone_impact").fetchone()
        self.assertEqual(daily["avg_bounce_pct"], 10.8)
        self.assertEqual(page["avg_bounce_pct"], 10.8)
        self.assertEqual(milestone["avg_engagement_sec"], 50.0)
        self.assertEqual(milestone["avg_bounce_pct"], 10.8)
        conn.close()

    def test_report_overview_full_history_and_optional_days(self):
        """Ensures report overview defaults to all tracked dates and filters only when --days is set."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(google_analytics.SCHEMA_DDL)
        conn.executemany(
            """INSERT INTO daily_pages (
                property_id, date, page_path, page_title, country, device_category, source_medium,
                screen_page_views, active_users, sessions, user_engagement_duration, bounce_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("p1", "2026-06-01", "/", "Home", "US", "desktop", "google / organic", 100, 80, 90, 900.0, 0.20),
                ("p1", "2026-08-01", "/", "Home", "US", "desktop", "google / organic", 150, 120, 130, 1200.0, 0.20),
                ("p1", "2026-08-15", "/", "Home", "US", "desktop", "google / organic", 200, 160, 180, 1800.0, 0.15),
                ("p1", "2026-08-16", "/", "Home", "US", "desktop", "google / organic", 250, 200, 220, 2400.0, 0.10),
            ],
        )

        # Default (days=None) covers the entire history including 2026-06-01
        title_all, sql_all, params_all = google_analytics.build_report_query("overview", days=None)
        row_all = conn.execute(sql_all, params_all).fetchone()
        self.assertIn("All Tracked Dates", title_all)
        self.assertEqual(row_all["first_date"], "2026-06-01")
        self.assertEqual(row_all["last_date"], "2026-08-16")
        self.assertEqual(row_all["active_days"], 4)

        # Explicit 30-day window anchored on latest ingested date (2026-08-16 -> >= 2026-07-18)
        title_30, sql_30, params_30 = google_analytics.build_report_query("overview", days=30)
        row_30 = conn.execute(sql_30, params_30).fetchone()
        self.assertIn("Last 30 Days", title_30)
        self.assertEqual(row_30["first_date"], "2026-08-01")
        self.assertEqual(row_30["active_days"], 3)

        # Explicit 7-day window anchored on latest ingested date (2026-08-16 -> >= 2026-08-10)
        _, sql_7, params_7 = google_analytics.build_report_query("overview", days=7)
        row_7 = conn.execute(sql_7, params_7).fetchone()
        self.assertEqual(row_7["first_date"], "2026-08-15")
        self.assertEqual(row_7["active_days"], 2)
        conn.close()

    def test_ingest_daily_pages_multipage_pagination(self):
        """Verifies RunReportRequest offset pagination fetches every batch across multiple pages."""
        offsets_seen = []

        def make_row(date_val, path_val):
            return SimpleNamespace(
                dimension_values=[
                    SimpleNamespace(value=date_val),
                    SimpleNamespace(value=path_val),
                    SimpleNamespace(value="Title"),
                    SimpleNamespace(value="United States"),
                    SimpleNamespace(value="desktop"),
                    SimpleNamespace(value="google / organic"),
                ],
                metric_values=[
                    SimpleNamespace(value="10"),
                    SimpleNamespace(value="8"),
                    SimpleNamespace(value="9"),
                    SimpleNamespace(value="120.0"),
                    SimpleNamespace(value="0.25"),
                ],
            )

        pages = {
            0: SimpleNamespace(
                rows=[make_row("20260801", "/p1"), make_row("20260801", "/p2")],
                row_count=3,
            ),
            2: SimpleNamespace(
                rows=[make_row("20260801", "/p3")],
                row_count=3,
            ),
        }

        class FakeClient:
            def run_report(self, req):
                offsets_seen.append(req.offset)
                return pages[req.offset]

        conn = sqlite3.connect(":memory:")
        conn.executescript(google_analytics.SCHEMA_DDL)
        with patch.multiple(
            google_analytics,
            RunReportRequest=SimpleNamespace,
            DateRange=SimpleNamespace,
            Dimension=SimpleNamespace,
            Metric=SimpleNamespace,
        ):
            total = google_analytics.ingest_daily_pages(
                FakeClient(), conn, "prop_123", "2026-08-01", "2026-08-01", page_limit=2
            )

        self.assertEqual(offsets_seen, [0, 2])
        self.assertEqual(total, 3)
        stored = conn.execute("SELECT COUNT(*) FROM daily_pages").fetchone()[0]
        self.assertEqual(stored, 3)
        conn.close()

    def test_markdown_query_extraction(self):
        """Extracts and executes every ```sql block found across all markdown docs in skill."""
        md_files = [
            os.path.join(SKILL_DIR, "SKILL.md"),
            os.path.join(SKILL_DIR, "references", "queries.md"),
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
        self.assertGreaterEqual(total_executed, 13, "Expected at least 13 markdown SQL blocks to be tested.")


class TestGoogleAnalyticsCLI(unittest.TestCase):
    """Tests CLI entry points and argument parsing."""

    def test_cli_help(self):
        script_path = os.path.join(SCRIPT_DIR, "google_analytics.py")
        cmd = [sys.executable, script_path, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Google Analytics 4", result.stdout)
        self.assertIn("sync", result.stdout)
        self.assertIn("report", result.stdout)
        self.assertIn("query", result.stdout)
        self.assertIn("annotate", result.stdout)

    def test_cli_report_invalid_days_fails_fast(self):
        script_path = os.path.join(SCRIPT_DIR, "google_analytics.py")
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            cmd = [sys.executable, script_path, "report", "overview", "--days", "0", "--db", db_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--days", result.stderr)


class _StubCredentials:
    """Minimal Credentials stand-in matching google-auth naive UTC expiry semantics."""

    def __init__(
        self,
        token=None,
        refresh_token=None,
        token_uri=None,
        client_id=None,
        client_secret=None,
        scopes=None,
        expiry=None,
    ):
        self.token = token
        self.refresh_token = refresh_token
        self.token_uri = token_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.expiry = expiry

    @property
    def expired(self):
        if not self.expiry:
            return False
        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        return now_utc >= (self.expiry - datetime.timedelta(minutes=5))

    def refresh(self, request):
        raise NotImplementedError("Subclasses or mocks must implement refresh()")


class TestGoogleAnalyticsAuth(unittest.TestCase):
    """Tests OAuth credential persistence, expiry serialization, and auto-refresh."""

    def _build_google_modules(self, creds_cls, request_cls):
        google_mod = ModuleType("google")
        oauth2_mod = ModuleType("google.oauth2")
        oauth2_creds_mod = ModuleType("google.oauth2.credentials")
        oauth2_creds_mod.Credentials = creds_cls
        oauth2_sa_mod = ModuleType("google.oauth2.service_account")
        auth_mod = ModuleType("google.auth")
        transport_mod = ModuleType("google.auth.transport")
        requests_mod = ModuleType("google.auth.transport.requests")
        requests_mod.Request = request_cls

        google_mod.oauth2 = oauth2_mod
        google_mod.auth = auth_mod
        oauth2_mod.credentials = oauth2_creds_mod
        oauth2_mod.service_account = oauth2_sa_mod
        auth_mod.transport = transport_mod
        transport_mod.requests = requests_mod

        return google_mod, {
            "google": google_mod,
            "google.oauth2": oauth2_mod,
            "google.oauth2.credentials": oauth2_creds_mod,
            "google.oauth2.service_account": oauth2_sa_mod,
            "google.auth": auth_mod,
            "google.auth.transport": transport_mod,
            "google.auth.transport.requests": requests_mod,
        }

    def test_credentials_to_dict_serializes_iso_utc_expiry(self):
        naive_expiry = datetime.datetime(2026, 11, 26, 22, 15, 0)
        creds = SimpleNamespace(
            token="access-123",
            refresh_token="refresh-456",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="client-id",
            client_secret="client-secret",
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            expiry=naive_expiry,
        )
        data = google_analytics.credentials_to_dict(creds)
        self.assertEqual(data["expiry"], "2026-11-26T22:15:00Z")

        # Aware non-UTC timestamps normalize cleanly to UTC ISO-8601 Z
        offset_tz = datetime.timezone(datetime.timedelta(hours=-3))
        aware_creds = SimpleNamespace(
            token="access-123",
            refresh_token="refresh-456",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="client-id",
            client_secret="client-secret",
            scopes=("https://www.googleapis.com/auth/analytics.readonly",),
            expiry=datetime.datetime(2026, 11, 26, 19, 15, 0, tzinfo=offset_tz),
        )
        aware_data = google_analytics.credentials_to_dict(aware_creds)
        self.assertEqual(aware_data["expiry"], "2026-11-26T22:15:00Z")

        no_expiry_creds = SimpleNamespace(
            token="access-123",
            refresh_token="refresh-456",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="client-id",
            client_secret="client-secret",
            scopes=None,
            expiry=None,
        )
        self.assertNotIn("expiry", google_analytics.credentials_to_dict(no_expiry_creds))

    def test_save_credentials_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "nested", ".config", "ga4", "credentials.json")
            creds = SimpleNamespace(
                token="tok-1",
                refresh_token="ref-1",
                token_uri="https://oauth2.googleapis.com/token",
                client_id="cid",
                client_secret="csec",
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
                expiry=datetime.datetime(2026, 12, 1, 12, 0, 0),
            )
            google_analytics.save_credentials_to_disk(creds, creds_path)
            self.assertTrue(os.path.exists(creds_path))
            with open(creds_path, "r", encoding="utf-8") as fh:
                saved = json.load(fh)
            self.assertEqual(saved["token"], "tok-1")
            self.assertEqual(saved["expiry"], "2026-12-01T12:00:00Z")

    def test_load_credentials_refreshes_expired_and_expiryless_tokens_and_persists(self):
        refresh_calls = []
        future_expiry = datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=None, microsecond=0
        ) + datetime.timedelta(hours=1)
        past_expiry = datetime.datetime.now(datetime.timezone.utc).replace(
            tzinfo=None, microsecond=0
        ) - datetime.timedelta(minutes=10)

        if google_analytics.HAS_GOOGLE_API:
            creds_cls = google_analytics.google.oauth2.credentials.Credentials
        else:
            creds_cls = _StubCredentials

        def fake_refresh(self_creds, request):
            refresh_calls.append(request)
            self_creds.token = "refreshed-token"
            self_creds.expiry = future_expiry

        class FakeRequest:
            pass

        with tempfile.TemporaryDirectory() as tmpdir:
            creds_path = os.path.join(tmpdir, "credentials.json")
            cases = [
                ("expired", past_expiry.isoformat() + "Z"),
                ("missing_expiry", None),
            ]
            for label, raw_expiry in cases:
                with self.subTest(case=label):
                    refresh_calls.clear()
                    payload = {
                        "token": "stale-token",
                        "refresh_token": "valid-refresh-token",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "client_id": "cid",
                        "client_secret": "csec",
                        "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
                    }
                    if raw_expiry is not None:
                        payload["expiry"] = raw_expiry
                    with open(creds_path, "w", encoding="utf-8") as fh:
                        json.dump(payload, fh)

                    if google_analytics.HAS_GOOGLE_API:
                        with (
                            patch.object(creds_cls, "refresh", autospec=True, side_effect=fake_refresh),
                            patch("google.auth.transport.requests.Request", FakeRequest),
                        ):
                            loaded = google_analytics.load_credentials(creds_path)
                    else:
                        fake_google, mod_map = self._build_google_modules(creds_cls, FakeRequest)
                        with (
                            patch.dict(sys.modules, mod_map),
                            patch.object(creds_cls, "refresh", autospec=True, side_effect=fake_refresh),
                            patch.object(google_analytics, "HAS_GOOGLE_API", True),
                            patch.object(google_analytics, "google", fake_google, create=True),
                        ):
                            loaded = google_analytics.load_credentials(creds_path)

                    self.assertEqual(len(refresh_calls), 1)
                    self.assertIsInstance(refresh_calls[0], FakeRequest)
                    self.assertEqual(loaded.token, "refreshed-token")
                    self.assertEqual(loaded.expiry, future_expiry)

                    with open(creds_path, "r", encoding="utf-8") as fh:
                        persisted = json.load(fh)
                    self.assertEqual(persisted["token"], "refreshed-token")
                    self.assertEqual(persisted["expiry"], future_expiry.isoformat() + "Z")

                    # Subsequent load while token is still fresh should NOT refresh
                    refresh_calls.clear()
                    if google_analytics.HAS_GOOGLE_API:
                        with (
                            patch.object(creds_cls, "refresh", autospec=True, side_effect=fake_refresh),
                            patch("google.auth.transport.requests.Request", FakeRequest),
                        ):
                            loaded_again = google_analytics.load_credentials(creds_path)
                    else:
                        fake_google, mod_map = self._build_google_modules(creds_cls, FakeRequest)
                        with (
                            patch.dict(sys.modules, mod_map),
                            patch.object(creds_cls, "refresh", autospec=True, side_effect=fake_refresh),
                            patch.object(google_analytics, "HAS_GOOGLE_API", True),
                            patch.object(google_analytics, "google", fake_google, create=True),
                        ):
                            loaded_again = google_analytics.load_credentials(creds_path)

                    self.assertEqual(refresh_calls, [])
                    self.assertEqual(loaded_again.token, "refreshed-token")

    def test_resolve_default_credentials_file_persists_to_home_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_home = os.path.join(tmpdir, "home")
            cwd_dir = os.path.join(tmpdir, "workdir")
            os.makedirs(fake_home)
            os.makedirs(cwd_dir)

            expected_global = os.path.join(fake_home, ".config", "ga4", "credentials.json")
            orig_cwd = os.getcwd()
            try:
                os.chdir(cwd_dir)
                with patch.dict(os.environ, {"HOME": fake_home}):
                    # Neither ~/.config/ga4/credentials.json nor ./credentials.json exists -> global path
                    self.assertEqual(
                        google_analytics.resolve_default_credentials_file(),
                        expected_global,
                    )

                    # Local ./credentials.json exists when global does not -> local fallback
                    with open(os.path.join(cwd_dir, "credentials.json"), "w", encoding="utf-8") as fh:
                        fh.write("{}")
                    self.assertEqual(
                        google_analytics.resolve_default_credentials_file(),
                        "credentials.json",
                    )

                    # Global ~/.config/ga4/credentials.json takes precedence over ./credentials.json
                    os.makedirs(os.path.dirname(expected_global), exist_ok=True)
                    with open(expected_global, "w", encoding="utf-8") as fh:
                        fh.write("{}")
                    self.assertEqual(
                        google_analytics.resolve_default_credentials_file(),
                        expected_global,
                    )
            finally:
                os.chdir(orig_cwd)


if __name__ == "__main__":
    unittest.main(verbosity=2)
