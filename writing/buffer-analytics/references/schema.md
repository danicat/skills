# Buffer Analytics SQLite Schema Reference

The Buffer Analytics database is stored by default at `~/.buffer/analytics.db`. It preserves the full, unaltered JSON payloads from the Buffer API alongside indexed relational tables and high-performance SQL views.

---

## 1. Tables

### `channels`
Stores connected social channel metadata.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `TEXT PRIMARY KEY` | Channel ID (e.g., `6949d272457dae6a34a43851`) |
| `organization_id` | `TEXT` | Buffer Organization ID |
| `name` | `TEXT` | Channel username/handle |
| `service` | `TEXT` | Social network (`linkedin`, `twitter`, `bluesky`, `instagram`, `facebook`) |
| `display_name` | `TEXT` | Formatted display name |
| `timezone` | `TEXT` | Channel timezone string (e.g., `Europe/London`) |
| `is_disconnected` | `INTEGER` | 1 if account is disconnected |
| `is_locked` | `INTEGER` | 1 if locked by plan limits |
| `is_queue_paused` | `INTEGER` | 1 if queue is paused |
| `avatar_url` | `TEXT` | Profile avatar URL |
| `external_link` | `TEXT` | Profile URL on the social network |
| `raw_json` | `TEXT NOT NULL` | Complete raw JSON channel payload from Buffer |
| `created_at` | `TEXT` | ISO-8601 creation timestamp |
| `updated_at` | `TEXT` | ISO-8601 update timestamp |
| `synced_at` | `TEXT NOT NULL` | Timestamp of local database sync |

---

### `posts`
Stores individual post records, scheduling state, and content.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `TEXT PRIMARY KEY` | Buffer Post ID (e.g., `6a83963a54c341291db5c8e2`) |
| `organization_id` | `TEXT` | Buffer Organization ID |
| `channel_id` | `TEXT NOT NULL` | Foreign key referencing `channels.id` |
| `channel_service` | `TEXT` | Service identifier (`linkedin`, `twitter`, `bluesky`) |
| `status` | `TEXT NOT NULL` | Post status (`sent`, `scheduled`, `draft`, `error`) |
| `text` | `TEXT` | Full text copy of the post |
| `external_link` | `TEXT` | Live post URL on the social network |
| `sent_at` | `TEXT` | ISO-8601 timestamp when post was published |
| `due_at` | `TEXT` | Scheduled posting time |
| `created_at` | `TEXT` | Timestamp when post was created in Buffer |
| `updated_at` | `TEXT` | Timestamp when post was last modified |
| `scheduling_type` | `TEXT` | Buffer scheduling mode (`queue`, `custom_time`, `share_now`) |
| `is_ai_generated` | `INTEGER` | 1 if flagged as AI generated in Buffer |
| `thread_count` | `INTEGER` | Number of posts in thread (e.g. on Bluesky/Twitter) |
| `first_comment` | `TEXT` | Text of scheduled first comment |
| `char_count` | `INTEGER` | Character length of post text |
| `word_count` | `INTEGER` | Word count of post text |
| `has_link` | `INTEGER` | 1 if post contains URLs or external links |
| `has_media` | `INTEGER` | 1 if post has attached images or videos |
| `raw_json` | `TEXT NOT NULL` | Complete raw post object from Buffer API |
| `synced_at` | `TEXT NOT NULL` | Local sync timestamp |

---

### `post_metrics`
Stores all metrics captured per post.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-incrementing metric ID |
| `post_id` | `TEXT NOT NULL` | Foreign key referencing `posts.id` |
| `channel_id` | `TEXT` | Channel ID |
| `channel_service` | `TEXT` | Service name |
| `metric_type` | `TEXT NOT NULL` | Metric identifier (`impressions`, `reach`, `reactions`, `comments`, `reposts`, `clicks`, `engagementRate`) |
| `name` | `TEXT` | Human-readable metric name |
| `value` | `REAL NOT NULL` | Numerical metric value |
| `unit` | `TEXT` | Unit (`count`, `percentage`) |
| `description` | `TEXT` | Metric definition |
| `recorded_at` | `TEXT` | Timestamp when Buffer recorded the metric |
| `synced_at` | `TEXT NOT NULL` | Local sync timestamp |

---

### `sync_history`
Audit log of all backfill and incremental sync executions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Log ID |
| `organization_id` | `TEXT` | Organization ID |
| `channel_id` | `TEXT` | Filtered channel ID (or null for all) |
| `sync_mode` | `TEXT NOT NULL` | `full` or `incremental` |
| `start_date` | `TEXT` | Start date filter if specified |
| `end_date` | `TEXT` | End date filter if specified |
| `posts_fetched` | `INTEGER` | Number of items returned by Buffer API |
| `posts_inserted` | `INTEGER` | New posts inserted |
| `posts_updated` | `INTEGER` | Existing posts updated |
| `started_at` | `TEXT NOT NULL` | Sync start time |
| `finished_at` | `TEXT` | Sync completion time |
| `status` | `TEXT NOT NULL` | `SUCCESS` or `FAILED` |
| `error_message` | `TEXT` | Error details if failed |

---

## 2. Analytical Views

### `v_posts_summary`
The primary analytical view flattening posts with pivoted metrics and calculated temporal dimensions.

```sql
SELECT 
    post_id,
    service,
    channel_name,
    status,
    sent_at,
    sent_date,        -- YYYY-MM-DD
    year_month,       -- YYYY-MM
    day_of_week,      -- Monday, Tuesday, ...
    hour_of_day,      -- 0-23 UTC
    char_count,
    word_count,
    has_link,
    has_media,
    thread_count,
    external_link,
    text,
    impressions,
    reach,
    reactions,
    comments,
    reposts,
    clicks,
    engagement_rate
FROM v_posts_summary;
```
