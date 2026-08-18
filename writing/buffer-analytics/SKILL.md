---
name: buffer-analytics
description: Ingest raw Buffer social post and channel data into a local SQLite analytics database (without loss), run backfills and incremental syncs, execute ad-hoc SQL queries, and perform deep performance crunching across LinkedIn, Twitter/X, and Bluesky. Activate whenever analyzing social post performance, auditing historical metrics, finding best days/hours to post, running SQL queries over social archives, or evaluating campaign engagement.
---

# Buffer Analytics: SQLite Ingestion & SQL Query Engine

The `buffer-analytics` skill provides high-performance data warehousing and SQL querying for social media data downloaded via the Buffer CLI (`@bufferapp/cli`). It ingests raw payloads without filtering into a local SQLite database (`buffer_analytics.db` or `$XDG_DATA_HOME/buffer-analytics/analytics.db`) and provides a SQL interface for deep content crunching.

---

## ⚡ Quick Start & Primary Actions

All operations are driven via the bundled Python script:

```bash
# 1. Incremental Sync (New posts + 2-day lookback metrics refresh)
python3 scripts/buffer_analytics.py sync

# 2. Full Historical Backfill (Paginates through entire history)
python3 scripts/buffer_analytics.py sync --full

# 3. Run Pre-Packaged Reports
python3 scripts/buffer_analytics.py report overview
python3 scripts/buffer_analytics.py report top-posts
python3 scripts/buffer_analytics.py report timing
python3 scripts/buffer_analytics.py report hooks

# 4. Run Ad-Hoc SQL Query
python3 scripts/buffer_analytics.py query "SELECT service, AVG(impressions), AVG(reactions) FROM v_posts_summary WHERE status = 'sent' GROUP BY service"
```

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
WHERE status = 'sent' AND impressions > 0
GROUP BY service, has_link;
```

---

## 🛠️ Progressive Disclosure & References

- **Database Schema Reference**: [`references/schema.md`](references/schema.md) — Full DDL tables (`channels`, `posts`, `post_metrics`, `post_assets`, `post_tags`, `sync_history`).
- **SQL Query Cookbook**: [`references/queries.md`](references/queries.md) — Advanced SQL recipes (topic clustering, word count cohorts, engagement distributions).
- **Operational Runbook**: [`references/workflows.md`](references/workflows.md) — Cursor pagination, error recovery, and backfill options.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Test cases for validating skill triggers and query execution.
