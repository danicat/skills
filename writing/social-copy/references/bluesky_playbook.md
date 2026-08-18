# Bluesky (AT Protocol) Developer Copy Playbook

Comprehensive guide for writing developer, open-source, and technical posts on **Bluesky (AT Protocol)**.

---

## 1. Platform Dynamics & Culture

### Core Cultural Norms
- **Anti-Corporate & Anti-Hype:** Corporate jargon, breathless buzzwords, and engagement-bait tactics (*"Thoughts?", "Agree?"*) are actively muted. Write with peer-level engineering candor.
- **Reverse-Chronological Following Feed:** Posts appear directly without algorithmic demotion or manipulation.
- **Zero Link Suppression:** Bluesky does **not** penalize external links or link cards. Direct URLs and rich Open Graph preview cards thrive directly in the main post.
- **Custom Feeds:** 40,000+ custom feeds query the AT Protocol firehose. Natural technical keywords (e.g. `Postgres`, `Golang`, `eBPF`, `Kubernetes`) automatically route your post into relevant developer feeds.
- **Domain Verification:** Using a custom domain handle (e.g., `@handle.dev` or `@project.org`) is the primary trust badge.

---

## 2. Platform Constraints & Formatting

| Parameter | Limit / Specification | Best Practice |
| :--- | :--- | :--- |
| **Post Length** | **300 graphemes** (visual characters) | Keep posts punchy (sweet spot: 200–270 chars). |
| **Outbound URLs** | Count grapheme-by-grapheme | Let the rich Open Graph link card do the work, or use clean URLs. |
| **Alt Text (`[ALT]`)** | Up to **2,000 characters** per image | **Culturally mandatory**. Missing alt text triggers mutes. Describe code logic and diagrams clearly. |
| **Media Attachments** | Up to 4 images or 1 video (up to 60s) | Attach terminal GIFs, benchmarks, or architecture diagrams. |
| **Hashtags** | Clickable / searchable | Use **0 to 1 specific hashtag max** (e.g., `#Golang`). Never stuff hashtags. |

---

## 3. High-Performing Post Frameworks

### Framework A: Open Source Launch / Tool Announcement
```text
We built [ToolName] because parsing 10GB JSON dumps in Node was eating 4GB of RAM.

[ToolName] uses SIMD streaming in Go to process files in 120ms with zero allocations.

MIT licensed, zero dependencies.

🔗 github.com/org/toolname
```

### Framework B: Technical Deep-Dive / Blog Teaser (Direct Link Card)
```text
Why did our Postgres connection pool choke at 5,000 req/s despite 64-core instances?

It wasn't lock contention or CPU exhaustion—it was transaction wraparound autovacuum starving ephemeral worker queries.

Here is how we debugged and fixed it:

[Direct Link to Blog Post / Docs]
```

### Framework C: Multi-Post Architecture Breakdown (3–4 Posts)
- **Post 1 (Hook + Outcome):** The bottleneck solved and unexpected discovery.
- **Post 2 (Mechanism):** Concrete algorithmic or architectural approach.
- **Post 3 (Visual Proof):** Benchmark chart or diagram with descriptive `[ALT]` text.
- **Post 4 (Resources):** Direct links to repository, paper, or documentation.

---

## 4. Bluesky Do's & Don'ts

### ❌ Don'ts
- **No algorithmic evasions:** Never say *"Link in bio"* or *"Link in first reply"*. Put the link directly in the post.
- **No engagement bait:** Never use *"Thoughts?"*, *"Agree?"*, or *"Bookmark this!"*.
- **No images without Alt Text:** Always write detailed descriptions of code and charts.
- **No PR fluff:** Avoid *"We are super thrilled to announce..."*.

### ✅ Do's
- Put links directly in the post with clean Open Graph previews.
- Write 1–2 sentence descriptions explaining the engineering mechanism.
- Tag and credit open-source contributors transparently.
