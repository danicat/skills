---
name: social-copy
description: >
  Editorial workflow and platform playbooks for developer social media copy and
  campaigns. Extracts technical evidence from git history or author interviews,
  builds a canonical narrative (CANONICAL.md), adapts posts sequentially for
  LinkedIn, X, Bluesky, Instagram, Reddit, and Threads, and checks for AI
  cliches. Activate when drafting or auditing developer social posts and launches.
license: Apache-2.0
metadata:
  category: writing
  tags: "social-media, developer-marketing, copywriting, campaigns, devrel"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.5.0"
  catalog: https://skills.danicat.dev
---

# Social copy playbook

Draft, audit, and schedule developer-native social media posts and multi-channel launches grounded in verified engineering work rather than marketing hype.

---

## 1. Playbook routing and operating modes

Load only the reference files needed for the target channels:

- **LinkedIn**: Read [references/linkedin_playbook.md](references/linkedin_playbook.md) for `1,300` to `2,000` character engineering field notes, PDF carousels, and in-body link placement.
- **X (Twitter)**: Read [references/twitter_playbook.md](references/twitter_playbook.md) for X Premium long-form posts (`800` to `2,500` chars), standard `280`-character posts, and `3` to `5` post micro-threads.
- **`Bluesky`**: Read [references/bluesky_playbook.md](references/bluesky_playbook.md) for AT Protocol posts (`300` graphemes max), `180s` video clips, and mandatory image `alt` text.
- **Instagram**: Read [references/instagram_playbook.md](references/instagram_playbook.md) for `4:5` carousels (`6` to `10` slides sweet spot, `20` max), micro-blog captions, and DM triggers.
- **Reddit**: Read [references/reddit_playbook.md](references/reddit_playbook.md) for zero-click Markdown self-posts across technical communities (`r/programming`, `r/golang`, `r/webdev`, `r/MachineLearning`, `r/devops`).
- **Threads**: Read [references/threads_playbook.md](references/threads_playbook.md) for builder posts under `500` characters with a single topic tag.
- **Anti-patterns**: Read [references/anti_patterns.md](references/anti_patterns.md) before presenting any draft to check for AI tells, Unicode bold fonts, and platform missteps.

### Operating modes

- **Campaign mode (new launches)**: Follow the seven-stage workflow starting from `CANONICAL.md`.
- **Audit mode (existing drafts on disk)**: Never rewrite or mutate an author's draft file silently. Return a numbered list of suggested improvements and wait for explicit user approval before modifying files.

---

## 2. Core voice and hook judgment

1. **Peer-to-peer engineering voice**: Write like a senior engineer speaking to peers. Name the concrete bottleneck, metric, or failure mode in Line 1, state real trade-offs (memory, latency, complexity), and use exact technical nouns (*lock-free ring buffer*, *connection pool*) instead of slogans.
2. **Hook economy without banned-word lists**: The visible preview before `...see more` (`140` chars on mobile, `210` chars on desktop) carries the highest opportunity cost. Static banned-word lists fail in both directions: synthetic copy passes by dodging listed words, while genuine personal milestones get blocked. Judge the opening lines by reader utility: within two seconds, does a cold reader see a concrete engineering problem or outcome rather than author housekeeping (*"I've been quiet lately"*, *"In Part 3 of my series"*)?
3. **Standalone zero-click value**: Deliver a complete technical insight directly in the timeline so readers learn something useful even without clicking an outbound URL.
4. **Clean punctuation without em dashes**: Break clauses with periods, commas, or colons. Never use mid-sentence em dashes, en dashes, or spaced double hyphens.

---

## 3. Frontmatter schema and lifecycle states

Every campaign file (`CANONICAL.md`, `linkedin.md`, `twitter.md`, `bluesky.md`, `instagram.md`, `reddit.md`, `threads.md`) uses YAML frontmatter followed by Markdown body text:

```markdown
---
title: "Working headline"
platform: canonical | linkedin | twitter | bluesky | threads | instagram | reddit
status: draft | review | ready | scheduled | published
target_audience: "Target developer persona or subreddit"
character_count: 1420
media:
  - type: image | video
    path: "assets/diagram.png"
    alt: "Sequence diagram of bounded worker queues"
    description: "Dark-mode architecture flow"
---

# Post body or canonical narrative

## References and sources
### Verbatim user voice log (1:1)
- "Exact unedited quote from the author during chat or interview."

### Technical and git references
- Repo: `owner/repo` (commit `<hash>`, PR `#123`)
```

| State | Trigger and rule | Required files |
| :--- | :--- | :--- |
| `draft` | Evidence gathering, author interview, and writing `CANONICAL.md`. **Zero platform derivatives allowed yet.** | `CANONICAL.md` |
| `review` | `CANONICAL.md` or a single channel draft presented to the author for sign-off. | `CANONICAL.md` or active channel file |
| `ready` | Explicit user approval granted, AI tells removed, character budget verified, and media attached. | Approved `CANONICAL.md` and channel files |
| `scheduled` | Queued or scheduled for a target timestamp via Buffer CLI or native scheduler. | Channel files with scheduled timestamp |
| `published` | Published live (`shareNow`) or confirmed live on external feeds. | Live URLs recorded in frontmatter and body |

---

## 4. Seven-stage social campaign workflow

### Stage 1: Evidence discovery and canonical narrative
Never invent features, benchmarks, or war stories.
1. **Inspect full git history and docs**: Run full `git log` with commit bodies, `git show --stat` diffs, design docs, and benchmark outputs. Never rely on `git log --oneline` commit titles alone.
2. **Interview the author one question at a time**: When working from an open-ended idea, interview the author one question at a time to surface real friction points, surprises, and trade-offs. Record every raw user remark verbatim (`1:1`) under `## References and sources` in `CANONICAL.md`, and sync any later user feedback to `CANONICAL.md` before updating channel drafts.
3. **Draft `CANONICAL.md`**: Document the real motivation, repositories changed, measured performance deltas, failure modes, trade-offs, and verbatim `1:1` user quotes.

