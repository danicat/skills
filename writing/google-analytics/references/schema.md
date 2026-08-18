# Google Analytics 4 SQLite Database Schema DDL

The `google-analytics` SQLite database (`google_analytics.db` or `$XDG_DATA_HOME/google-analytics/analytics.db`) stores raw Google Analytics 4 performance metrics, traffic sources, event streams, and outbound click records without data loss.

---

## 1. Tables DDL

### `properties`
Verified GA4 property metadata and configuration details.

```sql
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
```

### `daily_pages`
Granular daily page views, active users, sessions, dwell time, and bounce rate broken down by country, device, and source.

```sql
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
```

### `daily_traffic`
Granular daily acquisition channels, source/medium breakdown, sessions, new users, engaged sessions, and bounce rate.

```sql
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
```

### `daily_events`
Daily user engagement events (`scroll`, `click`, `first_visit`, `user_engagement`, `page_view`, etc.).

```sql
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
```

### `outbound_clicks`
Outbound link destinations, exit URLs, source pages, and click frequencies.

```sql
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
```

### `sync_history`
Audit log recording every backfill and incremental sync operation.

```sql
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
```

---

## 2. Analytical Views

- **`v_daily_summary`**: High-level daily totals for sessions, users, pageviews, total active dwell time, and bounce rate.
- **`v_page_performance`**: Page-level rollup with language categorization (`/`, `/ja/`, `/pt-br/`), total page views, active users, average dwell time (seconds and minutes), and average bounce rate.
- **`v_channel_performance`**: Acquisition channels and source/medium pairs with total sessions, new user counts, engagement rate %, and total dwell minutes.
- **`v_geo_breakdown`**: Geographical ranking by country with total sessions, pageviews, average dwell time, and bounce rate.
- **`v_events_summary`**: Event breakdown across all user interactions.
- **`v_outbound_links`**: External destinations ranked by click counts and unique referring pages.
