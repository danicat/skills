# Social copy anti-patterns and slop checklist

Checklist of writing patterns, platform missteps, and synthetic AI tells that hurt credibility, reduce distribution, and cause reader fatigue.

---

## 1. Synthetic AI tells and editorial judgment

> [!IMPORTANT]
> **Why "banned lists" fail in social copy:**
> Treating anti-patterns as a rigid banned-word list fails in both directions: anything omitted from the list slips through while sounding synthetic, and valid openings (such as a real milestone) get blocked regardless of context. Treat the items below as **diagnostic signals**, not a mechanical blacklist.

### Common synthetic AI tells and empty modifiers
Watch out for generic filler phrases that substitute hype for substance:
- *"In today's fast-paced digital world / landscape..."*
- *"Delve into / Let's dive deep into..."*
- *"A testament to..."*
- *"Game-changer / Revolutionary / Paradigm shift"*
- *"Unleash the power of / Unlock seamless potential..."*
- *"Crucial / Paramount / Vital"* (when used as empty modifiers)
- *"Navigating the complexities of..."*
- *"Buckle up 🧵 / Mind-blowing 🤯"*

### Structural and workflow anti-patterns
- **The self-referential preamble trap (failing the Cold-Stranger and Line-1 Deletion tests):** Feeds truncate after ~140 characters on mobile (~210 on desktop). Spending those opening words on author housekeeping (*"I've been heads down working on new content so you haven't heard from me..."*) or chronological recaps (*"In Part 3 of my series, I showed..."*) wastes the fold. Run the **Line-1 Deletion test**: if deleting Sentence 1 lets Sentence 2 open with the technical problem, metric, or tension, cut Sentence 1.
- **Inventing synthetic copywriter strawmen:** Never invent dramatic problems or claims missing from the author's real code or article just to create a punchy hook.
- **Simultaneous multi-channel draft generation before core approval:** Never generate `linkedin.md`, `twitter.md`, `bluesky.md`, and other files all at once. Draft and iterate on **one primary channel first** (for example, `linkedin.md`) until the user approves it, then adapt secondary channels one by one.
- **Negative parallelism:** Avoid repetitive *"It's not just about X, it's about Y"* structures. State what it is directly.
- **Mid-sentence em dashes:** Never use mid-sentence em dashes, en dashes, or spaced double hyphens. Split clauses with periods, commas, or colons.
- **Rule-of-threes addiction:** Avoid forcing ideas into artificial triplets when two or four points match reality better.

---

## 2. Platform-specific anti-patterns

### LinkedIn anti-patterns
- **Wasted above-the-fold hooks (`...see more` failure):** Opening with chronological recaps (*"In my previous post..."*, *"Today I published..."*) or scheduling updates burns the 140-character mobile preview without giving peers a technical reason to expand.
- **Formulaic AI textbook summaries:** Writing a sterile, bulleted overview instead of sharing real design trade-offs and production lessons.
- **Intra-day multi-posting:** Because LinkedIn scores posts over an `18` to `48` hour horizon with creator-diversity caps, publishing two posts within `24` hours throttles both so severely that two same-day posts yield fewer daily impressions than one.
- **End-of-week wind-down drops:** Publishing heavy deep dives on Friday afternoons loses dwell time compared to mid-week or Sunday evening windows.
- **Naked text-only posts or bare link previews:** Publishing without a native visual asset (diagram, code card, UI screenshot, or carousel) loses `2x` to `3x` discussion depth and lets in-body URLs collapse the post into a compact OpenGraph link card.
- **"Broetry" and fake epiphanies:** Dramatic single-line sentences forcing mundane daily chores into software analogies (*"I watched my espresso drip this morning and realized Kafka partitions work the same way..."*).
- **Unicode bold or italic glyphs:** Formatting copy with mathematical Unicode fonts (`𝗕𝗼𝗹𝗱`) breaks screen readers, ruins search indexing, and inflates character counts.
- **Generic hashtag stuffing:** Using `5+` hashtags (`#tech #ai #software #coding #innovation`) triggers spam signals.
- **"Link in first comment 👇" evasions:** Hiding the main URL from the post body. Direct in-body URLs paired with native visuals outperform first-comment links, while LinkedIn's `Most Relevant` comment sorting buries unpinned comments once discussion starts and drops them on reshares.

### X (Twitter) anti-patterns
- **Intra-day rapid burst posting:** Posting multiple standalone tweets minutes apart saturates feeds without a `2` to `3` hour spacing buffer. Group connected points into a thread instead.
- **Hashtag clutter:** Hashtags add visual noise under semantic feed ranking. Keep hashtags at `0`.
- **Vague curiosity gaps:** *"10 tips senior engineers don't want you to know"* or *"I changed one line and you won't believe what happened"*.
- **Unreadable code walls:** Pasting unformatted raw code without clean visuals or syntax highlighting.

### Bluesky anti-patterns
- **Algorithmic evasions:** Writing *"Link in bio"* or *"Link in first comment"*. Bluesky does not penalize external links; hiding links signals platform unfamiliarity.
- **Missing image alt text:** Skipping `[ALT]` descriptions on code screenshots or diagrams breaks accessibility norms and triggers mutes.
- **Engagement farming:** *"Thoughts? Agree? Repost if you code in Go!"* drives blocks and mutes.

### Instagram anti-patterns
- **Square (`1:1`) carousels when `4:5` fits:** Using `1:1` wastes `35%` of vertical viewport height on mobile.
- **Unreadable mobile code:** Rendering code smaller than `24pt` equivalent forces readers to pinch-to-zoom.
- **Naked "Link in Bio" drops:** Sending readers through multiple clicks without a focused landing link or DM trigger.

### Reddit anti-patterns
- **Clickbait and marketing hype:** Titles like *"Why AI will replace devs"* or *"Check out my revolutionary tool"*.
- **Paywalled or gated links:** Submitting paywalled articles or forced email gates.
- **Violating the `9:1` ratio:** Dropping self-promotional links without genuine participation in community threads.
- **URL shorteners:** `bit.ly`, `t.co`, and heavy UTM parameters trigger instant AutoModerator removal.

### Threads anti-patterns
- **Hashtag overuse:** Only the **first** `#tag` indexes as a topic tag; extra tags add noise without discovery value.
- **Engagement bait:** *"Comment LINK"* triggers Meta's engagement-bait downranking filters.
- **Uncontextualized link drops:** Posting a bare URL with no standalone explanation.

---

## 3. Claim validation and fact-checking

Before presenting or scheduling social copy, verify:
- [ ] Latency, memory, and cost figures match reproducible benchmarks or post-mortems.
- [ ] Version numbers, language syntax, and CLI flags match current stable releases.
- [ ] Architecture trade-offs name what was sacrificed (memory, CPU, or complexity).
- [ ] Zero unverified hype appears.
- [ ] **At least one native media item** (diagram, screenshot, video, or code card) is attached in frontmatter. Naked text-only posts are prohibited.
