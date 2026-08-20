# Google Search Console SQLite Schema Reference

The Search Analytics database is created and maintained automatically by `scripts/search_analytics.py`. Database tables, indexes, and analytical views are provisioned during sync operations.

---

## 1. Relational Tables

### `search_performance`
Stores daily granular search performance partitioned by query, page, country, and device.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| `site_url` | `TEXT` | NOT NULL | Search Console property URL |
| `date` | `TEXT` | NOT NULL | Date of search activity (`YYYY-MM-DD`) |
| `query` | `TEXT` | NOT NULL, DEFAULT '' | Search query keyword |
| `page` | `TEXT` | NOT NULL, DEFAULT '' | Full URL of the landing page shown in SERP |
| `country` | `TEXT` | NOT NULL, DEFAULT '' | Three-letter ISO country code (`usa`, `gbr`, `jpn`, `bra`) |
| `device` | `TEXT` | NOT NULL, DEFAULT '' | Device category (`DESKTOP`, `MOBILE`, `TABLET`) |
| `search_appearance` | `TEXT` | NOT NULL, DEFAULT '' | Rich result type if applicable |
| `search_type` | `TEXT` | NOT NULL, DEFAULT 'web' | Search channel (`web`, `image`, `video`, `news`) |
| `clicks` | `REAL` | NOT NULL, DEFAULT 0 | Total clicks generated |
| `impressions` | `REAL` | NOT NULL, DEFAULT 0 | Total impressions displayed in SERP |
| `ctr` | `REAL` | NOT NULL, DEFAULT 0 | Click-through rate (fraction: `clicks / impressions`) |
| `position` | `REAL` | NOT NULL, DEFAULT 0 | Average ranking position (1-indexed, e.g. 1.0 = top) |
| `raw_json` | `TEXT` | NOT NULL | Complete raw API row JSON payload |
| `synced_at` | `TEXT` | NOT NULL | Local sync timestamp |

*Unique Constraint:* `(site_url, date, query, page, country, device, search_appearance, search_type)`

---

### `properties`
Stores verified Search Console property URLs and access permissions.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `site_url` | `TEXT` | PRIMARY KEY | Property URL (e.g. `https://example.com/` or `sc-domain:example.com`) |
| `permission_level` | `TEXT` | | Access tier (`siteOwner`, `siteFullUser`, `siteRestrictedUser`) |
| `raw_json` | `TEXT` | NOT NULL | Complete raw JSON payload from Search Console API |
| `synced_at` | `TEXT` | NOT NULL | Local sync timestamp |

---

### `sitemaps`
Stores XML sitemaps submitted to Search Console, processing status, and indexing numbers.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `site_url` | `TEXT` | PRIMARY KEY (site_url, path), FK -> `properties(site_url)` | Parent property URL |
| `path` | `TEXT` | PRIMARY KEY (site_url, path) | Full sitemap URL |
| `type` | `TEXT` | | Sitemap type (`sitemap`, `feedIndex`) |
| `last_downloaded` | `TEXT` | | Timestamp when Googlebot last downloaded the XML |
| `last_submitted` | `TEXT` | | Timestamp when sitemap was submitted |
| `errors` | `INTEGER` | DEFAULT 0 | Number of parsing errors reported |
| `warnings` | `INTEGER` | DEFAULT 0 | Number of non-fatal warnings reported |
| `indexed_count` | `INTEGER` | | Total count of indexed URLs from this sitemap |
| `raw_json` | `TEXT` | NOT NULL | Complete raw API payload |
| `synced_at` | `TEXT` | NOT NULL | Local sync timestamp |

---

### `site_milestones`
Tracks release milestones, major publications, and architectural launches for cohort impact analysis.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `commit_hash` | `TEXT` | PRIMARY KEY | Git commit hash or milestone unique identifier |
| `event_date` | `DATE` | NOT NULL | Milestone date (`YYYY-MM-DD`) |
| `title` | `TEXT` | NOT NULL | Short title of the milestone |
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
| `site_url` | `TEXT` | | Search Console property URL |
| `sync_type` | `TEXT` | NOT NULL | Sync type (`incremental`, `full`, `range`) |
| `start_date` | `TEXT` | | Starting date of sync window |
| `end_date` | `TEXT` | | Ending date of sync window |
| `rows_synced` | `INTEGER` | DEFAULT 0 | Total rows inserted or updated |
| `status` | `TEXT` | NOT NULL | Status (`success`, `failed`, `running`) |
| `error_message` | `TEXT` | | Error details if failed |
| `started_at` | `TEXT` | NOT NULL | Start timestamp |
| `completed_at` | `TEXT` | | Completion timestamp |

---

## 2. Analytical SQL Views

### `v_search_performance`
Granular performance with computed calendar dimensions (`year_month`, `day_of_week`, `ctr_pct`, `avg_position`).

