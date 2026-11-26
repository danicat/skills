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
  tags: "google-analytics, ga4, web-traffic, pageviews, engagement"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.1"
  catalog: https://skills.danicat.dev
---

# Google Analytics 4 ingestion and SQL analytics

The `google-analytics` skill pulls Google Analytics 4 (GA4) traffic, reading depth, acquisition channels, event streams, and outbound clicks into a local `SQLite` database (`google_analytics.db` or `$XDG_DATA_HOME/google-analytics/analytics.db`). It keeps complete raw JSON payloads and gives you fast SQL queries across every synced date.

## Available scripts
- `scripts/google_analytics.py`: Sync, reporting, and annotation CLI for GA4. Run it with `uv run scripts/google_analytics.py` (uses Google Cloud ADC or `OAuth` credentials).
- `scripts/test_google_analytics.py`: Unit and regression test suite covering schema views, query extraction, weighted metrics, pagination, and CLI flags.

---

## Quick start and primary actions

All commands run through the bundled script in `scripts/google_analytics.py`:

```bash
# 1. Authorize OAuth 2.0 (analytics.edit + analytics.readonly scopes)
uv run scripts/google_analytics.py auth --port 8080

# 2. Discover accessible GA4 properties (read-only scope)
uv run scripts/google_analytics.py properties

# 3. Create deployment or milestone annotation (Cloud API + local SQLite)
uv run scripts/google_analytics.py annotate \
  --title "Major Release / Architecture Overhaul" \
  --date 2026-08-18 \
  --commit abc1234 \
  --description "Milestone summary and release notes."

# 4. Incremental sync (latest days + 3-day overlap for delayed reporting)
uv run scripts/google_analytics.py sync --db path/to/database.db

# 5. Full historical sync (up to 14 months of daily breakdown rows)
uv run scripts/google_analytics.py sync --full --db path/to/database.db

# 6. Run pre-built reports (all tracked dates by default; add --days N to window)
uv run scripts/google_analytics.py report overview --db path/to/database.db
uv run scripts/google_analytics.py report overview --days 30 --db path/to/database.db
uv run scripts/google_analytics.py report top-pages --db path/to/database.db
uv run scripts/google_analytics.py report channels --db path/to/database.db
uv run scripts/google_analytics.py report geo --db path/to/database.db
uv run scripts/google_analytics.py report events --db path/to/database.db
uv run scripts/google_analytics.py report outbound --db path/to/database.db
uv run scripts/google_analytics.py report milestone-impact --db path/to/database.db

# 7. Execute ad-hoc SQL query
uv run scripts/google_analytics.py query "SELECT page_path, total_views, total_users, avg_dwell_sec, avg_bounce_pct FROM v_page_performance LIMIT 10" --db path/to/database.db
```

When you omit `--db`, the script writes to `google_analytics.db` in the current working directory. By default, `auth` saves OAuth credentials (including token expiry for automatic refresh across runs) to `~/.config/ga4/credentials.json` unless `./credentials.json` already exists.

---

## Database schema and relational structure

The database keeps 7 tables and 7 SQL views. See full DDL and column constraints in [`references/schema.md`](references/schema.md).

### Tables

1. **`daily_pages`**: Daily page metrics by path, country, device, and traffic source.
   - Key columns: `id` (PK), `property_id`, `date`, `page_path`, `page_title`, `country`, `device_category`, `source_medium`, `screen_page_views`, `active_users`, `sessions`, `user_engagement_duration`, `bounce_rate`, `raw_json`, `synced_at`.
2. **`daily_traffic`**: Acquisition channels and source/medium pairs.
   - Key columns: `id` (PK), `property_id`, `date`, `session_source_medium`, `session_default_channel_group`, `country`, `device_category`, `sessions`, `active_users`, `new_users`, `engaged_sessions`, `user_engagement_duration`, `bounce_rate`, `raw_json`, `synced_at`.
3. **`daily_events`**: User interaction events (`scroll`, `click`, `first_visit`, `user_engagement`, `page_view`).
   - Key columns: `id` (PK), `property_id`, `date`, `event_name`, `page_path`, `country`, `device_category`, `event_count`, `total_users`, `raw_json`, `synced_at`.
4. **`outbound_clicks`**: External exit link clicks and referring page paths.
   - Key columns: `id` (PK), `property_id`, `date`, `link_url`, `page_path`, `country`, `event_count`, `total_users`, `raw_json`, `synced_at`.
5. **`properties`**: Verified GA4 property details, time zone, and currency settings.
   - Key columns: `property_id` (PK), `name`, `account_id`, `display_name`, `industry_category`, `time_zone`, `currency_code`, `service_level`, `raw_json`, `last_synced_at`.
6. **`site_milestones`**: Release milestones and launch dates for cohort comparison.
   - Key columns: `commit_hash` (PK), `event_date`, `title`, `description`, `category`, `scope`, `author`, `created_at`.
7. **`sync_history`**: Audit log of sync runs and row counts.
   - Key columns: `id` (PK), `property_id`, `sync_type`, `start_date`, `end_date`, `pages_synced`, `traffic_synced`, `events_synced`, `outbound_synced`, `status`, `error_message`, `started_at`, `finished_at`.

