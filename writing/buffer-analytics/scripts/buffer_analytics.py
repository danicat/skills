#!/usr/bin/env python3
"""
buffer_analytics.py - Robust SQLite Data Ingestion, Backfill & SQL Analytics for Buffer

Preserves raw Buffer payloads without loss while exposing structured tables and
high-performance analytical SQL views for deep query crunching.

Usage:
  python3 buffer_analytics.py sync [--full] [--channel-id <id>] [--start-date <iso>] [--end-date <iso>]
  python3 buffer_analytics.py query "SELECT * FROM v_posts_summary LIMIT 10" [--format table|markdown|json|csv]
  python3 buffer_analytics.py report [overview|top-posts|channels|timing|hooks]
  python3 buffer_analytics.py schema
"""

import argparse
import datetime
import json
import os
import sqlite3
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

# Default local database path (local to working directory, override with --db)
DEFAULT_DB_PATH = "analytics.db"


def ensure_dirs(db_path: str = DEFAULT_DB_PATH):
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

SCHEMA_DDL = """
-- Core Channels Table
CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    organization_id TEXT,
    name TEXT,
    service TEXT,
    display_name TEXT,
    timezone TEXT,
    is_disconnected INTEGER DEFAULT 0,
    is_locked INTEGER DEFAULT 0,
    is_queue_paused INTEGER DEFAULT 0,
    avatar_url TEXT,
    external_link TEXT,
    raw_json TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT,
    synced_at TEXT NOT NULL
);

-- Core Posts Table (Stores full raw payload + indexed operational fields)
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    organization_id TEXT,
    channel_id TEXT NOT NULL,
    channel_service TEXT,
    status TEXT NOT NULL,
    text TEXT,
    external_link TEXT,
    sent_at TEXT,
    due_at TEXT,
    created_at TEXT,
    updated_at TEXT,
    scheduling_type TEXT,
    is_ai_generated INTEGER DEFAULT 0,
    thread_count INTEGER DEFAULT 0,
    first_comment TEXT,
    char_count INTEGER,
    word_count INTEGER,
    has_link INTEGER DEFAULT 0,
    has_media INTEGER DEFAULT 0,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id)
);

-- Normalized Post Metrics (Time-series / historical captures)
CREATE TABLE IF NOT EXISTS post_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    channel_id TEXT,
    channel_service TEXT,
    metric_type TEXT NOT NULL,
    name TEXT,
    value REAL NOT NULL DEFAULT 0,
    unit TEXT,
    description TEXT,
    recorded_at TEXT,
    synced_at TEXT NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id),
    UNIQUE(post_id, metric_type) ON CONFLICT REPLACE
);

-- Post Assets (Images, Videos, Thumbnails)
CREATE TABLE IF NOT EXISTS post_assets (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    type TEXT,
    mime_type TEXT,
    source TEXT,
    thumbnail TEXT,
    raw_json TEXT,
    FOREIGN KEY(post_id) REFERENCES posts(id)
);

-- Post Tags
CREATE TABLE IF NOT EXISTS post_tags (
    id TEXT,
    post_id TEXT NOT NULL,
    name TEXT,
    color TEXT,
    PRIMARY KEY(post_id, id),
    FOREIGN KEY(post_id) REFERENCES posts(id)
);

-- Sync History Log
CREATE TABLE IF NOT EXISTS sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id TEXT,
    channel_id TEXT,
    sync_mode TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    posts_fetched INTEGER DEFAULT 0,
    posts_inserted INTEGER DEFAULT 0,
    posts_updated INTEGER DEFAULT 0,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    error_message TEXT
);

-- Indexes for Fast Analytics
CREATE INDEX IF NOT EXISTS idx_posts_sent_at ON posts(sent_at);
CREATE INDEX IF NOT EXISTS idx_posts_channel_service ON posts(channel_service);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_post_metrics_lookup ON post_metrics(post_id, metric_type);

-- Flattened Analytical View for Posts & Metrics
DROP VIEW IF EXISTS v_posts_summary;
CREATE VIEW v_posts_summary AS
SELECT 
    p.id AS post_id,
    p.channel_service AS service,
    c.name AS channel_name,
    p.status,
    p.sent_at,
    strftime('%Y-%m-%d', p.sent_at) AS sent_date,
    strftime('%Y-%m', p.sent_at) AS year_month,
    CASE strftime('%w', p.sent_at)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    CAST(strftime('%H', p.sent_at) AS INTEGER) AS hour_of_day,
    p.char_count,
    p.word_count,
    p.has_link,
    p.has_media,
    p.thread_count,
    p.external_link,
    p.text,
    COALESCE(MAX(CASE WHEN m.metric_type = 'impressions' THEN m.value END), 0) AS impressions,
    COALESCE(MAX(CASE WHEN m.metric_type = 'reach' THEN m.value END), 0) AS reach,
    COALESCE(MAX(CASE WHEN m.metric_type = 'reactions' THEN m.value END), 0) AS reactions,
    COALESCE(MAX(CASE WHEN m.metric_type = 'comments' THEN m.value END), 0) AS comments,
    COALESCE(MAX(CASE WHEN m.metric_type = 'reposts' THEN m.value END), 0) AS reposts,
    COALESCE(MAX(CASE WHEN m.metric_type = 'clicks' THEN m.value END), 0) AS clicks,
    COALESCE(MAX(CASE WHEN m.metric_type = 'engagementRate' THEN m.value END), 
        CASE 
            WHEN COALESCE(MAX(CASE WHEN m.metric_type = 'impressions' THEN m.value END), 0) > 0 
            THEN ROUND((COALESCE(MAX(CASE WHEN m.metric_type = 'reactions' THEN m.value END), 0) + 
                        COALESCE(MAX(CASE WHEN m.metric_type = 'comments' THEN m.value END), 0) + 
                        COALESCE(MAX(CASE WHEN m.metric_type = 'reposts' THEN m.value END), 0)) * 100.0 / 
                       MAX(CASE WHEN m.metric_type = 'impressions' THEN m.value END), 2)
            ELSE 0.0 
        END
    ) AS engagement_rate
FROM posts p
LEFT JOIN channels c ON p.channel_id = c.id
LEFT JOIN post_metrics m ON p.id = m.post_id
GROUP BY p.id;
"""


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Ensure database directory exists and initialize SQLite connection with schema."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_DDL)
    conn.commit()
    return conn