### Stage 2: Canonical approval gate
> [!CAUTION]
> **Strict stopping gate**: Never generate `linkedin.md`, `twitter.md`, `bluesky.md`, or any other channel file until the user explicitly reviews and approves `CANONICAL.md`. Once approved, set `status: ready`.

### Stage 3: Target channel selection
Identify the target platforms for the campaign and load each matching `references/<platform>_playbook.md`.

### Stage 4: Sequential channel adaptation
> [!CAUTION]
> **One channel at a time**: Never generate all platform files at once. Draft and refine **one primary channel first** (such as `linkedin.md`) until the user approves it, then adapt secondary channels one by one.

Infuse the author's `1:1` quotes from `CANONICAL.md` while copyediting for clean grammar and platform limits:
- **LinkedIn** (`linkedin.md`): `1,300` to `2,000` chars (`3,000` cap) with direct in-body URLs and up to `9` images or a PDF carousel.
- **X (Twitter)** (`twitter.md`): Check account tier first. Use `800` to `2,500` char long-form posts (`25,000` cap) only on **X Premium**; use `180` to `280` char single posts or `3` to `5` post micro-threads on **standard X accounts and standard single-post API queues** (up to `4` images or video).
- **`Bluesky`** (`bluesky.md`): Single post or thread with every post at or under `300` graphemes, plus mandatory `alt` text (up to `4` images or `180s` video).
- **Instagram** (`instagram.md`): `4:5` carousel (`6` to `10` slides recommended, `20` max) and caption under `2,200` chars (`<125` char hook).
- **Reddit** (`reddit.md`): Value-first Markdown self-post (`300` to `800` words, `4`-space code indents for Old Reddit).
- **Threads** (`threads.md`): Builder post under `500` chars with strictly `1` topic tag (up to `20` carousel items).

**Mandatory native media and link-card override**:
- Every post must attach at least one visual asset (architecture diagram, dark-mode code card, screenshot, benchmark chart, or demo video) in `media:`. Never publish naked text-only posts.
- Pairing an in-body URL with native media overrides compact Open Graph link cards so feeds render full-height visuals while keeping links clickable in the text.
- Preserve every campaign image from `CANONICAL.md` up to each platform's multi-image limit, and verify `len(payload.assets) == len(frontmatter.media)` when building CLI or API payloads.

### Stage 5: Pre-presentation self-critique
Run these checks alongside [references/anti_patterns.md](references/anti_patterns.md) (and optionally load the `deslopify` skill for deeper prose cleanup) before showing a draft:
1. **Line-1 deletion test**: Delete Sentence 1 temporarily; if Sentence 2 opens with stronger technical tension, keep Sentence 2 as your opener.
2. **Cold-stranger test**: Confirm the first `140` characters address an engineering problem or result rather than the author's posting schedule.
3. **Formatting and link check**: Place primary URLs directly in the post body on LinkedIn, X, `Bluesky`, Threads, and Reddit instead of hiding them in a first comment. Avoid Unicode bold fonts and mid-sentence em dashes, attach descriptive `alt` text to every image, and respect platform hashtag caps (`0` on X, `1` on Threads, `0` to `1` on `Bluesky`, `1` to `3` on LinkedIn, `3` to `5` on Instagram).

### Stage 6: Per-post approval and cadence check
Get explicit user approval for every individual post before scheduling or publishing. Ask whether to **Publish Immediately** (`shareNow`), **Add to Queue** (`addToQueue`), or **Schedule** (`customScheduled`) unless already specified, test payloads with `--dry-run`, and match each feed's decay horizon:

| Platform | Feed half-life | Same-day multi-posting effect | Cadence rule | Visual and link mechanics |
| :--- | :--- | :--- | :--- | :--- |
| **LinkedIn** | `18h` to `48h` | Creator-diversity caps throttle same-day posts (`2` posts yield fewer views than `1`). | Max `1` post per `24h` during mid-week work hours or Sunday evening; skip Friday afternoon. | In-body URL + native visual (`up to 9` images or PDF). |
| **X (Twitter)** | `1h` to `3h` | Spaced standalone posts compound daily impressions and clicks. | Space standalone posts `2h` to `3h+` apart, or chain as a thread. Strong on weekends too. | In-body URL + demo video, screenshot, or code card (`up to 4` images). |
| **`Bluesky`** | `1h` to `4h` | Safe when spaced `1h` to `2h+` apart or chained as threads. | Space standalone posts `1h` to `2h+` apart. | In-body URL + `alt`-indexed visuals (`up to 4` images or `180s` video). |
| **Threads** | `4h` to `12h` | Safe with `2h` to `3h+` spacing. | Casual builder cadence; strictly `1` topic tag. | In-body URL + visual card (`up to 20` items). |
| **Reddit** | `12h` to `24h` | Rapid multi-posting triggers spam filters and moderator removal. | Max `1` self-post per community per launch; honor the `9:1` participation ratio. | Value-first Markdown self-post with inline links and diagrams. |

### Stage 7: Post-dispatch status sync
Once live or confirmed:
1. Set `status: published` and record the timestamp in `CANONICAL.md` and each published channel file.
2. Append live post URLs to `CANONICAL.md` and the corresponding channel files.
3. Update any active campaign backlog or task tracker in the workspace.
