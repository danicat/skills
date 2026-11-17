# Schema.org structured data guide for technical publications

A comprehensive reference for generating, validating, and embedding Schema.org JSON-LD structured data in developer blogs, technical documentation, and software engineering sites, fully aligned with official Google Search Central guidelines.

---

## 1. Why structured data matters for AI and search

Structured data using **JSON-LD (JavaScript Object Notation for Linked Data)** bridges the gap between raw markdown prose and semantic machine comprehension. It serves two distinct discovery surfaces:

1. **Google Rich Results**: Generates enhanced SERP appearances including article badges, breadcrumb navigation paths, site names, video previews, software metadata, and author profile cards.
2. **Generative AI & Entity Grounding**: LLMs (Gemini, ChatGPT, Claude, Perplexity) parse JSON-LD entities directly to confirm author credentials, publication dates, software dependencies, and authoritative source URLs without relying solely on heuristic scraping.

> [!NOTE]
> Google explicitly recommends **JSON-LD** embedded in `<script type="application/ld+json">` tags over Microdata or RDFa formats. JSON-LD keeps structured data decoupled from presentational HTML markup.

---

## 2. Recommended schemas by content type

| Content Type | Primary Schema Type | Key Properties |
| :--- | :--- | :--- |
| **Technical Blog Post / Deep Dive** | `TechArticle` / `Article` | `headline`, `description`, `dependencies`, `proficiencyLevel`, `author`, `publisher`, `datePublished`, `dateModified`, `image` |
| **Official Site / Root Domain** | `WebSite` | `name`, `alternateName`, `url`, `publisher`, `description` |
| **Author Bio / About Page** | `ProfilePage` | `mainEntity` (`Person`), `jobTitle`, `worksFor`, `sameAs`, `description`, `image` |
| **Company / Publisher Entity** | `Organization` | `name`, `url`, `logo`, `sameAs`, `contactPoint` |
| **CLI Tool / Library / Open Source** | `SoftwareApplication` | `applicationCategory`, `operatingSystem`, `programmingLanguage`, `codeRepository`, `downloadUrl`, `softwareVersion` |
| **Video Walkthrough / Tech Talk** | `VideoObject` | `name`, `description`, `thumbnailUrl`, `uploadDate`, `contentUrl`, `embedUrl`, `duration` |
| **Technical Diagram / Visual Asset** | `ImageObject` | `contentUrl`, `license`, `acquireLicensePage`, `creator`, `creditText`, `copyrightNotice` |
| **Paywalled / Premium Content** | `Article` (with paywall markup) | `isAccessibleForFree: false`, `hasPart` (`WebPageElement` with `cssSelector`) |
| **All Articles & Nested Pages** | `BreadcrumbList` | `itemListElement`, `position`, `name`, `item` |

---

## 3. Copy-pasteable JSON-LD templates

### 3.1. `TechArticle` and `Article` (developer tutorial or deep dive)

Use `TechArticle` for coding tutorials, architectural analyses, and technical guides. Fall back to `Article` for general engineering commentary.

```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "@id": "https://example.com/posts/mcp-server-go/#article",
  "headline": "Building an MCP Server in Go",
  "name": "Building an MCP Server in Go",
  "description": "Step-by-step tutorial on building a Model Context Protocol (MCP) server in Go. Covers JSON-RPC handlers, tool discovery, and local debugging.",
  "inLanguage": "en",
  "url": "https://example.com/posts/mcp-server-go/",
  "datePublished": "2026-07-29T10:00:00Z",
  "dateModified": "2026-08-18T12:00:00Z",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/posts/mcp-server-go/"
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://example.com/images/mcp-server-go-hero.png",
    "width": 1200,
    "height": 675,
    "caption": "Architecture diagram illustrating JSON-RPC communication between client and Go MCP server"
  },
  "proficiencyLevel": "Beginner",
  "dependencies": "Go 1.24+, git",
  "author": {
    "@type": "Person",
    "@id": "https://example.com/about/#person",
    "name": "Jane Doe",
    "url": "https://example.com/about/",
    "sameAs": [
      "https://github.com/example",
      "https://www.linkedin.com/in/example/",
      "https://bsky.app/profile/example.bsky.social"
    ]
  },
  "publisher": {
    "@type": "Organization",
    "@id": "https://example.com/#organization",
    "name": "Example Engineering",
    "url": "https://example.com/",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/images/logo.png",
      "width": 192,
      "height": 192
    }
  },
  "keywords": ["golang", "mcp", "tutorial"]
}
```

