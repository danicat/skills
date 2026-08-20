# Google Analytics 4 SQLite Schema Reference

The Google Analytics database is created and maintained automatically by `scripts/google_analytics.py`. Database tables, indexes, and analytical views are provisioned during sync operations.

---

## 1. Relational Tables

### `daily_pages`
Stores daily pageviews, active users, sessions, active dwell time, and bounce rate broken down by country, device, and traffic source.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `property_id` | `TEXT` | NOT NULL | GA4 Property ID |
| `date` | `TEXT` | NOT NULL | Activity date (`YYYY-MM-DD`) |
| `page_path` | `TEXT` | NOT NULL | URL path component (e.g. `/blog/post-1/`) |
| `page_title` | `TEXT` | | HTML page title |
| `country` | `TEXT` | | Visitor country name |
| `device_category` | `TEXT` | | Device category (`desktop`, `mobile`, `tablet`) |
| `source_medium` | `TEXT` | | Acquisition source / medium (e.g. `google / organic`) |
| `screen_page_views`| `INTEGER` | DEFAULT 0 | Total pageviews |
| `active_users` | `INTEGER` | DEFAULT 0 | Count of distinct active visitors |
| `sessions` | `INTEGER` | DEFAULT 0 | Number of visitor sessions |
| `user_engagement_duration` | `REAL` | DEFAULT 0.0 | Total active dwell time in seconds |
| `bounce_rate` | `REAL` | DEFAULT 0.0 | Fraction of unengaged sessions (0.0 to 1.0) |
| `raw_json` | `TEXT` | | Complete raw API row JSON payload |
| `synced_at` | `TEXT` | | Timestamp of local database sync |

*Unique Constraint:* `(property_id, date, page_path, country, device_category, source_medium)`

---

### `daily_traffic`
Stores daily acquisition channels, source/medium pairs, new users, engaged sessions, and dwell duration.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `property_id` | `TEXT` | NOT NULL | GA4 Property ID |
| `date` | `TEXT` | NOT NULL | Activity date (`YYYY-MM-DD`) |
| `session_source_medium` | `TEXT` | NOT NULL | Source / Medium (e.g. `direct / none`, `linkedin.com / referral`) |
| `session_default_channel_group` | `TEXT` | | High-level channel (`Direct`, `Organic Search`, `Organic Social`, `Referral`) |
| `country` | `TEXT` | | Visitor country name |
| `device_category` | `TEXT` | | Device category |
| `sessions` | `INTEGER` | DEFAULT 0 | Total sessions initiated |
| `active_users` | `INTEGER` | DEFAULT 0 | Total distinct active visitors |
| `new_users` | `INTEGER` | DEFAULT 0 | First-time visitors |
| `engaged_sessions`| `INTEGER` | DEFAULT 0 | Sessions lasting >10s, with 2+ views, or conversions |
| `user_engagement_duration` | `REAL` | DEFAULT 0.0 | Total active dwell time in seconds |
| `bounce_rate` | `REAL` | DEFAULT 0.0 | Bounce rate fraction |
| `raw_json` | `TEXT` | | Raw API row JSON payload |
| `synced_at` | `TEXT` | | Timestamp of local database sync |

*Unique Constraint:* `(property_id, date, session_source_medium, session_default_channel_group, country, device_category)`

---

### `daily_events`
Stores daily user engagement events (`scroll`, `click`, `first_visit`, `user_engagement`, `page_view`).

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `property_id` | `TEXT` | NOT NULL | GA4 Property ID |
| `date` | `TEXT` | NOT NULL | Activity date (`YYYY-MM-DD`) |
| `event_name` | `TEXT` | NOT NULL | Event name identifier |
| `page_path` | `TEXT` | | URL path where event occurred |
| `country` | `TEXT` | | Visitor country |
| `device_category` | `TEXT` | | Device category |
| `event_count` | `INTEGER` | DEFAULT 0 | Total event occurrences |
| `total_users` | `INTEGER` | DEFAULT 0 | Unique users triggering the event |
| `raw_json` | `TEXT` | | Raw API row JSON payload |
| `synced_at` | `TEXT` | | Timestamp of local database sync |

