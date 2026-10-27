---
name: social-copy
description: >
  Editorial workflow and platform playbooks for drafting developer-native social
  media copy and campaigns. Extracts technical evidence via git log inspections
  or /grill-me interviews, establishes a canonical foundation narrative
  (CANONICAL.md), tailors derivatives for connected platforms (such as LinkedIn,
  X/Twitter, Bluesky, and others), and enforces anti-slop guidelines. Activate
  when drafting social media posts, writing release announcements, authoring
  technical threads, or running developer campaigns.
license: Apache-2.0
compatibility:
  skills:
    - buffer
    - deslopify
metadata:
  category: writing
  tags: "social-media, developer-marketing, writing, publishing, campaigns"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.3"
  catalog: https://skills.danicat.dev
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

### 2. Hook Economy & Contextual Judgment (No "Banned Lists")
The first 1–2 lines (`~140 chars` on mobile, `~210 chars` on desktop) before the `...see more` fold are the highest-leverage space in a post. Treat them as an exercise in **editorial judgment and reader empathy**, not a mechanical blacklist:
- **Why "Banned Lists" Fail:** Relying on a static list of "banned words" or "banned openers" fails in both directions: it creates the false impression that any sentence avoiding the blacklist is automatically good copy, and it blindly forbids openings (such as a personal milestone or series callback) that are genuinely effective when they *are* the story.
- **The Reader-Utility Gate (No Self-Referential Preambles or Chronological Recaps):** A cold reader scanning an algorithmic feed asks *What does this solve for me?* in under two seconds. Avoid spending the pre-truncation window on **author-centric housekeeping** (explaining why you haven't posted lately, how busy your week was, or how excited you feel) or **chronological throat-clearing** (recapping a previous installment before stating today's point). Preambles that center on the author's schedule rather than the reader's problem starve `...see more` expansion clicks even when the body and visuals are strong.
- **Ground the Hook in the Real Story:** Open with the genuine technical tension, quantifiable engineering outcome (latency, cost, or build-time compression), architectural trade-off, or participatory design question from the source material, and weave in background or series context once the reader is hooked.

### 3. The "Value-First" / "Zero-Click" Principle
Every post should provide actionable insight directly in the timeline. Readers should learn something valuable even if they never click an external link.

### 4. Voice Preservation & User Narrative Copyediting
To ensure genuine author authenticity:
- **Preserve User Quotes 1:1 in Canonical**: Any live comments, raw reflections, and spoken quotes from the author must be recorded verbatim (1:1) in a dedicated `## References / Sources` section inside `CANONICAL.md`.
- **Infuse the Author's Voice into Derivative Copy**: These 1:1 remarks are the primary source for the author's authentic cadence, idioms, and engineering perspective.
- **Copyedit for Final Polish**: While preserving the narrative spirit, tone, and specific turns of phrase as originally typed, apply professional copyediting during the final draft to ensure clean syntax, grammar, and publication-grade polish.

---

## Frontmatter & Metadata Standards for Copy Files

All campaign artifacts—the canonical foundation narrative (`CANONICAL.md`) and every individual platform copy file (`linkedin.md`, `twitter.md`, `bluesky.md`, `threads.md`, `instagram.md`, `reddit.md`)—**MUST use YAML frontmatter for metadata followed by Markdown content**.

### Standard Frontmatter Schema & Canonical Layout

