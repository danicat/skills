# Google Search Meta Tags, Attributes, and Robots Directives

A complete reference on supported HTML `<meta>` tags, indexing attributes, robots directives, and HTTP headers based on official Google Search Central specifications.

---

## 1. Supported `<meta>` Tags Overview

Placed within the `<head>` element of an HTML document:

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Article Title - Brand</title>
  <meta name="description" content="120–160 character description of page content.">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <meta name="google-site-verification" content="verification_token_here">
</head>
```

### Supported Meta Tags Table

| Meta Tag | Syntax / Example | Purpose & Notes |
| :--- | :--- | :--- |
| **`description`** | `<meta name="description" content="...">` | Short, accurate summary. Often used as the SERP snippet when more descriptive than page text. |
| **`robots`** | `<meta name="robots" content="...">` | Controls crawling and indexing for **all** search engine crawlers. |
| **`googlebot`** | `<meta name="googlebot" content="...">` | Controls crawling/indexing specifically for `Googlebot` (text search). |
| **`googlebot-news`** | `<meta name="googlebot-news" content="...">` | Controls crawling/indexing specifically for Google News. |
| **`google-site-verification`** | `<meta name="google-site-verification" content="...">` | Verifies domain/site ownership in Google Search Console. Case-sensitive value. |
| **`notranslate`** | `<meta name="googlebot" content="notranslate">` | Prevents Google from offering automated translation of title and snippet. |
| **`nopagereadaloud`** | `<meta name="google" content="nopagereadaloud">` | Prevents Google text-to-speech (TTS) services from reading aloud page content. |
| **`Content-Type` / `charset`** | `<meta charset="utf-8">` | Declares document encoding. Unicode/UTF-8 is recommended. |
| **`viewport`** | `<meta name="viewport" content="width=device-width, initial-scale=1">` | Directs responsive layout rendering; signals mobile-friendliness. |
| **`rating`** | `<meta name="rating" content="adult">` | Flags adult/sexually-explicit content for SafeSearch filtering. |

---

## 2. Valid Robots Directives & Indexing Rules

Robots directives can be combined with commas (e.g. `content="noindex, nofollow"`) or split into multiple tags.

| Directive | Function | Impact on Generative AI |
| :--- | :--- | :--- |
| **`all`** | Default. No restrictions on indexing or snippet serving. | Full eligibility. |
| **`noindex`** | Prevents page from appearing in search results or AI features. | Excludes URL from search index. |
| **`nofollow`** | Tells Googlebot not to follow outbound links on this page. | Page still indexed, links not crawled. |
| **`none`** | Equivalent to `noindex, nofollow`. | Excludes URL and links. |
| **`nosnippet`** | Prevents text snippets and video previews in SERPs. | **Blocks content from being direct input for AI Overviews / AI Mode.** |
| **`max-snippet:[N]`** | Sets maximum textual snippet character length. Special values: `0` (equivalent to `nosnippet`), `-1` (unlimited). | Limits text input size for AI Overviews. |
| **`max-image-preview:[size]`** | Accepts `none`, `standard`, or `large`. Controls thumbnail size. | Governs multi-modal visual previews. |
| **`max-video-preview:[N]`** | Sets maximum video preview length in seconds (`0` to `-1`). | Controls video snippet duration. |
| **`notranslate`** | Prevents automated translation in search results. | Keeps source language in snippets. |
| **`noimageindex`** | Prevents images on the page from being indexed in Google Images. | Media excluded from Image search. |
| **`unavailable_after:[date]`** | Automatically stops indexing after an RFC 822 / ISO 8601 date. | Deprecates expired events/offers. |
| **`indexifembedded`** | Allows indexing if embedded in `iframe`, even if page has `noindex`. | Useful for widgets and embedded players. |

---

## 3. The `data-nosnippet` HTML Attribute

Use the `data-nosnippet` boolean attribute on `<span>`, `<div>`, or `<section>` tags to exclude specific text from search snippets and AI Overviews without affecting full-page indexing:

```html
<p>This tutorial explains how to build a Go MCP server.</p>

<!-- Exclude proprietary configuration or boilerplate from snippets -->
<div data-nosnippet>
  <p>Internal tracking code and environment specifics not needed in snippets.</p>
</div>
```

---

## 4. Qualifying Outbound Links (`rel` Attributes)

Tell Google your relationship to outbound linked URLs:

| `rel` Attribute | When to Use | Example |
| :--- | :--- | :--- |
| **`rel="sponsored"`** | Paid links, sponsored placements, affiliate partnerships. | `<a href="https://partner.com" rel="sponsored">Partner</a>` |
| **`rel="ugc"`** | User-generated content (comments, forum posts, guest submissions). | `<a href="https://example.com" rel="ugc">Commenter Link</a>` |
| **`rel="nofollow"`** | Untrusted content or when you want no association passed. | `<a href="https://untrusted.com" rel="nofollow">Reference</a>` |
| **Combined** | Space-separated values for complex cases. | `<a href="..." rel="ugc nofollow">External Link</a>` |

---

## 5. Unsupported & Ignored Tags (Do Not Rely On)

The following tags are **explicitly ignored by Google Search**:

- ❌ `<meta name="keywords" content="...">`: Completely ignored by Google Search. Has 0 impact on ranking or indexing.
- ❌ HTML `lang` attribute (e.g. `<html lang="en">`): Google does **not** rely on code-level `lang` attributes for language detection; it uses algorithmic text analysis on visible body prose.
- ❌ `<link rel="next" href="...">` and `<link rel="prev" href="...">`: Deprecated and ignored.
- ❌ `<meta name="google" content="nositelinkssearchbox">`: Feature no longer exists.
- ❌ `<meta name="robots" content="noarchive">` & `nocache`: Cached page feature no longer exists.

---

## 6. Server-Side HTTP Headers (`X-Robots-Tag`)

For non-HTML assets (PDFs, images, data files), use `X-Robots-Tag` headers in your web server configuration:

### NGINX Configuration:
```nginx
# Prevent indexing of PDF documents
location ~* \.pdf$ {
    add_header X-Robots-Tag "noindex, nofollow";
}

# Allow large image previews site-wide
location ~* \.(png|jpe?g|webp)$ {
    add_header X-Robots-Tag "max-image-preview:large";
}
```

### Apache Configuration:
```apache
<Files ~ "\.pdf$">
    Header set X-Robots-Tag "noindex, nofollow"
</Files>
```
