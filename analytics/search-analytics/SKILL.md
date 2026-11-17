---
name: search-analytics
description: >
  Collect and analyze Google Search Console organic search data in a local
  SQLite database. Stores clicks, impressions, click-through rates (CTR),
  average ranking positions, and landing pages so you can run SQL queries or
  view performance reports. Activate when analyzing Google Search traffic,
  tracking keyword rankings, finding SEO content optimization opportunities, or
  querying Search Console data with SQL.
license: Apache-2.0
metadata:
  category: analytics
  tags: "search-console, gsc, google-search, seo, keywords, rankings"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Google Search Console ingestion and SQL analytics

The `search-analytics` skill pulls Google Search Console metrics into a local `SQLite` database (`search_analytics.db`). It stores complete raw JSON payloads, pages through 25,000-row API batches, and lets you query search traffic with SQL.

## Available scripts
- `scripts/search_analytics.py`: Sync, reporting, milestone, and `OAuth` CLI for Google Search Console (`uv run scripts/search_analytics.py`; uses Google Cloud ADC or `OAuth` credentials).
- `scripts/test_search_analytics.py`: Unit and regression test suite covering schema views, weighted rankings, query extraction, pagination, and CLI flags.

---

## Quick start and primary actions

Run every command through the bundled script in `scripts/search_analytics.py`:

```bash
# 1. Authenticate with Google OAuth 2.0 (write scope for sitemap submission)
uv run scripts/search_analytics.py auth --port 8080

# 2. Incremental sync (updates newest days + 3-day overlap for reporting delay)
uv run scripts/search_analytics.py sync --db path/to/database.db

# 3. Full historical backfill (up to 16 months of daily data)
uv run scripts/search_analytics.py sync --full --db path/to/database.db

# 4. Record a release or SEO milestone for cohort comparisons
uv run scripts/search_analytics.py milestone \
  --title "v2.0 Architecture Refresh" \
  --date 2026-08-18 \
  --commit abc1234 \
  --db path/to/database.db

# 5. Run pre-built SQL reports (all tracked dates by default; add --days N to window)
uv run scripts/search_analytics.py report overview --db path/to/database.db
uv run scripts/search_analytics.py report overview --days 28 --db path/to/database.db
uv run scripts/search_analytics.py report top-queries --db path/to/database.db
uv run scripts/search_analytics.py report top-pages --db path/to/database.db
uv run scripts/search_analytics.py report countries --db path/to/database.db
uv run scripts/search_analytics.py report devices --db path/to/database.db
uv run scripts/search_analytics.py report timing --db path/to/database.db
uv run scripts/search_analytics.py report milestone-impact --db path/to/database.db

# 6. Run ad-hoc SQL query
uv run scripts/search_analytics.py query "SELECT query, SUM(clicks), SUM(impressions) FROM search_performance GROUP BY query ORDER BY SUM(clicks) DESC LIMIT 10" --db path/to/database.db
```

When you omit `--db`, the script writes to `search_analytics.db` in the current working directory.

---

## Database schema and relational structure

The database keeps 6 tables and 7 SQL views. See full DDL definitions and constraints in [`references/schema.md`](references/schema.md).

### Tables

1. **`daily_site_performance`**: Unfiltered daily property totals (`dimensions: ['date']`). Matches property clicks and impressions in the Search Console web dashboard and 28-day achievement badges.
   - Key columns: `id` (PK), `site_url`, `date`, `search_type`, `clicks`, `impressions`, `ctr`, `position`, `raw_json`, `synced_at`.
2. **`search_performance`**: Granular keyword metrics split by query, page, country, and device.
   - Key columns: `id` (PK), `site_url`, `date`, `query`, `page`, `country`, `device`, `search_appearance`, `search_type`, `clicks`, `impressions`, `ctr`, `position`, `raw_json`, `synced_at`.
3. **`properties`**: Verified Search Console properties and permissions.
   - Key columns: `site_url` (PK), `permission_level`, `raw_json`, `synced_at`.
4. **`sitemaps`**: Submitted XML sitemaps, errors, and indexed URL counts.
   - Key columns: `site_url`, `path` (PK), `type`, `last_downloaded`, `last_submitted`, `errors`, `warnings`, `indexed_count`, `raw_json`, `synced_at`.
5. **`site_milestones`**: Release milestones and launch dates for cohort tracking.
   - Key columns: `commit_hash` (PK), `event_date`, `title`, `description`, `category`, `scope`, `author`, `created_at`.
