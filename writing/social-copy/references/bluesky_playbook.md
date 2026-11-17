# Bluesky (AT Protocol) developer copy playbook

Guide for writing developer, open-source, and technical posts on **Bluesky (AT Protocol)**.

---

## 1. Platform dynamics and culture

### Core cultural norms
- **Anti-corporate and anti-hype:** Corporate jargon, breathless buzzwords, and engagement-bait tactics (*"Thoughts?", "Agree?"*) trigger mutes. Write with peer-level engineering candor.
- **Reverse-chronological Following feed:** Posts reach followers chronologically without algorithmic throttling.
- **Zero link suppression:** Bluesky does **not** penalize external links or link cards. Direct URLs and rich Open Graph preview cards work directly inside the main post.
- **Custom feeds:** Over `40,000` custom feeds scan the AT Protocol firehose. Natural technical keywords (`Postgres`, `Golang`, `eBPF`, `Kubernetes`) route posts into developer feeds automatically.
- **Domain verification:** Using a custom domain handle (such as `@handle.dev` or `@project.org`) acts as the main trust signal.

---

## 2. Platform constraints and formatting

| Parameter | Limit or specification | Best practice |
| :--- | :--- | :--- |
| **Post length** | **300 graphemes** (visual characters) | Keep single posts tight (sweet spot: `200` to `270` graphemes). |
| **Outbound URLs** | Counted against the `300`-grapheme cap unless faceted | Let the rich Open Graph link card handle context, or keep URLs clean. |
| **Alt text (`[ALT]`)** | Up to **2,000 characters** per image | **Culturally mandatory**. Missing `alt` text triggers mutes. Explain code logic and diagrams clearly. |
| **Media attachments** | Up to `4` images or `1` video (up to `180s` / `3` minutes) | Attach terminal recordings, benchmark charts, or architecture diagrams. |
| **Hashtags** | Clickable and searchable | Use **0 to 1 specific hashtag max** (such as `#Golang`). Never stuff hashtags. |

---

## 3. High-performing post frameworks

### Framework A: Open source launch or tool announcement
```text
We built [ToolName] because parsing 10GB JSON dumps in Node was eating 4GB of RAM.

[ToolName] uses SIMD streaming in Go to process files in 120ms with zero allocations.

MIT licensed, zero dependencies.

🔗 github.com/org/toolname
```

### Framework B: Technical deep dive or blog teaser (direct link card)
```text
Why did our Postgres connection pool stall at 5,000 req/s on 64-core instances?

Transaction wraparound autovacuum starved ephemeral worker queries while CPU and lock metrics looked idle.

Here is how we traced and fixed it:

[Direct Link to Blog Post / Docs]
```

### Framework C: Multi-post architecture breakdown (3 to 4 posts)
- **Post 1 (hook and outcome):** Name the bottleneck solved and the unexpected root cause.
- **Post 2 (mechanism):** Explain the concrete algorithm, protocol, or schema change.
- **Post 3 (visual proof):** Attach a benchmark plot or diagram with detailed `[ALT]` text.
- **Post 4 (resources):** Link directly to the repository, paper, or documentation.

---

## 4. Bluesky do's and don'ts

### ❌ Don'ts
- **No algorithmic evasions:** Never write *"Link in bio"* or *"Link in first reply"*. Put links directly in the post.
- **No engagement bait:** Never use *"Thoughts?"*, *"Agree?"*, or *"Bookmark this!"*.
- **No images without alt text:** Always write clear `[ALT]` descriptions for code and charts.
- **No PR fluff:** Avoid *"We are super thrilled to announce..."*.

### ✅ Do's
- Put links directly in the post with clean Open Graph previews or native media.
- Write `1` to `2` sentence explanations detailing the engineering mechanism.
- Tag and credit open-source contributors transparently.
