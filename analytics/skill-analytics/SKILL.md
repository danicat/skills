---
name: skill-analytics
description: >
  Mine and analyze Agent Skill usage, Context-Tax ROI, trigger attribution, and
  KungFu telemetry in a local SQLite database. Scans conversation transcripts and
  installed skill tiers (built-in, plugin, global, workspace, and catalog) to
  detect zero-use shelfware, tune activation descriptions with skill-optimizer,
  and backfill state.json. Activate when analyzing skill usage over time,
  auditing system-prompt token overhead, measuring autonomous vs. explicit
  (::skill or //skill) triggers, or querying skill telemetry with SQL.
license: Apache-2.0
metadata:
  category: analytics
  tags: "skills, agent-skills, telemetry, analytics, sql, roi, optimization"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Skill Analytics: Usage Mining, Context-Tax ROI & SQL Telemetry Engine

The `skill-analytics` skill mines local agent conversation transcripts (with 0% sampling and automatic `transcript.jsonl` + `transcript_full.jsonl` truncation merging) alongside your installed skill inventory across all tiers (`builtin`, `plugin`, `global`, `workspace`, and `catalog`) into a local SQLite warehouse (`skill_analytics.db`). Pair it with `skill-optimizer` to prune zero-use "shelfware" skills, rewrite under-performing frontmatter descriptions, and reconcile `~/.config/kungfu/state.json` telemetry.

## Available scripts
- `scripts/analyze.py`: Zero-dependency Python 3 CLI for incremental transcript ingestion, full historical rebuilds, pre-packaged ROI/trigger/drift reports, ad-hoc SQL queries, and deterministic `state.json` backfills.
- `scripts/test_analyze.py`: Automated unit and regression test suite validating schema DDL, views, parser accuracy, and markdown SQL code blocks.

---

## ⚡ Quick Start & Primary Actions

All operations are driven via `scripts/analyze.py` (runnable via `kungfu run skill-analytics analyze.py` or `uv run scripts/analyze.py`):

```bash
# 1. Incremental Sync (Only parses new or modified conversation transcripts)
uv run scripts/analyze.py sync --db skill_analytics.db

# 2. Full Historical Rebuild (Drops and re-mines all conversations from scratch)
uv run scripts/analyze.py sync --full --db skill_analytics.db

# 3. Run Pre-Packaged Analytical Reports
uv run scripts/analyze.py report overview --db skill_analytics.db
uv run scripts/analyze.py report roi --db skill_analytics.db
uv run scripts/analyze.py report triggers --db skill_analytics.db
uv run scripts/analyze.py report velocity --db skill_analytics.db
uv run scripts/analyze.py report gaps --db skill_analytics.db
uv run scripts/analyze.py report drift --db skill_analytics.db

# 4. Reconcile & Backfill ~/.config/kungfu/state.json (Dry-Run vs. Apply)
uv run scripts/analyze.py backfill-state --dry-run --db skill_analytics.db
uv run scripts/analyze.py backfill-state --apply --db skill_analytics.db

# 5. Run Ad-Hoc SQL Query
uv run scripts/analyze.py query "SELECT skill_name, source_tier, tier1_tokens_est, total_activations, roi_recommendation FROM v_skill_roi LIMIT 15" --db skill_analytics.db
```

If `--db` is omitted, the script defaults to `skill_analytics.db` in the current working directory.

---

## 🗄️ Database Schema & Relational Structure

The database maintains 5 relational tables and 7 analytical views. Full column-level DDL and constraints are documented in [`references/schema.md`](references/schema.md).

### Tables

1. **`skills_inventory`**: Every discovered skill across `builtin`, `plugin`, `global`, `workspace`, and `catalog` tiers, including `is_always_in_prompt`, `tier1_tokens_est` (`name + description` routing cost), and `tier2_tokens_est` (`SKILL.md` body cost).
2. **`conversations`**: Metadata across the union of `conversation_summaries.db` and `brain/` transcript directories (`total_steps`, `user_input_steps`, `planner_steps`, `first_step_at`, `last_step_at`).
3. **`ingestion_state`**: File size, `mtime_ns`, and SHA-256 head watermarks per conversation for sub-second incremental updates.
4. **`skill_events`**: Every extracted skill event across all sources:
   - `direct_skill_view`: Direct `view_file` activations on any `*/<skill>/SKILL.md`.
   - `skill_resource_view`: Companion `references/`, `examples/`, `assets/`, or `scripts/` reads.
   - `cli_invocation`: `kungfu` CLI commands (`load`, `learn`, `run`, `find`, `show`, `list`, `status`, `update`, `forget`, `catalog`) and direct script executions (`script_exec`).
   - `user_notation`: User prompt shortcuts (`modern_::`, `classic_//`, `find_:?`).
   - Includes `trigger_mode` (`autonomous`, `user_explicit`, `rule_driven`) and `is_self_test` (`0` for production, `1` for test/authoring).
5. **`state_telemetry_snapshot`**: Snapshot of `~/.config/kungfu/state.json` `history` (`recorded_count`, `page_load_count`, `subpath_load_count`, `run_count`, `last_loaded_at`).

---

## 📊 Analytical SQL Views

| View Name | Description | Key Columns |
| :--- | :--- | :--- |
| `v_skill_roi` | Context-Tax vs. Activation ROI across all skill tiers | `skill_name`, `source_tier`, `is_always_in_prompt`, `tier1_tokens_est`, `total_activations`, `autonomous_activations`, `explicit_activations`, `resource_reads`, `script_runs`, `roi_recommendation` |
| `v_trigger_attribution` | Autonomous description matching vs. manual user overrides | `skill_name`, `source_tier`, `total_activations`, `autonomous_activations`, `explicit_activations`, `autonomous_share_pct`, `trigger_health` |
| `v_daily_invocations` | Daily time-series across event categories and actions | `day`, `invocation_kind`, `action`, `prod_count`, `test_count`, `distinct_conversations` |
| `v_subcommand_summary` | Aggregate counts and date bounds per command/notation | `invocation_kind`, `action`, `total_events`, `prod_events`, `self_test_events`, `conversations` |
| `v_search_gaps` | Search queries ranked by whether they led to a skill load | `search_query`, `invocation_kind`, `search_count`, `led_to_load_count`, `last_searched_at` |
| `v_skill_telemetry_drift` | Side-by-side audit of `state.json` vs. transcript ground truth | `skill_name`, `state_json_count`, `transcript_cli_load_primary`, `transcript_total_activations`, `drift_total_vs_state`, `drift_diagnosis` |

---

## 🔍 Pairing with `skill-optimizer`: Core SQL Workflows

Tested SQL recipes for skill portfolio optimization are in [`references/queries.md`](references/queries.md).

### 1. Detect Shelfware Skills Consuming System-Prompt Tokens
Find skills with `is_always_in_prompt = 1` that add token overhead on every turn but have `0` activations:
```sql
SELECT
    skill_name,
    source_tier,
    source_origin,
    tier1_tokens_est,
    cumulative_prompt_tax_tokens,
    roi_recommendation
FROM v_skill_roi
WHERE is_always_in_prompt = 1
  AND total_activations = 0
  AND script_runs = 0
ORDER BY tier1_tokens_est DESC;
```

### 2. Find Skills Whose Descriptions Fail to Trigger Autonomously
Identify skills that are only activated when the user manually types `::skill` or `//skill` (`NEEDS_DESCRIPTION_TUNING` or `WEAK_AUTONOMOUS_TRIGGER`), then feed them to `skill-optimizer`:
```sql
SELECT
    skill_name,
    source_tier,
    total_activations,
    autonomous_activations,
    explicit_activations,
    autonomous_share_pct,
    trigger_health
FROM v_trigger_attribution
WHERE trigger_health IN ('NEEDS_DESCRIPTION_TUNING', 'WEAK_AUTONOMOUS_TRIGGER')
ORDER BY explicit_activations DESC;
```

---

## 📚 Progressive Disclosure & References

- **Full DDL Schema Reference**: [`references/schema.md`](references/schema.md) — Complete SQLite table definitions, indexes, and analytical view logic.
- **SQL Query Cookbook**: [`references/queries.md`](references/queries.md) — Ready-to-run queries for Context-Tax ROI, Trigger Attribution, Progressive Disclosure depth, Catalog Gap discovery, and KungFu `state.json` drift.
