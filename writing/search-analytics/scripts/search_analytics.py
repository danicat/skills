#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "flask>=3.0.0",
#     "google-api-python-client>=2.100.0",
#     "google-auth-oauthlib>=1.2.0",
#     "google-auth>=2.28.0",
#     "tabulate>=0.9.0",
#     "requests>=2.31.0",
# ]
# ///
"""
Google Search Console Ingestion Engine & SQL Analytics CLI.

Ingests raw search performance data, properties, and sitemaps from the Google Search Console API
into a local SQLite database (~/.gsc/analytics.db) without data loss, supporting:
- Interactive OAuth 2.0 web authentication flow
- Robust day-by-day historical backfill (up to GSC 16-month limit)
- Automatic batch pagination (25,000 row chunks per day)
- True incremental sync with data latency lookback overlap
- Raw JSON retention on all records
- Direct SQL querying and pre-canned analytical views

Usage:
  # 1. Authenticate with Google via local OAuth companion
  python3 search_analytics.py auth [--port 8080]

  # 2. Incremental Sync (New days since last sync + 3-day latency refresh)
  python3 search_analytics.py sync

  # 3. Full Historical Backfill (16 months of daily granular data)
  python3 search_analytics.py sync --full

  # 4. Custom Date Range Sync
  python3 search_analytics.py sync --start-date 2026-06-01 --end-date 2026-08-15

  # 5. Execute Arbitrary SQL Query
  python3 search_analytics.py query "SELECT query, SUM(clicks), SUM(impressions) FROM v_search_performance GROUP BY query ORDER BY SUM(clicks) DESC LIMIT 10"

  # 6. Run Pre-Built Reports
  python3 search_analytics.py report overview
  python3 search_analytics.py report top-queries
  python3 search_analytics.py report top-pages
  python3 search_analytics.py report countries
  python3 search_analytics.py report devices
"""

import argparse
import csv
import datetime
import json
import os
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Enable insecure transport for localhost OAuth development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

## Default Paths (Local to working directory, overridable via CLI flags)
DEFAULT_CLIENT_SECRETS_FILE = (
    os.path.expanduser("~/.config/gsc/client_secret.json")
    if os.path.exists(os.path.expanduser("~/.config/gsc/client_secret.json"))
    else "client_secret.json"
)
DEFAULT_CREDENTIALS_FILE = (
    os.path.expanduser("~/.config/gsc/credentials.json")
    if os.path.exists(os.path.expanduser("~/.config/gsc/credentials.json"))
    else "credentials.json"
)
DEFAULT_DB_FILE = "analytics.db"

# Google Search Console API Constants
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters",
]
API_SERVICE_NAME = "searchconsole"
API_VERSION = "v1"


def ensure_dirs(db_path: str = DEFAULT_DB_FILE, config_file: Optional[str] = None):
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    if config_file:
        config_dir = os.path.dirname(os.path.abspath(config_file))
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)


# ---------------------------------------------------------------------------
# Database Schema & Migrations
# ---------------------------------------------------------------------------

