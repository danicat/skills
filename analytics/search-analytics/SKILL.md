---
name: search-analytics
description: >
  Ingest raw Google Search Console property totals and granular keyword
  performance data (clicks, impressions, CTR, position), properties, and XML
  sitemaps into a local SQLite database without data loss, run mature 16-month
  backfills and incremental syncs, and execute deep SQL analytics over organic
  search traffic. Activate whenever analyzing Google Search performance,
  auditing historical keyword rankings, diagnosing search CTR decay, running SQL
  queries over search traffic archives, or detecting keyword cannibalization.
license: Apache-2.0
metadata:
  category: analytics
  tags: "analytics, search-console, seo-analytics, sqlite, keywords, gsc, rankings"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  homepage: https://skills.danicat.dev/analytics/search-analytics/
  canonical: https://skills.danicat.dev/analytics/search-analytics/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/analytics/search-analytics
---

# Google Search Console SQLite Ingestion & SQL Analytics

The `search-analytics` skill ingests Google Search Console performance metrics into a local SQLite analytics database (`search_analytics.db` or `$XDG_DATA_HOME/search-analytics/analytics.db`) without data loss, preserving all raw JSON payloads, handling API quotas via 25,000 batch chunks, and providing direct SQL querying over indexed search traffic.

---

## ⚡ Quick Start & Primary Actions

All operations are driven via the bundled Python script in `scripts/search_analytics.py`:

```bash
# 1. Authenticate with Google OAuth 2.0
uv run <skill_dir>/scripts/search_analytics.py auth --port 8080

# 2. Incremental Sync (Updates newest days + 3-day latency overlap)
uv run <skill_dir>/scripts/search_analytics.py sync --db path/to/database.db

# 3. Full Historical Backfill (Ingests up to 16 months of granular daily data)
uv run <skill_dir>/scripts/search_analytics.py sync --full --db path/to/database.db

# 4. Run Pre-Built SQL Reports
uv run <skill_dir>/scripts/search_analytics.py report overview --db path/to/database.db
uv run <skill_dir>/scripts/search_analytics.py report top-queries --db path/to/database.db
uv run <skill_dir>/scripts/search_analytics.py report top-pages --db path/to/database.db
uv run <skill_dir>/scripts/search_analytics.py report countries --db path/to/database.db
uv run <skill_dir>/scripts/search_analytics.py report devices --db path/to/database.db
uv run <skill_dir>/scripts/search_analytics.py report timing --db path/to/database.db
uv run <skill_dir>/scripts/search_analytics.py report milestone-impact --db path/to/database.db

# 5. Run Ad-Hoc SQL Query
uv run <skill_dir>/scripts/search_analytics.py query "SELECT query, SUM(clicks), SUM(impressions) FROM search_performance GROUP BY query ORDER BY SUM(clicks) DESC LIMIT 10" --db path/to/database.db
```

If `--db` is omitted, the script defaults to `search_analytics.db` in the current working directory.

---

## 🗄️ Database Schema & Relational Structure

The database maintains 6 relational tables and 7 high-performance analytical views. Detailed DDL and schema definitions are in [`references/schema.md`](references/schema.md).

### Tables

1. **`daily_site_performance`**: Unfiltered property-level daily totals (`dimensions: ['date']`). Matches 100% of property clicks/impressions in the Search Console web interface and 28-day Achievement badges.
   - Key columns: `id` (PK), `site_url`, `date`, `search_type`, `clicks`, `impressions`, `ctr`, `position`, `raw_json`, `synced_at`.
2. **`search_performance`**: Granular keyword-level performance partitioned by query, page, country, and device.
   - Key columns: `id` (PK), `site_url`, `date`, `query`, `page`, `country`, `device`, `search_appearance`, `search_type`, `clicks`, `impressions`, `ctr`, `position`, `raw_json`, `synced_at`.
3. **`properties`**: Verified Search Console web properties.
   - Key columns: `site_url` (PK), `permission_level`, `raw_json`, `synced_at`.
4. **`sitemaps`**: Submitted XML sitemaps, error counts, and indexed URL counts.
   - Key columns: `site_url`, `path` (PK), `type`, `last_downloaded`, `last_submitted`, `errors`, `warnings`, `indexed_count`, `raw_json`, `synced_at`.
5. **`site_milestones`**: Release milestones and publication launches for cohort impact analysis.
   - Key columns: `commit_hash` (PK), `event_date`, `title`, `description`, `category`, `scope`, `author`, `created_at`.
