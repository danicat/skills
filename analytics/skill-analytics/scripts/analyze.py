#!/usr/bin/env python3
# Copyright 2026 Daniela Petruzalek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Skill Analytics: Universal Agent Skill Usage, Context-Tax ROI & Telemetry Engine.

Mines all local agent conversations (0% sampling), inventories all installed and catalog
skills across built-in, plugin, global, workspace, and remote catalog tiers, and populates
a local SQLite warehouse (`skill_analytics.db`) for deep SQL analytics and optimization.

Capabilities:
1. Universal Skill Activation Mapping (`view_file` on any `SKILL.md`, companion `references/`,
   `scripts/`, and `kungfu` CLI invocations).
2. Context-Tax vs. Activation ROI (`v_skill_roi`) — compares each skill's Tier-1 system-prompt
   token footprint against real conversation activations to detect shelfware vs. high-ROI skills.
3. Trigger Attribution (`v_trigger_attribution`) — classifies activations into `autonomous`
   (frontmatter description match), `user_explicit` (`::skill`, `//skill`, `/skill`), and
   `rule_driven` to help `skill-optimizer` refine skill descriptions.
4. Search Gap Discovery (`v_search_gaps`) — surfaces `kungfu find` and `:?` queries that did
   not lead to a skill activation.
5. KungFu State Telemetry Drift & Backfill (`v_skill_telemetry_drift`, `backfill-state`).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

HOME_DIR = pathlib.Path.home()
DEFAULT_BRAIN_DIR = HOME_DIR / ".gemini" / "antigravity" / "brain"
DEFAULT_SUMMARIES_DB = HOME_DIR / ".gemini" / "antigravity" / "conversation_summaries.db"
DEFAULT_STATE_JSON = HOME_DIR / ".config" / "kungfu" / "state.json"
DEFAULT_DB_PATH = pathlib.Path("skill_analytics.db")

UNIT_TEST_POLLUTED_SKILLS = {
    "evals",
    "latest-version",
    "engineering-flow",
    "pyhd",
}

BUILTIN_KNOWN_SKILLS = {
    "kungfu",
    "godoctor",
    "ebitengineer",
    "game-design",
    "procedural-art",
    "procedural-composer",
    "sprite-animation",
    "vibe-game-developer",
    "lyria",
    "nano-banana",
    "adr-template",
    "engineering-flow",
    "google-oss",
    "latest-version",
    "pyhd",
    "rfc-template",
    "double-diamond",
    "intercom",
    "parallel",
    "skill-optimizer",
    "skill-analytics",
    "swarm-coding",
    "uno-reverse",
    "buffer",
    "deslopify",
    "google-blog-style",
    "inverted-pyramid",
    "seo-optimizer",
    "social-copy",
    "buffer-analytics",
    "google-analytics",
    "search-analytics",
    "pagespeed-insights",
    "gemma4go",
    "gemini-api-dev",
    "gemini-interactions-api",
    "gemini-live-api-dev",
    "gemini-omni-flash-api",
    "tech-interviewer",
    "tech-publisher",
    "tech-reviewer",
    "tech-writer",
    "speedgrapher",
    "generative_ui",
    "antigravity-guide",
    "agy-customizations",
    "automation",
    "brain-visualizer",
    "chrome-devtools",
    "chrome-extensions",
    "a11y-debugging",
    "debug-optimize-lcp",
    "memory-leak-debugging",
    "modern-web-guidance",
    "paint-studio",
    "playtest-studio",
    "plugin",
    "troubleshooting",
    "ui-extension",
    "ui-plugin-navigation",
    "migrate-workflows",
    "developing-genkit-go",
    "developing-genkit-js",
    "ag-ui-a2ui-integration",
}

KNOWN_SUBCOMMANDS = {
    "load",
    "find",
    "search",
    "learn",
    "add",
    "run",
    "show",
    "list",
    "status",
    "update",
    "forget",
    "unlearn",
    "catalog",
    "version",
    "help",
}

COLON_FALSE_POSITIVES = {
    "before",
    "after",
    "first-line",
    "first-letter",
    "selection",
    "placeholder",
    "marker",
    "backdrop",
    "slotted",
    "part",
    "cue",
    "webkit-scrollbar",
    "webkit-slider-thumb",
    "moz-placeholder",
    "new",
    "default",
    "delete",
    "size_t",
    "string",
    "vector",
    "map",
    "cout",
    "cin",
    "endl",
    "optional",
    "variant",
    "function",
    "move",
    "forward",
    "chrono",
    "filesystem",
    "ios",
    "runtime_error",
    "exception",
    "from",
    "into",
    "iter",
    "collect",
    "unwrap",
    "ok",
    "err",
    "some",
    "none",
    "path",
    "env",
    "fs",
    "io",
    "net",
    "sync",
    "thread",
    "time",
    "fmt",
    "str",
    "vec",
    "box",
    "rc",
    "arc",
    "cell",
    "refcell",
    "pin",
    "future",
    "task",
    "poll",
    "main",
    "test",
    "cfg",
    "derive",
    "allow",
    "warn",
    "deny",
    "forbid",
    "Deprecated",
    "Override",
    "SuppressWarnings",
}

DOC_PLACEHOLDER_TARGETS = {
    "skill",
    "skill-name",
    "skill1",
    "skill2",
    "skills",
    "category",
    "cat",
    "keyword",
    "keywords",
    "query",
    "term",
    "notation",
    "command",
    "script",
    "subpath",
    "catalog",
    "args",
}

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
SYSTEM_TAG_RE = re.compile(
    r"<(RULE|skills|identity|user_information|mcp_servers|subagents|messaging|"
    r"conversation_transcript|artifacts|slash_commands|guidelines|communication_style|"
    r"CONTEXT_SUMMARY|ADDITIONAL_METADATA)\b[^>]*>.*?</\1>",
    re.DOTALL | re.IGNORECASE,
)

CLASSIC_SLASH_RE = re.compile(
    r"(?:^|(?<=\s))//([a-z][a-z0-9]*(?:-[a-z0-9]+)*)(?=\s|$|[.,;!?)\]])"
)
SINGLE_SLASH_RE = re.compile(
    r"(?:^|(?<=\s))/([a-z][a-z0-9]*(?:[-_][a-z0-9]+)*)(?=\s|$|[.,;!?)\]])"
)
MODERN_FIND_RE = re.compile(
    r"(?:^|(?<=\s))(::\?|:\?)(?!\s*$)([^\n`|<>{}\[\]]{1,80})"
)
MODERN_COLON_RE = re.compile(
    r"(?:^|(?<![:\w/\\]))"
    r"(::(?:\+\+\*|\+\*|\+\+|\+|--|-|\*|>|:|\^_?\^|@\^?)?"
    r"[a-zA-Z0-9_][a-zA-Z0-9_./@:!-]*)"
    r"(?:\(([^)\s\n]{1,40})\)?)?"
)

SKILL_MD_PATH_RE = re.compile(
    r"(?:^|/)([^/]+)/SKILL\.md$"
)
SKILL_RESOURCE_PATH_RE = re.compile(
    r"(?:^|/)(?:skills|_skills)/([^/]+)/(references|examples|assets|scripts|evals)/(.+)$"
)
DIRECT_SCRIPT_EXEC_RE = re.compile(
    r"(?:^|\s|\"|')([^\s\"']*/([^/\s\"']+)/scripts/([a-zA-Z0-9_.-]+\.(?:py|sh|mjs|js|ts)))"
)

