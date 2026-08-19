---
name: buffer-analytics
description: Ingest raw Buffer social post and channel data into a local SQLite analytics database (without loss), run backfills and incremental syncs, execute ad-hoc SQL queries, and perform deep performance crunching across LinkedIn, Twitter/X, and Bluesky. Activate whenever analyzing social post performance, auditing historical metrics, finding best days/hours to post, running SQL queries over social archives, or evaluating campaign engagement.
---

# Buffer Analytics: SQLite Ingestion & SQL Query Engine

The `buffer-analytics` skill provides high-performance data warehousing and SQL querying for social media data downloaded via the Buffer CLI (`@bufferapp/cli`). It ingests raw payloads without filtering into a local SQLite database and provides a SQL interface for deep content crunching.

---

## ⚡ Quick Start & Primary Actions

All operations are driven via the bundled Python script in `scripts/buffer_analytics.py`:

```bash
# 1. Incremental Sync (New posts + 2-day lookback metrics refresh)
uv run <skill_dir>/scripts/buffer_analytics.py sync --db path/to/database.db

# 2. Full Historical Backfill (Paginates through entire history)
uv run <skill_dir>/scripts/buffer_analytics.py sync --full --db path/to/database.db

# 3. Run Pre-Packaged Reports
uv run <skill_dir>/scripts/buffer_analytics.py report overview --db path/to/database.db
uv run <skill_dir>/scripts/buffer_analytics.py report top-posts --db path/to/database.db
uv run <skill_dir>/scripts/buffer_analytics.py report channels --db path/to/database.db
uv run <skill_dir>/scripts/buffer_analytics.py report timing --db path/to/database.db
uv run <skill_dir>/scripts/buffer_analytics.py report hooks --db path/to/database.db

# 4. Run Ad-Hoc SQL Query
uv run <skill_dir>/scripts/buffer_analytics.py query "SELECT service, AVG(impressions), AVG(reactions) FROM v_posts_summary WHERE status = 'sent' GROUP BY service" --db path/to/database.db
```

If `--db` is omitted, the script defaults to `buffer_analytics.db` in the current working directory.

---

## 📊 Core Analytical Views (`v_posts_summary`)

The primary view for SQL queries is `v_posts_summary`, which automatically pivots all metrics into clean columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `post_id` | `TEXT` | Buffer Post ID |
| `service` | `TEXT` | Network (`linkedin`, `twitter`, `bluesky`) |
| `channel_name` | `TEXT` | Account handle/name |
| `status` | `TEXT` | `sent`, `scheduled`, `draft` |
| `sent_at` / `sent_date` | `TEXT` | Publication timestamp (`YYYY-MM-DD`) |
| `day_of_week` | `TEXT` | `Monday`, `Tuesday`, `Wednesday`, etc. |
| `hour_of_day` | `INTEGER` | UTC hour (0–23) |
| `char_count` / `word_count` | `INTEGER` | Length metrics |
| `has_link` / `has_media` | `INTEGER` | 1 if link/media present |
| `impressions` | `REAL` | Total views/impressions |
| `reach` | `REAL` | Unique viewers |
| `reactions` | `REAL` | Likes / reactions |
| `comments` | `REAL` | Comments count |
| `reposts` | `REAL` | Retweets / reposts |
| `clicks` | `REAL` | Link clicks |
| `engagement_rate` | `REAL` | Engagement percentage |
| `text` | `TEXT` | Full post copy |

---

## 🔍 Common SQL Analytics Recipes

### 1. Best Day of the Week by Channel
```sql
SELECT 
    service,
    day_of_week,
    COUNT(*) AS posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions,
    ROUND(AVG(engagement_rate), 2) AS avg_eng_rate
FROM v_posts_summary
WHERE status = 'sent' AND day_of_week IS NOT NULL
GROUP BY service, day_of_week
ORDER BY service, avg_impressions DESC;
```

### 2. Best Posting Hours (UTC)
```sql
SELECT 
    service,
    hour_of_day || ':00 UTC' AS hour,
    COUNT(*) AS posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions
FROM v_posts_summary
WHERE status = 'sent' AND impressions > 0
GROUP BY service, hour_of_day
HAVING COUNT(*) >= 3
ORDER BY avg_impressions DESC;
```

### 3. Impact of Links in Body vs. First Comment
```sql
SELECT 
    service,
    CASE WHEN has_link = 1 THEN 'Link in Body' ELSE 'No Link / First Comment' END AS placement,
    COUNT(*) AS posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions
FROM v_posts_summary
WHERE status = 'sent' AND service = 'linkedin'
GROUP BY placement;
```

---

## 🛠️ CLI Reference

```text
usage: buffer_analytics.py [-h] [--db DB_PATH] [-q QUERY] [--format {table,markdown,json,csv}] {sync,query,report,schema} ...

Subcommands:
  sync      Sync channels and posts into SQLite (--full for historical backfill)
  query     Execute SQL query against the database
  report    Run pre-canned analytical reports (overview, top-posts, channels, timing, hooks)
  schema    Print the database DDL schema and analytical views
```