```markdown
---
title: "Title or Working Headline"
platform: canonical | linkedin | twitter | bluesky | threads | instagram | reddit
status: draft | review | ready | scheduled | published
target_audience: "Target developer persona or subreddit"
character_count: 1420
media:
  - type: image | video
    path: "assets/diagram.png"
    alt: "Architecture diagram showing event pipeline"
    description: "Dark-mode sequence diagram illustrating worker queues"
---

# Post Content / Narrative Begins Here (Markdown)

## Core Narrative & Technical Breakdown
...

## References / Sources
### Live User Comments & Voice Log (Verbatim 1:1)
- "Actual unedited quote from the user during chat/interview..."
- "Another raw observation about the bug or performance tradeoff..."

### Technical & Git References
- Repo: `owner/repo` (commit `<hash>`)
- PR: `#123`
```

Frontmatter rules:
- **`status`**: Current lifecycle state (`draft`, `review`, `ready`, `scheduled`, `published`).
- **`media`**: Required array detailing media attachments (type, path/url, alt text, description).
- **`character_count`**: Character, grapheme, or word count to verify platform constraints.

---

## Campaign Lifecycle States

Every social campaign follows a strict 5-state lifecycle tracked explicitly in the YAML frontmatter of `CANONICAL.md` and all derivative files:

| State | Definition & Trigger | Required Artifacts |
| :--- | :--- | :--- |
| `draft` | Initial research, deep git inspection, `/grill-me` extraction, and authoring `CANONICAL.md`. **Zero derivative posts allowed in this state.** | `CANONICAL.md` |
| `review` | Canonical copy or individual derivative draft presented to author for review. Awaiting explicit user approval. | `CANONICAL.md` or platform copy files |
| `ready` | Explicit human approval granted, copy deslopified, character budget verified, and media attached. | Approved `CANONICAL.md` and platform files |
| `scheduled` | Dispatched to a queue or scheduled for a specific timestamp (via Buffer CLI or native scheduler). | Platform files with scheduled date/time |
| `published` | Dispatched live (`shareNow`) or confirmed live on external channels. | Live post URLs recorded in frontmatter & body |

---

## 7-Stage Social Campaign Workflow

Follow this procedure when creating, publishing, or auditing social campaigns:

### Stage 1: Evidence Discovery & Grounding
Never hallucinate features, metrics, or claims.
1. **Inspect Deep Git & Source References**:
   - **No Shallow Summaries / No One-Line Shortcuts**: Never rely on `git log --oneline` or brief commit titles alone. One-line summaries hide critical architectural nuance, structural refactors, and behavioral details.
   - Always run full `git log` with commit bodies, inspect diff statistics (`git show --stat`), check architecture decision records (ADRs), and inspect source documentation directly across all referenced repositories.
2. **Interview via `/grill-me` & Live User Log**:
   - If the source is an open-ended topic or raw idea, conduct an interactive interview or recommend `/grill-me` to extract the author's real friction points, unexpected discoveries, and authentic engineering voice.
   - **Capture Live Comments 1:1**: Every raw remark, feedback note, or chat input from the user must be logged verbatim into the `## References / Sources` section of `CANONICAL.md`.
3. **Draft the Canonical Foundation Narrative (`CANONICAL.md`)**:
   Author a comprehensive, unconstrained master document using YAML frontmatter followed by Markdown content:
   - Core premise & real motivation.
   - Exact repositories and what was specifically built/refactored in each.
   - Concrete performance observations (time-to-first-token, reasoning depth, compile times).
   - Architectural breakthroughs, failure modes, and trade-offs.
   - Philosophical takeaways and references to published writing.
   - **Mandatory `## References / Sources` section**: Houses all verbatim 1:1 user comments and technical source links.
   > [!IMPORTANT]
   > **Continuous Master Synchronization**: Whenever new evidence is collected (whether through proactive deep git inspection or after user feedback/pushback), immediately update `CANONICAL.md`—including appending any new user comments—before adjusting derivative platform posts.

### Stage 2: Canonical Approval Gate (Mandatory Human-in-the-Loop)
> [!CAUTION]
> **STRICT STOPPING GATE**: No individual post or platform copy (`linkedin.md`, `twitter.md`, `bluesky.md`, etc.) may be generated until the user has explicitly reviewed and approved `CANONICAL.md`.
1. Present `CANONICAL.md` to the user for explicit review.
2. Incorporate revisions until the user gives clear, unambiguous approval (e.g., *"approved"*, *"canonical looks great"*, *"proceed with platform posts"*).
3. Update `CANONICAL.md` frontmatter status to `status: ready`.
4. Only after this approval is received, proceed to Stage 3 and Stage 4.

### Stage 3: Target Channel Selection & Playbook Routing
1. Identify target platform(s) for the campaign.
2. Load matching platform references (`references/<platform>_playbook.md`).

### Stage 4: Channel-Specific Adaptation & Format Assembly
Cut and reformat the approved Foundation Narrative into the appropriate archetype for each channel. Each file MUST use YAML frontmatter followed by Markdown content:
- **LinkedIn** (`linkedin.md`): Architectural deep-dive (1,300–2,000 chars) with direct in-body link(s) to the primary article, documentation, or repository.
- **Twitter / X** (`twitter.md`): Native long-form post (800–2,500 chars) with direct links or micro-thread.
- **Bluesky** (`bluesky.md`): Multi-post thread where every post is strictly <= 300 graphemes.
- **Instagram** (`instagram.md`): 4:5 multi-slide carousel outline + micro-blog caption with DM automation hook.
- **Reddit** (`reddit.md`): Value-first Markdown self-post (300–800 words, 4-space code indents for Old Reddit).
- **Threads** (`threads.md`): Casual, builder-centric post (<500 chars) with strictly 1 `#topic` tag.

