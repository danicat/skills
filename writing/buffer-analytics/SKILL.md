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

## 🗄️ Database Schema & Relational Structure

The database maintains 6 normalized relational tables and high-performance SQL views. Detailed DDL and schema definitions are in [`references/schema.md`](references/schema.md).

### Tables

1. **`channels`**: Connected social accounts and metadata.
   - Key columns: `id` (PK), `organization_id`, `name`, `service` (`linkedin`, `twitter`, `bluesky`), `display_name`, `timezone`, `is_disconnected`, `raw_json`, `synced_at`.
2. **`posts`**: Individual posts, scheduling state, and content.
   - Key columns: `id` (PK), `channel_id` (FK), `channel_service`, `status` (`sent`, `scheduled`, `draft`), `text`, `external_link`, `sent_at`, `due_at`, `char_count`, `word_count`, `has_link`, `has_media`, `thread_count`, `raw_json`, `synced_at`.
3. **`post_metrics`**: Time-series metrics per post.
   - Key columns: `id` (PK), `post_id` (FK), `channel_service`, `metric_type` (`impressions`, `reach`, `reactions`, `comments`, `reposts`, `clicks`, `engagementRate`), `value`, `synced_at`.
4. **`post_assets`**: Attached images, videos, and media URLs.
   - Key columns: `id` (PK), `post_id` (FK), `type`, `mime_type`, `source`, `thumbnail`, `raw_json`.
5. **`post_tags`**: Campaign and topic tags assigned in Buffer.
   - Key columns: `id`, `post_id` (FK), `name`, `color`.
6. **`sync_history`**: Audit trail of all sync executions.
   - Key columns: `id` (PK), `channel_id`, `sync_mode`, `posts_fetched`, `posts_inserted`, `posts_updated`, `started_at`, `status`.

---

## 📊 Core Analytical View: `v_posts_summary`

The primary view for SQL analytics is `v_posts_summary`, which pivots metrics and computes calendar dimensions:

| Column | Type | Description |
| :--- | :--- | :--- |
| `post_id` | `TEXT` | Buffer Post ID |
| `service` | `TEXT` | Network (`linkedin`, `twitter`, `bluesky`) |
| `channel_name` | `TEXT` | Account handle/name |
| `status` | `TEXT` | `sent`, `scheduled`, `draft` |
| `sent_at` | `TEXT` | Full ISO timestamp |
| `sent_date` | `TEXT` | Publication date (`YYYY-MM-DD`) |
| `year_month` | `TEXT` | Calendar month (`YYYY-MM`) |
| `day_of_week` | `TEXT` | Day name (`Monday`, `Tuesday`, etc.) |
| `hour_of_day` | `INTEGER` | UTC hour (0–23) |
| `char_count` / `word_count` | `INTEGER` | Text length metrics |
| `has_link` / `has_media` | `INTEGER` | 1 if link or media is present |
| `thread_count` | `INTEGER` | Number of posts in thread |
| `impressions` | `REAL` | Total impressions / views |
| `reach` | `REAL` | Unique accounts reached |
| `reactions` | `REAL` | Likes and reactions |
| `comments` | `REAL` | Comments received |
| `reposts` | `REAL` | Retweets / reshares |
| `clicks` | `REAL` | Link click count |
| `engagement_rate` | `REAL` | Total engagement % |
| `external_link` | `TEXT` | Live post URL |
| `text` | `TEXT` | Full text copy |

---

## 🔍 SQL Analytics Cookbook

Pre-tested SQL query recipes are documented in [`references/queries.md`](references/queries.md).

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

## 📚 Progressive Disclosure & References

- **Full DDL Schema Reference**: [`references/schema.md`](references/schema.md) — Exact SQL table definitions, column types, constraints, and views.
- **SQL Query Recipes**: [`references/queries.md`](references/queries.md) — Analytical queries for timing, link penalties, hooks, and topic cohorts.
- **Workflows Guide**: [`references/workflows.md`](references/workflows.md) — Operational guidance for periodic backfills and cron automations.
- **Inquiry Playbook**: [`references/inquiry_playbook.md`](references/inquiry_playbook.md) — Strategic questions for campaign and social retrospectives.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Test cases for validating ingestion and analytical queries.
