#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-analytics-data>=0.18.0",
#     "google-analytics-admin>=0.22.0",
#     "google-auth>=2.28.0",
#     "tabulate>=0.9.0",
# ]
# ///
"""
Google Analytics 4 SQLite Ingestion Engine & SQL Analytics CLI.

Ingests raw GA4 performance data, traffic sources, page metrics, events, and outbound clicks
into a local SQLite database (e.g. google_analytics.db) without data loss, supporting:
- ADC (Application Default Credentials) authentication via Google Cloud
- Property auto-discovery via GA4 Admin API
- Full historical backfill (up to GA4 property creation / 14 months)
- Robust incremental sync with lookback refresh
- Raw JSON payload retention on all records
- Direct SQL querying and pre-packaged analytical views

Usage:
  # 1. List accessible GA4 accounts and properties
  python3 scripts/google_analytics.py properties

  # 2. Incremental Sync (Newest days + 3-day lookback refresh)
  python3 scripts/google_analytics.py sync

  # 3. Full Historical Backfill
  python3 scripts/google_analytics.py sync --full

  # 4. Specific Date Range Sync
  python3 scripts/google_analytics.py sync --start-date 2026-06-01 --end-date 2026-08-15

  # 5. Execute Arbitrary SQL Query
  python3 scripts/google_analytics.py query "SELECT page_path, SUM(views), ROUND(AVG(avg_dwell_sec),1) FROM v_page_performance GROUP BY page_path ORDER BY SUM(views) DESC LIMIT 10"

  # 6. Run Pre-Built Reports
  python3 scripts/google_analytics.py report overview
  python3 scripts/google_analytics.py report top-pages
  python3 scripts/google_analytics.py report channels
  python3 scripts/google_analytics.py report geo
  python3 scripts/google_analytics.py report recurring
  python3 scripts/google_analytics.py report events
  python3 scripts/google_analytics.py report outbound
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

# Optional tabulate for terminal tables
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

# Google Analytics & Auth Libraries
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy,
    FilterExpression,
    Filter
)
from google.analytics.admin_v1beta import AnalyticsAdminServiceClient

DEFAULT_DB_FILE = "google_analytics.db"
DEFAULT_PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "")


def ensure_dirs(db_path: str = DEFAULT_DB_FILE):
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


# ---------------------------------------------------------------------------
# Database Schema & Migrations
# ---------------------------------------------------------------------------

SCHEMA_DDL = """
-- Properties Metadata
CREATE TABLE IF NOT EXISTS properties (
    property_id TEXT PRIMARY KEY,
    name TEXT,
    account_id TEXT,
    display_name TEXT,
    industry_category TEXT,
    time_zone TEXT,
    currency_code TEXT,
    service_level TEXT,
    create_time TEXT,
    update_time TEXT,
    raw_json TEXT,
    last_synced_at TEXT DEFAULT (datetime('now'))
);

-- Daily Page Metrics
CREATE TABLE IF NOT EXISTS daily_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    date TEXT NOT NULL,
    page_path TEXT NOT NULL,
    page_title TEXT,
    country TEXT,
    device_category TEXT,
    source_medium TEXT,
    screen_page_views INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    sessions INTEGER DEFAULT 0,
    user_engagement_duration REAL DEFAULT 0.0,
    bounce_rate REAL DEFAULT 0.0,
    raw_json TEXT,
    synced_at TEXT DEFAULT (datetime('now')),
    UNIQUE (property_id, date, page_path, country, device_category, source_medium)
);

-- Daily Traffic Sources & Channels
CREATE TABLE IF NOT EXISTS daily_traffic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    date TEXT NOT NULL,
    session_source_medium TEXT NOT NULL,
    session_default_channel_group TEXT,
    country TEXT,
    device_category TEXT,
    sessions INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    engaged_sessions INTEGER DEFAULT 0,
    user_engagement_duration REAL DEFAULT 0.0,
    bounce_rate REAL DEFAULT 0.0,
    raw_json TEXT,
    synced_at TEXT DEFAULT (datetime('now')),
    UNIQUE (property_id, date, session_source_medium, session_default_channel_group, country, device_category)
);

-- Daily Events (e.g. scroll, click, first_visit, form_submit)
CREATE TABLE IF NOT EXISTS daily_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    date TEXT NOT NULL,
    event_name TEXT NOT NULL,
    page_path TEXT,
    country TEXT,
    device_category TEXT,
    event_count INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    raw_json TEXT,
    synced_at TEXT DEFAULT (datetime('now')),
    UNIQUE (property_id, date, event_name, page_path, country, device_category)
);

