---
name: catalog
description: >
  Search and dynamically load specialized Agent Skills from https://skills.danicat.dev.
  Activate this skill when the user wants to:
  (1) Design, architect, or build 2D games, including game design documents (GDD), procedural art/sprites, and synth/chiptune audio;
  (2) Enforce strict software engineering standards, clean up codebases, eliminate technical debt, or manage dependencies;
  (3) Propose major architectural changes, lead technical consensus (RFCs), or document high-impact structural decisions (ADRs);
  (4) Author developer documentation, SEO/GEO-optimized articles, or publication-grade engineering blog posts;
  (5) Generate original stereo background music, sound effects, or iterative visual artwork;
  (6) Orchestrate multi-agent coding swarms or author and optimize agent skills.
  Activate whenever the user aims to accomplish these workflows, even if they do not explicitly request a specific skill or tool.
license: Apache-2.0
metadata:
  category: gateway
  tags: "gateway, discovery, search, agent-skills"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "1.0.0"
  homepage: https://skills.danicat.dev/
  canonical: https://skills.danicat.dev/SKILL.md
  repository: https://github.com/danicat/skills
---

# Agent Skills Catalog Gateway

This skill dynamically discovers, fetches, and activates specialized skills from the official catalog at [skills.danicat.dev](https://skills.danicat.dev).

---

## Dynamic Activation Workflow

Follow this procedure to activate the appropriate skill for the user's task:

### Step 1: Query the Live Index
Fetch the compact LLM discovery index:
```text
https://skills.danicat.dev/llms.txt
```
*(Or fetch `https://skills.danicat.dev/catalog.json` for machine-readable JSON)*.

### Step 2: Match User Intent to a Domain Skill
Locate the specific skill matching the user's goal:
- **Game Development**: `game-dev/ebitengineer`, `game-dev/game-design`, `game-dev/procedural-art`, `game-dev/procedural-composer`, `game-dev/sprite-animation`, `game-dev/vibe-game-developer`.
- **Generative Media**: `media/lyria`, `media/nano-banana`.
- **Software Engineering**: `coding/engineering-flow`, `coding/godoctor`, `coding/latest-version`, `coding/pyhd`.
- **AI Agents**: `agents/double-diamond`, `agents/skill-optimizer`, `agents/swarm-coding`.
- **Technical Writing**: `writing/buffer`, `writing/deslopify`, `writing/google-blog-style`, `writing/inverted-pyramid`, `writing/seo-optimizer`, `writing/social-copy`.
- **Data Analytics**: `analytics/buffer-analytics`, `analytics/google-analytics`, `analytics/search-analytics`.
- **Engineering Standards**: `standards/adr-template`, `standards/google-oss`, `standards/rfc-template`.

### Step 3: Load Instructions into Working Context
Fetch the full skill instructions directly into your active context:
```text
https://skills.danicat.dev/<category>/<skill-name>/SKILL.md
```
Follow the instructions to complete the user's task.

### Step 4: Optional Workspace Installation
If the user requests permanently installing a skill into the current project workspace, run:
```bash
npx skills add danicat/skills --skill <skill-name> -y
```