---

### `outbound_clicks`
Stores external link exit destinations, referring pages, and user clicks.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique row ID |
| `property_id` | `TEXT` | NOT NULL | GA4 Property ID |
| `date` | `TEXT` | NOT NULL | Activity date (`YYYY-MM-DD`) |
| `link_url` | `TEXT` | NOT NULL | Destination URL clicked |
| `page_path` | `TEXT` | | Referring page path |
| `country` | `TEXT` | | Visitor country |
| `event_count` | `INTEGER` | DEFAULT 0 | Total clicks on destination link |
| `total_users` | `INTEGER` | DEFAULT 0 | Unique visitors clicking destination |
| `raw_json` | `TEXT` | | Raw API row JSON payload |
| `synced_at` | `TEXT` | | Timestamp of local database sync |

---

### `properties`
Verified GA4 property metadata, time zone, and account configuration.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `property_id` | `TEXT` | PRIMARY KEY | GA4 Property numeric ID (e.g. `123456789`) |
| `name` | `TEXT` | | GA4 resource name (`properties/123456789`) |
| `account_id` | `TEXT` | | Parent GA4 Account ID |
| `display_name` | `TEXT` | | Human-readable property title |
| `industry_category`| `TEXT` | | Industry category classification |
| `time_zone` | `TEXT` | | Reporting timezone string (e.g. `UTC`, `America/New_York`) |
| `currency_code` | `TEXT` | | Reporting currency code (e.g. `USD`) |
| `service_level` | `TEXT` | | GA4 service level (`GOOGLE_ANALYTICS_STANDARD`, `GOOGLE_ANALYTICS_360`) |
| `create_time` | `TEXT` | | Creation timestamp |
| `update_time` | `TEXT` | | Modification timestamp |
| `raw_json` | `TEXT` | | Complete raw JSON property payload |
| `last_synced_at` | `TEXT` | | Timestamp of local database sync |

---

### `site_milestones`
Tracks release milestones, major blog launches, and architectural updates for cohort impact analysis.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `commit_hash` | `TEXT` | PRIMARY KEY | Git commit hash or unique milestone identifier |
| `event_date` | `DATE` | NOT NULL | Milestone date (`YYYY-MM-DD`) |
| `title` | `TEXT` | NOT NULL | Short title of the release / milestone |
| `description` | `TEXT` | | Detailed context or release notes |
| `category` | `TEXT` | | Category (`release`, `article`, `campaign`, `major_feature`) |
| `scope` | `TEXT` | | Scope tag (`site`, `blog`, `oss`) |
| `author` | `TEXT` | | Author name or handle |
| `created_at` | `TIMESTAMP`| DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

---

### `sync_history`
Audit log recording every backfill and incremental sync operation.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique sync run ID |
| `property_id` | `TEXT` | NOT NULL | GA4 Property ID |
| `sync_type` | `TEXT` | NOT NULL | Sync type (`incremental`, `full`, `range`) |
| `start_date` | `TEXT` | | Starting date of sync window |
| `end_date` | `TEXT` | | Ending date of sync window |
| `pages_synced` | `INTEGER` | DEFAULT 0 | Count of page rows synced |
| `traffic_synced` | `INTEGER` | DEFAULT 0 | Count of traffic rows synced |
| `events_synced` | `INTEGER` | DEFAULT 0 | Count of event rows synced |
| `outbound_synced`| `INTEGER` | DEFAULT 0 | Count of outbound click rows synced |
| `status` | `TEXT` | NOT NULL | Status (`success`, `failed`, `running`) |
| `error_message` | `TEXT` | | Error details if failed |
| `started_at` | `TEXT` | NOT NULL | Start timestamp |
| `finished_at` | `TEXT` | | Completion timestamp |

---

## 2. Analytical SQL Views

### `v_daily_summary`
Daily aggregated traffic totals across all landing pages.

| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | `TEXT` | Activity date (`YYYY-MM-DD`) |
| `total_sessions` | `INTEGER` | Sum of sessions |
| `total_active_users` | `INTEGER` | Sum of active visitors |
| `total_page_views` | `INTEGER` | Sum of pageviews |
| `total_engagement_min`| `REAL` | Total active dwell time in minutes |
| `avg_bounce_pct` | `REAL` | Average bounce rate percentage |

---

### `v_page_performance`
Page-level rollup with views, active users, average dwell time, and bounce rate.

| Column | Type | Description |
| :--- | :--- | :--- |
| `page_path` | `TEXT` | URL path |
| `page_title` | `TEXT` | Page title tag |
| `total_views` | `INTEGER` | Total pageviews |
| `total_users` | `INTEGER` | Distinct active visitors |
| `total_sessions` | `INTEGER` | Visitor sessions |
| `avg_dwell_sec` | `REAL` | Average active dwell time per user (seconds) |
| `total_dwell_min`| `REAL` | Total cumulative active dwell time (minutes) |
| `avg_bounce_pct` | `REAL` | Average bounce rate percentage |

---

### `v_channel_performance`
Acquisition channels and source/medium pairs with sessions, new users, and engagement rate %.

| Column | Type | Description |
| :--- | :--- | :--- |
| `channel_group` | `TEXT` | High-level channel (`Direct`, `Organic Search`, `Referral`) |
| `source_medium` | `TEXT` | Specific source / medium |
| `total_sessions` | `INTEGER` | Total sessions initiated |
| `total_users` | `INTEGER` | Total active visitors |
| `total_new_users` | `INTEGER` | First-time visitors |
| `total_engaged_sessions`| `INTEGER` | Count of engaged sessions |
| `engagement_rate_pct` | `REAL` | Engagement percentage (`engaged_sessions / sessions * 100`) |
| `total_dwell_min`| `REAL` | Total active dwell time in minutes |
| `avg_bounce_pct` | `REAL` | Average bounce rate percentage |

---

### `v_geo_breakdown`
Geographical ranking by country with sessions, pageviews, and dwell time.

| Column | Type | Description |
| :--- | :--- | :--- |
| `country` | `TEXT` | Country name |
| `total_sessions` | `INTEGER` | Total sessions |
| `total_users` | `INTEGER` | Total active visitors |
| `total_page_views` | `INTEGER` | Total pageviews |
| `avg_dwell_sec` | `REAL` | Average dwell time per user (seconds) |
| `avg_bounce_pct` | `REAL` | Average bounce rate percentage |

---

### `v_events_summary`
Aggregate event interaction counts.

| Column | Type | Description |
| :--- | :--- | :--- |
| `event_name` | `TEXT` | Event name identifier |
| `total_events` | `INTEGER` | Total event occurrences |
| `total_users` | `INTEGER` | Count of distinct users triggering event |

---

### `v_outbound_links`
Outbound exit destinations ranked by click counts and unique referring pages.

| Column | Type | Description |
| :--- | :--- | :--- |
| `link_url` | `TEXT` | External destination URL |
| `total_clicks` | `INTEGER` | Total click count |
| `total_users` | `INTEGER` | Distinct users who clicked |
| `referring_pages_count`| `INTEGER` | Number of distinct local pages linking to destination |

---

### `v_milestone_impact`
Pre vs post milestone comparison of page traffic and engagement.

| Column | Type | Description |
| :--- | :--- | :--- |
| `commit_hash` | `TEXT` | Milestone identifier |
| `milestone_title` | `TEXT` | Title of the milestone |
| `milestone_date` | `DATE` | Event date (`YYYY-MM-DD`) |
| `cohort` | `TEXT` | `Pre-Milestone` or `Post-Milestone` |
| `days_tracked` | `INTEGER` | Days tracked in cohort |
| `total_views` | `INTEGER` | Total pageviews in cohort |
| `total_users` | `INTEGER` | Total active visitors in cohort |
| `total_sessions` | `INTEGER` | Total sessions in cohort |
| `avg_engagement_sec` | `REAL` | Average active engagement duration (seconds) |
| `avg_bounce_pct` | `REAL` | Average bounce rate percentage |
