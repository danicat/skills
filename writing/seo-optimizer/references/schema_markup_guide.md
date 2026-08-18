# Schema.org Structured Data Guide for Technical Publications

A comprehensive reference for generating, validating, and embedding Schema.org JSON-LD structured data in developer blogs, technical documentation, and software engineering sites, fully aligned with official Google Search Central guidelines.

---

## 1. Why Structured Data Matters for AI & Search

Structured data using **JSON-LD (JavaScript Object Notation for Linked Data)** bridges the gap between raw markdown prose and semantic machine comprehension. It serves two distinct discovery surfaces:

1. **Google Rich Results**: Generates enhanced SERP appearances including article badges, breadcrumb navigation paths, site names, video previews, software metadata, and author profile cards.
2. **Generative AI & Entity Grounding**: LLMs (Gemini, ChatGPT, Claude, Perplexity) parse JSON-LD entities directly to confirm author credentials, publication dates, software dependencies, and authoritative source URLs without relying solely on heuristic scraping.

> [!NOTE]
> Google explicitly recommends **JSON-LD** embedded in `<script type="application/ld+json">` tags over Microdata or RDFa formats. JSON-LD keeps structured data decoupled from presentational HTML markup.

---

## 2. Recommended Schemas by Content Type

| Content Type | Primary Schema Type | Key Properties |
| :--- | :--- | :--- |
| **Technical Blog Post / Deep Dive** | `TechArticle` / `Article` | `headline`, `description`, `dependencies`, `proficiencyLevel`, `author`, `publisher`, `datePublished`, `dateModified`, `image` |
| **Official Site / Root Domain** | `WebSite` | `name`, `alternateName`, `url`, `potentialAction` (`SearchAction`) |
| **Author Bio / About Page** | `ProfilePage` | `mainEntity` (`Person`), `jobTitle`, `worksFor`, `sameAs`, `description`, `image` |
| **Company / Publisher Entity** | `Organization` | `name`, `url`, `logo`, `sameAs`, `contactPoint` |
| **CLI Tool / Library / Open Source** | `SoftwareApplication` | `applicationCategory`, `operatingSystem`, `programmingLanguage`, `codeRepository`, `downloadUrl`, `softwareVersion` |
| **Video Walkthrough / Tech Talk** | `VideoObject` | `name`, `description`, `thumbnailUrl`, `uploadDate`, `contentUrl`, `embedUrl`, `duration` |
| **Technical Diagram / Visual Asset** | `ImageObject` | `contentUrl`, `license`, `acquireLicensePage`, `creator`, `creditText`, `copyrightNotice` |
| **Paywalled / Premium Content** | `Article` (with paywall markup) | `isAccessibleForFree: false`, `hasPart` (`WebPageElement` with `cssSelector`) |
| **All Articles & Nested Pages** | `BreadcrumbList` | `itemListElement`, `position`, `name`, `item` |

---

## 3. Complete Copy-Pasteable JSON-LD Templates

### 3.1. `TechArticle` & `Article` (Developer Tutorial / Deep Dive)

Use `TechArticle` for coding tutorials, architectural analyses, and technical guides. Fall back to `Article` for general engineering commentary.

```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "@id": "https://danicat.dev/posts/20260729-mcp-server-go/#article",
  "headline": "Building an MCP Server with Gemini CLI and Go",
  "name": "Building an MCP Server with Gemini CLI and Go",
  "description": "Step-by-step tutorial on building a Model Context Protocol (MCP) server in Go for Gemini CLI. Covers JSON-RPC handlers, tool discovery, and local debugging.",
  "inLanguage": "en",
  "url": "https://danicat.dev/posts/20260729-mcp-server-go/",
  "datePublished": "2026-07-29T10:00:00Z",
  "dateModified": "2026-08-18T12:00:00Z",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://danicat.dev/posts/20260729-mcp-server-go/"
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://danicat.dev/images/20260729-mcp-server-go-hero.png",
    "width": 1200,
    "height": 675,
    "caption": "Architecture diagram illustrating JSON-RPC communication between Gemini CLI and Go MCP server"
  },
  "proficiencyLevel": "Beginner",
  "dependencies": "Go 1.24+, Gemini CLI, git",
  "author": {
    "@type": "Person",
    "@id": "https://danicat.dev/about/#person",
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
    "@id": "https://danicat.dev/#organization",
    "name": "danicat.dev",
    "url": "https://danicat.dev/",
    "logo": {
      "@type": "ImageObject",
      "url": "https://danicat.dev/images/avatar.png",
      "width": 192,
      "height": 192
    }
  },
  "keywords": ["gemini-cli", "golang", "mcp", "tutorial"]
}
```

---

### 3.2. `WebSite` (Official Site Name in SERPs)

Place this schema on the homepage or in the site-wide base template to control how Google Search renders your site name and alternate names in search result headers.

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://danicat.dev/#website",
  "url": "https://danicat.dev/",
  "name": "Daniela Petruzalek",
  "alternateName": ["danicat.dev", "DaniCat Tech"],
  "description": "Technical publications, Go engineering, and AI agent architecture.",
  "inLanguage": "en",
  "publisher": {
    "@type": "Organization",
    "@id": "https://danicat.dev/#organization"
  },
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://danicat.dev/search/?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