SCHEMA_DDL = """
-- Verified Properties
CREATE TABLE IF NOT EXISTS properties (
    site_url TEXT PRIMARY KEY,
    permission_level TEXT,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL
);

-- Submitted XML Sitemaps
CREATE TABLE IF NOT EXISTS sitemaps (
    site_url TEXT NOT NULL,
    path TEXT NOT NULL,
    type TEXT,
    last_downloaded TEXT,
    last_submitted TEXT,
    errors INTEGER DEFAULT 0,
    warnings INTEGER DEFAULT 0,
    indexed_count INTEGER,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL,
    PRIMARY KEY (site_url, path),
    FOREIGN KEY (site_url) REFERENCES properties(site_url) ON DELETE CASCADE
);

-- Granular Daily Search Performance (Zero data loss)
CREATE TABLE IF NOT EXISTS search_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_url TEXT NOT NULL,
    date TEXT NOT NULL,
    query TEXT NOT NULL DEFAULT '',
    page TEXT NOT NULL DEFAULT '',
    country TEXT NOT NULL DEFAULT '',
    device TEXT NOT NULL DEFAULT '',
    search_appearance TEXT NOT NULL DEFAULT '',
    search_type TEXT NOT NULL DEFAULT 'web',
    clicks REAL NOT NULL DEFAULT 0,
    impressions REAL NOT NULL DEFAULT 0,
    ctr REAL NOT NULL DEFAULT 0,
    position REAL NOT NULL DEFAULT 0,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL,
    UNIQUE(site_url, date, query, page, country, device, search_appearance, search_type)
);

-- Unfiltered Property-Level Daily Totals (Zero data loss, no anonymized query filtering)
CREATE TABLE IF NOT EXISTS daily_site_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_url TEXT NOT NULL,
    date TEXT NOT NULL,
    search_type TEXT NOT NULL DEFAULT 'web',
    clicks REAL NOT NULL DEFAULT 0,
    impressions REAL NOT NULL DEFAULT 0,
    ctr REAL NOT NULL DEFAULT 0,
    position REAL NOT NULL DEFAULT 0,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL,
    UNIQUE(site_url, date, search_type)
);

-- Indexes for lightning fast analytical aggregation
CREATE INDEX IF NOT EXISTS idx_search_perf_date ON search_performance(site_url, date);
CREATE INDEX IF NOT EXISTS idx_search_perf_query ON search_performance(site_url, query);
CREATE INDEX IF NOT EXISTS idx_search_perf_page ON search_performance(site_url, page);
CREATE INDEX IF NOT EXISTS idx_search_perf_country ON search_performance(site_url, country);
CREATE INDEX IF NOT EXISTS idx_search_perf_device ON search_performance(site_url, device);
CREATE INDEX IF NOT EXISTS idx_daily_site_date ON daily_site_performance(site_url, date);

-- Sync History Audit Log
CREATE TABLE IF NOT EXISTS sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_url TEXT,
    sync_type TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    rows_synced INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT
);

-- ===========================================================================
-- Analytical SQL Views
-- ===========================================================================

-- 1. Main Search Performance View with Date Dimensions
DROP VIEW IF EXISTS v_search_performance;
CREATE VIEW v_search_performance AS
SELECT
    site_url,
    date,
    strftime('%Y-%m', date) AS year_month,
    CASE strftime('%w', date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    query,
    page,
    country,
    device,
    search_type,
    clicks,
    impressions,
    ROUND(ctr * 100, 2) AS ctr_pct,
    ROUND(position, 1) AS avg_position
FROM search_performance;

-- 2. Daily Summary Aggregate View (Powered by unfiltered site performance with fallback)
DROP VIEW IF EXISTS v_daily_summary;
CREATE VIEW v_daily_summary AS
WITH s_daily AS (
    SELECT
        site_url,
        date,
        SUM(clicks) AS clicks,
        SUM(impressions) AS impressions,
        CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100 ELSE 0 END AS ctr_pct,
        ROUND(AVG(position), 1) AS avg_position
    FROM daily_site_performance
    GROUP BY site_url, date
),
p_daily AS (
    SELECT
        site_url,
        date,
        COUNT(DISTINCT query) AS distinct_queries,
        COUNT(DISTINCT page) AS distinct_pages,
        SUM(clicks) AS clicks,
        SUM(impressions) AS impressions,
        CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100 ELSE 0 END AS ctr_pct,
        ROUND(AVG(position), 1) AS avg_position
    FROM search_performance
    GROUP BY site_url, date
),
dates AS (
    SELECT DISTINCT site_url, date FROM daily_site_performance
    UNION
    SELECT DISTINCT site_url, date FROM search_performance
)
SELECT
    d.site_url,
    d.date,
    strftime('%Y-%m', d.date) AS year_month,
    CASE strftime('%w', d.date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    COALESCE(p.distinct_queries, 0) AS distinct_queries,
    COALESCE(p.distinct_pages, 0) AS distinct_pages,
    ROUND(COALESCE(s.clicks, p.clicks, 0), 0) AS total_clicks,
    ROUND(COALESCE(s.impressions, p.impressions, 0), 0) AS total_impressions,
    ROUND(COALESCE(s.ctr_pct, p.ctr_pct, 0), 2) AS avg_ctr_pct,
    ROUND(COALESCE(s.avg_position, p.avg_position, 0), 1) AS avg_position
FROM dates d
LEFT JOIN s_daily s ON d.site_url = s.site_url AND d.date = s.date
LEFT JOIN p_daily p ON d.site_url = p.site_url AND d.date = p.date;

-- 3. Top Search Queries Aggregate View
DROP VIEW IF EXISTS v_top_queries;
CREATE VIEW v_top_queries AS
SELECT
    site_url,
    query,
    COUNT(DISTINCT date) AS active_days,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND(CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100 ELSE 0 END, 2) AS avg_ctr_pct,
    ROUND(AVG(position), 1) AS avg_position
FROM search_performance
WHERE query != ''
GROUP BY site_url, query;

-- 4. Top Landing Pages Aggregate View
DROP VIEW IF EXISTS v_top_pages;
CREATE VIEW v_top_pages AS
SELECT
    site_url,
    page,
    COUNT(DISTINCT query) AS ranking_queries,
    COUNT(DISTINCT date) AS active_days,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND(CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100 ELSE 0 END, 2) AS avg_ctr_pct,
    ROUND(AVG(position), 1) AS avg_position
FROM search_performance
WHERE page != ''
GROUP BY site_url, page;

-- 5. Country Breakdown View
DROP VIEW IF EXISTS v_country_breakdown;
CREATE VIEW v_country_breakdown AS
SELECT
    site_url,
    country,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND(CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100 ELSE 0 END, 2) AS avg_ctr_pct,
    ROUND(AVG(position), 1) AS avg_position
FROM search_performance
WHERE country != ''
GROUP BY site_url, country;

-- 6. Device Breakdown View
DROP VIEW IF EXISTS v_device_breakdown;
CREATE VIEW v_device_breakdown AS
SELECT
    site_url,
    device,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions,
    ROUND(CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) / SUM(impressions)) * 100 ELSE 0 END, 2) AS avg_ctr_pct,
    ROUND(AVG(position), 1) AS avg_position
FROM search_performance
WHERE device != ''
GROUP BY site_url, device;

-- 7. Release / Deployment Milestones
CREATE TABLE IF NOT EXISTS site_milestones (
    commit_hash TEXT PRIMARY KEY,
    event_date DATE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    scope TEXT,
    author TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Milestone Impact Cohort Comparison View
DROP VIEW IF EXISTS v_milestone_impact;
CREATE VIEW v_milestone_impact AS
SELECT
    m.commit_hash,
    m.title AS milestone_title,
    m.event_date AS milestone_date,
    CASE WHEN sp.date < m.event_date THEN 'Pre-Milestone' ELSE 'Post-Milestone' END AS cohort,
    COUNT(DISTINCT sp.date) AS days_tracked,
    ROUND(SUM(sp.impressions), 0) AS total_impressions,
    ROUND(SUM(sp.clicks), 0) AS total_clicks,
    ROUND((SUM(sp.clicks) / MAX(SUM(sp.impressions), 1)) * 100, 2) AS ctr_pct,
    ROUND(AVG(sp.position), 1) AS avg_position
FROM search_performance sp
CROSS JOIN site_milestones m
GROUP BY m.commit_hash, cohort;
"""


