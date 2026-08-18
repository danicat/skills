# Search Analytics Database Schema (`~/.gsc/analytics.db`)

The `search-analytics` skill ingests Google Search Console data into a normalized SQLite database without data loss, retaining all raw JSON payloads for complete fidelity.

---

## 1. Tables

### `properties`
Stores verified Search Console properties and permission levels.
```sql
CREATE TABLE properties (
    site_url TEXT PRIMARY KEY,
    permission_level TEXT,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL
);
```

### `sitemaps`
Stores XML sitemaps submitted to Search Console, their processing status, error counts, and indexed URL counts.
```sql
CREATE TABLE sitemaps (
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
```

### `search_performance`
Stores day-by-day granular search performance by query, page, country, and device.
```sql
CREATE TABLE search_performance (
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

CREATE INDEX idx_search_perf_date ON search_performance(site_url, date);
CREATE INDEX idx_search_perf_query ON search_performance(site_url, query);
CREATE INDEX idx_search_perf_page ON search_performance(site_url, page);
CREATE INDEX idx_search_perf_country ON search_performance(site_url, country);
CREATE INDEX idx_search_perf_device ON search_performance(site_url, device);
```

### `sync_history`
Audit log of all backfill and incremental sync operations.
```sql
CREATE TABLE sync_history (
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
```

---

## 2. Analytical SQL Views

| View Name | Description | Key Columns |
| :--- | :--- | :--- |
| `v_search_performance` | Flattened granular performance with computed date dimensions | `date`, `year_month`, `day_of_week`, `query`, `page`, `country`, `device`, `clicks`, `impressions`, `ctr_pct`, `avg_position` |
| `v_daily_summary` | Daily aggregated traffic metrics per site | `date`, `distinct_queries`, `distinct_pages`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_top_queries` | Aggregated search term rankings & click share | `query`, `active_days`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_top_pages` | Aggregated landing page performance & query breadth | `page`, `ranking_queries`, `active_days`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_country_breakdown` | Geographic traffic distribution | `country`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_device_breakdown` | Desktop vs. Mobile vs. Tablet comparison | `device`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
