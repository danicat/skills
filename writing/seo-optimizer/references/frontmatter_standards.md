# Frontmatter & Metadata Standards: Search vs. Humans

A precise specification for structuring frontmatter metadata in technical articles, distinguishing human-facing presentation from search engine and AI ingestion, aligned with Google Search Central standards.

---

## 1. The Summary vs. Description Dichotomy

A common anti-pattern in static site generators is using a single `description` or `summary` field for both search engine metadata and on-site user interface elements. This produces subpar outcomes for both:
- Search snippets need **dense, factual keywords, concrete problem-solving language, and direct answers**.
- UI cards need **curiosity hooks, narrative tension, and scannable editorial phrasing**.

```
+------------------------------------+------------------------------------+
| Frontmatter: `summary`             | Frontmatter: `description`         |
+------------------------------------+------------------------------------+
| Audience: Human site visitors      | Audience: Search engines & LLMs    |
| Surface: Homepage cards, feeds,    | Surface: `<meta description>`,     |
|          related post widgets      |          OpenGraph, Schema.org     |
| Tone: Engaging, intriguing, punchy | Tone: Factual, keyword-dense,      |
|                                    |       direct-answer summary        |
| Length: 80–180 characters          | Length: 120–160 characters         |
+------------------------------------+------------------------------------+
```

### Side-by-Side Examples

#### Example 1: Agentic Coding Post
```yaml
# BAD: Reusing identical text for both
summary: "Learn how to build MCP servers in Go with Gemini CLI."
description: "Learn how to build MCP servers in Go with Gemini CLI."

# GOOD: Distinct, optimized fields
summary: "Turn any Go CLI into a native tool for AI agents with just 50 lines of code."
description: "Step-by-step tutorial on building a Model Context Protocol (MCP) server in Go for Gemini CLI. Covers JSON-RPC handlers, tool discovery, and local debugging."
```

#### Example 2: Architecture / Technical Retrospective
```yaml
# GOOD:
summary: "What happens when you replace manual code reviews with a fleet of specialized subagents? We crunched the data."
description: "Analysis of multi-agent code review workflows in Go and TypeScript. Evaluates PR review speed, defect detection rates, and context isolation benchmarks."
```

---

## 2. Meta Tags Note: Keywords are Ignored

> [!NOTE]
> **Do NOT add `keywords` metadata.**
> Official Google Search documentation confirms that `<meta name="keywords">` is **completely ignored** and has zero ranking value. Focus your metadata efforts exclusively on `<title>`, `<meta name="description">`, and structured JSON-LD.

---

## 3. Taxonomy & Tag Discipline

To maximize search relevance and avoid internal tag cannibalization:

### 1. Single Pillar Category
Every article should belong to exactly **one** primary category to avoid duplicate taxonomy indexing and maintain clean topic clusters (e.g., `Software Engineering`, `Cloud Architecture`, `Artificial Intelligence`, `DevOps`, `Tutorials`).

### 2. Tag Invariants
- **Format**: Strictly lowercase, alphanumeric, single hyphens (`kebab-case`).
- **Alphabetical Sorting**: Tags must be sorted alphabetically in the frontmatter array.
- **No Category Duplication**: If the category is `Software Engineering`, do NOT add `software-engineering` as a tag.
- **Unified Tag Archives**: Maintain consistent, standardized tag naming across all translated editions if publishing a multilingual site.

```yaml
# BAD: Unsorted, mixed casing, category duplication
categories: ["Software Engineering"]
tags: ["Go", "Architecture", "software-engineering", "APIs"]

# GOOD: Canonical, sorted, clean
categories: ["Software Engineering"]
tags: ["apis", "architecture", "golang", "microservices"]
```

---

## 4. Complete Frontmatter Specification

```yaml
---
title: "Go Developers Guide to Gemini: Model Family and SDKs"
summary: "Explore the Gemini model family, token pricing dynamics, and native Go SDK patterns for production backend services."
description: "Complete guide for Go developers using Gemini API and Google GenAI SDK. Compares Gemini 2.5 Flash, Pro, and thinking models with code examples in Go."
date: 2026-08-08T10:00:00Z
categories: ["Applied GenAI"]
tags: ["gemini", "golang", "sdk"]
series: ["Gemini for Go Developers"]
series_order: 1
---
```

---

## 5. Hugo Layout Mapping

In your Hugo partials (e.g. `layouts/partials/head.html` and `layouts/partials/schema.html`):

```html
<!-- Meta Description: Prefer .Params.description, fallback to .Summary -->
<meta name="description" content="{{ with .Params.description }}{{ . }}{{ else }}{{ .Summary | plainify | htmlUnescape }}{{ end }}">

<!-- OpenGraph Description -->
<meta property="og:description" content="{{ with .Params.description }}{{ . }}{{ else }}{{ .Summary | plainify | htmlUnescape }}{{ end }}">

<!-- Theme UI Cards (e.g., layouts/_default/summary.html) -->
<p class="summary-text">{{ with .Params.summary }}{{ . }}{{ else }}{{ .Summary }}{{ end }}</p>
```
