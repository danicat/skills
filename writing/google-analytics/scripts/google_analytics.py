#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-analytics-data>=0.18.0",
#     "google-analytics-admin>=0.22.0",
#     "google-auth>=2.28.0",
#     "google-auth-oauthlib>=1.2.0",
#     "requests>=2.31.0",
#     "tabulate>=0.9.0",
# ]
# ///
"""
Google Analytics 4 SQLite Ingestion Engine & SQL Analytics CLI.

Ingests raw GA4 performance data, traffic sources, page metrics, events, and outbound clicks
into a local SQLite database (e.g. google_analytics.db) without data loss, supporting:
- Multi-tier Authentication: OAuth 2.0 Client Credentials, Service Accounts, and ADC
- Property auto-discovery via GA4 Admin API
- Cloud Reporting Data Annotations (marking site deployments/milestones in GA4 charts)
- Full historical backfill (up to GA4 property creation / 14 months)
- Robust incremental sync with lookback refresh
- Raw JSON payload retention on all records
- Direct SQL querying, milestone impact comparison views, and pre-packaged analytical reports

Usage:
  # 1. Authorize OAuth 2.0 (with analytics.edit & readonly scopes)
  python3 scripts/google_analytics.py auth

  # 2. Discover accessible GA4 accounts and properties
  python3 scripts/google_analytics.py properties

  # 3. Incremental Sync (Newest days + 3-day lookback refresh)
  python3 scripts/google_analytics.py sync

  # 4. Full Historical Backfill
  python3 scripts/google_analytics.py sync --full

  # 5. Add Deployment / Release Milestone (Cloud Annotation + Local SQLite)
  python3 scripts/google_analytics.py annotate \
    --title "v2.0 Redesign Launch" \
    --date 2026-08-18 \
    --commit abc1234 \
    --description "Site redesign and technical SEO improvements."

  # 6. Execute Arbitrary SQL Query
  python3 scripts/google_analytics.py query "SELECT * FROM v_milestone_impact;"

  # 7. Run Pre-Built Reports
  python3 scripts/google_analytics.py report overview
  python3 scripts/google_analytics.py report top-pages
  python3 scripts/google_analytics.py report channels
  python3 scripts/google_analytics.py report milestone-impact
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
import google.auth
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
import google.oauth2.credentials
import google.oauth2.service_account
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

DEFAULT_CLIENT_SECRETS_FILE = (
    os.path.expanduser("~/.config/ga4/client_secret.json")
    if os.path.exists(os.path.expanduser("~/.config/ga4/client_secret.json"))
    else (
        os.path.expanduser("~/.config/gcloud/analytics_oauth_client.json")
        if os.path.exists(os.path.expanduser("~/.config/gcloud/analytics_oauth_client.json"))
        else "client_secret.json"
    )
)
DEFAULT_CREDENTIALS_FILE = (
    os.path.expanduser("~/.config/ga4/credentials.json")
    if os.path.exists(os.path.expanduser("~/.config/ga4/credentials.json"))
    else "credentials.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/analytics",
    "https://www.googleapis.com/auth/cloud-platform"
]


def ensure_dirs(db_path: str = DEFAULT_DB_FILE, config_file: Optional[str] = None):
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    if config_file:
        cfg_dir = os.path.dirname(os.path.abspath(config_file))
        if cfg_dir:
            os.makedirs(cfg_dir, exist_ok=True)


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

-- Release / Deployment Milestones
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
        WHEN page_path LIKE '/ja/%' THEN 'Japanese'
        WHEN page_path LIKE '/pt-br/%' THEN 'Portuguese'
        ELSE 'English'
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

DROP VIEW IF EXISTS v_milestone_impact;
CREATE VIEW v_milestone_impact AS
SELECT 
    m.commit_hash,
    m.title AS milestone_title,
    m.event_date AS milestone_date,
    CASE WHEN dp.date < m.event_date THEN 'Pre-Milestone' ELSE 'Post-Milestone' END AS cohort,
    COUNT(DISTINCT dp.date) AS days_tracked,
    SUM(dp.screen_page_views) AS total_views,
    SUM(dp.active_users) AS total_users,
    SUM(dp.sessions) AS total_sessions,
    ROUND(AVG(dp.user_engagement_duration), 1) AS avg_engagement_sec,
    ROUND(AVG(dp.bounce_rate) * 100, 1) AS avg_bounce_pct
FROM daily_pages dp
CROSS JOIN site_milestones m
GROUP BY m.commit_hash, cohort;
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
# Authentication & Credentials Management
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
    ensure_dirs(config_file=filepath)
    data = credentials_to_dict(credentials)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_credentials(
    filepath: str = DEFAULT_CREDENTIALS_FILE,
    service_account_path: Optional[str] = None
):
    """Resolves credentials from explicit OAuth JSON, service account, or ADC."""
    # 1. Check explicit OAuth credentials JSON with refresh token
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return google.oauth2.credentials.Credentials(**data)
        except Exception:
            pass

    # 2. Check service account JSON
    sa_path = service_account_path or ("service_account.json" if os.path.exists("service_account.json") else os.path.expanduser("~/.config/ga4/service_account.json"))
    if os.path.exists(sa_path):
        try:
            return google.oauth2.service_account.Credentials.from_service_account_file(
                sa_path, scopes=SCOPES
            )
        except Exception:
            pass

    # 3. Fall back to Google Application Default Credentials (ADC)
    try:
        credentials, _ = google.auth.default(scopes=SCOPES)
        return credentials
    except Exception:
        pass

    return None


def get_clients(credentials_file: str = DEFAULT_CREDENTIALS_FILE) -> Tuple[BetaAnalyticsDataClient, AnalyticsAdminServiceClient]:
    """Returns initialized Data and Admin clients."""
    creds = load_credentials(credentials_file)
    if not creds:
        print("❌ Error: No valid Google Credentials found.", file=sys.stderr)
        print("💡 Run 'python3 scripts/google_analytics.py auth' to log in via OAuth 2.0, or use ADC.", file=sys.stderr)
        sys.exit(1)
        
    data_client = BetaAnalyticsDataClient(credentials=creds)
    admin_client = AnalyticsAdminServiceClient(credentials=creds)
    return data_client, admin_client


def cmd_auth(
    client_secrets_file: str = DEFAULT_CLIENT_SECRETS_FILE,
    credentials_file: str = DEFAULT_CREDENTIALS_FILE,
    port: int = 8080,
    host: str = "127.0.0.1"
):
    """Launches OAuth 2.0 companion flow to authenticate with analytics.edit and readonly scopes."""
    import google_auth_oauthlib.flow

    ensure_dirs(config_file=credentials_file)

    if not os.path.exists(client_secrets_file):
        print(f"❌ Client secret file not found: {client_secrets_file}", file=sys.stderr)
        print("💡 Place your OAuth 2.0 Client Secret JSON in ~/.config/ga4/client_secret.json or ~/.config/gcloud/analytics_oauth_client.json", file=sys.stderr)
        sys.exit(1)

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
        print(f"✅ Credentials successfully authorized and saved to {credentials_file}!\n")
        return

    # Web flow fallback
    print(f"❌ Web application client secrets detected. Please use an Installed Application OAuth client ID.", file=sys.stderr)


# ---------------------------------------------------------------------------
# Reporting Annotations & Milestones Engine
# ---------------------------------------------------------------------------

def create_annotation(
    property_id: str,
    title: str,
    description: str,
    date_str: str,
    color: str = "BLUE",
    commit_hash: Optional[str] = None,
    category: Optional[str] = None,
    scope: Optional[str] = None,
    author: Optional[str] = None,
    db_path: str = DEFAULT_DB_FILE,
    credentials_file: str = DEFAULT_CREDENTIALS_FILE
):
    """Creates an annotation both in the GA4 Cloud Property and in the local SQLite database."""
    conn = init_db(db_path)
    
    parts = date_str.split("-")
    if len(parts) != 3:
        print(f"❌ Invalid date format '{date_str}'. Expected YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)
        
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    c_hash = commit_hash or f"milestone-{date_str}"
    
    # 1. Local SQLite Milestone Record
    conn.execute("""
        INSERT OR REPLACE INTO site_milestones (
            commit_hash, event_date, title, description, category, scope, author
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        c_hash,
        date_str,
        title,
        description,
        category or "SEO/Architecture",
        scope or "sitewide",
        author or os.environ.get("USER", "")
    ))
    conn.commit()
    conn.close()
    print(f"✅ Milestone recorded locally in SQLite: '{title}' [{c_hash}] on {date_str}")

    # 2. GA4 Cloud Annotation via Admin API
    creds = load_credentials(credentials_file)
    if not creds:
        print("⚠️ Note: No OAuth write credentials found for GA4 Cloud API. Local milestone recorded.")
        return

    import google.auth.transport.requests
    import requests

    try:
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/reportingDataAnnotations"
        headers = {
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "title": title[:60],
            "description": description[:150] if description else "",
            "color": color.upper(),
            "annotationDate": {
                "year": year,
                "month": month,
                "day": day
            }
        }
        
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code in (200, 201):
            ann_data = res.json()
            ann_name = ann_data.get("name", "")
            print(f"🎉 GA4 Cloud Reporting Annotation created successfully! Resource: {ann_name}")
        else:
            print(f"⚠️ GA4 API returned status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"⚠️ Could not post annotation to GA4 Cloud API: {e}")


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
    """Ingests outbound link clicks specifically."""
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
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="click")
            )
        ),
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
            
        link_url = r.dimension_values[1].value
        if not link_url:
            continue
            
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
    property_id: str,
    days: Optional[int] = None,
    full: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: str = DEFAULT_DB_FILE,
    credentials_file: str = DEFAULT_CREDENTIALS_FILE
):
    """Orchestrates sync operations across all GA4 domains."""
    data_client, admin_client = get_clients(credentials_file)
    conn = init_db(db_path)
    started_at = datetime.datetime.now().isoformat()
    
    if not property_id:
        cur = conn.cursor()
        cur.execute("SELECT property_id FROM properties ORDER BY last_synced_at DESC LIMIT 1;")
        row = cur.fetchone()
        if row:
            property_id = row[0]
        else:
            print("🔍 Auto-discovering GA4 properties...")
            accounts = admin_client.list_account_summaries()
            for acc in accounts:
                if acc.property_summaries:
                    property_id = acc.property_summaries[0].property.split('/')[-1]
                    break
                    
    if not property_id:
        print("❌ Error: No GA4 property found or specified. Run 'properties' command first.", file=sys.stderr)
        sys.exit(1)
        
    sync_property_metadata(admin_client, conn, property_id)
    
    # Determine date ranges
    today = datetime.date.today()
    if full:
        s_date = (today - datetime.timedelta(days=420)).isoformat()
        e_date = today.isoformat()
        sync_type = "FULL_BACKFILL"
    elif days:
        s_date = (today - datetime.timedelta(days=days)).isoformat()
        e_date = today.isoformat()
        sync_type = f"TRAILING_{days}_DAYS"
    elif start_date and end_date:
        s_date = start_date
        e_date = end_date
        sync_type = "CUSTOM_RANGE"
    else:
        # Incremental: check latest date in db and overlap 3 days for latency
        cur = conn.cursor()
        cur.execute("SELECT MAX(date) FROM daily_pages WHERE property_id = ?;", (property_id,))
        max_d = cur.fetchone()[0]
        if max_d:
            max_dt = datetime.datetime.strptime(max_d, "%Y-%m-%d").date()
            s_date = (max_dt - datetime.timedelta(days=3)).isoformat()
        else:
            s_date = (today - datetime.timedelta(days=90)).isoformat()
        e_date = today.isoformat()
        sync_type = "INCREMENTAL"

    print(f"🚀 Starting GA4 Sync ({sync_type}) for Property {property_id} [{s_date} -> {e_date}]...")
    
    try:
        p_count = ingest_daily_pages(data_client, conn, property_id, s_date, e_date)
        t_count = ingest_daily_traffic(data_client, conn, property_id, s_date, e_date)
        e_count = ingest_daily_events(data_client, conn, property_id, s_date, e_date)
        o_count = ingest_outbound_clicks(data_client, conn, property_id, s_date, e_date)
        
        conn.execute("""
            INSERT INTO sync_history (
                property_id, sync_type, start_date, end_date,
                pages_synced, traffic_synced, events_synced, outbound_synced,
                status, started_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'SUCCESS', ?)
        """, (property_id, sync_type, s_date, e_date, p_count, t_count, e_count, o_count, started_at))
        conn.commit()
        
        print("\n✅ Sync Complete Summary:")
        print(f"  • Daily Page Breakdowns: {p_count} records")
        print(f"  • Traffic Sources:        {t_count} records")
        print(f"  • Interaction Events:     {e_count} records")
        print(f"  • Outbound Link Clicks:   {o_count} records")
        print(f"  • SQLite Database:        {db_path}")
        
    except Exception as e:
        conn.execute("""
            INSERT INTO sync_history (
                property_id, sync_type, start_date, end_date,
                status, error_message, started_at
            ) VALUES (?, ?, ?, ?, 'FAILED', ?, ?)
        """, (property_id, sync_type, s_date, e_date, str(e), started_at))
        conn.commit()
        print(f"❌ Sync failed with error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Pre-Packaged Analytical Reports
# ---------------------------------------------------------------------------

def run_report(name: str, db_path: str = DEFAULT_DB_FILE):
    """Executes pre-packaged analytical queries."""
    conn = init_db(db_path)
    cur = conn.cursor()
    
    reports = {
        "overview": ("Site Overview (30-Day Aggregates)", """
            SELECT 
                COUNT(DISTINCT date) AS active_days,
                SUM(total_sessions) AS total_sessions,
                SUM(total_active_users) AS total_active_users,
                SUM(total_page_views) AS total_views,
                ROUND(AVG(total_engagement_min), 1) AS avg_daily_engagement_min,
                ROUND(AVG(avg_bounce_pct), 1) AS overall_bounce_pct
            FROM v_daily_summary
            LIMIT 30;
        """),
        "top-pages": ("Top 15 Pages by Total Views & Engagement", """
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
        """),
        "channels": ("Acquisition Channels Performance", """
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
        """),
        "geo": ("Top 10 Countries by Visitor Volume & Dwell Time", """
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
        """),
        "events": ("User Interaction Events Summary", """
            SELECT 
                event_name,
                total_events,
                total_users
            FROM v_events_summary;
        """),
        "outbound": ("Top 15 Outbound Link Click Destinations", """
            SELECT 
                link_url,
                total_clicks,
                total_users,
                referring_pages_count
            FROM v_outbound_links
            ORDER BY total_clicks DESC
            LIMIT 15;
        """),
        "milestone-impact": ("Milestone / Release Cohort Comparison", """
            SELECT 
                commit_hash,
                milestone_title,
                milestone_date,
                cohort,
                days_tracked,
                total_views,
                total_users,
                avg_engagement_sec || 's' AS avg_dwell,
                avg_bounce_pct || '%' AS bounce
            FROM v_milestone_impact;
        """)
    }
    
    if name not in reports:
        print(f"❌ Unknown report '{name}'. Choices: {list(reports.keys())}", file=sys.stderr)
        return
        
    title, sql = reports[name]
    print(f"\n📊 {title}\n" + "=" * len(title))
    
    cur.execute(sql)
    cols = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    
    if HAS_TABULATE:
        print(tabulate(rows, headers=cols, tablefmt="grid"))
    else:
        print(" | ".join(cols))
        print("-" * (len(" | ".join(cols))))
        for r in rows:
            print(" | ".join(str(x) for x in r))
    print(f"\n({len(rows)} rows)\n")
    conn.close()


def run_query(sql: str, db_path: str = DEFAULT_DB_FILE, output_format: str = "markdown", output_json: bool = False, output_csv: bool = False):
    """Executes arbitrary SQL query against the analytics database."""
    conn = init_db(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        
        if output_json or output_format == "json":
            result = [dict(zip(cols, row)) for row in rows]
            print(json.dumps(result, indent=2))
        elif output_csv or output_format == "csv":
            writer = csv.writer(sys.stdout)
            writer.writerow(cols)
            writer.writerows(rows)
        elif output_format == "table" and HAS_TABULATE:
            print(tabulate(rows, headers=cols, tablefmt="grid"))
            print(f"\n({len(rows)} rows)")
        else:
            if HAS_TABULATE:
                print(tabulate(rows, headers=cols, tablefmt="github"))
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
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("--db", "--db-path", dest="db_path", default=DEFAULT_DB_FILE, help=f"Path to SQLite database (default: {DEFAULT_DB_FILE})")
    base_parser.add_argument("--property-id", default=DEFAULT_PROPERTY_ID, help=f"GA4 Property ID (default: {DEFAULT_PROPERTY_ID})")
    base_parser.add_argument("--credentials", default=DEFAULT_CREDENTIALS_FILE, help=f"OAuth credentials JSON (default: {DEFAULT_CREDENTIALS_FILE})")

    parser = argparse.ArgumentParser(
        description="Google Analytics 4 Ingestion Engine & SQL Analytics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
        parents=[base_parser],
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcommand: auth
    auth_p = subparsers.add_parser("auth", parents=[base_parser], help="Authenticate via OAuth 2.0 Web Flow")
    auth_p.add_argument("--client-secrets", "--client-secret", dest="client_secret", default=DEFAULT_CLIENT_SECRETS_FILE, help="Path to client secret JSON")
    auth_p.add_argument("--port", type=int, default=8080, help="Port for OAuth callback server")
    
    # Subcommand: annotate
    ann_p = subparsers.add_parser("annotate", parents=[base_parser], help="Create a deployment/milestone annotation in GA4 and SQLite")
    ann_p.add_argument("--title", required=True, help="Annotation / Milestone Title")
    ann_p.add_argument("--date", required=True, help="Event Date (YYYY-MM-DD)")
    ann_p.add_argument("--commit", help="Git commit hash")
    ann_p.add_argument("--description", default="", help="Detailed description of changes")
    ann_p.add_argument("--color", default="BLUE", choices=["BLUE", "GREEN", "PURPLE", "RED", "BROWN", "CYAN"], help="Chart Pin Color")
    ann_p.add_argument("--category", default="Release", help="Milestone category")
    ann_p.add_argument("--scope", default="sitewide", help="Scope of changes")
    ann_p.add_argument("--author", default=os.environ.get("USER", ""), help="Author of release")
    
    # Subcommand: properties
    subparsers.add_parser("properties", parents=[base_parser], help="List all accessible GA4 accounts and properties")
    
    # Subcommand: sync
    sync_p = subparsers.add_parser("sync", parents=[base_parser], help="Ingest raw GA4 data into SQLite database")
    sync_p.add_argument("--days", type=int, help="Number of trailing days to sync")
    sync_p.add_argument("--full", action="store_true", help="Perform full historical backfill (up to 14 months)")
    sync_p.add_argument("--start-date", help="Custom start date (YYYY-MM-DD)")
    sync_p.add_argument("--end-date", help="Custom end date (YYYY-MM-DD)")
    
    # Subcommand: report
    report_p = subparsers.add_parser("report", parents=[base_parser], help="Run pre-built analytical reports")
    report_p.add_argument("name", choices=["overview", "top-pages", "channels", "geo", "events", "outbound", "milestone-impact"], help="Report name")
    
    # Subcommand: query
    query_p = subparsers.add_parser("query", parents=[base_parser], help="Execute arbitrary SQL against the database")
    query_p.add_argument("sql", help="SQL query to execute")
    query_p.add_argument("--format", default="markdown", choices=["markdown", "table", "json", "csv"], help="Output format (default: markdown)")
    query_p.add_argument("--json", action="store_true", help="Output results in JSON format")
    query_p.add_argument("--csv", action="store_true", help="Output results in CSV format")
    
    args = parser.parse_args()
    
    if args.command == "auth":
        cmd_auth(
            client_secrets_file=args.client_secret,
            credentials_file=args.credentials,
            port=args.port
        )
    elif args.command == "annotate":
        create_annotation(
            property_id=args.property_id,
            title=args.title,
            description=args.description,
            date_str=args.date,
            color=args.color,
            commit_hash=args.commit,
            category=args.category,
            scope=args.scope,
            author=args.author,
            db_path=args.db_path,
            credentials_file=args.credentials
        )
    elif args.command == "properties":
        _, admin_client = get_clients(args.credentials)
        list_properties(admin_client, args.db_path)
    elif args.command == "sync":
        run_sync(
            property_id=args.property_id,
            days=args.days,
            full=args.full,
            start_date=args.start_date,
            end_date=args.end_date,
            db_path=args.db_path,
            credentials_file=args.credentials
        )
    elif args.command == "report":
        run_report(args.name, args.db_path)
    elif args.command == "query":
        run_query(args.sql, args.db_path, args.format, args.json, args.csv)


if __name__ == "__main__":
    main()
