---
name: discovery
description: >
  Scientific and procedural problem-space exploration workflow that widens the
  investigative aperture across any domain to surface blind spots, hidden
  constraints, overlooked outliers, and unknown unknowns before narrowing on a
  choice. Frames and quantifies findings using a 6-tier evidence hierarchy.
  Activate when exploring a problem space, investigating systems or markets,
  hunting for hidden gems, or uncovering what an initial framing missed.
license: Apache-2.0
metadata:
  category: workflows
  tags: "discovery, exploration, divergence, problem-space, evidence, research"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Discovery problem-space expansion

When given a goal, agents often lock onto the literal words of a prompt and rush toward the first obvious answer. In software, that tunnel vision misses hidden coupling and edge cases. In business, research, or media curation, it recycles common clichés and misses high-value outliers.

`discovery` is a **scientific, divergent step that amplifies the problem space**. You might be mapping a software system, scouting business leads, or hunting for forgotten retro gaming gems and niche anime. In every case, widen the lens first. Rank your proof by source quality, and surface what the first framing missed.

---

## 🔒 Core rules

1. **Diverge before narrowing**:
   Don't jump into building, running code, or picking a single winner during discovery. Expand the search space first so you see the full board before narrowing down.
2. **Look beyond the literal prompt**:
   Treat the first request as a starting point, not the boundary. Hunt for blind spots, adjacent links, second-order effects, and unasked questions.
3. **Read-only exploration**:
   Keep discovery strictly observational. When exploring a project workspace, use read-only checks and leave all tracked files untouched.
4. **Rank and count every claim**:
   Tag every found item with its **Proof Tier (`[T1]` to `[T6]`)** and a source link. This shows the user how much of the map rests on hard facts versus open leads.

---

## ⚖️ Proof hierarchy and scoring

Don't treat all sources as equal. Frame, tag, and count every found item using this 6-tier hierarchy:

```text
[T1] Primary Artifact & Direct Observation (highest authority)
  └── [T2] Canonical Specs, Official Records & Primary Data
        └── [T3] Peer-Reviewed Studies, Benchmarks & Domain Experts
              └── [T4] Curated Community Consensus & Field Reports
                    └── [T5] Anecdotal Signals & Social Media (unverified — cross-check first)
                          └── [T6] Unbacked Hype, Rumors, or Stale Claims (flag or discard)
```

### Cross-domain tier examples

| Tier | Software and systems | Business and market research | Culture, media, and retro gems |
| :--- | :--- | :--- | :--- |
| **`[T1]`** | Source code, live traces, settings files. | Financial filings, raw sales logs, user interviews. | Original hardware or media, credits, playable builds. |
| **`[T2]`** | Official docs, specs, schemas, release notes. | Census data, market standards, patent filings. | Official catalogs, studio archives, print press. |
| **`[T3]`** | Independent benchmarks, security audits. | Analyst breakdowns, tested case studies. | Historian deep dives, specialist critics. |
| **`[T4]`** | Issue trackers, postmortems, practitioner blogs. | Verified buyer reviews, operator forums. | Fan databases, translation logs, niche wikis. |
| **`[T5]`** | Unverified chat threads or social posts. | Social buzz, single founder stories. | Passing forum mentions, nostalgia threads. |
| **`[T6]`** | Outdated blog posts for fast-moving tools. | Unbacked pitch claims, hype posts. | Rumors, wrongly credited works, generic top-10 lists. |

### Source age rules
- **Fast-moving domains**: For software libraries, AI models, or live pricing, drop `[T4]` to `[T5]` posts older than 3 to 6 months when interfaces or market terms have changed.
- **Archival or timeless domains**: For retro games, anime history, or math, period reviews, release catalogs, and historian essays keep full `[T1]` to `[T3]` weight regardless of age.

---

## 🔭 The 5 discovery angles

Sweep the problem space across five outward-looking angles. You can inspect these one by one or fan them out across parallel research subagents:

| Angle | Core question | What it uncovers |
| :--- | :--- | :--- |
| **1. Baseline state** | *What exists today, what's already known, and how does the system, market, or catalog work?* | Replaces guesses with `[T1]` to `[T2]` facts. |
| **2. Hidden assumptions** | *What's the first framing taking for granted that might be false, stale, or too narrow?* | Catches flawed premises before you commit to them. |
| **3. Adjacent links** | *What upstream causes, downstream effects, creator lineages, or related niches connect here?* | Surfaces hidden coupling and unexpected crossovers. |
| **4. Limits and pitfalls** | *Where do standard choices break down, fail under load, or disappoint in practice?* | Exposes failure modes and deal-breakers early. |
| **5. Outliers and gems** | *What prior art, unmet niches, or forgotten classics sit outside the mainstream?* | Breaks recency bias and surfaces non-obvious winners. |

---

## 🗺️ Workflow steps

- [ ] **Step 1: Unpack the first framing**
  List the stated goal next to the hidden assumptions and limits baked into the request.
- [ ] **Step 2: Outward sweep across the 5 angles**
  Explore all five angles using read-only checks, primary data, or web search. Tag each finding with its `[T1]` to `[T6]` tier.
- [ ] **Step 3: Surface blind spots and outliers**
  Call out findings that weren't in the first prompt. Look for hidden risks, design mismatches, unmet niches, or forgotten gems that reshape the search.
- [ ] **Step 4: Tally the proof tiers**
  Count how many findings sit in each band (`[T1]` to `[T2]` hard facts, `[T3]` to `[T4]` expert or community signal, and `[T5]` open leads). List the remaining open questions.
- [ ] **Step 5: Check gates and hand off**
  Run the quality checks below, share the expanded map, and use `ask_question` if scope or taste trade-offs need user input.

---

## ✅ Quality checks

Before sharing the discovery report, verify all three rules:

1. **Problem-space expansion**: The report surfaces at least two non-obvious blind spots, outliers, or hidden assumptions that weren't in the user's first prompt.
2. **Scored proof**: Every claim carries a `[T1]` to `[T6]` tag and source link, and the report includes the tier tally table.
3. **Read-only execution**: When run inside a project workspace, the search leaves all tracked files untouched.

---

## 📄 Output template

```markdown
## 1. Initial framing vs. uncovered reality
- **Initial prompt framing**: <What the prompt asked>
- **Implicit assumptions challenged**: <What the framing assumed vs. what the proof shows>

## 2. Quantified proof summary
| Tier band | Count | Share of findings | Confidence note |
| :--- | :--- | :--- | :--- |
| **`[T1]`–`[T2]` Primary & canonical** | <N> | <X%> | Directly verified facts |
| **`[T3]`–`[T4]` Expert & community** | <M> | <Y%> | Cross-checked domain signal |
| **`[T5]`–`[T6]` Unverified / noise** | <K> | <Z%> | Leads requiring testing or filtered out |

## 3. Expanded discovery map

### Baseline state & verified facts
- **`[T1]` [Element or behavior]**: <Observed fact> — Source: <file:line or URL>

### Surfaced blind spots, outliers, and forgotten gems
- **`[T2]` [Outlier or blind spot 1]**: <Why the first framing missed it and why it matters> — Source: <file:line or URL>
- **`[T3]` [Outlier or blind spot 2]**: <Adjacent link, niche opportunity, or overlooked gem> — Source: <file:line or URL>

## 4. Reframed problem statement
- <How the problem or search space looks now that the full board is visible>

## 5. Open questions for convergence
- **Questions for the user**: <Preference, scope, or strategy choices>
- **Questions for follow-up testing**: <Specific `[T4]`–`[T5]` leads to test or sample next>
```
