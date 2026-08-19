# Agent Skills Collection

A curated collection of specialized skills for AI agents and pair programmers, organized by domain.

---

## Installation

### Install from GitHub
Install skills directly from this repository using the Skills CLI:

```bash
# Install a specific skill by category path:
npx skills install github.com/danicat/skills/coding/engineering-flow
npx skills install github.com/danicat/skills/game-dev/ebitengineer
npx skills install github.com/danicat/skills/agents/skill-optimizer

# Install an entire repository or category:
npx skills install github.com/danicat/skills
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

### 💻 Coding & Development (`coding/`)
Engineering workflow standards, compiler gates, package resolvers, and language-specific tools.

* **[`engineering-flow`](coding/engineering-flow/SKILL.md)**: Engineering workflow standards detailing semantic versioning (with 0.x zero-debt rules), broken window hygiene, RFC/ADR planning, and the 7-tier Evidence Hierarchy.
* **[`find-examples`](coding/find-examples/SKILL.md)**: Real-world code search and GitHub example extraction with strict workspace isolation and sandbox rules.
* **[`godoctor`](coding/godoctor/SKILL.md)**: AST-aware Go developer tooling with automatic compiler rollback gates, Selene mutation testing, and multi-tier test runners.
* **[`latest-version`](coding/latest-version/SKILL.md)**: Real-time package registry and Gemini model version resolver (NPM, PyPI, Go proxy, Cargo, RubyGems).
* **[`pyhd`](coding/pyhd/SKILL.md)**: Modern Python development workflow using `uv` virtual environments, Ruff linting/formatting, and pytest suites.

---

### 🤖 Agents & Meta-Tooling (`agents/`)
Frameworks, UI streaming protocols, swarm orchestration, and skill authoring tools.

* **[`a2ui-developer-guide`](agents/a2ui-developer-guide/SKILL.md)**: Comprehensive guide for the Agent-Driven User Interface (A2UI) streaming protocol, specifications, and component catalog validations.
* **[`double-diamond`](agents/double-diamond/SKILL.md)**: Two-phase multi-agent orchestration for complex engineering initiatives separating problem space discovery from solution space implementation with human steering gates.
* **[`skill-optimizer`](agents/skill-optimizer/SKILL.md)**: Meta-skill for authoring, auditing, and optimizing Agent Skills according to the official specification, trigger evaluation, and MCP setup (`https://agentskills.io/mcp`).
* **[`swarm-coding`](agents/swarm-coding/SKILL.md)**: Parallelized multi-agent swarm task decomposition and coordination for complex full-stack features and refactorings.

---

### ✍️ Technical Writing & Publishing (`writing/`)
Editorial guidelines, analytics data warehousing, social copy engineering, and developer tutorial authoring.

* **[`buffer`](writing/buffer/SKILL.md)**: Manage, draft, schedule, and publish social media content across connected channels using the Buffer CLI.
* **[`buffer-analytics`](writing/buffer-analytics/SKILL.md)**: Ingest raw Buffer social post and channel data into a local SQLite analytics database and run SQL queries across LinkedIn, Twitter/X, and Bluesky.
* **[`google-analytics`](writing/google-analytics/SKILL.md)**: Ingest raw Google Analytics 4 (GA4) traffic, dwell time, localization performance, and outbound clicks into a local SQLite analytics database and run pre-built or ad-hoc SQL reports.
* **[`google-blog-style`](writing/google-blog-style/SKILL.md)**: Official style guide and compliance rules for the Google Developers Blog, including Gunning Fog readability and Vale style checks.
* **[`google-codelab-authoring`](writing/google-codelab-authoring/SKILL.md)**: Step-by-step developer tutorial authoring in Google Codelabs format (`.lab.md`) with Claat metadata and aside block validation.
* **[`search-analytics`](writing/search-analytics/SKILL.md)**: Ingest raw Google Search Console performance metrics into a local SQLite database and execute deep SQL analytics over organic search traffic.
* **[`seo-optimizer`](writing/seo-optimizer/SKILL.md)**: Technical SEO and Generative Engine Optimization (GEO) for developer blogs and documentation, including metadata split (summary vs. description), heading hierarchies, and `llms.txt` generation.
* **[`social-copy`](writing/social-copy/SKILL.md)**: Draft, audit, and optimize high-performing technical and developer social media copy across LinkedIn, Twitter/X, Bluesky, Instagram, Reddit, and Threads.

---

### 📐 Engineering Standards (`standards/`)
Decision records and design consensus frameworks.

* **[`adr-template`](standards/adr-template/SKILL.md)**: Guidelines, best practices, and templates for authoring immutable Architecture Decision Records (ADRs).
* **[`rfc-template`](standards/rfc-template/SKILL.md)**: Collaborative Request for Comments (RFC) frameworks for exploring major features and complex design alternatives.