-- Outbound Link Clicks
CREATE TABLE IF NOT EXISTS outbound_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    date TEXT NOT NULL,
    link_url TEXT NOT NULL,
    page_path TEXT,
    country TEXT,
    event_count INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    raw_json TEXT,
    synced_at TEXT DEFAULT (datetime('now')),
    UNIQUE (property_id, date, link_url, page_path, country)
);

-- Sync History Audit Log
CREATE TABLE IF NOT EXISTS sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id TEXT NOT NULL,
    sync_type TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    pages_synced INTEGER DEFAULT 0,
    traffic_synced INTEGER DEFAULT 0,
    events_synced INTEGER DEFAULT 0,
    outbound_synced INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT DEFAULT (datetime('now'))
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_pages_date ON daily_pages(date);
CREATE INDEX IF NOT EXISTS idx_pages_path ON daily_pages(page_path);
CREATE INDEX IF NOT EXISTS idx_pages_country ON daily_pages(country);
CREATE INDEX IF NOT EXISTS idx_traffic_date ON daily_traffic(date);
CREATE INDEX IF NOT EXISTS idx_traffic_channel ON daily_traffic(session_default_channel_group);
CREATE INDEX IF NOT EXISTS idx_events_name ON daily_events(event_name);
CREATE INDEX IF NOT EXISTS idx_events_date ON daily_events(date);
CREATE INDEX IF NOT EXISTS idx_outbound_url ON outbound_clicks(link_url);

-- Analytical Views
DROP VIEW IF EXISTS v_daily_summary;
CREATE VIEW v_daily_summary AS
SELECT 
    date,
    SUM(sessions) AS total_sessions,
    SUM(active_users) AS total_active_users,
    SUM(screen_page_views) AS total_page_views,
    ROUND(SUM(user_engagement_duration) / 60.0, 1) AS total_engagement_min,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_pct
FROM daily_pages
GROUP BY date
ORDER BY date DESC;

DROP VIEW IF EXISTS v_page_performance;
CREATE VIEW v_page_performance AS
SELECT 
    page_path,
    MAX(page_title) AS page_title,
    CASE 
        WHEN page_path LIKE '/pt-br/%' THEN 'Portuguese (/pt-br/)'
        WHEN page_path LIKE '/ja/%' THEN 'Japanese (/ja/)'
        ELSE 'English (Default /)'
    END AS localization,
    SUM(screen_page_views) AS total_views,
    SUM(active_users) AS total_users,
    SUM(sessions) AS total_sessions,
    ROUND(SUM(user_engagement_duration) / MAX(SUM(active_users), 1), 1) AS avg_dwell_sec,
    ROUND(SUM(user_engagement_duration) / 60.0, 1) AS total_dwell_min,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_pct
FROM daily_pages
GROUP BY page_path
ORDER BY total_views DESC;

DROP VIEW IF EXISTS v_channel_performance;
CREATE VIEW v_channel_performance AS
SELECT 
    session_default_channel_group AS channel_group,
    session_source_medium AS source_medium,
    SUM(sessions) AS total_sessions,
    SUM(active_users) AS total_users,
    SUM(new_users) AS total_new_users,
    SUM(engaged_sessions) AS total_engaged_sessions,
    ROUND((SUM(engaged_sessions) * 100.0) / MAX(SUM(sessions), 1), 1) AS engagement_rate_pct,
    ROUND(SUM(user_engagement_duration) / 60.0, 1) AS total_dwell_min,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_pct
FROM daily_traffic
GROUP BY session_default_channel_group, session_source_medium
ORDER BY total_sessions DESC;

DROP VIEW IF EXISTS v_geo_breakdown;
CREATE VIEW v_geo_breakdown AS
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
ORDER BY total_sessions DESC;

DROP VIEW IF EXISTS v_events_summary;
CREATE VIEW v_events_summary AS
SELECT 
    event_name,
    SUM(event_count) AS total_events,
    SUM(total_users) AS total_users
FROM daily_events
GROUP BY event_name
ORDER BY total_events DESC;

