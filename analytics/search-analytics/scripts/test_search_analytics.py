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
Test Suite for search-analytics
Validates:
1. SQLite schema DDL, indexes, WAL/FK pragmas, and all 7 analytical views (v_search_performance,
   v_daily_summary, v_top_queries, v_top_pages, v_country_breakdown, v_device_breakdown, v_milestone_impact).
2. Impression-weighted position and CTR calculations, cannibalization queries, and cohort impacts.
3. Every SQL query used as an example in SKILL.md and references/queries.md.
4. Pre-packaged reports in scripts/search_analytics.py (all tracked dates default and optional --days).
5. Multi-page startRow pagination and fail-fast API propagation.
6. Dynamic extraction and execution of all SQL code blocks in markdown documentation.
7. CLI argument parsing, milestone recording, and validation.
"""

import os
import re
import sqlite3
import subprocess
import sys
import tempfile
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
            "daily_site_performance",
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

        # 4. Daily Site Performance (Property-level unfiltered totals)
        site_perf_data = [
            ('https://example.com/', '2026-08-01', 'web', 150, 4500, 0.0333, 3.5),
            ('https://example.com/', '2026-08-02', 'web', 180, 5200, 0.0346, 3.2),
            ('https://example.com/', '2026-08-03', 'web', 90, 2500, 0.036, 4.1),
            ('https://example.com/', '2026-08-15', 'web', 350, 8900, 0.0393, 2.8),
        ]
        for row in site_perf_data:
            conn.execute(
                """INSERT INTO daily_site_performance (
                    site_url, date, search_type, clicks, impressions, ctr, position, raw_json, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
                row,
            )

        # 5. Site Milestones (Pre and Post)
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
                ROUND(SUM(position * impressions) * 1.0 / MAX(SUM(impressions), 1), 1) AS avg_rank
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
                ROUND(SUM(position * impressions) * 1.0 / MAX(SUM(impressions), 1), 1) AS avg_rank
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
                ROUND(SUM(position * impressions) * 1.0 / MAX(SUM(impressions), 1), 1) AS avg_rank
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
                ROUND(SUM(total_clicks) * 100.0 / MAX(SUM(total_impressions), 1), 2) AS avg_ctr_pct
            FROM v_daily_summary
            GROUP BY day_of_week
            ORDER BY avg_clicks_per_day DESC;
            """,
            # 6. Month-over-Month Growth Trajectory (Unfiltered property totals)
            """
            SELECT
                year_month,
                COUNT(DISTINCT date) AS days_in_month,
                ROUND(SUM(total_clicks), 0) AS total_clicks,
                ROUND(SUM(total_impressions), 0) AS total_impressions,
                ROUND(SUM(total_clicks) * 100.0 / MAX(SUM(total_impressions), 1), 2) AS monthly_ctr_pct,
                ROUND(SUM(avg_position * total_impressions) * 1.0 / MAX(SUM(total_impressions), 1), 1) AS avg_rank
            FROM v_daily_summary
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
                ROUND(SUM(position * impressions) * 1.0 / MAX(SUM(impressions), 1), 1) AS avg_position
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
        for name in search_analytics.VALID_REPORTS:
            with self.subTest(report_name=name):
                _, sql, params = search_analytics.build_report_query(name)
                cursor = self.conn.execute(sql, params)
                rows = cursor.fetchall()
                self.assertIsNotNone(rows)
                self.assertGreater(len(rows), 0, f"Report '{name}' returned empty result.")

    def test_default_db_nested_dir_and_foreign_keys(self):
        """Verifies DEFAULT_DB_FILE, nested dir creation in init_db, and foreign-key cascades."""
        self.assertEqual(search_analytics.DEFAULT_DB_FILE, "search_analytics.db")
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_db = os.path.join(tmpdir, "nested", "dir", "gsc.db")
            conn = search_analytics.init_db(nested_db)
            conn.execute(
                "INSERT INTO properties (site_url, permission_level, raw_json, synced_at) VALUES ('https://example.com/', 'siteOwner', '{}', '2026-08-20T00:00:00Z')"
            )
            conn.execute(
                "INSERT INTO sitemaps (site_url, path, type, raw_json, synced_at) VALUES ('https://example.com/', 'https://example.com/sitemap.xml', 'sitemap', '{}', '2026-08-20T00:00:00Z')"
            )
            conn.commit()
            conn.execute("DELETE FROM properties WHERE site_url = 'https://example.com/'")
            remaining = conn.execute("SELECT COUNT(*) FROM sitemaps").fetchone()[0]
            self.assertEqual(remaining, 0)
            conn.close()

    def test_impression_weighted_avg_position(self):
        """Ensures v_top_queries computes impression-weighted average position rather than simple shard average."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(search_analytics.SCHEMA_DDL)
        # 1000 impressions at pos 1.0 + 10 impressions at pos 50.0 -> (1000 + 500)/1010 = 1.485 -> 1.5
        conn.executemany(
            """INSERT INTO search_performance (
                site_url, date, query, page, country, device, search_appearance,
                search_type, clicks, impressions, ctr, position, raw_json, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, '', 'web', ?, ?, ?, ?, '{}', '2026-08-20T00:00:00Z')""",
            [
                ("https://example.com/", "2026-08-01", "weighted query", "https://example.com/a", "usa", "DESKTOP", 100, 1000, 0.1, 1.0),
                ("https://example.com/", "2026-08-01", "weighted query", "https://example.com/a", "usa", "MOBILE", 0, 10, 0.0, 50.0),
            ],
        )
        row = conn.execute("SELECT avg_position FROM v_top_queries WHERE query = 'weighted query'").fetchone()
        self.assertEqual(row["avg_position"], 1.5)
        conn.close()

    def test_overview_and_milestone_unfiltered_plus_days(self):
        """Verifies report overview & v_milestone_impact read unfiltered v_daily_summary and honor optional --days."""
        _, sql, params = search_analytics.build_report_query("overview", days=None)
        ov = self.conn.execute(sql, params).fetchone()
        self.assertEqual(ov["active_days"], 4)
        self.assertEqual(ov["total_clicks"], 770.0)
        self.assertEqual(ov["total_impressions"], 21100.0)
        self.assertGreater(ov["distinct_queries"], 0)

        pre = self.conn.execute(
            "SELECT days_tracked, total_clicks FROM v_milestone_impact WHERE cohort = 'Pre-Milestone'"
        ).fetchone()
        post = self.conn.execute(
            "SELECT days_tracked, total_clicks FROM v_milestone_impact WHERE cohort = 'Post-Milestone'"
        ).fetchone()
        self.assertEqual(pre["days_tracked"], 3)
        self.assertEqual(pre["total_clicks"], 420.0)
        self.assertEqual(post["days_tracked"], 1)
        self.assertEqual(post["total_clicks"], 350.0)

        # Verify no implicit 30-day truncation and explicit --days windowing
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript(search_analytics.SCHEMA_DDL)
        conn.executemany(
            """INSERT INTO daily_site_performance (
                site_url, date, search_type, clicks, impressions, ctr, position, raw_json, synced_at
            ) VALUES ('https://example.com/', ?, 'web', ?, ?, 0.05, 2.0, '{}', '2026-08-20T00:00:00Z')""",
            [
                ("2026-06-01", 20, 400),
                ("2026-08-01", 30, 600),
                ("2026-08-15", 40, 800),
                ("2026-08-16", 50, 1000),
            ],
        )
        _, sql_all, p_all = search_analytics.build_report_query("overview", days=None)
        all_row = conn.execute(sql_all, p_all).fetchone()
        self.assertEqual(all_row["earliest_date"], "2026-06-01")
        self.assertEqual(all_row["active_days"], 4)
        self.assertEqual(all_row["total_clicks"], 140.0)

        _, sql_30, p_30 = search_analytics.build_report_query("overview", days=30)
        row_30 = conn.execute(sql_30, p_30).fetchone()
        self.assertEqual(row_30["earliest_date"], "2026-08-01")
        self.assertEqual(row_30["active_days"], 3)

        _, sql_7, p_7 = search_analytics.build_report_query("overview", days=7)
        row_7 = conn.execute(sql_7, p_7).fetchone()
        self.assertEqual(row_7["earliest_date"], "2026-08-15")
        self.assertEqual(row_7["active_days"], 2)
        conn.close()

    def test_fetch_day_data_pagination_and_fail_fast(self):
        """Verifies startRow pagination across batches and fail-fast error propagation."""
        starts = []
        pages = {
            0: {"rows": [{"keys": ["q1", "p1"], "clicks": 1, "impressions": 10}, {"keys": ["q2", "p2"], "clicks": 2, "impressions": 20}]},
            2: {"rows": [{"keys": ["q3", "p3"], "clicks": 3, "impressions": 30}]},
        }

        class FakeExec:
            def __init__(self, start_row):
                self.start_row = start_row

            def execute(self):
                starts.append(self.start_row)
                return pages[self.start_row]

        class FakeSearchAnalytics:
            def query(self, siteUrl, body):
                return FakeExec(body["startRow"])

        class FakeService:
            def searchanalytics(self):
                return FakeSearchAnalytics()

        rows = search_analytics.fetch_day_data(FakeService(), "https://example.com/", "2026-08-01", ["query", "page"], max_rows=2)
        self.assertEqual(starts, [0, 2])
        self.assertEqual(len(rows), 3)

        class FailingExec:
            def execute(self):
                raise RuntimeError("API 429 quota exceeded")

        class FailingSearchAnalytics:
            def query(self, siteUrl, body):
                return FailingExec()

        class FailingService:
            def searchanalytics(self):
                return FailingSearchAnalytics()

        with self.assertRaises(RuntimeError):
            search_analytics.fetch_day_data(FailingService(), "https://example.com/", "2026-08-01", ["query", "page"])

    def test_record_milestone(self):
        """Verifies record_milestone persists entries into site_milestones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "gsc.db")
            c_hash = search_analytics.record_milestone(
                title="v3.0 Launch",
                date_str="2026-08-18",
                commit_hash="abc999",
                description="Major release",
                db_path=db_path,
            )
            self.assertEqual(c_hash, "abc999")
            conn = sqlite3.connect(db_path)
            row = conn.execute("SELECT title, event_date FROM site_milestones WHERE commit_hash = 'abc999'").fetchone()
            self.assertEqual(row, ("v3.0 Launch", "2026-08-18"))
            conn.close()

    def test_daily_summary_zero_loss_reconciliation(self):
        """Validates that v_daily_summary correctly prioritizes unfiltered property totals over privacy-truncated query sums."""
        # Query 2026-08-01 where daily_site_performance has clicks=150, but search_performance sum is 110
        row = self.conn.execute(
            "SELECT total_clicks, total_impressions, distinct_queries FROM v_daily_summary WHERE date = '2026-08-01'"
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["total_clicks"], 150)
        self.assertEqual(row["total_impressions"], 4500)
        self.assertGreater(row["distinct_queries"], 0)

        # Query 2026-08-03 where search_performance has 0 rows (100% anonymized query day)
        row_anon = self.conn.execute(
            "SELECT total_clicks, total_impressions, distinct_queries, distinct_pages FROM v_daily_summary WHERE date = '2026-08-03'"
        ).fetchone()
        self.assertIsNotNone(row_anon)
        self.assertEqual(row_anon["total_clicks"], 90)
        self.assertEqual(row_anon["total_impressions"], 2500)
        self.assertEqual(row_anon["distinct_queries"], 0)
        self.assertEqual(row_anon["distinct_pages"], 0)

    def test_schema_migration_view_replacement(self):
        """Verifies that executing SCHEMA_DDL on an existing DB replaces legacy views."""
        conn = sqlite3.connect(":memory:")
        # Create full legacy tables with an obsolete view definition
        conn.execute("""
            CREATE TABLE search_performance (
                id INTEGER PRIMARY KEY, site_url TEXT, date TEXT, query TEXT DEFAULT '',
                page TEXT DEFAULT '', country TEXT DEFAULT '', device TEXT DEFAULT '',
                search_appearance TEXT DEFAULT '', search_type TEXT DEFAULT 'web',
                clicks REAL DEFAULT 0, impressions REAL DEFAULT 0, ctr REAL DEFAULT 0,
                position REAL DEFAULT 0, raw_json TEXT DEFAULT '{}', synced_at TEXT DEFAULT ''
            )
        """)
        conn.execute("CREATE VIEW v_daily_summary AS SELECT site_url, date, SUM(clicks) AS total_clicks FROM search_performance GROUP BY site_url, date")
        # Apply updated SCHEMA_DDL (which includes DROP VIEW IF EXISTS)
        conn.executescript(search_analytics.SCHEMA_DDL)
        # Verify view was replaced with new schema columns
        cursor = conn.execute("PRAGMA table_info(v_daily_summary)")
        cols = {r[1] for r in cursor.fetchall()}
        self.assertIn("distinct_queries", cols)
        self.assertIn("distinct_pages", cols)
        self.assertIn("avg_ctr_pct", cols)
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
        self.assertIn("milestone", result.stdout)
        self.assertIn("report", result.stdout)
        self.assertIn("query", result.stdout)
        self.assertIn("submit-sitemap", result.stdout)

    def test_cli_report_invalid_days_fails_fast(self):
        script_path = os.path.join(SCRIPT_DIR, "search_analytics.py")
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "gsc.db")
            cmd = [sys.executable, script_path, "report", "overview", "--days", "0", "--db", db_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--days", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