---

### 3.2. `WebSite` (official site name in SERPs)

Place this schema on the homepage or in the site-wide base template to control how Google Search renders your site name and alternate names in search result headers.

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://example.com/#website",
  "url": "https://example.com/",
  "name": "Example Engineering",
  "alternateName": ["Example Tech", "example.com"],
  "description": "Technical publications, software engineering guides, and system architecture deep dives.",
  "inLanguage": "en",
  "publisher": {
    "@type": "Organization",
    "@id": "https://example.com/#organization"
  }
}
```

---

### 3.3. `ProfilePage` (author bio and about pages)

Google uses `ProfilePage` structured data to power author knowledge cards, verify author authority (E-E-A-T), and disambiguate creators across social platforms.

```json
{
  "@context": "https://schema.org",
  "@type": "ProfilePage",
  "@id": "https://example.com/about/#profilepage",
  "url": "https://example.com/about/",
  "name": "About Jane Doe",
  "mainEntity": {
    "@type": "Person",
    "@id": "https://example.com/about/#person",
    "name": "Jane Doe",
    "alternateName": "janedoe",
    "jobTitle": "Principal Software Engineer & Systems Architect",
    "description": "Software engineer specializing in Go systems programming, developer tooling, and distributed systems.",
    "image": "https://example.com/images/avatar.png",
    "url": "https://example.com/about/",
    "worksFor": {
      "@type": "Organization",
      "name": "Example Corp"
    },
    "sameAs": [
      "https://github.com/example",
      "https://www.linkedin.com/in/example/",
      "https://bsky.app/profile/example.bsky.social",
      "https://x.com/example"
    ]
  }
}
```

---

### 3.4. `Organization` (brand identity and entity grounding)

Declares the publishing entity, official brand logo, and authoritative web footprints.

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Example Engineering",
  "url": "https://example.com/",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/images/logo.png",
    "width": 512,
    "height": 512,
    "caption": "Example Engineering logo"
  },
  "sameAs": [
    "https://github.com/example",
    "https://bsky.app/profile/example.bsky.social",
    "https://www.linkedin.com/company/example"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "editorial",
    "url": "https://example.com/about/"
  }
}
```

---

### 3.5. `SoftwareApplication` (CLI tools, libraries, and open source packages)

