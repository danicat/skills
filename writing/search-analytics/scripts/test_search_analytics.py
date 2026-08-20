#!/usr/bin/env python3
"""
Test Suite for search-analytics
Validates:
1. SQLite schema DDL, indexes, and all 7 analytical views (v_search_performance, v_daily_summary,
   v_top_queries, v_top_pages, v_country_breakdown, v_device_breakdown, v_milestone_impact).
2. Data insertion, cannibalization queries, CTR calculations, and cohort impacts.
3. Every SQL query used as an example in SKILL.md and references/queries.md.
4. Pre-packaged reports in scripts/search_analytics.py.
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
import search_analytics


class TestSearchAnalyticsSchema(unittest.TestCase):
    """Validates DDL, table structures, and analytical views."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(search_analytics.SCHEMA_DDL)

    def tearDown(self):
        self.conn.close()

    def test_tables_and_views_exist(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view')")
        names = {row["name"] for row in cursor.fetchall()}
        expected_items = {
            "properties",
            "sitemaps",
            "search_performance",
            "site_milestones",
            "sync_history",
            "v_search_performance",
            "v_daily_summary",
            "v_top_queries",
            "v_top_pages",
            "v_country_breakdown",
            "v_device_breakdown",
            "v_milestone_impact",
        }
        for item in expected_items:
            self.assertIn(item, names, f"Expected table or view '{item}' to exist in schema.")

    def test_view_top_queries_columns(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(v_top_queries)")
        columns = {row["name"] for row in cursor.fetchall()}
        expected_columns = {
            "site_url",
            "query",
            "active_days",
            "total_clicks",
            "total_impressions",
            "avg_ctr_pct",
            "avg_position",
        }
        for col in expected_columns:
            self.assertIn(col, columns, f"Expected column '{col}' in view 'v_top_queries'.")


class TestSearchAnalyticsQueries(unittest.TestCase):
    """Populates realistic fixture data and executes all example and report queries."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.row_factory = sqlite3.Row
        cls.conn.executescript(search_analytics.SCHEMA_DDL)
        cls._populate_fixture_data(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    @classmethod
    def _populate_fixture_data(cls, conn: sqlite3.Connection):
        """Populates rich synthetic fixture rows for Google Search Console analytics."""
        # 1. Properties
        conn.execute(
            "INSERT INTO properties (site_url, permission_level, raw_json, synced_at) "
            "VALUES ('https://example.com/', 'siteOwner', '{}', '2026-08-20T00:00:00Z')"
        )

        # 2. Sitemaps
        conn.execute(
            "INSERT INTO sitemaps (site_url, path, type, last_downloaded, last_submitted, errors, warnings, indexed_count, raw_json, synced_at) "
            "VALUES ('https://example.com/', 'https://example.com/sitemap.xml', 'sitemap', '2026-08-20T00:00:00Z', '2026-08-01T00:00:00Z', 0, 0, 150, '{}', '2026-08-20T00:00:00Z')"
        )

        # 3. Search Performance Rows (Varied dates, ranking queries, cannibalization pairs, CTRs)
        perf_data = [
            # site_url, date, query, page, country, device, search_appearance, search_type, clicks, impressions, ctr, position
            # High opportunity query (pos <= 10, imps >= 500, ctr < 3%)
            ('https://example.com/', '2026-08-01', 'sqlite analytics guide', 'https://example.com/blog/sqlite-guide', 'usa', 'DESKTOP', '', 'web', 12, 1200, 0.01, 4.2),
            ('https://example.com/', '2026-08-02', 'sqlite analytics guide', 'https://example.com/blog/sqlite-guide', 'usa', 'DESKTOP', '', 'web', 15, 1400, 0.0107, 3.8),
            # Cannibalization query (same query ranked on 2 different pages)
            ('https://example.com/', '2026-08-01', 'agent skills specification', 'https://example.com/docs/agent-skills', 'usa', 'DESKTOP', '', 'web', 45, 800, 0.056, 2.1),
            ('https://example.com/', '2026-08-01', 'agent skills specification', 'https://example.com/blog/agent-skills-intro', 'usa', 'DESKTOP', '', 'web', 25, 600, 0.041, 6.5),
            ('https://example.com/', '2026-08-15', 'agent skills specification', 'https://example.com/docs/agent-skills', 'gbr', 'MOBILE', '', 'web', 55, 950, 0.057, 1.8),
            ('https://example.com/', '2026-08-15', 'agent skills specification', 'https://example.com/blog/agent-skills-intro', 'gbr', 'MOBILE', '', 'web', 18, 400, 0.045, 7.2),
            # Mobile vs Desktop split
            ('https://example.com/', '2026-08-01', 'golang concurrency patterns', 'https://example.com/blog/go-concurrency', 'deu', 'DESKTOP', '', 'web', 80, 1600, 0.05, 2.5),
            ('https://example.com/', '2026-08-01', 'golang concurrency patterns', 'https://example.com/blog/go-concurrency', 'deu', 'MOBILE', '', 'web', 30, 900, 0.033, 3.2),
            ('https://example.com/', '2026-08-15', 'golang concurrency patterns', 'https://example.com/blog/go-concurrency', 'jpn', 'DESKTOP', '', 'web', 110, 2100, 0.052, 2.1),
            # Non-branded query
            ('https://example.com/', '2026-08-15', 'how to design agent tools', 'https://example.com/docs/agent-tools', 'can', 'DESKTOP', '', 'web', 60, 1100, 0.054, 3.1),
            # Branded query
            ('https://example.com/', '2026-08-15', 'brand_name agent platform', 'https://example.com/', 'usa', 'DESKTOP', '', 'web', 150, 400, 0.375, 1.0),
        ]
        for row in perf_data:
            conn.execute(
                """INSERT INTO search_performance (
                    site_url, date, query, page, country, device, search_appearance,
                    search_type, clicks, impressions, ctr, position, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                row,
            )

        # 4. Site Milestones (Pre and Post)
        conn.execute(
            """INSERT INTO site_milestones (
                commit_hash, event_date, title, description, category, scope, author, created_at
            ) VALUES ('c1a2b3d', '2026-08-10', 'Major Architecture & Content Overhaul', 'Complete refresh of site documentation', 'ARCHITECTURE', 'SITE_WIDE', 'Engineering Team', '2026-08-10T00:00:00Z')"""
        )

        conn.commit()

    def test_quickstart_adhoc_query(self):
        sql = "SELECT query, SUM(clicks), SUM(impressions) FROM search_performance GROUP BY query ORDER BY SUM(clicks) DESC LIMIT 10"
        rows = self.conn.execute(sql).fetchall()
        self.assertGreater(len(rows), 0)

    def test_cookbook_queries_skill_md(self):
        queries = [
            # 1. High-Opportunity Search Queries
            """
            SELECT
                query,
                page,
                ROUND(SUM(impressions), 0) AS imps,
                ROUND(SUM(clicks), 0) AS clks,
                ROUND((SUM(clicks)/SUM(impressions))*100, 2) AS ctr_pct,
                ROUND(AVG(position), 1) AS avg_rank
            FROM search_performance
            WHERE position <= 10
            GROUP BY query, page
            HAVING SUM(impressions) >= 500 AND ctr_pct < 3.0
            ORDER BY imps DESC
            LIMIT 15;
            """,
            # 2. Keyword Cannibalization Detection
            """
            SELECT
                query,
                COUNT(DISTINCT page) AS competing_pages,
                GROUP_CONCAT(DISTINCT page) AS pages,
                ROUND(SUM(clicks), 0) AS total_clicks,
                ROUND(SUM(impressions), 0) AS total_impressions
            FROM search_performance
            WHERE query != ''
            GROUP BY query
            HAVING COUNT(DISTINCT page) > 1
            ORDER BY total_impressions DESC
            LIMIT 10;
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
            # 1. High-Opportunity Optimization Targets
            """
            SELECT
                query,
                page,
                ROUND(SUM(impressions), 0) AS total_impressions,
                ROUND(SUM(clicks), 0) AS total_clicks,
                ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS ctr_pct,
                ROUND(AVG(position), 1) AS avg_rank
            FROM search_performance
            WHERE position <= 10
            GROUP BY query, page
            HAVING SUM(impressions) >= 500 AND ctr_pct < 3.0
            ORDER BY total_impressions DESC
            LIMIT 20;
            """,
            # 2. Keyword Cannibalization Detection
            """
            SELECT
                query,
                COUNT(DISTINCT page) AS competing_pages,
                GROUP_CONCAT(DISTINCT page) AS pages,
                ROUND(SUM(clicks), 0) AS total_clicks,
                ROUND(SUM(impressions), 0) AS total_impressions
            FROM search_performance
            WHERE query != ''
            GROUP BY query
            HAVING COUNT(DISTINCT page) > 1
            ORDER BY total_impressions DESC
            LIMIT 15;
            """,
            # 3. Position-to-CTR Decay Curve
            """
            SELECT
                ROUND(position) AS rank_bucket,
                ROUND(SUM(clicks), 0) AS clicks,
                ROUND(SUM(impressions), 0) AS impressions,
                ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS actual_ctr_pct
            FROM search_performance
            WHERE position BETWEEN 1 AND 10
            GROUP BY rank_bucket
            ORDER BY rank_bucket ASC;
            """,
            # 4. Mobile vs Desktop Traffic Split
            """
            SELECT
                device,
                COUNT(DISTINCT date) AS active_days,
                ROUND(SUM(clicks), 0) AS clicks,
                ROUND(SUM(impressions), 0) AS impressions,
                ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS ctr_pct,
                ROUND(AVG(position), 1) AS avg_rank
            FROM search_performance
            WHERE device != ''
            GROUP BY device
            ORDER BY clicks DESC;
            """,
            # 5. Day-of-the-Week Traffic Trends
            """
            SELECT
                day_of_week,
                COUNT(DISTINCT date) AS day_count,
                ROUND(AVG(total_clicks), 1) AS avg_clicks_per_day,
                ROUND(AVG(total_impressions), 0) AS avg_impressions_per_day,
                ROUND(AVG(avg_ctr_pct), 2) AS avg_ctr_pct
            FROM v_daily_summary
            GROUP BY day_of_week
            ORDER BY avg_clicks_per_day DESC;
            """,
            # 6. Month-over-Month Growth Trajectory
            """
            SELECT
                strftime('%Y-%m', date) AS year_month,
                COUNT(DISTINCT date) AS days_in_month,
                ROUND(SUM(clicks), 0) AS total_clicks,
                ROUND(SUM(impressions), 0) AS total_impressions,
                ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS monthly_ctr_pct,
                ROUND(AVG(position), 1) AS avg_rank
            FROM search_performance
            GROUP BY year_month
            ORDER BY year_month DESC;
            """,
            # 7. Non-Branded Search Performance
            """
            SELECT
                query,
                COUNT(DISTINCT date) AS active_days,
                ROUND(SUM(clicks), 0) AS total_clicks,
                ROUND(SUM(impressions), 0) AS total_impressions,
                ROUND((SUM(clicks) / SUM(impressions)) * 100, 2) AS ctr_pct,
                ROUND(AVG(position), 1) AS avg_position
            FROM search_performance
            WHERE query != ''
              AND LOWER(query) NOT LIKE '%brand_name%'
              AND LOWER(query) NOT LIKE '%product_name%'
            GROUP BY query
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
                    site_url,
                    MIN(date) AS earliest_date,
                    MAX(date) AS latest_date,
                    COUNT(DISTINCT date) AS active_days,
                    COUNT(DISTINCT query) AS distinct_queries,
                    COUNT(DISTINCT page) AS distinct_pages,
                    ROUND(SUM(clicks), 0) AS total_clicks,
                    ROUND(SUM(impressions), 0) AS total_impressions,
                    ROUND((SUM(clicks)/SUM(impressions))*100, 2) AS avg_ctr_pct,
                    ROUND(AVG(position), 1) AS avg_position
                FROM search_performance
                GROUP BY site_url;
            """,
            "top-queries": """
                SELECT
                    query,
                    active_days,
                    total_clicks,
                    total_impressions,
                    avg_ctr_pct,
                    avg_position
                FROM v_top_queries
                ORDER BY total_clicks DESC, total_impressions DESC
                LIMIT 15;
            """,
            "top-pages": """
                SELECT
                    page,
                    ranking_queries,
                    total_clicks,
                    total_impressions,
                    avg_ctr_pct,
                    avg_position
                FROM v_top_pages
                ORDER BY total_clicks DESC, total_impressions DESC
                LIMIT 15;
            """,
            "countries": """
                SELECT
                    country,
                    total_clicks,
                    total_impressions,
                    avg_ctr_pct,
                    avg_position
                FROM v_country_breakdown
                ORDER BY total_clicks DESC, total_impressions DESC
                LIMIT 15;
            """,
            "devices": """
                SELECT
                    device,
                    total_clicks,
                    total_impressions,
                    avg_ctr_pct,
                    avg_position
                FROM v_device_breakdown
                ORDER BY total_clicks DESC;
            """,
            "timing": """
                SELECT
                    day_of_week,
                    COUNT(*) AS days_recorded,
                    ROUND(AVG(total_clicks), 1) AS avg_daily_clicks,
                    ROUND(AVG(total_impressions), 0) AS avg_daily_impressions,
                    ROUND(AVG(avg_ctr_pct), 2) AS avg_ctr_pct
                FROM v_daily_summary
                GROUP BY day_of_week
                ORDER BY avg_daily_clicks DESC;
            """,
            "milestone-impact": """
                SELECT
                    commit_hash,
                    milestone_title,
                    milestone_date,
                    cohort,
                    days_tracked,
                    total_impressions,
                    total_clicks,
                    ctr_pct || '%' AS ctr,
                    avg_position
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


class TestSearchAnalyticsCLI(unittest.TestCase):
    """Tests CLI entry points and argument parsing."""

    def test_cli_help(self):
        script_path = os.path.join(SCRIPT_DIR, "search_analytics.py")
        cmd = [sys.executable, script_path, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Google Search Console", result.stdout)
        self.assertIn("sync", result.stdout)
        self.assertIn("report", result.stdout)
        self.assertIn("query", result.stdout)
        self.assertIn("submit-sitemap", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
