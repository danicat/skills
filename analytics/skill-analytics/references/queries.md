# Skill Analytics SQL Query Cookbook

All SQL recipes below run directly against `skill_analytics.db` using `uv run scripts/analyze.py query "<SQL>"`. Pair these queries with `skill-optimizer` to prune shelfware skills, tune under-performing frontmatter descriptions, and discover catalog gaps.

---

## 1. Shelfware & Context-Tax Audit (Always-In-Prompt Skills with 0 Activations)

Identifies built-in, plugin, and globally installed skills that consume system-prompt tokens on every turn (`is_always_in_prompt = 1`) but have never been activated or executed in production conversations.

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
ORDER BY tier1_tokens_est DESC, skill_name ASC;
```

---

## 2. High-Demand JIT Skills to Promote to Global Scope

Finds catalog skills frequently loaded on-demand via `kungfu load` (`PROMOTE_TO_GLOBAL`) that are not yet installed globally.

```sql
SELECT
    skill_name,
    category,
    total_activations,
    resource_reads,
    script_runs,
    conversations_used,
    conversation_reach_pct || '%' AS reach_pct,
    last_used_at
FROM v_skill_roi
WHERE is_always_in_prompt = 0
  AND total_activations >= 5
ORDER BY total_activations DESC, conversations_used DESC;
```

---

## 3. Trigger Attribution Audit for `skill-optimizer` (Manual Override vs. Autonomous Match)

Pinpoints skills that users must manually invoke with `::skill`, `//skill`, or `/skill` because agents fail to match their frontmatter `description` autonomously (`NEEDS_DESCRIPTION_TUNING` or `WEAK_AUTONOMOUS_TRIGGER`).

```sql
SELECT
    skill_name,
    source_tier,
    total_activations,
    autonomous_activations,
    explicit_activations,
    autonomous_share_pct || '%' AS auto_pct,
    trigger_health
FROM v_trigger_attribution
WHERE total_activations > 0
ORDER BY explicit_activations DESC, total_activations DESC;
```

---

## 4. Progressive Disclosure Depth (Root Loads vs. Reference Reads & Script Runs)

Measures how deeply agents engage with each skill's Tier-3 companion `references/` and `scripts/` after loading the main `SKILL.md`.

```sql
SELECT
    skill_name,
    source_tier,
    total_activations,
    resource_reads,
    script_runs,
    ROUND(1.0 * (resource_reads + script_runs) / MAX(1, total_activations), 2) AS tier3_depth_ratio
FROM v_skill_roi
WHERE total_activations > 0 OR resource_reads > 0 OR script_runs > 0
ORDER BY (resource_reads + script_runs) DESC, total_activations DESC
LIMIT 20;
```

---

## 5. Catalog Gap Discovery (Unmet `kungfu find` and `:?` Searches)

Lists search queries issued via `kungfu find` or `:?` that did not result in a subsequent skill load within 12 steps, revealing missing topics in the catalog.

```sql
SELECT
    search_query,
    invocation_kind,
    search_count,
    led_to_load_count,
    last_searched_at
FROM v_search_gaps
WHERE led_to_load_count = 0
ORDER BY search_count DESC, last_searched_at DESC;
```

---

## 6. User Prompt Notation Adoption Over Time (`::skill` vs. `//skill` vs. `:?`)

Tracks the evolution of user prompt shortcut notations across conversations.

```sql
SELECT
    substr(step_created_at, 1, 10) AS day,
    notation_type,
    COUNT(*) AS notation_count,
    COUNT(DISTINCT conversation_id) AS conversations
FROM skill_events
WHERE invocation_kind = 'user_notation'
  AND is_self_test = 0
GROUP BY day, notation_type
ORDER BY day DESC, notation_count DESC;
```

---

## 7. KungFu `state.json` Telemetry Drift Audit

Compares recorded `load_count` values in `~/.config/kungfu/state.json` against ground-truth transcript activations.

```sql
SELECT
    skill_name,
    state_json_count,
    transcript_cli_load_primary,
    transcript_learn_load,
    transcript_direct_views,
    transcript_total_activations,
    drift_total_vs_state,
    drift_diagnosis
FROM v_skill_telemetry_drift
ORDER BY ABS(drift_total_vs_state) DESC, transcript_total_activations DESC;
```