def run_buffer_cli(args: List[str], timeout_ms: int = 60000) -> Dict[str, Any]:
    """Execute a buffer CLI command and return parsed JSON."""
    cmd = ["buffer"] + args + ["--output", "json"]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_ms / 1000.0,
            check=False,
        )
        if proc.returncode != 0:
            err_msg = proc.stderr.strip() or proc.stdout.strip()
            raise RuntimeError(f"Buffer CLI exited with code {proc.returncode}: {err_msg}")
        return json.loads(proc.stdout)
    except FileNotFoundError:
        # Fallback to npx @bufferapp/cli
        cmd_npx = ["npx", "-y", "@bufferapp/cli@latest"] + args + ["--output", "json"]
        proc = subprocess.run(cmd_npx, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"npx Buffer CLI failed: {proc.stderr.strip()}")
        return json.loads(proc.stdout)


def get_organization_id() -> str:
    """Fetch default organization ID from Buffer CLI account info."""
    data = run_buffer_cli(["account"])
    orgs = data.get("organizations", [])
    if not orgs:
        raise ValueError("No Buffer organizations found in account.")
    return orgs[0]["id"]


def sync_channels(conn: sqlite3.Connection, org_id: str) -> List[Dict[str, Any]]:
    """Download and upsert all channels for the organization."""
    data = run_buffer_cli(["channels", "list"])
    channels = data.get("items", []) if isinstance(data, dict) and "items" in data else data
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cursor = conn.cursor()
    for ch in channels:
        ch_id = ch.get("id")
        raw_json = json.dumps(ch)
        cursor.execute(
            """
            INSERT INTO channels (
                id, organization_id, name, service, display_name, timezone,
                is_disconnected, is_locked, is_queue_paused, avatar_url, external_link,
                raw_json, created_at, updated_at, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                service=excluded.service,
                display_name=excluded.display_name,
                timezone=excluded.timezone,
                is_disconnected=excluded.is_disconnected,
                is_locked=excluded.is_locked,
                is_queue_paused=excluded.is_queue_paused,
                avatar_url=excluded.avatar_url,
                external_link=excluded.external_link,
                raw_json=excluded.raw_json,
                updated_at=excluded.updated_at,
                synced_at=excluded.synced_at;
            """,
            (
                ch_id,
                org_id,
                ch.get("name"),
                ch.get("service"),
                ch.get("displayName"),
                ch.get("timezone"),
                1 if ch.get("isDisconnected") else 0,
                1 if ch.get("isLocked") else 0,
                1 if ch.get("isQueuePaused") else 0,
                ch.get("avatar"),
                ch.get("externalLink"),
                raw_json,
                ch.get("createdAt"),
                ch.get("updatedAt"),
                now_iso,
            ),
        )
    conn.commit()
    return channels


