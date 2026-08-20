# ADR-0001: Agent Skills Metadata & Catalog Specification

- Status: Approved
- Date: 2026-08-20
- Author(s): Daniela Petruzalek (daniela@danicat.dev)
- Deciders: Daniela Petruzalek (daniela@danicat.dev)
- Schema Reference: `https://agentskills.io/schema/v1/catalog.json`

---

## 1. Context

Autonomous AI agents and coding assistants require structured, progressive access to specialized engineering skills, workflows, and domain knowledge. As the catalog of Agent Skills grew across game development, media generation, Go tooling, writing guidelines, and engineering standards, two fundamental challenges emerged:

1. **Schema Fragmentation**: Multiple formats existed across early skill definitions, static site generators (`skills.danicat.dev`), and package managers (`npx skills`). Without a single normative specification, frontmatter keys diverged (e.g., camelCase vs. snake_case, string vs. array tags, nested vs. flat metadata).
2. **Gateway Discovery & Runtime Loading**: Modern agent workflows need sub-millisecond local discovery, category browsing, fuzzy search, and dynamic context injection without requiring heavy Node.js or Python runtimes.

To solve these challenges, we established a unified specification aligning the **Agent Skills Metadata Format** (`agentskills.io/schema/v1`), static site generation, and the **Gateway CLI** ecosystem.

---

## 2. Decision

We define and standardize the **Agent Skills & Open Knowledge Format (OKF) Metadata Specification** across both the `skills` repository (`https://skills.danicat.dev`) and native CLI tools.

### 2.1 YAML Frontmatter Specification (`SKILL.md`)

Every skill package MUST contain a `SKILL.md` file at its root with valid YAML frontmatter delimited by `---`:

```yaml
---
name: godoctor
description: >
  Activate this skill whenever developing, building, editing, testing,
  documenting, or verifying Go (golang) code, or managing GoDoctor CLI and MCP
  surfaces. Enforces strict Google Go Style, flat package architecture,
  zero-fallback execution, multi-tier testing, AST-aware edits with compiler
  rollback gates, Selene mutation testing, and TestQuery SQL analytics.
license: Apache-2.0
metadata:
  category: coding
  tags: "coding, golang, ast, refactoring, testing, mutation, selene, testquery"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.34.0"
  homepage: https://skills.danicat.dev/coding/godoctor/
  canonical: https://skills.danicat.dev/coding/godoctor/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/coding/godoctor
---
```

#### Field Rules:
- **`name`** *(string, required)*: Lowercase alphanumeric kebab-case identifier matching the directory name.
- **`description`** *(string, required)*: Concise summary written with explicit agent trigger conditions ("Activate this skill when...").
- **`license`** *(string, required)*: Valid SPDX identifier (e.g., `Apache-2.0`, `MIT`).
- **`allowed-tools`** *(string, optional)*: Comma-separated list of tool permissions.
- **`metadata`** *(mapping, required)*:
  - **`category`** *(string, required)*: One of the 7 canonical categories.
  - **`tags`** *(string or array, required)*: Comma-separated string or YAML sequence of keywords.
  - **`author`** *(string, required)*: Primary maintainer identifier (e.g., `Daniela Petruzalek (daniela@danicat.dev)`).
  - **`version`** *(string, required)*: Semantic Version string (`X.Y.Z`).
  - **`homepage`** *(string, required)*: Skill documentation landing URL.
  - **`canonical`** *(string, required)*: Absolute URL to the raw `SKILL.md`.
  - **`repository`** *(string, required)*: Absolute URL to the Git source folder.

---

### 2.2 Canonical Taxonomy

All skills and knowledge bundles MUST belong to exactly one of the seven official categories:

| ID | Name | Emoji | Scope & Focus |
|---|---|---|---|
| `game-dev` | Game Development | 🕹️ | 2D game architecture, Ebitengine, procedural art, chiptune audio, shaders, WebAssembly |
| `media` | Generative Media | 🎨 | Multimodal audio synthesis, visual prompts, procedural generators, asset pipelines |
| `coding` | Coding & Tooling | 💻 | Go style enforcement, AST refactoring, mutation testing, compiler rollback gates |
| `agents` | Agents & Meta-Tooling | 🤖 | Agent Skills authoring, evaluation suites, progressive disclosure, swarm orchestration |
| `writing` | Technical Writing | ✍️ | De-slopification, Inverted Pyramid density, tech review, style guidelines |
| `standards` | Engineering Standards | 📐 | Request for Comments (RFCs), Architecture Decision Records (ADRs), QA gates |
| `gateway` | Gateway / CLI | 🥋 | Fast discovery, catalog synchronization, search indexing, batch loading |

---

### 2.3 Catalog JSON Schema (`https://agentskills.io/schema/v1/catalog.json`)

The remote index published at `https://skills.danicat.dev/catalog.json` aggregates all skills into a structured, declarative manifest adhering strictly to the `agentskills.io` standard:

