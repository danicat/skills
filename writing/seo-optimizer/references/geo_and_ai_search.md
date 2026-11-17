# Generative Engine Optimization (GEO) and AI search discovery

Guide for optimizing technical publications for generative AI search engines, answer engines, and LLM grounding pipelines (`Google AI Overviews`, `ChatGPT Search`, `Perplexity`, `Claude`).

---

## 1. How AI search and grounding work

Discoverability in generative AI search operates across two complementary retrieval models:

### Google Search: core index RAG and query fan-out
According to official Google Search Central guidelines:
- **Rooted in core SEO**: `Google AI Overviews` and `AI Mode` use Retrieval-Augmented Generation (RAG) to fetch fresh pages directly from the primary Google Search index.
- **Query fan-out**: The model issues concurrent related sub-queries to synthesize answers across multiple angles.
- **No proprietary shortcuts**: Google Search ignores `/llms.txt`. Visibility depends on technical crawlability and **non-commodity content with high information gain**.

### Third-party AI engines and coding agents
Independent AI search engines and CLI coding agents combine web search with direct Markdown fetching:
- **`llms.txt` and `.well-known` indexes**: Coding agents and AI tools fetch `/llms.txt`, `/llms-full.txt`, or `.well-known/llms.txt` as token-efficient tables of contents.
- **Passage and table extraction**: Answer engines quote bolded definition sentences and structured Markdown tables directly.

---

## 2. Five pillars of high-citation content

### Pillar 1: High information gain
Publish primary technical evidence that baseline models cannot synthesize from memory:
- Production post-mortems, root-cause traces, and failure-mode analyses.
- Measured benchmarks, memory profiles, `p99` latency numbers, and throughput deltas.
- Runnable implementations and explicit architectural trade-off comparisons.

### Pillar 2: Direct answer blocks (inverted pyramid)
Place a concise direct answer right below question headings:
- **Formula**: Question `H2` -> `1` to `2` sentence bolded definition -> Code or table -> Trade-offs.
- **Example**:
  ```markdown
  ## How does SQLite WAL mode prevent database locks in concurrent agent swarms?

  **SQLite Write-Ahead Logging (WAL) avoids reader-writer stalls by appending writes to a separate `.wal` file while readers query the immutable main database file.** This lets concurrent readers proceed without blocking background indexing workers.
  ```

### Pillar 3: Quotable data density
Format structured evidence cleanly:
- **Markdown tables**: Explicit column headers and consistent units.
- **Bulleted specs**: Concise, self-contained technical constraints.
- **Fenced code blocks**: Complete, runnable snippets with language tags.

### Pillar 4: Entity consistency and canonical naming
- Name protocols, runtimes, and tools with exact canonical spelling (`Model Context Protocol`, `PEP 723`, `Go 1.27`).
- Avoid ambiguous pronouns (*"it"*, *"the tool"*) when referring to components.

### Pillar 5: Author credentials and first-hand accountability
- Include explicit author frontmatter (`author`) and Schema.org `Person` metadata.
- Ground claims in concrete environments (*"In our Go 1.27 benchmarks on macOS..."*) and link primary specifications.

---

## 3. The `llms.txt` family (`/llms.txt`, `/llms-full.txt`, `.well-known/llms.txt`)

Maintained at [llmstxt.org](https://llmstxt.org/), `/llms.txt` provides a curated Markdown sitemap for coding agents and LLM documentation clients. Expose optional companions alongside `/llms.txt`:
- **`/llms.txt`**: Concise title, summary blockquote, and prioritized links to canonical Markdown or HTML pages.
- **`/llms-full.txt`**: Concatenated full-text Markdown corpus of public docs or articles for single-fetch ingestion.
- **`/.well-known/llms.txt` (or redirect)**: Optional standard discovery path alongside root `/llms.txt`.

```markdown
# Site or Project Name

> Concise summary of the site, audience, and scope.

## Core Documentation
- [Quickstart Guide](https://example.com/docs/quickstart/): Setup and verification commands.
- [Architecture Overview](https://example.com/docs/architecture/): Component boundaries and schemas.

## Technical Articles
- [Building an MCP Server in Go](https://example.com/tutorials/mcp-server-go/): Complete tutorial with tests.

## Optional
- [About](https://example.com/about/): Author bio and background.
```

---

## 4. AI crawler `robots.txt` matrix (grounding vs. training)

Modern sites separate **live search grounding and citation bots** from **offline model-training crawlers** inside `robots.txt`:

| Crawler / token | Operator | Primary purpose | Typical `robots.txt` stance |
| :--- | :--- | :--- | :--- |
| **`Googlebot`** | Google | Classic Search indexing and `AI Overviews` RAG citations | **Allow** (`nosnippet` / `data-nosnippet` control excerpts) |
| **`Google-Extended`** | Google | Gemini training and Vertex grounding opt-out control | Allow for open docs; `Disallow: /` to opt out of training |
| **`OAI-SearchBot`** / **`ChatGPT-User`** | OpenAI | ChatGPT Search index citations and user-triggered fetches | **Allow** if you want ChatGPT Search referrals |
| **`GPTBot`** | OpenAI | Foundation model pre-training and fine-tuning corpus | Disallow if restricting model training |
| **`Claude-SearchBot`** / **`Claude-User`** | Anthropic | Search discovery and user-initiated web fetches | **Allow** for live documentation retrieval |
| **`ClaudeBot`** | Anthropic | Model training web crawl | Disallow if restricting model training |
| **`PerplexityBot`** / **`Perplexity-User`** | Perplexity | Answer engine search indexing and user link fetches | **Allow** for citation traffic |
| **`Applebot`** / **`Applebot-Extended`** | Apple | Search/Siri retrieval vs. Apple Intelligence model training | Allow `Applebot`; `Disallow` `Applebot-Extended` to opt out of training |

*(Verify exact user-agent behavior and IP ranges against each operator's official crawler documentation before deploying strict rules.)*

---

## 5. AI search audit checklist

- [ ] **Non-commodity evidence**: Contains original code, benchmarks, or post-mortem findings.
- [ ] **Lead direct answer**: First `H2` opens with `1` to `2` clear direct-answer sentences.
- [ ] **Structured blocks**: Uses comparison tables and fenced language-tagged code blocks.
- [ ] **Entity clarity**: Names tools, protocols, and stable versions (`Go 1.27`, `Gemini 4`) explicitly.
- [ ] **Zero AI slop**: Free of cliché filler (*delve*, *game-changer*, *testament to*) and mid-sentence em dashes.
- [ ] **Crawler policy**: `robots.txt` intentionally configures search vs. training user-agents, and `/llms.txt` stays current.
