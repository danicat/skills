# Generative Engine Optimization (GEO) & AI Search Discovery

A guide to optimizing technical publications for generative AI search engines, answer engines, and LLM grounding systems (Google AI Overviews, Gemini Grounding, ChatGPT Search, Perplexity, Claude).

---

## 1. How AI Search & Grounding Actually Works

Discoverability in generative AI search operates across two complementary retrieval architectures:

### 1. Google Search: Core Index RAG & Query Fan-Out
As documented in official Google Search Central guidelines:
- **Rooted in Core SEO**: Google AI Overviews and AI Mode use **Retrieval-Augmented Generation (RAG / Grounding)** to pull relevant, fresh pages directly from the primary Google Search index.
- **Query Fan-Out**: The generative model automatically executes concurrent related sub-queries to gather comprehensive background information.
- **No Special Shortcuts**: Google Search does not use `llms.txt` or proprietary "GEO markup." Visibility in Google AI features is achieved by meeting foundational Search technical requirements and creating **non-commodity, people-first content with high information gain**.

### 2. Third-Party AI Agents & Direct LLM Retrieval (ChatGPT, Perplexity, Claude)
Independent AI engines and developer coding agents use web search tools, direct Markdown parsing, and repository indices:
- **`llms.txt` Standard**: Read by agent tools and LLM crawlers as a curated, token-efficient table of contents.
- **Direct Semantic Chunk Extraction**: AI answer engines extract concise, bolded answer blocks and tables to synthesize direct responses.

---

## 2. The 5 Pillars of Non-Commodity, High-Citation Content

Whether parsed by Google Search Grounding or third-party AI agents, high-citation content shares five core attributes:

### Pillar 1: High Information Gain (Non-Commodity Evidence)
AI systems prioritize content that adds unique, non-redundant value beyond common knowledge:
- **First-hand Experience**: Production post-mortems, real debugging logs, and failure-mode analysis.
- **Original Benchmarks**: Real-world metrics, memory profiles, latency measurements, and token throughput.
- **Novel Implementations**: Verified code examples, end-to-end recipes, and architectural trade-off comparisons.

### Pillar 2: The Direct Answer Block (Inverted Pyramid)
When a search query triggers an AI summary, the system retrieves the most semantically relevant paragraph:
- **Formula**: Heading (Question/Topic) $\rightarrow$ 1-to-2 sentence direct answer $\rightarrow$ Code/Table $\rightarrow$ In-depth explanation.
- **Example**:
  ```markdown
  ## How does SQLite WAL mode prevent database locks in concurrent agent swarms?

  **SQLite Write-Ahead Logging (WAL) prevents reader-writer locks by appending writes to a separate `.wal` file while readers query the immutable main database file.** This allows unlimited concurrent readers to operate without blocking background indexing agents.
  ```

### Pillar 3: Quotable Data Density & Formatting
AI models parse structured markdown elements losslessly:
- **Markdown Tables**: Clear column headers and consistent types for comparison data.
- **Bulleted Summaries**: Concise, unambiguous technical specifications.
- **Fenced Code Blocks**: Complete, syntax-highlighted code with language identifiers.

### Pillar 4: Entity Consistency & Domain Vocabulary
- Explicitly name protocols, specifications, and libraries with their official canonical casing (e.g., `Model Context Protocol`, `Antigravity CLI`, `PEP 723`, `Go 1.26`).
- Avoid vague pronouns ("it", "the tool", "this thing") when referring to architectural components.

### Pillar 5: E-E-A-T & Verifiable Author Credentials
- Explicit author byline with domain credentials (`author` in frontmatter and Schema.org `Person`).
- First-person engineering accounts ("In our benchmarks on macOS Sonoma with Go 1.26...").
- Active outbound links to official specifications and public source repositories.

---

## 3. The `llms.txt` Specification (For AI Coding Agents)

Maintained at [llmstxt.org](https://llmstxt.org/), `llms.txt` provides a curated, token-efficient Markdown index for AI agents, Cursor, and LLM tools. *(Note: Google Search ignores `llms.txt`, but it is highly valuable for AI developer agents).*

```markdown
# Site or Project Name

> High-level summary of the site, core mission, and primary audience.

Contextual guidance on how an agent should interpret the documentation and resources.

## Core Documentation
- [Quickstart Guide](https://danicat.dev/posts/quickstart/): Step-by-step setup for new developers.
- [Architecture Overview](https://danicat.dev/posts/architecture/): Deep dive into system components.

## Tutorials & Guides
- [Building an MCP Server in Go](https://danicat.dev/posts/mcp-server-go/): Complete implementation guide.

## Optional
- [About the Author](https://danicat.dev/about/): Background, credentials, and engineering principles.
```

---

## 4. AI Search & Grounding Audit Checklist

When auditing technical content for AI search and grounding:

- [ ] **Non-Commodity Value**: Does the article provide original code, first-hand data, or unique engineering perspective rather than generic recycled advice?
- [ ] **Lead Direct Answer**: Does the first section under `H2` directly answer the primary search intent in 1–2 bolded sentences?
- [ ] **Structured Formatting**: Are comparisons formatted in Markdown tables and code snippets properly fenced?
- [ ] **Entity Precision**: Are all tools, SDKs, and version numbers explicitly named?
- [ ] **No AI Slop**: Is the prose free of AI clichés (*"delve", "game-changer", "testament to", "in today's fast-paced world"*)?
- [ ] **Search Console Monitoring**: Is the site tracking AI impressions via the **Generative AI performance report** in Google Search Console?
