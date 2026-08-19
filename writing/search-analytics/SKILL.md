---
name: search-analytics
description: Ingest raw Google Search Console performance data (clicks, impressions, CTR, average position), properties, and XML sitemaps into a local SQLite database without data loss, run mature 16-month backfills and incremental syncs, and execute deep SQL analytics over organic search traffic. Activate whenever analyzing Google Search performance, auditing historical keyword rankings, diagnosing search CTR decay, running SQL queries over search traffic archives, or detecting keyword cannibalization.
---

# Google Search Console SQLite Ingestion & SQL Analytics

The `search-analytics` skill ingests Google Search Console performance metrics into a local SQLite analytics database (`search_analytics.db` or `$XDG_DATA_HOME/search-analytics/analytics.db`) without data loss, preserving all raw JSON payloads, handling API quotas via 25,000 batch chunks, and providing direct SQL querying over indexed search traffic.

---

## ⚡ Quick Start & Primary Actions

### 1. Authenticate with Google
Launches a local OAuth 2.0 companion server on `http://localhost:8080` to authenticate and save credentials to `~/.config/gsc/credentials.json`:

```bash
uv run <skill_dir>/scripts/search_analytics.py auth --port 8080
```

---

### 2. Ingest Data (Backfill & Incremental Sync)

```bash
# Incremental Sync: Updates newest days since last sync (+ 3-day latency overlap)
uv run <skill_dir>/scripts/search_analytics.py sync

# Full Historical Backfill: Ingests up to 16 months of granular daily data
uv run <skill_dir>/scripts/search_analytics.py sync --full

# Specific Date Range:
uv run <skill_dir>/scripts/search_analytics.py sync \
  --start-date 2026-06-01 \
  --end-date 2026-08-15

# Sync a single property:
uv run <skill_dir>/scripts/search_analytics.py sync \
  --site-url "https://example.com/" \
  --days 30
```

---

### 3. Run Pre-Built SQL Reports

```bash
# Overall site health and date coverage
uv run <skill_dir>/scripts/search_analytics.py report overview

# Top search queries ranked by clicks and impressions
uv run <skill_dir>/scripts/search_analytics.py report top-queries

# Top landing pages and ranking query count
uv run <skill_dir>/scripts/search_analytics.py report top-pages

# Geographic country breakdown
uv run <skill_dir>/scripts/search_analytics.py report countries

# Device performance (Mobile vs Desktop vs Tablet)
uv run <skill_dir>/scripts/search_analytics.py report devices

# Day-of-the-week traffic trends
uv run <skill_dir>/scripts/search_analytics.py report timing

# Release / Milestone cohort impact comparison
uv run <skill_dir>/scripts/search_analytics.py report milestone-impact
```

---

### 4. Execute Ad-Hoc SQL Queries

Execute arbitrary SQL directly against `~/.gsc/analytics.db`:

```bash
# Find high-impression queries ranking on page 1 with low CTR (Optimization opportunities)
uv run <skill_dir>/scripts/search_analytics.py query "
SELECT query, page, ROUND(SUM(impressions),0) AS imps, ROUND(SUM(clicks),0) AS clks, ROUND((SUM(clicks)/SUM(impressions))*100,2) AS ctr_pct, ROUND(AVG(position),1) AS avg_rank
FROM v_search_performance
WHERE avg_position <= 10
GROUP BY query, page
HAVING SUM(impressions) >= 500 AND ctr_pct < 3.0
ORDER BY imps DESC
LIMIT 15;
"
```

---

## 🗄️ Relational Schema & Analytical Views

- **`search_performance`**: Granular daily performance records by `date`, `query`, `page`, `country`, `device`, `clicks`, `impressions`, `ctr`, `position`, and full `raw_json`.
- **`properties`**: Verified Search Console web properties and permission levels.
- **`sitemaps`**: Submitted XML sitemaps, error counts, and indexed URL numbers.
- **`sync_history`**: Audit log of backfill and incremental runs.
- **Views**: `v_search_performance`, `v_daily_summary`, `v_top_queries`, `v_top_pages`, `v_country_breakdown`, `v_device_breakdown`.

---

## 📚 Progressive Disclosure & References

- **Database Schema DDL**: [`references/schema.md`](references/schema.md) — Full table definitions, constraints, indexes, and analytical views.
- **SQL Query Cookbook**: [`references/queries.md`](references/queries.md) — Pre-tested SQL recipes for CTR decay curves, keyword cannibalization, and MoM trends.
- **OAuth Setup Guide**: [`references/setup_oauth.md`](references/setup_oauth.md) — Step-by-step GCP project, API enablement, and credential setup.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Test cases for validating ingestion and analytical queries.
