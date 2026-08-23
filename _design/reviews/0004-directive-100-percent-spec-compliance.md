# Architectural Directive: 100% agentskills.io Spec Compliance & Zero Schema Contamination

- Status: Mandatory / Non-Negotiable
- Date: 2026-08-23
- Author: Daniela Petruzalek (daniela@danicat.dev)
- Target Audience: KungFu CLI Engineering Team & Catalog Compiler Maintainers
- Normative Schema: `https://schemas.agentskills.io/discovery/0.2.0/schema.json`

---

## 1. Executive Directive

**Business Directive: 100% SPEC COMPLIANCE.**

The `agentskills.io` standard is an external, open specification. Modifying, extending, or introducing non-standard custom top-level fields into public discovery manifests (`catalog.json` / `index.json`) breaks third-party agent tools (Claude Code, Cursor, Codex, OpenDevin, Aider) that enforce strict JSON Schema validation (`additionalProperties: false`).

**Effective immediately, all catalog manifests published by this repository and consumed by the KungFu CLI must strictly adhere to the official specification with ZERO custom top-level schema fields.**

---

## 2. Normative Discovery Manifest Specification

Discovery endpoints MUST be published at both:
1. `/.well-known/agent-skills/index.json` (Standard discovery path)
2. `/catalog.json` (Canonical alias for backwards compatibility)

### 2.1 Schema Definition
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

### 2.2 Field Invariants:
1. **Root `$schema`**: Must be `"https://schemas.agentskills.io/discovery/0.2.0/schema.json"`.
2. **Root `skills`**: Must be an array containing skill descriptor objects (renamed from legacy `items`).
3. **`name`**: URL-safe slug (1–64 characters, lowercase alphanumeric and hyphens).
4. **`type`**: String literal `"skill-md"`.
5. **`description`**: Tier 1 routing description ($\le 1024$ characters).
6. **`url`**: Direct HTTPS URI pointing to the target `SKILL.md`.
7. **`digest`**: Cryptographic content hash prefixed with algorithm: `"sha256:<64-hex-characters>"`.
8. **ZERO NON-STANDARD FIELDS**: Fields such as `category`, `tags`, `author`, `version`, `byteSize`, `tokenEstimate`, `detailUrl`, `githubUrl`, or `categories[]` MUST NOT be serialized into discovery manifests.

---

## 3. Where Extended Metadata Lives

All domain taxonomy and author metadata MUST reside inside the `metadata:` dictionary of `SKILL.md` frontmatter, as permitted by the base specification:

```yaml
---
name: godoctor
description: Developer tooling and architectural safety rules for Go...
license: Apache-2.0
compatibility: Requires Go 1.22+
allowed-tools: Bash(go:*) Read
metadata:
  category: coding
  tags: "go, golang, testing, refactoring, quality, mutation-testing"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  catalog: https://skills.danicat.dev/catalog.json
---
```

### Downstream Tooling Protocol:
* **Remote Discovery**: `kungfu list` and `kungfu find` query the standard manifest for `name`, `description`, `url`, and `digest`.
* **Deep Inspection & JIT Loading**: When `kungfu show` or `kungfu load` fetches a skill, it parses the YAML frontmatter of `SKILL.md` to extract extended metadata (`category`, `tags`, `author`, `version`, `catalog`).
* **Fast-Sync (Optional)**: `/versions.json` remains available as a lightweight `{ [name]: { v, h, c, u } }` key-value optimization for CLI hash diffs without polluting the standard discovery manifest.

---

## 4. CLI Implementation Requirements (`kungfu`)

1. **Manifest Ingestion**: Update `internal/catalog` parser in Go to parse `skills: []` containing `type: "skill-md"` and `digest: "sha256:<hex>"`.
2. **State Tracking**: Update `~/.config/kungfu/state.json` to record `"registry"` origin:
   ```json
   {
     "installed": {
       "godoctor": {
         "registry": "https://skills.danicat.dev/catalog.json",
         "scope": "workspace",
         "path": ".agents/skills/godoctor",
         "version": "0.2.0",
         "sha256": "cb8f829d8d3e...",
         "installedAt": "2026-08-23T00:00:00Z"
       }
     }
   }
   ```
3. **Symlink Security in `load`**: Enforce `os.Root` (Go 1.24+) or `filepath.EvalSymlinks` on all subpath requests (`kungfu load <skill>/<path>`) to guarantee the resolved path remains strictly within the skill directory jail.

---

This directive is approved and binding for all development across `skills` and `kungfu`.
