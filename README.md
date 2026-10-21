# Agent Skills

A curated collection of specialized skills for AI agents and pair programmers, organized by domain.

---

## Installation

### Install from GitHub
Install skills directly from this repository using `kungfu` or the Skills CLI:

```bash
# Stream or install a specific skill via KungFu:
kungfu load ebitengineer
kungfu learn engineering-flow

# Install a specific skill via npx skills:
npx skills add danicat/skills --skill engineering-flow -y
npx skills add danicat/skills --skill ebitengineer -y
npx skills add danicat/skills --skill skill-optimizer -y

# Install all skills from this repository:
npx skills add danicat/skills -y
```

---

## Agent Skills

### 🕹️ Games (`game-dev/`)
Specialized skills for designing and building 2D games in Go with Ebitengine, chiptune DSP, and procedural generation.

* **[`ebitengineer`](game-dev/ebitengineer/SKILL.md)**: Production-grade 2D game architecture, cycle timing, state machines, shaders, and audio sync for Go & Ebitengine (v2).
* **[`game-design`](game-dev/game-design/SKILL.md)**: Game concept ideation, interactive `/grill-me` design interviews, and Game Design Document (`GDD.md`) generation.
* **[`procedural-art`](game-dev/procedural-art/SKILL.md)**: Pure-code procedural 2D sprites, tilemaps, vector graphics, particle systems, and rasterization algorithms without external assets.
* **[`procedural-composer`](game-dev/procedural-composer/SKILL.md)**: Pure-code procedural audio synthesis, sound effects (SFX), and chiptune/FM sound engine architecture.
* **[`sprite-animation`](game-dev/sprite-animation/SKILL.md)**: 2D sprite sheets, frame durations, tag loops, and Aseprite (`.ase`/`.aseprite`) file validation and slicing.
* **[`vibe-game-developer`](game-dev/vibe-game-developer/SKILL.md)**: Master orchestrator and request router for 2D Go game development, asset pipelines, and WebAssembly deployment.

---

### 🎨 GenAI (`media/`)
Audio and visual generation using Google AI models with ADC authentication.

* **[`lyria`](media/lyria/SKILL.md)**: High-fidelity 44.1 kHz stereo music and soundtrack generation from text prompts and images using Google's Lyria 3 models.
* **[`nano-banana`](media/nano-banana/SKILL.md)**: Conversational image generation and editing using Google's native Nano Banana models with character consistency support.

---

### 💻 Software Engineering (`coding/`)
Engineering workflow standards, compiler gates, package resolvers, architectural decision records, and language-specific tools.

* **[`adr-template`](coding/adr-template/SKILL.md)**: Guidelines, best practices, and templates for authoring immutable Architecture Decision Records (ADRs).
* **[`engineering-flow`](coding/engineering-flow/SKILL.md)**: Engineering workflow standards detailing semantic versioning (with 0.x zero-debt rules), broken window hygiene, RFC/ADR planning, and the 7-tier Evidence Hierarchy.
* **[`godoctor`](coding/godoctor/SKILL.md)**: Go developer tooling and static analysis orchestrator with automatic compiler rollback gates, Selene mutation testing, and TestQuery analytics.
* **[`google-oss`](coding/google-oss/SKILL.md)**: Apply and verify Google open-source compliance, Apache-2.0 license headers via `addlicense`, copyright attributions, and repository disclaimers.
* **[`latest-version`](coding/latest-version/SKILL.md)**: Real-time package registry and Gemini model version resolver (NPM, PyPI, Go proxy, Cargo, RubyGems).
* **[`less-is-more`](coding/less-is-more/SKILL.md)**: Frontend design and universal simplification skill that counters AI interface bloat using the Inverted Pyramid, Material Symbols icon buttons with hover hints, non-modal settings popovers, and plain English.
* **[`pyhd`](coding/pyhd/SKILL.md)**: Modern Python development workflow using `uv` virtual environments, Ruff linting/formatting, and pytest suites.
* **[`rfc-template`](coding/rfc-template/SKILL.md)**: Collaborative Request for Comments (RFC) frameworks for exploring major features and complex design alternatives.

---

### 🤖 Agents (`agents/`)
Frameworks, multi-agent swarm orchestration, and skill authoring tools.

* **[`double-diamond`](agents/double-diamond/SKILL.md)**: Two-phase multi-agent orchestration for complex engineering initiatives separating problem space discovery from solution space implementation with human steering gates.
* **[`intercom`](agents/intercom/SKILL.md)**: Cross-session and cross-project agent communication in Antigravity using the native `agentapi` CLI and `conversation_summaries.db`, with automatic session discovery, `projectId` environment sanitization, and return-address framing.
* **[`parallel`](agents/parallel/SKILL.md)**: General-purpose task parallelization and agent scaling engine across concurrent subagents.
* **[`show-me-the-money`](agents/show-me-the-money/SKILL.md)**: Mine local conversation history, brain artifacts, and full session transcripts using parallel Flash/Flash-Lite `agy` CLI workers to recover high-value features lost to conversation drift or abandonment without burning frontier model quota.
* **[`skill-optimizer`](agents/skill-optimizer/SKILL.md)**: Meta-skill for authoring, auditing, and optimizing Agent Skills according to the official specification, trigger evaluation, and MCP setup (`https://agentskills.io/mcp`).
* **[`swarm-coding`](agents/swarm-coding/SKILL.md)**: Parallelized multi-agent swarm task decomposition and coordination for complex full-stack features and refactorings.
* **[`uno-reverse`](agents/uno-reverse/SKILL.md)**: Radical simplification, red-teaming, and Occam's Razor devil's advocate for software architecture, PRDs, agent workflows, and technical designs.

