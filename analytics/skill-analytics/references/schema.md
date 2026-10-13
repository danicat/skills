# Skill Analytics SQLite Schema Reference

The Skill Analytics database (`skill_analytics.db`) is provisioned and maintained automatically by `scripts/analyze.py`. All tables, indexes, and analytical views are created during `sync` operations.

---

## 1. Relational Tables

### `skills_inventory`
Stores every discovered skill across built-in, plugin, global, workspace, and catalog tiers along with its Tier-1 routing token footprint (`name + description`) and Tier-2 body metrics.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `skill_name` | `TEXT` | PRIMARY KEY | Canonical kebab-case skill identifier |
| `source_tier` | `TEXT` | NOT NULL | Installation tier (`builtin`, `plugin`, `global`, `workspace`, `catalog`) |
| `source_origin` | `TEXT` | NOT NULL | Plugin name, catalog repository, or scope origin |
| `category` | `TEXT` | | Skill category (`agents`, `analytics`, `coding`, `game-dev`, `media`, `writing`) |
| `version` | `TEXT` | | Semantic version from frontmatter (`0.5.0`, `unversioned`) |
| `description` | `TEXT` | | Full Tier-1 routing description string |
| `skill_path` | `TEXT` | | Local path or canonical remote URL |
| `is_always_in_prompt` | `INTEGER` | NOT NULL, DEFAULT 0 | `1` if injected into the system prompt `<skills>` block on every turn; `0` if JIT-only |
| `tier1_chars` | `INTEGER` | NOT NULL, DEFAULT 0 | Character count of `name + description` |
| `tier1_tokens_est` | `INTEGER` | NOT NULL, DEFAULT 0 | Estimated Tier-1 routing token tax per turn |
| `tier2_lines` | `INTEGER` | NOT NULL, DEFAULT 0 | Line count of `SKILL.md` body |
| `tier2_tokens_est` | `INTEGER` | NOT NULL, DEFAULT 0 | Estimated Tier-2 instruction token count when loaded |
| `synced_at` | `TEXT` | NOT NULL | ISO-8601 UTC timestamp of inventory scan |

---

### `conversations`
Stores conversation-level metadata across the union of `conversation_summaries.db` and `brain/` transcript directories.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `conversation_id` | `TEXT` | PRIMARY KEY | UUID of the agent conversation |
| `title` | `TEXT` | | Conversation summary title |
| `workspace_uris` | `TEXT` | | Active workspace URI(s) |
| `git_origin_urls` | `TEXT` | | Parent conversation ID or git origin metadata |
| `created_at` | `TEXT` | | ISO-8601 creation timestamp |
| `updated_at` | `TEXT` | | ISO-8601 last modified timestamp |
| `first_step_at` | `TEXT` | | Timestamp of earliest step in transcript |
| `last_step_at` | `TEXT` | | Timestamp of latest step in transcript |
| `total_steps` | `INTEGER` | DEFAULT 0 | Total steps parsed in transcript |
| `user_input_steps` | `INTEGER` | DEFAULT 0 | Count of `USER_INPUT` steps |
| `planner_steps` | `INTEGER` | DEFAULT 0 | Count of `PLANNER_RESPONSE` steps |
| `has_transcript` | `INTEGER` | DEFAULT 0 | `1` if `transcript.jsonl` or `transcript_full.jsonl` exists on disk |
| `has_summary_db` | `INTEGER` | DEFAULT 0 | `1` if indexed in `conversation_summaries.db` |
| `ingested_at` | `TEXT` | NOT NULL | ISO-8601 UTC ingestion timestamp |

---

### `ingestion_state`
Tracks file size, modification timestamp (`mtime_ns`), and SHA-256 head watermarks per conversation for fast incremental syncing.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `conversation_id` | `TEXT` | PRIMARY KEY | Conversation UUID |
| `transcript_path` | `TEXT` | NOT NULL | Path to transcript file |
| `file_size_bytes` | `INTEGER` | NOT NULL | Combined byte size of compact and full transcripts |
| `file_mtime_ns` | `INTEGER` | NOT NULL | Latest modification time in nanoseconds |
| `last_step_index` | `INTEGER` | NOT NULL | Highest `step_index` ingested |
| `sha256_head` | `TEXT` | NOT NULL | SHA-256 digest of leading 64 KB |
| `updated_at` | `TEXT` | NOT NULL | ISO-8601 UTC watermark update time |

---

