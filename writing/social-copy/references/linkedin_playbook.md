# LinkedIn technical copy playbook

Guide for authoring technical copy, engineering field notes, architecture case studies, and release announcements on LinkedIn.

---

## 1. Algorithmic dynamics and ranking signals

LinkedIn uses an **Interest and Authority Graph** that measures dwell time, technical depth, and comment quality rather than raw reactions.

### Key ranking factors
- **Dwell time (top priority):** The algorithm measures active reading time. Posts generating `30` to `60+` seconds of dwell time earn strong distribution multipliers.
- **Comment velocity and depth:** Substantive, multi-sentence comments from peers in the first `60` minutes ("the golden hour") expand reach to secondary feeds.
- **Author response velocity:** Author replies within the first `1` to `2` hours extend the post's active distribution window by `20%` to `30%`.
- **Saves > Shares > Comments > Reactions:** Saves indicate evergreen reference utility; one-click reactions carry minimal weight.
- **Direct in-body links beat first-comment links:** Technical posts that place concrete URLs (`https://...` to an article, docs page, or GitHub repo) directly inside a substantive post body (`900` to `2,000` chars) paired with native visual media consistently outperform linkless and "first-comment" posts in both reach and discussion depth. Always keep outbound URLs in the body while delivering standalone technical value above them.
- **Dual function of native visual media:** Attaching an architecture diagram, benchmark chart, screenshot, or PDF carousel arrests scroll velocity (`2x` to `3x` higher discussion depth than text-only posts) and overrides LinkedIn's compact OpenGraph link preview so the post renders at full viewport size while keeping in-body URLs clickable.

### Publishing cadence and the feed-horizon law
- **`18` to `48` hour feed lifecycle:** LinkedIn ranks posts across a multi-day distribution horizon rather than a chronological stream.
- **Negative marginal daily reach from intra-day posting:** Creator-diversity caps throttle competing same-day posts so two same-day posts split early velocity and yield **fewer total daily views than publishing once**.
- **Optimal cadence:** Maximum **1 post per 24 hours** (`3` to `5` high-signal posts per week). Separate follow-up angles by at least `24` hours.
- **Audience work-mode alignment:** Publish architectural deep dives during core mid-week working hours or Sunday evening prep windows in your audience's primary timezone; avoid Friday afternoon wind-down windows.

---

## 2. Hook window and formatting mechanics

### Visible fold window
LinkedIn truncates posts behind `...see more`:
- **Mobile:** ~`140` characters (`2` to `3` lines). *Blank lines count toward line truncation.*
- **Desktop:** ~`210` characters (`3` to `5` lines).

> [!IMPORTANT]
> **Hook economy vs. the "banned list" fallacy:**
> Never treat hook writing as a mechanical banned-word list. That causes two failures: assuming any sentence avoiding blacklisted words is good copy, and rejecting genuine milestone openings when the milestone is the real story. Judge the visible `140` to `210` chars by opportunity cost: does Line 1 give a cold reader an immediate technical reason to expand instead of wasting space on chronological recaps or scheduling updates?

### Post length and grounded voice benchmarks
- **Optimal post length:** **1,300 to 2,000 characters** (`200` to `350` words) for strong dwell without reader fatigue.
- **Hard limit:** `3,000` characters.
- **Grounded senior-engineer voice over textbook summaries:** Share real design trade-offs, failure modes, and field notes rather than a sterile textbook checklist.

### Formatting rules
- **Paragraphs:** `1` to `3` short sentences per paragraph with clean spacing.
- **Bullet markers:** Use plain markers (`•`, `->`, `-`, `1.`, `2.`). Avoid noisy emoji walls.
- **Section labels:** Use short uppercase labels (`THE PROBLEM:`, `THE FIX:`, `THE TRADE-OFF:`) sparingly where they improve scanning.
- **Zero Unicode bolding:** Never use mathematical Unicode bold fonts (`𝗕𝗼𝗹𝗱`). They break screen readers, ruin search indexing, and inflate byte counts.

---

## 3. High-converting hook formulas

1. **Scale and hard metric hook:**
   > *"We dropped P99 database latency from 850ms to 24ms across 12,000 req/s. It did not require sharding, only fixing one overlooked cache serialization flaw."*
2. **Contrarian architectural insight:**
   > *"Most microservices migrations fail not from Kubernetes complexity, but from enforcing distributed transactions. Here is why we reverted to an asynchronous outbox."*
3. **Incident post-mortem hook:**
   > *"At 03:14 UTC, an unnoticed DNS propagation drift took down our primary auth cluster for 42 minutes. Here is the post-mortem and the 3 guardrails we deployed."*
4. **Trade-off dilemma:**
   > *"Eventual consistency looks cheap on paper until billing pipelines drop idempotent reconciliation. Here's how we solved double-spend risks in Go."*
5. **Developer ROI and cost compression:**
   > *"We cut our asynchronous LLM batch bill by 50% without touching a single prompt or degrading answer quality. Here is how the pipeline works:"*