---

### 3.3. `ProfilePage` (Author Bio & About Pages)

Google uses `ProfilePage` structured data to power author knowledge cards, verify author authority (E-E-A-T), and disambiguate creators across social platforms.

```json
{
  "@context": "https://schema.org",
  "@type": "ProfilePage",
  "@id": "https://danicat.dev/about/#profilepage",
  "url": "https://danicat.dev/about/",
  "name": "About Daniela Petruzalek",
  "mainEntity": {
    "@type": "Person",
    "@id": "https://danicat.dev/about/#person",
    "name": "Daniela Petruzalek",
    "alternateName": "danicat",
    "jobTitle": "Principal Software Engineer & AI Systems Architect",
    "description": "Software engineer specializing in Go systems programming, agentic coding workflows, and developer tooling.",
    "image": "https://danicat.dev/images/avatar.png",
    "url": "https://danicat.dev/about/",
    "worksFor": {
      "@type": "Organization",
      "name": "Independent"
    },
    "sameAs": [
      "https://github.com/danicat",
      "https://www.linkedin.com/in/danicat/",
      "https://bsky.app/profile/danicat.dev",
      "https://x.com/danicatdev"
    ]
  }
}
```

---

### 3.4. `Organization` (Brand Identity & Entity Grounding)

Declares the publishing entity, official brand logo, and authoritative web footprints.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://danicat.dev/#organization",
  "name": "danicat.dev",
  "url": "https://danicat.dev/",
  "logo": {
    "@type": "ImageObject",
    "url": "https://danicat.dev/images/avatar.png",
    "width": 512,
    "height": 512,
    "caption": "danicat.dev logo"
  },
  "sameAs": [
    "https://github.com/danicat",
    "https://bsky.app/profile/danicat.dev",
    "https://www.linkedin.com/in/danicat/"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "editorial",
    "url": "https://danicat.dev/about/"
  }
}
```

---

### 3.5. `SoftwareApplication` (CLI Tools, Libraries & Open Source Packages)

Use this schema when releasing or documenting software packages, CLI utilities, or Go modules.

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://danicat.dev/projects/godoctor/#software",
  "name": "GoDoctor",
  "description": "Automated code diagnostics, mutation testing, and style enforcement CLI for Go codebases.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "programmingLanguage": "Go",
  "softwareVersion": "1.4.0",
  "codeRepository": "https://github.com/danicat/godoctor",
  "downloadUrl": "https://github.com/danicat/godoctor/releases",
  "author": {
    "@type": "Person",
    "name": "Daniela Petruzalek",
    "url": "https://danicat.dev/about/"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
```

---

### 3.6. `VideoObject` (Embedded Technical Walkthroughs & Talks)