| Column | Type | Description |
| :--- | :--- | :--- |
| `site_url` | `TEXT` | Property URL |
| `date` | `TEXT` | Activity date (`YYYY-MM-DD`) |
| `year_month` | `TEXT` | Formatted year and month (`YYYY-MM`) |
| `day_of_week` | `TEXT` | Full day name (`Monday`, `Tuesday`, etc.) |
| `query` | `TEXT` | Search query term |
| `page` | `TEXT` | Landing page URL |
| `country` | `TEXT` | Three-letter country code |
| `device` | `TEXT` | Device category (`DESKTOP`, `MOBILE`, `TABLET`) |
| `search_type` | `TEXT` | Search type (`web`, `image`, `video`) |
| `clicks` | `REAL` | Total clicks |
| `impressions` | `REAL` | Total impressions |
| `ctr_pct` | `REAL` | Click-through rate percentage (`clicks / impressions * 100`) |
| `avg_position` | `REAL` | Average ranking position |

---

### `v_daily_summary`
Daily aggregated search totals across all queries and landing pages.

| Column | Type | Description |
| :--- | :--- | :--- |
| `site_url` | `TEXT` | Property URL |
| `date` | `TEXT` | Activity date (`YYYY-MM-DD`) |
| `year_month` | `TEXT` | Formatted year and month (`YYYY-MM`) |
| `day_of_week` | `TEXT` | Full day name |
| `distinct_queries` | `INTEGER` | Count of distinct search keywords |
| `distinct_pages` | `INTEGER` | Count of distinct landing pages |
| `total_clicks` | `REAL` | Sum of clicks for the day |
| `total_impressions`| `REAL` | Sum of impressions for the day |
| `avg_ctr_pct` | `REAL` | Overall click-through rate percentage |
| `avg_position` | `REAL` | Average ranking position |

---

### `v_top_queries`
Search queries aggregated by active days, total clicks, impressions, CTR, and average position.

| Column | Type | Description |
| :--- | :--- | :--- |
| `site_url` | `TEXT` | Property URL |
| `query` | `TEXT` | Search query term |
| `active_days` | `INTEGER` | Number of distinct days query generated impressions |
| `total_clicks` | `REAL` | Total clicks received |
| `total_impressions`| `REAL` | Total impressions displayed |
| `avg_ctr_pct` | `REAL` | Average click-through rate percentage |
| `avg_position` | `REAL` | Average ranking position |

---

### `v_top_pages`
Landing pages aggregated by distinct ranking queries, clicks, impressions, CTR, and average position.

| Column | Type | Description |
| :--- | :--- | :--- |
| `site_url` | `TEXT` | Property URL |
| `page` | `TEXT` | Landing page URL |
| `ranking_queries` | `INTEGER` | Number of unique queries ranking for this page |
| `active_days` | `INTEGER` | Number of active traffic days |
| `total_clicks` | `REAL` | Total clicks received |
| `total_impressions`| `REAL` | Total impressions displayed |
| `avg_ctr_pct` | `REAL` | Average click-through rate percentage |
| `avg_position` | `REAL` | Average ranking position |

---

### `v_country_breakdown`
Geographic search performance aggregated by country code.

| Column | Type | Description |
| :--- | :--- | :--- |
| `site_url` | `TEXT` | Property URL |
| `country` | `TEXT` | Three-letter ISO country code |
| `total_clicks` | `REAL` | Total clicks from country |
| `total_impressions`| `REAL` | Total impressions in country |
| `avg_ctr_pct` | `REAL` | Average click-through rate percentage |
| `avg_position` | `REAL` | Average ranking position |

---

### `v_device_breakdown`
Device performance breakdown (`DESKTOP`, `MOBILE`, `TABLET`).

| Column | Type | Description |
| :--- | :--- | :--- |
| `site_url` | `TEXT` | Property URL |
| `device` | `TEXT` | Device category |
| `total_clicks` | `REAL` | Total clicks from device |
| `total_impressions`| `REAL` | Total impressions on device |
| `avg_ctr_pct` | `REAL` | Average click-through rate percentage |
| `avg_position` | `REAL` | Average ranking position |

---

### `v_milestone_impact`
Pre vs post milestone comparison of organic search traffic.

| Column | Type | Description |
| :--- | :--- | :--- |
| `commit_hash` | `TEXT` | Milestone identifier |
| `milestone_title` | `TEXT` | Title of the milestone |
| `milestone_date` | `DATE` | Event date (`YYYY-MM-DD`) |
| `cohort` | `TEXT` | `Pre-Milestone` or `Post-Milestone` |
| `days_tracked` | `INTEGER` | Number of days in cohort |
| `total_clicks` | `REAL` | Total clicks in cohort |
| `total_impressions`| `REAL` | Total impressions in cohort |
| `avg_ctr_pct` | `REAL` | Average click-through rate percentage |
| `avg_position` | `REAL` | Average ranking position |
