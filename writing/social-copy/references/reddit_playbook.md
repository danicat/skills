# Reddit Technical Writing Playbook

Comprehensive guide for sharing engineering post-mortems, open-source libraries, architecture deep dives, and technical blogs across Reddit without getting banned, downvoted, or filtered as spam.

---

## 1. Platform Culture & Self-Promotion Rules

### The Golden Rule: "Redditor with a Website"
- **The 9:1 Community Ratio:** For every 1 submission linking to your own work, you must have at least 9–10 substantive, organic, non-promotional comments and contributions across technical subreddits.
- **The "Value-First" / "Zero-Click" Ethos:** The Reddit post must provide **100% of the core lesson, benchmark, and architectural takeaway directly on Reddit**. Readers must not be forced to leave Reddit to get value. Outbound links to GitHub or blogs serve only as references.
- **No Paywalls or Lead Gates:** Never link to Medium paywalls, gated Substacks, or sites with email capture modals.
- **Transparent Affiliation:** Always disclose your relationship upfront (*"Disclaimer: I'm the author of this tool / an engineer at..."*).

---

## 2. Subreddit Ecosystems

| Subreddit | Policies & Content Preferences | Rules & Gotchas |
| :--- | :--- | :--- |
| **`r/programming`** | CS theory, compiler internals, language design, major post-mortems. | **Zero tolerance for beginner tutorials, personal promotion, or SaaS.** Direct link posts must use the exact original article title. |
| **`r/golang` / `r/rust`** | Package releases, concurrency deep-dives, runtime/GC internals. | Use flairs (`[Showcase]`, `[Discussion]`). Zero tolerance for AI-generated posts or engagement bait. |
| **`r/webdev`** | Tooling, frameworks, performance benchmarks. | Showcase posts **strictly restricted to Saturdays** using `[Showoff Saturday]` flair. |
| **`r/MachineLearning`** | Research implementations, benchmark papers, novel architectures. | Mandatory title tags: `[P]` (Project), `[R]` (Research), `[D]` (Discussion). Bare links without writeups are removed. |
| **`r/devops` / `r/sysadmin`** | Infrastructure war stories, post-mortems, CI/CD failures. | Weekly promo thread for tools. Upfront affiliation disclosure mandatory. |

---

## 3. Title Engineering

Tech redditors immediately downvote marketing hype, clickbait questions, and vague promises.

### Anti-Patterns ❌
- ❌ *"Why AI will change programming forever"* (Hyperbolic hype)
- ❌ *"I built a tool that 10x's your workflow!"* (Infomercial cringe)
- ❌ *"You won't believe how we solved our database latency"* (Clickbait)

### High-Converting Formulas ✅
- **Formula 1 (Tool Launch):** `[Tool Name]: An open-source [Language] [Component] designed for [Problem] with [Metric/Architecture]`
  - *Example:* *"Show Reddit: Govalid – A compile-time schema validator for Go that avoids reflection and runtime allocations"*
- **Formula 2 (Post-Mortem):** `How [Team] diagnosed and fixed [Failure] at [Scale] ([Root Cause])`
  - *Example:* *"Post-mortem: How an unnoticed transaction wraparound caused a 45-minute PostgreSQL outage at 10k req/s"*
- **Formula 3 (Migration / Benchmark):** `Why we migrated [A] to [B]: Benchmarks, memory profiles, and trade-offs`
  - *Example:* *"Why we replaced our Redis cluster with a local SQLite + WAL setup: Real-world latency and cost breakdown"*

---

## 4. Post Body Blueprints

### Blueprint: The "Value-First" Case Study / Post-Mortem

```markdown
## The Problem
We were running a webhook ingestion service in [Language] handling [Scale]. Under peak loads, we experienced [Specific failure mode, e.g. thread starvation / GC pauses of 400ms].

## Architectural Bottlenecks Identified
After profiling with [Tool, e.g. pprof / perf], we identified two primary bottlenecks:
1. **[Bottleneck 1]**: [Root cause, e.g., lock contention on shared mutex]
2. **[Bottleneck 2]**: [Root cause, e.g., memory churn in JSON deserialization]

## What We Changed (The Solution)

### 1. [Architectural Change 1]
Instead of [Old approach], we switched to [New approach]:

    // 4-space indent for clean rendering across all Reddit clients
    func processPayload(buf *bytes.Buffer) error {
        obj := payloadPool.Get().(*Payload)
        defer payloadPool.Put(obj)
        return obj.UnmarshalVT(buf.Bytes())
    }

## Benchmark & Production Results
| Metric | Before | After | Delta |
| :--- | :--- | :--- | :--- |
| P99 Latency | 420ms | 18ms | -95% |
| Memory Footprint | 2.4GB | 180MB | -92% |
| CPU Usage | 78% | 35% | -55% |

## Trade-offs & Limitations
- Increased code complexity from manual object pool lifecycle management.
- Static binary serialization requires strict schema contract synchronization.

---
*Full benchmarks and flame graphs are documented on my engineering blog: [Link]*
```

---

## 5. Comment Engagement & Author Participation

- **The Golden Window (First 1–2 Hours):** Be online to answer the first 3–5 technical questions within 10 minutes.
- **Radical Honesty on Trade-offs:** Never claim your tool is better in every way. Clearly specify the exact constraints and use cases where your solution makes sense vs where existing tools are superior.
- **Accept Technical Corrections:** When peers point out an unhandled edge case or race condition, thank them and open an issue immediately. Humility turns critics into advocates.
