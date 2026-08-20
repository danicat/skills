# Technical SEO & Generative Engine Optimization (GEO) Audit Report

**Article:** `{{ ARTICLE_TITLE }}`
**File Path:** `{{ FILE_PATH }}`
**Auditor:** `seo-optimizer` Agent Skill
**Date:** `{{ AUDIT_DATE }}`

---

## 1. Executive Summary & Health Score

| Dimension | Target Benchmark | Current Score | Status |
| :--- | :--- | :--- | :--- |
| **Traditional Technical SEO** | 85–100 / 100 | `{{ SEO_SCORE }}/100` | {{ SEO_STATUS }} |
| **Generative Engine (GEO)** | 80–100 / 100 | `{{ GEO_SCORE }}/100` | {{ GEO_STATUS }} |
| **Readability (Fog Index)** | 11.0–15.0 | `{{ FOG_INDEX }}` | {{ FOG_STATUS }} |
| **AI Slop Score** | < 25 / 100 | `{{ SLOP_SCORE }}` | {{ SLOP_STATUS }} |

---

## 2. Metadata Split & Frontmatter Audit

### Current Frontmatter:
```yaml
title: "{{ CURRENT_TITLE }}"
summary: "{{ CURRENT_SUMMARY }}"
description: "{{ CURRENT_DESCRIPTION }}"
categories: {{ CURRENT_CATEGORIES }}
tags: {{ CURRENT_TAGS }}
```

### Proposed Optimized Frontmatter:
```yaml
title: "{{ OPTIMIZED_TITLE }}"
summary: "{{ OPTIMIZED_SUMMARY }}"
description: "{{ OPTIMIZED_DESCRIPTION }}"
categories: {{ OPTIMIZED_CATEGORIES }}
tags: {{ OPTIMIZED_TAGS }}
```

- **Title Analysis:** Length: `{{ TITLE_LEN }}` chars. Front-loaded with primary entity.
- **Description vs Summary Analysis:**
  - `summary` provides an engaging editorial hook for on-site cards.
  - `description` provides a dense, keyword-rich direct answer snippet for Google and LLMs.

---

## 3. Heading & Content Structure

- **Heading Outline:**
  - `H1`: Provided via frontmatter title
  - `H2`: {{ H2_COUNT }} sections
  - `H3`: {{ H3_COUNT }} subsections
- **Hierarchy Status:** {{ HIERARCHY_STATUS }} (No skipped heading levels).
- **Inverted Pyramid Status:** Lead section contains definitive 1-sentence answer hook within opening 150 words.

---

## 4. Accessibility & Asset Review

| Asset | Current Alt Text | Recommendation |
| :--- | :--- | :--- |
| `image.png` | `{{ CURRENT_ALT }}` | `{{ OPTIMIZED_ALT }}` |

---

## 5. Schema.org JSON-LD Verification

- **Primary Type:** `TechArticle`
- **Dependencies:** `{{ DEPENDENCIES }}`
- **Proficiency Level:** `{{ PROFICIENCY_LEVEL }}`
- **Author Entity:** {{ AUTHOR_NAME }}
- **Publisher Entity:** {{ PUBLISHER_NAME }}

---

## 6. Actionable Implementation Checklist

- [ ] Update frontmatter with distinct `summary` and `description`.
- [ ] Refine image alt text to describe architectural diagrams.
- [ ] Add direct-answer definition block under first major `H2`.
- [ ] Verify clean build in static generator.
