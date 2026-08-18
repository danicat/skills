# Social Copy Anti-Patterns & Slop Checklist

Exhaustive checklist of writing patterns, platform missteps, and synthetic AI tells that destroy credibility, suppress algorithmic distribution, and trigger audience fatigue.

---

## 1. Synthetic AI Tells & Cliché Vocabulary

### Banned Fluff & Magic Words
Never use these generic filler words and phrases in developer copy:
- *"In today's fast-paced digital world / landscape..."*
- *"Delve into / Let's dive deep into..."*
- *"A testament to..."*
- *"Game-changer / Revolutionary / Paradigm shift"*
- *"Unleash the power of / Unlock seamless potential..."*
- *"Crucial / Paramount / Vital" (when used as empty adverbs)*
- *"Navigating the complexities of..."*
- *"Buckle up 🧵 / Mind-blowing 🤯"*

### Structural AI Tells
- **Negative Parallelism:** Avoid repetitive *"It's not just about X, it's about Y"* structures. State what it is directly.
- **Em-Dash Overdose:** Avoid multiple em-dashes (`—`) per post. Use concise sentences or colons.
- **Rule of Threes Addiction:** Avoid forcing ideas into artificial triplets when two or four points are more accurate.

---

## 2. Platform-Specific Anti-Patterns

### LinkedIn Anti-Patterns
- **"Broetry" & Fake Epiphanies:** Dramatic single-line staccato sentences linking mundane chores to system architecture (*"I watched my espresso drip this morning and realized Kafka partitions work the same way..."*).
- **Unicode Bold / Italic Glyphs:** Formatting text with `𝗕𝗼𝗹𝗱` glyphs breaks screen readers (accessibility failure), destroys search indexing, and inflates character counts.
- **Generic Hashtag Stuffing:** Using 5+ hashtags (`#tech #ai #software #coding #innovation`) flags posts as spam.
- **In-Body Links Without Workaround:** Putting links directly in the post body cuts organic reach by 40–60%.

### Twitter / X Anti-Patterns
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
