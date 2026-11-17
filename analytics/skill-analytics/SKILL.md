---
name: skill-analytics
description: >
  Mine and analyze Agent Skill usage, prompt-tax ROI, and trigger attribution
  from conversation transcripts in a local SQLite database. Scans conversation
  transcripts and installed skill tiers (built-in, plugin, global, workspace,
  and catalog) to detect zero-use shelfware and tune activation descriptions.
  Activate when analyzing skill usage over time, auditing system-prompt token
  overhead, measuring autonomous vs. explicit (::skill or //skill) triggers, or
  querying conversation skill events with SQL.
license: Apache-2.0
metadata:
  category: analytics
  tags: "agent-skills, transcripts, telemetry, usage, roi"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Skill analytics

The `skill-analytics` skill mines local agent conversation transcripts (with full coverage and automatic `transcript.jsonl` + `transcript_full.jsonl` truncation merging) alongside your installed skill inventory across `builtin`, `plugin`, `global`, `workspace`, and `catalog` tiers into a local `SQLite` database (`skill_analytics.db`). Use these metrics to prune zero-use idle skills and improve under-performing frontmatter descriptions.

## Available scripts

- `scripts/analyze.py`: Zero-dependency Python `3.11+` CLI (`uv run scripts/analyze.py`) for incremental transcript syncs, full rebuilds, pre-packaged ROI/trigger/velocity/gap reports, and SQL queries.
- `scripts/test_analyze.py`: Unit and regression test suite covering schema DDL, views, parser accuracy (`read_file`, `view_file`, nested `::` notation, `.go` scripts), and Markdown SQL blocks.

---

## Quick start and primary actions

Run all operations with `uv run scripts/analyze.py`:

```bash
# 1. Incremental sync (only parses new or modified conversation transcripts)
uv run scripts/analyze.py sync --db skill_analytics.db

# 2. Full historical rebuild (drops and re-mines all conversations from scratch)
uv run scripts/analyze.py sync --full --db skill_analytics.db

# 3. Run pre-packaged analytical reports
uv run scripts/analyze.py report overview --db skill_analytics.db
uv run scripts/analyze.py report roi --db skill_analytics.db
uv run scripts/analyze.py report triggers --db skill_analytics.db
uv run scripts/analyze.py report velocity --db skill_analytics.db
uv run scripts/analyze.py report gaps --db skill_analytics.db

# 4. Run an ad-hoc SQL query
uv run scripts/analyze.py query "SELECT skill_name, source_tier, tier1_tokens_est, total_activations, roi_recommendation FROM v_skill_roi LIMIT 15" --db skill_analytics.db
```

When you omit `--db`, the script defaults to `skill_analytics.db` in the current working directory.

---

## Database schema and relational structure

The database maintains `4` tables and `5` analytical views. See [`references/schema.md`](references/schema.md) for full column definitions and constraints.

### Tables

1. **`skills_inventory`**: Discovered skills across `builtin`, `plugin`, `global`, `workspace`, and `catalog` tiers, storing `is_always_in_prompt`, `tier1_tokens_est` (`name + description` routing tax), and `tier2_tokens_est` (`SKILL.md` body tokens).
2. **`conversations`**: Metadata across the union of `conversation_summaries.db` and `brain/` transcript folders (`total_steps`, `user_input_steps`, `planner_steps`, `first_step_at`, `last_step_at`).
3. **`ingestion_state`**: File size, `mtime_ns`, and SHA-256 head watermarks per conversation for fast incremental updates.
4. **`skill_events`**: Extracted skill events across conversation transcripts:
   - `direct_skill_view`: Direct `read_file` and legacy `view_file` initial reads (`page_number = 1`) on `*/<skill>/SKILL.md`.
   - `skill_resource_view`: Companion `references/`, `examples/`, `assets/`, `scripts/`, `evals/`, or `resources/` reads.
   - `cli_invocation`: CLI calls (`load`, `learn`, `run`, `find`, `show`, `list`, `status`, `update`, `forget`, `catalog`, `telemetry`) and direct script executions (`script_exec`, including `.py`, `.sh`, `.js`, `.ts`, `.go`).
   - `user_notation`: User prompt shortcuts (`modern_::`, `classic_//`, `find_:?`, including nested `::skill(params...)` expressions).
   - Tracks `trigger_mode` (`autonomous`, `user_explicit`, `rule_driven`) and `is_self_test` (`0` for production usage, `1` for self-tests or authoring).

### Gemini 4 prompt tax and implicit caching

Always-in-prompt skills impose two separate costs:
- **Billed token cost (`cache_adjusted_tax_tokens`)**: Gemini 4 applies a `90%` implicit system-prompt cache discount after turn `1` of each conversation, so turn `1` pays full `tier1_tokens_est` while subsequent `planner_steps` pay `10%`.
- **Attention dilution (`tier1_tokens_est`)**: Every turn still passes `tier1_tokens_est` through model attention alongside all other installed skills, increasing routing interference as the prompt grows.

---

## Analytical SQL views

| View Name | Description | Key Columns |
| :--- | :--- | :--- |
| `v_skill_roi` | Prompt tax vs. activation ROI across all tiers | `skill_name`, `source_tier`, `is_always_in_prompt`, `tier1_tokens_est`, `cumulative_prompt_tax_tokens`, `cache_adjusted_tax_tokens`, `total_activations`, `roi_recommendation` |
| `v_trigger_attribution` | Autonomous description match vs. manual triggers | `skill_name`, `source_tier`, `total_activations`, `autonomous_activations`, `explicit_activations`, `autonomous_share_pct`, `trigger_health` |
| `v_daily_invocations` | Daily time-series across event types and actions | `day`, `invocation_kind`, `action`, `prod_count`, `test_count`, `distinct_conversations` |
| `v_subcommand_summary` | Total counts and date bounds per command or shortcut | `invocation_kind`, `action`, `total_events`, `prod_events`, `self_test_events`, `conversations` |
| `v_search_gaps` | Search queries ranked by whether they led to a load | `search_query`, `invocation_kind`, `search_count`, `led_to_load_count`, `last_searched_at` |

---

## Core SQL workflows for skill portfolio tuning

Tested SQL recipes live in [`references/queries.md`](references/queries.md).

### 1. Detect idle always-in-prompt skills

Find always-in-prompt skills (`is_always_in_prompt = 1`) that add routing overhead on every turn with `0` activations:

```sql
SELECT
    skill_name,
    source_tier,
    source_origin,
    tier1_tokens_est,
    cumulative_prompt_tax_tokens,
    cache_adjusted_tax_tokens,
    roi_recommendation
FROM v_skill_roi
WHERE is_always_in_prompt = 1
  AND total_activations = 0
  AND script_runs = 0
ORDER BY tier1_tokens_est DESC;
```

### 2. Find skills whose descriptions miss autonomous triggers

Identify skills invoked manually (`::skill` or `//skill`) because agents miss their frontmatter descriptions (`NEEDS_DESCRIPTION_TUNING` or `WEAK_AUTONOMOUS_TRIGGER`):

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

## Progressive disclosure and references

- **Full DDL schema reference**: [`references/schema.md`](references/schema.md): Complete `SQLite` table definitions, indexes, and analytical view logic.
- **SQL query cookbook**: [`references/queries.md`](references/queries.md): Tested queries for prompt-tax ROI, trigger attribution, progressive disclosure depth, catalog gap discovery, and multi-skill workflows.