def backfill_posts(
    conn: sqlite3.Connection,
    org_id: str,
    channel_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_filter: Optional[List[str]] = None,
    full_sync: bool = False,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    Robustly backfill posts with cursor-based pagination and upsert to SQLite.
    Preserves all raw data and normalized metrics.
    """
    sync_mode = "full" if full_sync else "incremental"
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Check latest synced post if incremental
    if not full_sync and not start_date:
        cursor = conn.cursor()
        query = "SELECT MAX(sent_at) as max_sent FROM posts"
        if channel_id:
            query += " WHERE channel_id = ?"
            cursor.execute(query, (channel_id,))
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        if row and row["max_sent"]:
            # Small lookback overlap of 2 days to catch updated metrics on recent posts
            try:
                latest_dt = datetime.datetime.fromisoformat(row["max_sent"].replace("Z", "+00:00"))
                overlap_dt = latest_dt - datetime.timedelta(days=2)
                start_date = overlap_dt.isoformat()
            except Exception:
                pass

    total_fetched = 0
    total_inserted = 0
    total_updated = 0
    after_cursor: Optional[str] = None
    has_next_page = True

    fields = (
        "items.id,items.status,items.text,items.externalLink,items.createdAt,items.updatedAt,"
        "items.dueAt,items.sentAt,items.schedulingType,items.channelId,items.channelService,"
        "items.channel.name,items.channel.service,items.metadata,items.assets,items.tags,items.metrics,"
        "pageInfo.startCursor,pageInfo.endCursor,pageInfo.hasNextPage"
    )

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        while has_next_page:
            args = [
                "posts",
                "list",
                "--organization-id",
                org_id,
                "--limit",
                str(page_size),
                "--fields",
                fields,
            ]
            if channel_id:
                args.extend(["--filter.channel-ids", json.dumps([channel_id])])
            if start_date:
                args.extend(["--filter.start-date", start_date])
            if end_date:
                args.extend(["--filter.end-date", end_date])
            if status_filter:
                args.extend(["--filter.status", json.dumps(status_filter)])
            if after_cursor:
                args.extend(["--after", after_cursor])

            data = run_buffer_cli(args)
            items = data.get("items", [])
            page_info = data.get("pageInfo", {})

            if not items:
                break

            total_fetched += len(items)
            cursor = conn.cursor()

            for item in items:
                post_id = item.get("id")
                ch_id = item.get("channelId") or (item.get("channel") or {}).get("id")
                service = item.get("channelService") or (item.get("channel") or {}).get("service")
                text = item.get("text") or ""
                metadata = item.get("metadata") or {}
                first_comment = metadata.get("firstComment")
                thread_count = metadata.get("threadCount", 0)
                is_ai = 1 if metadata.get("isAiGenerated") else 0
                assets = item.get("assets") or []
                tags = item.get("tags") or []
                metrics = item.get("metrics") or []

                char_count = len(text)
                word_count = len(text.split()) if text else 0
                has_link = 1 if ("http://" in text or "https://" in text or item.get("externalLink")) else 0
                has_media = 1 if len(assets) > 0 else 0

                raw_json = json.dumps(item)

                # Check if post exists
                cursor.execute("SELECT id FROM posts WHERE id = ?", (post_id,))
                exists = cursor.fetchone() is not None

                cursor.execute(
                    """
                    INSERT INTO posts (
                        id, organization_id, channel_id, channel_service, status, text,
                        external_link, sent_at, due_at, created_at, updated_at, scheduling_type,
                        is_ai_generated, thread_count, first_comment, char_count, word_count,
                        has_link, has_media, raw_json, synced_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        status=excluded.status,
                        text=excluded.text,
                        external_link=excluded.external_link,
                        sent_at=excluded.sent_at,
                        due_at=excluded.due_at,
                        updated_at=excluded.updated_at,
                        first_comment=excluded.first_comment,
                        thread_count=excluded.thread_count,
                        has_link=excluded.has_link,
                        has_media=excluded.has_media,
                        raw_json=excluded.raw_json,
                        synced_at=excluded.synced_at;
                    """,
                    (
                        post_id,
                        org_id,
                        ch_id,
                        service,
                        item.get("status"),
                        text,
                        item.get("externalLink"),
                        item.get("sentAt"),
                        item.get("dueAt"),
                        item.get("createdAt"),
                        item.get("updatedAt"),
                        item.get("schedulingType"),
                        is_ai,
                        thread_count,
                        first_comment,
                        char_count,
                        word_count,
                        has_link,
                        has_media,
                        raw_json,
                        now_iso,
                    ),
                )

                if exists:
                    total_updated += 1
                else:
                    total_inserted += 1

                # Upsert Metrics
                recorded_at = item.get("metricsUpdatedAt") or now_iso
                for m in metrics:
                    m_type = m.get("type")
                    if not m_type:
                        continue
                    m_val = float(m.get("value", 0))
                    cursor.execute(
                        """
                        INSERT INTO post_metrics (
                            post_id, channel_id, channel_service, metric_type, name,
                            value, unit, description, recorded_at, synced_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(post_id, metric_type) DO UPDATE SET
                            value=excluded.value,
                            recorded_at=excluded.recorded_at,
                            synced_at=excluded.synced_at;
                        """,
                        (
                            post_id,
                            ch_id,
                            service,
                            m_type,
                            m.get("name"),
                            m_val,
                            m.get("unit"),
                            m.get("description"),
                            recorded_at,
                            now_iso,
                        ),
                    )

                # Upsert Assets
                for ast in assets:
                    ast_id = ast.get("id") or f"{post_id}_asset_{ast.get('type')}"
                    cursor.execute(
                        """
                        INSERT INTO post_assets (id, post_id, type, mime_type, source, thumbnail, raw_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            source=excluded.source,
                            thumbnail=excluded.thumbnail;
                        """,
                        (
                            ast_id,
                            post_id,
                            ast.get("type"),
                            ast.get("mimeType"),
                            ast.get("source"),
                            ast.get("thumbnail"),
                            json.dumps(ast),
                        ),
                    )

                # Upsert Tags
                for tg in tags:
                    tg_id = tg.get("id") or tg.get("name")
                    cursor.execute(
                        """
                        INSERT INTO post_tags (id, post_id, name, color)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(post_id, id) DO UPDATE SET
                            name=excluded.name,
                            color=excluded.color;
                        """,
                        (tg_id, post_id, tg.get("name"), tg.get("color")),
                    )

            conn.commit()

            # Pagination check
            has_next_page = page_info.get("hasNextPage", False)
            after_cursor = page_info.get("endCursor")

            if not has_next_page or not after_cursor:
                break

        # Record successful sync history
        cursor.execute(
            """
            INSERT INTO sync_history (
                organization_id, channel_id, sync_mode, start_date, end_date,
                posts_fetched, posts_inserted, posts_updated, started_at, finished_at,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUCCESS');
            """,
            (
                org_id,
                channel_id,
                sync_mode,
                start_date,
                end_date,
                total_fetched,
                total_inserted,
                total_updated,
                started_at,
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
            ),
        )
        conn.commit()

        return {
            "status": "SUCCESS",
            "sync_mode": sync_mode,
            "posts_fetched": total_fetched,
            "posts_inserted": total_inserted,
            "posts_updated": total_updated,
        }

    except Exception as e:
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sync_history (
                organization_id, channel_id, sync_mode, start_date, end_date,
                posts_fetched, posts_inserted, posts_updated, started_at, finished_at,
                status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'FAILED', ?);
            """,
            (
                org_id,
                channel_id,
                sync_mode,
                start_date,
                end_date,
                total_fetched,
                total_inserted,
                total_updated,
                started_at,
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                str(e),
            ),
        )
        conn.commit()
        raise


def execute_sql(conn: sqlite3.Connection, sql: str, output_format: str = "table") -> str:
    """Execute raw SQL query and format results."""
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    if not rows:
        return "No results returned."

    columns = [desc[0] for desc in cursor.description]

    if output_format == "json":
        result = [dict(row) for row in rows]
        return json.dumps(result, indent=2)

    if output_format == "csv":
        import csv
        import io
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(columns)
        for r in rows:
            writer.writerow([r[c] for c in columns])
        return buf.getvalue()

    if output_format in ("table", "markdown"):
        # Format markdown table
        headers = columns
        col_widths = [len(h) for h in headers]
        
        str_rows = []
        for r in rows:
            row_vals = []
            for i, c in enumerate(columns):
                val = r[c]
                val_str = "" if val is None else str(val).replace("\n", " ")
                if len(val_str) > 60:
                    val_str = val_str[:57] + "..."
                row_vals.append(val_str)
                col_widths[i] = max(col_widths[i], len(val_str))
            str_rows.append(row_vals)

        header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
        separator = "|-" + "-|-".join("-" * col_widths[i] for i in range(len(headers))) + "-|"
        data_lines = ["| " + " | ".join(r[i].ljust(col_widths[i]) for i in range(len(r))) + " |" for r in str_rows]

        return "\n".join([header_line, separator] + data_lines)

    return str([dict(row) for row in rows])


REPORTS = {
    "overview": """
        SELECT 
            service,
            COUNT(*) AS total_posts,
            SUM(impressions) AS total_impressions,
            SUM(reactions) AS total_reactions,
            SUM(comments) AS total_comments,
            SUM(reposts) AS total_reposts,
            ROUND(AVG(engagement_rate), 2) AS avg_engagement_rate
        FROM v_posts_summary
        WHERE status = 'sent'
        GROUP BY service
        ORDER BY total_impressions DESC;
    """,
    "top-posts": """
        SELECT 
            service,
            sent_date,
            reactions,
            impressions,
            comments,
            reposts,
            engagement_rate,
            SUBSTR(text, 1, 80) AS hook
        FROM v_posts_summary
        WHERE status = 'sent'
        ORDER BY impressions DESC
        LIMIT 10;
    """,
    "timing": """
        SELECT 
            day_of_week,
            COUNT(*) AS post_count,
            ROUND(AVG(impressions), 0) AS avg_impressions,
            ROUND(AVG(reactions), 1) AS avg_reactions,
            ROUND(AVG(comments), 1) AS avg_comments,
            ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
        FROM v_posts_summary
        WHERE status = 'sent' AND day_of_week IS NOT NULL
        GROUP BY day_of_week
        ORDER BY avg_impressions DESC;
    """,
    "hooks": """
        SELECT 
            service,
            sent_date,
            char_count,
            has_link,
            reactions,
            impressions,
            engagement_rate,
            SUBSTR(text, 1, 100) AS opening_hook
        FROM v_posts_summary
        WHERE status = 'sent'
        ORDER BY reactions DESC
        LIMIT 10;
    """,
}


def main():
    parser = argparse.ArgumentParser(
        description="Buffer Analytics CLI: High-Performance SQLite Ingestion & SQL Query Engine"
    )
    parser.add_argument("--db", "--db-path", dest="db_path", default=DEFAULT_DB_PATH, help=f"Path to SQLite DB (default: {DEFAULT_DB_PATH})")
    parser.add_argument("-q", "--query", help="Execute SQL query directly against the analytics database")
    parser.add_argument("--format", choices=["table", "markdown", "json", "csv"], default="markdown", help="Output format (default: markdown)")

    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # Sync subcommand
    sync_parser = subparsers.add_parser("sync", help="Sync channels and posts into SQLite")
    sync_parser.add_argument("--full", action="store_true", help="Perform complete historical backfill")
    sync_parser.add_argument("--channel-id", help="Filter backfill to specific channel ID")
    sync_parser.add_argument("--start-date", help="Backfill posts created after this ISO date")
    sync_parser.add_argument("--end-date", help="Backfill posts created before this ISO date")
    sync_parser.add_argument("--status", nargs="+", help="Filter by status (e.g. sent scheduled draft)")

    # Query subcommand
    query_parser = subparsers.add_parser("query", help="Execute SQL query against Buffer analytics database")
    query_parser.add_argument("sql", help="SQL query string")
    query_parser.add_argument(
        "--format",
        choices=["table", "markdown", "json", "csv"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    # Report subcommand
    report_parser = subparsers.add_parser("report", help="Run pre-canned analytical reports")
    report_parser.add_argument("name", choices=list(REPORTS.keys()), help="Report name")
    report_parser.add_argument(
        "--format", choices=["table", "markdown", "json", "csv"], default="markdown", help="Output format"
    )

    # Schema subcommand
    subparsers.add_parser("schema", help="Print the database DDL schema and analytical views")

    args = parser.parse_args()

    conn = get_db_connection(args.db_path)

    if args.query:
        result = execute_sql(conn, args.query, output_format=args.format)
        print(result)
        sys.exit(0)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "schema":
        print(SCHEMA_DDL.strip())
        sys.exit(0)

    if args.command == "sync":
        print(f"Connecting to Buffer CLI and initializing DB at: {args.db_path}")
        org_id = get_organization_id()
        print(f"Discovered Organization ID: {org_id}")
        
        channels = sync_channels(conn, org_id)
        print(f"Synced {len(channels)} channels.")

        print(f"Starting post ingestion (mode: {'full backfill' if args.full else 'incremental'})...")
        res = backfill_posts(
            conn=conn,
            org_id=org_id,
            channel_id=args.channel_id,
            start_date=args.start_date,
            end_date=args.end_date,
            status_filter=args.status,
            full_sync=args.full,
        )
        print(f"Ingestion complete: {res['posts_fetched']} fetched, {res['posts_inserted']} inserted, {res['posts_updated']} updated.")
        sys.exit(0)

    if args.command == "query":
        result = execute_sql(conn, args.sql, output_format=args.format)
        print(result)
        sys.exit(0)

    if args.command == "report":
        sql = REPORTS[args.name]
        result = execute_sql(conn, sql, output_format=args.format)
        print(result)
        sys.exit(0)


if __name__ == "__main__":
    main()
