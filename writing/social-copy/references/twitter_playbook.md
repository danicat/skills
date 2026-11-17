# X (Twitter) technical copy playbook

Guide for writing high-signal engineering posts, release logs, and technical threads on X (formerly Twitter).

---

## 1. Algorithm mechanics and account tier rules

X ranks posts using semantic embeddings and engagement velocity that weight deep reading, bookmarks, and active replies over passive likes.

### Algorithmic weight signals
- **Dwell time and reading seconds:** Core distribution driver for long-form breakdowns and threads.
- **Bookmarks (~`10x` to `13x` over Likes):** Strongest indicator of reference value for tutorials and benchmarks.
- **Reposts (~`20x`) and Quote Posts (~`15x`):** Primary reach multipliers into secondary timelines.
- **Replies (~`13.5x`):** Active back-and-forth technical threads accelerate feed distribution.
- **`Show more` clicks:** Strong positive signal that the opening lines converted scrollers into readers.
- **Likes (`1x`):** Baseline low-weight engagement signal.

### X Premium long-form vs. standard `280`-character posts
- **Verify account tier and API queue limits first:**
  - **X Premium accounts (native composer or long-form enabled):** Long-form posts (`800` to `2,500` chars recommended, `25,000`-character platform ceiling) maximize dwell time and bookmarks without thread drop-off.
  - **Standard accounts and standard single-post API queues:** Enforces a strict **280-character limit** per post (`280` chars max; `t.co` URLs count as `23` chars). Never draft a `1,200`-char monologue for a `280`-char queue; split multi-part breakdowns into a `3` to `5` post micro-thread or tighten into an `180` to `260` char single post.
- **Native links and visual proof:** Outbound URLs perform best when paired with real commentary plus visual proof (UI screenshots, architecture diagrams, terminal captures, or demo clips), which boosts reach, multiplies reply depth (`3x+` over text-only posts), and increases outbound click-throughs.

### Hashtags rule (`0` hashtags)
- Hashtags are obsolete for discovery on X because semantic retrieval indexes post body text directly. Use **0 hashtags** (or at most `1` official event tag during a live conference).

### Stream velocity and spacing
- **Short `1` to `3` hour decay horizon:** Early interactions in the first `15` to `30` minutes heavily influence reach.
- **Spacing rule (`2` to `3` hours):** Unlike LinkedIn, X rewards multi-post launch days when standalone broadcasts are spaced `2` to `3` hours apart. Posting multiple standalone tweets back-to-back splits early velocity; bundle closely related points into a thread instead.
- **Weekend builder windows:** Developer demos, OSS releases, and field notes perform strongly on weekends when corporate PR noise drops.

---

## 2. Formatting and above-the-fold constraints

### Visible fold window (`< 240` to `280` characters)
Feeds truncate copy around **240 to 280 characters** (`3` to `4` lines) behind `Show more`. Place the concrete problem, benchmark delta, and hook above the fold.

### Format options and budgets
- **Long-form post (`800` to `2,500` chars, X Premium):** Best for self-contained incident retros, release changelogs, and architecture breakdowns.
- **Micro-thread (`3` to `5` posts, `<= 280` chars each):** Works on all accounts and API queues; ideal for step-by-step visuals and multi-chart benchmarks.
- **Single post (`180` to `260` chars, `<= 280` chars):** Ideal for crisp releases, hot fixes, and single benchmark screenshots.

---

## 3. High-converting hook patterns

1. **Benchmark delta hook:**
   > *"How we cut Docker build times from 14 minutes to 38 seconds with one multi-stage cache flag:"*
2. **Production post-mortem hook:**
   > *"We burned $14,000 in API credits overnight. Here is the 1-line async retry bug behind the infinite loop (and how we capped it):"*
3. **Engineering trade-off hook:**
   > *"Stop fighting the agent harness: as models get stronger, rigid hooks fail in surprising ways. Here is the constraint model we moved to:"*

---

## 4. Templates

### Template A: Technical case study or release (X Premium long-form)
```text
[Hook under 240 chars: metric, failure mode, or decision]

WHAT CHANGED:
• [Module 1]: [Upgrade and measured effect]
• [Module 2]: [Upgrade and measured effect]
• [Module 3]: [Upgrade and measured effect]

WHY PREVIOUS DESIGN FAILED:
[2 to 3 crisp paragraphs explaining root cause and constraints]

FIX:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Repo and benchmark logs: [URL]
```

### Template B: Micro-thread (all X accounts, <= 280 chars per post)
```text
1/ [Hook < 240 chars + key metric + attached visual]

2/ [Root cause or constraint < 280 chars]

3/ [Fix + benchmark table or code image < 280 chars]

4/ [Trade-offs + direct URL to repo or post < 280 chars]
```
