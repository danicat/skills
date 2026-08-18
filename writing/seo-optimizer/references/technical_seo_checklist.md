# Technical SEO Checklist for Developer Content & Static Sites

A rigorous, full-scope technical SEO checklist for engineering publications, developer documentation, and static site generators (Hugo, Astro, Next.js), strictly aligned with official Google Search Central guidelines and Generative Engine Optimization (GEO) standards.

---

## 1. Head HTML Integrity & Document Structure

The `<head>` section is parsed sequentially by browsers and search engine crawlers. Structural defects in `<head>` can cause premature closure of the head context, resulting in dropped `<meta>` tags, unparsed canonical links, and indexing failures.

- [ ] **Strict `<head>` Tag Hygiene**:
  - Ensure all tags opened in `<head>` are properly closed or self-closing.
  - **Never place body elements inside `<head>`**: Elements like `<img>`, `<div>`, `<iframe>`, `<p>`, or unclosed script tags force HTML parsers to prematurely terminate the `<head>` and implicitly open `<body>`. Any subsequent `<meta>`, `<link rel="canonical">`, or `<title>` tags will be ignored by Googlebot.
- [ ] **Valid Charset Declaration in First 1024 Bytes**:
  - Place `<meta charset="utf-8">` as the very first element inside `<head>`.
  - Use valid quoting syntax (`<meta charset="utf-8">` or `<meta http-equiv="Content-Type" content="text/html; charset=utf-8">`).
- [ ] **Viewport Configuration**:
  - Include `<meta name="viewport" content="width=device-width, initial-scale=1">` to signal mobile-friendliness and trigger responsive layout evaluation.
- [ ] **Single `H1` Tag Per Page**:
  - Exactly one `H1` element per document, representing the primary document title and search intent.
  - In static site generators (Hugo, Astro), ensure the `H1` is rendered by the layout template from frontmatter `title`. Do **not** duplicate `# Title` at the beginning of the markdown body.
- [ ] **Strict Sequential Heading Nesting (`H1` -> `H2` -> `H3` -> `H4`)**:
  - Never skip heading levels (e.g., jumping directly from `H2` to `H4`).
  - Use descriptive, intent-focused heading text that clearly explains the subtopic rather than ambiguous metaphors.

---

## 2. Titles & Meta Descriptions

Titles and descriptions determine SERP snippet display and supply critical grounding context for AI Overviews and answer synthesis.

- [ ] **Dual-Purpose Metadata Split**:
  - **`summary` (For Humans)**: Curiosity-inducing editorial teaser (80–180 chars) for homepage feeds and social cards.
  - **`description` (For Search & LLM Engines)**: Factual, direct answer (120–160 chars) loaded into `<meta name="description">` and JSON-LD `description`.
  - Never duplicate identical text between `summary` and `description`.
- [ ] **Title Tag Optimization (`<title>`)**:
  - **Length**: **40–60 characters** (under 40 lacks signal; over 60 gets truncated on desktop and mobile SERPs).
  - **Front-Loading**: Place the primary keyword / core technology stack within the first 3 words (e.g., *"Building an MCP Server in Go"*).
  - **Brand Suffix**: Append brand/site suffix via layout templates (e.g., `<title>{{ .Title }} | example.com</title>`), not manually in markdown frontmatter.
- [ ] **Meta Description Formatting (`<meta name="description">`)**:
  - **Length**: **120–160 characters**.
  - **Content Formula**: Context / Problem + Core Technical Solution.
  - **Clean Formatting**: Plain text only; escape or avoid unescaped double quotes (`"`) that prematurely terminate the HTML attribute.
- [ ] **Robots Meta Directives**:
  - Include the standard crawl and preview directives in your base template:
    ```html
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
    ```
  - `max-image-preview:large`: Enables high-resolution thumbnail cards in Google Discover and SERPs.
  - `max-snippet:-1`: Enables optimal text snippet generation for Google Search and AI Overviews.
- [ ] **No Unsupported Keywords Meta Tag**:
  - Do **not** include `<meta name="keywords">`; Google Search completely ignores it.

---

## 3. Site Attribution & Visual Assets

Proper visual identity markup guarantees crisp site attribution badges and eligibility for Google Discover visual feeds.

- [ ] **High-Resolution Favicon / Site Icon**:
  - Provide a square icon that is a multiple of **48px** (e.g., `48x48`, `96x96`, `144x144`, `192x192`, or SVG).
  - Ensure the favicon URL is stable and statically declared in `<head>`:
    ```html
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/icon.svg" type="image/svg+xml">
    ```
  - Googlebot requires open access to the favicon file (do not block in `robots.txt`).
- [ ] **`WebSite` Structured Data for Site Name in SERPs**:
  - Include a `WebSite` JSON-LD object on the root domain declaring official `name` and `alternateName` arrays to ensure Google displays the correct brand name in SERP headers.
- [ ] **Google Discover Hero Images**:
  - Every article should feature a high-quality visual asset at least **1200px wide**.
  - Maintain a standard aspect ratio: `16:9` (recommended, e.g., 1200x675), `4:3`, or `1:1`.
  - Pair with `<meta name="robots" content="max-image-preview:large">`.
