---
name: google-analytics
description: >
  Collect and analyze Google Analytics 4 (GA4) website data in a local SQLite
  database. Stores pageviews, active users, reading dwell time, traffic sources,
  and outbound clicks so you can run SQL queries or view reports on site
  performance. Activate when analyzing website traffic, measuring reader
  engagement and dwell time, evaluating the impact of site updates or
  milestones, or querying Google Analytics with SQL.
license: Apache-2.0
metadata:
  category: analytics
  tags: "ga4, analytics, traffic, metrics, optimization"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.1"
  homepage: https://skills.danicat.dev/analytics/google-analytics/
  canonical: https://skills.danicat.dev/analytics/google-analytics/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/analytics/google-analytics
---

# Google Analytics 4 SQLite Ingestion & SQL Analytics

The `google-analytics` skill ingests Google Analytics 4 (GA4) traffic, reading depth, acquisition channels, event streams, and outbound clicks into a local SQLite analytics database (`google_analytics.db` or `$XDG_DATA_HOME/google-analytics/analytics.db`) without data loss, preserving raw JSON payloads on all records, and providing a fast SQL interface for website analytics.

---

## ⚡ Quick Start & Primary Actions

All operations are driven via the bundled Python CLI script:

```bash
# 1. Authorize OAuth 2.0 (with analytics.edit & readonly scopes)
uv run <skill_dir>/scripts/google_analytics.py auth --port 8080

# 2. Discover accessible GA4 properties
uv run <skill_dir>/scripts/google_analytics.py properties

# 3. Create Deployment / Milestone Annotation (Cloud API + Local SQLite)
uv run <skill_dir>/scripts/google_analytics.py annotate \
  --title "Major Release / Architecture Overhaul" \
  --date 2026-08-18 \
  --commit abc1234 \
  --description "Milestone description and release context."

# 4. Incremental Sync (Updates newest days + 3-day latency lookback overlap)
uv run <skill_dir>/scripts/google_analytics.py sync --db path/to/database.db

# 5. Full Historical Backfill (Ingests up to 14 months of daily granular data)
uv run <skill_dir>/scripts/google_analytics.py sync --full --db path/to/database.db

# 6. Run Pre-Built Reports
uv run <skill_dir>/scripts/google_analytics.py report overview --db path/to/database.db
uv run <skill_dir>/scripts/google_analytics.py report top-pages --db path/to/database.db
uv run <skill_dir>/scripts/google_analytics.py report channels --db path/to/database.db
uv run <skill_dir>/scripts/google_analytics.py report geo --db path/to/database.db
uv run <skill_dir>/scripts/google_analytics.py report events --db path/to/database.db
uv run <skill_dir>/scripts/google_analytics.py report outbound --db path/to/database.db
uv run <skill_dir>/scripts/google_analytics.py report milestone-impact --db path/to/database.db

# 7. Execute Ad-Hoc SQL Query
uv run <skill_dir>/scripts/google_analytics.py query "SELECT page_path, total_views, total_users, avg_dwell_sec, avg_bounce_pct FROM v_page_performance LIMIT 10" --db path/to/database.db
```

If `--db` is omitted, the script defaults to `google_analytics.db` in the current working directory.

---

## 🗄️ Database Schema & Relational Structure

The database maintains 7 relational tables and 7 analytical views. Detailed DDL and schema definitions are in [`references/schema.md`](references/schema.md).

### Tables

1. **`daily_pages`**: Granular daily page metrics by URL, country, device, and traffic source.
   - Key columns: `id` (PK), `property_id`, `date`, `page_path`, `page_title`, `country`, `device_category`, `source_medium`, `screen_page_views`, `active_users`, `sessions`, `user_engagement_duration`, `bounce_rate`, `raw_json`, `synced_at`.
2. **`daily_traffic`**: Acquisition channels and source/medium pairs.
   - Key columns: `id` (PK), `property_id`, `date`, `session_source_medium`, `session_default_channel_group`, `country`, `device_category`, `sessions`, `active_users`, `new_users`, `engaged_sessions`, `user_engagement_duration`, `bounce_rate`, `raw_json`, `synced_at`.
3. **`daily_events`**: User interaction event stream (`scroll`, `click`, `first_visit`, `user_engagement`, `page_view`).
   - Key columns: `id` (PK), `property_id`, `date`, `event_name`, `page_path`, `country`, `device_category`, `event_count`, `total_users`, `raw_json`, `synced_at`.
4. **`outbound_clicks`**: External link exit destinations and click counts.
   - Key columns: `id` (PK), `property_id`, `date`, `link_url`, `page_path`, `country`, `event_count`, `total_users`, `raw_json`, `synced_at`.
5. **`properties`**: Verified GA4 property metadata, timezone, and settings.
   - Key columns: `property_id` (PK), `name`, `account_id`, `display_name`, `industry_category`, `time_zone`, `currency_code`, `service_level`, `raw_json`, `last_synced_at`.
