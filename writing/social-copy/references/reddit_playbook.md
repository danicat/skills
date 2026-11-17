# Reddit technical writing playbook

Guide for sharing engineering post-mortems, open-source packages, architecture deep dives, and technical articles on Reddit without triggering spam filters or downvotes.

---

## 1. Platform culture and self-promotion rules

### Golden rule: "Redditor with a website"
- **The `9:1` community ratio:** For every `1` post linking to your own work, contribute at least `9` to `10` substantive, non-promotional comments across technical subreddits.
- **Standalone zero-click depth:** Deliver `100%` of the core lesson, benchmarks, and architectural takeaways directly in the Reddit self-post. Outbound links to GitHub or a blog serve strictly as supporting references.
- **No paywalls or lead gates:** Never link to paywalled posts or forced email-capture forms.
- **Transparent affiliation:** Disclose ownership upfront (*"Disclaimer: I'm the author of this tool..."*).

---

## 2. Subreddit ecosystems

| Subreddit | Content focus | Key rules and pitfalls |
| :--- | :--- | :--- |
| **`r/programming`** | CS theory, compiler internals, language design, major post-mortems. | Zero tolerance for beginner tutorials or SaaS promos. Link posts must keep the original article title. |
| **`r/golang` / `r/rust`** | Package releases, concurrency deep dives, runtime and GC internals. | Use flairs (`[Showcase]`, `[Discussion]`). Zero tolerance for AI-generated posts or engagement bait. |
| **`r/webdev`** | Tooling, frameworks, performance benchmarks. | Showcase posts allowed strictly on Saturdays with `[Showoff Saturday]`. |
| **`r/MachineLearning`** | Implementations, benchmark papers, model architectures. | Mandatory title prefixes: `[P]` (Project), `[R]` (Research), `[D]` (Discussion). Bare links are removed. |
| **`r/devops` / `r/sysadmin`** | Infrastructure war stories, post-mortems, CI/CD failures. | Weekly promo threads for tools. Upfront affiliation disclosure required. |

---

## 3. Title engineering

Technical subreddits downvote hype, clickbait questions, and vague marketing claims fast.

### Anti-patterns ❌
- ❌ *"Why AI will change programming forever"*
- ❌ *"I built a tool that 10x's your workflow!"*
- ❌ *"You won't believe how we fixed database latency"*

### High-converting formulas ✅
- **Tool launch:** `[Tool Name]: An open-source [Language] [Component] for [Problem] with [Metric or Mechanism]`
  - *Example:* *"Show Reddit: Govalid, a compile-time Go schema validator avoiding runtime reflection"*
- **Post-mortem:** `How [Team] diagnosed and fixed [Failure] at [Scale] ([Root Cause])`
  - *Example:* *"Post-mortem: How transaction wraparound caused a 45-minute PostgreSQL outage at 10k req/s"*
- **Migration or benchmark:** `Why we migrated [A] to [B]: Benchmarks, memory profiles, and trade-offs`
  - *Example:* *"Why we replaced Redis with SQLite WAL mode: production latency and cost breakdown"*

---

## 4. Post body blueprint

### Blueprint: zero-click case study or post-mortem

```markdown
## Problem
We ran a webhook ingestion service in [Language] handling [Scale]. Under peak traffic, we hit [specific failure mode, such as 400ms GC pauses].

## Bottlenecks identified
Profiling with [tool, such as pprof or perf] isolated two bottlenecks:
1. **[Bottleneck 1]**: [Root cause, such as mutex contention]
2. **[Bottleneck 2]**: [Root cause, such as JSON allocation churn]

## Fix implemented

### 1. [Architectural change]
Instead of [old approach], we switched to [new approach]:

    // 4-space indent renders cleanly across Old and New Reddit
    func processPayload(buf *bytes.Buffer) error {
        obj := payloadPool.Get().(*Payload)
        defer payloadPool.Put(obj)
        return obj.UnmarshalVT(buf.Bytes())
    }

## Benchmark and production delta
| Metric | Before | After | Delta |
| :--- | :--- | :--- | :--- |
| P99 Latency | 420ms | 18ms | -95% |
| Memory Footprint | 2.4GB | 180MB | -92% |
| CPU Usage | 78% | 35% | -55% |

## Trade-offs and limits
- Manual object pool lifecycles add complexity.
- Binary serialization enforces stricter schema contracts.

---
Full flame graphs and raw benchmark logs: [Link]
```

---

## 5. Comment engagement and author follow-up

- **Golden window (`1` to `2` hours):** Stay active after posting to answer the first `3` to `5` technical questions within `10` minutes.
- **Radical honesty on limits:** State explicitly where existing tools outperform yours.
- **Welcome technical corrections:** When commenters catch an edge case or race condition, acknowledge it directly and open an issue right away.
