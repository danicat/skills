# Buffer Analytics SQLite Schema Reference

The Buffer Analytics database is stored by default in `buffer_analytics.db` in the current working directory, or at the explicit path passed to `--db <path>`. It preserves the full, unaltered JSON payloads from the Buffer API alongside indexed relational tables and high-performance SQL views.

---

## 1. Relational Tables

### `channels`
Stores connected social channel metadata.

```sql
CREATE TABLE channels (
    id TEXT PRIMARY KEY,
    organization_id TEXT,
    name TEXT,
    service TEXT,
    display_name TEXT,
    timezone TEXT,
    is_disconnected INTEGER DEFAULT 0,
    is_locked INTEGER DEFAULT 0,
    is_queue_paused INTEGER DEFAULT 0,
    avatar_url TEXT,
    external_link TEXT,
    raw_json TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT,
    synced_at TEXT NOT NULL
);
```

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `TEXT PRIMARY KEY` | Channel ID (e.g., `1234567890abcdef12345678`) |
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
Stores individual post records, scheduling state, and text copy.

```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    organization_id TEXT,
    channel_id TEXT NOT NULL,
    channel_service TEXT,
    status TEXT NOT NULL,
    text TEXT,
    external_link TEXT,
    sent_at TEXT,
    due_at TEXT,
    created_at TEXT,
    updated_at TEXT,
    scheduling_type TEXT,
    is_ai_generated INTEGER DEFAULT 0,
    thread_count INTEGER DEFAULT 0,
    first_comment TEXT,
    char_count INTEGER,
    word_count INTEGER,
    has_link INTEGER DEFAULT 0,
    has_media INTEGER DEFAULT 0,
    raw_json TEXT NOT NULL,
    synced_at TEXT NOT NULL,
    FOREIGN KEY(channel_id) REFERENCES channels(id)
);

CREATE INDEX idx_posts_sent_at ON posts(sent_at);
CREATE INDEX idx_posts_channel_service ON posts(channel_service);
CREATE INDEX idx_posts_status ON posts(status);
```

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `TEXT PRIMARY KEY` | Buffer Post ID (e.g., `abcdef1234567890abcdef12`) |
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
Normalized time-series metrics captured per post.

```sql
CREATE TABLE post_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    channel_id TEXT,
    channel_service TEXT,
    metric_type TEXT NOT NULL,
    name TEXT,
    value REAL NOT NULL DEFAULT 0,
    unit TEXT,
    description TEXT,
    recorded_at TEXT,
    synced_at TEXT NOT NULL,
    FOREIGN KEY(post_id) REFERENCES posts(id),
    UNIQUE(post_id, metric_type) ON CONFLICT REPLACE
);

CREATE INDEX idx_post_metrics_lookup ON post_metrics(post_id, metric_type);
```

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-incrementing metric ID |
| `post_id` | `TEXT NOT NULL` | Foreign key referencing `posts.id` |
| `channel_id` | `TEXT` | Channel ID |
| `channel_service` | `TEXT` | Service name (`linkedin`, `twitter`, `bluesky`) |
| `metric_type` | `TEXT NOT NULL` | Metric identifier (`impressions`, `reach`, `reactions`, `comments`, `reposts`, `clicks`, `engagementRate`) |
| `name` | `TEXT` | Human-readable metric name |
| `value` | `REAL NOT NULL` | Numerical metric value |
| `unit` | `TEXT` | Unit (`count`, `percentage`) |
| `description` | `TEXT` | Metric definition |
| `recorded_at` | `TEXT` | Timestamp when Buffer recorded the metric |
| `synced_at` | `TEXT NOT NULL` | Local sync timestamp |

---

### `post_assets`
Attached images, videos, thumbnails, and media links.

```sql
CREATE TABLE post_assets (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    type TEXT,
    mime_type TEXT,
    source TEXT,
    thumbnail TEXT,
    raw_json TEXT,
    FOREIGN KEY(post_id) REFERENCES posts(id)
);
```

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `TEXT PRIMARY KEY` | Asset ID or generated hash |
| `post_id` | `TEXT NOT NULL` | Foreign key referencing `posts.id` |
| `type` | `TEXT` | Media type (`image`, `video`, `gif`) |
| `mime_type` | `TEXT` | MIME format (`image/png`, `video/mp4`) |
| `source` | `TEXT` | Full resolution media URL |
| `thumbnail` | `TEXT` | Thumbnail image URL |
| `raw_json` | `TEXT` | Full asset payload from Buffer API |

---

### `post_tags`
Campaign and organizational labels assigned in Buffer.

```sql
CREATE TABLE post_tags (
    id TEXT,
    post_id TEXT NOT NULL,
    name TEXT,
    color TEXT,
    PRIMARY KEY(post_id, id),
    FOREIGN KEY(post_id) REFERENCES posts(id)
);
```

---

### `sync_history`
Audit log recording every backfill and incremental sync operation.

```sql
CREATE TABLE sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id TEXT,
    channel_id TEXT,
    sync_mode TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    posts_fetched INTEGER DEFAULT 0,
    posts_inserted INTEGER DEFAULT 0,
    posts_updated INTEGER DEFAULT 0,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    error_message TEXT
);
```

---

## 2. Analytical SQL Views

### `v_posts_summary`
The primary analytical view flattening posts with pivoted metrics, engagement rate calculations, and temporal dimensions.

```sql
CREATE VIEW v_posts_summary AS
SELECT 
    p.id AS post_id,
    p.channel_service AS service,
    c.name AS channel_name,
    p.status,
    p.sent_at,
    strftime('%Y-%m-%d', p.sent_at) AS sent_date,
    strftime('%Y-%m', p.sent_at) AS year_month,
    CASE strftime('%w', p.sent_at)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    CAST(strftime('%H', p.sent_at) AS INTEGER) AS hour_of_day,
    p.char_count,
    p.word_count,
    p.has_link,
    p.has_media,
    p.thread_count,
    p.external_link,
    p.text,
    COALESCE(MAX(CASE WHEN m.metric_type = 'impressions' THEN m.value END), 0) AS impressions,
    COALESCE(MAX(CASE WHEN m.metric_type = 'reach' THEN m.value END), 0) AS reach,
    COALESCE(MAX(CASE WHEN m.metric_type = 'reactions' THEN m.value END), 0) AS reactions,
    COALESCE(MAX(CASE WHEN m.metric_type = 'comments' THEN m.value END), 0) AS comments,
    COALESCE(MAX(CASE WHEN m.metric_type = 'reposts' THEN m.value END), 0) AS reposts,
    COALESCE(MAX(CASE WHEN m.metric_type = 'clicks' THEN m.value END), 0) AS clicks,
    COALESCE(MAX(CASE WHEN m.metric_type = 'engagementRate' THEN m.value END), 
        CASE 
            WHEN COALESCE(MAX(CASE WHEN m.metric_type = 'impressions' THEN m.value END), 0) > 0 
            THEN ROUND((COALESCE(MAX(CASE WHEN m.metric_type = 'reactions' THEN m.value END), 0) + 
                        COALESCE(MAX(CASE WHEN m.metric_type = 'comments' THEN m.value END), 0) + 
                        COALESCE(MAX(CASE WHEN m.metric_type = 'reposts' THEN m.value END), 0)) * 100.0 / 
                       MAX(CASE WHEN m.metric_type = 'impressions' THEN m.value END), 2)
            ELSE 0.0 
        END
    ) AS engagement_rate
FROM posts p
LEFT JOIN channels c ON p.channel_id = c.id
LEFT JOIN post_metrics m ON p.id = m.post_id
GROUP BY p.id;
```