> [!CAUTION]
> **Strictly Sequential Channel Drafting (One Channel at a Time)**:
> NEVER generate all platform drafts (`linkedin.md`, `twitter.md`, `bluesky.md`, etc.) simultaneously. Generating all channels upfront wastes time and tokens if the core narrative or hook needs revision. Always draft and iterate on **one single primary channel first** (e.g., `linkedin.md`) until the user explicitly approves the copy, and only then adapt the approved text to secondary channels one by one.

> [!IMPORTANT]
> **Hook Economy Above the Fold**:
> The first 1–2 lines (`~140 chars` on mobile, `~210 chars` on desktop) before `...see more` carry the highest opportunity cost in the post. Do not waste them on chronological throat-clearing or generic filler—and do not rely on a mechanical "banned list" that tricks you into writing synthetic copy just because it avoids certain words. Evaluate the hook in context: does it immediately convey the core problem, insight, or human moment from the author's actual work?

> [!NOTE]
> **Infusing User Voice with Copyediting**: Draw heavily on the 1:1 user comments captured in the Canonical's `## References / Sources` section to infuse the author's personality, perspective, and phrasing into each channel post. Preserve the author's authentic narrative while applying professional copyediting to ensure a polished appearance.

> [!IMPORTANT]
> **Mandatory Native Media & Multi-Image Parity (The Link-Card Override)**:
> - Every single social post MUST include at least one native media item (picture or video)—such as an architectural diagram, Ray.so/Carbon dark-mode code card, terminal recording, benchmark plot, carousel slide, or demo clip. Naked, text-only posts are strictly prohibited across all platforms.
> - **Dual Structural Function**: Native visual attachments both arrest scroll velocity (multiplying dwell time and comment depth) and **override compact OpenGraph link-preview cards** when paired with an in-body URL—allowing the post to render as a full-viewport visual card while keeping links clickable inside the text.
> - **Never Drop Multi-Image Assets**: When a campaign or article has multiple visual assets declared in `CANONICAL.md` (such as a hero cover plus UI screenshots or architecture diagrams), preserve **all** of them in each channel's YAML frontmatter `media:` array up to the platform's multi-image limit (e.g., up to 9 images on LinkedIn, up to 4 images on X and Bluesky). Never silently reduce a multi-image campaign to a single image.

### Stage 5: Self-Critique Rubric, Anti-Pattern & Deslopification Audit
Before presenting any draft to the user, run this 4-step **Pre-Presentation Self-Critique Rubric** alongside [references/anti_patterns.md](references/anti_patterns.md) and the `deslopify` skill:
1. **The Line-1 Deletion Test**: Temporarily delete your opening sentence or paragraph. Does Sentence 2 state the technical problem, metric, or architectural tension more directly? If yes, permanently delete Sentence 1.
2. **The Cold-Stranger Test**: Read only the first `140` characters. Do they talk about *the author's publishing schedule/feelings* (*"I've been quiet lately"*, *"In my previous post"*, *"Excited to share"*) or *a concrete engineering problem/outcome* that a stranger cares about?
3. **The Link-Card Override Check**: Are all primary outbound URLs placed directly in the post body *and* paired with at least one native visual asset in the frontmatter `media:` array so the feed renders a full visual card rather than a cropped link preview or buried first comment?
4. **The Feed-Horizon Check**: Does the proposed publishing mode respect the target platform's decay horizon (see the Platform Physics Matrix in Stage 6)?

Checklist:
- [ ] **Passed the 4 Self-Critique Tests** (Line-1 Deletion, Cold-Stranger, Link-Card Override, Feed-Horizon).
- [ ] **Sequential Drafting Enforced**: Only one platform draft is generated at a time prior to user approval of the primary channel copy.
- [ ] Free of synthetic AI filler and hollow marketing clichés.
- [ ] No mathematical unicode bolding (`𝗕𝗼𝗹𝗱` fonts).
- [ ] Links positioned directly in the post body across technical platforms (LinkedIn, X, Bluesky, Threads, Reddit); never hide primary links in the first comment.
- [ ] Hashtags strictly match platform limits (0 for X, 1 for Threads, 0-1 for Bluesky, 1-3 for LinkedIn, 3-5 for Instagram).
- [ ] Technical claims, metrics, and commands verified against reality.
- [ ] **At least one media item (image or video) is attached and documented in frontmatter.**