Use when embedding YouTube, Vimeo, or self-hosted video recordings of tutorials, presentations, or demos.

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Building an MCP Server in Go from Scratch",
  "description": "Full walkthrough of constructing a JSON-RPC Model Context Protocol server in Go and connecting it to Gemini CLI.",
  "thumbnailUrl": [
    "https://danicat.dev/images/video-mcp-thumb-16x9.jpg",
    "https://danicat.dev/images/video-mcp-thumb-4x3.jpg"
  ],
  "uploadDate": "2026-07-29T12:00:00Z",
  "duration": "PT14M32S",
  "contentUrl": "https://danicat.dev/videos/mcp-server-go.mp4",
  "embedUrl": "https://www.youtube-nocookie.com/embed/example123",
  "publisher": {
    "@type": "Organization",
    "name": "danicat.dev",
    "logo": {
      "@type": "ImageObject",
      "url": "https://danicat.dev/images/avatar.png"
    }
  }
}
```

---

### 3.7. `ImageObject` (Technical Diagrams & Licensable Media)

Enables enhanced image previews and Google Images "Licensable" badges for proprietary architectural diagrams and graphics.

```json
{
  "@context": "https://schema.org",
  "@type": "ImageObject",
  "contentUrl": "https://danicat.dev/images/20260729-mcp-architecture.png",
  "license": "https://creativecommons.org/licenses/by-sa/4.0/",
  "acquireLicensePage": "https://danicat.dev/about/#licensing",
  "creditText": "Daniela Petruzalek",
  "creator": {
    "@type": "Person",
    "name": "Daniela Petruzalek"
  },
  "copyrightNotice": "© 2026 Daniela Petruzalek. CC BY-SA 4.0."
}
```

---

### 3.8. Subscription & Paywalled Content

When offering gated technical whitepapers or paywalled deep dives, mark the paywalled section explicitly to prevent cloaking penalties.

```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Advanced Distributed Consensus in Go: Raft Deep Dive",
  "description": "Deep dive into production Raft implementation details and edge cases in distributed systems.",
  "isAccessibleForFree": false,
  "hasPart": {
    "@type": "WebPageElement",
    "isAccessibleForFree": false,
    "cssSelector": ".paywalled-content"
  },
  "author": {
    "@type": "Person",
    "name": "Daniela Petruzalek",
    "url": "https://danicat.dev/about/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "danicat.dev",
    "url": "https://danicat.dev/"
  }
}
```

---

### 3.9. `BreadcrumbList` (Navigational Trail)

Generates clean breadcrumb paths in Google Search results instead of raw URL strings.

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

## 4. Structured Data Quality Policies & Rich Result Limits

### 4.1. Official Google Deprecations & Restrictions

Stay current with Google Search Central policy updates regarding rich result eligibility:

1. **`HowTo` Structured Data (Deprecated on Mobile / Restricted)**:
   - In September 2023, Google deprecated `HowTo` rich results on mobile devices and drastically restricted them on desktop.
   - **Recommendation**: Do not depend on `HowTo` markup for mobile SERP dominance. Mark technical walkthroughs with `TechArticle` instead. If `HowTo` is included for non-Google consumers, keep it supplementary.
2. **`FAQPage` Structured Data (Restricted to Authority Domains)**:
   - In August 2023, Google restricted `FAQPage` rich results exclusively to well-known authoritative government (`.gov`) and health organization websites.
   - Standard commercial, personal, and tech blogs will **not** receive collapsible FAQ accordion rich results in SERPs, even if the schema is 100% valid.

---

### 4.2. Core Quality Policies & Validation Rules

To prevent algorithmic demotion or manual actions for spammy structured data:

1. **Visible Content Requirement**: Structured data must accurately represent the content visible to human visitors on the rendered page. Never markup invisible elements, hidden keywords, or phantom reviews.
2. **Relevance & Specificity**: Use the most specific applicable Schema type (e.g., prefer `TechArticle` over generic `Article` or `Thing`).
3. **No Deceptive Pricing or Authorship**: Attributes like `author.name`, `datePublished`, and `isAccessibleForFree` must match the page text verbatim.

---

### 4.3. Interaction with Robots Directives

Understanding how Googlebot reconciles robots meta tags with Schema markup:

1. **`max-snippet` Scope**:
   - Setting `<meta name="robots" content="max-snippet:50">` limits the textual snippet drawn from `article.description` or prose to 50 characters.
   - **It does NOT restrict other structured data rich results** (such as breadcrumb badges, video cards, software metadata, or author attribution).
2. **`data-nosnippet` and Structured Data**:
   - Wrapping HTML content in `<div data-nosnippet>` instructs Google not to use that HTML block in search text snippets.
   - **Schema declared inside or describing `data-nosnippet` sections remains 100% valid for structured data parsing and rich results.**

---

## 5. Implementation in Static Site Generators

### 5.1. Hugo Partial Implementation

In `layouts/partials/schema.html`:

```html
{{ if .IsPage }}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "@id": {{ printf "%s#article" .Permalink | jsonify }},
  "headline": {{ .Title | jsonify }},
  "description": {{ with .Params.description }}{{ . | jsonify }}{{ else }}{{ .Summary | plainify | htmlUnescape | jsonify }}{{ end }},
  "url": {{ .Permalink | jsonify }},
  "datePublished": {{ .Date.Format "2006-01-02T15:04:05Z07:00" | jsonify }},
  {{ with .Lastmod }}"dateModified": {{ .Format "2006-01-02T15:04:05Z07:00" | jsonify }},{{ end }}
  "inLanguage": {{ .Language.Lang | jsonify }},
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": {{ .Permalink | jsonify }}
  },
  {{ with .Params.images }}
  "image": {
    "@type": "ImageObject",
    "url": {{ index . 0 | absURL | jsonify }}
  },
  {{ end }}
  "author": {
    "@type": "Person",
    "@id": {{ "about/#person" | absURL | jsonify }},
    "name": {{ .Site.Params.author.name | default "Daniela Petruzalek" | jsonify }},
    "url": {{ "about/" | absURL | jsonify }}
  },
  "publisher": {
    "@type": "Organization",
    "@id": {{ "#organization" | absURL | jsonify }},
    "name": {{ .Site.Title | jsonify }},
    "url": {{ .Site.BaseURL | jsonify }},
    "logo": {
      "@type": "ImageObject",
      "url": {{ "images/avatar.png" | absURL | jsonify }}
    }
  }
}
</script>

<!-- BreadcrumbList Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": {{ .Site.BaseURL | jsonify }}
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Posts",
      "item": {{ "posts/" | absURL | jsonify }}
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": {{ .Title | jsonify }},
      "item": {{ .Permalink | jsonify }}
    }
  ]
}
</script>
{{ end }}
```

---

## 6. Testing & Validation Checklist

Always validate your structured data prior to publication:

1. **Google Rich Results Test**: [https://search.google.com/test/rich-results](https://search.google.com/test/rich-results)
   - Verify that your URL or code snippet passes with **0 errors and 0 critical warnings**.
2. **Schema Markup Validator**: [https://validator.schema.org/](https://validator.schema.org/)
   - Confirm standard Schema.org syntactic compliance and `@type` inheritance.
3. **Automated CI Validation**:
   - Ensure your build pipeline verifies that emitted `<script type="application/ld+json">` blocks contain valid, parseable JSON.