Use this schema when releasing or documenting software packages, CLI utilities, or Go modules.

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://example.com/projects/tool/#software",
  "name": "DevTool",
  "description": "Automated code diagnostics, mutation testing, and style enforcement CLI.",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "programmingLanguage": "Go",
  "softwareVersion": "1.4.0",
  "codeRepository": "https://github.com/example/tool",
  "downloadUrl": "https://github.com/example/tool/releases",
  "author": {
    "@type": "Person",
    "name": "Jane Doe",
    "url": "https://example.com/about/"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
```

---

### 3.6. `VideoObject` (embedded technical walkthroughs and talks)

Use when embedding YouTube, Vimeo, or self-hosted video recordings of tutorials, presentations, or demos.

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Building an MCP Server in Go from Scratch",
  "description": "Full walkthrough of constructing a JSON-RPC Model Context Protocol server in Go.",
  "thumbnailUrl": [
    "https://example.com/images/video-thumb-16x9.jpg",
    "https://example.com/images/video-thumb-4x3.jpg"
  ],
  "uploadDate": "2026-07-29T12:00:00Z",
  "duration": "PT14M32S",
  "contentUrl": "https://example.com/videos/mcp-server-go.mp4",
  "embedUrl": "https://www.youtube-nocookie.com/embed/example123",
  "publisher": {
    "@type": "Organization",
    "name": "Example Engineering",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/images/logo.png"
    }
  }
}
```

---

### 3.7. `ImageObject` (technical diagrams and licensable media)

Enables enhanced image previews and Google Images "Licensable" badges for proprietary architectural diagrams and graphics.

```json
{
  "@context": "https://schema.org",
  "@type": "ImageObject",
  "contentUrl": "https://example.com/images/architecture-diagram.png",
  "license": "https://creativecommons.org/licenses/by-sa/4.0/",
  "acquireLicensePage": "https://example.com/about/#licensing",
  "creditText": "Jane Doe",
  "creator": {
    "@type": "Person",
    "name": "Jane Doe"
  },
  "copyrightNotice": "© 2026 Jane Doe. CC BY-SA 4.0."
}
```

---

### 3.8. Subscription and paywalled content

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
    "name": "Jane Doe",
    "url": "https://example.com/about/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Example Engineering",
    "url": "https://example.com/"
  }
}
```

---

### 3.9. `BreadcrumbList` (navigational trail)

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
      "item": "https://example.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Posts",
      "item": "https://example.com/posts/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Building an MCP Server in Go",
      "item": "https://example.com/posts/mcp-server-go/"
    }
  ]
}
```

---

## 4. Structured data quality policies and rich result limits

### 4.1. Official Google deprecations and restrictions

Stay current with Google Search Central policy updates regarding rich result eligibility:

1. **`HowTo` Structured Data (Deprecated on Mobile / Restricted)**:
   - In September 2023, Google deprecated `HowTo` rich results on mobile devices and drastically restricted them on desktop.
   - **Recommendation**: Do not depend on `HowTo` markup for mobile SERP dominance. Mark technical walkthroughs with `TechArticle` instead. If `HowTo` is included for non-Google consumers, keep it supplementary.
2. **`FAQPage` Structured Data (Restricted to Authority Domains)**:
   - In August 2023, Google restricted `FAQPage` rich results exclusively to well-known authoritative government (`.gov`) and health organization websites.
   - Standard commercial, personal, and tech blogs will **not** receive collapsible FAQ accordion rich results in SERPs, even if the schema is 100% valid.

---

### 4.2. Core quality policies and validation rules

To prevent algorithmic demotion or manual actions for spammy structured data:

1. **Visible Content Requirement**: Structured data must accurately represent the content visible to human visitors on the rendered page. Never markup invisible elements, hidden keywords, or phantom reviews.
2. **Relevance & Specificity**: Use the most specific applicable Schema type (e.g., prefer `TechArticle` over generic `Article` or `Thing`).
3. **No Deceptive Pricing or Authorship**: Attributes like `author.name`, `datePublished`, and `isAccessibleForFree` must match the page text verbatim.

---

### 4.3. Interaction with robots directives

Understanding how Googlebot reconciles robots meta tags with Schema markup:

1. **`max-snippet` Scope**:
   - Setting `<meta name="robots" content="max-snippet:50">` limits the textual snippet drawn from `article.description` or prose to 50 characters.
   - **It does NOT restrict other structured data rich results** (such as breadcrumb badges, video cards, software metadata, or author attribution).
2. **`data-nosnippet` and Structured Data**:
   - Wrapping HTML content in `<div data-nosnippet>` instructs Google not to use that HTML block in search text snippets.
   - **Schema declared inside or describing `data-nosnippet` sections remains 100% valid for structured data parsing and rich results.**

---

## 5. Implementation in static site generators

### 5.1. Hugo partial implementation

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
    "name": {{ .Site.Params.author.name | default "Author Name" | jsonify }},
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

## 6. Agent skills and open knowledge catalogs (`@graph` architecture)

