# Threads (by Meta) Technical Copy Playbook

Comprehensive guide for writing builder, developer, and technical posts on **Threads**.

---

## 1. Algorithm Dynamics & Ranking Factors

Meta's Threads prioritizes **conversational depth, authentic builder vulnerability, and multi-turn discussions** over sterile marketing broadcasts.

### Key Ranking Signals
- **Replies & Multi-turn Discussions (Top Weight):** Receiving 10–25 meaningful replies within the first hour pushes content into the wider "For You" discovery feeds across Threads and Instagram.
- **Outbound Replies:** Leaving high-signal technical replies on others' posts trains the algorithm on your topical authority.
- **Dwell Time:** Maximized via multi-card carousels (Ray.so code cards, architecture diagrams) and clean micro-essays.
- **The Link Myth:** Outbound links are **not** algorithmically suppressed on Threads. However, posts providing standalone native value convert 5x better than lone link drops.

---

## 2. Platform Ergonomics & Specifications

| Feature | Specification | Best Practice for Tech Content |
| :--- | :--- | :--- |
| **Standard Post Limit** | **500 characters** | Keep core insight to 280–420 chars for rapid mobile scannability. |
| **Rich Text Attachments** | Up to **10,000 characters** with markdown-like styling | Use for full code walkthroughs or incident post-mortems. |
| **Carousel Media** | Up to **20 images/videos** | 1:1 or 4:5 aspect ratio dark-mode code cards (Ray.so) or architecture flows. |
| **Topic Tags** | **Strict 1-Tag Rule** (Only the first `#tag` is indexed) | Use natural language tags with spaces (e.g. `#software engineering`, `#system design`). |

---

## 3. High-Converting Copy Templates

### Template A: The Micro-Tutorial / Code Optimization
```text
Most developers handle [problem] with [common approach].

Here is why that causes [issue, e.g., memory bloat / connection exhaustion] at scale:

• [Point 1: Technical bottleneck]
• [Point 2: Edge case risk]

A cleaner approach:
[Attach 1:1 Ray.so/Carbon Code Image]

This reduced our [metric] by [X%]. 

How is your team handling this in production?

#software engineering
```

### Template B: The Production Post-Mortem / Bug Retro
```text
We had an incident that knocked out [service/feature] for 45 minutes today.

Here is the exact root cause and how we fixed it:

1. What happened: [Brief failure context]
2. The trigger: [Specific code/query flaw]
3. The mitigation: [Immediate hotfix]
4. The long-term fix: [Architectural adjustment]

Full retro notes + post-mortem doc in the link below: [URL]

What’s the most subtle bug you’ve had to debug recently?

#devops
```

### Template C: The Open Source Feature Release
```text
Shipping v2.4 of [Project Name] 🚀

We completely rewrote the [component] engine.

What's new:
⚡ 3x faster [action/metric]
🛠️ Zero-config support for [Framework/DB]
📦 40% smaller bundle size

Demo screencast attached below. 

GitHub repo + documentation: [Link]

#open source
```

---

## 4. Threads Do's & Don'ts

### ❌ Don'ts
- **No Engagement Bait:** Phrases like *"Comment LINK to get the repo"* or *"Like if you agree"* trigger algorithmic downranking filters.
- **No Hashtag Stuffing:** Never use multiple hashtags (`#golang #dev #coding`). Only the first tag is indexed.
- **No Uncontextualized URL Drops:** Lone links with "Check out my new post" get near-zero distribution.

### ✅ Do's
- Deliver 100% standalone value natively in the 500-char post.
- Use exactly **1 natural-language Topic Tag** at the bottom.
- End posts with concrete, experience-based technical questions.
- Engage and reply to comments within the first 30–60 minutes.
