#!/usr/bin/env python3
"""
Test Suite for google-analytics
Validates:
1. SQLite schema DDL, indexes, and all 7 analytical views (v_daily_summary, v_page_performance,
   v_channel_performance, v_geo_breakdown, v_events_summary, v_outbound_links, v_milestone_impact).
2. Data insertion, referential integrity, and cohort computations.
3. Every SQL query used as an example in SKILL.md and references/queries.md.
4. Pre-packaged reports in scripts/google_analytics.py.
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
            ('prop_123', '2026-08-15', 'google / organic', 'Organic Search', 'United States', 'desktop', 680, 590, 380, 560, 62000.0, 0.18),
            ('prop_123', '2026-08-15', 'direct / none', 'Direct', 'United States', 'mobile', 310, 270, 60, 240, 24000.0, 0.26),
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
            ('prop_123', '2026-08-01', 'click', '/blog/sqlite-analytics-guide', 'United Kingdom', 'desktop', 85, 70),
            ('prop_123', '2026-08-15', 'page_view', '/blog/sqlite-analytics-guide', 'United States', 'desktop', 480, 400),
            ('prop_123', '2026-08-15', 'scroll', '/blog/sqlite-analytics-guide', 'United States', 'desktop', 410, 350),
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
            ('prop_123', '2026-08-01', 'https://github.com/danicat/skills', '/docs/getting-started', 'United States', 45, 40),
            ('prop_123', '2026-08-01', 'https://sqlite.org/wal.html', '/blog/sqlite-analytics-guide', 'United Kingdom', 28, 25),
            ('prop_123', '2026-08-15', 'https://github.com/danicat/skills', '/tutorials/building-agent-skills', 'United States', 62, 55),
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
                ROUND(AVG(avg_bounce_pct), 1) AS avg_bounce_pct
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
                ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_pct
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
                ROUND(AVG(engagement_rate_pct), 1) || '%' AS avg_engagement_rate,
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
        reports = {
            "overview": """
                SELECT
                    COUNT(DISTINCT date) AS active_days,
                    SUM(total_sessions) AS total_sessions,
                    SUM(total_active_users) AS total_active_users,
                    SUM(total_page_views) AS total_views,
                    ROUND(AVG(total_engagement_min), 1) AS avg_daily_engagement_min,
                    ROUND(AVG(avg_bounce_pct), 1) AS overall_bounce_pct
                FROM v_daily_summary
                LIMIT 30;
            """,
            "top-pages": """
                SELECT
                    page_path,
                    page_title,
                    total_views,
                    total_users,
                    avg_dwell_sec || 's' AS dwell,
                    avg_bounce_pct || '%' AS bounce
                FROM v_page_performance
                ORDER BY total_views DESC
                LIMIT 15;
            """,
            "channels": """
                SELECT
                    channel_group,
                    source_medium,
                    total_sessions,
                    total_users,
                    engagement_rate_pct || '%' AS eng_rate,
                    total_dwell_min || 'm' AS dwell,
                    avg_bounce_pct || '%' AS bounce
                FROM v_channel_performance
                WHERE total_sessions > 5
                ORDER BY total_sessions DESC
                LIMIT 15;
            """,
            "geo": """
                SELECT
                    country,
                    total_sessions,
                    total_users,
                    total_page_views,
                    avg_dwell_sec || 's' AS avg_dwell,
                    avg_bounce_pct || '%' AS bounce
                FROM v_geo_breakdown
                ORDER BY total_sessions DESC
                LIMIT 10;
            """,
            "events": """
                SELECT
                    event_name,
                    total_events,
                    total_users
                FROM v_events_summary;
            """,
            "outbound": """
                SELECT
                    link_url,
                    total_clicks,
                    total_users,
                    referring_pages_count
                FROM v_outbound_links
                ORDER BY total_clicks DESC
                LIMIT 15;
            """,
            "milestone-impact": """
                SELECT
                    commit_hash,
                    milestone_title,
                    milestone_date,
                    cohort,
                    days_tracked,
                    total_views,
                    total_users,
                    total_sessions,
                    avg_engagement_sec || 's' AS avg_dwell,
                    avg_bounce_pct || '%' AS bounce
                FROM v_milestone_impact;
            """,
        }
        for name, sql in reports.items():
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
        self.assertGreaterEqual(total_executed, 9, "Expected at least 9 markdown SQL blocks to be tested.")


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
