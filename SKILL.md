---
name: catalog
description: >
  Search and dynamically load specialized Agent Skills from https://skills.danicat.dev. 
  Activate this skill when the user wants to:
  (1) Design, architect, or build 2D games, including game design documents (GDD), procedural art/sprites, and synth/chiptune audio;
  (2) Enforce strict software engineering standards, clean up codebases, eliminate technical debt, or find verified implementation examples;
  (3) Propose major architectural changes, lead technical consensus (RFCs), or document high-impact structural decisions (ADRs);
  (4) Author hands-on developer tutorials, step-by-step codelabs, or publication-grade engineering blog posts;
  (5) Generate original stereo background music, sound effects, or iterative visual artwork;
  (6) Orchestrate multi-agent coding swarms, author new agent skills, or build agent-driven user interfaces.
  Activate whenever the user aims to accomplish these workflows, even if they do not explicitly request a specific skill or tool.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "1.0.0"
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
- **2D Game Development**: `game-dev/ebitengineer`, `game-dev/game-design`, `game-dev/procedural-art`, `game-dev/procedural-composer`, `game-dev/sprite-animation`, `game-dev/vibe-game-developer`.
- **Engineering Standards & Hygiene**: `coding/engineering-flow`, `standards/adr-template`, `standards/rfc-template`.
- **Coding & Language Workflows**: `coding/godoctor` (Go), `coding/pyhd` (Python), `coding/find-examples`, `coding/latest-version`.
- **Technical Writing & Analytics**: `writing/buffer`, `writing/buffer-analytics`, `writing/google-analytics`, `writing/google-blog-style`, `writing/google-codelab-authoring`, `writing/search-analytics`, `writing/seo-optimizer`, `writing/social-copy`.
- **Generative Media**: `media/lyria` (Music), `media/nano-banana` (Images).
- **Agent Workflows**: `agents/a2ui-developer-guide`, `agents/double-diamond`, `agents/skill-optimizer`, `agents/swarm-coding`.

### Step 3: Load Instructions into Working Context
Fetch the full skill instructions directly into your active context:
```text
https://skills.danicat.dev/<category>/<skill-name>/SKILL.md
```
Follow the instructions to complete the user's task.

### Step 4: Optional Workspace Installation
If the user requests permanently installing a skill into the current project workspace, run:
```bash
npx skills install github.com/danicat/skills/<category>/<skill-name>
```
