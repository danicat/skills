# LinkedIn Technical Copy Playbook

Comprehensive guide for authoring high-performing technical copy, engineering field notes, architectural case studies, and release announcements on LinkedIn.

---

## 1. Algorithmic Dynamics & Ranking Signals

LinkedIn uses an **Interest & Authority Graph** that measures dwell time, technical depth, and conversation quality rather than raw like count.

### Key Ranking Factors
- **Dwell Time (Top Priority):** The algorithm measures active viewing/reading time. Posts generating 30–60+ seconds of dwell time receive maximum distribution multipliers.
- **Comment Velocity & Depth:** Meaningful, multi-sentence comments from active industry accounts in the first 60 minutes ("the golden hour") expand distribution to 2nd- and 3rd-degree feeds.
- **Author Response Velocity:** Author replies to comments within the first 1–2 hours boost the post's active lifecycle by 20–30%.
- **Saves > Shares > Comments > Reactions:** Saves signal evergreen utility; shallow reactions ("Like") carry minimal algorithmic weight.
- **Direct In-Body Links Outperform "First Comment" Links (`+32%` Median / `2.5x` Mean Reach):** Contrary to generic social marketing folklore, developer posts that include concrete outbound URLs (`https://...` to a technical blog post, documentation page, or GitHub repository) directly inside a substantive post body (`900–2,000` chars) outperform linkless and "first-comment" posts across every metric (`+32%` higher median impressions, `2.5x` higher mean impressions, `+50%` more median reactions, and `2x` more comments). Always place primary links directly in the post body while delivering 100% standalone technical value in the text above them.

### Publishing Cadence & Anti-Cannibalization Rules
- **18–24 Hour Feed Lifecycle:** LinkedIn's algorithm operates on an extended 18–48 hour distribution cycle.
- **Intra-Day Self-Cannibalization:** Publishing a second personal post within 18–24 hours causes LinkedIn's feed engine to throttle distribution across both posts (an estimated ~30% reach reduction for the first post and suppressed distribution for the second) to prevent multi-post flooding in follower feeds.
- **Optimal Personal Cadence:** Maximum **1 post per 24 hours** (3 to 5 high-quality posts per week). Allow each post a full 24-hour window to cycle through its engagement runway.

---

## 2. Hook Window & Formatting Mechanics

### The Visible Fold Window
The feed truncates copy with `...see more`:
- **Mobile:** ~140 characters (2–3 lines). *Note: Blank lines count as full lines against this limit.*
- **Desktop:** ~210 characters (3–5 lines).

### Post Length Benchmarks
- **Optimal Post Length:** **1,300 to 2,000 characters** (200–350 words). Provides enough depth to maximize dwell time without causing fatigue.
- **Hard Limit:** 3,000 characters.

### Formatting Rules
- **Paragraphs:** 1–3 short sentences per paragraph with generous whitespace.
- **Bullet Glyphs:** Use standard unicode markers (`•`, `->`, `-`, `1.`, `2.`). Avoid chaotic emoji walls.
- **Section Headers:** Use short uppercase labels (`THE PROBLEM:`, `THE FIX:`, `THE TRADE-OFF:`).
- **NO Unicode Bolding:** Do not use mathematical unicode bold fonts (e.g., `𝗕𝗼𝗹𝗱`). They break screen readers, fail semantic search indexing, and inflate byte counts.

---

## 3. High-Converting Hook Formulas

1. **The Scale / Hard Metric Hook:**
   > *"We dropped P99 database latency from 850ms to 24ms across 12,000 req/s. It didn’t require sharding—just fixing one overlooked cache serialization flaw."*
2. **The Contrarian Architectural Insight:**
   > *"Most microservices migrations fail not because of Kubernetes complexity, but because teams try to enforce distributed transactions. Here is why we reverted to an asynchronous outbox."*
3. **The Incident Post-Mortem Hook:**
   > *"At 03:14 UTC, an unnoticed DNS propagation drift took down our primary auth cluster for 42 minutes. Here is the exact post-mortem and the 3 guardrails we deployed."*
4. **The Trade-off / Decision Dilemma:**
   > *"Eventual consistency is cheap to architect on paper, but brutal when billing systems drop idempotent reconciliation. Here’s how we solved double-spend risks in Go."*

---

## 4. Post Archetypes & Templates