---

## Analytical SQL views

| View Name | Purpose | Key Columns |
| :--- | :--- | :--- |
| `v_daily_summary` | Daily traffic totals and session-weighted bounce rate | `date`, `total_sessions`, `total_active_users`, `total_page_views`, `total_engagement_min`, `avg_bounce_pct` |
| `v_page_performance` | Page summary with views, active users, dwell time, and weighted bounce | `page_path`, `page_title`, `total_views`, `total_users`, `total_sessions`, `avg_dwell_sec`, `total_dwell_min`, `avg_bounce_pct` |
| `v_channel_performance` | Acquisition channel breakdown | `channel_group`, `source_medium`, `total_sessions`, `total_users`, `total_new_users`, `total_engaged_sessions`, `engagement_rate_pct`, `avg_dwell_sec`, `engaged_dwell_sec`, `total_dwell_min`, `avg_bounce_pct` |
| `v_geo_breakdown` | Country traffic, dwell time, and weighted bounce | `country`, `total_sessions`, `total_users`, `total_page_views`, `avg_dwell_sec`, `avg_bounce_pct` |
| `v_events_summary` | Event totals | `event_name`, `total_events`, `total_users` |
| `v_outbound_links` | Outbound destination rankings | `link_url`, `total_clicks`, `total_users`, `referring_pages_count` |
| `v_milestone_impact` | Before and after milestone comparison with weighted dwell and bounce | `milestone_title`, `milestone_date`, `cohort`, `days_tracked`, `total_views`, `total_users`, `total_sessions`, `avg_engagement_sec`, `avg_bounce_pct` |

---

## SQL analytics recipes

Find the full tested cookbook in [`references/queries.md`](references/queries.md).

### 1. Top landing pages by active dwell time
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

### 2. Category and subdirectory summary
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

## Analytical guardrails and engagement methodology

Apply these four checks so raw GA4 numbers do not mislead your analysis:

1. **Two-stage engagement split (`avg_dwell_sec` vs. `engaged_dwell_sec` + interaction density):**
   - GA4 measures `user_engagement_duration` between `session_start` and the final event. Single-page visits that leave without another event log `0s` duration.
   - Report engaged session dwell (`engaged_dwell_sec`) alongside raw session dwell (`avg_dwell_sec`). Pair time metrics with `scroll` depth and `outbound_clicks` per user via Recipe #11 in [`references/queries.md`](references/queries.md).
2. **Unengaged `Direct` traffic gate (bot and scraper check):**
   - Headless crawlers, link previewers, and uptime probes often drop the HTTP `Referer` header, land in `Direct`, and exit in under 2 seconds with under 15% engagement.
   - Check `Direct` traffic for `(month, country, device_category)` spikes with near-zero engagement (Recipe #9 in [`references/queries.md`](references/queries.md)) before computing site-wide averages. Separate human traffic from unengaged spikes.
3. **Generative AI channel split (organic vs. AI assistants vs. social):**
   - GA4's `session_default_channel_group` lumps AI assistants (`chatgpt.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`) under `Referral` or `Organic Search`.
   - Use Recipe #8 in [`references/queries.md`](references/queries.md) to split `session_source_medium` into Generative AI, Organic Search, Social Referrals, and Web Referrals.
4. **Custom event inventory gate (`daily_events` check):**
   - Page reports (`v_page_performance`) read only `daily_pages`. Custom events (`scroll_25`, `scroll_50`, `scroll_75`, `code_copy`, `form_submit`) land in `daily_events`.
   - Run Recipe #10 in [`references/queries.md`](references/queries.md) (`WHERE event_name NOT IN ('page_view', 'user_engagement', 'session_start', 'first_visit')`) so custom interaction events enter your findings.

---

## Cross-tool alignment: GA4 Organic Search vs. Search Console property totals

Keep these differences in mind when comparing GA4 acquisition numbers with Google Search Console:

1. **Multi-engine reach:** GA4 `Organic Search` combines sessions across every search engine (`Google`, `Bing`, `DuckDuckGo`, `Ecosia`, `Yahoo`, and AI search engines). Search Console reports Google Search clicks and impressions only.
2. **Session arrivals vs. SERP clicks:** GA4 records 100% of landing sessions with no keyword privacy filter. Search Console keyword tables drop hidden rare queries.
3. **Property-level matching:** For organic search totals, match GA4 `v_channel_performance` (`channel_group = 'Organic Search'`) against Search Console property-level totals rather than query-level keyword sums.

---

## References

- **Full DDL schema reference**: [`references/schema.md`](references/schema.md): complete SQL tables, column types, constraints, and views.
- **SQL query cookbook**: [`references/queries.md`](references/queries.md): tested SQL queries for reading depth, channels, bots, and exit clicks.
- **Authentication setup guide**: [`references/setup_auth.md`](references/setup_auth.md): Google Cloud ADC login, API setup, least-privilege scopes, and GA4 property permissions.