---

### ✍️ Writing (`writing/`)
Editorial guidelines, Inverted Pyramid hierarchy, AI slop removal, social copy, and developer documentation.

* **[`buffer`](writing/buffer/SKILL.md)**: Manage, draft, schedule, and publish social media content across connected channels using the Buffer CLI.
* **[`deslopify`](writing/deslopify/SKILL.md)**: Re-write, edit, and purge text of common AI tropes, clichés, and formulaic filler using strict editorial guidelines.
* **[`google-blog-style`](writing/google-blog-style/SKILL.md)**: Official style guide and compliance rules for the Google Developers Blog, including Gunning Fog readability and Vale style checks.
* **[`inverted-pyramid`](writing/inverted-pyramid/SKILL.md)**: Action-first, summary-first information hierarchy for technical documentation and developer guides.
* **[`seo-optimizer`](writing/seo-optimizer/SKILL.md)**: Technical SEO and Generative Engine Optimization (GEO) for developer blogs and documentation, including metadata split (summary vs. description), heading hierarchies, and `llms.txt` generation.
* **[`social-copy`](writing/social-copy/SKILL.md)**: Draft, audit, and optimize high-performing technical and developer social media copy across LinkedIn, Twitter/X, Bluesky, Instagram, Reddit, and Threads.

---

### 📊 Analytics (`analytics/`)
Raw metrics ingestion and SQLite data warehousing for search performance, web traffic, and social distribution.

* **[`buffer-analytics`](analytics/buffer-analytics/SKILL.md)**: Ingest raw Buffer social post and channel data into a local SQLite analytics database and run SQL queries across LinkedIn, Twitter/X, and Bluesky.
* **[`google-analytics`](analytics/google-analytics/SKILL.md)**: Ingest raw Google Analytics 4 (GA4) traffic, dwell time, localization performance, and outbound clicks into a local SQLite analytics database and run pre-built or ad-hoc SQL reports.
* **[`search-analytics`](analytics/search-analytics/SKILL.md)**: Ingest raw Google Search Console performance metrics into a local SQLite database and execute deep SQL analytics over organic search traffic.
* **[`skill-analytics`](analytics/skill-analytics/SKILL.md)**: Mine Agent Skill usage, Context-Tax ROI, and trigger attribution from conversation transcripts into a local SQLite database across all installed skill tiers.

---

## Freshness

Every skill in [skills.danicat.dev](https://skills.danicat.dev/freshness/) has a freshness score calculated from substantive Git commit age (`U`, 45-day half-life), `kungfu` CLI telemetry (`loads`, `runs`, `learns`), `npx skills` installs, and web engagement across **🌱 New**, **✨ Mint** (`90–100%`), **🌿 Fresh** (`70–89%`), **🕸️ Stale** (`50–69%`), **🤢 Spoiled** (`25–49%`), and **🦠 Rotten** (`0–24%`).

## Graveyard

Retired skills live in the **[Graveyard](https://skills.danicat.dev/graveyard/)**:

| Skill | Lifespan | Why It Was Killed | Replacement | Command |
| :--- | :--- | :--- | :--- | :--- |
| `go-best-practices` | Feb 14 – Feb 16, 2026 | Merged into `godoctor` | [`godoctor`](coding/godoctor/SKILL.md) | `kungfu forget go-best-practices && kungfu learn godoctor` |
| `go-project-setup` | Feb 14 – Feb 16, 2026 | Merged into `godoctor` | [`godoctor`](coding/godoctor/SKILL.md) | `kungfu forget go-project-setup && kungfu learn godoctor` |
| `a2ui-developer-guide` | Feb 14 – Feb 21, 2026 | Factually incorrect (produced botched implementations) | None | `kungfu forget a2ui-developer-guide` |
| `find-examples` | Feb 14 – Mar 14, 2026 | Never used in real life | None | `kungfu forget find-examples` |
| `google-codelab-authoring` | Feb 14 – Mar 19, 2026 | Never used in real life | None | `kungfu forget google-codelab-authoring` |
| `agy-extensions` | Mar 23 – Mar 26, 2026 | Replaced by official `agy-customizations` skill | `agy-customizations` | `kungfu forget agy-extensions` |
| `experiment-analyst` | Mar 15 – Apr 7, 2026 | Niche analysis skill not meant for general use | None | `kungfu forget experiment-analyst` |
| `catalog` | Feb 14 – Apr 2026 | Unnecessary; replaced by `kungfu list` and `kungfu find` | `kungfu list` / `kungfu find` | `kungfu forget catalog` |