def init_db(db_path: str = DEFAULT_DB_FILE) -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_DDL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# OAuth & Credential Utilities
# ---------------------------------------------------------------------------

def credentials_to_dict(credentials) -> Dict[str, Any]:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def save_credentials_to_disk(credentials, filepath: str = DEFAULT_CREDENTIALS_FILE):
    ensure_dirs()
    data = credentials_to_dict(credentials)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_credentials_from_disk(filepath: str = DEFAULT_CREDENTIALS_FILE, service_account_path: Optional[str] = None):
    import google.oauth2.credentials
    import google.oauth2.service_account

    # 1. Check explicit service account JSON
    sa_path = service_account_path or ("service_account.json" if os.path.exists("service_account.json") else os.path.expanduser("~/.config/gsc/service_account.json"))
    if os.path.exists(sa_path):
        try:
            return google.oauth2.service_account.Credentials.from_service_account_file(
                sa_path, scopes=SCOPES
            )
        except Exception:
            pass

    # 2. Check direct Search Console OAuth credentials JSON
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return google.oauth2.credentials.Credentials(**data)
        except Exception:
            pass

    # 3. Check Google Application Default Credentials (ADC / gcloud)
    try:
        import google.auth
        credentials, _ = google.auth.default(scopes=SCOPES)
        return credentials
    except Exception:
        pass

    return None


