# ADR-0002: Agent Skills Extended Specification — Progressive Disclosure, Intrinsic Provenance & 100% Spec-Compliant Discovery

- Status: Approved
- Date: 2026-08-23
- Author(s): Daniela Petruzalek (daniela@danicat.dev)
- Deciders: Daniela Petruzalek (daniela@danicat.dev)
- Target Standards: `agentskills.io` Discovery Specification v0.2.0, RFC-0003, SPEC-0001
- Supersedes: Portions of ADR-0001 relating to redundant frontmatter URLs (`homepage`, `canonical`, `repository`) and custom top-level catalog properties.

---

## 1. Context

In ADR-0001, we established basic metadata conventions for Agent Skills (`SKILL.md`). However, as the ecosystem matured and third-party AI coding harnesses (Cursor, Claude Code, Codex, OpenDevin, Aider) introduced strict JSON schema validation, several critical architecture problems arose:

1. **Schema Contamination in Discovery Manifests**: Adding non-standard custom fields (`categories[]`, `gateway`, `totalSkills`, `githubUrl`, `detailUrl`, `items[]`) to discovery manifests breaks downstream agent harnesses configured with strict validation (`additionalProperties: false`).
2. **Redundant Provenance Triplication in Frontmatter**: Frontmatter in ADR-0001 required `homepage`, `canonical`, and `repository`. In monorepos and registries, all three URLs are mechanically derivable from the base catalog and the skill's category and name.
3. **Duplicate Root Manifest Files**: Maintaining both `catalog.json` and `.well-known/agent-skills/index.json` created duplicate data files on disk.
4. **Context Window Token Bloat**: Without explicit token accounting across progressive disclosure tiers, agent orchestrators risked saturating context windows during session startup.
5. **Sub-Millisecond CLI Diffing**: Full catalog synchronization across hundreds of skills introduced unnecessary network payload overhead for local package managers (KungFu CLI).

---

## 2. Decision

We formally approve and enforce the **Agent Skills Extended Specification** across the repository and ecosystem:

### 2.1 100% Spec-Compliant Discovery Manifest (`/.well-known/agent-skills/index.json`)
The public discovery manifest MUST conform 100% strictly to `https://schemas.agentskills.io/discovery/0.2.0/schema.json` with **zero custom top-level schema extensions**:

```json
{
  "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
  "skills": [
    {
      "name": "godoctor",
      "type": "skill-md",
      "description": "Developer tooling and architectural safety rules for Go. Automatically validates AST integrity, guards against regressions with compiler rollback gates, eliminates blind spots via Selene mutation testing, and isolates test databases with TestQuery SQL transactions. Activate when writing or refactoring Go code, fixing compilation or test failures, auditing test thoroughness with mutation testing, or enforcing idiomatic Go standards.",
      "url": "https://skills.danicat.dev/coding/godoctor/SKILL.md",
      "digest": "sha256:cb8f829d8d3ec1590408544a49c6d62884a2d8a571f0ffc9d6438069542a170a"
    }
  ]
}
```

- **RFC 8615 Standard Endpoint**: The manifest is published exclusively at `/.well-known/agent-skills/index.json`. Duplicate root `catalog.json` files are deleted.
- **Zero Extraneous Fields**: All taxonomy, category metadata, and author details reside inside the individual `SKILL.md` files, keeping discovery manifests lean, fast, and universally parseable.

---

### 2.2 Intrinsic Provenance & Base Origin Coordinate (`SKILL.md`)
We collapse redundant URL declarations into a single base origin coordinate:

```yaml
---
name: godoctor
description: >
  Developer tooling and architectural safety rules for Go. Automatically
  validates AST integrity, guards against regressions with compiler rollback
  gates, eliminates blind spots via Selene mutation testing, and isolates
  test databases with TestQuery SQL transactions. Activate when writing or
  refactoring Go code, fixing compilation or test failures, auditing test
  thoroughness with mutation testing, or enforcing idiomatic Go standards.
license: Apache-2.0
metadata:
  category: coding
  tags: "go, golang, testing, refactoring, quality, mutation-testing"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  catalog: https://skills.danicat.dev
---
```

1. **`metadata.catalog` (Base Origin Coordinate)**: Points directly to the authoritative registry base URL (`https://skills.danicat.dev`). Downstream tools automatically resolve `/.well-known/agent-skills/index.json` or `/versions.json`.
2. **`metadata.repository` (Fallback for Standalone Skills)**: Used only when a skill author publishes an isolated repository without an associated catalog.
3. **Purged Fields**: `homepage`, `canonical`, and redundant `repository` (in catalog-managed skills) are purged from `SKILL.md` frontmatter.

---

### 2.3 The 3-Tier Progressive Disclosure Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       3-TIER PROGRESSIVE DISCLOSURE                         │
├────────┬──────────────────────────┬─────────────────┬───────────────────────┤
│ Tier   │ Scope                    │ Size Budget     │ Ingestion Phase       │
├────────┼──────────────────────────┼─────────────────┼───────────────────────┤
│ Tier 1 │ name + description       │ <= 150 tokens   │ Agent Startup Prompt  │
│ Tier 2 │ SKILL.md Markdown Body   │ <= 5,000 tokens │ On Skill Activation   │
│ Tier 3 │ references/ & scripts/   │ Dynamic / Tools │ On-Demand Tool Calls  │
└────────┴──────────────────────────┴─────────────────┴───────────────────────┘
```

---

### 2.4 Fast-Sync Optimization Manifest (`/.well-known/agent-skills/versions.json`)
To enable sub-5ms CLI hash comparisons (`kungfu update` / `kungfu list --all`) without downloading large payloads, registries publish a separate, unpolluted key-value hash map:

```json
{
  "updatedAt": "2026-08-23T00:00:00.000Z",
  "totalSkills": 28,
  "skills": {
    "godoctor": {
      "v": "0.2.0",
      "h": "cb8f829d8d3ec1590408544a49c6d62884a2d8a571f0ffc9d6438069542a170a",
      "c": "coding",
      "u": "https://skills.danicat.dev/coding/godoctor/SKILL.md"
    }
  }
}
```

---

## 3. Consequences

### Positive
- **100% Interoperability**: Zero schema errors across third-party AI agents, strict JSON schema validators, and public scrapers.
- **Minimal Maintenance Overhead**: Updating base domains or repository structures requires editing only the site generator and catalog compiler, not individual `SKILL.md` files.
- **Fast Local Execution**: Sub-millisecond cache lookups and SHA-256 integrity verification in native CLI tooling.
- **Clean Token Accounting**: Strict progressive disclosure budgets guarantee LLM context efficiency.
- **Zero Redundancy**: No duplicate catalog files in the repository.

### Negative / Trade-offs
- Downstream tools expecting legacy ADR-0001 fields (`metadata.canonical`, `metadata.homepage`) or `/catalog.json` must query base domains via RFC 8615 well-known path resolution (`/.well-known/agent-skills/index.json`).

---

## 4. Compliance & Verification

- **Build Pipeline**: `scripts/build_site.mjs` generates `/.well-known/agent-skills/index.json` adhering to schema v0.2.0.
- **Static Validation**: `scripts/validate_metadata.mjs` validates 100% green across all 28 skills.
- **Reference Runtime**: Go CLI implementation (`github.com/danicat/kungfu`) verified against `SPEC-0001`.
