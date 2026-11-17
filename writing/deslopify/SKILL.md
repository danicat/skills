---
name: deslopify
description: >
  Editorial guide and rewriting workflow for removing AI cliches, tropes, and
  formulaic filler from prose. Flags overused vocabulary (such as delve,
  tapestry, seamlessly), negative parallelism, dramatic countdowns, reasoning
  throat-clearing, and fractal summaries while preserving the author's voice.
  Activate when auditing prose for AI tells or polishing drafts to read naturally.
license: Apache-2.0
metadata:
  category: writing
  tags: "copyediting, prose, tropes, readability, voice"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Deslopify: AI slop and trope removal

Remove recognizable Large Language Model (LLM) structural habits, inflated vocabulary, and formulaic filler so technical writing reads like a real engineer speaking to peers.

---

## 1. Operating modes and voice preservation

- **Review mode (default for existing drafts)**: Never rewrite or mutate user text on disk silently. Scan the draft and return a numbered, line-indexed list of concrete recommendations:
  `- [N] Line <N> | Trope: <Category> | Excerpt: "<exact quote>" | Suggestion: "<concrete rewrite>"`
  Wait for explicit user approval (`"apply all"`, `"apply 1, 3"`, `"discuss 2"`, or `"reject"`) before modifying files.
- **Rewrite mode (new drafts or explicit permission)**: Apply the four-stage workflow directly when generating new prose or when the user explicitly asks to rewrite or clean up a file in place.
- **Preserve authentic author voice**: Cutting AI slop never means sterilizing human personality. Keep the author's natural cadence, contractions, direct opinions, exclamation marks, and casual idioms (such as `"pretty cool"` or `"TL;DR"`). Never swap informal human turns of phrase for stiff corporate synonyms.

---

## 2. Quick reference of AI tells

Read [references/tropes.md](references/tropes.md) for the full catalog of lexical, structural, and tonal tells.

| Category | Overused AI pattern | Direct human alternative |
| :--- | :--- | :--- |
| **Magic adverbs** | *quietly*, *deeply*, *fundamentally*, *remarkably*, *arguably* | Cut the adverb or replace it with a measured metric or concrete fact. |
| **Pompous vocabulary** | *delve*, *tapestry*, *landscape*, *robust*, *seamless*, *leverage*, *harness*, *testament* | Use plain words: *inspect*, *system*, *reliable*, *fast*, *use*. |
| **Copula dodges** | *serves as a reminder*, *stands as a testament*, *marks a pivotal moment* | Use direct verbs: *is*, *shows*, *routes*, *started in*. |
| **Negative parallelism** | *"It's not X, it's Y."* *"Not because X, but because Y."* | State what the thing is without staging a theatrical contrast. |
| **Dramatic countdowns** | *"Not a bug. Not a feature. A design flaw."* | Combine into one plain sentence: *"This is a design flaw."* |
| **Self-answering questions** | *"The result? Devastating."* *"The catch? Latency doubled."* | State cause and effect directly: *"Latency doubled under load."* |
| **Filler transitions** | *It's worth noting that*, *Importantly*, *Notably* | Cut the opener and state the fact right away. |
| **Pedagogical signposting** | *Let's break this down*, *Here's the kicker*, *Think of it as* | Drop teacher-mode buildup and address the reader as a peer. |
| **Reasoning throat-clearing** | *Let's carefully consider*, *Upon closer inspection*, *At its core*, *When it comes to* | Cut leaked thinking preambles and start with the claim. |
| **Symmetric fence-sitting** | *"While both approaches have merits, the right choice depends on your use case."* | Name the concrete threshold or constraint that decides between them. |
| **Colon-pivot headlines** | *"Beyond X: How Y Redefines Z"* or *"From Hype to Production: Scaling X"* | Write a literal title stating the technical subject or result. |
| **Fractal summaries** | Ending every subsection with *"In summary, this step showed X"* | Delete section recaps and end on the last concrete point. |

---

## 3. Before and after engineering rewrites

| Anti-pattern | Raw AI draft | Human engineering rewrite | Editorial fix |
| :--- | :--- | :--- | :--- |
| **Pompous vocabulary and adverbs** | *"The system quietly leverages a robust pipeline to seamlessly deliver throughput across the distributed landscape."* | *"The distributed pipeline processes `50,000` requests per second."* | Cut buzzwords (*quietly*, *leverages*, *robust*, *seamlessly*, *landscape*) and added a concrete rate. |
| **Negative parallelism and drama** | *"It's not just a cache, it's a complete rewrite of state. The result? Instant queries."* | *"Keeping index pages in memory cut query latency from `80ms` to `2ms`."* | Removed theatrical contrast and self-answering Q&A; stated the measured change. |
| **Dramatic countdown** | *"Not a slow disk. Not network jitter. A deadlock in the connection pool."* | *"A connection pool deadlock stalled all worker threads."* | Dropped faux suspense and named the root cause first. |
| **Reasoning throat-clearing** | *"When it comes to connection management, let's carefully consider why pool sizing matters at its core."* | *"Sizing the connection pool above CPU core count increases lock contention."* | Removed leaked reasoning filler and stated the mechanism. |
| **Superficial participle tail** | *"We enabled HTTP/3, highlighting our forward-looking design and underscoring our commitment to speed."* | *"Enabling HTTP/3 removed head-of-line blocking during packet loss."* | Cut hollow puffery (*highlighting*, *underscoring*) and named the transport gain. |
| **Symmetric fence-sitting** | *"While both SQLite and PostgreSQL have merits, the optimal choice depends on your specific requirements."* | *"Use SQLite for single-node workloads under `5,000` writes per second; switch to PostgreSQL when multiple writers share state."* | Replaced vague hedge with a concrete decision boundary. |

---

## 4. Four-stage editing workflow

```mermaid
flowchart LR
    A["1. Scan and tag tells"] --> B["2. Strip AI scaffolding"]
    B --> C["3. Write active specifics"]
    C --> D["4. Check voice and rhythm"]
```

### Stage 1: Scan and tag tells
- Check the draft against [references/tropes.md](references/tropes.md).
- Flag magic adverbs, pompous nouns and verbs, copula dodges, negative parallelism, rhetorical Q&A, reasoning throat-clearing, and fence-sitting conclusions.

### Stage 2: Strip AI scaffolding
- **Fractal and signposted summaries**: Delete intermediate sub-conclusions and formulaic closers (*In conclusion*, *Wrapping up*, *The bottom line*).
- **Bold-first bullet walls (by document type)**: In narrative essays, blog posts, and social copy, turn mechanical bold-lead bullet walls into connected paragraphs. Keep concise bold-lead items or Markdown tables in `README.md` files, API specs, CLI references, and changelogs where readers scan by key.
- **Zero em dashes**: Remove all mid-sentence em dashes, en dashes, and spaced double hyphens. Break clauses with periods, commas, colons, or parentheses.

### Stage 3: Write active specifics
- Replace inflated verbs and abstract labels with plain active verbs and concrete nouns.
- State the outcome upfront instead of holding back conclusions for a dramatic reveal.
- Replace vague praise (*"an extraordinarily fast mechanism"*) with verifiable numbers (*"finishes in `5ms` on one core"*).

### Stage 4: Check voice and rhythm
- Mix long explanatory sentences with short direct sentences so paragraphs do not march in uniform `15`-word beats.
- Break back-to-back rule-of-three triplets.
- Confirm the result still sounds like the human author rather than a sanitized press release.