For developer portals, agent skill registries, and open-source documentation hubs (e.g. `skills.example.com`), multiple Schema entities must be interconnected cleanly in a single `@graph` array.

### 6.1. Skill detail page schema (`@graph` implementation)

Combines `Person` (author), `Organization` (consistent publishing entity), `SoftwareApplication` (the skill package), `TechArticle` (the documentation), and `BreadcrumbList` (navigation):

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://example.com/about/#person",
      "name": "Jane Doe",
      "jobTitle": "Principal Software Engineer",
      "worksFor": {
        "@type": "Organization",
        "name": "Example Corp",
        "url": "https://example.com/"
      },
      "url": "https://example.com/about/",
      "image": "https://example.com/images/avatar.png",
      "sameAs": [
        "https://github.com/example",
        "https://www.linkedin.com/in/example/",
        "https://bsky.app/profile/example.bsky.social",
        "https://x.com/example"
      ]
    },
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Example Engineering",
      "url": "https://example.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://example.com/apple-touch-icon.png"
      }
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://skills.example.com/tools/acme-cli/#software",
      "name": "acme-cli",
      "applicationCategory": "DeveloperApplication",
      "operatingSystem": "Cross-platform",
      "image": "https://example.com/apple-touch-icon.png",
      "description": "Best practices and guidelines for building developer workflows with acme-cli.",
      "softwareVersion": "1.2.0",
      "license": "https://www.apache.org/licenses/LICENSE-2.0",
      "url": "https://skills.example.com/tools/acme-cli/",
      "downloadUrl": "https://skills.example.com/tools/acme-cli/SKILL.md",
      "codeRepository": "https://github.com/example/acme-cli",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "author": {
        "@type": "Person",
        "@id": "https://example.com/about/#person",
        "name": "Jane Doe",
        "url": "https://example.com/about/"
      },
      "publisher": {
        "@type": "Organization",
        "@id": "https://example.com/#organization",
        "name": "Example Engineering"
      }
    },
    {
      "@type": "TechArticle",
      "@id": "https://skills.example.com/tools/acme-cli/#article",
      "headline": "acme-cli Documentation",
      "description": "Best practices and guidelines for building developer workflows with acme-cli.",
      "image": "https://example.com/apple-touch-icon.png",
      "url": "https://skills.example.com/tools/acme-cli/",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://skills.example.com/tools/acme-cli/"
      },
      "datePublished": "2026-01-01T00:00:00Z",
      "dateModified": "2026-08-20T00:00:00Z",
      "author": {
        "@type": "Person",
        "@id": "https://example.com/about/#person",
        "name": "Jane Doe",
        "url": "https://example.com/about/"
      },
      "publisher": {
        "@type": "Organization",
        "@id": "https://example.com/#organization",
        "name": "Example Engineering",
        "logo": {
          "@type": "ImageObject",
          "url": "https://example.com/apple-touch-icon.png"
        }
      },
      "about": {
        "@id": "https://skills.example.com/tools/acme-cli/#software"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://skills.example.com/tools/acme-cli/#breadcrumbs",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Catalog",
          "item": "https://skills.example.com/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Developer Tools",
          "item": "https://skills.example.com/tools/"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "acme-cli",
          "item": "https://skills.example.com/tools/acme-cli/"
        }
      ]
    }
  ]
}
```

---

### 6.2. Catalog root and homepage schema

On catalog root domains, define the global `@graph` connecting the author, publisher organization, `WebSite` entity (for Google Site Names), and the `CollectionPage`:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://example.com/about/#person",
      "name": "Jane Doe",
      "url": "https://example.com/about/",
      "jobTitle": "Principal Software Engineer",
      "worksFor": {
        "@type": "Organization",
        "name": "Example Corp",
        "url": "https://example.com/"
      },
      "image": "https://example.com/images/avatar.png",
      "sameAs": [
        "https://github.com/example",
        "https://www.linkedin.com/in/example/",
        "https://bsky.app/profile/example.bsky.social",
        "https://x.com/example"
      ]
    },
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Example Engineering",
      "url": "https://example.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://example.com/apple-touch-icon.png"
      }
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "url": "https://skills.example.com/",
      "name": "example/skills",
      "description": "A curated collection of specialized Agent Skills for coding, game development, generative media, writing, and engineering standards.",
      "publisher": { "@id": "https://example.com/#organization" }
    },
    {
      "@type": "CollectionPage",
      "@id": "https://skills.example.com/#catalog",
      "url": "https://skills.example.com/",
      "name": "Agent Skills Catalog",
      "isPartOf": { "@id": "https://example.com/#website" },
      "about": {
        "@type": "ItemList",
        "name": "All Agent Skills",
        "itemListElement": [
          {
            "@type": "ListItem",
            "position": 1,
            "name": "acme-cli",
            "description": "Best practices for building developer workflows with acme-cli.",
            "url": "https://skills.example.com/tools/acme-cli/"
          }
        ]
      }
    }
  ]
}
```

