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
- **Outbound Link Suppression (40–60% Penalty):** Links in the post body face severe reach throttling. Deliver 100% standalone value natively and place external URLs in the **first comment** (e.g. *"Full benchmarks & source code linked in the first comment 👇"*).

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
- **Bullet Glyphs:** Use standard unicode markers (`•`, `→`, `-`, `1.`, `2.`). Avoid chaotic emoji walls.
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

Full architecture breakdown and benchmark logs in the first comment 👇

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

Full release notes and GitHub repository linked in the first comment 👇

#OpenSource #DevOps #Engineering
```

---

## 5. Document Carousels (PDF Slides)

Carousels capture the highest dwell times on LinkedIn.
- **Aspect Ratio:** 4:5 Portrait (1080 x 1350 px) for maximum mobile height, or 1:1 Square (1080 x 1080 px).
- **Slide Count:** 6 to 10 slides (sweet spot for completion).
- **Format:** Multi-page PDF document under 100MB.
- **Typography:** Sans-serif (Inter, Roboto), minimum 24–32pt body, 48–60pt headers. Keep text 60–80px away from edges.
- **Slide Structure:** Cover hook (Slide 1) → Problem & baseline (2–3) → Diagrams & code diffs (4–7) → Summary & CTA (Slide 8).

---

## 6. Hashtags & Mentions
- **Hashtags:** **1 to 3 targeted domain hashtags** at the very end (e.g., `#Golang #SystemDesign #SoftwareEngineering`). Never stuff generic tags (`#tech #ai`).
- **Mentions:** Tag 1–3 directly relevant people/orgs who will actively respond. Unresponsive tags trigger algorithmic reach penalties.

---

## 7. The First Comment & Clipboard Pipeline (Zero-Cost Frictionless Flow)

### Why the First Comment Strategy Matters
- **Outbound Link Throttling**: LinkedIn penalizes posts containing outbound links in the body by 40–60% of potential reach.
- **Dwell Time Optimization**: Placing links in the first comment keeps readers focused on the main post's technical narrative.

### The Problem with Third-Party Schedulers
Automated first-comment features in scheduling tools like Buffer are frequently gated behind expensive paid plans ($60/channel/year). Furthermore, if a post is scheduled for later, authors often forget to return and paste the comment manually.

### The Frictionless Agent / Terminal Trick (`pbcopy` / `xclip`)
When publishing via automated tooling or the Buffer CLI:
1. Dispatch the main post immediately using `mode: shareNow`:
   ```bash
   buffer posts create --json "$postPayload" --output json
   ```
2. **Immediately pipe the pre-formatted First Comment to the OS clipboard**:
   - **macOS**:
     ```bash
     cat << 'EOF' | pbcopy
     Links to everything mentioned in the post:

     📖 Technical Deep Dive:
     https://example.com/posts/deep-dive

     🛠️ Project Repository:
     https://github.com/example/project
     EOF
     ```
   - **Linux (X11)**: `cat << 'EOF' | xclip -selection clipboard`
   - **Linux (Wayland)**: `cat << 'EOF' | wl-copy`
3. Print the live post URL directly to the user so they can click the link, press `Cmd+V` / `Ctrl+V`, and post the comment in 2 seconds.

### Strategic Benefits
- **Zero Cost ($0/year)**: Bypasses expensive subscription gates.
- **Zero Forgotten Comments**: The author is already at their keyboard when the post is dispatched live.
- **Boosts Golden-Hour Velocity**: Triggers an active author session and native interaction on LinkedIn immediately after publishing, which signals active conversation to LinkedIn's algorithm.