6. **`sync_history`**: Audit log of backfill and incremental sync runs.
   - Key columns: `id` (PK), `site_url`, `sync_type`, `start_date`, `end_date`, `rows_synced`, `status`, `error_message`, `started_at`, `completed_at`.

---

## Analytical SQL views

| View Name | Purpose | Key Columns |
| :--- | :--- | :--- |
| `v_search_performance` | Granular search rows with calendar fields | `date`, `year_month`, `day_of_week`, `query`, `page`, `country`, `device`, `clicks`, `impressions`, `ctr_pct`, `avg_position` |
| `v_daily_summary` | Unfiltered daily totals and weighted position per site | `date`, `distinct_queries`, `distinct_pages`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_top_queries` | Search term totals and impression-weighted ranking | `query`, `active_days`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_top_pages` | Landing page totals, query breadth, and weighted ranking | `page`, `ranking_queries`, `active_days`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_country_breakdown` | Country traffic and weighted ranking | `country`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_device_breakdown` | Desktop vs. mobile vs. tablet split | `device`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_milestone_impact` | Before and after milestone comparison from unfiltered totals | `milestone_title`, `milestone_date`, `cohort`, `days_tracked`, `total_clicks`, `total_impressions`, `ctr_pct`, `avg_position` |

---

## Common SQL analytics recipes

Find tested SQL queries for ranking decay curves, keyword checks, and monthly trends in [`references/queries.md`](references/queries.md).

### 1. High-opportunity search queries (rank 1 to 10, low CTR)
```sql
SELECT
    query,
    page,
    ROUND(SUM(impressions), 0) AS imps,
    ROUND(SUM(clicks), 0) AS clks,
    ROUND((SUM(clicks)/SUM(impressions))*100, 2) AS ctr_pct,
    ROUND(SUM(position * impressions) * 1.0 / MAX(SUM(impressions), 1), 1) AS avg_rank
FROM search_performance
WHERE position <= 10
GROUP BY query, page
HAVING SUM(impressions) >= 500 AND ctr_pct < 3.0
ORDER BY imps DESC
LIMIT 15;
```

### 2. Keyword cannibalization check
```sql
SELECT
    query,
    COUNT(DISTINCT page) AS competing_pages,
    GROUP_CONCAT(DISTINCT page) AS pages,
    ROUND(SUM(clicks), 0) AS total_clicks,
    ROUND(SUM(impressions), 0) AS total_impressions
FROM search_performance
WHERE query != ''
GROUP BY query
HAVING COUNT(DISTINCT page) > 1
ORDER BY total_impressions DESC
LIMIT 10;
```

---

## Property-level totals vs. keyword-level breakdown

Search Console splits API results into two layers, stored in separate tables:

1. **Unfiltered property totals (`daily_site_performance`):**
   - Querying the GSC API with `dimensions: ['date']` and `aggregationType: 'byProperty'` returns 100% of search traffic, including rare and long-tail queries.
   - Sync writes these rows to `daily_site_performance`, which feeds `v_daily_summary`, `report overview`, and `v_milestone_impact`. These numbers match the Search Console dashboard charts and 28-day achievement cards.
2. **Granular keyword breakdown (`search_performance`):**
   - When querying with `dimensions: ['query', 'page', 'country', 'device']`, Google drops hidden rare queries to protect searcher privacy.
   - On developer blogs, hidden rare queries often make up 50% to 70% of all clicks. Use `search_performance` for keyword and page rankings, and read aggregate totals from `daily_site_performance` or `v_daily_summary`.
3. **Cross-engine matching with Google Analytics 4:**
   - GA4 records landing sessions under `session_default_channel_group = 'Organic Search'` across `Google`, `Bing`, `DuckDuckGo`, and other search engines without query filtering.
   - Match GA4 Organic Search numbers against `daily_site_performance` property totals rather than query-filtered `search_performance` sums.

---

## References

- **Full DDL schema reference**: [`references/schema.md`](references/schema.md): complete SQL tables, column types, constraints, and views.
- **SQL query cookbook**: [`references/queries.md`](references/queries.md): tested SQL queries for CTR decay curves, keyword overlap, and monthly growth.
- **Authentication setup guide**: [`references/setup_oauth.md`](references/setup_oauth.md): Google Cloud API setup, ADC login, least-privilege scopes, and `OAuth` configuration.
