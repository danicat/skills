# Social Copy Anti-Patterns & Slop Checklist

Exhaustive checklist of writing patterns, platform missteps, and synthetic AI tells that destroy credibility, suppress algorithmic distribution, and trigger audience fatigue.

---

## 1. Synthetic AI Tells & Editorial Judgment

> [!IMPORTANT]
> **Why "Banned Lists" Fail in Social Copy:**
> Treating anti-patterns as a rigid "banned word/phrase list" is a trap in both directions: it makes you think anything *not* on the list is automatically valid (encouraging synthetic copywriter formulas that dodge specific words while still sounding fake), and it makes you think patterns on the list are *always* wrong regardless of context. Use the patterns below as **diagnostic signals for editorial judgment**, not a mechanical blacklist.

### Common Synthetic AI Tells & Empty Modifiers
Watch out for generic filler phrases that substitute hype for substance:
- *"In today's fast-paced digital world / landscape..."*
- *"Delve into / Let's dive deep into..."*
- *"A testament to..."*
- *"Game-changer / Revolutionary / Paradigm shift"*
- *"Unleash the power of / Unlock seamless potential..."*
- *"Crucial / Paramount / Vital" (when used as empty adverbs)*
- *"Navigating the complexities of..."*
- *"Buckle up 🧵 / Mind-blowing 🤯"*

### Structural & Workflow Anti-Patterns
- **The Self-Referential Preamble Trap (Failing the Cold-Stranger & Line-1 Deletion Tests):** Because feeds truncate after ~140 characters on mobile (~210 on desktop), spending the first lines on **author-centric housekeeping** (*"I've been heads down working on new content so you haven't heard from me..."*, *"I'm usually very grounded in my posts, but..."*) or **chronological throat-clearing** (*"In Part 3 of my series, I showed..."*) fails the reader-utility filter before `...see more`. Always run the **Line-1 Deletion Test**: if deleting your opening sentence lets Sentence 2 state the technical problem, metric, or tension more directly, delete Sentence 1.
- **Inventing Synthetic Copywriter Strawmen:** Never invent dramatic problems or claims that are not in the author's actual article or code just to manufacture a "punchy" hook. Ground every claim in the author's real perspective and work.
- **Simultaneous Multi-Channel Draft Generation Before Core Copy Approval:** Never generate all platform derivatives (`linkedin.md`, `twitter.md`, `bluesky.md`, etc.) at the same time. Drafting all channels simultaneously wastes tokens and review cycles if the core hook, angle, or narrative framing needs adjustment. Always draft and iterate on **one single primary channel first** (e.g., `linkedin.md`) until the user explicitly approves the copy, and only then adapt the approved text to secondary channels one by one.
- **Negative Parallelism:** Avoid repetitive *"It's not just about X, it's about Y"* structures. State what it is directly.
- **Em-Dash Overdose:** Avoid multiple em-dashes (`—`) per post. Use concise sentences or colons.
- **Rule of Threes Addiction:** Avoid forcing ideas into artificial triplets when two or four points are more accurate.

---

## 2. Platform-Specific Anti-Patterns

### LinkedIn Anti-Patterns
- **Wasted Above-the-Fold Hooks (`...see more` Failure):** Opening a LinkedIn post with chronological recaps (*"In my previous post..."*, *"Today I published..."*) or self-referential status updates (*"I've been quiet this week because..."*) burns the entire 140-character mobile preview window without giving peer engineers a technical reason to expand the post.
- **Formulaic AI Textbook Summaries:** Writing a post that reads like a sterile, bulleted AI textbook overview rather than a grounded senior engineer sharing real architectural trade-offs and production lessons.
- **Intra-Day Multi-Posting (Negative Marginal Daily Reach):** Because LinkedIn's feed scores posts over an 18–48 hour horizon with creator-diversity caps, publishing 2+ posts within 24 hours throttles both posts so severely that two same-day posts generate **fewer total daily impressions than a single post**.
- **End-of-Week Wind-Down Drops:** Publishing heavy architectural deep-dives during Friday afternoon wind-down windows in your target audience's primary timezone suffers steep reach and dwell loss compared to mid-week or Sunday evening windows.
- **Naked Text-Only Posts or Bare Link Previews:** Publishing without an attached native visual asset (diagram, code card, UI screenshot, or carousel) forfeits `2x–3x` higher discussion depth and allows in-body URLs to collapse the post into a low-dwell OpenGraph link preview.
- **"Broetry" & Fake Epiphanies:** Dramatic single-line staccato sentences linking mundane chores to system architecture (*"I watched my espresso drip this morning and realized Kafka partitions work the same way..."*).
- **Unicode Bold / Italic Glyphs:** Formatting text with `𝗕𝗼𝗹𝗱` glyphs breaks screen readers (accessibility failure), destroys search indexing, and inflates character counts.
- **Generic Hashtag Stuffing:** Using 5+ hashtags (`#tech #ai #software #coding #innovation`) flags posts as spam.
- **"Link in First Comment 👇" Evasions:** Withholding the primary article or repository URL from the post body and telling readers to hunt in the comments. Direct in-body URLs paired with native visuals outperform first-comment links—while LinkedIn's default `Most Relevant` comment sorting buries unpinned first-comment links as soon as discussion starts and drops them entirely on reshares.