### Stage 6: Individual Copy Human-in-the-Loop Approval Gate & Dispatch
> [!CAUTION]
> **STRICT HUMAN-IN-THE-LOOP APPROVAL FOR EVERY COPY**: Every individual platform post draft MUST be presented to the user and receive explicit human-in-the-loop approval before submitting, dispatching, or scheduling. Never publish or schedule unapproved drafts.

When human approval is granted and dispatching/automating publication (e.g. via Buffer CLI):
1. **Publishing Mode Confirmation Gate**:
   - Always ask the author whether to **Publish Immediately** (`shareNow`), **Add to Queue** (`addToQueue`), or **Schedule for a Specific Time** (`customScheduled`) before dispatching, unless explicitly commanded in the initial prompt.
2. **Platform Physics & Feed-Horizon Cadence Matrix**:
   Match your publishing cadence and timing to the target platform's algorithmic decay horizon:

   | Platform | Feed Half-Life | Intra-Day Multi-Posting Effect | Optimal Cadence & Timing Heuristic | Primary Visual & Link Mechanics |
   | :--- | :--- | :--- | :--- | :--- |
   | **LinkedIn** | **18–48 hours** *(Long-horizon authority graph)* | **Negative marginal daily reach**: Creator-diversity caps throttle competing same-day posts so 2 posts/day yield fewer total views than 1. | **Strictly max 1 post / 24h**. Schedule during target audience's mid-week work hours or Sunday evening prep; avoid Friday afternoon wind-down. | Direct in-body URL + native diagram/carousel (`up to 9 images`) to override compact link previews. |
   | **Twitter / X** | **1–3 hours** *(Real-time velocity stream)* | **Compounds daily reach**: Spaced multi-post launch sequences multiply daily impressions and outbound clicks. | **2–3h+ spacing buffer** between standalone posts (or chain as a Thread). Strong affinity for mid-week & weekend builder demos. | Direct in-body URL + demo video, UI screenshot, or code card (`up to 4 images`). |
   | **Bluesky** | **1–4 hours** *(Chronological + custom feeds)* | Safe when spaced `1–2h+` apart or chained as multi-post threads. | **1–2h+ spacing buffer** between standalone broadcasts. | Direct in-body URL + alt-text indexed visuals (`up to 4 images`) or rich link card. |
   | **Threads** | **4–12 hours** *(Interest graph stream)* | Safe with `2–3h+` spacing. | Casual builder cadence; strictly **1 Topic Tag**. | Direct in-body URL + visual card. |
   | **Reddit** | **12–24 hours** *(Subreddit hot/upvote decay)* | Rapid multi-posting triggers spam filters and moderator removal. | Max 1 self-post per subreddit per launch; honor the 9:1 contribution ratio. | Value-first Markdown self-post with inline links and diagrams. |

3. **Safe Validation**: Always run `--dry-run` to validate JSON structures and per-channel constraints before live mutations.
4. **Direct In-Body Link & Programmatic Multi-Image Asset Wiring**:
   - Include primary outbound URLs (blog post, documentation, or GitHub repo) directly in the post body on LinkedIn, X, Bluesky, Threads, and Reddit, paired with the native image/video assets (`assets` array) so the post renders as a visual card or multi-image gallery rather than a bare link preview.
   - **Never Hand-Code `assets` Payloads**: Always construct the API/CLI `assets` array programmatically from the channel file's YAML frontmatter `media:` list, and assert `len(payload.assets) == len(frontmatter.media)` before and after dispatch so images are never accidentally dropped.
   - Because the primary URL lives inside the post body, posts can be safely scheduled (`customScheduled` or `addToQueue`) without needing manual first-comment follow-ups.

### Stage 7: Post-Dispatch Lifecycle Synchronization & Status Marking
As soon as posts are published or confirmed live:
1. **Mark Campaign as `published`**:
   - Update frontmatter `status: published` in `CANONICAL.md` and channel copy files.
   - Record publication timestamp.
2. **Record Live URLs**:
   - Append live post URLs (LinkedIn, Twitter/X, Bluesky, Reddit, etc.) directly into `CANONICAL.md` and the respective copy file.
3. **Synchronize Workspace Backlog / Task Trackers**:
   - If the active workspace tracks campaigns in a backlog or task file, mark the campaign as published and resolve the corresponding active item.
