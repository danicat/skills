# Threads (by Meta) technical copy playbook

Guide for writing builder, developer, and technical posts on **Threads**.

---

## 1. Algorithm dynamics and ranking factors

Threads prioritizes **conversational depth, candid builder lessons, and multi-turn replies** over corporate announcements.

### Key ranking signals
- **Replies and multi-turn threads (top weight):** Reaching `10` to `25` substantive replies in the first hour pushes posts into broader discovery feeds across Threads and Instagram.
- **Outbound replies:** Leaving thoughtful technical comments on peers' posts builds topical distribution.
- **Dwell time:** Boosted by multi-card carousels (code cards, architecture diagrams) and tight micro-essays.
- **Outbound links:** External URLs are not penalized when paired with standalone native value inside the post body.

---

## 2. Platform ergonomics and specifications

| Feature | Specification | Best practice |
| :--- | :--- | :--- |
| **Standard post cap** | **500 characters** | Keep insights around `280` to `420` chars for fast mobile scanning. |
| **Rich text attachments** | Up to **10,000 characters** | Use for complete code walkthroughs or incident retros. |
| **Carousel media** | Up to **20 images or videos** | Pair `1:1` or `4:5` dark-mode code cards with architecture diagrams. |
| **Topic tags** | **Strict 1-tag rule** (only the first `#tag` indexes) | Use natural keywords with spaces (`#software engineering`, `#system design`). |

---

## 3. High-converting copy templates

### Template A: Micro-tutorial or optimization
```text
Most teams handle [problem] with [common pattern].

Here is why that breaks at [scale, such as memory bloat or lock exhaustion]:

• [Point 1: Bottleneck]
• [Point 2: Edge case risk]

Cleaner fix:
[Attach 1:1 dark-mode code image]

Cut [metric] by [X%].

How are you handling this in production?

#software engineering
```

### Template B: Incident post-mortem or bug retro
```text
An unnoticed config bug knocked out [service] for 45 minutes today.

Root cause and fix:

1. Impact: [Brief failure scope]
2. Trigger: [Specific query or flag bug]
3. Mitigation: [Immediate hotfix]
4. Permanent fix: [Architectural guardrail]

Full post-mortem notes: [URL]

What's the sneakiest bug you've chased this month?

#devops
```

### Template C: Open-source release
```text
Shipped v2.4 of [Project Name] 🚀

We rewrote the [component] engine from scratch.

What changed:
⚡ 3x faster [action]
🛠️ Zero-config support for [Framework/DB]
📦 40% smaller bundle

Demo clip attached below.

Source and release notes: [Link]

#open source
```

---

## 4. Threads do's and don'ts

### ❌ Don'ts
- **No engagement bait:** Phrases like *"Comment LINK to get the repo"* trigger Meta downranking filters.
- **No hashtag stuffing:** Only the first `#tag` indexes as a topic tag.
- **No bare URL drops:** Standalone links without technical explanation get minimal reach.

### ✅ Do's
- Deliver complete standalone value inside the `500`-character body.
- End with `1` natural-language topic tag.
- Close with concrete engineering questions and reply actively within the first `30` to `60` minutes.
