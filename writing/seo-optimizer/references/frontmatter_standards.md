# Frontmatter and metadata standards: search vs. humans

Specification for structuring frontmatter metadata in technical articles, separating human preview copy from search engine and AI ingestion fields per Google Search Central guidelines.

---

## 1. Summary vs. description split

Reusing one string for both search snippets and on-site UI cards hurts click-throughs on one surface and keyword clarity on the other:
- **Search snippets (`description`)** need factual keywords, problem-solving terms, and direct answers.
- **UI cards (`summary`)** need editorial tension, concrete outcomes, and scannable hooks.

```
+------------------------------------+------------------------------------+
| Frontmatter: `summary`             | Frontmatter: `description`         |
+------------------------------------+------------------------------------+
| Audience: Human site visitors      | Audience: Search engines and LLMs  |
| Surface: Homepage cards, feeds,    | Surface: <meta description>,       |
|          related post widgets      |          Open Graph, Schema.org    |
| Tone: Engaging, crisp hook         | Tone: Factual, keyword-dense,      |
|                                    |       direct-answer summary        |
| Length: 80 to 180 characters       | Length: 120 to 160 characters      |
+------------------------------------+------------------------------------+
```

### Side-by-side examples

#### Example 1: Agentic coding post
```yaml
# BAD: Identical text in both fields
summary: "Learn how to build MCP servers in Go."
description: "Learn how to build MCP servers in Go."

# GOOD: Distinct audience-tuned fields
summary: "Turn any Go CLI into a native tool server for AI agents in 50 lines of code."
description: "Step-by-step tutorial on building a Model Context Protocol (MCP) server in Go. Covers JSON-RPC handlers, tool discovery, and local testing."
```

#### Example 2: Engineering retrospective
```yaml
summary: "What happens when specialized subagents replace manual PR triage? We measured the latency and defect rate."
description: "Benchmark analysis of multi-agent code review pipelines in Go and TypeScript, covering defect detection, turnaround time, and context isolation."
```

---

## 2. Meta keywords note

> [!NOTE]
> **Never add `keywords` metadata.**
> Official Google Search documentation confirms `<meta name="keywords">` is ignored completely and carries zero ranking weight. Spend that effort on `title`, `description`, and JSON-LD.

---

## 3. Taxonomy and tag discipline

### Single pillar category
Assign each post to **one** primary category so topic archives stay focused (`Software Engineering`, `Cloud Architecture`, `Applied AI`, `DevOps`, `Tutorials`).

### Tag invariants
- **Format**: Strictly lowercase `kebab-case` (`[a-z0-9-]`).
- **Alphabetical sorting**: Sort tags alphabetically in frontmatter.
- **No category duplication**: If `categories` is `["Software Engineering"]`, do not include `software-engineering` in `tags`.
- **Translation parity**: Keep canonical tag slugs aligned across localized versions.

```yaml
# BAD: Unsorted, mixed case, duplicates primary category
categories: ["Software Engineering"]
tags: ["Go", "Architecture", "software-engineering", "APIs"]

# GOOD: Sorted lowercase kebab-case
categories: ["Software Engineering"]
tags: ["apis", "architecture", "golang", "microservices"]
```

---

## 4. Complete frontmatter specification

```yaml
---
title: "Go Developer Guide to Gemini 4: Models, Caching, and SDKs"
summary: "Compare Gemini 4 models, implicit context caching, and typed tool schemas in Go services."
description: "Complete Go guide to the Google GenAI SDK with Gemini 4. Covers Carbon, Argon, and Hydrogen models, structured outputs, and production error handling."
date: 2026-10-08T10:00:00Z
categories: ["Applied AI"]
tags: ["gemini", "golang", "sdk"]
series: ["Gemini for Go Developers"]
series_order: 1
---
```

---

## 5. Hugo layout mapping

In template partials (`layouts/partials/head.html` and `layouts/partials/schema.html`):

```html
<!-- Meta description: prefer .Params.description, fall back to .Summary -->
<meta name="description" content="{{ with .Params.description }}{{ . }}{{ else }}{{ .Summary | plainify | htmlUnescape }}{{ end }}">

<!-- Open Graph description -->
<meta property="og:description" content="{{ with .Params.description }}{{ . }}{{ else }}{{ .Summary | plainify | htmlUnescape }}{{ end }}">

<!-- UI card summary -->
<p class="summary-text">{{ with .Params.summary }}{{ . }}{{ else }}{{ .Summary }}{{ end }}</p>
```