### Template A: Architectural Deep-Dive / Field Note
```markdown
[Direct, High-Tension Hook stating metric, problem, or decision]

[1-2 sentences on context: traffic volume, legacy stack, or scaling limits]

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
• [Metric 1: Latency / CPU / Memory change]
• [Metric 2: Cost / Uptime delta]

[Nuanced discussion question for peer engineers]

Full architecture breakdown and benchmark logs: https://example.com/posts/architecture-deep-dive

#SystemDesign #DistributedSystems #SoftwareEngineering
```

### Template B: Engineering Release & Changelog
```markdown
[Direct statement of developer friction being eliminated]

Today we're shipping version [X.Y] of [Tool/Project], focused entirely on [Core Capability].

WHAT'S NEW:
1. [Feature 1 with practical CLI/API example]
2. [Feature 2 with performance win]
3. [Feature 3 with DX improvement]

BENCHMARK DELTA:
• [Memory footprint / build time / throughput comparison]

Full release notes: https://example.com/posts/release-notes
GitHub repository: https://github.com/example/project

#OpenSource #DevOps #Engineering
```

---

## 5. Document Carousels (PDF Slides)

Carousels capture the highest dwell times on LinkedIn.
- **Aspect Ratio:** 4:5 Portrait (1080 x 1350 px) for maximum mobile height, or 1:1 Square (1080 x 1080 px).
- **Slide Count:** 6 to 10 slides (sweet spot for completion).
- **Format:** Multi-page PDF document under 100MB.
- **Typography:** Sans-serif (Inter, Roboto), minimum 24–32pt body, 48–60pt headers. Keep text 60–80px away from edges.
- **Slide Structure:** Cover hook (Slide 1) -> Problem & baseline (2-3) -> Diagrams & code diffs (4-7) -> Summary & CTA (Slide 8).

---

## 6. Hashtags & Mentions
- **Hashtags:** **1 to 3 targeted domain hashtags** at the very end (e.g., `#Golang #SystemDesign #SoftwareEngineering`). Never stuff generic tags (`#tech #ai`).
- **Mentions:** Tag 1–3 directly relevant people/orgs who will actively respond. Unresponsive tags trigger algorithmic reach penalties.

---

## 7. Direct In-Body Links vs. The "First Comment" Myth

### Why Direct In-Body Links Win for Technical Audiences
Empirical analysis across 190+ technical LinkedIn posts (`658K+` total impressions) demonstrates that placing outbound links (`https://...`) directly in the post body **outperforms** linkless and "first-comment" posts:
- **`+32.0%` Higher Median Impressions** (`1,274` vs. `965` views) and **`2.52x` Higher Mean Impressions** (`5,519` vs. `2,192` views).
- **`+50.0%` Higher Median Reactions** (`27.0` vs. `18.0`) and **`2x` Median Comments** (`2.0` vs. `1.0`).
- **7 of the Top 10 All-Time Posts** contained `1` to `4` outbound URLs directly inside the post body.
- **Engineering Proof Signal**: When paired with a substantive narrative (`900–2,000` chars) and an explicit native visual asset (`featured.png` diagram or screenshot), an in-body URL signals verifiable engineering depth (runnable code, repository, or benchmark article) rather than generic thought-leadership fluff.

### Why "Link in the First Comment 👇" Backfires
1. **Comment Sorting Buries Your Link**: LinkedIn defaults comment threads to `Most Relevant` rather than chronological order. As soon as peer engineers leave substantive comments, the author's unpinned "first comment" sinks below the fold, destroying click-through conversions.
2. **Zero Reach Advantage in Controlled Series Tests**: In multi-part technical series launches, withholding the URL from the body (`"Full chapter and runnable code walkthrough in the first comment 👇"`) resulted in **`-88%` to `-96%` fewer impressions** than adjacent chapters in the exact same series that placed the URL directly in the post body—even when the first-comment post earned more reactions.
3. **Scheduling Fragility**: Placing the primary URL directly in the post body allows campaigns to be scheduled reliably (`customScheduled` or `addToQueue`) without requiring manual post-publish clipboard workarounds.

### Best Practices for In-Body Link Placement
- **Pair with a Native Image or Video Asset**: Always attach an explicit media asset (`1200×630` hero card, architecture diagram, or demo clip). When a native media asset is attached, LinkedIn renders the full-size visual card in the feed while keeping the in-body URL clickable inside the text—avoiding compact/cropped link-preview cards.
- **Position Links After the Core Value**: Deliver the complete problem statement, architectural breakdown, and trade-offs first (`Zero-Click` value), then place `1–3` clearly labeled URLs near the bottom of the post just above the hashtags.