---

## 7. Google Rich Results data quality and warning elimination guide

When validating with [Google's Rich Results Test](https://search.google.com/test/rich-results), Google enforces strict property rules:

| Issue / Warning in Test | Root Cause | Exact Solution |
| :--- | :--- | :--- |
| **"No rich results detected" on Homepage** | Normal behavior: Google Rich Results tool only evaluates rich snippet card types (Articles, Products, Recipes). Root `Person`, `Organization`, and `WebSite` nodes are used for Google Knowledge Graph and Site Names, not rich snippets. | No fix needed. Ensure `WebSite.name`, `Organization.logo`, and `Person.sameAs` are present for Knowledge Graph. |
| **"Missing field 'image'" (in 'TechArticle' or 'Article')** | Google requires a hero image or app icon for visual article cards. | Add `"image": "https://example.com/apple-touch-icon.png"` (or an array of 16x9, 4x3, 1x1 image URLs) directly to `TechArticle`. |
| **"Missing field 'name' (in 'author')"** | Referring to `author` solely by `@id` causes isolated entity validators to fail if they do not resolve the graph link inline. | Inline the author name & URL: <br>`"author": { "@type": "Person", "@id": "https://example.com/about/#person", "name": "Jane Doe", "url": "https://example.com/about/" }` |
| **"Missing field 'publisher.logo'"** | `publisher` reference lacks a resolvable image URL. | Include `"logo": { "@type": "ImageObject", "url": "https://example.com/apple-touch-icon.png" }` on the `Organization`. |
| **"Unrecognized value for 'operatingSystem'"** | Using `"Any"` is non-standard in Google's taxonomy. | Change `"Any"` to `"Cross-platform"` or `"macOS, Linux, Windows"`. |
| **"Invalid 'mainEntityOfPage'"** | Providing `mainEntityOfPage` as a plain string URL can fail type checkers. | Format as an object: <br>`"mainEntityOfPage": { "@type": "WebPage", "@id": "https://skills.example.com/..." }` |
| **Organization Identity Inconsistency** | Child pages define competing organization entities (e.g., `example/skills` vs `example.com`). | Standardize the organization root entity across all pages to `https://example.com/#organization` with name `"Example Engineering"`. |

---

## 8. Testing and validation checklist

Always validate your structured data prior to publication:

1. **Google Rich Results Test**: [https://search.google.com/test/rich-results](https://search.google.com/test/rich-results)
   - Verify that your URL or code snippet passes with **0 errors and 0 critical warnings**.
2. **Schema Markup Validator**: [https://validator.schema.org/](https://validator.schema.org/)
   - Confirm standard Schema.org syntactic compliance and `@type` inheritance across all `@graph` entities.
3. **Automated CI Validation**:
   - Ensure your build pipeline verifies that emitted `<script type="application/ld+json">` blocks contain valid, parseable JSON.