- [ ] **Descriptive Image `alt` Text**:
  - Provide informative, context-rich alternative text (30–100 characters) for every image and architecture diagram.
  - *Bad*: `alt="diagram"` or `alt="screenshot"`
  - *Good*: `alt="Sequence diagram showing JSON-RPC handshake between Gemini CLI client and Go MCP server"`

---

## 4. Crawlable Link Architecture & Outbound Link Qualification

Google discovers and evaluates web topology exclusively through standard crawlable hyperlinks.

- [ ] **Crawlable Standard HTML Links (`<a href="...">`)**:
  - Use real `<a href="/target-path/">` elements with resolvable URLs.
  - **Avoid JS-only pseudo-links**: Googlebot does not execute or discover links implemented via `<span onclick="...">`, `<a href="javascript:void(0)">`, `<a href="#">`, or programmatic `window.location` triggers.
- [ ] **Pagination & Archive Navigation**:
  - Provide static, crawlable `<a>` links for multi-page archives (e.g., `/posts/page/2/`).
  - Do not rely entirely on client-side infinite scroll without a server-rendered HTML pagination fallback.
- [ ] **Outbound Link Qualification (`rel` Attributes)**:
  - Qualify outbound links according to Google Search Central specifications:
    - **`rel="sponsored"`**: For paid links, sponsorships, advertisements, and affiliate links.
    - **`rel="ugc"`**: For user-generated content (comments, community forums, guest contributions).
    - **`rel="nofollow"`**: For untrusted references or links where you do not endorse the destination.
  - Multi-value qualification: Use space-separated or comma-separated syntax (e.g., `rel="ugc nofollow"` or `rel="sponsored nofollow"`).
- [ ] **Zero Internal `nofollow` Links**:
  - **Never** place `rel="nofollow"` on internal links between your own site pages. Doing so fragments PageRank distribution and blocks Googlebot from crawling your internal content graph.
- [ ] **Descriptive Internal Anchor Text**:
  - Always link using descriptive topic names or target article titles (e.g., `[Building an MCP Server in Go]({{< ref "..." >}})`).
  - Avoid generic anchor text such as *"click here"*, *"link"*, or raw naked URLs.

---

## 5. HTTP Status & Redirect Hygiene

Clean HTTP response codes ensure efficient crawl budget usage and rapid search index updates.

- [ ] **301 Permanent Redirects Over Client-Side Refresh**:
  - Always execute server-level HTTP `301 Moved Permanently` redirects for renamed or relocated URLs.
  - Do **not** use `<meta http-equiv="refresh">` tags or JavaScript redirects, as they delay index updates and transfer link signals poorly.
- [ ] **Soft 404 Prevention**:
  - Ensure missing, non-existent, or invalid URLs return a genuine HTTP `404 Not Found` or `410 Gone` status code.
  - Never return an HTTP `200 OK` response with a visual "Page Not Found" message in the body (a "Soft 404"). Google will drop soft 404 pages from the index while wasting crawl capacity.
- [ ] **Explicit HTTP 410 Gone for Deleted Content**:
  - Return HTTP `410 Gone` for permanently removed articles and deprecated resources. Googlebot recognizes `410` as intentional and de-indexes the URL faster than with standard `404`.
- [ ] **Canonical Link Hygiene (`<link rel="canonical">`)**:
  - Every page must render a single, self-referencing canonical URL in `<head>`:
    ```html
    <link rel="canonical" href="https://example.com/posts/mcp-server-go/">
    ```
  - Ensure the canonical URL matches the canonical trailing slash convention and protocol (`https://`).

---

## 6. Multilingual & International Parity

Multilingual technical sites must provide crystal-clear language signals without falling into international indexing traps.

- [ ] **`hreflang` Implementation Methods**:
  - Declare language and regional alternate URLs using one of three supported methods:
    1. HTML `<link rel="alternate" hreflang="..." href="...">` tags in `<head>`.
    2. HTTP `Link:` response headers (ideal for non-HTML assets).
    3. XML Sitemaps (`<xhtml:link rel="alternate" ...>`).
- [ ] **Bidirectional Parity & Self-Referencing**:
  - If English page `A` references Japanese page `B`, page `B` **must** reference page `A`.
  - Every page must include its **own** URL in the `hreflang` set (self-reference).
  - Include an `x-default` entry pointing to the default fallback language edition.
- [ ] **Valid ISO Language & Region Codes**:
  - Use **ISO 639-1** for language codes (e.g., `en`, `ja`, `pt`, `de`, `es`).
  - Use **ISO 3166-1 Alpha 2** for optional country codes (e.g., `pt-BR`, `en-GB`, `en-US`).
  - ❌ **No UN M.49 Regional Codes (e.g., `es-419`)**: Google `hreflang` does **not** support regional UN M.49 codes like `419` (Latin America). Use language-only `es` or specific country codes like `es-MX`, `es-AR`.
  - ❌ **No Standalone Country Codes**: Do not use country codes alone (e.g., `be` is Belarusian language, not Belgium).
