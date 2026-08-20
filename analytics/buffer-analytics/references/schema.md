# Buffer Analytics SQLite Schema Reference

The Buffer Analytics database is created and maintained automatically by `scripts/buffer_analytics.py`. Database tables, indexes, and analytical views are provisioned during sync operations.

---

## 1. Relational Tables

### `channels`
Stores connected social media channel profiles and account configuration.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | PRIMARY KEY | Unique Buffer channel ID (e.g. `1234567890abcdef12345678`) |
| `organization_id` | `TEXT` | | Buffer organization ID |
| `name` | `TEXT` | | Channel handle / username |
| `service` | `TEXT` | | Social network (`linkedin`, `twitter`, `bluesky`, `instagram`, `facebook`) |
| `display_name` | `TEXT` | | Formatted account display name |
| `timezone` | `TEXT` | | Account timezone string (e.g. `UTC`, `America/New_York`) |
| `is_disconnected` | `INTEGER` | DEFAULT 0 | 1 if account is disconnected |
| `is_locked` | `INTEGER` | DEFAULT 0 | 1 if account is locked by plan limits |
| `is_queue_paused` | `INTEGER` | DEFAULT 0 | 1 if publishing queue is paused |
| `avatar_url` | `TEXT` | | URL of profile picture |
| `external_link` | `TEXT` | | URL of the social media profile |
| `raw_json` | `TEXT` | NOT NULL | Complete raw JSON payload from Buffer API |
| `created_at` | `TEXT` | | ISO-8601 creation timestamp |
| `updated_at` | `TEXT` | | ISO-8601 modification timestamp |
| `synced_at` | `TEXT` | NOT NULL | Timestamp of local database sync |

---

### `posts`
Stores individual social media posts, scheduling lifecycle status, and text content.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | PRIMARY KEY | Unique Buffer post ID |
| `organization_id` | `TEXT` | | Buffer organization ID |
| `channel_id` | `TEXT` | NOT NULL, FK -> `channels(id)` | Associated social channel ID |
| `channel_service` | `TEXT` | | Service name (`linkedin`, `twitter`, `bluesky`) |
| `status` | `TEXT` | NOT NULL | Post status (`sent`, `scheduled`, `draft`, `error`) |
| `text` | `TEXT` | | Full text copy of the post |
| `external_link` | `TEXT` | | URL of the live published post on the network |
| `sent_at` | `TEXT` | | ISO-8601 publication timestamp |
| `due_at` | `TEXT` | | Scheduled publication timestamp |
| `created_at` | `TEXT` | | Creation timestamp |
| `updated_at` | `TEXT` | | Modification timestamp |
| `scheduling_type` | `TEXT` | | Scheduling method (`queue`, `custom_time`, `share_now`) |
| `is_ai_generated` | `INTEGER` | DEFAULT 0 | 1 if marked AI generated in Buffer |
| `thread_count` | `INTEGER` | DEFAULT 0 | Number of posts in thread |
| `first_comment` | `TEXT` | | Scheduled first comment text |
| `char_count` | `INTEGER` | | Total character count of post body |
| `word_count` | `INTEGER` | | Total word count of post body |
| `has_link` | `INTEGER` | DEFAULT 0 | 1 if post contains URLs or external links |
| `has_media` | `INTEGER` | DEFAULT 0 | 1 if post contains image or video attachments |
| `raw_json` | `TEXT` | NOT NULL | Complete raw JSON payload from Buffer API |
| `synced_at` | `TEXT` | NOT NULL | Timestamp of local database sync |

---

### `post_metrics`
Stores normalized engagement metrics recorded per post.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique metric record ID |
| `post_id` | `TEXT` | NOT NULL, FK -> `posts(id)` | Associated post ID |
| `channel_id` | `TEXT` | | Associated channel ID |
| `channel_service` | `TEXT` | | Service name (`linkedin`, `twitter`, `bluesky`) |
| `metric_type` | `TEXT` | NOT NULL | Metric key (`impressions`, `reach`, `reactions`, `comments`, `reposts`, `clicks`, `engagementRate`) |
| `name` | `TEXT` | | Human-readable metric name |
| `value` | `REAL` | NOT NULL, DEFAULT 0 | Metric numeric value |
| `unit` | `TEXT` | | Unit (`count`, `percentage`) |
| `description` | `TEXT` | | Metric description |
| `recorded_at` | `TEXT` | | Timestamp recorded by Buffer |
| `synced_at` | `TEXT` | NOT NULL | Timestamp of local database sync |

