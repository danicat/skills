# Buffer Analytics Workflows & Operational Runbook

## Ingestion Architecture

```
Buffer API (GraphQL / REST)
          │
          │ buffer CLI (cursor pagination, --output json)
          ▼
scripts/buffer_analytics.py
          │
          ├──> channels (raw JSON + metadata)
          ├──> posts (raw JSON + indexed fields)
          ├──> post_metrics (impressions, reactions, comments, etc.)
          ├──> post_assets (images, video sources)
          ├──> post_tags (tag taxonomy)
          └──> sync_history (audit run logs)
          │
          ▼
    ~/.buffer/analytics.db (SQLite)
          │
          ▼
   v_posts_summary (Pivoted SQL View)
          │
          ▼
   Custom SQL Analytics & Reports
```

---

## Standard Workflows

### 1. Initial Historical Backfill
Paginates through the entire post history across all connected channels from newest to oldest:
```bash
python3 scripts/buffer_analytics.py sync --full
```

### 2. Routine Incremental Sync
Syncs only new posts or updates from the last recorded timestamp (with a 2-day lookback overlap to refresh engagement metrics on recent posts):
```bash
python3 scripts/buffer_analytics.py sync
```

### 3. Channel-Specific Backfill
Filter sync to a specific channel (e.g. LinkedIn only):
```bash
python3 scripts/buffer_analytics.py sync --channel-id 6949d272457dae6a34a43851
```

### 4. Date-Bounded Ingestion
Backfill a specific campaign or date window:
```bash
python3 scripts/buffer_analytics.py sync --start-date 2026-06-01T00:00:00Z --end-date 2026-08-18T00:00:00Z
```

### 5. Running Ad-Hoc SQL
Execute custom queries with output formatting:
```bash
# Markdown table output
python3 scripts/buffer_analytics.py query "SELECT * FROM v_posts_summary LIMIT 5" --format markdown

# JSON output
python3 scripts/buffer_analytics.py query "SELECT service, AVG(impressions) FROM v_posts_summary GROUP BY service" --format json

# CSV export
python3 scripts/buffer_analytics.py query "SELECT * FROM v_posts_summary WHERE status = 'sent'" --format csv > /tmp/posts_export.csv
```

### 6. Pre-Packaged Reports
```bash
python3 scripts/buffer_analytics.py report overview
python3 scripts/buffer_analytics.py report top-posts
python3 scripts/buffer_analytics.py report timing
python3 scripts/buffer_analytics.py report hooks
```
