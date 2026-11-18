# Agent Skills

A curated collection of specialized skills for AI agents and pair programmers, organized by domain.

---

## Installation

### Install from GitHub
Install skills directly from this repository using `kungfu` or the Skills CLI:

```bash
# Stream or install a specific skill via KungFu:
kungfu load ebitengineer
kungfu learn godoctor

# Install a specific skill via npx skills:
npx skills add danicat/skills --skill godoctor -y
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
* **[`game-design`](game-dev/game-design/SKILL.md)**: Game concept ideation, structured design interviews, and Game Design Document (`GDD.md`) generation.
* **[`procedural-music`](game-dev/procedural-music/SKILL.md)**: Original game soundtrack composition and dual-engine `.music` DSL (pure-Go YM2612 FM + SN76489 PSG or macOS CoreAudio `-apple`) with music-theory validation.
* **[`procedural-sfx`](game-dev/procedural-sfx/SKILL.md)**: Pure-code procedural SFX DSL and PolyBLEP/LFSR/SVF/FM sound synthesis engine producing 4-byte aligned `44.1 kHz` stereo PCM cues.
* **[`sprite-design`](game-dev/sprite-design/SKILL.md)**: Unified `.sprite` container and procedural SDF engine, two-step AI sprite normalization, binary `.aseprite` export, visual QA, and zero-allocation `AnimationController` playback.
* **[`vibe-game-developer`](game-dev/vibe-game-developer/SKILL.md)**: Master orchestrator and request router for 2D Go game development, asset pipelines, and WebAssembly deployment.

---

### 🎨 GenAI (`media/`)
Audio, image, and video generation using Google AI models via bundled `uv run` scripts and Google Gen AI SDKs.

* **[`gemini-omni`](media/gemini-omni/SKILL.md)**: Conversational video generation, multimodal video editing, frame interpolation, video extension, and video upscaling using Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`).
* **[`lyria`](media/lyria/SKILL.md)**: High-fidelity 44.1 kHz stereo music and soundtrack generation from text prompts and images using Google's Lyria 3.5 and Lyria 3 models.
* **[`nano-banana`](media/nano-banana/SKILL.md)**: Conversational image generation and multimodal editing using Google's Nano Banana 2.1 and Pro models with multi-reference character consistency.

---

### 💻 Engineering (`coding/`)
Compiler gates, architectural decision records, and language-specific tools.

* **[`design-docs`](coding/design-docs/SKILL.md)**: Author and manage collaborative Request for Comments (RFC) proposals and immutable Architecture Decision Records (ADRs) across `design/rfc/` and `design/adr/`.
* **[`godoctor`](coding/godoctor/SKILL.md)**: Go developer tooling and static analysis orchestrator with automatic compiler rollback gates, Selene mutation testing, and TestQuery analytics.
* **[`google-oss`](coding/google-oss/SKILL.md)**: Apply and verify Google open-source compliance, Apache-2.0 license headers via `addlicense`, copyright attributions, and repository disclaimers.

---

### 🔄 Workflows (`workflows/`)
Multi-agent swarm orchestration, evidence-first discovery, divergent ideation, philosophical abstraction, Agile spikes, radical simplification, and skill authoring workflows.