DROP VIEW IF EXISTS v_outbound_links;
CREATE VIEW v_outbound_links AS
SELECT 
    link_url,
    SUM(event_count) AS total_clicks,
    SUM(total_users) AS total_users,
    COUNT(DISTINCT page_path) AS referring_pages_count
FROM outbound_clicks
WHERE link_url IS NOT NULL AND link_url != ''
GROUP BY link_url
ORDER BY total_clicks DESC;
"""


def init_db(db_path: str = DEFAULT_DB_FILE) -> sqlite3.Connection:
    ensure_dirs(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_DDL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Authentication & Clients
# ---------------------------------------------------------------------------

def get_clients() -> Tuple[BetaAnalyticsDataClient, AnalyticsAdminServiceClient]:
    """Resolves credentials via ADC and returns Data & Admin clients."""
    try:
        credentials, project = default(scopes=[
            "https://www.googleapis.com/auth/analytics.readonly",
            "https://www.googleapis.com/auth/cloud-platform"
        ])
        data_client = BetaAnalyticsDataClient(credentials=credentials)
        admin_client = AnalyticsAdminServiceClient(credentials=credentials)
        return data_client, admin_client
    except DefaultCredentialsError as e:
        print(f"❌ Error initializing Google Credentials: {e}", file=sys.stderr)
        print("💡 Run 'gcloud auth application-default login --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform'", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Property Management
# ---------------------------------------------------------------------------

def list_properties(admin_client: AnalyticsAdminServiceClient, db_path: str = DEFAULT_DB_FILE):
    """Lists all accessible GA4 accounts and properties."""
    print("🔍 Fetching accessible Google Analytics 4 accounts and properties...\n")
    conn = init_db(db_path)
    
    try:
        accounts = admin_client.list_account_summaries()
        rows = []
        for acc in accounts:
            acc_id = acc.account.split('/')[-1]
            acc_name = acc.display_name
            for prop in acc.property_summaries:
                p_id = prop.property.split('/')[-1]
                p_name = prop.display_name
                rows.append([p_id, p_name, acc_id, acc_name])
                
                conn.execute("""
                    INSERT INTO properties (property_id, name, account_id, display_name, raw_json)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(property_id) DO UPDATE SET
                        name = excluded.name,
                        account_id = excluded.account_id,
                        display_name = excluded.display_name,
                        last_synced_at = datetime('now');
                """, (p_id, prop.property, acc_id, p_name, json.dumps({
                    "property": prop.property,
                    "display_name": p_name,
                    "account": acc.account,
                    "account_display_name": acc_name
                })))
        conn.commit()
        
        if HAS_TABULATE:
            print(tabulate(rows, headers=["Property ID", "Property Name", "Account ID", "Account Name"], tablefmt="grid"))
        else:
            print(f"{'Property ID':<15} | {'Property Name':<30} | {'Account ID':<15} | {'Account Name'}")
            print("-" * 80)
            for r in rows:
                print(f"{r[0]:<15} | {r[1]:<30} | {r[2]:<15} | {r[3]}")
    except Exception as e:
        print(f"❌ Failed to list properties: {e}", file=sys.stderr)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Data Ingestion Engine
# ---------------------------------------------------------------------------

def sync_property_metadata(admin_client: AnalyticsAdminServiceClient, conn: sqlite3.Connection, property_id: str):
    """Syncs detailed property metadata."""
    try:
        p_name = f"properties/{property_id}"
        details = admin_client.get_property(name=p_name)
        raw = {
            "name": details.name,
            "display_name": details.display_name,
            "industry_category": str(details.industry_category),
            "time_zone": details.time_zone,
            "currency_code": details.currency_code,
            "service_level": str(details.service_level),
            "create_time": details.create_time.isoformat() if details.create_time else None,
            "update_time": details.update_time.isoformat() if details.update_time else None,
        }
        conn.execute("""
            INSERT INTO properties (
                property_id, name, account_id, display_name, industry_category,
                time_zone, currency_code, service_level, create_time, update_time, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(property_id) DO UPDATE SET
                display_name = excluded.display_name,
                industry_category = excluded.industry_category,
                time_zone = excluded.time_zone,
                currency_code = excluded.currency_code,
                service_level = excluded.service_level,
                create_time = excluded.create_time,
                update_time = excluded.update_time,
                raw_json = excluded.raw_json,
                last_synced_at = datetime('now');
        """, (
            property_id, details.name, details.parent.split('/')[-1] if details.parent else None,
            details.display_name, str(details.industry_category), details.time_zone,
            details.currency_code, str(details.service_level),
            details.create_time.isoformat() if details.create_time else None,
            details.update_time.isoformat() if details.update_time else None,
            json.dumps(raw)
        ))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch detailed property metadata: {e}")


def ingest_daily_pages(data_client: BetaAnalyticsDataClient, conn: sqlite3.Connection, property_id: str, start_date: str, end_date: str) -> int:
    """Ingests daily page performance breakdowns."""
    p_name = f"properties/{property_id}"
    req = RunReportRequest(
        property=p_name,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="pagePath"),
            Dimension(name="pageTitle"),
            Dimension(name="country"),
            Dimension(name="deviceCategory"),
            Dimension(name="sessionSourceMedium")
        ],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="userEngagementDuration"),
            Metric(name="bounceRate")
        ],
        limit=100000
    )
    
    resp = data_client.run_report(req)
    count = 0
    
    for r in resp.rows:
        date_str = r.dimension_values[0].value
        if len(date_str) == 8 and "-" not in date_str:
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        else:
            date_fmt = date_str
            
        page_path = r.dimension_values[1].value
        page_title = r.dimension_values[2].value
        country = r.dimension_values[3].value
        device = r.dimension_values[4].value
        source_med = r.dimension_values[5].value
        
        views = int(float(r.metric_values[0].value))
        users = int(float(r.metric_values[1].value))
        sess = int(float(r.metric_values[2].value))
        dur = float(r.metric_values[3].value)
        bounce = float(r.metric_values[4].value)
        
        raw = {
            "date": date_fmt,
            "page_path": page_path,
            "page_title": page_title,
            "country": country,
            "device": device,
            "source_medium": source_med,
            "views": views,
            "users": users,
            "sessions": sess,
            "engagement_duration": dur,
            "bounce_rate": bounce
        }
        
        conn.execute("""
            INSERT INTO daily_pages (
                property_id, date, page_path, page_title, country, device_category,
                source_medium, screen_page_views, active_users, sessions,
                user_engagement_duration, bounce_rate, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(property_id, date, page_path, country, device_category, source_medium) DO UPDATE SET
                page_title = excluded.page_title,
                screen_page_views = excluded.screen_page_views,
                active_users = excluded.active_users,
                sessions = excluded.sessions,
                user_engagement_duration = excluded.user_engagement_duration,
                bounce_rate = excluded.bounce_rate,
                raw_json = excluded.raw_json,
                synced_at = datetime('now');
        """, (
            property_id, date_fmt, page_path, page_title, country, device,
            source_med, views, users, sess, dur, bounce, json.dumps(raw)
        ))
        count += 1
        
    conn.commit()
    return count


def ingest_daily_traffic(data_client: BetaAnalyticsDataClient, conn: sqlite3.Connection, property_id: str, start_date: str, end_date: str) -> int:
    """Ingests traffic source and channel acquisition data."""
    p_name = f"properties/{property_id}"
    req = RunReportRequest(
        property=p_name,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="sessionSourceMedium"),
            Dimension(name="sessionDefaultChannelGroup"),
            Dimension(name="country"),
            Dimension(name="deviceCategory")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="engagedSessions"),
            Metric(name="userEngagementDuration"),
            Metric(name="bounceRate")
        ],
        limit=100000
    )
    
    resp = data_client.run_report(req)
    count = 0
    
    for r in resp.rows:
        date_str = r.dimension_values[0].value
        if len(date_str) == 8 and "-" not in date_str:
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        else:
            date_fmt = date_str
            
        source_med = r.dimension_values[1].value
        channel = r.dimension_values[2].value
        country = r.dimension_values[3].value
        device = r.dimension_values[4].value
        
        sess = int(float(r.metric_values[0].value))
        users = int(float(r.metric_values[1].value))
        new_users = int(float(r.metric_values[2].value))
        engaged_sess = int(float(r.metric_values[3].value))
        dur = float(r.metric_values[4].value)
        bounce = float(r.metric_values[5].value)
        
        raw = {
            "date": date_fmt,
            "source_medium": source_med,
            "channel_group": channel,
            "country": country,
            "device": device,
            "sessions": sess,
            "active_users": users,
            "new_users": new_users,
            "engaged_sessions": engaged_sess,
            "engagement_duration": dur,
            "bounce_rate": bounce
        }
        
        conn.execute("""
            INSERT INTO daily_traffic (
                property_id, date, session_source_medium, session_default_channel_group,
                country, device_category, sessions, active_users, new_users,
                engaged_sessions, user_engagement_duration, bounce_rate, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(property_id, date, session_source_medium, session_default_channel_group, country, device_category) DO UPDATE SET
                sessions = excluded.sessions,
                active_users = excluded.active_users,
                new_users = excluded.new_users,
                engaged_sessions = excluded.engaged_sessions,
                user_engagement_duration = excluded.user_engagement_duration,
                bounce_rate = excluded.bounce_rate,
                raw_json = excluded.raw_json,
                synced_at = datetime('now');
        """, (
            property_id, date_fmt, source_med, channel, country, device,
            sess, users, new_users, engaged_sess, dur, bounce, json.dumps(raw)
        ))
        count += 1
        
    conn.commit()
    return count


def ingest_daily_events(data_client: BetaAnalyticsDataClient, conn: sqlite3.Connection, property_id: str, start_date: str, end_date: str) -> int:
    """Ingests daily event metrics (scroll, click, page_view, etc.)."""
    p_name = f"properties/{property_id}"
    req = RunReportRequest(
        property=p_name,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="eventName"),
            Dimension(name="pagePath"),
            Dimension(name="country"),
            Dimension(name="deviceCategory")
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers")
        ],
        limit=100000
    )
    
    resp = data_client.run_report(req)
    count = 0
    
    for r in resp.rows:
        date_str = r.dimension_values[0].value
        if len(date_str) == 8 and "-" not in date_str:
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        else:
            date_fmt = date_str
            
        event_name = r.dimension_values[1].value
        page_path = r.dimension_values[2].value
        country = r.dimension_values[3].value
        device = r.dimension_values[4].value
        
        event_count = int(float(r.metric_values[0].value))
        users = int(float(r.metric_values[1].value))
        
        raw = {
            "date": date_fmt,
            "event_name": event_name,
            "page_path": page_path,
            "country": country,
            "device": device,
            "event_count": event_count,
            "total_users": users
        }
        
        conn.execute("""
            INSERT INTO daily_events (
                property_id, date, event_name, page_path, country, device_category,
                event_count, total_users, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(property_id, date, event_name, page_path, country, device_category) DO UPDATE SET
                event_count = excluded.event_count,
                total_users = excluded.total_users,
                raw_json = excluded.raw_json,
                synced_at = datetime('now');
        """, (
            property_id, date_fmt, event_name, page_path, country, device,
            event_count, users, json.dumps(raw)
        ))
        count += 1
        
    conn.commit()
    return count


def ingest_outbound_clicks(data_client: BetaAnalyticsDataClient, conn: sqlite3.Connection, property_id: str, start_date: str, end_date: str) -> int:
    """Ingests outbound link click destinations."""
    p_name = f"properties/{property_id}"
    req = RunReportRequest(
        property=p_name,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="linkUrl"),
            Dimension(name="pagePath"),
            Dimension(name="country")
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers")
        ],
        limit=50000
    )
    
    resp = data_client.run_report(req)
    count = 0
    
    for r in resp.rows:
        link_url = r.dimension_values[1].value
        if not link_url:
            continue
            
        date_str = r.dimension_values[0].value
        if len(date_str) == 8 and "-" not in date_str:
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        else:
            date_fmt = date_str
            
        page_path = r.dimension_values[2].value
        country = r.dimension_values[3].value
        event_count = int(float(r.metric_values[0].value))
        users = int(float(r.metric_values[1].value))
        
        raw = {
            "date": date_fmt,
            "link_url": link_url,
            "page_path": page_path,
            "country": country,
            "event_count": event_count,
            "total_users": users
        }
        
        conn.execute("""
            INSERT INTO outbound_clicks (
                property_id, date, link_url, page_path, country,
                event_count, total_users, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(property_id, date, link_url, page_path, country) DO UPDATE SET
                event_count = excluded.event_count,
                total_users = excluded.total_users,
                raw_json = excluded.raw_json,
                synced_at = datetime('now');
        """, (
            property_id, date_fmt, link_url, page_path, country,
            event_count, users, json.dumps(raw)
        ))
        count += 1
        
    conn.commit()
    return count


def run_sync(
    property_id: str = DEFAULT_PROPERTY_ID,
    days: Optional[int] = None,
    full: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: str = DEFAULT_DB_FILE
):
    if not property_id:
        print("Error: No GA4 Property ID provided.", file=sys.stderr)
        print("Set the GA4_PROPERTY_ID environment variable or pass --property-id <ID>.", file=sys.stderr)
        print("Tip: Run 'python3 scripts/google_analytics.py properties' to list all accessible GA4 properties.", file=sys.stderr)
        sys.exit(1)

    data_client, admin_client = get_clients()
    conn = init_db(db_path)
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    sync_property_metadata(admin_client, conn, property_id)
    
    # Calculate Date Range
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    if start_date and end_date:
        s_date = start_date
        e_date = end_date
        sync_type = "custom_range"
    elif full:
        s_date = (today - datetime.timedelta(days=420)).strftime("%Y-%m-%d")
        e_date = yesterday.strftime("%Y-%m-%d")
        sync_type = "full_backfill"
    elif days:
        s_date = (today - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        e_date = yesterday.strftime("%Y-%m-%d")
        sync_type = f"last_{days}_days"
    else:
        cur = conn.cursor()
        cur.execute("SELECT MAX(date) FROM daily_pages WHERE property_id = ?", (property_id,))
        max_date = cur.fetchone()[0]
        if max_date:
            last_d = datetime.date.fromisoformat(max_date) - datetime.timedelta(days=3)
            s_date = last_d.strftime("%Y-%m-%d")
            sync_type = "incremental"
        else:
            s_date = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
            sync_type = "initial_90_days"
        e_date = yesterday.strftime("%Y-%m-%d")
        
    print(f"🚀 Starting GA4 Ingestion Sync for Property: {property_id}")
    print(f"   Mode:       {sync_type}")
    print(f"   Date Range: {s_date} -> {e_date}")
    print(f"   Database:   {os.path.abspath(db_path)}\n")
    
    try:
        t0 = time.time()
        print("⏳ [1/4] Syncing daily page metrics...")
        p_count = ingest_daily_pages(data_client, conn, property_id, s_date, e_date)
        print(f"   ✅ Ingested {p_count:,} page metric records")
        
        print("⏳ [2/4] Syncing traffic & channel acquisition...")
        t_count = ingest_daily_traffic(data_client, conn, property_id, s_date, e_date)
        print(f"   ✅ Ingested {t_count:,} traffic source records")
        
        print("⏳ [3/4] Syncing user interaction events...")
        e_count = ingest_daily_events(data_client, conn, property_id, s_date, e_date)
        print(f"   ✅ Ingested {e_count:,} event records")
        
        print("⏳ [4/4] Syncing outbound link clicks...")
        o_count = ingest_outbound_clicks(data_client, conn, property_id, s_date, e_date)
        print(f"   ✅ Ingested {o_count:,} outbound click records")
        
        elapsed = time.time() - t0
        
        conn.execute("""
            INSERT INTO sync_history (
                property_id, sync_type, start_date, end_date,
                pages_synced, traffic_synced, events_synced, outbound_synced,
                status, started_at, finished_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'SUCCESS', ?, datetime('now'))
        """, (property_id, sync_type, s_date, e_date, p_count, t_count, e_count, o_count, started_at))
        conn.commit()
        
        print(f"\n🎉 Sync completed in {elapsed:.2f}s! Total records synced: {p_count + t_count + e_count + o_count:,}")
    except Exception as e:
        print(f"\n❌ Sync failed: {e}", file=sys.stderr)
        conn.execute("""
            INSERT INTO sync_history (
                property_id, sync_type, start_date, end_date,
                status, error_message, started_at, finished_at
            ) VALUES (?, ?, ?, ?, 'FAILED', ?, ?, datetime('now'))
        """, (property_id, sync_type, s_date, e_date, str(e), started_at))
        conn.commit()
        sys.exit(1)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Pre-Built SQL Reports
# ---------------------------------------------------------------------------

def run_report(report_name: str, db_path: str = DEFAULT_DB_FILE):
    """Executes pre-built analytical reports."""
    conn = init_db(db_path)
    cur = conn.cursor()
    
    if report_name == "overview":
        print("\n================================================================================")
        print("  📊 GOOGLE ANALYTICS 4: SITE OVERVIEW & RECENT TRENDS")
        print("================================================================================\n")
        
        cur.execute("""
            SELECT 
                COUNT(DISTINCT date) AS active_days,
                MIN(date) AS first_date,
                MAX(date) AS last_date,
                SUM(sessions) AS total_sessions,
                SUM(active_users) AS total_active_users,
                SUM(screen_page_views) AS total_page_views,
                ROUND(SUM(user_engagement_duration)/60.0, 1) AS total_engagement_min,
                ROUND(AVG(bounce_rate)*100, 1) AS avg_bounce_pct
            FROM daily_pages;
        """)
        r = cur.fetchone()
        if not r or not r[0]:
            print("❌ No data found in database. Run 'sync' first.")
            return
            
        print(f"  Coverage:               {r[1]} to {r[2]} ({r[0]} days)")
        print(f"  Total Sessions:         {r[3]:,}")
        print(f"  Active Users:           {r[4]:,}")
        print(f"  Page Views:             {r[5]:,}")
        print(f"  Pages / Session:        {r[5]/max(r[3],1):.2f}")
        print(f"  Total Engagement:       {r[6]:,} minutes ({r[6]/60:.1f} hours)")
        print(f"  Avg Active Dwell/User:  {(r[6]*60)/max(r[4],1):.1f}s")
        print(f"  Avg Bounce Rate:        {r[7]}%\n")
        
        print("--- Last 7 Days Daily Performance ---")
        cur.execute("""
            SELECT date, total_sessions, total_active_users, total_page_views, total_engagement_min, avg_bounce_pct
            FROM v_daily_summary
            LIMIT 7;
        """)
        rows = cur.fetchall()
        headers = ["Date", "Sessions", "Users", "PageViews", "Dwell (Min)", "Bounce %"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)

    elif report_name == "top-pages":
        print("\n================================================================================")
        print("  📄 TOP LANDING PAGES & ARTICLE ENGAGEMENT")
        print("================================================================================\n")
        cur.execute("""
            SELECT 
                page_path,
                localization,
                total_views,
                total_users,
                total_sessions,
                avg_dwell_sec || 's' AS avg_dwell,
                avg_bounce_pct || '%' AS bounce_pct
            FROM v_page_performance
            LIMIT 20;
        """)
        rows = cur.fetchall()
        headers = ["Page Path", "Localization", "Views", "Users", "Sessions", "Avg Dwell", "Bounce %"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)

    elif report_name == "channels":
        print("\n================================================================================")
        print("  🌐 TRAFFIC SOURCES & ACQUISITION CHANNELS")
        print("================================================================================\n")
        cur.execute("""
            SELECT 
                channel_group,
                source_medium,
                total_sessions,
                total_users,
                total_new_users,
                engagement_rate_pct || '%' AS eng_rate,
                total_dwell_min || 'm' AS dwell_min
            FROM v_channel_performance
            LIMIT 15;
        """)
        rows = cur.fetchall()
        headers = ["Channel Group", "Source / Medium", "Sessions", "Users", "New Users", "Eng Rate", "Total Dwell"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)

    elif report_name == "geo":
        print("\n================================================================================")
        print("  🌍 GEOGRAPHICAL DISTRIBUTION & DWELL TIME")
        print("================================================================================\n")
        cur.execute("""
            SELECT 
                country,
                total_sessions,
                total_users,
                total_page_views,
                avg_dwell_sec || 's' AS avg_dwell,
                avg_bounce_pct || '%' AS bounce_pct
            FROM v_geo_breakdown
            LIMIT 20;
        """)
        rows = cur.fetchall()
        headers = ["Country", "Sessions", "Users", "PageViews", "Avg Dwell", "Bounce %"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)

    elif report_name == "events":
        print("\n================================================================================")
        print("  🎯 USER ENGAGEMENT EVENTS BREAKDOWN")
        print("================================================================================\n")
        cur.execute("""
            SELECT event_name, total_events, total_users
            FROM v_events_summary
            LIMIT 20;
        """)
        rows = cur.fetchall()
        headers = ["Event Name", "Total Events", "Users Triggering"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)

    elif report_name == "outbound":
        print("\n================================================================================")
        print("  ↗️ OUTBOUND LINK DESTINATIONS")
        print("================================================================================\n")
        cur.execute("""
            SELECT link_url, total_clicks, total_users, referring_pages_count
            FROM v_outbound_links
            LIMIT 20;
        """)
        rows = cur.fetchall()
        headers = ["Outbound Destination URL", "Clicks", "Users", "Source Pages"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)

    elif report_name == "recurring":
        print("\n================================================================================")
        print("  🔄 RECURRING AUDIENCE & RETENTION PROFILE")
        print("================================================================================\n")
        cur.execute("""
            SELECT 
                CASE 
                    WHEN total_sessions > total_new_users THEN 'Returning Traffic'
                    ELSE 'New Traffic'
                END AS traffic_type,
                SUM(total_sessions) AS sessions,
                SUM(total_users) AS users,
                SUM(total_new_users) AS new_users,
                ROUND(AVG(engagement_rate_pct), 1) || '%' AS avg_eng_rate,
                ROUND(SUM(total_dwell_min), 1) || 'm' AS dwell_time
            FROM v_channel_performance
            GROUP BY traffic_type;
        """)
        rows = cur.fetchall()
        headers = ["Audience Type", "Sessions", "Users", "New Users", "Avg Eng Rate", "Dwell Time"]
        if HAS_TABULATE:
            print(tabulate(rows, headers=headers, tablefmt="simple"))
        else:
            for row in rows:
                print(row)
    else:
        print(f"❌ Unknown report name: {report_name}. Valid choices: overview, top-pages, channels, geo, events, outbound, recurring")

    conn.close()


# ---------------------------------------------------------------------------
# Ad-Hoc SQL Query Runner
# ---------------------------------------------------------------------------

def run_query(sql: str, db_path: str = DEFAULT_DB_FILE, output_json: bool = False, output_csv: bool = False):
    """Executes arbitrary SQL query against the analytics database."""
    conn = init_db(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        
        if output_json:
            result = [dict(zip(cols, row)) for row in rows]
            print(json.dumps(result, indent=2))
        elif output_csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(cols)
            writer.writerows(rows)
        else:
            if HAS_TABULATE:
                print(tabulate(rows, headers=cols, tablefmt="grid"))
            else:
                print(" | ".join(cols))
                print("-" * (len(" | ".join(cols))))
                for r in rows:
                    print(" | ".join(str(x) for x in r))
            print(f"\n({len(rows)} rows)")
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main CLI Entrypoint
# ---------------------------------------------------------------------------

def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--db-path", default=DEFAULT_DB_FILE, help=f"Path to SQLite database (default: {DEFAULT_DB_FILE})")
    parent_parser.add_argument("--property-id", default=DEFAULT_PROPERTY_ID, help=f"GA4 Property ID (default: {DEFAULT_PROPERTY_ID})")
    
    parser = argparse.ArgumentParser(
        description="Google Analytics 4 Ingestion Engine & SQL Analytics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parent_parser],
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcommand: properties
    subparsers.add_parser("properties", parents=[parent_parser], help="List all accessible GA4 accounts and properties")
    
    # Subcommand: sync
    sync_p = subparsers.add_parser("sync", parents=[parent_parser], help="Ingest raw GA4 data into SQLite database")
    sync_p.add_argument("--days", type=int, help="Number of trailing days to sync")
    sync_p.add_argument("--full", action="store_true", help="Perform full historical backfill (up to 14 months)")
    sync_p.add_argument("--start-date", help="Custom start date (YYYY-MM-DD)")
    sync_p.add_argument("--end-date", help="Custom end date (YYYY-MM-DD)")
    
    # Subcommand: report
    report_p = subparsers.add_parser("report", parents=[parent_parser], help="Run pre-built analytical reports")
    report_p.add_argument("name", choices=["overview", "top-pages", "channels", "geo", "events", "outbound", "recurring"], help="Report name")
    
    # Subcommand: query
    query_p = subparsers.add_parser("query", parents=[parent_parser], help="Execute arbitrary SQL against the database")
    query_p.add_argument("sql", help="SQL query to execute")
    query_p.add_argument("--json", action="store_true", help="Output results in JSON format")
    query_p.add_argument("--csv", action="store_true", help="Output results in CSV format")
    
    args = parser.parse_args()
    
    if args.command == "properties":
        _, admin_client = get_clients()
        list_properties(admin_client, args.db_path)
    elif args.command == "sync":
        run_sync(
            property_id=args.property_id,
            days=args.days,
            full=args.full,
            start_date=args.start_date,
            end_date=args.end_date,
            db_path=args.db_path
        )
    elif args.command == "report":
        run_report(args.name, args.db_path)
    elif args.command == "query":
        run_query(args.sql, args.db_path, args.json, args.csv)


if __name__ == "__main__":
    main()