6. **Participatory design question:**
   > *"We are building a live debugging series where we break and repair production distributed systems from scratch. Which failure mode should we stress-test first?"*

### Hook comparison: reader-utility gate (< 140 chars)

| Approach | Above-the-fold text (< 140 chars) | Causal effect |
| :--- | :--- | :--- |
| **Bad (chronological recap)** | *"In my previous article, I set up a basic worker pool in Go. Today in Part 5, I'm excited to share..."* | Burns the mobile preview on past housekeeping; a cold reader sees no reason to click `...see more`. |
| **Bad (author housekeeping)** | *"I've been heads down shipping new projects this week so you haven't heard from me lately. Today I want to discuss..."* | Centers on the author's calendar instead of an engineering problem. |
| **Good (immediate tension)** | *"Unbounded goroutines under bursty webhooks will OOM your Go service before autoscaling reacts. Here is bounded backpressure:"* | Names a concrete failure mode and fix inside the visible window. Series links move to the bottom. |

---

## 4. Post archetypes and templates

### Template A: Architectural deep dive or field note
```markdown
[Direct hook naming metric, failure mode, or architectural decision]

[1 to 2 sentences on context: traffic volume, legacy stack, or scaling limits]

THE PROBLEM:
• [Friction point or failure mode 1]
• [Friction point or failure mode 2]

THE ARCHITECTURAL APPROACH:
1. [Concrete technical change 1]
2. [Concrete technical change 2]
3. [Concrete technical change 3]

THE TRADE-OFFS:
[Honest discussion of what was sacrificed: memory, operational complexity, or write throughput]

QUANTITATIVE OUTCOME:
• [Metric 1: Latency / CPU / Memory delta]
• [Metric 2: Cost / Uptime delta]

[Specific discussion question for peer engineers]

Full architecture breakdown and benchmarks: https://example.com/posts/architecture-deep-dive

#SystemDesign #DistributedSystems #SoftwareEngineering
```

### Template B: Engineering release and changelog
```markdown
[Direct statement of developer friction removed]

Today we shipped [Tool/Project] [X.Y], focused on [Core Capability].

WHAT'S NEW:
1. [Feature 1 with practical CLI/API example]
2. [Feature 2 with measured speed or size gain]
3. [Feature 3 with developer experience fix]

BENCHMARK DELTA:
• [Memory footprint / build time / throughput comparison]

Release notes: https://example.com/posts/release-notes
GitHub repository: https://github.com/example/project

#OpenSource #DevOps #Engineering
```

---

## 5. Document carousels (PDF slides)

Carousels drive the highest dwell times on LinkedIn:
- **Aspect ratio:** `4:5` portrait (`1080 x 1350` px) for maximum mobile screen height, or `1:1` square (`1080 x 1080` px).
- **Slide count:** `6` to `10` slides (completion sweet spot).
- **Format:** Multi-page PDF under `100MB`.
- **Typography:** Sans-serif (`Inter`, `Roboto`), minimum `24` to `32pt` body and `48` to `60pt` headers, keeping `60` to `80px` margin from edges.
- **Slide flow:** Cover hook (Slide `1`) -> Problem and baseline (`2` to `3`) -> Diagrams and code diffs (`4` to `7`) -> Summary and CTA (Slide `8`).

---

## 6. Hashtags and mentions
- **Hashtags:** `1` to `3` targeted domain hashtags at the bottom (`#Golang #SystemDesign #SoftwareEngineering`). Skip generic tags (`#tech #ai`).
- **Mentions:** Tag `1` to `3` relevant people or orgs likely to engage. Unanswered tags hurt reach.

---

## 7. Direct in-body links vs. the "first comment" myth

### Why direct in-body links win for technical audiences
Placing outbound URLs (`https://...`) directly in the post body, paired with a substantive engineering narrative (`900` to `2,000` chars) and a native visual asset, consistently outperforms linkless and "first-comment" posts:
- **Engineering proof signal:** Direct links to runnable code, benchmarks, or repositories signal verifiable engineering substance.
- **Link-card override mechanism:** LinkedIn's historical link drop comes from bare link posts collapsing into low-dwell OpenGraph cards. Pairing an in-body URL with an explicit image, diagram, or PDF renders the full-size native visual while keeping the URL clickable in the text.

### Why "Link in the first comment 👇" backfires
1. **Comment sorting hides the URL:** LinkedIn defaults comments to `Most Relevant`, so discussion pushes an unpinned author comment down the thread.
2. **Broken reshares:** Reposting strips the original author's first comment, dropping the destination URL across secondary feeds.
3. **Scheduling fragility:** Keeping URLs inside the body lets `customScheduled` and `addToQueue` campaigns publish cleanly without manual follow-up edits.

### Best practices for in-body link placement
- **Attach native visual assets:** Pair in-body URLs with a `1200x630` card, diagram, PDF, or video so the feed displays rich media instead of a compact preview.
- **Place URLs after the value:** Deliver the full technical lesson first, then place `1` to `3` labeled URLs near the bottom right above the hashtags.