* **[`abstract`](workflows/abstract/SKILL.md)**: Philosophical and inductive knowledge-distillation workflow that extracts general principles, causal laws, and portable concepts from concrete facts, evidence, and examples using Aristotle's essence-versus-accident split, Bacon's inductive ascent, Peirce's concept naming, and Popper's flip test.
* **[`brainstorm`](workflows/brainstorm/SKILL.md)**: Divergent ideation and option-generation engine that breaks LLM mode collapse using symmetry-breaking algorithms (taboo deflection, assumption flips, tension breaking, cross-domain transfer, and testable bets) and same-prompt parallel dispatch (`brainstorm(N)`) with Map-Reduce synthesis.
* **[`discovery`](workflows/discovery/SKILL.md)**: Evidence-first fact-finding and source-grounding workflow that investigates technical, business, or cultural problem spaces, maps empirical findings across a 6-tier proof hierarchy (`[T1]` to `[T6]`), and surfaces unknowns before planning or action.
* **[`double-diamond`](workflows/double-diamond/SKILL.md)**: Two-phase multi-agent orchestration for complex engineering initiatives separating problem space discovery from solution space implementation with human steering gates.
* **[`intercom`](workflows/intercom/SKILL.md)**: Cross-project and cross-session collaboration between Antigravity agents using the `agentapi` CLI and `conversation_summaries.db`, with active session discovery, target project routing, and return-address headers.
* **[`less-is-more`](workflows/less-is-more/SKILL.md)**: Life and craft philosophy for focusing on what matters and doing the essential things well instead of doing everything in a mediocre way. Inspired by MasterChef plating discipline, honoring the hero ingredient and executing 1 to 3 core elements with care across product choices, writing, architecture, and frontend interfaces.
* **[`parallel`](workflows/parallel/SKILL.md)**: General-purpose task parallelization and agent scaling engine across concurrent subagents.
* **[`show-me-the-money`](workflows/show-me-the-money/SKILL.md)**: Mine local conversation history, brain artifacts, and full session transcripts using parallel `flash` and `flash_lite` subagents and `run_workflow` scripts to recover high-value features lost to conversation drift or abandonment without burning frontier model quota.
* **[`skill-optimizer`](workflows/skill-optimizer/SKILL.md)**: Meta-skill for authoring, auditing, and optimizing Agent Skills according to the official specification, trigger evaluation, and MCP setup (`https://agentskills.io/mcp`).
* **[`spike`](workflows/spike/SKILL.md)**: Pragmatic Agile spike workflow for retiring technical, design, or functional risk before committing to implementation or estimates using spec/source audits, blast-radius traces, state-table walk-throughs, and throwaway probes.
* **[`swarm-coding`](workflows/swarm-coding/SKILL.md)**: Parallelized multi-agent swarm task decomposition and coordination for complex full-stack features and refactorings.
* **[`uno-reverse`](workflows/uno-reverse/SKILL.md)**: Radical simplification, red-teaming, and Occam's Razor devil's advocate for software architecture, PRDs, agent workflows, and technical designs.

---

### ✍️ Writing (`writing/`)
Editorial guidelines, Inverted Pyramid hierarchy, AI slop removal, social copy, and developer documentation.

* **[`buffer`](writing/buffer/SKILL.md)**: Manage, draft, schedule, and publish social media content across connected channels using the Buffer CLI.
* **[`deslopify`](writing/deslopify/SKILL.md)**: Re-write, edit, and purge text of common AI tropes, clichés, and formulaic filler using strict editorial guidelines.
* **[`inverted-pyramid`](writing/inverted-pyramid/SKILL.md)**: Action-first, summary-first information hierarchy for technical documentation and developer guides.
* **[`seo-optimizer`](writing/seo-optimizer/SKILL.md)**: Technical SEO and Generative Engine Optimization (GEO) for developer blogs and documentation, including metadata split (summary vs. description), heading hierarchies, and `llms.txt` generation.
* **[`social-copy`](writing/social-copy/SKILL.md)**: Draft, audit, and optimize high-performing technical and developer social media copy across LinkedIn, Twitter/X, Bluesky, Instagram, Reddit, and Threads.

---

### 📊 Analytics (`analytics/`)
Raw metrics ingestion and SQLite data warehousing for search performance, web traffic, and social distribution.

* **[`buffer-analytics`](analytics/buffer-analytics/SKILL.md)**: Ingest raw Buffer social post and channel data into a local SQLite analytics database and run SQL queries across LinkedIn, Twitter/X, and Bluesky.
* **[`google-analytics`](analytics/google-analytics/SKILL.md)**: Ingest raw Google Analytics 4 (GA4) traffic, dwell time, localization performance, and outbound clicks into a local SQLite analytics database and run pre-built or ad-hoc SQL reports.
* **[`pagespeed-insights`](analytics/pagespeed-insights/SKILL.md)**: Run, extract, and debug Mobile and Desktop Lighthouse audits and 28-day CrUX field Core Web Vitals (`LCP`, `INP`, `CLS`) via the PageSpeed Insights v5 API (`curl` + `jq`) or Chrome DevTools MCP without DOM snapshot bloat.
* **[`search-analytics`](analytics/search-analytics/SKILL.md)**: Ingest raw Google Search Console performance metrics into a local SQLite database and execute deep SQL analytics over organic search traffic.
* **[`skill-analytics`](analytics/skill-analytics/SKILL.md)**: Mine Agent Skill usage, prompt-tax and cache-adjusted ROI, and trigger attribution from conversation transcripts into a local SQLite database across all installed skill tiers.

---

## Freshness

