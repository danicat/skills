# Architectural Directive: RFC 8615 Well-Known Resolution & Catalog Purge

- Status: Mandatory / Non-Negotiable
- Date: 2026-08-23
- Author: Daniela Petruzalek (daniela@danicat.dev)
- Target Audience: KungFu CLI Engineering Team (`github.com/danicat/kungfu`) & Toolchain Maintainers
- Related Directives: Directive 0004, ADR-0002, RFC-0003, SPEC-0001
- Target Standards: IETF RFC 8615 (`.well-known`), `agentskills.io` Discovery Specification v0.2.0

---

## 1. Executive Directive

**Business Directive: Eliminate Redundant Catalog Files & Enforce RFC 8615 Discovery Resolution.**

Maintaining duplicate static JSON files (`/catalog.json` and `/.well-known/agent-skills/index.json`) creates unnecessary data duplication and violates Occam's Razor. 

Following standard internet architecture established by RFC 8615 and package managers (npm, Cargo, Go proxy, OIDC):
1. **The root `/catalog.json` and `/versions.json` have been permanently purged.**
2. **The sole discovery manifest is hosted at `/.well-known/agent-skills/index.json`.**
3. **The catalog coordinate declared in `SKILL.md` frontmatter and CLI flags is the clean base origin URL (e.g. `https://skills.danicat.dev`), with no hardcoded JSON filenames.**

---

## 2. CLI Implementation Requirements

### 2.1 Base Origin URL Auto-Completion
When the KungFu CLI receives a registry coordinate (via `--registry`, `.kungfurc`, or `metadata.catalog`), it MUST resolve endpoints as follows:

1. **Base Domain / Origin** (e.g., `https://skills.danicat.dev` or `skills.danicat.dev`):
   - Standard Discovery: `${origin}/.well-known/agent-skills/index.json`
2. **Explicit File URL** (e.g., `https://example.com/custom-manifest.json`):
   - Direct Ingestion: Fetch the supplied URL directly.

### 2.2 In-Flight Frontmatter Parsing
When reading `metadata.catalog` from installed or discovered `SKILL.md` files:
- The `catalog` field contains `https://skills.danicat.dev` (base origin).
- The CLI automatically queries `${catalog}/.well-known/agent-skills/index.json` to verify updates or retrieve the skill index.

### 2.3 State Tracking Manifest (`~/.config/kungfu/state.json`)
The `installed.<skill>.registry` field in `state.json` MUST store the clean base origin:
```json
{
  "version": 1,
  "installed": {
    "godoctor": {
      "registry": "https://skills.danicat.dev",
      "scope": "workspace",
      "path": ".agents/skills/godoctor",
      "version": "0.2.0",
      "sha256": "cb8f829d8d3ec1590408544a49c6d62884a2d8a571f0ffc9d6438069542a170a",
      "installedAt": "2026-08-23T00:00:00Z"
    }
  }
}
```

---

## 3. Normative Discovery Manifest (`/.well-known/agent-skills/index.json`)

Minimal manifest structure with **zero custom top-level fields**:

```json
{
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

---

## 4. Verification & Readiness

1. **Repository & Website Generator**: `scripts/build_site.mjs` has purged `catalog.json` and `versions.json`, and exclusively emits `/.well-known/agent-skills/index.json`.
2. **All 28 Skills Standardized**: `SKILL.md` frontmatter across all skills declares `metadata.catalog: https://skills.danicat.dev`.
3. **Validation Passed**: `scripts/validate_metadata.mjs` and `scripts/qa_audit.mjs` pass 100% green with 0 errors and 0 warnings.