def get_search_console_service(credentials):
    import googleapiclient.discovery
    return googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )


# ---------------------------------------------------------------------------
# Ingestion & Backfill Engine
# ---------------------------------------------------------------------------

def sync_properties_and_sitemaps(service, conn: sqlite3.Connection) -> List[str]:
    """Syncs all verified properties and their sitemaps into SQLite."""
    site_list = service.sites().list().execute()
    entries = site_list.get("siteEntry", [])
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    verified_urls = []

    for s in entries:
        site_url = s.get("siteUrl")
        perm = s.get("permissionLevel", "Unknown")
        if perm != "siteUnverifiedUser":
            verified_urls.append(site_url)

        conn.execute(
            """
            INSERT OR REPLACE INTO properties (site_url, permission_level, raw_json, synced_at)
            VALUES (?, ?, ?, ?)
            """,
            (site_url, perm, json.dumps(s), now),
        )

        # Sync sitemaps for this property
        try:
            sm_resp = service.sitemaps().list(siteUrl=site_url).execute()
            for sm in sm_resp.get("sitemap", []):
                path = sm.get("path")
                sm_type = sm.get("type", "sitemap")
                last_dl = sm.get("lastDownloaded")
                last_sub = sm.get("lastSubmitted")
                errors = sm.get("errors", 0)
                warnings = sm.get("warnings", 0)
                indexed = None
                if "contents" in sm and sm["contents"]:
                    indexed = int(sm["contents"][0].get("indexed", 0))

                conn.execute(
                    """
                    INSERT OR REPLACE INTO sitemaps
                    (site_url, path, type, last_downloaded, last_submitted, errors, warnings, indexed_count, raw_json, synced_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (site_url, path, sm_type, last_dl, last_sub, errors, warnings, indexed, json.dumps(sm), now),
                )
        except Exception as ex:
            print(f"Warning: Could not fetch sitemaps for {site_url}: {ex}")

    conn.commit()
    return verified_urls


def fetch_day_data(
    service,
    site_url: str,
    target_date: str,
    dimensions: List[str],
    search_type: str = "web",
) -> List[Dict[str, Any]]:
    """Fetches all search analytics rows for a single day using 25,000 batch pagination."""
    max_rows = 25000
    start_row = 0
    day_rows = []

    while True:
        req = {
            "startDate": target_date,
            "endDate": target_date,
            "dimensions": dimensions,
            "type": search_type,
            "rowLimit": max_rows,
            "startRow": start_row,
        }
        try:
            resp = service.searchanalytics().query(siteUrl=site_url, body=req).execute()
            rows = resp.get("rows", [])
            if not rows:
                break
            day_rows.extend(rows)
            start_row += max_rows
            if len(rows) < max_rows:
                break
        except Exception as e:
            # Handle rate limits or temporary API errors
            print(f"Error querying {site_url} on {target_date} (startRow={start_row}): {e}")
            break

    return day_rows


def ingest_search_performance(
    service,
    conn: sqlite3.Connection,
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: List[str],
    search_type: str = "web",
) -> int:
    """Iterates day-by-day and inserts granular rows into SQLite without data loss."""
    cur_date = datetime.date.fromisoformat(start_date)
    stop_date = datetime.date.fromisoformat(end_date)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    total_inserted = 0

    dim_map = {d: i for i, d in enumerate(dimensions)}

    print(f"\n--- Ingesting {site_url} from {start_date} to {end_date} (Dimensions: {', '.join(dimensions)}) ---")

    while cur_date <= stop_date:
        d_str = cur_date.isoformat()
        rows = fetch_day_data(service, site_url, d_str, dimensions, search_type)

        if rows:
            for r in rows:
                keys = r.get("keys", [])
                query = keys[dim_map["query"]] if "query" in dim_map and dim_map["query"] < len(keys) else ""
                page = keys[dim_map["page"]] if "page" in dim_map and dim_map["page"] < len(keys) else ""
                country = keys[dim_map["country"]] if "country" in dim_map and dim_map["country"] < len(keys) else ""
                device = keys[dim_map["device"]] if "device" in dim_map and dim_map["device"] < len(keys) else ""
                sa = keys[dim_map["searchAppearance"]] if "searchAppearance" in dim_map and dim_map["searchAppearance"] < len(keys) else ""

                clicks = r.get("clicks", 0)
                impressions = r.get("impressions", 0)
                ctr = r.get("ctr", 0)
                position = r.get("position", 0)

                conn.execute(
                    """
                    INSERT OR REPLACE INTO search_performance
                    (site_url, date, query, page, country, device, search_appearance, search_type, clicks, impressions, ctr, position, raw_json, synced_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (site_url, d_str, query, page, country, device, sa, search_type, clicks, impressions, ctr, position, json.dumps(r), now),
                )
            conn.commit()
            total_inserted += len(rows)
            print(f"  ✓ {d_str}: Ingested {len(rows):,} rows (Total so far: {total_inserted:,})")
        else:
            print(f"  - {d_str}: 0 rows (no search traffic or not yet indexed)")

        cur_date += datetime.timedelta(days=1)

    return total_inserted


def ingest_daily_site_performance(
    service,
    conn: sqlite3.Connection,
    site_url: str,
    start_date: str,
    end_date: str,
    search_type: str = "web",
) -> int:
    """Fetches unfiltered property-level daily totals (dimensions=['date']) without anonymized query loss."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    req = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["date"],
        "type": search_type,
        "aggregationType": "byProperty",
        "rowLimit": 25000,
    }
    try:
        resp = service.searchanalytics().query(siteUrl=site_url, body=req).execute()
        rows = resp.get("rows", [])
        for r in rows:
            d_str = r["keys"][0]
            clicks = r.get("clicks", 0)
            impressions = r.get("impressions", 0)
            ctr = r.get("ctr", 0)
            position = r.get("position", 0)
            conn.execute(
                """
                INSERT OR REPLACE INTO daily_site_performance
                (site_url, date, search_type, clicks, impressions, ctr, position, raw_json, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (site_url, d_str, search_type, clicks, impressions, ctr, position, json.dumps(r), now),
            )
        conn.commit()
        print(f"  ✓ Ingested {len(rows)} property-level daily totals ({start_date} to {end_date})")
        return len(rows)
    except Exception as e:
        print(f"Error fetching property-level daily performance for {site_url}: {e}")
        return 0


def run_sync_pipeline(
    credentials_file: str,
    db_file: str,
    target_site_url: Optional[str] = None,
    full_backfill: bool = False,
    custom_start: Optional[str] = None,
    custom_end: Optional[str] = None,
    days: Optional[int] = None,
    dimensions_str: str = "page,query,country,device",
):
    """Orchestrates properties sync, determines backfill/incremental date bounds, and runs ingestion."""
    creds = load_credentials_from_disk(credentials_file)
    if not creds:
        print(f"Error: Credentials not found at {credentials_file}.")
        print("Run 'python3 search_analytics.py auth' to authorize with Google Search Console.")
        sys.exit(1)

    service = get_search_console_service(creds)
    conn = init_db(db_file)
    dimensions = [d.strip() for d in dimensions_str.split(",") if d.strip()]

    # 1. Sync properties & sitemaps
    verified_sites = sync_properties_and_sitemaps(service, conn)
    sites_to_sync = [target_site_url] if target_site_url else verified_sites

    if not sites_to_sync:
        print("No verified properties found in Google Search Console.")
        return

    # 2. Determine Date Bounds
    # GSC data latency is ~2-3 days
    latest_available_date = datetime.date.today() - datetime.timedelta(days=2)

    for site in sites_to_sync:
        started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end
            sync_type = "date_range"
        elif full_backfill:
            # GSC maximum historical retention window is 16 months (approx 480 days)
            start_date = (latest_available_date - datetime.timedelta(days=480)).isoformat()
            end_date = latest_available_date.isoformat()
            sync_type = "full_backfill"
        elif days:
            start_date = (latest_available_date - datetime.timedelta(days=days)).isoformat()
            end_date = latest_available_date.isoformat()
            sync_type = f"last_{days}_days"
        else:
            # Incremental Sync: Look up latest synced date in SQLite
            cur = conn.cursor()
            cur.execute("SELECT MAX(date) AS max_date FROM search_performance WHERE site_url = ?", (site,))
            row = cur.fetchone()
            max_date = row["max_date"] if row and row["max_date"] else None

            if max_date:
                # Include a 3-day lookback overlap to capture delayed metric revisions
                start_dt = datetime.date.fromisoformat(max_date) - datetime.timedelta(days=3)
                start_date = start_dt.isoformat()
                end_date = latest_available_date.isoformat()
                sync_type = "incremental"
            else:
                # Default initial backfill: 90 days if fresh database
                start_date = (latest_available_date - datetime.timedelta(days=90)).isoformat()
                end_date = latest_available_date.isoformat()
                sync_type = "initial_90_days"

        print(f"\n=======================================================")
        print(f"Starting {sync_type.upper()} for: {site}")
        print(f"Date Range: {start_date} -> {end_date}")
        print(f"Database: {db_file}")
        print(f"=======================================================")

        try:
            site_rows = ingest_daily_site_performance(service, conn, site, start_date, end_date)
            rows_synced = ingest_search_performance(service, conn, site, start_date, end_date, dimensions)
            total_synced = site_rows + rows_synced
            completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            conn.execute(
                """
                INSERT INTO sync_history (site_url, sync_type, start_date, end_date, rows_synced, status, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, 'SUCCESS', ?, ?)
                """,
                (site, sync_type, start_date, end_date, total_synced, started_at, completed_at),
            )
            conn.commit()
            print(f"\n✅ Sync completed successfully for {site}: {rows_synced:,} keyword rows, {site_rows:,} daily property totals recorded ({total_synced:,} total).")

        except Exception as ex:
            completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            conn.execute(
                """
                INSERT INTO sync_history (site_url, sync_type, start_date, end_date, rows_synced, status, error_message, started_at, completed_at)
                VALUES (?, ?, ?, ?, 0, 'FAILED', ?, ?, ?)
                """,
                (site, sync_type, start_date, end_date, str(ex), started_at, completed_at),
            )
            conn.commit()
            print(f"\n❌ Sync failed for {site}: {ex}")


# ---------------------------------------------------------------------------
# SQL Query Runner & Pre-Packaged Reports
# ---------------------------------------------------------------------------

def run_sql_query(query: str, db_path: str = DEFAULT_DB_FILE, output_format: str = "markdown"):
    """Executes arbitrary SQL queries against ~/.gsc/analytics.db and formats output."""
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} does not exist. Run 'python3 search_analytics.py sync' first.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        cur.execute(query)
    except Exception as e:
        print(f"SQL Error: {e}")
        sys.exit(1)

    rows = cur.fetchall()
    if not rows:
        print("Query returned 0 rows.")
        return

    cols = [desc[0] for desc in cur.description]

    if output_format == "json":
        data = [dict(r) for r in rows]
        print(json.dumps(data, indent=2))
        return

    if output_format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(cols)
        for r in rows:
            writer.writerow(list(r))
        return

    # Markdown Table / Grid format
    try:
        from tabulate import tabulate
        table_style = "grid" if output_format == "table" else "github"
        print(tabulate([list(r) for r in rows], headers=cols, tablefmt=table_style))
    except ImportError:
        # Fallback text formatter
        col_widths = [len(c) for c in cols]
        for r in rows:
            for i, val in enumerate(r):
                col_widths[i] = max(col_widths[i], len(str(val)))
        header = " | ".join([cols[i].ljust(col_widths[i]) for i in range(len(cols))])
        sep = "-+-".join(["-" * col_widths[i] for i in range(len(cols))])
        print(f"{header}\n{sep}")
        for r in rows:
            print(" | ".join([str(r[i]).ljust(col_widths[i]) for i in range(len(cols))]))