6. **`site_milestones`**: Release milestones and publication events.
   - Key columns: `commit_hash` (PK), `event_date`, `title`, `description`, `category`, `scope`, `author`, `created_at`.
7. **`sync_history`**: Audit log of sync executions and row counts.
   - Key columns: `id` (PK), `property_id`, `sync_type`, `start_date`, `end_date`, `pages_synced`, `traffic_synced`, `events_synced`, `outbound_synced`, `status`, `error_message`, `started_at`, `finished_at`.

---

## 📊 Analytical SQL Views

| View Name | Description | Key Columns |
| :--- | :--- | :--- |
| `v_daily_summary` | Daily aggregated traffic metrics | `date`, `total_sessions`, `total_active_users`, `total_page_views`, `total_engagement_min`, `avg_bounce_pct` |
| `v_page_performance` | Page rollup with views, active users, dwell time, and bounce rate | `page_path`, `page_title`, `total_views`, `total_users`, `total_sessions`, `avg_dwell_sec`, `total_dwell_min`, `avg_bounce_pct` |
| `v_channel_performance` | Acquisition channel breakdown | `channel_group`, `source_medium`, `total_sessions`, `total_users`, `total_new_users`, `total_engaged_sessions`, `engagement_rate_pct`, `total_dwell_min`, `avg_bounce_pct` |
| `v_geo_breakdown` | Country traffic and dwell time | `country`, `total_sessions`, `total_users`, `total_page_views`, `avg_dwell_sec`, `avg_bounce_pct` |
| `v_events_summary` | Aggregate event counts | `event_name`, `total_events`, `total_users` |
| `v_outbound_links` | Outbound destination rankings | `link_url`, `total_clicks`, `total_users`, `referring_pages_count` |
| `v_milestone_impact` | Pre vs. Post milestone comparison | `milestone_title`, `milestone_date`, `cohort`, `days_tracked`, `total_views`, `total_users`, `total_sessions`, `avg_engagement_sec`, `avg_bounce_pct` |

---

## 🔍 SQL Analytics Recipes

Pre-tested SQL query recipes are documented in [`references/queries.md`](references/queries.md).

### 1. Top Landing Pages by Active Dwell Time
```sql
SELECT
    page_path,
    page_title,
    total_views,
    total_users,
    avg_dwell_sec || 's' AS avg_dwell,
    total_dwell_min || 'm' AS total_dwell,
    avg_bounce_pct || '%' AS bounce_pct
FROM v_page_performance
ORDER BY total_dwell_min DESC
LIMIT 15;
```

### 2. Category / Subdirectory Rollup
```sql
SELECT
    CASE
        WHEN page_path LIKE '/docs/%' THEN 'Docs'
        WHEN page_path LIKE '/blog/%' THEN 'Blog'
        WHEN page_path = '/' THEN 'Homepage'
        ELSE 'Other'
    END AS category,
    COUNT(DISTINCT page_path) AS page_count,
    SUM(total_views) AS total_views,
    SUM(total_users) AS total_users,
    ROUND(SUM(total_dwell_min), 1) AS total_dwell_min
FROM v_page_performance
GROUP BY category
ORDER BY total_views DESC;
```

---

## ⚠️ Cross-Tool Alignment: GA4 Organic Search vs. Search Console Property Totals

When cross-referencing GA4 acquisition metrics with Google Search Console data:

1. **Multi-Engine Organic Reach:** GA4 `Organic Search` aggregates landing sessions and active users across **all search engines** (Google Search, Bing, DuckDuckGo, Ecosia, Yahoo, AI search engines). Search Console exclusively measures Google Search impressions and clicks.
2. **Session Arrivals vs. SERP Clicks:** GA4 tracks 100% of landing sessions without query-level privacy truncation. In contrast, Search Console API keyword exports filter out "anonymized queries".
3. **Property-Level Reconciliation:** For organic traffic reporting, GA4 `v_channel_performance` (filtering for `channel_group = 'Organic Search'`) naturally aligns with Search Console property-level totals (`daily_site_performance` in `search-analytics` and GSC Web UI Performance cards), while Search Console's `search_performance` table provides the granular ranking breakdown for identifiable keywords.

---

## 📚 Progressive Disclosure & References

- **Full DDL Schema Reference**: [`references/schema.md`](references/schema.md) — Complete SQL table definitions, column types, constraints, and views.
- **SQL Query Cookbook**: [`references/queries.md`](references/queries.md) — Tested SQL recipes for reading depth, acquisition channels, and exit destinations.
- **Authentication Guide**: [`references/setup_auth.md`](references/setup_auth.md) — Google Cloud ADC login, API enablement, and GA4 property permissions.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Test benchmarks for validating skill triggers and query execution.
