# Instagram Technical & Design Copy Playbook

Comprehensive guide for writing technical, architectural, and design copy on Instagram to maximize saves, sends (DMs), and engagement.

---

## 1. Algorithm Dynamics & Ranking Hierarchy

Instagram's discovery engine indexes visual OCR, caption semantics, and active user intent signals.

### Ranking Signal Weights
$$\text{Sends (DM Shares)} > \text{Saves} > \text{Comments} > \text{Likes}$$
- **Sends (DMs):** The highest algorithmic signal for Explore feed distribution. Triggered by relatable engineering pains, anti-patterns, and breakthrough tools.
- **Saves:** Signals evergreen utility. Triggered by cheat sheets, system design blueprints, and code refactorings.
- **Comments:** Driven by polarizing technical trade-offs and comment automation keywords.

---

## 2. Format Specifications & Visual Synergy

### Post Formats
- **Carousel (Multi-Slide 4:5):** The highest-performing format for technical content.
  - Aspect Ratio: **4:5 ($1080 \times 1350\text{ px}$)** for maximum vertical feed real estate.
  - Optimal Length: **6 to 10 slides**.
  - Re-serving loop: Instagram re-serves unengaged carousels on the next session starting at Slide 2.
- **Single Infographic (4:5):** High-density architecture diagrams that stop scroll inertia and force saves.

### Visual-to-Copy Synergy
- **The Slides / Images ("The What"):** Visual code diffs, terminal outputs, high-contrast dark-mode typography (JetBrains Mono / Inter, min 24pt).
- **The Caption ("The Why & How"):** Explains edge cases, memory trade-offs, and production implementation details.

---

## 3. Caption Architecture & Micro-Blogging

### The Hook Before the Fold (< 125 Characters)
The feed truncates captions at **approx. 125 characters** behind the `...more` button. The first sentence must provide an irresistible reason to read.

- ❌ *"Hey guys! Today I wanted to share some thoughts on database indexing..."*
- ✅ *"This single PostgreSQL query mistake cost our startup $4,200 in AWS egress fees 💸"*

### Micro-Blog Caption Blueprint (Up to 2,200 Characters)
```text
[THE HOOK: <125 Chars ending before the fold]
Most developers format their PostgreSQL indexes completely wrong. 🛑

[THE PROBLEM / CONTEXT: 1-2 Short Sentences]
A standard B-tree index on a JSONB column will destroy query performance when data scales past 100k rows.

[THE BREAKDOWN / SOLUTION: Bulleted, High Whitespace]
Here is the exact index strategy senior database engineers use:

• Use GIN (Generalized Inverted Index) for JSONB key-value lookups
• Add expression indexes for high-frequency nested queries
• Combine with partial indexes (`WHERE active = true`) to minimize bloat

[CODE / SYNTAX TAKEAWAY]
Query refactor:
`CREATE INDEX idx_meta ON users USING gin (metadata jsonb_path_ops);`

[DUAL CALL-TO-ACTION]
💾 Save this post for your next database refactor sprint.
💬 Comment "INDEX" below to get the full Postgres Tuning Cheat Sheet in your DMs!

#softwareengineering #postgresql #backend #database
```

---

## 4. Link Funnels & Hashtag Strategy

### The Comment-to-DM Growth Loop
"Link in bio" has heavy drop-off. Use single-word comment automation triggers (e.g., *"Comment 'CODE'"*):
1. User comments keyword → Spikes post engagement velocity.
2. Direct message sends link directly to the user's inbox → 10x higher conversion rate.

### Hashtags (3–5 Target Tags)
- Limit to **3 to 5 hyper-targeted niche tags** placed at the very end of the caption:
  1. Broad Domain: `#softwareengineering`
  2. Specific Stack: `#golang` or `#postgresql`
  3. Specific Topic: `#systemdesign` or `#databaseoptimization`