6. **`sync_history`**: Audit log of backfill and incremental sync operations.
   - Key columns: `id` (PK), `site_url`, `sync_type`, `start_date`, `end_date`, `rows_synced`, `status`, `error_message`, `started_at`, `completed_at`.

---

## 📊 Analytical SQL Views

| View Name | Description | Key Columns |
| :--- | :--- | :--- |
| `v_search_performance` | Granular performance with computed calendar dimensions | `date`, `year_month`, `day_of_week`, `query`, `page`, `country`, `device`, `clicks`, `impressions`, `ctr_pct`, `avg_position` |
| `v_daily_summary` | Daily aggregated traffic metrics per site | `date`, `distinct_queries`, `distinct_pages`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_top_queries` | Aggregated search term rankings & click share | `query`, `active_days`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_top_pages` | Aggregated landing page performance & query breadth | `page`, `ranking_queries`, `active_days`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_country_breakdown` | Geographic traffic distribution | `country`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_device_breakdown` | Desktop vs. Mobile vs. Tablet comparison | `device`, `total_clicks`, `total_impressions`, `avg_ctr_pct`, `avg_position` |
| `v_milestone_impact` | Pre vs. Post milestone search traffic cohort impact | `milestone_title`, `milestone_date`, `cohort`, `days_tracked`, `total_clicks`, `total_impressions`, `avg_ctr_pct` |

---

## 🔍 Common SQL Analytics Recipes

Pre-tested SQL query recipes are documented in [`references/queries.md`](references/queries.md).

### 1. High-Opportunity Search Queries (Rank 1-10, Low CTR)
```sql
SELECT
    query,
    page,
    ROUND(SUM(impressions), 0) AS imps,
    ROUND(SUM(clicks), 0) AS clks,
    ROUND((SUM(clicks)/SUM(impressions))*100, 2) AS ctr_pct,
    ROUND(AVG(position), 1) AS avg_rank
FROM search_performance
WHERE position <= 10
GROUP BY query, page
HAVING SUM(impressions) >= 500 AND ctr_pct < 3.0
ORDER BY imps DESC
LIMIT 15;
```

### 2. Keyword Cannibalization Detection
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

## ⚠️ Critical Architecture: Property-Level Totals vs. Keyword-Level Breakdown

When querying and analyzing Search Console data, note the two distinct API behaviors and database tables:

1. **Unfiltered Property-Level Totals (`daily_site_performance`):**
   - Querying the GSC API with `dimensions: ['date']` (and `aggregationType: 'byProperty'`) returns **100% of property search traffic**, including all rare and long-tail queries.
   - This data is ingested into `daily_site_performance` and powers `v_daily_summary`. It directly matches the Search Console Web UI Performance graphs, Total Clicks cards, and 28-day Achievement badges (e.g. *700 clicks in 28 days*).
2. **Granular Keyword-Level Breakdown (`search_performance`):**
   - When querying the GSC API with `dimensions: ['query', 'page', 'country', 'device']`, Google automatically applies **anonymized query filtering** to protect searcher privacy, stripping out rare/unique queries.
   - On technical and developer blogs, long-tail anonymized queries often represent 50%–70% of total search traffic. Therefore, `search_performance` should be used for keyword rankings and page distributions, while `daily_site_performance` (or `v_daily_summary`) must be used for aggregate traffic totals.
3. **Cross-Engine Reconciliation with Google Analytics 4:**
   - GA4 records landing sessions under `session_default_channel_group = 'Organic Search'` across all search engines (Google, Bing, DuckDuckGo, etc.) without privacy filtering.
   - GA4 Organic Search traffic naturally aligns with Search Console property-level totals (`daily_site_performance`), rather than the query-filtered `search_performance` table.

---

## 📚 Progressive Disclosure & References

- **Full DDL Schema Reference**: [`references/schema.md`](references/schema.md) — Complete SQL table definitions, column types, constraints, and views.
- **SQL Query Cookbook**: [`references/queries.md`](references/queries.md) — Tested SQL recipes for CTR decay curves, keyword cannibalization, and MoM trends.
- **OAuth Setup Guide**: [`references/setup_oauth.md`](references/setup_oauth.md) — Step-by-step GCP project, API enablement, and credential setup.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Test cases for validating ingestion and analytical queries.