---

### `post_assets`
Stores media attachments (images, videos, thumbnails) linked to posts.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | PRIMARY KEY | Asset identifier or URL hash |
| `post_id` | `TEXT` | NOT NULL, FK -> `posts(id)` | Associated post ID |
| `type` | `TEXT` | | Media type (`image`, `video`, `gif`) |
| `mime_type` | `TEXT` | | MIME format (e.g. `image/png`, `video/mp4`) |
| `source` | `TEXT` | | Full-resolution asset URL |
| `thumbnail` | `TEXT` | | Thumbnail asset URL |
| `raw_json` | `TEXT` | | Complete asset JSON payload |

---

### `post_tags`
Stores organizational tags and campaign labels assigned in Buffer.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `TEXT` | PRIMARY KEY (post_id, id) | Tag identifier |
| `post_id` | `TEXT` | PRIMARY KEY (post_id, id), FK -> `posts(id)` | Associated post ID |
| `name` | `TEXT` | | Tag name / label |
| `color` | `TEXT` | | Hex color code |

---

### `sync_history`
Audit log recording every backfill and incremental sync operation.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique sync run ID |
| `organization_id` | `TEXT` | | Buffer organization ID |
| `channel_id` | `TEXT` | | Specific channel ID if scoped |
| `sync_mode` | `TEXT` | NOT NULL | Sync type (`incremental`, `full`) |
| `start_date` | `TEXT` | | Starting date of sync window |
| `end_date` | `TEXT` | | Ending date of sync window |
| `posts_fetched` | `INTEGER` | DEFAULT 0 | Count of records fetched from API |
| `posts_inserted` | `INTEGER` | DEFAULT 0 | Count of newly inserted posts |
| `posts_updated` | `INTEGER` | DEFAULT 0 | Count of existing posts refreshed |
| `started_at` | `TEXT` | NOT NULL | Start timestamp |
| `finished_at` | `TEXT` | | Completion timestamp |
| `status` | `TEXT` | NOT NULL | Status (`success`, `failed`, `running`) |
| `error_message` | `TEXT` | | Error details if failed |

---

## 2. Analytical SQL Views

### `v_posts_summary`
Primary analytical view flattening posts with pivoted metrics, engagement rate calculations, and temporal calendar dimensions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `post_id` | `TEXT` | Unique post ID |
| `service` | `TEXT` | Social network (`linkedin`, `twitter`, `bluesky`) |
| `channel_name` | `TEXT` | Channel username / handle |
| `status` | `TEXT` | Post status (`sent`, `scheduled`, `draft`) |
| `sent_at` | `TEXT` | Full ISO timestamp of publication |
| `sent_date` | `TEXT` | Date string (`YYYY-MM-DD`) |
| `year_month` | `TEXT` | Year and month string (`YYYY-MM`) |
| `day_of_week` | `TEXT` | Full day name (`Monday`, `Tuesday`, `Wednesday`, etc.) |
| `hour_of_day` | `INTEGER` | UTC hour of publication (0 to 23) |
| `char_count` | `INTEGER` | Body text character count |
| `word_count` | `INTEGER` | Body text word count |
| `has_link` | `INTEGER` | 1 if external links are present in text |
| `has_media` | `INTEGER` | 1 if image or video attachments are present |
| `thread_count` | `INTEGER` | Number of posts in thread |
| `external_link` | `TEXT` | Live social network URL |
| `text` | `TEXT` | Full text copy of post |
| `impressions` | `REAL` | Total post views / impressions |
| `reach` | `REAL` | Unique viewers reached |
| `reactions` | `REAL` | Total likes and reactions |
| `comments` | `REAL` | Total comments received |
| `reposts` | `REAL` | Total retweets / reshares |
| `clicks` | `REAL` | Total link clicks |
| `engagement_rate` | `REAL` | Overall engagement percentage |