```json
{
  "$schema": "https://agentskills.io/schema/v1/catalog.json",
  "name": "danicat/skills",
  "title": "Daniela Petruzalek Agent Skills Catalog",
  "description": "Curated collection of production-grade Agent Skills and Open Knowledge bundles.",
  "url": "https://skills.danicat.dev",
  "repository": "https://github.com/danicat/skills",
  "totalSkills": 27,
  "updatedAt": "2026-08-20T22:28:48.846Z",
  "categories": [
    {
      "id": "coding",
      "name": "Coding & Tooling",
      "emoji": "💻",
      "description": "Go quality enforcement, AST refactoring, and test analytics."
    }
  ],
  "gateway": {
    "name": "catalog",
    "description": "Dynamic search and loader for all skills in this repository.",
    "url": "https://skills.danicat.dev/SKILL.md"
  },
  "items": [
    {
      "id": "godoctor",
      "name": "godoctor",
      "type": "skill",
      "category": "coding",
      "categoryName": "Coding & Tooling",
      "categoryEmoji": "💻",
      "description": "Activate this skill whenever developing, building, editing...",
      "tags": ["coding", "golang", "ast", "testing"],
      "author": "Daniela Petruzalek (daniela@danicat.dev)",
      "version": "0.34.0",
      "license": "Apache-2.0",
      "digest": "sha256:d8a2...4c",
      "sha256": "sha256:d8a2...4c",
      "byteSize": 11190,
      "tokenEstimate": 2797,
      "url": "https://skills.danicat.dev/coding/godoctor/SKILL.md",
      "detailUrl": "https://skills.danicat.dev/coding/godoctor/",
      "githubUrl": "https://github.com/danicat/skills/tree/main/coding/godoctor",
      "relativePath": "coding/godoctor/SKILL.md",
      "metadata": {
        "category": "coding",
        "tags": "coding, golang, ast, testing",
        "author": "Daniela Petruzalek (daniela@danicat.dev)",
        "version": "0.34.0",
        "homepage": "https://skills.danicat.dev/coding/godoctor/",
        "canonical": "https://skills.danicat.dev/coding/godoctor/SKILL.md",
        "repository": "https://github.com/danicat/skills/tree/main/coding/godoctor"
      }
    }
  ]
}
```

> [!NOTE]
> **Declarative Registry Principle**: In accordance with open registry standards (`agentskills.io`, `npm`, `pypi`, `cargo`), the catalog manifest is strictly declarative. Imperative client execution strings (such as `installCommand`, `npx_add`, etc.) are omitted from item descriptors; downstream tools (CLIs, LLM agents, web templates) construct client-specific command invocations deterministically from `repository` and `name`.

---

### 2.4 Gateway Ingestion & Normalization Protocol

To guarantee 100% backward and forward compatibility, native CLI gateways implement an automated normalization pipeline in `internal/catalog`:

1. **Dual Collection Support**: Unmarshals both `items` and legacy `skills` manifest arrays.
2. **Metadata Backfilling**: If top-level fields (`category`, `author`, `version`, `tags`, `url`, `githubUrl`) are omitted in manual entries, `Item.Normalize()` automatically populates them from the nested `metadata` dictionary.
3. **Digest Hashing**: Normalizes and verifies SHA-256 digests (`sha256:...`) during cache persistence and live content retrieval.
4. **Self-Skill Injection**: Automatically embeds the local gateway self-skill (`version: "0.1.0"`, `category: "gateway"`) to ensure the CLI is always discoverable even in total network isolation.

---

## 3. Consequences

### Positive Impacts:
- **Zero Loss Interoperability**: Tools across the ecosystem (Web docs, Node CLI, Go CLI gateways, LLM agents) read identical metadata representations without discrepancies.
- **Offline Resilience**: Caches catalog manifests and downloaded skills locally under standard cache directories (`~/.cache/...`), falling back gracefully when offline.
- **Strict Discoverability**: Consistent categories and tags power fuzzy search, boolean filters (`-t "golang AND testing"`), and Levenshtein suggestion engines.

### Constraints & Trade-offs:
- **Strict Frontmatter Gate**: Skills missing required metadata fields fail site build (`validate_metadata.mjs`) and Open Knowledge verification tests.
- **Canonical Category Rule**: Sub-categories or arbitrary folder names are disallowed; all skills must map directly into one of the 7 designated top-level categories.

---

## 4. Compliance and Verification

1. **Automated Frontmatter Validator**: `node scripts/validate_metadata.mjs` runs in CI and pre-commit hooks to verify all frontmatter blocks.
2. **Catalog Ingestion Test Suite**: `internal/catalog/catalog_test.go:TestManifestNormalization` validates end-to-end unmarshaling and field normalization.
3. **GoDoctor Quality Gates**: Full test pass and coverage validation via `godoctor call test`.
