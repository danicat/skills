# International & Multilingual SEO: `hreflang` Architecture

A complete guide to managing multilingual and multi-regional websites, implementing valid `hreflang` annotations, and structuring localized static sites for Google Search.

---

## 1. Multilingual vs. Multi-Regional Definitions

- **Multilingual Site**: Offers content translated into more than one language (e.g. `danicat.dev/` in English, `danicat.dev/ja/` in Japanese, `danicat.dev/pt-br/` in Portuguese). Google matches results based on query language.
- **Multi-Regional Site**: Explicitly targets users in different geographical countries/locales (e.g. `en-US`, `en-GB`, `en-AU`). Google matches results based on searcher region.

---

## 2. Recommended URL Architecture for Static Sites

| URL Structure | Example | Google Recommendation & Trade-offs |
| :--- | :--- | :--- |
| **Subdirectories with gTLD** | `danicat.dev/` (EN)<br>`danicat.dev/ja/` (JA)<br>`danicat.dev/pt-br/` (PT-BR) | **Recommended.** Low maintenance, shared domain authority, simple SSL and hosting setup. |
| **Subdomains with gTLD** | `ja.danicat.dev` | Acceptable, but splits domain authority and requires multiple SSL certs. |
| **Country-Code Domains (ccTLDs)** | `example.de`, `example.jp` | Strong geotargeting signal, but expensive, separate authority, and inflexible. |
| **URL Parameters** | `example.com?lang=ja` | ❌ **Not recommended.** Difficult segmentation, bad UX. |

> [!CAUTION]
> **Do NOT Use IP Sniffing or Auto-Redirects!**
> Googlebot crawlers originate almost exclusively from the United States and do not send `Accept-Language` headers. If you automatically redirect users based on IP or headers, Googlebot will never discover or index your localized `/ja/` or `/pt-br/` pages. Always serve default content at the URL and provide explicit on-page language switchers.

---

## 3. The 5 Invariable Rules of `hreflang`

```
+------------------------------------------------------------------------------+
| 1. Bidirectional Parity: If Page A links to Page B, Page B MUST link to A.   |
| 2. Self-Referencing: Every page must include its OWN URL in the set.         |
| 3. Fully-Qualified URLs: Must include protocol (https://danicat.dev/ja/...). |
| 4. ISO Codes: ISO 639-1 (Language) + optional ISO 3166-1 Alpha 2 (Region).   |
| 5. Fallback Default: Include hreflang="x-default" for unmatched locales.     |
+------------------------------------------------------------------------------+
```

### Supported Code Syntax & Gotchas:
- **Language Only**: `en`, `ja`, `pt`, `de`, `es`, `fr`
- **Language + Region**: `pt-BR`, `en-GB`, `en-US`, `de-CH`
- ❌ **Common Mistake - Country Code Alone**: Specifying `be` means **Belarusian language**, NOT Belgium! To target French in Belgium, use `fr-be`.
- ❌ **Common Mistake - Invalid Region Codes**: Using `uk` instead of `gb` (ISO 3166-1 Alpha 2 requires `gb` for the United Kingdom).
- ❌ **Script Variations**: For Chinese, use ISO 15924 scripts: `zh-Hans` (Simplified) or `zh-Hant` (Traditional).

---

## 4. Implementation in Hugo

### In `layouts/partials/head.html`:

```html
{{ if .IsTranslated }}
  <!-- Self-referencing link -->
  <link rel="alternate" hreflang="{{ .Language.Lang }}" href="{{ .Permalink }}" />

  <!-- Alternate translated pages -->
  {{ range .Translations }}
    <link rel="alternate" hreflang="{{ .Language.Lang }}" href="{{ .Permalink }}" />
  {{ end }}

  <!-- Fallback x-default pointing to default English canonical -->
  {{ with (index (where .AllTranslations "Language.Lang" "en") 0) }}
    <link rel="alternate" hreflang="x-default" href="{{ .Permalink }}" />
  {{ end }}
{{ end }}
```

### Resulting Rendered HTML:
```html
<link rel="alternate" hreflang="en" href="https://danicat.dev/posts/20260729-mcp-server-go/" />
<link rel="alternate" hreflang="ja" href="https://danicat.dev/ja/posts/20260729-mcp-server-go/" />
<link rel="alternate" hreflang="pt-br" href="https://danicat.dev/pt-br/posts/20260729-mcp-server-go/" />
<link rel="alternate" hreflang="x-default" href="https://danicat.dev/posts/20260729-mcp-server-go/" />
```

---

## 5. Duplicate Content Handling & Canonicalization

- **Fully Translated Pages**: Are **not** considered duplicates by Google Search. Each language version ranks for queries in that target language.
- **Partially Translated / Boilerplate-Only Pages**: If only headers/footers are translated but the main article body remains in English, Google treats it as duplicate content. **Always translate the full body prose.**
- **Canonical Tags**: Each localized edition (`/`, `/ja/`, `/pt-br/`) must have a self-referencing canonical tag `<link rel="canonical" href="...">` when the content is translated, accompanied by bidirectional `hreflang` annotations.