Every skill in [skills.danicat.dev](https://skills.danicat.dev/freshness/) receives a 0% to 100% freshness score calculated directly from substantive Git commits in its folder, using a 30-day grace window at 100% followed by a 90-day half-life across **Current** (`85-100%`), **Active** (`60-84%`), **Aging** (`35-59%`), and **Outdated** (`0-34%`).

## Graveyard

Retired skills live in the **[Graveyard](https://skills.danicat.dev/graveyard/)**:

| Skill | Lifespan | Why It Was Killed | Replacement | Command |
| :--- | :--- | :--- | :--- | :--- |
| `go-best-practices` | Feb 14 - Feb 16, 2026 | Merged into `godoctor` | [`godoctor`](coding/godoctor/SKILL.md) | `kungfu forget go-best-practices && kungfu learn godoctor` |
| `go-project-setup` | Feb 14 - Feb 16, 2026 | Merged into `godoctor` | [`godoctor`](coding/godoctor/SKILL.md) | `kungfu forget go-project-setup && kungfu learn godoctor` |
| `a2ui-developer-guide` | Feb 14 - Feb 21, 2026 | Factually incorrect (produced botched implementations) | None | `kungfu forget a2ui-developer-guide` |
| `find-examples` | Feb 14 - Mar 14, 2026 | Never used in real life | None | `kungfu forget find-examples` |
| `google-codelab-authoring` | Feb 14 - Mar 19, 2026 | Never used in real life | None | `kungfu forget google-codelab-authoring` |
| `agy-extensions` | Mar 23 - Mar 26, 2026 | Replaced by official `agy-customizations` skill | `agy-customizations` | `kungfu forget agy-extensions` |
| `experiment-analyst` | Mar 15 - Apr 7, 2026 | Niche analysis skill not meant for general use | None | `kungfu forget experiment-analyst` |
| `catalog` | Feb 14 - Apr 2026 | Unnecessary; replaced by `kungfu list` and `kungfu find` | `kungfu list` / `kungfu find` | `kungfu forget catalog` |
| `google-blog-style` | Feb 2026 - Nov 2026 | Never used in real life | None | `kungfu forget google-blog-style` |
| `veo` | Oct 2026 - Nov 2026 | Model deprecated in favor of `gemini-omni` | [`gemini-omni`](media/gemini-omni/SKILL.md) | `kungfu forget veo && kungfu learn gemini-omni` |
| `router` | Nov 2026 | Replaced by built-in Orchestrator | Orchestrator (built-in) | `kungfu forget router` |
| `latest-version` | Feb 2026 - Nov 2026 | Obsolete | None | `kungfu forget latest-version` |
| `engineering-flow` | Aug 2026 - Nov 2026 | Superseded by dedicated workflow skills | [`discovery`](workflows/discovery/SKILL.md), [`spike`](workflows/spike/SKILL.md), [`less-is-more`](workflows/less-is-more/SKILL.md) | `kungfu forget engineering-flow` |
| `adr-template` | Jul 2026 - Nov 2026 | Merged into `design-docs` | [`design-docs`](coding/design-docs/SKILL.md) | `kungfu forget adr-template && kungfu learn design-docs` |
| `rfc-template` | Jul 2026 - Nov 2026 | Merged into `design-docs` | [`design-docs`](coding/design-docs/SKILL.md) | `kungfu forget rfc-template && kungfu learn design-docs` |
| `pyhd` | Feb 2026 - Nov 2026 | Obsolete | None | `kungfu forget pyhd` |
| `procedural-art` | Aug 2026 - Nov 2026 | Consolidated into `sprite-design` | [`sprite-design`](game-dev/sprite-design/SKILL.md) | `kungfu forget procedural-art && kungfu learn sprite-design` |
| `sprite-animation` | Aug 2026 - Nov 2026 | Consolidated into `sprite-design` | [`sprite-design`](game-dev/sprite-design/SKILL.md) | `kungfu forget sprite-animation && kungfu learn sprite-design` |
| `procedural-composer` | Aug 2026 - Nov 2026 | Split into `procedural-sfx` and `procedural-music` | [`procedural-sfx`](game-dev/procedural-sfx/SKILL.md), [`procedural-music`](game-dev/procedural-music/SKILL.md) | `kungfu forget procedural-composer && kungfu learn procedural-sfx && kungfu learn procedural-music` |

---

## Disclaimer

This is not an officially supported Google product.
