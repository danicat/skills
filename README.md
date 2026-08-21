# Agent Skills Collection

A curated collection of specialized skills for AI agents and pair programmers, organized by domain.

---

## Installation

### Install from GitHub
Install skills directly from this repository using the Skills CLI:

```bash
# Install a specific skill from this repository:
npx skills add danicat/skills --skill engineering-flow -y
npx skills add danicat/skills --skill ebitengineer -y
npx skills add danicat/skills --skill skill-optimizer -y

# Install all skills from this repository:
npx skills add danicat/skills -y
```

---

## Skills Catalog

### 🕹️ Game Development (`game-dev/`)
Specialized skills for designing and building 2D games in Go with Ebitengine, chiptune DSP, and procedural generation.

* **[`ebitengineer`](game-dev/ebitengineer/SKILL.md)**: Production-grade 2D game architecture, cycle timing, state machines, shaders, and audio sync for Go & Ebitengine (v2).
* **[`game-design`](game-dev/game-design/SKILL.md)**: Game concept ideation, interactive `/grill-me` design interviews, and Game Design Document (`GDD.md`) generation.
* **[`procedural-art`](game-dev/procedural-art/SKILL.md)**: Pure-code procedural 2D sprites, tilemaps, vector graphics, particle systems, and rasterization algorithms without external assets.
* **[`procedural-composer`](game-dev/procedural-composer/SKILL.md)**: Pure-code procedural audio synthesis, sound effects (SFX), and chiptune/FM sound engine architecture.
* **[`sprite-animation`](game-dev/sprite-animation/SKILL.md)**: 2D sprite sheets, frame durations, tag loops, and Aseprite (`.ase`/`.aseprite`) file validation and slicing.
* **[`vibe-game-developer`](game-dev/vibe-game-developer/SKILL.md)**: Master orchestrator and request router for 2D Go game development, asset pipelines, and WebAssembly deployment.

---

### 🎨 Generative Media (`media/`)
Audio and visual generation using Google AI models with ADC authentication.

* **[`lyria`](media/lyria/SKILL.md)**: High-fidelity 44.1 kHz stereo music and soundtrack generation from text prompts and images using Google's Lyria 3 models.
* **[`nano-banana`](media/nano-banana/SKILL.md)**: Conversational image generation and editing using Google's native Nano Banana models with character consistency support.

---

### 💻 Software Engineering (`coding/`)
Engineering workflow standards, compiler gates, package resolvers, and language-specific tools.

* **[`engineering-flow`](coding/engineering-flow/SKILL.md)**: Engineering workflow standards detailing semantic versioning (with 0.x zero-debt rules), broken window hygiene, RFC/ADR planning, and the 7-tier Evidence Hierarchy.
* **[`godoctor`](coding/godoctor/SKILL.md)**: AST-aware Go developer tooling with automatic compiler rollback gates, Selene mutation testing, and multi-tier test runners.
* **[`latest-version`](coding/latest-version/SKILL.md)**: Real-time package registry and Gemini model version resolver (NPM, PyPI, Go proxy, Cargo, RubyGems).
* **[`pyhd`](coding/pyhd/SKILL.md)**: Modern Python development workflow using `uv` virtual environments, Ruff linting/formatting, and pytest suites.

---

### 🤖 AI Agents (`agents/`)
Frameworks, multi-agent swarm orchestration, and skill authoring tools.

* **[`double-diamond`](agents/double-diamond/SKILL.md)**: Two-phase multi-agent orchestration for complex engineering initiatives separating problem space discovery from solution space implementation with human steering gates.
* **[`skill-optimizer`](agents/skill-optimizer/SKILL.md)**: Meta-skill for authoring, auditing, and optimizing Agent Skills according to the official specification, trigger evaluation, and MCP setup (`https://agentskills.io/mcp`).
* **[`swarm-coding`](agents/swarm-coding/SKILL.md)**: Parallelized multi-agent swarm task decomposition and coordination for complex full-stack features and refactorings.

---

### ✍️ Technical Writing (`writing/`)
Editorial guidelines, Inverted Pyramid hierarchy, AI slop removal, social copy, and developer documentation.

* **[`buffer`](writing/buffer/SKILL.md)**: Manage, draft, schedule, and publish social media content across connected channels using the Buffer CLI.
* **[`deslopify`](writing/deslopify/SKILL.md)**: Re-write, edit, and purge text of common AI tropes, clichés, and formulaic filler using strict editorial guidelines.
* **[`google-blog-style`](writing/google-blog-style/SKILL.md)**: Official style guide and compliance rules for the Google Developers Blog, including Gunning Fog readability and Vale style checks.
* **[`inverted-pyramid`](writing/inverted-pyramid/SKILL.md)**: Action-first, summary-first information hierarchy for technical documentation and developer guides.
* **[`seo-optimizer`](writing/seo-optimizer/SKILL.md)**: Technical SEO and Generative Engine Optimization (GEO) for developer blogs and documentation, including metadata split (summary vs. description), heading hierarchies, and `llms.txt` generation.
* **[`social-copy`](writing/social-copy/SKILL.md)**: Draft, audit, and optimize high-performing technical and developer social media copy across LinkedIn, Twitter/X, Bluesky, Instagram, Reddit, and Threads.

---

### 📊 Data Analytics (`analytics/`)
Raw metrics ingestion and SQLite data warehousing for search performance, web traffic, and social distribution.

* **[`buffer-analytics`](analytics/buffer-analytics/SKILL.md)**: Ingest raw Buffer social post and channel data into a local SQLite analytics database and run SQL queries across LinkedIn, Twitter/X, and Bluesky.
* **[`google-analytics`](analytics/google-analytics/SKILL.md)**: Ingest raw Google Analytics 4 (GA4) traffic, dwell time, localization performance, and outbound clicks into a local SQLite analytics database and run pre-built or ad-hoc SQL reports.
* **[`search-analytics`](analytics/search-analytics/SKILL.md)**: Ingest raw Google Search Console performance metrics into a local SQLite database and execute deep SQL analytics over organic search traffic.

---

### 📐 Engineering Standards (`standards/`)
Decision records, design consensus frameworks, and open-source compliance.

* **[`adr-template`](standards/adr-template/SKILL.md)**: Guidelines, best practices, and templates for authoring immutable Architecture Decision Records (ADRs).
* **[`google-oss`](standards/google-oss/SKILL.md)**: Apply and verify Google open-source compliance, Apache-2.0 license headers via `addlicense`, copyright attributions, and repository disclaimers.
* **[`rfc-template`](standards/rfc-template/SKILL.md)**: Collaborative Request for Comments (RFC) frameworks for exploring major features and complex design alternatives.

---

## Disclaimer

This is not an officially supported Google product.