### Twitter / X Anti-Patterns
- **Intra-Day Rapid Burst Posting:** Publishing multiple standalone tweets in a few minutes/hours without a 2–3 hour spacing buffer saturates follower feeds and kills early engagement velocity. Bundle related thoughts into a Thread instead.
- **Hashtag Clutter:** Using multiple hashtags on X is obsolete and dampens reach under current semantic NLP indexing. Keep to 0 hashtags.
- **Vague Curiosity Gaps:** *"10 tips senior engineers don't want you to know"* or *"I changed one line and you won't believe what happened"*.
- **Code Walls Without Visuals:** Pasting unformatted monospaced text walls without syntax highlighting or Ray.so cards.

### Bluesky Anti-Patterns
- **Algorithmic Evasions:** Writing *"Link in bio"* or *"Link in first comment"*. Bluesky does not penalize external links; putting links in comments signals platform illiteracy.
- **Missing Image Alt Text:** Omitting `[ALT]` descriptions on code screenshots or architecture diagrams violates platform accessibility norms and triggers automated mutes.
- **Engagement Farming:** *"Thoughts? Agree? Retweet if you code in Go!"* triggers swift community blocking.

### Instagram Anti-Patterns
- **Square (1:1) Carousels When 4:5 is Available:** Using 1:1 sacrifices 35% of vertical viewport real estate on mobile.
- **Unreadable Mobile Code:** Displaying code snippets smaller than 24pt equivalent that force users to pinch-to-zoom.
- **Naked "Link in Bio" Drops:** Forcing 4 friction clicks without using comment-to-DM automation.

### Reddit Anti-Patterns
- **Clickbait & Marketing Speak:** Titles like *"Why AI will replace devs"* or *"Check out my revolutionary tool"*.
- **Paywalled / Gated Destinations:** Linking to Medium paywalls or forced email capture forms.
- **Violating the 9:1 Ratio:** Submitting self-promotional links without active organic participation in comments and peer threads.
- **URL Shorteners:** `bit.ly`, `t.co`, and UTM-cluttered links are instantly auto-removed by AutoModerator sitewide.

### Threads Anti-Patterns
- **Hashtag Overuse:** Only the **first** `#tag` is indexed as a Topic Tag; extra hashtags add visual clutter and do not index.
- **Engagement Bait Bans:** *"Comment LINK"* triggers Meta's engagement-bait downranking filters.
- **Uncontextualized Link Dumps:** Dropping a bare link with zero standalone explanation.

---

## 3. Claim Validation & Fact-Checking

Before publishing any social copy, verify:
- [ ] Are latency, memory, or cost metrics reproducible from actual benchmarks or post-mortems?
- [ ] Are version numbers, language syntax, and command-line flags accurate for the current stable releases?
- [ ] Are architecture trade-offs explicitly acknowledged (what is sacrificed in memory, CPU, or complexity)?
- [ ] Is there zero reliance on unsubstantiated hyperbole?
- [ ] **Mandatory Media Item**: Does the post include at least one media item (diagram, screenshot, video, or graphic card)? Naked text-only posts are strictly prohibited.
