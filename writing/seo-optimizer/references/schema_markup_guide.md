# Schema.org Structured Data Guide for Technical Publications

A comprehensive reference for generating, validating, and embedding Schema.org JSON-LD structured data in developer blogs and documentation sites.

---

## 1. Why Structured Data Matters for AI & Search

Structured data (JSON-LD) bridges the gap between raw prose and semantic machine comprehension. It enables:
1. **Google Rich Results**: Article snippets, breadcrumbs, author knowledge cards, and code previews.
2. **AI Entity Grounding**: LLMs and AI search engines parse JSON-LD entities directly to confirm author credentials, publication dates, language variants, and software dependencies.

---

## 2. Recommended Schemas by Content Type

| Content Type | Primary Schema Type | Key Properties |
| :--- | :--- | :--- |
| **Technical Blog Post / Deep Dive** | `TechArticle` | `headline`, `description`, `dependencies`, `proficiencyLevel`, `author` |
| **Step-by-Step Tutorial / Codelab** | `TechArticle` + `HowTo` | `step`, `totalTime`, `tool`, `supply` |
| **CLI Tool / Library / Package** | `SoftwareApplication` | `operatingSystem`, `applicationCategory`, `downloadUrl`, `programmingLanguage` |
| **All Articles** | `BreadcrumbList` | `itemListElement`, `position`, `name`, `item` |

---

## 3. `TechArticle` JSON-LD Template

```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "@id": "https://danicat.dev/posts/20260729-mcp-server-go/#article",
  "headline": "How to Build an MCP Server with Gemini CLI and Go",
  "name": "How to Build an MCP Server with Gemini CLI and Go",
  "description": "Step-by-step tutorial on building a Model Context Protocol (MCP) server in Go for Gemini CLI. Covers JSON-RPC handlers, tool discovery, and local debugging.",
  "inLanguage": "en",
  "url": "https://danicat.dev/posts/20260729-mcp-server-go/",
  "datePublished": "2026-07-29T10:00:00Z",
  "dateModified": "2026-08-18T12:00:00Z",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://danicat.dev/posts/20260729-mcp-server-go/"
  },
  "proficiencyLevel": "Beginner",
  "dependencies": "Go 1.24+, Gemini CLI, git",
  "author": {
    "@type": "Person",
    "name": "Daniela Petruzalek",
    "url": "https://danicat.dev/about/",
    "sameAs": [
      "https://github.com/danicat",
      "https://www.linkedin.com/in/danicat/",
      "https://bsky.app/profile/danicat.dev"
    ]
  },
  "publisher": {
    "@type": "Organization",
    "name": "danicat.dev",
    "url": "https://danicat.dev/",
    "logo": {
      "@type": "ImageObject",
      "url": "https://danicat.dev/images/avatar.png"
    }
  },
  "keywords": ["gemini-cli", "golang", "mcp", "tutorial"]
}
```

---

## 4. `BreadcrumbList` JSON-LD Template

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://danicat.dev/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Posts",
      "item": "https://danicat.dev/posts/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Building an MCP Server with Gemini CLI and Go",
      "item": "https://danicat.dev/posts/20260729-mcp-server-go/"
    }
  ]
}
```

---

## 5. Hugo Partial Implementation

In `layouts/partials/schema.html`:

```html
{{ if .IsPage }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": {{ .Title | jsonify }},
  "description": {{ with .Params.description }}{{ . | jsonify }}{{ else }}{{ .Summary | plainify | htmlUnescape | jsonify }}{{ end }},
  "url": {{ .Permalink | jsonify }},
  "datePublished": {{ .Date.Format "2006-01-02T15:04:05Z07:00" | jsonify }},
  {{ with .Lastmod }}"dateModified": {{ .Format "2006-01-02T15:04:05Z07:00" | jsonify }},{{ end }}
  "inLanguage": {{ .Language.Lang | jsonify }},
  "author": {
    "@type": "Person",
    "name": {{ .Site.Params.author.name | default "Daniela Petruzalek" | jsonify }},
    "url": {{ "about/" | absURL | jsonify }}
  },
  "publisher": {
    "@type": "Organization",
    "name": {{ .Site.Title | jsonify }},
    "url": {{ .Site.BaseURL | jsonify }}
  }
}
</script>
{{ end }}
```