SCHEMA_DDL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS skills_inventory (
    skill_name TEXT PRIMARY KEY,
    source_tier TEXT NOT NULL,
    source_origin TEXT NOT NULL,
    category TEXT,
    version TEXT,
    description TEXT,
    skill_path TEXT,
    is_always_in_prompt INTEGER NOT NULL DEFAULT 0,
    tier1_chars INTEGER NOT NULL DEFAULT 0,
    tier1_tokens_est INTEGER NOT NULL DEFAULT 0,
    tier2_lines INTEGER NOT NULL DEFAULT 0,
    tier2_tokens_est INTEGER NOT NULL DEFAULT 0,
    synced_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT,
    workspace_uris TEXT,
    git_origin_urls TEXT,
    created_at TEXT,
    updated_at TEXT,
    first_step_at TEXT,
    last_step_at TEXT,
    total_steps INTEGER DEFAULT 0,
    user_input_steps INTEGER DEFAULT 0,
    planner_steps INTEGER DEFAULT 0,
    has_transcript INTEGER DEFAULT 0,
    has_summary_db INTEGER DEFAULT 0,
    ingested_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_state (
    conversation_id TEXT PRIMARY KEY,
    transcript_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    file_mtime_ns INTEGER NOT NULL,
    last_step_index INTEGER NOT NULL,
    sha256_head TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    step_created_at TEXT,
    step_type TEXT NOT NULL,
    invocation_kind TEXT NOT NULL,
    notation_type TEXT,
    subcommand TEXT,
    target_skill TEXT,
    raw_args TEXT,
    subpath_or_script TEXT,
    page_number INTEGER DEFAULT 1,
    trigger_mode TEXT DEFAULT 'autonomous',
    source_tier TEXT,
    raw_snippet TEXT NOT NULL,
    is_self_test INTEGER DEFAULT 0
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_skill_events_unique ON skill_events(
    conversation_id,
    step_index,
    invocation_kind,
    COALESCE(subcommand, ''),
    COALESCE(target_skill, ''),
    raw_snippet
);

CREATE INDEX IF NOT EXISTS idx_se_conv ON skill_events(conversation_id);
CREATE INDEX IF NOT EXISTS idx_se_kind ON skill_events(invocation_kind);
CREATE INDEX IF NOT EXISTS idx_se_subcmd ON skill_events(subcommand);
CREATE INDEX IF NOT EXISTS idx_se_skill ON skill_events(target_skill);
CREATE INDEX IF NOT EXISTS idx_se_created ON skill_events(step_created_at);
CREATE INDEX IF NOT EXISTS idx_se_trigger ON skill_events(trigger_mode);

CREATE TABLE IF NOT EXISTS state_telemetry_snapshot (
    skill_name TEXT PRIMARY KEY,
    recorded_count INTEGER NOT NULL,
    page_load_count INTEGER NOT NULL DEFAULT 0,
    subpath_load_count INTEGER NOT NULL DEFAULT 0,
    run_count INTEGER NOT NULL DEFAULT 0,
    last_loaded_at TEXT NOT NULL,
    is_learned INTEGER NOT NULL DEFAULT 0,
    snapshot_at TEXT NOT NULL
);

DROP VIEW IF EXISTS kungfu_invocations;
CREATE VIEW kungfu_invocations AS
SELECT
    id,
    conversation_id,
    step_index,
    step_created_at,
    step_type,
    invocation_kind,
    notation_type,
    subcommand,
    target_skill,
    raw_args,
    subpath_or_script,
    page_number,
    trigger_mode,
    source_tier,
    raw_snippet,
    is_self_test
FROM skill_events;

DROP VIEW IF EXISTS v_daily_invocations;
CREATE VIEW v_daily_invocations AS
SELECT
    COALESCE(substr(step_created_at, 1, 10), 'UNKNOWN') AS day,
    invocation_kind,
    COALESCE(subcommand, notation_type, 'view_file') AS action,
    COUNT(*) AS total_count,
    SUM(CASE WHEN is_self_test = 0 THEN 1 ELSE 0 END) AS prod_count,
    SUM(CASE WHEN is_self_test = 1 THEN 1 ELSE 0 END) AS test_count,
    COUNT(DISTINCT conversation_id) AS distinct_conversations
FROM skill_events
GROUP BY day, invocation_kind, action
ORDER BY day DESC, total_count DESC;

DROP VIEW IF EXISTS v_subcommand_summary;
CREATE VIEW v_subcommand_summary AS
SELECT
    invocation_kind,
    COALESCE(subcommand, notation_type, 'view_file') AS action,
    COUNT(*) AS total_events,
    SUM(CASE WHEN is_self_test = 0 THEN 1 ELSE 0 END) AS prod_events,
    SUM(CASE WHEN is_self_test = 1 THEN 1 ELSE 0 END) AS self_test_events,
    COUNT(DISTINCT conversation_id) AS conversations,
    MIN(step_created_at) AS first_seen_at,
    MAX(step_created_at) AS last_seen_at
FROM skill_events
GROUP BY invocation_kind, action
ORDER BY total_events DESC;

DROP VIEW IF EXISTS v_skill_roi;
CREATE VIEW v_skill_roi AS
WITH total_convs AS (
    SELECT MAX(1, COUNT(*)) AS conv_count FROM conversations WHERE has_transcript = 1
),
skill_usage AS (
    SELECT
        target_skill AS skill_name,
        SUM(CASE WHEN is_self_test = 0 AND (
            (invocation_kind = 'cli_invocation' AND subcommand = 'load' AND page_number = 1 AND subpath_or_script IS NULL)
            OR (invocation_kind = 'cli_invocation' AND subcommand = 'learn' AND subpath_or_script = '--load')
            OR invocation_kind = 'direct_skill_view'
        ) THEN 1 ELSE 0 END) AS total_activations,
        SUM(CASE WHEN is_self_test = 0 AND trigger_mode = 'autonomous' AND (
            (invocation_kind = 'cli_invocation' AND subcommand = 'load' AND page_number = 1 AND subpath_or_script IS NULL)
            OR (invocation_kind = 'cli_invocation' AND subcommand = 'learn' AND subpath_or_script = '--load')
            OR invocation_kind = 'direct_skill_view'
        ) THEN 1 ELSE 0 END) AS autonomous_activations,
        SUM(CASE WHEN is_self_test = 0 AND trigger_mode = 'user_explicit' AND (
            (invocation_kind = 'cli_invocation' AND subcommand = 'load' AND page_number = 1 AND subpath_or_script IS NULL)
            OR (invocation_kind = 'cli_invocation' AND subcommand = 'learn' AND subpath_or_script = '--load')
            OR invocation_kind = 'direct_skill_view'
        ) THEN 1 ELSE 0 END) AS explicit_activations,
        SUM(CASE WHEN is_self_test = 0 AND trigger_mode = 'rule_driven' AND (
            (invocation_kind = 'cli_invocation' AND subcommand = 'load' AND page_number = 1 AND subpath_or_script IS NULL)
            OR (invocation_kind = 'cli_invocation' AND subcommand = 'learn' AND subpath_or_script = '--load')
            OR invocation_kind = 'direct_skill_view'
        ) THEN 1 ELSE 0 END) AS rule_activations,
        SUM(CASE WHEN is_self_test = 0 AND (
            invocation_kind = 'skill_resource_view'
            OR (invocation_kind = 'cli_invocation' AND subcommand = 'load' AND subpath_or_script IS NOT NULL AND subpath_or_script != 'MULTI_SKILL_BATCH_REJECTED_V050')
        ) THEN 1 ELSE 0 END) AS resource_reads,
        SUM(CASE WHEN is_self_test = 0 AND invocation_kind = 'cli_invocation' AND subcommand IN ('run', 'script_exec') THEN 1 ELSE 0 END) AS script_runs,
        COUNT(DISTINCT CASE WHEN is_self_test = 0 AND (
            (invocation_kind = 'cli_invocation' AND subcommand IN ('load', 'run', 'script_exec'))
            OR invocation_kind IN ('direct_skill_view', 'skill_resource_view')
        ) THEN conversation_id END) AS conversations_used,
        MAX(CASE WHEN is_self_test = 0 THEN step_created_at END) AS last_used_at
    FROM skill_events
    WHERE target_skill IS NOT NULL AND instr(target_skill, ',') = 0
    GROUP BY target_skill
),
all_skill_names AS (
    SELECT skill_name FROM skills_inventory
    UNION
    SELECT skill_name FROM skill_usage WHERE total_activations > 0 OR script_runs > 0
)
SELECT
    a.skill_name,
    COALESCE(i.source_tier, 'catalog') AS source_tier,
    COALESCE(i.source_origin, 'catalog') AS source_origin,
    COALESCE(i.category, 'uncategorized') AS category,
    COALESCE(i.is_always_in_prompt, 0) AS is_always_in_prompt,
    COALESCE(i.tier1_tokens_est, 0) AS tier1_tokens_est,
    COALESCE(i.tier2_tokens_est, 0) AS tier2_tokens_est,
    COALESCE(u.total_activations, 0) AS total_activations,
    COALESCE(u.autonomous_activations, 0) AS autonomous_activations,
    COALESCE(u.explicit_activations, 0) AS explicit_activations,
    COALESCE(u.rule_activations, 0) AS rule_activations,
    COALESCE(u.resource_reads, 0) AS resource_reads,
    COALESCE(u.script_runs, 0) AS script_runs,
    COALESCE(u.conversations_used, 0) AS conversations_used,
    ROUND(100.0 * COALESCE(u.conversations_used, 0) / tc.conv_count, 2) AS conversation_reach_pct,
    CASE
        WHEN COALESCE(i.is_always_in_prompt, 0) = 1 THEN COALESCE(i.tier1_tokens_est, 0) * tc.conv_count
        ELSE 0
    END AS cumulative_prompt_tax_tokens,
    u.last_used_at,
    CASE
        WHEN COALESCE(i.is_always_in_prompt, 0) = 1 AND COALESCE(u.total_activations, 0) = 0 AND COALESCE(u.script_runs, 0) = 0
            THEN 'SHELFWARE_CANDIDATE'
        WHEN COALESCE(i.is_always_in_prompt, 0) = 1 AND COALESCE(u.total_activations, 0) <= 1 AND COALESCE(i.tier1_tokens_est, 0) >= 80
            THEN 'LOW_ROI_GLOBAL'
        WHEN COALESCE(i.is_always_in_prompt, 0) = 0 AND COALESCE(u.total_activations, 0) >= 8
            THEN 'PROMOTE_TO_GLOBAL'
        WHEN COALESCE(i.is_always_in_prompt, 0) = 1 AND COALESCE(u.total_activations, 0) > 0
            THEN 'ACTIVE_GLOBAL'
        ELSE 'HEALTHY_JIT'
    END AS roi_recommendation
FROM all_skill_names a
CROSS JOIN total_convs tc
LEFT JOIN skills_inventory i ON i.skill_name = a.skill_name
LEFT JOIN skill_usage u ON u.skill_name = a.skill_name
ORDER BY total_activations DESC, tier1_tokens_est DESC, a.skill_name ASC;

DROP VIEW IF EXISTS v_trigger_attribution;
CREATE VIEW v_trigger_attribution AS
SELECT
    skill_name,
    source_tier,
    category,
    total_activations,
    autonomous_activations,
    explicit_activations,
    rule_activations,
    ROUND(
        CASE WHEN total_activations > 0
            THEN 100.0 * autonomous_activations / total_activations
            ELSE 0.0
        END,
        1
    ) AS autonomous_share_pct,
    CASE
        WHEN total_activations = 0 THEN 'NO_ACTIVATIONS'
        WHEN rule_activations > 0 AND rule_activations >= autonomous_activations THEN 'RULE_DRIVEN_GATEWAY'
        WHEN autonomous_activations = 0 AND explicit_activations >= 3 THEN 'NEEDS_DESCRIPTION_TUNING'
        WHEN (100.0 * autonomous_activations / total_activations) < 35.0 AND explicit_activations >= 3 THEN 'WEAK_AUTONOMOUS_TRIGGER'
        ELSE 'HEALTHY_TRIGGER'
    END AS trigger_health
FROM v_skill_roi
WHERE total_activations > 0 OR is_always_in_prompt = 1
ORDER BY total_activations DESC, explicit_activations DESC;

DROP VIEW IF EXISTS v_search_gaps;
CREATE VIEW v_search_gaps AS
WITH search_events AS (
    SELECT
        id,
        conversation_id,
        step_index,
        step_created_at,
        invocation_kind,
        COALESCE(subpath_or_script, raw_args) AS search_query
    FROM skill_events
    WHERE is_self_test = 0
      AND (
          (invocation_kind = 'cli_invocation' AND subcommand = 'find')
          OR (invocation_kind = 'user_notation' AND notation_type = 'find_:?')
      )
)
SELECT
    s.search_query,
    s.invocation_kind,
    COUNT(*) AS search_count,
    COUNT(DISTINCT s.conversation_id) AS conversations,
    SUM(CASE WHEN EXISTS (
        SELECT 1 FROM skill_events e2
        WHERE e2.conversation_id = s.conversation_id
          AND e2.step_index > s.step_index
          AND e2.step_index <= s.step_index + 12
          AND e2.invocation_kind = 'cli_invocation'
          AND e2.subcommand IN ('load', 'learn')
    ) THEN 1 ELSE 0 END) AS led_to_load_count,
    MIN(s.step_created_at) AS first_searched_at,
    MAX(s.step_created_at) AS last_searched_at
FROM search_events s
WHERE s.search_query IS NOT NULL AND trim(s.search_query) != ''
GROUP BY s.search_query, s.invocation_kind
ORDER BY led_to_load_count ASC, search_count DESC;

DROP VIEW IF EXISTS v_skill_telemetry_drift;
CREATE VIEW v_skill_telemetry_drift AS
WITH all_skills AS (
    SELECT skill_name FROM state_telemetry_snapshot WHERE recorded_count > 0
    UNION
    SELECT DISTINCT target_skill AS skill_name
    FROM skill_events
    WHERE target_skill IS NOT NULL
      AND instr(target_skill, ',') = 0
      AND is_self_test = 0
      AND (
          invocation_kind = 'cli_invocation'
          OR (invocation_kind = 'direct_skill_view' AND target_skill = 'kungfu')
      )
),
transcript_agg AS (
    SELECT
        target_skill AS skill_name,
        SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'load' THEN 1 ELSE 0 END) AS cli_load_raw,
        SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'load' AND is_self_test = 0 THEN 1 ELSE 0 END) AS cli_load_prod,
        SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'load' AND is_self_test = 0 AND page_number = 1 AND subpath_or_script IS NULL THEN 1 ELSE 0 END) AS cli_load_primary,
        SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'learn' AND is_self_test = 0 AND subpath_or_script = '--load' THEN 1 ELSE 0 END) AS cli_learn_load,
        SUM(CASE WHEN invocation_kind = 'direct_skill_view' AND is_self_test = 0 AND target_skill = 'kungfu' THEN 1 ELSE 0 END) AS direct_views,
        SUM(CASE WHEN invocation_kind = 'user_notation' AND is_self_test = 0 THEN 1 ELSE 0 END) AS user_notations,
        SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'run' AND is_self_test = 0 THEN 1 ELSE 0 END) AS cli_runs,
        MIN(CASE WHEN is_self_test = 0 THEN step_created_at END) AS first_seen_at,
        MAX(CASE WHEN is_self_test = 0 AND (
            (invocation_kind = 'cli_invocation' AND subcommand = 'load')
            OR (invocation_kind = 'cli_invocation' AND subcommand = 'learn' AND subpath_or_script = '--load')
            OR (invocation_kind = 'direct_skill_view' AND target_skill = 'kungfu')
        ) THEN step_created_at END) AS last_activated_at,
        MAX(CASE WHEN is_self_test = 0 THEN step_created_at END) AS last_seen_at
    FROM skill_events
    WHERE target_skill IS NOT NULL
      AND instr(target_skill, ',') = 0
    GROUP BY target_skill
)
SELECT
    a.skill_name,
    COALESCE(s.recorded_count, 0) AS state_json_count,
    s.last_loaded_at AS state_json_last_loaded,
    COALESCE(s.is_learned, 0) AS is_learned,
    COALESCE(t.cli_load_raw, 0) AS transcript_cli_load_raw,
    COALESCE(t.cli_load_prod, 0) AS transcript_cli_load_prod,
    COALESCE(t.cli_load_primary, 0) AS transcript_cli_load_primary,
    COALESCE(t.cli_learn_load, 0) AS transcript_learn_load,
    COALESCE(t.direct_views, 0) AS transcript_direct_views,
    COALESCE(t.user_notations, 0) AS transcript_user_notations,
    COALESCE(t.cli_runs, 0) AS transcript_cli_runs,
    (COALESCE(t.cli_load_primary, 0) + COALESCE(t.cli_learn_load, 0) + COALESCE(t.direct_views, 0)) AS transcript_total_activations,
    (COALESCE(t.cli_load_primary, 0) - COALESCE(s.recorded_count, 0)) AS drift_cli_primary_vs_state,
    ((COALESCE(t.cli_load_primary, 0) + COALESCE(t.cli_learn_load, 0) + COALESCE(t.direct_views, 0)) - COALESCE(s.recorded_count, 0)) AS drift_total_vs_state,
    t.first_seen_at AS transcript_first_seen,
    t.last_activated_at AS transcript_last_activated,
    t.last_seen_at AS transcript_last_seen,
    CASE
        WHEN COALESCE(s.recorded_count, 0) = (COALESCE(t.cli_load_primary, 0) + COALESCE(t.cli_learn_load, 0) + COALESCE(t.direct_views, 0))
            THEN 'RECONCILED_OK'
        WHEN a.skill_name = 'kungfu' THEN 'DIRECT_VIEW_BYPASS_AND_V050_STATELESS_FREEZE'
        WHEN COALESCE(s.recorded_count, 0) = 0 AND (COALESCE(t.cli_load_primary, 0) + COALESCE(t.cli_learn_load, 0)) > 0 THEN 'POST_V050_STATELESS_LOAD_UNRECORDED'
        WHEN COALESCE(t.cli_load_primary, 0) > COALESCE(s.recorded_count, 0) THEN 'POST_V050_LOADS_FROZEN_IN_STATE_JSON'
        WHEN COALESCE(t.cli_load_primary, 0) = 0 AND COALESCE(s.recorded_count, 0) > 0 AND s.last_loaded_at LIKE '2026-10-08T01:09:%' THEN 'PRE_V050_UNIT_TEST_POLLUTION'
        WHEN COALESCE(s.recorded_count, 0) > COALESCE(t.cli_load_primary, 0) THEN 'PRE_V050_EXTERNAL_OR_SUBPATH_HISTORICAL'
        ELSE 'ACTIVITY_WITHOUT_LOAD'
    END AS drift_diagnosis
