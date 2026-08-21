---
name: social-copy
description: >
  Editorial workflow and platform playbooks for drafting developer-native
  social media copy and campaigns. Extracts technical evidence via git log
  inspections or /grill-me interviews, establishes a canonical foundation
  narrative (CANONICAL.md), tailors derivatives for connected platforms (such as
  LinkedIn, X/Twitter, Bluesky, and others), and enforces anti-slop guidelines.
  Activate when drafting social media posts, writing release announcements,
  authoring technical threads, or running developer campaigns.
license: Apache-2.0
metadata:
  category: writing
  tags: "social-media, developer-marketing, writing, publishing, campaigns"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.1"
  canonical: https://skills.danicat.dev/writing/social-copy/
---

# Social Copy Playbook

Systematic procedures, voice standards, and platform-specific playbooks for crafting high-engagement, developer-native social media copy and cross-platform campaigns.

---

## Architecture & Progressive Disclosure

To minimize context overhead, `SKILL.md` defines core editorial workflows and routing. Load detailed platform playbooks and anti-pattern checklists on demand:

- **LinkedIn**: Read [references/linkedin_playbook.md](references/linkedin_playbook.md) when writing LinkedIn posts, PDF document carousels, or B2B engineering announcements.
- **Twitter / X**: Read [references/twitter_playbook.md](references/twitter_playbook.md) when writing single tweets, micro-threads (3–5 tweets), or X long-form native posts / articles.
- **Bluesky**: Read [references/bluesky_playbook.md](references/bluesky_playbook.md) when posting to AT Protocol feeds, sharing direct links, or formatting open-source releases with rich link cards.
- **Instagram**: Read [references/instagram_playbook.md](references/instagram_playbook.md) when designing 4:5 carousels, micro-blog captions, and comment-to-DM funnels.
- **Reddit**: Read [references/reddit_playbook.md](references/reddit_playbook.md) when writing self-posts for technical subreddits (`r/programming`, `r/golang`, `r/webdev`, `r/MachineLearning`, `r/devops`).
- **Threads**: Read [references/threads_playbook.md](references/threads_playbook.md) when writing builder-centric 500-character posts with single Topic Tags.
- **Anti-Patterns & Slop**: Read [references/anti_patterns.md](references/anti_patterns.md) before finalizing copy to eliminate AI clichés, unicode bolding bugs, and engagement-bait triggers.

---

## Core Voice & Editorial Philosophy

Technical copy succeeds by delivering **immediate utility and authentic engineering depth** rather than marketing hype.

### 1. The Developer-to-Developer Tone
Write like a **senior engineer or architect speaking to peers**:
- **Direct & Unvarnished:** State the technical problem, constraint, or metric on Line 1.
- **Transparent About Trade-offs:** No architecture or tool is flawless. Acknowledge what was sacrificed (memory, complexity, query latency).
- **Substance Over Slogans:** Replace vague buzzwords (*"seamless", "revolutionary"*) with concrete technical nouns (*"lock-free ring buffer", "eager loading", "connection pooling"*).

### 2. The "Value-First" / "Zero-Click" Principle
Every post should provide actionable insight directly in the timeline. Readers should learn something valuable even if they never click an external link.

---

## Campaign Lifecycle States

Every social campaign follows a strict 4-state lifecycle tracked explicitly in its `CANONICAL.md` header (`- **Status**: <state>`):

| State | Definition & Trigger | Required Artifacts |
| :--- | :--- | :--- |
| `Draft` | Initial research, deep git inspection, `/grill-me` extraction, and `CANONICAL.md` authoring. Channel derivatives are being drafted. | `CANONICAL.md` |
| `Ready` | Copy audited against anti-patterns, character budgets verified, and derivatives finalized. Awaiting author publishing gate. | `CANONICAL.md`, channel files (`linkedin.md`, `twitter.md`, etc.) |
| `Scheduled` | Dispatched to a queue or scheduled for a specific timestamp (via Buffer CLI or native scheduler). | `CANONICAL.md`, scheduled date/time, optional `.ics` reminder |
| `Published / Live` | Dispatched live (`shareNow`) or confirmed live on external channels. | Live post URLs recorded, workspace backlog updated |

---

## 7-Stage Social Campaign Workflow

Follow this procedure when creating, publishing, or auditing social campaigns:

### Stage 1: Evidence Discovery & Grounding
Never hallucinate features, metrics, or claims.
1. **Inspect Deep Git & Source References**:
   - **No Shallow Summaries / No One-Line Shortcuts**: Never rely on `git log --oneline` or brief commit titles alone. One-line summaries hide critical architectural nuance, structural refactors, and behavioral details.
   - Always run full `git log` with commit bodies, inspect diff statistics (`git show --stat`), check architecture decision records (ADRs), and inspect source documentation directly across all referenced repositories.