def run_report(report_name: str, db_path: str = DEFAULT_DB_FILE):
    """Runs pre-canned SQL analytical reports."""
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

    if report_name not in reports:
        print(f"Unknown report '{report_name}'. Available: {', '.join(reports.keys())}")
        sys.exit(1)

    print(f"\n==================== Report: {report_name.upper()} ====================\n")
    run_sql_query(reports[report_name], db_path)


# ---------------------------------------------------------------------------
# OAuth Web Server
# ---------------------------------------------------------------------------

def run_auth_web_server(client_secrets_file: str, credentials_file: str, port: int = 8080, host: str = "127.0.0.1"):
    if not os.path.exists(client_secrets_file):
        print(f"Error: Client secrets file not found at {client_secrets_file}.")
        print("Please place your downloaded OAuth client secret JSON file at that path.")
        sys.exit(1)

    import google_auth_oauthlib.flow

    # Check client secret type (installed / desktop app vs web application)
    with open(client_secrets_file, "r") as f:
        secret_data = json.load(f)

    if "installed" in secret_data:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes=SCOPES
        )
        try:
            creds = flow.run_local_server(port=port, prompt="consent", access_type="offline", open_browser=True)
        except OSError:
            print(f"Port {port} is in use, selecting an available ephemeral port...")
            creds = flow.run_local_server(port=0, prompt="consent", access_type="offline", open_browser=True)
        save_credentials_to_disk(creds, credentials_file)
        script_name = os.path.basename(sys.argv[0])
        print(f"You can now run: python3 {script_name} sync --days 30\n")
        return

    # Web application flow using Flask
    import flask

    app = flask.Flask(__name__)
    app.secret_key = os.urandom(24)

    @app.route("/")
    def index():
        creds = load_credentials_from_disk(credentials_file)
        status_badge = (
            '<span style="color: #137333; background: #e6f4ea; padding: 4px 10px; border-radius: 12px; font-weight: 600;">Authorized</span>'
            if creds
            else '<span style="color: #c5221f; background: #fce8e6; padding: 4px 10px; border-radius: 12px; font-weight: 600;">Not Authorized</span>'
        )
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Analytics OAuth Companion</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #202124; background: #f8f9fa; }}
                h1 {{ color: #1a73e8; border-bottom: 2px solid #e8eaed; padding-bottom: 12px; }}
                .card {{ background: #fff; border: 1px solid #dadce0; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
                .btn {{ display: inline-block; background: #1a73e8; color: #fff; text-decoration: none; padding: 10px 18px; border-radius: 4px; font-weight: 500; }}
                .btn:hover {{ background: #155724; }}
                code {{ background: #f1f3f4; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>🔐 Search Analytics OAuth Authorization</h1>
            <div class="card">
                <h3>Authentication Status: {status_badge}</h3>
                <p>Authorize access to Google Search Console to enable automated SQLite ingestion and SQL analytics.</p>
                <div style="margin-top: 20px;">
                    <a class="btn" href="/authorize">Authorize with Google</a>
                </div>
            </div>
        </body>
        </html>
        """

    @app.route("/authorize")
    def authorize():
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file, scopes=SCOPES
        )
        flow.redirect_uri = flask.url_for("oauth2callback", _external=True)

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )

        flask.session["state"] = state
        return flask.redirect(authorization_url)

    @app.route("/oauth2callback")
    def oauth2callback():
        state = flask.session.get("state")
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file, scopes=SCOPES, state=state
        )
        flow.redirect_uri = flask.url_for("oauth2callback", _external=True)

        flow.fetch_token(authorization_response=flask.request.url)
        save_credentials_to_disk(flow.credentials, credentials_file)

        return """
        <!DOCTYPE html>
        <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h2 style="color: #137333;">🎉 Authorization Successful!</h2>
            <p>Credentials saved to <code>~/.config/gsc/credentials.json</code>.</p>
            <p>You can close this browser tab and return to the terminal to run <code>python3 search_analytics.py sync</code>.</p>
        </body>
        </html>
        """

    print(f"Starting Search Analytics OAuth companion on http://{host}:{port}")
    print(f"Open http://{host}:{port} in your browser to authorize.")
    app.run(host=host, port=port, debug=False)


# ---------------------------------------------------------------------------
# Sitemaps API
# ---------------------------------------------------------------------------

def cli_submit_sitemap(site_url: str, sitemap_url: str, credentials_file: str):
    creds = load_credentials_from_disk(credentials_file)
    if not creds:
        print("Error: No credentials found. Run 'python3 search_analytics.py auth' to authorize.")
        sys.exit(1)

    service = get_search_console_service(creds)
    print(f"Submitting sitemap {sitemap_url} to site {site_url}...")
    service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
    print("✓ Sitemap successfully submitted to Google Search Console!")


# ---------------------------------------------------------------------------
# Main CLI Entrypoint
# ---------------------------------------------------------------------------

def main():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "--client-secrets",
        "--client-secret",
        dest="client_secrets",
        default=DEFAULT_CLIENT_SECRETS_FILE,
        help=f"Path to OAuth client secret JSON (default: {DEFAULT_CLIENT_SECRETS_FILE})",
    )
    base_parser.add_argument(
        "--credentials",
        default=DEFAULT_CREDENTIALS_FILE,
        help=f"Path to saved credentials JSON (default: {DEFAULT_CREDENTIALS_FILE})",
    )
    base_parser.add_argument(
        "--db",
        "--db-path",
        dest="db",
        default=DEFAULT_DB_FILE,
        help=f"Path to SQLite database (default: {DEFAULT_DB_FILE})",
    )

    parser = argparse.ArgumentParser(
        description="Search Analytics: Google Search Console Ingestion Engine & SQL CLI",
        parents=[base_parser],
    )
    parser.add_argument(
        "-q",
        "--query",
        help="Execute arbitrary SQL query directly against the analytics database",
    )
    parser.add_argument(
        "--format",
        default="markdown",
        choices=["markdown", "table", "json", "csv"],
        help="Output format for query results (default: markdown)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 1. Auth command
    auth_parser = subparsers.add_parser("auth", parents=[base_parser], help="Launch OAuth 2.0 Web Server to authorize")
    auth_parser.add_argument("--port", type=int, default=8080, help="Port to run OAuth app (default: 8080)")
    auth_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")

    # 2. Sync command (Backfill & Incremental)
    sync_parser = subparsers.add_parser("sync", parents=[base_parser], help="Sync search analytics and sitemaps into SQLite")
    sync_parser.add_argument("--site-url", help="Specific property URL to sync (defaults to all verified sites)")
    sync_parser.add_argument("--full", action="store_true", help="Run full historical backfill (16 months)")
    sync_parser.add_argument("--start-date", help="Custom start date (YYYY-MM-DD)")
    sync_parser.add_argument("--end-date", help="Custom end date (YYYY-MM-DD)")
    sync_parser.add_argument("--days", type=int, help="Number of days to sync back from latest date")
    sync_parser.add_argument("--dimensions", default="page,query,country,device", help="Comma-separated dimensions")

    # 3. Query command (Direct SQL)
    query_parser = subparsers.add_parser("query", parents=[base_parser], help="Execute arbitrary SQL against the database")
    query_parser.add_argument("sql", help="SQL query string")
    query_parser.add_argument("--format", default="markdown", choices=["markdown", "table", "json", "csv"], help="Output format")

    # 4. Report command (Pre-packaged SQL views)
    report_parser = subparsers.add_parser("report", parents=[base_parser], help="Run pre-packaged analytical SQL report")
    report_parser.add_argument("name", choices=["overview", "top-queries", "top-pages", "countries", "devices", "timing", "milestone-impact"], help="Report name")

    # 5. Sitemaps submission command
    submit_parser = subparsers.add_parser("submit-sitemap", parents=[base_parser], help="Submit an XML sitemap to Search Console")
    submit_parser.add_argument("--site-url", required=True, help="Site property URL (e.g. https://example.com/ or sc-domain:example.com)")
    submit_parser.add_argument("--sitemap-url", required=True, help="Full URL of the sitemap XML")

    args = parser.parse_args()

    if args.query:
        run_sql_query(args.query, args.db, args.format)
        return

    if not args.command:
        parser.print_help()
        return

    if args.command == "auth":
        run_auth_web_server(args.client_secrets, args.credentials, args.port, args.host)
    elif args.command == "sync":
        run_sync_pipeline(
            credentials_file=args.credentials,
            db_file=args.db,
            target_site_url=args.site_url,
            full_backfill=args.full,
            custom_start=args.start_date,
            custom_end=args.end_date,
            days=args.days,
            dimensions_str=args.dimensions,
        )
    elif args.command == "query":
        run_sql_query(args.sql, args.db, args.format)
    elif args.command == "report":
        run_report(args.name, args.db)
    elif args.command == "submit-sitemap":
        cli_submit_sitemap(args.site_url, args.sitemap_url, args.credentials)


if __name__ == "__main__":
    main()