FROM all_skills a
LEFT JOIN state_telemetry_snapshot s ON s.skill_name = a.skill_name
LEFT JOIN transcript_agg t ON t.skill_name = a.skill_name
ORDER BY transcript_total_activations DESC, state_json_count DESC, a.skill_name ASC;
"""


def fail_fast(message: str, *, context: Optional[Dict[str, Any]] = None) -> None:
    """Abort immediately with rich structured context on stderr."""
    sys.stderr.write("\n" + "=" * 80 + "\n")
    sys.stderr.write(f"FATAL ERROR [skill-analytics]: {message}\n")
    if context:
        sys.stderr.write("Context:\n")
        for k, v in context.items():
            sys.stderr.write(f"  {k}: {v}\n")
    sys.stderr.write("=" * 80 + "\n")
    raise SystemExit(1)


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_skill_frontmatter(md_text: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from a SKILL.md document without external dependencies."""
    norm = md_text.replace("\r\n", "\n")
    if not norm.startswith("---\n"):
        return {"name": "", "description": "", "category": "", "version": "", "body": norm}
    parts = norm[4:].split("\n---\n", 1)
    if len(parts) < 2:
        return {"name": "", "description": "", "category": "", "version": "", "body": norm}

    raw_yaml, body = parts[0], parts[1]
    name = ""
    desc_lines: List[str] = []
    category = ""
    version = ""
    in_desc = False
    in_meta = False

    for line in raw_yaml.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("name:"):
            in_desc = False
            in_meta = False
            name = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("description:"):
            in_meta = False
            val = line.split(":", 1)[1].strip()
            if val in {">", "|", ">-", "|-"}:
                in_desc = True
            else:
                in_desc = False
                desc_lines.append(val.strip("\"'"))
        elif line.startswith("metadata:"):
            in_desc = False
            in_meta = True
        elif in_desc and (line.startswith("  ") or line.startswith("\t")):
            desc_lines.append(stripped)
        elif in_meta and (line.startswith("  ") or line.startswith("\t")):
            if stripped.startswith("category:"):
                category = stripped.split(":", 1)[1].strip().strip("\"'")
            elif stripped.startswith("version:"):
                version = stripped.split(":", 1)[1].strip().strip("\"'")
        else:
            in_desc = False
            if not line.startswith(" ") and not line.startswith("\t"):
                in_meta = False

    description = " ".join(desc_lines).strip()
    return {
        "name": name,
        "description": description,
        "category": category,
        "version": version,
        "body": body,
    }


def discover_skills_inventory(
    home_dir: pathlib.Path,
    catalog_dir: Optional[pathlib.Path] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Scan all skill tiers on disk to compute Tier-1 routing token tax and Tier-2 body size:
    - builtin: ~/.gemini/antigravity/builtin/skills/*/SKILL.md
    - plugin: ~/.gemini/config/plugins/*/skills/*/SKILL.md
    - global: ~/.gemini/config/skills/*/SKILL.md and ~/.agents/skills/*/SKILL.md
    - workspace: .agents/skills/*/SKILL.md
    - catalog: catalog repository or ~/.cache/kungfu/index.json
    """
    inventory: Dict[str, Dict[str, Any]] = {}
    now_iso = utc_now_iso()

    def register_skill_md(
        md_path: pathlib.Path,
        source_tier: str,
        source_origin: str,
        always_in_prompt: int,
    ) -> None:
        if not md_path.is_file():
            return
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return
        fm = parse_skill_frontmatter(text)
        skill_name = fm["name"] or md_path.parent.name
        desc = fm["description"]
        body = fm["body"]
        tier1_chars = len(skill_name) + len(desc)
        tier1_tokens = max(1, int(round(tier1_chars / 4.0))) if tier1_chars > 0 else 0
        tier2_lines = len(body.splitlines())
        tier2_tokens = max(1, int(round(len(body) / 4.0))) if body else 0

        existing = inventory.get(skill_name)
        if existing and existing["is_always_in_prompt"] == 1 and always_in_prompt == 0:
            return

        inventory[skill_name] = {
            "skill_name": skill_name,
            "source_tier": source_tier,
            "source_origin": source_origin,
            "category": fm["category"] or source_tier,
            "version": fm["version"] or "unversioned",
            "description": desc,
            "skill_path": str(md_path),
            "is_always_in_prompt": always_in_prompt,
            "tier1_chars": tier1_chars,
            "tier1_tokens_est": tier1_tokens,
            "tier2_lines": tier2_lines,
            "tier2_tokens_est": tier2_tokens,
            "synced_at": now_iso,
        }

    # 1. Catalog repository skills (if present, e.g. ../skills/<category>/<skill>/SKILL.md)
    candidates = []
    if catalog_dir and catalog_dir.is_dir():
        candidates.append(catalog_dir)
    script_repo_root = pathlib.Path(__file__).resolve().parents[3]
    if (script_repo_root / "catalog.json").is_file():
        candidates.append(script_repo_root)

    for cat_root in candidates:
        for cat_name in ("agents", "analytics", "coding", "game-dev", "media", "writing"):
            cat_dir = cat_root / cat_name
            if cat_dir.is_dir():
                for skill_dir in sorted(cat_dir.iterdir()):
                    if skill_dir.is_dir():
                        register_skill_md(
                            skill_dir / "SKILL.md",
                            source_tier="catalog",
                            source_origin="danicat/skills",
                            always_in_prompt=0,
                        )

    # Also read ~/.cache/kungfu/index.json for cached catalog metadata
    cache_index = home_dir / ".cache" / "kungfu" / "index.json"
    if cache_index.is_file():
        try:
            idx_obj = json.loads(cache_index.read_text(encoding="utf-8"))
            manifest = idx_obj.get("manifest") or idx_obj
            items = manifest.get("skills") or manifest.get("items") or []
            for it in items:
                if not isinstance(it, dict):
                    continue
                sname = it.get("name") or it.get("id")
                if sname and sname not in inventory:
                    desc = it.get("description") or ""
                    t1_chars = len(sname) + len(desc)
                    inventory[sname] = {
                        "skill_name": sname,
                        "source_tier": "catalog",
                        "source_origin": manifest.get("name") or "catalog",
                        "category": it.get("category") or "catalog",
                        "version": it.get("version") or "unversioned",
                        "description": desc,
                        "skill_path": it.get("url") or "",
                        "is_always_in_prompt": 0,
                        "tier1_chars": t1_chars,
                        "tier1_tokens_est": max(1, int(round(t1_chars / 4.0))),
                        "tier2_lines": 0,
                        "tier2_tokens_est": 0,
                        "synced_at": now_iso,
                    }
        except Exception:
            pass

    # 2. Built-in Antigravity skills
    builtin_dir = home_dir / ".gemini" / "antigravity" / "builtin" / "skills"
    if builtin_dir.is_dir():
        for d in sorted(builtin_dir.iterdir()):
            if d.is_dir():
                register_skill_md(d / "SKILL.md", "builtin", "antigravity-builtin", 1)

    # 3. Plugin skills
    plugins_dir = home_dir / ".gemini" / "config" / "plugins"
    if plugins_dir.is_dir():
        for pdir in sorted(plugins_dir.iterdir()):
            skills_sub = pdir / "skills"
            if skills_sub.is_dir():
                for sdir in sorted(skills_sub.iterdir()):
                    if sdir.is_dir():
                        register_skill_md(sdir / "SKILL.md", "plugin", pdir.name, 1)

    # 4. Global skills (~/.agents/skills and ~/.gemini/config/skills)
    for gdir, origin in (
        (home_dir / ".agents" / "skills", "global-agents"),
        (home_dir / ".gemini" / "config" / "skills", "global-gemini"),
    ):
        if gdir.is_dir():
            for sdir in sorted(gdir.iterdir()):
                if sdir.is_dir():
                    register_skill_md(sdir / "SKILL.md", "global", origin, 1)

    # 5. Current Workspace skills (.agents/skills)
    ws_skills = pathlib.Path.cwd() / ".agents" / "skills"
    if ws_skills.is_dir():
        for sdir in sorted(ws_skills.iterdir()):
            if sdir.is_dir():
                register_skill_md(sdir / "SKILL.md", "workspace", "workspace", 1)

    return inventory


def read_state_snapshot(
    state_json_path: pathlib.Path,
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]], Set[str]]:
    """Read `~/.config/kungfu/state.json` if present."""
    if not state_json_path.is_file():
        return {}, {}, set()

    try:
        raw_state = json.loads(state_json_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail_fast(
            "Failed to parse state.json",
            context={"state_json_path": str(state_json_path), "error": str(exc)},
        )

    history = raw_state.get("history")
    if history is None:
        history = {}

    installed_set: Set[str] = set()
    global_skills = (raw_state.get("global") or {}).get("skills") or {}
    for s_name, meta in global_skills.items():
        if isinstance(meta, dict) and meta.get("status") == "installed":
            installed_set.add(s_name)

    workspaces = raw_state.get("workspaces") or {}
    for ws_meta in workspaces.values():
        if not isinstance(ws_meta, dict):
            continue
        ws_skills = ws_meta.get("skills") or {}
        for s_name, meta in ws_skills.items():
            if isinstance(meta, dict) and meta.get("status") == "installed":
                installed_set.add(s_name)

    return raw_state, history, installed_set


def read_summaries_metadata(summaries_db_path: pathlib.Path) -> Dict[str, Dict[str, Any]]:
    """Read conversation metadata from `conversation_summaries.db` if present."""
    if not summaries_db_path.is_file():
        return {}

    uri = f"file:{summaries_db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
                conversation_id,
                title,
                last_user_input_time,
                last_modified_time,
                workspace_uris,
                parent_conversation_id
            FROM conversation_summaries
            """
        ).fetchall()
    except Exception as exc:
        conn.close()
        fail_fast(
            "Failed querying conversation_summaries.db",
            context={"summaries_db_path": str(summaries_db_path), "error": str(exc)},
        )
    conn.close()

    result: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        result[r["conversation_id"]] = {
            "conversation_id": r["conversation_id"],
            "title": r["title"],
            "created_at": r["last_user_input_time"] or r["last_modified_time"],
            "updated_at": r["last_modified_time"],
            "workspace_uris": r["workspace_uris"],
            "git_origin_urls": r["parent_conversation_id"] or None,
        }
    return result


