---
name: buffer-analytics
description: >
  Collect and analyze social media data from Buffer in a local SQLite database.
  Stores your full post history and metrics across connected channels (such as
  LinkedIn, X/Twitter, Bluesky, and others) so you can run SQL queries or view
  reports on engagement, clicks, and views. Activate when you need to analyze
  social media performance, find the best days or times to post, identify
  top-performing content, or query Buffer data with SQL.
license: Apache-2.0
metadata:
  category: analytics
  tags: "buffer, social-media, engagement, impressions, posts"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.1"
  catalog: https://skills.danicat.dev
---

# Buffer analytics

The `buffer-analytics` skill pulls social post history and engagement metrics through the Buffer CLI (`@bufferapp/cli`) into a local `SQLite` database (`buffer_analytics.db`). It keeps complete raw JSON payloads alongside normalized relational tables for SQL querying.

## Available scripts
- `scripts/buffer_analytics.py`: Automated sync, reporting, and SQL CLI (`uv run scripts/buffer_analytics.py`; requires `Node.js 20+` and `@bufferapp/cli`).
- `scripts/test_buffer_analytics.py`: Unit and regression suite covering schema definitions, Markdown SQL blocks, backfill filters, and CLI commands.

---

## Quick start and primary actions

Run all operations with `scripts/buffer_analytics.py`:

```bash
# 1. Incremental sync (new posts plus a 2-day lookback metrics refresh)
uv run scripts/buffer_analytics.py sync --db path/to/database.db

# 2. Full historical backfill (paginates through full post history)
uv run scripts/buffer_analytics.py sync --full --db path/to/database.db

# 3. Run pre-packaged reports
uv run scripts/buffer_analytics.py report overview --db path/to/database.db
uv run scripts/buffer_analytics.py report top-posts --db path/to/database.db
uv run scripts/buffer_analytics.py report channels --db path/to/database.db
uv run scripts/buffer_analytics.py report timing --db path/to/database.db
uv run scripts/buffer_analytics.py report hooks --db path/to/database.db

# 4. Run an ad-hoc SQL query
uv run scripts/buffer_analytics.py query "SELECT service, AVG(impressions), AVG(reactions) FROM v_posts_summary WHERE status = 'sent' GROUP BY service" --db path/to/database.db
```

When you omit `--db`, the script defaults to `buffer_analytics.db` in the current working directory.

---

## Database schema and relational structure

The database maintains `6` tables and `1` pivoted view (`v_posts_summary`). See [`references/schema.md`](references/schema.md) for full column definitions and constraints.

### Tables

1. **`channels`**: Connected social accounts and metadata (`id`, `organization_id`, `name`, `service`, `display_name`, `timezone`, `is_disconnected`, `raw_json`, `synced_at`).
2. **`posts`**: Individual posts, scheduling status, body copy, and link flags (`id`, `channel_id`, `channel_service`, `status`, `text`, `external_link`, `sent_at`, `due_at`, `char_count`, `word_count`, `has_link`, `has_media`, `thread_count`, `raw_json`, `synced_at`).
3. **`post_metrics`**: Metrics per post (`id`, `post_id`, `channel_service`, `metric_type`, `value`, `synced_at`).
4. **`post_assets`**: Attached images, videos, and media URLs (`id`, `post_id`, `type`, `mime_type`, `source`, `thumbnail`, `raw_json`).
5. **`post_tags`**: Campaign tags assigned in Buffer (`id`, `post_id`, `name`, `color`).
6. **`sync_history`**: Audit log of sync runs (`id`, `channel_id`, `sync_mode`, `posts_fetched`, `posts_inserted`, `posts_updated`, `started_at`, `status`).

---

## Core analytical view: `v_posts_summary`

The main reporting view `v_posts_summary` pivots per-post metrics and calendar dimensions:

| Column | Type | Description |
| :--- | :--- | :--- |
| `post_id` | `TEXT` | Buffer post ID |
| `service` | `TEXT` | Social network (`linkedin`, `twitter`, `bluesky`) |
| `channel_name` | `TEXT` | Account handle or name |
| `status` | `TEXT` | `sent`, `scheduled`, or `draft` |
| `sent_at` | `TEXT` | Full ISO publication timestamp |
| `sent_date` | `TEXT` | Publication date (`YYYY-MM-DD`) |
| `year_month` | `TEXT` | Calendar month (`YYYY-MM`) |
| `day_of_week` | `TEXT` | Day name (`Monday` through `Sunday`) |
| `hour_of_day` | `INTEGER` | UTC hour (`0 to 23`) |
| `char_count` / `word_count` | `INTEGER` | Body text length metrics |
| `has_link` / `has_media` | `INTEGER` | `1` when post body/attachments contain a URL or media |
| `thread_count` | `INTEGER` | Number of items in thread |
| `impressions` | `REAL` | Total impressions or views |
| `reach` | `REAL` | Unique accounts reached |
| `reactions` | `REAL` | Likes and reactions |
| `comments` | `REAL` | Comments received |
| `reposts` | `REAL` | Shares and quotes |
| `clicks` | `REAL` | Link click count |
| `engagement_rate` | `REAL` | Engagement percentage |
| `external_link` | `TEXT` | Live post permalink |
| `text` | `TEXT` | Full post text copy |

---

## SQL analytics cookbook

Pre-tested queries live in [`references/queries.md`](references/queries.md).

### 1. Best day of the week by channel
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

### 2. Best posting hours (UTC)
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

### 3. In-body URLs vs. posts without body links
```sql
SELECT
    service,
    CASE WHEN has_link = 1 THEN 'In-body URL' ELSE 'No in-body URL' END AS placement,
    COUNT(*) AS posts,
    ROUND(AVG(impressions), 0) AS avg_impressions,
    ROUND(AVG(reactions), 1) AS avg_reactions
FROM v_posts_summary
WHERE status = 'sent' AND service = 'linkedin'
GROUP BY placement;
```

---

## Platform regime breaks and baseline hygiene

When a social network changes how its feed distributes posts, raw impression baselines before and after the shift are **not comparable (apples to oranges)**.

- **Known regime break (LinkedIn H2 2026 distribution reset):** Across H2 2026, LinkedIn shifted distribution away from broad connection-graph reach toward tighter LLM-driven Interest Graph matching (widely tracked around the `360Brew` ranking updates). Personal profiles saw steep platform-wide impression compression while engagement rates per view often stayed steady or rose.
- **Wait for a clean post-shift baseline:** Do **not** over-analyze LinkedIn H2 2026 reach drops, compare post-shift raw impressions against H1 2026 or 2025, or blame topic niches until the full half-year completes and establishes a valid post-shift baseline.
- **Separate reach compression from audience rejection:** Always check `impressions` alongside `engagement_rate` on substantive posts (`char_count >= 300`). Falling impressions with flat or rising `engagement_rate` signals a platform distribution shift, not a drop in content quality. See Section 6 of [`references/inquiry_playbook.md`](references/inquiry_playbook.md) for the diagnostic SQL template.

---

## Progressive disclosure and references

- **Full DDL schema reference**: [`references/schema.md`](references/schema.md): Exact `SQLite` table definitions, column types, constraints, and views.
- **SQL query recipes**: [`references/queries.md`](references/queries.md): Analytical queries for timing, link placement, hooks, and topic cohorts.
- **Workflows guide**: [`references/workflows.md`](references/workflows.md): Operational commands for full syncs, incremental updates, and scheduled automation.
- **Inquiry playbook**: [`references/inquiry_playbook.md`](references/inquiry_playbook.md): Statistical baselines (`SQLite` medians) and campaign retrospective guides.