- [ ] **No Side-by-Side Dual Translations on One Page**:
  - Never publish dual-language text side-by-side on the same URL (e.g., English paragraph followed by Portuguese translation). This confuses Google's automated language detector and breaks snippet rendering.
- [ ] **Vanity ccTLD Recognition**:
  - Recognize that Google treats 20 country-code top-level domains as generic top-level domains (gTLDs), including: `.ad`, `.ai`, `.as`, `.bz`, `.cc`, `.cd`, `.co`, `.dj`, `.fm`, `.io`, `.la`, `.me`, `.ms`, `.nu`, `.sc`, `.sr`, `.su`, `.tk`, `.tv`, `.ws`. These domains are not geotargeted to specific geographic countries.
- [ ] **Zero IP-Based Auto-Redirects**:
  - Never redirect users automatically based on IP geolocation or `Accept-Language` headers. Googlebot crawls primarily from US IP addresses without localized language headers; auto-redirects will prevent localized pages from being crawled. Provide an accessible manual language switcher instead.

---

## 7. Schema.org Validation & AI Grounding

Structured data provides direct entity grounding for generative search engines and powers rich result badges in SERPs.

- [ ] **Full JSON-LD Implementation**:
  - Implement appropriate Schemas: `TechArticle`, `Article`, `WebSite`, `ProfilePage`, `Organization`, `SoftwareApplication`, and `BreadcrumbList`.
- [ ] **Visible Content Match**:
  - Ensure all structured data attributes (`headline`, `author`, `datePublished`, `dependencies`) correspond to visible text on the page.
- [ ] **Avoid Deprecated Rich Result Targets**:
  - Do not rely on `HowTo` schema for mobile SERPs (deprecated by Google on mobile).
  - Do not expect `FAQPage` accordion rich results on commercial or blog sites (restricted to government/health authorities).
- [ ] **IPTC Standards for AI-Generated Images**:
  - For AI-generated artwork or diagrams, embed IPTC `DigitalSourceType` metadata (`trainedAlgorithmicMedia` or `compositeWithTrainedAlgorithmicMedia`) to ensure compliance with Google Image metadata and AI transparency standards.
- [ ] **Rich Results Test Verification**:
  - Test all templates with the [Google Rich Results Test](https://search.google.com/test/rich-results) and confirm **0 errors and 0 critical warnings**.

---

## 8. Core Web Vitals & Mobile-First Parity

Page experience and responsive performance metrics serve as baseline ranking and usability gates.

- [ ] **Core Web Vitals Metric Targets (75th Percentile)**:
  - **Largest Contentful Paint (LCP)**: **< 2.5 seconds** (optimize hero images, inline critical CSS, pre-connect CDN origins).
  - **Interaction to Next Paint (INP)**: **< 200 milliseconds** (minimize long-running JavaScript main-thread tasks).
  - **Cumulative Layout Shift (CLS)**: **< 0.1** (set explicit `width` and `height` dimensions on all images, diagrams, and video embeds).
- [ ] **100% Desktop / Mobile DOM Parity**:
  - Under Mobile-First Indexing, Googlebot indexes exclusively the mobile view of your page.
  - Ensure the mobile DOM contains **100% parity** with the desktop version:
    - Identical body text, headings, and code blocks.
    - Identical structured data (`<script type="application/ld+json">`).
    - Identical meta tags and robots directives.
    - Identical internal links, image elements, and alt text.
    - Never hide essential content or links behind desktop-only CSS rules (`display: none`).

---

## Quick Reference Summary Table

| Category | Primary Metric / Requirement | Tool / Validation |
| :--- | :--- | :--- |
| **Document Structure** | Single `H1`, no unclosed head tags, UTF-8 in first 1KB | W3C Validator / Lighthouse |
| **Titles & Descriptions** | Title: 40–60 chars, Desc: 120–160 chars, Split Summary | `scripts/audit_seo.py` |
| **Attribution & Images** | Favicon $\ge 48\text{px}$, Discover Hero $\ge 1200\text{px}$, `max-image-preview:large` | Lighthouse / Chrome DevTools |
| **Link Architecture** | Crawlable `<a href>`, `rel="sponsored"`, `rel="ugc"`, no internal `nofollow` | Google Search Console |
| **Redirect Hygiene** | 301 server redirects, true 404/410 status codes, self-referencing canonical | `curl -I <URL>` |
| **Multilingual Parity** | Bidirectional `hreflang`, ISO 639-1 / 3166-1, no `es-419`, no IP auto-redirects | `hreflang` Testing Tool |
| **Structured Data** | Valid JSON-LD, `TechArticle`, `ProfilePage`, IPTC AI image metadata | Google Rich Results Test |
| **Core Web Vitals** | LCP $< 2.5\text{s}$, INP $< 200\text{ms}$, CLS $< 0.1$, 100% Mobile DOM Parity | PageSpeed Insights / CrUX |
