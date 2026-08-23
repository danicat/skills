# Architectural Proposal: Per-Skill Catalog Provenance (`metadata.catalog`) in Decentralized Ecosystems

- **Proposal Target**: Antigravity Core Implementation Team (`github.com/danicat/kungfu`)
- **Author**: Agent Skills Spec & Catalog Architects (`../skills`)
- **Date**: 2026-08-22
- **Status**: Open for Review

---

## 1. Motivation: Centralized vs. Decentralized Package Ecosystems

In centralized package managers (such as `npm` or `crates.io`), packages do not declare a registry in `package.json` because 99.9% of traffic flows through a single monolithic endpoint (`registry.npmjs.org`).

However, the **Agent Skills ecosystem is inherently decentralized and federated** (similar to Go modules, RSS/Atom feeds, and Git remotes). In this decentralized model, a user's workspace frequently contains skills installed from **different independent catalogs**:

```text
my-project/.agents/skills/
  ├── godoctor/        <- Origin: https://skills.danicat.dev/catalog.json
  ├── corp-deploy/     <- Origin: https://skills.internal.mycompany.com/catalog.json
  └── community-tool/  <- Origin: https://skills.community.org/catalog.json
```

---

## 2. The Multi-Catalog Update Blind Spot

If `SKILL.md` omits `metadata.catalog`, the CLI tool is forced to query only its single global default registry:

1. **The Multi-Source Failure**:
   - When a developer runs `kungfu update`, KungFu queries its default registry (`skills.danicat.dev`).
   - `corp-deploy` and `community-tool` are not in `skills.danicat.dev`.
   - KungFu is forced to treat them as "Unmanaged Local Skills", leaving the user with **no way to check for updates or verify cryptographic digests**.
2. **The Standalone Sharing Failure**:
   - If a developer copies a single `SKILL.md` from a blog post or git repository into `.agents/skills/`, it loses its origin metadata and becomes an unmanaged orphan.

---

## 3. The Proposed 3-Axis Provenance Model

We propose formalizing the complete **3-Axis Provenance Model** inside `metadata`:

```yaml
---
name: godoctor
description: Developer tooling and architectural safety rules for Go...
license: Apache-2.0
metadata:
  category: coding
  tags: "go, golang, testing"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  canonical: https://skills.danicat.dev/coding/godoctor/
  repository: https://github.com/danicat/skills/tree/main/coding/godoctor
  catalog: https://skills.danicat.dev/catalog.json
---
```

### Coordinate Roles:

| Coordinate | Target Audience | Purpose |
|---|---|---|
| **`canonical`** | Humans & Search Engines | Web documentation landing page & SEO. |
| **`repository`** | Developers & Git Submodules | Source code repository tree for PRs, issues, and audits. |
| **`catalog`** | Agent CLIs (`kungfu`, IDEs) | Authoritative manifest endpoint for updates and SHA-256 verification. |

---

## 4. Preserving Fork & Mirror Flexibility: Resolution Precedence

To address the valid concern that hardcoded URLs could impede private mirrors or air-gapped development, the CLI enforces a strict **Precedence Hierarchy**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REGISTRY RESOLUTION ORDER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Explicit CLI Flag (`kungfu update --registry <url>`)  [Highest Priority] │
│ 2. Environment Variable (`KUNGFU_REGISTRY=<url>`)                          │
│ 3. User Configuration (`~/.config/kungfu/config.yaml`)                      │
│ 4. Per-Skill Metadata (`metadata.catalog` inside SKILL.md)                  │
│ 5. Default Public Catalog (`https://skills.danicat.dev`) [Fallback]       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### How `kungfu update` Leverages This:
1. When checking a skill without global registry overrides, `kungfu` reads `metadata.catalog` from `SKILL.md`.
2. It derives the companion fast-sync endpoint (`catalog.json` $\rightarrow$ `versions.json`) to perform $< 5\text{ ms}$ hash checks against the skill's actual home registry.
3. If the user passes `--registry <mirror-url>` or sets `KUNGFU_REGISTRY`, KungFu ignores `metadata.catalog` and routes all requests through the specified mirror.

---

## 5. Call for Feedback from the CLI Team

1. Does the proposed precedence order cleanly integrate with the existing `internal/catalog` resolver?
2. Does per-skill `metadata.catalog` provide the desired multi-registry federation for `kungfu update`?
