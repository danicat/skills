# Instagram technical and design copy playbook

Guide for writing technical, architectural, and design copy on Instagram to drive saves, shares (sends), and peer discussion.

---

## 1. Algorithm dynamics and ranking hierarchy

Instagram indexes visual OCR, caption text semantics, and active user intent signals.

### Ranking signal weights
```
Sends (DM shares) > Saves > Comments > Likes
```
- **Sends (DMs):** Highest Explore distribution signal, driven by relatable engineering bugs, anti-patterns, and useful tools.
- **Saves:** Signals evergreen reference utility, driven by cheat sheets, system blueprints, and code refactors.
- **Comments:** Driven by concrete trade-off questions and optional DM keyword prompts.

---

## 2. Format specifications and visual synergy

### Post formats
- **Carousel (multi-slide `4:5`):** Highest-performing format for technical breakdowns.
  - Aspect ratio: **4:5 (`1080 x 1350` px)** for maximum vertical feed real estate.
  - Slide count: **6 to 10 slides** for optimal completion (platform limit: **20 slides**).
  - Re-serving loop: Instagram often re-serves skipped carousels in a later session starting at Slide 2.
- **Single infographic (`4:5`):** High-density architecture diagrams that encourage saves.

### Visual-to-copy synergy
- **Slides or images (the "what"):** High-contrast dark-mode diffs, terminal captures, and diagrams (`JetBrains Mono` / `Inter`, minimum `24pt`).
- **Caption (the "why and how"):** Explains edge cases, memory trade-offs, and production caveats.

---

## 3. Caption architecture and micro-blogging

### Hook before the fold (< 125 characters)
Instagram truncates captions around **125 characters** behind `...more`. Open with the concrete cost, failure, or takeaway:

- ❌ *"Hey guys! Today I wanted to share some thoughts on database indexing..."*
- ✅ *"This single PostgreSQL query mistake cost our startup $4,200 in AWS egress fees 💸"*

### Micro-blog caption blueprint (up to 2,200 characters)
```text
[THE HOOK: <125 chars ending before the fold]
Most developers format their PostgreSQL indexes completely wrong. 🛑

[THE PROBLEM / CONTEXT: 1 to 2 short sentences]
A standard B-tree index on a JSONB column will crush query latency once tables pass 100k rows.

[THE BREAKDOWN / SOLUTION: Bulleted, clean whitespace]
Here is the exact index strategy we use in production:

• Use GIN (Generalized Inverted Index) for JSONB key-value lookups
• Add expression indexes for hot nested queries
• Combine partial indexes (`WHERE active = true`) to shrink bloat

[CODE / SYNTAX TAKEAWAY]
Query refactor:
`CREATE INDEX idx_meta ON users USING gin (metadata jsonb_path_ops);`

[CALL TO ACTION]
💾 Save this post for your next database tuning sprint.
💬 Comment "INDEX" below to get the full Postgres tuning cheat sheet.

#softwareengineering #postgresql #backend #database
```

---

## 4. Link funnels and hashtag strategy

### Comment-to-DM workflow
"Link in bio" flows suffer heavy drop-off. Optional single-word comment triggers (such as *"Comment 'CODE'"*) drive replies first and deliver links straight to DMs.

### Hashtags (3 to 5 target tags)
- Limit captions to **3 to 5 niche tags** at the end:
  1. Broad domain: `#softwareengineering`
  2. Specific stack: `#golang` or `#postgresql`
  3. Specific topic: `#systemdesign` or `#databaseoptimization`