def compute_file_watermark(path: pathlib.Path) -> Tuple[int, int, str]:
    st = path.stat()
    h = hashlib.sha256()
    with path.open("rb") as f:
        h.update(f.read(65536))
    return st.st_size, st.st_mtime_ns, h.hexdigest()


def unwrap_json_string(val: Any) -> str:
    if val is None:
        return ""
    if not isinstance(val, str):
        return str(val)
    s = val.strip()
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        try:
            unwrapped = json.loads(s)
            if isinstance(unwrapped, str):
                return unwrapped
        except Exception:
            pass
    return val


def load_merged_steps(
    conv_id: str,
    compact_path: pathlib.Path,
    full_path: pathlib.Path,
) -> List[Dict[str, Any]]:
    """Merge `transcript.jsonl` with `transcript_full.jsonl` on `truncated_fields`."""
    steps_by_idx: Dict[int, Dict[str, Any]] = {}
    needs_full_indices: Set[int] = set()
    had_torn_compact_line = False

    if compact_path.is_file():
        with compact_path.open("r", encoding="utf-8", errors="replace") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    had_torn_compact_line = True
                    continue
                idx = obj.get("step_index")
                if not isinstance(idx, int):
                    had_torn_compact_line = True
                    continue
                steps_by_idx[idx] = obj
                trunc = obj.get("truncated_fields")
                if trunc and ("content" in trunc or "tool_calls" in trunc):
                    needs_full_indices.add(idx)

    if full_path.is_file() and (needs_full_indices or had_torn_compact_line or not steps_by_idx):
        with full_path.open("r", encoding="utf-8", errors="replace") as f:
            for line_no, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    fail_fast(
                        "Corrupted JSON line in transcript_full.jsonl",
                        context={
                            "conversation_id": conv_id,
                            "full_path": str(full_path),
                            "line_no": line_no,
                            "error": str(exc),
                        },
                    )
                idx = obj.get("step_index")
                if not isinstance(idx, int):
                    continue
                if idx in needs_full_indices or idx not in steps_by_idx or had_torn_compact_line:
                    steps_by_idx[idx] = obj

    return [steps_by_idx[k] for k in sorted(steps_by_idx.keys())]