### `skill_events`
Stores every extracted skill activation, companion resource view, CLI subcommand execution, script run, and user prompt notation (`::skill`, `//skill`, `:?`, `/skill`).

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | Unique event ID |
| `conversation_id` | `TEXT` | NOT NULL | Conversation UUID |
| `step_index` | `INTEGER` | NOT NULL | Step index within the transcript |
| `step_created_at` | `TEXT` | | ISO-8601 UTC step timestamp |
| `step_type` | `TEXT` | NOT NULL | `USER_INPUT` or `PLANNER_RESPONSE` |
| `invocation_kind` | `TEXT` | NOT NULL | `direct_skill_view`, `skill_resource_view`, `cli_invocation`, or `user_notation` |
| `notation_type` | `TEXT` | | For `user_notation`: `modern_::`, `classic_//`, `find_:?` |
| `subcommand` | `TEXT` | | Subcommand or action (`load`, `find`, `learn`, `run`, `script_exec`, `show`, `list`, `status`, `update`, `forget`, `catalog`, `view_file`) |
| `target_skill` | `TEXT` | | Target skill name (or comma-joined list for rejected multi-skill batches) |
| `raw_args` | `TEXT` | | Parsed CLI arguments or file path |
| `subpath_or_script` | `TEXT` | | Loaded subpath (`references/...`), script name, `--load`, or search query |
| `page_number` | `INTEGER` | DEFAULT 1 | Page number for paginated `kungfu load -p N` calls |
| `trigger_mode` | `TEXT` | DEFAULT `'autonomous'` | `autonomous` (frontmatter description match), `user_explicit` (`::`, `//`, `/`), or `rule_driven` |
| `source_tier` | `TEXT` | | `builtin`, `plugin`, `global`, `workspace`, `kungfu_cli`, `direct_script`, `user_prompt`, `repo_authoring` |
| `raw_snippet` | `TEXT` | NOT NULL | Command line or prompt excerpt |
| `is_self_test` | `INTEGER` | DEFAULT 0 | `1` if development self-test or repo authoring inspection; `0` for production usage |

---

### `state_telemetry_snapshot`
Stores a snapshot of `~/.config/kungfu/state.json` `history` counters for drift comparison and deterministic backfilling.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `skill_name` | `TEXT` | PRIMARY KEY | Skill name in `state.json` |
| `recorded_count` | `INTEGER` | NOT NULL | `load_count` in `state.json` |
| `page_load_count` | `INTEGER` | NOT NULL, DEFAULT 0 | Continuation page loads (`-p 2+`) |
| `subpath_load_count` | `INTEGER` | NOT NULL, DEFAULT 0 | Companion subpath loads (`skill/references/...`) |
| `run_count` | `INTEGER` | NOT NULL, DEFAULT 0 | Bundled script executions (`kungfu run`) |
| `last_loaded_at` | `TEXT` | NOT NULL | `last_seen_at` ISO-8601 timestamp |
| `is_learned` | `INTEGER` | NOT NULL, DEFAULT 0 | `1` if currently installed in global or workspace scope |
| `snapshot_at` | `TEXT` | NOT NULL | ISO-8601 UTC snapshot timestamp |

---

## 2. Analytical SQL Views

| View Name | Description |
| :--- | :--- |
| `v_skill_roi` | Joins `skills_inventory` and `skill_events` to compute Context-Tax vs. Activation ROI (`SHELFWARE_CANDIDATE`, `LOW_ROI_GLOBAL`, `PROMOTE_TO_GLOBAL`, `ACTIVE_GLOBAL`, `HEALTHY_JIT`). |
| `v_trigger_attribution` | Breaks down activations per skill by `autonomous_activations`, `explicit_activations`, `rule_activations`, `autonomous_share_pct`, and `trigger_health` (`NEEDS_DESCRIPTION_TUNING`, `WEAK_AUTONOMOUS_TRIGGER`, `HEALTHY_TRIGGER`). |
| `v_daily_invocations` | Daily time-series of events grouped by `day`, `invocation_kind`, and `action`. |
| `v_subcommand_summary` | Aggregate counts, production vs. self-test split, conversation reach, and first/last seen timestamps by `invocation_kind` and `action`. |
| `v_search_gaps` | Ranks `kungfu find` and `:?` search queries by whether they led to a subsequent skill load (`led_to_load_count`). |
| `v_skill_telemetry_drift` | Compares `state.json` `load_count` against mined CLI primary loads, `learn --load`, and direct `SKILL.md` views with diagnostic classifications. |
| `kungfu_invocations` | Compatibility projection over `skill_events`. |
