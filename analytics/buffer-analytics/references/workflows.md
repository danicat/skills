# Buffer analytics workflows and operational runbook

## Ingestion architecture

```
Buffer API (GraphQL)
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
     buffer_analytics.db (SQLite)
          │
          ▼
   v_posts_summary (Pivoted SQL View)
          │
          ▼
   Custom SQL Analytics & Reports
```

---

## Standard workflows

### 1. Initial historical backfill
Paginates through the full post history across all connected channels from newest to oldest:
```bash
uv run scripts/buffer_analytics.py sync --full --db buffer_analytics.db
```

### 2. Routine incremental sync
Syncs new posts or updates since the last recorded timestamp (with a 2-day lookback overlap to refresh engagement metrics on recent posts):
```bash
uv run scripts/buffer_analytics.py sync --db buffer_analytics.db
```

### 3. Channel-specific backfill
Filter sync to one channel (for example LinkedIn only):
```bash
uv run scripts/buffer_analytics.py sync --channel-id 1234567890abcdef12345678 --db buffer_analytics.db
```

### 4. Date-bounded ingestion
Backfill a specific campaign or date window:
```bash
uv run scripts/buffer_analytics.py sync --start-date 2026-06-01T00:00:00Z --end-date 2026-08-18T00:00:00Z --db buffer_analytics.db
```

### 5. Running ad-hoc SQL
Execute custom queries with structured formatting:
```bash
# Markdown table output
uv run scripts/buffer_analytics.py query "SELECT * FROM v_posts_summary LIMIT 5" --format markdown --db buffer_analytics.db

# JSON output
uv run scripts/buffer_analytics.py query "SELECT service, AVG(impressions) FROM v_posts_summary GROUP BY service" --format json --db buffer_analytics.db

# CSV export
uv run scripts/buffer_analytics.py query "SELECT * FROM v_posts_summary WHERE status = 'sent'" --format csv --db buffer_analytics.db > posts_export.csv
```

### 6. Pre-packaged reports
```bash
uv run scripts/buffer_analytics.py report overview --db buffer_analytics.db
uv run scripts/buffer_analytics.py report top-posts --db buffer_analytics.db
uv run scripts/buffer_analytics.py report channels --db buffer_analytics.db
uv run scripts/buffer_analytics.py report timing --db buffer_analytics.db
uv run scripts/buffer_analytics.py report hooks --db buffer_analytics.db
```
