---
name: google-analytics
description: Ingest raw Google Analytics 4 (GA4) performance data (sessions, active users, pageviews, dwell time, engagement events, acquisition channels, and outbound clicks) into a local SQLite database without data loss, run full historical backfills and incremental syncs, and execute deep SQL analytics over website traffic and release milestones. Activate whenever analyzing Google Analytics 4 performance, auditing reader dwell time, evaluating release cohort impact, querying GA4 data via SQL, or tracking user journeys and outbound link exits.
---

# Google Analytics 4 SQLite Ingestion & SQL Analytics

The `google-analytics` skill ingests Google Analytics 4 (GA4) traffic, reading depth, acquisition channels, event streams, and outbound clicks into a local SQLite analytics database (`google_analytics.db` or `$XDG_DATA_HOME/google-analytics/analytics.db`) without data loss, preserving raw JSON payloads on all records, and providing a fast SQL interface for website analytics.

---

## ⚡ Quick Start & Primary Actions

All operations are driven via the bundled Python CLI script (runnable with `python3` or `uv run`):

```bash
# 1. Authorize OAuth 2.0 (with analytics.edit & readonly scopes)
uv run <skill_dir>/scripts/google_analytics.py auth --port 8080

# 2. Discover accessible GA4 properties
uv run <skill_dir>/scripts/google_analytics.py properties

# 3. Create Deployment / Milestone Annotation (Cloud API + Local SQLite)
uv run <skill_dir>/scripts/google_analytics.py annotate \
  --title "Site Redesign & Architecture Overhaul" \
  --date 2026-08-18 \
  --commit abc1234 \
  --description "Comprehensive site architecture and performance release."

# 4. Incremental Sync (Updates newest days + 3-day latency lookback overlap)
uv run <skill_dir>/scripts/google_analytics.py sync

# 5. Full Historical Backfill (Ingests up to 14 months of daily granular data)
uv run <skill_dir>/scripts/google_analytics.py sync --full

# 6. Custom Date Range Sync
uv run <skill_dir>/scripts/google_analytics.py sync \
  --start-date 2026-06-01 \
  --end-date 2026-08-15
```

---

## 📊 Pre-Built Analytical Reports

```bash
# 1. Overall site health, sessions, users, dwell time, and 7-day trend
uv run <skill_dir>/scripts/google_analytics.py report overview

# 2. Top pages ranked by views, active dwell time, and bounce rate
uv run <skill_dir>/scripts/google_analytics.py report top-pages

# 3. Traffic sources, channels, and conversion engagement rates
uv run <skill_dir>/scripts/google_analytics.py report channels

# 4. Geographical breakdown & country dwell times
uv run <skill_dir>/scripts/google_analytics.py report geo

# 5. User interaction events (scroll, click, first_visit, form_submit)
uv run <skill_dir>/scripts/google_analytics.py report events

# 6. Outbound link click destinations
uv run <skill_dir>/scripts/google_analytics.py report outbound

# 7. Release / Milestone cohort impact comparison
uv run <skill_dir>/scripts/google_analytics.py report milestone-impact
```

---

## 🔍 Execute Ad-Hoc SQL Queries

Execute arbitrary SQL queries against the local database with formatted ASCII tables, `--json`, or `--csv`:

```bash
# Top 10 landing pages by total dwell time and engagement
python3 scripts/google_analytics.py query "
SELECT 
    page_path,
    total_views,
    total_users,
    total_sessions,
    avg_dwell_sec || 's' AS dwell,
    avg_bounce_pct || '%' AS bounce
FROM v_page_performance
ORDER BY total_views DESC
LIMIT 10;
"
```

---

## 🗄️ Relational Schema & Analytical Views

- **`daily_pages`**: Granular daily performance records by `date`, `page_path`, `page_title`, `country`, `device_category`, `source_medium`, `screen_page_views`, `active_users`, `sessions`, `user_engagement_duration`, `bounce_rate`, and `raw_json`.
- **`daily_traffic`**: Acquisition channels and sources (`session_source_medium`, `session_default_channel_group`, `sessions`, `new_users`, `engaged_sessions`, `bounce_rate`).
- **`daily_events`**: Event stream logs (`scroll`, `click`, `first_visit`, `user_engagement`, `page_view`).
- **`outbound_clicks`**: Destination link URLs, referring pages, and user clicks.
- **`properties`**: GA4 metadata, time zone, currency, and property names.
- **`sync_history`**: Audit log of backfills and sync operations.
- **Analytical Views**: `v_daily_summary`, `v_page_performance`, `v_channel_performance`, `v_geo_breakdown`, `v_events_summary`, `v_outbound_links`.

---

## 📚 Progressive Disclosure & References

- **Database Schema DDL**: [`references/schema.md`](references/schema.md) — Full table definitions, constraints, indexes, and view schemas.
- **SQL Query Cookbook**: [`references/queries.md`](references/queries.md) — Pre-tested SQL recipes for reading depth, multi-lingual performance, and traffic channels.
- **Authentication Guide**: [`references/setup_auth.md`](references/setup_auth.md) — Google Cloud ADC login, API enablement, and GA4 property permissions.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Test benchmarks for validating skill triggers and query execution.