def strip_non_user_prose(raw_text: str) -> str:
    text = raw_text
    if "<USER_REQUEST>" in text and "</USER_REQUEST>" in text:
        blocks = re.findall(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, flags=re.DOTALL)
        text = "\n".join(blocks)
    else:
        text = SYSTEM_TAG_RE.sub(" ", text)

    text = FENCED_CODE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)

    cleaned_lines: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("|") and s.endswith("|"):
            continue
        if s.startswith((">", "#")):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def classify_modern_colon_token(
    raw_token: str,
    paren_arg: Optional[str],
    known_skills: Set[str],
) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    body = raw_token[2:]
    if not body:
        return None

    if body in {"@", "@^"} or body.startswith("@^"):
        cat_arg = body[2:] if body.startswith("@^") and len(body) > 2 else None
        return ("catalog", None, cat_arg or body)

    if body in {"^", "^_^"}:
        return ("update", None, body)

    prefix = ""
    for p in ("++*", "+*", "++", "+", "--", "-", "*", ">", ":"):
        if body.startswith(p):
            prefix = p
            body = body[len(p) :]
            break

    if not body:
        return None

    if body in COLON_FALSE_POSITIVES or body.lower() in COLON_FALSE_POSITIVES:
        return None
    if body in DOC_PLACEHOLDER_TARGETS or body.lower() in DOC_PLACEHOLDER_TARGETS:
        return None

    subcommand = "load"
    if prefix in {"++*", "+*", "++", "+"}:
        subcommand = "learn"
    elif prefix in {"--", "-"}:
        subcommand = "forget"
    elif prefix == ">":
        subcommand = "show"

    subpath_or_script: Optional[str] = None
    if "!" in body:
        skill_part, script_part = body.split("!", 1)
        subcommand = "run"
        subpath_or_script = script_part
    elif "/" in body:
        skill_part, subpath_part = body.split("/", 1)
        subpath_or_script = subpath_part
    elif "@" in body:
        skill_part, cat_part = body.split("@", 1)
        subpath_or_script = f"@{cat_part}"
    elif ":" in body:
        skill_part, cat_part = body.split(":", 1)
        subpath_or_script = f":{cat_part}"
    else:
        skill_part = body

    if paren_arg and not subpath_or_script:
        subpath_or_script = f"({paren_arg})"

    skill_clean = skill_part.strip().lower()
    if not re.match(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$", skill_clean):
        return None

    if not prefix and "/" not in raw_token and "!" not in raw_token and "@" not in raw_token and not paren_arg:
        if skill_clean not in known_skills:
            return None

    return (subcommand, skill_clean, subpath_or_script)


def extract_user_notations(
    conv_id: str,
    step_index: int,
    step_created_at: Optional[str],
    step_type: str,
    raw_content: str,
    known_skills: Set[str],
) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """Extract user prompt notations (`::skill`, `//skill`, `:?`, `/skill`) and return explicitly named skills."""
    events: List[Dict[str, Any]] = []
    explicit_skills: Set[str] = set()
    if not raw_content:
        return events, explicit_skills

    cleaned = strip_non_user_prose(raw_content)
    if not cleaned.strip():
        return events, explicit_skills

    for line in cleaned.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue

        for m in MODERN_FIND_RE.finditer(line):
            prefix_tok = m.group(1)
            query_str = m.group(2).strip()
            if not query_str or query_str.startswith(("=", ")", "]", ":", "/")):
                continue
            first_word = query_str.split()[0].lower().rstrip(".,;!?")
            if first_word in DOC_PLACEHOLDER_TARGETS:
                continue
            snippet = f"{prefix_tok}{query_str}"[:200]
            events.append(
                {
                    "conversation_id": conv_id,
                    "step_index": step_index,
                    "step_created_at": step_created_at,
                    "step_type": step_type,
                    "invocation_kind": "user_notation",
                    "notation_type": "find_:?",
                    "subcommand": "find",
                    "target_skill": first_word if first_word in known_skills else None,
                    "raw_args": query_str,
                    "subpath_or_script": query_str,
                    "page_number": 1,
                    "trigger_mode": "user_explicit",
                    "source_tier": "user_prompt",
                    "raw_snippet": snippet,
                    "is_self_test": 0,
                }
            )

        for m in CLASSIC_SLASH_RE.finditer(line):
            candidate = m.group(1).lower()
            if candidate not in known_skills or candidate in DOC_PLACEHOLDER_TARGETS:
                continue
            start_pos = m.start()
            preceding = line[max(0, start_pos - 12) : start_pos].lower()
            if preceding.endswith(("http:", "https:", "file:", "sidecar:", "ws:", "wss:")):
                continue
            explicit_skills.add(candidate)
            events.append(
                {
                    "conversation_id": conv_id,
                    "step_index": step_index,
                    "step_created_at": step_created_at,
                    "step_type": step_type,
                    "invocation_kind": "user_notation",
                    "notation_type": "classic_//",
                    "subcommand": "load",
                    "target_skill": candidate,
                    "raw_args": f"//{candidate}",
                    "subpath_or_script": None,
                    "page_number": 1,
                    "trigger_mode": "user_explicit",
                    "source_tier": "user_prompt",
                    "raw_snippet": line_stripped[:240],
                    "is_self_test": 0,
                }
            )

        for m in SINGLE_SLASH_RE.finditer(line):
            candidate = m.group(1).lower()
            if candidate in known_skills and candidate not in DOC_PLACEHOLDER_TARGETS:
                explicit_skills.add(candidate)

        for m in MODERN_COLON_RE.finditer(line):
            raw_tok = m.group(1)
            paren_arg = m.group(2)
            start_pos = m.start(1)
            if start_pos > 0 and line[start_pos - 1] not in (" ", "\t", "(", "[", "\"", "'"):
                continue
            classified = classify_modern_colon_token(raw_tok, paren_arg, known_skills)
            if not classified:
                continue
            subcmd, target_skill, subpath_or_script = classified
            if target_skill:
                explicit_skills.add(target_skill)
            full_tok = f"{raw_tok}({paren_arg})" if paren_arg else raw_tok
            events.append(
                {
                    "conversation_id": conv_id,
                    "step_index": step_index,
                    "step_created_at": step_created_at,
                    "step_type": step_type,
                    "invocation_kind": "user_notation",
                    "notation_type": "modern_::",
                    "subcommand": subcmd,
                    "target_skill": target_skill,
                    "raw_args": full_tok,
                    "subpath_or_script": subpath_or_script,
                    "page_number": 1,
                    "trigger_mode": "user_explicit",
                    "source_tier": "user_prompt",
                    "raw_snippet": line_stripped[:240],
                    "is_self_test": 0,
                }
            )

    return events, explicit_skills


def split_shell_segments(command_line: str) -> List[str]:
    norm = command_line.replace("\\\n", " ")
    parts = re.split(r"(?:&&|\|\||;|\n)", norm)
    return [p.strip() for p in parts if p.strip()]


def tokenize_segment(seg: str) -> List[str]:
    cleaned = re.sub(r"\s+\d*>&\d+|\s*>\s*[^\s]+|\s*<\s*[^\s]+", " ", seg)
    if "|" in cleaned:
        cleaned = cleaned.split("|", 1)[0].strip()
    return [t.strip("\"'`") for t in cleaned.split() if t.strip("\"'`")]


def parse_kungfu_cli_segment(
    seg: str,
    conv_id: str,
    step_index: int,
    step_created_at: Optional[str],
    step_type: str,
    known_skills: Set[str],
    explicit_skills_in_conv: Set[str],
) -> Optional[Dict[str, Any]]:
    raw_seg = seg.strip()
    if not raw_seg:
        return None
    if re.match(r"^(echo|printf|cat|grep|rg|sed|awk|git|python|python3|sqlite3)\b", raw_seg):
        return None

    tokens = tokenize_segment(raw_seg)
    if not tokens:
        return None

    idx = 0
    has_env_override = False
    while idx < len(tokens) and "=" in tokens[idx] and not tokens[idx].startswith("-"):
        if tokens[idx].startswith(("KUNGFU_STATE_PATH=", "KUNGFU_CONFIG_DIR=", "HOME=")):
            has_env_override = True
        idx += 1

    if idx >= len(tokens):
        return None

    is_dev_binary = has_env_override
    sub_idx = -1

    if (
        idx + 2 < len(tokens)
        and tokens[idx] == "go"
        and tokens[idx + 1] == "run"
        and (tokens[idx + 2] in {".", "./main.go", "main.go"} or tokens[idx + 2].endswith("/kungfu"))
    ):
        is_dev_binary = True
        sub_idx = idx + 3
    else:
        bin_tok = tokens[idx]
        if bin_tok in {"kungfu", "./kungfu", "bin/kungfu", "./bin/kungfu"} or bin_tok.endswith("/kungfu"):
            if bin_tok.startswith("./") or bin_tok.startswith("/tmp/"):
                is_dev_binary = True
            sub_idx = idx + 1
        else:
            return None

    if sub_idx >= len(tokens):
        return None

    raw_sub = tokens[sub_idx]
    rest = tokens[sub_idx + 1 :]

    if raw_sub in {"--version", "-v", "version"}:
        subcommand = "version"
    elif raw_sub in {"--help", "-h", "help"}:
        subcommand = "help"
    elif raw_sub in KNOWN_SUBCOMMANDS:
        subcommand = "find" if raw_sub == "search" else ("forget" if raw_sub == "unlearn" else raw_sub)
    else:
        return None

    target_skill: Optional[str] = None
    subpath_or_script: Optional[str] = None
    page_number = 1
    raw_args = " ".join([raw_sub] + rest) if rest else raw_sub
    is_self_test = 1 if is_dev_binary else 0

    if subcommand == "load":
        positionals: List[str] = []
        j = 0
        while j < len(rest):
            arg = rest[j]
            if arg in {"-p", "--page"}:
                if j + 1 < len(rest):
                    try:
                        page_number = int(rest[j + 1])
                    except ValueError:
                        page_number = 1
                    j += 2
                    continue
                j += 1
                continue
            if arg.startswith("--page=") or arg.startswith("-p="):
                try:
                    page_number = int(arg.split("=", 1)[1])
                except ValueError:
                    page_number = 1
                j += 1
                continue
            if arg in {"-s", "--search", "-c", "--category", "-t", "--tags", "--page-size"}:
                j += 2
                continue
            if arg.startswith(("--search=", "-s=", "--category=", "-c=", "--tags=", "-t=", "--page-size=")):
                j += 1
                continue
            if arg.startswith("-"):
                j += 1
                continue
            positionals.append(arg)
            j += 1

        if len(positionals) == 1:
            spec = positionals[0]
            if "/" in spec:
                parts = spec.split("/", 1)
                target_skill = parts[0]
                subpath_or_script = parts[1]
            else:
                target_skill = spec.split("@", 1)[0]
            if target_skill not in known_skills:
                is_self_test = 1
        elif len(positionals) > 1:
            base_skills = [p.split("/", 1)[0].split("@", 1)[0] for p in positionals]
            target_skill = ",".join(base_skills)
            subpath_or_script = "MULTI_SKILL_BATCH_REJECTED_V050"

    elif subcommand == "run":
        if rest and rest[0] in {"--help", "-h"}:
            subpath_or_script = "--help"
        else:
            positionals = [arg for arg in rest if not arg.startswith("-")]
            if positionals:
                first = positionals[0]
                if "/" in first:
                    parts = first.split("/", 1)
                    target_skill = parts[0]
                    subpath_or_script = parts[1]
                else:
                    target_skill = first
                    if len(positionals) >= 2:
                        subpath_or_script = positionals[1]

    elif subcommand in {"learn", "add", "forget", "update"}:
        positionals = [a for a in rest if not a.startswith("-")]
        if positionals:
            target_skill = positionals[0].split("@", 1)[0]
        if "--load" in rest or "-l" in rest:
            subpath_or_script = "--load"

    elif subcommand == "find":
        positionals = []
        j = 0
        while j < len(rest):
            arg = rest[j]
            if arg in {"-c", "--category", "-t", "--tags", "-s", "--strategy", "--limit"}:
                j += 2
                continue
            if arg.startswith("-"):
                j += 1
                continue
            positionals.append(arg)
            j += 1
        if positionals:
            query_str = " ".join(positionals)
            subpath_or_script = query_str
            if len(positionals) == 1 and positionals[0] in known_skills:
                target_skill = positionals[0]

    elif subcommand == "show":
        positionals = []
        j = 0
        while j < len(rest):
            arg = rest[j]
            if arg in {"-c", "--category", "-t", "--tags"}:
                if j + 1 < len(rest):
                    subpath_or_script = f"{arg} {rest[j + 1]}"
                j += 2
                continue
            if arg.startswith("-"):
                j += 1
                continue
            positionals.append(arg)
            j += 1
        if len(positionals) == 1:
            target_skill = positionals[0]
        elif len(positionals) > 1:
            target_skill = ",".join(positionals)
            subpath_or_script = "MULTI_SKILL_SHOW"

    elif subcommand == "catalog":
        positionals = [a for a in rest if not a.startswith("-")]
        if positionals:
            subpath_or_script = " ".join(positionals)

    snippet = re.sub(r"\s+", " ", raw_seg).strip()
    if len(snippet) > 400:
        snippet = snippet[:397] + "..."

    trigger_mode = "autonomous"
    if target_skill == "kungfu":
        trigger_mode = "rule_driven"
    elif target_skill and target_skill in explicit_skills_in_conv:
        trigger_mode = "user_explicit"

    return {
        "conversation_id": conv_id,
        "step_index": step_index,
        "step_created_at": step_created_at,
        "step_type": step_type,
        "invocation_kind": "cli_invocation",
        "notation_type": None,
        "subcommand": subcommand,
        "target_skill": target_skill,
        "raw_args": raw_args,
        "subpath_or_script": subpath_or_script,
        "page_number": page_number,
        "trigger_mode": trigger_mode,
        "source_tier": "kungfu_cli",
        "raw_snippet": snippet,
        "is_self_test": is_self_test,
    }


def classify_skill_path_tier(norm_path: str) -> Tuple[str, int]:
    """Return (source_tier, is_self_test) for a SKILL.md or resource file path."""
    if "/.gemini/antigravity/builtin/skills/" in norm_path:
        return ("builtin", 0)
    if "/.gemini/config/plugins/" in norm_path:
        return ("plugin", 0)
    if "/.gemini/config/skills/" in norm_path or "/.agents/skills/" in norm_path:
        return ("global", 0)
    if "/.agents/skills/" in norm_path:
        return ("workspace", 0)
    if "/projects/kungfu/skills/kungfu/SKILL.md" in norm_path:
        return ("repo_authoring", 1)
    return ("repo_authoring", 1)


def extract_planner_invocations(
    conv_id: str,
    step_index: int,
    step_created_at: Optional[str],
    step_type: str,
    tool_calls: List[Dict[str, Any]],
    known_skills: Set[str],
    explicit_skills_in_conv: Set[str],
) -> List[Dict[str, Any]]:
    """
    Extract all skill events from PLANNER_RESPONSE tool_calls:
    1. `direct_skill_view` (`view_file` on any `*/<skill>/SKILL.md`)
    2. `skill_resource_view` (`view_file` on any `*/<skill>/(references|scripts|assets|examples)/*`)
    3. `cli_invocation` (`kungfu <subcmd>` or direct execution of `*/<skill>/scripts/*`)
    """
    events: List[Dict[str, Any]] = []
    if not isinstance(tool_calls, list):
        return events

    for tc in tool_calls:
        if not isinstance(tc, dict):
            continue
        name = tc.get("name") or ""
        args = tc.get("args") or tc.get("arguments") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        if not isinstance(args, dict):
            continue

        # 1. File views (`SKILL.md` or companion resource)
        if name in {"view_file", "default_api:view_file", "view_file_outline", "default_api:view_file_outline"}:
            abs_path = unwrap_json_string(args.get("AbsolutePath") or args.get("FilePath") or "")
            norm_path = abs_path.replace("\\", "/")

            m_skill = SKILL_MD_PATH_RE.search(norm_path)
            if m_skill:
                skill_name = m_skill.group(1)
                source_tier, is_self_test = classify_skill_path_tier(norm_path)
                if skill_name in known_skills or source_tier in {"builtin", "plugin", "global", "workspace"}:
                    trigger_mode = "autonomous"
                    if skill_name == "kungfu":
                        trigger_mode = "rule_driven"
                    elif skill_name in explicit_skills_in_conv:
                        trigger_mode = "user_explicit"
                    events.append(
                        {
                            "conversation_id": conv_id,
                            "step_index": step_index,
                            "step_created_at": step_created_at,
                            "step_type": step_type,
                            "invocation_kind": "direct_skill_view",
                            "notation_type": None,
                            "subcommand": "view_file",
                            "target_skill": skill_name,
                            "raw_args": norm_path,
                            "subpath_or_script": "SKILL.md",
                            "page_number": 1,
                            "trigger_mode": trigger_mode,
                            "source_tier": source_tier,
                            "raw_snippet": f"{name}({norm_path})",
                            "is_self_test": is_self_test,
                        }
                    )
                continue

            m_res = SKILL_RESOURCE_PATH_RE.search(norm_path)
            if m_res:
                skill_name, res_folder, res_rel = m_res.group(1), m_res.group(2), m_res.group(3)
                source_tier, is_self_test = classify_skill_path_tier(norm_path)
                if skill_name in known_skills:
                    events.append(
                        {
                            "conversation_id": conv_id,
                            "step_index": step_index,
                            "step_created_at": step_created_at,
                            "step_type": step_type,
                            "invocation_kind": "skill_resource_view",
                            "notation_type": None,
                            "subcommand": f"view_{res_folder}",
                            "target_skill": skill_name,
                            "raw_args": norm_path,
                            "subpath_or_script": f"{res_folder}/{res_rel}",
                            "page_number": 1,
                            "trigger_mode": "autonomous",
                            "source_tier": source_tier,
                            "raw_snippet": f"{name}({norm_path})",
                            "is_self_test": is_self_test,
                        }
                    )

        # 2. CLI command executions (`kungfu ...` or direct skill script execution)
        if name in {"run_command", "default_api:run_command"}:
            cmd_line = unwrap_json_string(args.get("CommandLine") or args.get("command") or "")
            if not cmd_line:
                continue

            if "kungfu" in cmd_line or "go run" in cmd_line:
                for seg in split_shell_segments(cmd_line):
                    if "kungfu" not in seg and "go run" not in seg:
                        continue
                    parsed = parse_kungfu_cli_segment(
                        seg=seg,
                        conv_id=conv_id,
                        step_index=step_index,
                        step_created_at=step_created_at,
                        step_type=step_type,
                        known_skills=known_skills,
                        explicit_skills_in_conv=explicit_skills_in_conv,
                    )
                    if parsed:
                        events.append(parsed)

            if "/scripts/" in cmd_line:
                for m_exec in DIRECT_SCRIPT_EXEC_RE.finditer(cmd_line):
                    full_script_path, skill_name, script_file = (
                        m_exec.group(1),
                        m_exec.group(2),
                        m_exec.group(3),
                    )
                    if skill_name in known_skills and not script_file.startswith("test_"):
                        events.append(
                            {
                                "conversation_id": conv_id,
                                "step_index": step_index,
                                "step_created_at": step_created_at,
                                "step_type": step_type,
                                "invocation_kind": "cli_invocation",
                                "notation_type": None,
                                "subcommand": "script_exec",
                                "target_skill": skill_name,
                                "raw_args": full_script_path,
                                "subpath_or_script": script_file,
                                "page_number": 1,
                                "trigger_mode": "autonomous",
                                "source_tier": "direct_script",
                                "raw_snippet": cmd_line.strip()[:240],
                                "is_self_test": 0,
                            }
                        )

    return events


def init_db(conn: sqlite3.Connection, rebuild: bool = False) -> None:
    row = conn.execute(
        "SELECT type FROM sqlite_master WHERE name = 'kungfu_invocations'"
    ).fetchone()
    if row and row[0] == "table":
        conn.execute("DROP TABLE IF EXISTS kungfu_invocations")

    if rebuild:
        conn.executescript(
            """
            DROP VIEW IF EXISTS v_skill_telemetry_drift;
            DROP VIEW IF EXISTS v_search_gaps;
            DROP VIEW IF EXISTS v_trigger_attribution;
            DROP VIEW IF EXISTS v_skill_roi;
            DROP VIEW IF EXISTS v_subcommand_summary;
            DROP VIEW IF EXISTS v_daily_invocations;
            DROP VIEW IF EXISTS kungfu_invocations;
            DROP TABLE IF EXISTS skill_events;
            DROP TABLE IF EXISTS skills_inventory;
            DROP TABLE IF EXISTS ingestion_state;
            DROP TABLE IF EXISTS conversations;
            DROP TABLE IF EXISTS state_telemetry_snapshot;
            """
        )
    conn.executescript(SCHEMA_DDL)
    conn.commit()


def sync_skills_inventory_table(
    conn: sqlite3.Connection,
    inventory: Dict[str, Dict[str, Any]],
) -> None:
    conn.execute("DELETE FROM skills_inventory")
    for s in sorted(inventory.values(), key=lambda x: x["skill_name"]):
        conn.execute(
            """
            INSERT INTO skills_inventory (
                skill_name, source_tier, source_origin, category, version,
                description, skill_path, is_always_in_prompt,
                tier1_chars, tier1_tokens_est, tier2_lines, tier2_tokens_est, synced_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                s["skill_name"],
                s["source_tier"],
                s["source_origin"],
                s["category"],
                s["version"],
                s["description"],
                s["skill_path"],
                s["is_always_in_prompt"],
                s["tier1_chars"],
                s["tier1_tokens_est"],
                s["tier2_lines"],
                s["tier2_tokens_est"],
                s["synced_at"],
            ),
        )
    conn.commit()


def sync_state_snapshot_table(
    conn: sqlite3.Connection,
    state_json_path: pathlib.Path,
) -> None:
    _, history, installed_set = read_state_snapshot(state_json_path)
    now_iso = utc_now_iso()

    conn.execute("DELETE FROM state_telemetry_snapshot")
    all_state_skills = set(history.keys()) | installed_set
    for skill in sorted(all_state_skills):
        entry = history.get(skill) or {}
        count = int(entry.get("load_count", entry.get("count", 0)))
        page_cnt = int(entry.get("page_load_count", 0))
        sub_cnt = int(entry.get("subpath_load_count", 0))
        run_cnt = int(entry.get("run_count", 0))
        last_loaded = str(entry.get("last_seen_at", entry.get("last_loaded", "")))
        is_learned = 1 if skill in installed_set else 0
        conn.execute(
            """
            INSERT INTO state_telemetry_snapshot (
                skill_name, recorded_count, page_load_count, subpath_load_count,
                run_count, last_loaded_at, is_learned, snapshot_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (skill, count, page_cnt, sub_cnt, run_cnt, last_loaded, is_learned, now_iso),
        )
    conn.commit()


def ingest_conversations(
    conn: sqlite3.Connection,
    brain_dir: pathlib.Path,
    summaries_db_path: pathlib.Path,
    state_json_path: pathlib.Path,
    catalog_dir: Optional[pathlib.Path] = None,
    rebuild: bool = False,
) -> Dict[str, int]:
    if not brain_dir.is_dir():
        fail_fast("Antigravity brain directory does not exist", context={"brain_dir": str(brain_dir)})

    inventory = discover_skills_inventory(HOME_DIR, catalog_dir)
    sync_skills_inventory_table(conn, inventory)
    sync_state_snapshot_table(conn, state_json_path)

    known_skills = set(BUILTIN_KNOWN_SKILLS) | set(inventory.keys())
    _, state_hist, state_inst = read_state_snapshot(state_json_path)
    known_skills |= set(state_hist.keys()) | state_inst

    summaries_meta = read_summaries_metadata(summaries_db_path)

    brain_conv_dirs: Dict[str, pathlib.Path] = {}
    for entry in sorted(brain_dir.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            brain_conv_dirs[entry.name] = entry

    all_conv_ids = sorted(set(summaries_meta.keys()) | set(brain_conv_dirs.keys()))

    existing_watermarks: Dict[str, sqlite3.Row] = {}
    if not rebuild:
        conn.row_factory = sqlite3.Row
        for r in conn.execute("SELECT * FROM ingestion_state").fetchall():
            existing_watermarks[r["conversation_id"]] = r

    stats = {
        "total_union_conversations": len(all_conv_ids),
        "conversations_with_transcript": 0,
        "conversations_parsed": 0,
        "conversations_skipped_unchanged": 0,
        "steps_scanned": 0,
        "invocations_inserted": 0,
    }

    now_iso = utc_now_iso()

    for conv_id in all_conv_ids:
        s_meta = summaries_meta.get(conv_id, {})
        c_dir = brain_conv_dirs.get(conv_id)
        compact_path = (
            c_dir / ".system_generated" / "logs" / "transcript.jsonl"
            if c_dir is not None
            else pathlib.Path("/nonexistent")
        )
        full_path = (
            c_dir / ".system_generated" / "logs" / "transcript_full.jsonl"
            if c_dir is not None
            else pathlib.Path("/nonexistent")
        )

        has_transcript = 1 if (compact_path.is_file() or full_path.is_file()) else 0
        has_summary_db = 1 if conv_id in summaries_meta else 0

        if not has_transcript:
            conn.execute(
                """
                INSERT INTO conversations (
                    conversation_id, title, workspace_uris, git_origin_urls,
                    created_at, updated_at, first_step_at, last_step_at,
                    total_steps, user_input_steps, planner_steps,
                    has_transcript, has_summary_db, ingested_at
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, 0, 0, 0, 0, ?, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    title = excluded.title,
                    workspace_uris = excluded.workspace_uris,
                    git_origin_urls = excluded.git_origin_urls,
                    created_at = excluded.created_at,
                    updated_at = excluded.updated_at,
                    has_summary_db = excluded.has_summary_db,
                    ingested_at = excluded.ingested_at
                """,
                (
                    conv_id,
                    s_meta.get("title"),
                    s_meta.get("workspace_uris"),
                    s_meta.get("git_origin_urls"),
                    s_meta.get("created_at"),
                    s_meta.get("updated_at"),
                    has_summary_db,
                    now_iso,
                ),
            )
            continue

        stats["conversations_with_transcript"] += 1
        primary_path = compact_path if compact_path.is_file() else full_path
        c_size, c_mtime, c_hash = compute_file_watermark(primary_path)
        f_size = full_path.stat().st_size if full_path.is_file() else 0
        f_mtime = full_path.stat().st_mtime_ns if full_path.is_file() else 0
        combined_size = c_size + f_size
        combined_mtime = max(c_mtime, f_mtime)

        prev = existing_watermarks.get(conv_id)
        if (
            prev is not None
            and prev["file_size_bytes"] == combined_size
            and prev["file_mtime_ns"] == combined_mtime
            and prev["sha256_head"] == c_hash
        ):
            stats["conversations_skipped_unchanged"] += 1
            continue

        steps = load_merged_steps(conv_id, compact_path, full_path)
        stats["conversations_parsed"] += 1
        stats["steps_scanned"] += len(steps)

        conn.execute("DELETE FROM skill_events WHERE conversation_id = ?", (conv_id,))

        first_step_at: Optional[str] = None
        last_step_at: Optional[str] = None
        user_steps = 0
        planner_steps = 0
        last_step_index = -1
        explicit_skills_in_conv: Set[str] = set()

        for step in steps:
            s_idx = step.get("step_index", -1)
            if isinstance(s_idx, int) and s_idx > last_step_index:
                last_step_index = s_idx

            s_type = step.get("type") or "UNKNOWN"
            s_created = step.get("created_at")
            if isinstance(s_created, str) and s_created:
                if first_step_at is None or s_created < first_step_at:
                    first_step_at = s_created
                if last_step_at is None or s_created > last_step_at:
                    last_step_at = s_created

            extracted: List[Dict[str, Any]] = []
            if s_type == "USER_INPUT":
                user_steps += 1
                content = step.get("content") or ""
                if isinstance(content, str) and content:
                    extracted, new_explicit = extract_user_notations(
                        conv_id=conv_id,
                        step_index=s_idx,
                        step_created_at=s_created,
                        step_type=s_type,
                        raw_content=content,
                        known_skills=known_skills,
                    )
                    explicit_skills_in_conv |= new_explicit
            elif s_type == "PLANNER_RESPONSE":
                planner_steps += 1
                tcs = step.get("tool_calls") or []
                if isinstance(tcs, list) and tcs:
                    extracted = extract_planner_invocations(
                        conv_id=conv_id,
                        step_index=s_idx,
                        step_created_at=s_created,
                        step_type=s_type,
                        tool_calls=tcs,
                        known_skills=known_skills,
                        explicit_skills_in_conv=explicit_skills_in_conv,
                    )

            for ev in extracted:
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO skill_events (
                        conversation_id, step_index, step_created_at, step_type,
                        invocation_kind, notation_type, subcommand, target_skill,
                        raw_args, subpath_or_script, page_number, trigger_mode,
                        source_tier, raw_snippet, is_self_test
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ev["conversation_id"],
                        ev["step_index"],
                        ev["step_created_at"],
                        ev["step_type"],
                        ev["invocation_kind"],
                        ev["notation_type"],
                        ev["subcommand"],
                        ev["target_skill"],
                        ev["raw_args"],
                        ev["subpath_or_script"],
                        ev["page_number"],
                        ev["trigger_mode"],
                        ev["source_tier"],
                        ev["raw_snippet"],
                        ev["is_self_test"],
                    ),
                )
                if cur.rowcount > 0:
                    stats["invocations_inserted"] += 1

        conn.execute(
            """
            INSERT INTO conversations (
                conversation_id, title, workspace_uris, git_origin_urls,
                created_at, updated_at, first_step_at, last_step_at,
                total_steps, user_input_steps, planner_steps,
                has_transcript, has_summary_db, ingested_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(conversation_id) DO UPDATE SET
                title = excluded.title,
                workspace_uris = excluded.workspace_uris,
                git_origin_urls = excluded.git_origin_urls,
                created_at = excluded.created_at,
                updated_at = excluded.updated_at,
                first_step_at = excluded.first_step_at,
                last_step_at = excluded.last_step_at,
                total_steps = excluded.total_steps,
                user_input_steps = excluded.user_input_steps,
                planner_steps = excluded.planner_steps,
                has_transcript = 1,
                has_summary_db = excluded.has_summary_db,
                ingested_at = excluded.ingested_at
            """,
            (
                conv_id,
                s_meta.get("title"),
                s_meta.get("workspace_uris"),
                s_meta.get("git_origin_urls"),
                s_meta.get("created_at") or first_step_at,
                s_meta.get("updated_at") or last_step_at,
                first_step_at,
                last_step_at,
                len(steps),
                user_steps,
                planner_steps,
                has_summary_db,
                now_iso,
            ),
        )

        conn.execute(
            """
            INSERT INTO ingestion_state (
                conversation_id, transcript_path, file_size_bytes,
                file_mtime_ns, last_step_index, sha256_head, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(conversation_id) DO UPDATE SET
                transcript_path = excluded.transcript_path,
                file_size_bytes = excluded.file_size_bytes,
                file_mtime_ns = excluded.file_mtime_ns,
                last_step_index = excluded.last_step_index,
                sha256_head = excluded.sha256_head,
                updated_at = excluded.updated_at
            """,
            (
                conv_id,
                str(primary_path),
                combined_size,
                combined_mtime,
                last_step_index,
                c_hash,
                now_iso,
            ),
        )

    conn.commit()
    return stats


def compute_backfill_plan(
    conn: sqlite3.Connection,
    state_json_path: pathlib.Path,
) -> Dict[str, Any]:
    conn.row_factory = sqlite3.Row
    raw_state, history, _ = read_state_snapshot(state_json_path)

    drift_rows = conn.execute("SELECT * FROM v_skill_telemetry_drift").fetchall()
    detail_rows = conn.execute(
        """
        SELECT
            target_skill AS skill_name,
            SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'load' AND is_self_test = 0 AND page_number > 1 AND subpath_or_script IS NULL THEN 1 ELSE 0 END) AS page_loads,
            SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'load' AND is_self_test = 0 AND subpath_or_script IS NOT NULL AND subpath_or_script != 'MULTI_SKILL_BATCH_REJECTED_V050' THEN 1 ELSE 0 END) AS subpath_loads,
            SUM(CASE WHEN invocation_kind = 'cli_invocation' AND subcommand = 'run' AND is_self_test = 0 THEN 1 ELSE 0 END) AS run_count
        FROM skill_events
        WHERE target_skill IS NOT NULL AND instr(target_skill, ',') = 0
        GROUP BY target_skill
        """
    ).fetchall()
    details_by_skill = {r["skill_name"]: dict(r) for r in detail_rows}

    new_history: Dict[str, Dict[str, Any]] = {}
    changes: List[Dict[str, Any]] = []

    for r in drift_rows:
        skill = r["skill_name"]
        old_count = int(r["state_json_count"] or 0)
        old_last = r["state_json_last_loaded"] or ""
        tx_activations = int(r["transcript_total_activations"] or 0)
        tx_cli_primary = int(r["transcript_cli_load_primary"] or 0)
        tx_last = r["transcript_last_activated"] or ""
        det = details_by_skill.get(skill) or {}
        page_loads = int(det.get("page_loads") or 0)
        subpath_loads = int(det.get("subpath_loads") or 0)
        run_cnt = int(det.get("run_count") or 0)

        if skill in UNIT_TEST_POLLUTED_SKILLS and tx_activations == 0:
            changes.append(
                {
                    "skill": skill,
                    "action": "remove_unit_test_pollution",
                    "old_count": old_count,
                    "new_count": 0,
                    "old_last_loaded": old_last,
                    "new_last_loaded": None,
                }
            )
            continue

        reconciled_count = max(old_count, tx_activations)
        if skill == "godoctor" and tx_activations > 0:
            reconciled_count = tx_activations

        reconciled_last = max(old_last, tx_last) if (old_last and tx_last) else (tx_last or old_last)

        if reconciled_count > 0 and reconciled_last:
            rec: Dict[str, Any] = {
                "last_seen_at": reconciled_last,
                "load_count": reconciled_count,
            }
            if page_loads > 0:
                rec["page_load_count"] = page_loads
            if subpath_loads > 0:
                rec["subpath_load_count"] = subpath_loads
            if run_cnt > 0:
                rec["run_count"] = run_cnt
            new_history[skill] = rec
            if (
                reconciled_count != old_count
                or reconciled_last != old_last
                or page_loads > 0
                or subpath_loads > 0
                or run_cnt > 0
            ):
                changes.append(
                    {
                        "skill": skill,
                        "action": "update" if old_count > 0 else "insert_missing_post_v050",
                        "old_count": old_count,
                        "new_count": reconciled_count,
                        "page_load_count": page_loads,
                        "subpath_load_count": subpath_loads,
                        "run_count": run_cnt,
                        "transcript_cli_primary": tx_cli_primary,
                        "transcript_total_activations": tx_activations,
                        "old_last_loaded": old_last or None,
                        "new_last_loaded": reconciled_last,
                    }
                )

    sorted_history = {k: new_history[k] for k in sorted(new_history.keys())}
    new_state_payload = dict(raw_state)
    new_state_payload["updated_at"] = utc_now_iso()
    new_state_payload["history"] = sorted_history

    return {
        "state_json_path": str(state_json_path),
        "old_skill_count": len(history),
        "new_skill_count": len(sorted_history),
        "old_total_loads": sum(
            int(v.get("load_count", v.get("count", 0))) for v in history.values()
        ),
        "new_total_loads": sum(
            int(v.get("load_count", 0)) for v in sorted_history.values()
        ),
        "changes": changes,
        "new_state": new_state_payload,
    }


def apply_backfill_state(state_json_path: pathlib.Path, new_state: Dict[str, Any]) -> None:
    state_json_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state_json_path.with_suffix(".json.tmp")
    serialized = json.dumps(new_state, indent=2) + "\n"
    tmp_path.write_text(serialized, encoding="utf-8")
    os.replace(tmp_path, state_json_path)


def run_report(conn: sqlite3.Connection, report_type: str, as_json: bool = False) -> None:
    conn.row_factory = sqlite3.Row

    if report_type in {"overview", "summary"}:
        conv = dict(
            conn.execute(
                """
                SELECT
                    COUNT(*) AS total_conversations,
                    SUM(has_transcript) AS with_transcript,
                    SUM(total_steps) AS total_steps,
                    MIN(first_step_at) AS earliest_step_at,
                    MAX(last_step_at) AS latest_step_at
                FROM conversations
                """
            ).fetchone()
        )
        inv = dict(
            conn.execute(
                """
                SELECT
                    COUNT(*) AS total_skills,
                    SUM(is_always_in_prompt) AS always_in_prompt_skills,
                    SUM(CASE WHEN is_always_in_prompt = 1 THEN tier1_tokens_est ELSE 0 END) AS per_turn_prompt_tax_tokens
                FROM skills_inventory
                """
            ).fetchone()
        )
        subcmds = [dict(r) for r in conn.execute("SELECT * FROM v_subcommand_summary").fetchall()]
        top_roi = [dict(r) for r in conn.execute("SELECT * FROM v_skill_roi LIMIT 25").fetchall()]
        if as_json:
            print(
                json.dumps(
                    {
                        "conversations": conv,
                        "inventory": inv,
                        "subcommand_summary": subcmds,
                        "top_skills_roi": top_roi,
                    },
                    indent=2,
                )
            )
            return

        print("=" * 100)
        print("SKILL ANALYTICS OVERVIEW")
        print("=" * 100)
        print(
            f"Conversations:  {conv['total_conversations']} "
            f"(with transcripts: {conv['with_transcript']}, steps: {(conv['total_steps'] or 0):,})"
        )
        print(f"Time Range:     {conv['earliest_step_at']} -> {conv['latest_step_at']}")
        print(
            f"Skill Inventory: {inv['total_skills'] or 0} total | "
            f"{inv['always_in_prompt_skills'] or 0} always-in-prompt "
            f"(~{inv['per_turn_prompt_tax_tokens'] or 0} Tier-1 tokens/turn)"
        )
        print("-" * 100)
        print(f"{'KIND':<22} {'ACTION':<18} {'PROD':>7} {'TEST':>7} {'CONVS':>7} {'LAST SEEN':<20}")
        for r in subcmds:
            print(
                f"{r['invocation_kind']:<22} {r['action']:<18} {r['prod_events']:>7} "
                f"{r['self_test_events']:>7} {r['conversations']:>7} {(r['last_seen_at'] or '')[:19]:<20}"
            )
        print()
        return

    if report_type == "roi":
        rows = [dict(r) for r in conn.execute("SELECT * FROM v_skill_roi").fetchall()]
        if as_json:
            print(json.dumps(rows, indent=2))
            return
        print("=" * 105)
        print("SKILL CONTEXT-TAX vs. ACTIVATION ROI REPORT (v_skill_roi)")
        print("=" * 105)
        print(
            f"{'SKILL':<26} {'TIER':<10} {'PROMPT?':>7} {'T1_TOK':>6} "
            f"{'ACT':>5} {'AUTO':>5} {'EXPL':>5} {'RES':>4} {'RUN':>4} {'RECOMMENDATION'}"
        )
        print("-" * 105)
        for r in rows:
            p_flag = "YES" if r["is_always_in_prompt"] else "no"
            print(
                f"{r['skill_name']:<26} {r['source_tier']:<10} {p_flag:>7} {r['tier1_tokens_est']:>6} "
                f"{r['total_activations']:>5} {r['autonomous_activations']:>5} {r['explicit_activations']:>5} "
                f"{r['resource_reads']:>4} {r['script_runs']:>4} {r['roi_recommendation']}"
            )
        return

    if report_type == "triggers":
        rows = [dict(r) for r in conn.execute("SELECT * FROM v_trigger_attribution").fetchall()]
        if as_json:
            print(json.dumps(rows, indent=2))
            return
        print("=" * 98)
        print("SKILL TRIGGER ATTRIBUTION REPORT (v_trigger_attribution)")
        print("=" * 98)
        print(
            f"{'SKILL':<26} {'TIER':<10} {'TOTAL':>6} {'AUTO':>6} {'EXPLICIT':>8} "
            f"{'RULE':>6} {'AUTO%':>7} {'TRIGGER HEALTH'}"
        )
        print("-" * 98)
        for r in rows:
            print(
                f"{r['skill_name']:<26} {r['source_tier']:<10} {r['total_activations']:>6} "
                f"{r['autonomous_activations']:>6} {r['explicit_activations']:>8} "
                f"{r['rule_activations']:>6} {r['autonomous_share_pct']:>6.1f}% {r['trigger_health']}"
            )
        return

    if report_type == "velocity":
        rows = [dict(r) for r in conn.execute("SELECT * FROM v_daily_invocations LIMIT 60").fetchall()]
        if as_json:
            print(json.dumps(rows, indent=2))
            return
        print("=" * 90)
        print("DAILY INVOCATION VELOCITY (v_daily_invocations)")
        print("=" * 90)
        print(f"{'DAY':<12} {'KIND':<22} {'ACTION':<18} {'PROD':>7} {'TEST':>7} {'CONVS':>7}")
        print("-" * 90)
        for r in rows:
            print(
                f"{r['day']:<12} {r['invocation_kind']:<22} {r['action']:<18} "
                f"{r['prod_count']:>7} {r['test_count']:>7} {r['distinct_conversations']:>7}"
            )
        return

    if report_type == "gaps":
        rows = [dict(r) for r in conn.execute("SELECT * FROM v_search_gaps").fetchall()]
        if as_json:
            print(json.dumps(rows, indent=2))
            return
        print("=" * 95)
        print("SEARCH QUERIES & CATALOG GAP DISCOVERY (v_search_gaps)")
        print("=" * 95)
        print(f"{'QUERY':<42} {'KIND':<16} {'SEARCHES':>8} {'LED_TO_LOAD':>12} {'LAST SEARCHED'}")
        print("-" * 95)
        for r in rows:
            print(
                f"{(r['search_query'] or '')[:40]:<42} {r['invocation_kind']:<16} "
                f"{r['search_count']:>8} {r['led_to_load_count']:>12} {(r['last_searched_at'] or '')[:19]}"
            )
        return

    if report_type == "drift":
        rows = [dict(r) for r in conn.execute("SELECT * FROM v_skill_telemetry_drift").fetchall()]
        if as_json:
            print(json.dumps(rows, indent=2))
            return
        print("=" * 105)
        print("KUNGFU STATE.JSON TELEMETRY DRIFT (v_skill_telemetry_drift)")
        print("=" * 105)
        print(
            f"{'SKILL':<26} {'STATE':>5} {'CLI_1ST':>7} {'LEARN_L':>7} {'VIEW':>5} "
            f"{'TOT_ACT':>7} {'DRIFT':>6} {'DIAGNOSIS'}"
        )
        print("-" * 105)
        for r in rows:
            print(
                f"{r['skill_name']:<26} {r['state_json_count']:>5} {r['transcript_cli_load_primary']:>7} "
                f"{r['transcript_learn_load']:>7} {r['transcript_direct_views']:>5} "
                f"{r['transcript_total_activations']:>7} {r['drift_total_vs_state']:>+6} {r['drift_diagnosis']}"
            )
        return

    fail_fast(f"Unknown report type: {report_type}")


def run_query(conn: sqlite3.Connection, sql: str, as_json: bool = False) -> None:
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
    except Exception as exc:
        fail_fast("SQL query execution failed", context={"sql": sql, "error": str(exc)})

    if as_json:
        print(json.dumps(rows, indent=2))
        return

    if not rows:
        print("(0 rows)")
        return

    headers = list(rows[0].keys())
    widths = {h: max(len(h), *(len(str(r.get(h, ""))) for r in rows)) for h in headers}
    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    print(header_line)
    print("-" * len(header_line))
    for r in rows:
        print(" | ".join(str(r.get(h, "")).ljust(widths[h]) for h in headers))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze.py",
        description="Skill Analytics: Universal Agent Skill Usage, Context-Tax ROI & Telemetry Engine.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["sync", "report", "query", "backfill-state"],
        help="Primary subcommand (sync, report, query, backfill-state).",
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Report name (overview, roi, triggers, velocity, gaps, drift) or SQL query string.",
    )
    parser.add_argument(
        "--mode",
        choices=["rebuild", "incremental", "backfill-state", "summary"],
        help="Compatibility mode flag (rebuild, incremental, backfill-state, summary).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform a full rebuild when running sync.",
    )
    parser.add_argument(
        "--db",
        type=pathlib.Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database (default: {DEFAULT_DB_PATH}).",
    )
    parser.add_argument(
        "--brain-dir",
        type=pathlib.Path,
        default=DEFAULT_BRAIN_DIR,
        help="Path to Antigravity brain directory.",
    )
    parser.add_argument(
        "--summaries-db",
        type=pathlib.Path,
        default=DEFAULT_SUMMARIES_DB,
        help="Path to conversation_summaries.db.",
    )
    parser.add_argument(
        "--state-json",
        type=pathlib.Path,
        default=DEFAULT_STATE_JSON,
        help="Path to KungFu state.json.",
    )
    parser.add_argument(
        "--catalog-dir",
        type=pathlib.Path,
        default=None,
        help="Optional path to local skills catalog repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview backfill changes without modifying state.json (default).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Atomically write reconciled history to state.json.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Map subcommand or --mode
    cmd = args.command
    if not cmd:
        if args.mode == "rebuild":
            cmd = "sync"
            args.full = True
        elif args.mode == "incremental":
            cmd = "sync"
        elif args.mode == "backfill-state":
            cmd = "backfill-state"
        elif args.mode == "summary":
            cmd = "report"
            args.target = "overview"
        else:
            cmd = "sync"

    db_path: pathlib.Path = args.db
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))

    try:
        if cmd == "sync":
            init_db(conn, rebuild=args.full)
            stats = ingest_conversations(
                conn=conn,
                brain_dir=args.brain_dir,
                summaries_db_path=args.summaries_db,
                state_json_path=args.state_json,
                catalog_dir=args.catalog_dir,
                rebuild=args.full,
            )
            if args.json:
                print(json.dumps({"mode": "full" if args.full else "incremental", "stats": stats}, indent=2))
            else:
                print(
                    f"[skill-analytics] sync ({'full' if args.full else 'incremental'}) complete | "
                    f"convs={stats['total_union_conversations']} "
                    f"with_transcripts={stats['conversations_with_transcript']} "
                    f"parsed={stats['conversations_parsed']} "
                    f"skipped={stats['conversations_skipped_unchanged']} "
                    f"steps={stats['steps_scanned']:,} "
                    f"events_inserted={stats['invocations_inserted']:,}"
                )
            return 0

        if cmd == "report":
            init_db(conn, rebuild=False)
            report_name = args.target or "overview"
            run_report(conn, report_name, as_json=args.json)
            return 0

        if cmd == "query":
            if not args.target:
                fail_fast("query subcommand requires a SQL string argument")
            run_query(conn, args.target, as_json=args.json)
            return 0

        if cmd == "backfill-state":
            init_db(conn, rebuild=False)
            plan = compute_backfill_plan(conn, args.state_json)
            if args.apply:
                apply_backfill_state(args.state_json, plan["new_state"])
                sync_state_snapshot_table(conn, args.state_json)
            if args.json:
                out = {k: v for k, v in plan.items() if k != "new_state"}
                out["applied"] = bool(args.apply)
                print(json.dumps(out, indent=2))
            else:
                mode_label = "APPLIED" if args.apply else "DRY-RUN"
                print("=" * 95)
                print(f"KUNGFU STATE.JSON BACKFILL PLAN [{mode_label}]")
                print("=" * 95)
                print(f"Target file:     {plan['state_json_path']}")
                print(
                    f"Tracked skills:  {plan['old_skill_count']} -> {plan['new_skill_count']} | "
                    f"Total load count: {plan['old_total_loads']} -> {plan['new_total_loads']}"
                )
                for ch in plan["changes"]:
                    print(
                        f"  {ch['skill']:<26} {ch['action']:<28} "
                        f"{ch['old_count']:>4} -> {ch['new_count']:>4}"
                    )
            return 0

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
