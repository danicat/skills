---
name: deslopify
description: >
  Re-write, edit, and purge text of common AI tropes, clichés, formulaic filler,
  and recognizable large language model structural patterns (AI slop) using
  strict editorial guidelines. Activate this skill whenever the user asks to
  "deslopify" text, remove AI tells, polish text to sound authentically human,
  eliminate formulaic transitions (e.g. "delve", "testament", "tapestry",
  "seamlessly"), fix negative parallelism, or audit prose for AI idioms.
license: Apache-2.0
metadata:
  category: writing
  tags: "writing, deslopify, editorial, tropes, ai-cleanup, style, prose"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  homepage: https://skills.danicat.dev/writing/deslopify/
  canonical: https://skills.danicat.dev/writing/deslopify/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/writing/deslopify
---

# Deslopify: AI Slop & Trope Removal

Procedures, editorial standards, and de-slopification workflows for purging text of recognizable Large Language Model (LLM) structural patterns, formulaic clichés, and conversational tropes to make technical writing sound authentically human, grounded, and engaging.

---

## 📖 Reference Catalog of AI Tells

Read [`references/tropes.md`](references/tropes.md) for the exhaustive catalog of AI tells, syntactic anti-patterns, and overused vocabulary.

### Quick Reference: Common AI Tells & Alternatives

| Category | Overused AI Pattern | Human-Sounding Alternative |
| :--- | :--- | :--- |
| **Magic Adverbs** | *quietly*, *deeply*, *fundamentally*, *remarkably*, *arguably* | Cut entirely or replace with concrete metrics and verified facts. |
| **Pompous Vocabulary** | *delve*, *tapestry*, *landscape*, *robust*, *seamless*, *leverage*, *harness*, *testament* | Use simple, concrete words: *explore*, *look at*, *system*, *reliable*, *fast*, *use*. |
| **The "Serves As" Dodge** | *serves as a reminder*, *stands as a testament*, *marks a pivotal moment* | Use direct copulas: *is*, *reminds us*, *shows*, *was built in*. |
| **Negative Parallelism** | *"It's not X — it's Y"*, *"Not because X, but because Y"* | State the point directly without staging a theatrical contradiction. |
| **Dramatic Countdowns** | *"Not a bug. Not a feature. A design flaw."* | Combine into a single direct statement: *"This is a design flaw."* |
| **Self-Answering Rhetoric** | *"The result? Devastating."*, *"The scary part? Nobody noticed."* | State facts without self-answering drama: *"Nobody noticed the failure."* |
| **Filler Transitions** | *"It's worth noting that..."*, *"Importantly..."*, *"Notably..."* | Cut the preamble. If it's worth noting, state the fact directly. |
| **Pedagogical Tones** | *"Let's break this down"*, *"Here's the thing"*, *"Here's the kicker"* | Eliminate teacher-mode signposting; present the evidence directly. |
| **Fractal Summaries** | Summarizing every section at the end of the section | Let the section content speak for itself; eliminate redundant sub-conclusions. |

---

## ⚡ 4-Stage Deslopification Workflow

Follow this procedure when reviewing or rewriting any text:

```mermaid
graph LR
    A[1. Scan & Tag Tells] --> B[2. Deconstruct AI Structure]
    B --> C[3. Direct Active Rewrite]
    C --> D[4. Cadence & Rhythm Audit]
```

### 1. Stage 1: Scan & Tag Tells
- Scan the input text against the patterns in [`references/tropes.md`](references/tropes.md).
- Tag every occurrence of:
  - Magic adverbs (*quietly*, *deeply*, *fundamentally*).
  - Pompous vocabulary (*delve*, *tapestry*, *landscape*, *robust*, *seamless*).
  - Rhetorical questions and false suspense (*The catch?*, *Here's the kicker*).
  - Negative parallelism (*It's not just X, it's Y*).

### 2. Stage 2: Deconstruct AI Structure
- Strip out formulaic LLM structures:
  - **Fractal summaries**: Remove repetitive summaries under every heading.
  - **Signposted conclusions**: Replace "In conclusion", "Wrapping up", and "The bottom line" with natural conclusions or concrete next steps.
  - **Bold-first bullet fatigue**: Convert long lists of bold-leaded pseudo-bullets into connected, narrative paragraphs where appropriate.
  - **Excessive em-dashes**: Limit em-dashes to at most one per page; use parentheses, commas, or separate sentences instead.

### 3. Stage 3: Direct Active Rewrite
- **Replace inflated vocabulary**: Simplify grandiose descriptors to plain, active verbs and concrete nouns.
- **Break formulaic symmetry**: Vary sentence lengths dramatically. Follow a long, nuanced sentence with a short, punchy one.
- **Remove false suspense**: State the takeaway upfront (Inverted Pyramid style) rather than holding back information for a staged reveal.
- **Ground claims in specifics**: Replace vague hype (*"provides an incredibly powerful mechanism"*) with concrete technical specifics (*"executes within 5ms on a single core"*).

### 4. Stage 4: Cadence & Rhythm Audit
- Read the final draft to verify:
  - Does it sound like a knowledgeable human engineer speaking with a peer?
  - Are there any lingering rule-of-three triplets (tricolons)?
  - Is the tone authentic, conversational, and grounded in real-world nuance?