2. **Interview via `/grill-me`**: If the source is an open-ended topic or raw idea, recommend `/grill-me` or conduct an interactive interview to extract the author's real friction points, unexpected discoveries, and authentic engineering voice.
3. **Draft & Continuously Sync the Canonical Foundation Narrative (`CANONICAL.md`)**:
   Author a comprehensive, unconstrained master document with `- **Status**: Draft` covering:
   - Core premise & real motivation.
   - Exact repositories and what was specifically built/refactored in each.
   - Concrete performance observations (time-to-first-token, reasoning depth, compile times).
   - Architectural breakthroughs, failure modes, and trade-offs.
   - Philosophical takeaways and references to published writing.
   > [!IMPORTANT]
   > **Continuous Master Synchronization**: Whenever new evidence is collected (whether through proactive deep git inspection or after user feedback/pushback), immediately update `CANONICAL.md` before adjusting derivative platform posts.

### Stage 2: Target Channel Selection & Playbook Routing
1. Identify target platform(s) for the campaign.
2. Load matching platform references (`references/<platform>_playbook.md`).

### Stage 3: Hook Engineering & Character Budgeting
Extract the sharpest tension, metric, or discovery from the Foundation Narrative to lead above the fold on each platform:
- **LinkedIn**: < 140 characters (Mobile fold).
- **Twitter / X**: < 280 characters (`Show more` fold).
- **Bluesky**: Total post < 300 graphemes per post (or multi-post thread).
- **Instagram**: < 125 characters (`...more` fold).
- **Reddit**: Descriptive title specifying `[Tech Stack] + [Problem Solved] + [Metric/Trade-off]`.
- **Threads**: Total post < 500 characters.

### Stage 4: Channel-Specific Distillation & Format Assembly
Cut and reformat the Foundation Narrative into the appropriate archetype for each channel:
- **LinkedIn**: Architectural deep-dive (1,300–2,000 chars) with first-comment link.
- **Twitter / X**: Native long-form post (800–2,500 chars) with direct links or micro-thread.
- **Bluesky**: Multi-post thread where every post is strictly $\le 300$ graphemes.
- **Instagram**: 4:5 multi-slide carousel outline + micro-blog caption with DM automation hook.
- **Reddit**: Value-first Markdown self-post (300–800 words, 4-space code indents for Old Reddit).
- **Threads**: Casual, builder-centric post (<500 chars) with strictly 1 `#topic` tag.

### Stage 5: Anti-Pattern & Deslopification Audit
Review all drafts against [references/anti_patterns.md](references/anti_patterns.md):
- [ ] No banned AI words (*"delve", "game-changer", "revolutionary", "testament"*).
- [ ] No mathematical unicode bolding (`𝗕𝗼𝗹𝗱` fonts).
- [ ] Links positioned according to platform rules (1st comment for LinkedIn, direct in-body for X/Bluesky/Threads/Reddit).
- [ ] Hashtags strictly match platform limits (0 for X, 1 for Threads, 0-1 for Bluesky, 1-3 for LinkedIn, 3-5 for Instagram).
- [ ] Technical claims, metrics, and commands verified against reality.
- Once verified, update header: `- **Status**: Ready`.

### Stage 6: Dispatch & Frictionless Clipboard Pipeline
When executing or automating campaign publication (e.g. via Buffer CLI):
1. **Publishing Mode Confirmation Gate**:
   - Always ask the author whether to **Publish Immediately** (`shareNow`), **Add to Queue** (`addToQueue`), or **Schedule for a Specific Time** (`customScheduled`) before dispatching, unless explicitly commanded in the initial prompt.
2. **Safe Validation**: Always run `--dry-run` to validate JSON structures and per-channel constraints before live mutations.
3. **First-Comment Clipboard Pipeline (Free Tier Strategy)**:
   - For platforms where outbound links are placed in the first comment (such as LinkedIn) and the scheduler's automated comment API is restricted behind paid plans, dispatch the post with `mode: shareNow`.
   - **Immediately pipe the pre-formatted First Comment to the user's OS clipboard** (`pbcopy` on macOS, `xclip`/`wl-copy` on Linux).
   - Return the live post URL directly so the author can click the link and press `Cmd+V` / `Ctrl+V` immediately, avoiding forgotten comments and boosting the post's golden-hour engagement signal.

### Stage 7: Post-Dispatch Lifecycle Synchronization & Status Marking
As soon as posts are published or confirmed live:
1. **Mark Campaign as `Published / Live`**:
   - Update `CANONICAL.md` header to `- **Status**: Published / Live` (or `- **Status**: Scheduled` if scheduled for a future milestone).
   - Record publication timestamp.
2. **Record Live URLs**:
   - Append the live post URLs (LinkedIn, Twitter/X, Bluesky, Medium, etc.) directly to `CANONICAL.md` or a `## Live Links` section.
3. **Synchronize Workspace Backlog / Task Trackers**:
   - In repositories tracking active tasks (such as `TODOs.md`), move the campaign to the **`## ✅ Completed Tasks`** section tagged `[DONE - PUBLISHED]`.
   - Remove or resolve the corresponding item from the active backlog.
