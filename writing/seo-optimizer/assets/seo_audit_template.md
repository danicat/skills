# Technical SEO and GEO audit report

**Article:** `{{ ARTICLE_TITLE }}`
**File path:** `{{ FILE_PATH }}`
**Auditor:** `seo-optimizer` Agent Skill
**Date:** `{{ AUDIT_DATE }}`

---

## 1. Executive summary and health score

| Dimension | Target benchmark | Current score | Status |
| :--- | :--- | :--- | :--- |
| **Traditional technical SEO** | 85 to 100 / 100 | `{{ SEO_SCORE }}/100` | {{ SEO_STATUS }} |
| **Generative engine (GEO)** | 80 to 100 / 100 | `{{ GEO_SCORE }}/100` | {{ GEO_STATUS }} |
| **Readability (Fog Index)** | 11.0 to 15.0 | `{{ FOG_INDEX }}` | {{ FOG_STATUS }} |
| **AI slop score** | < 25 / 100 | `{{ SLOP_SCORE }}` | {{ SLOP_STATUS }} |

---

## 2. Metadata split and frontmatter audit

### Current frontmatter
```yaml
title: "{{ CURRENT_TITLE }}"
summary: "{{ CURRENT_SUMMARY }}"
description: "{{ CURRENT_DESCRIPTION }}"
categories: {{ CURRENT_CATEGORIES }}
tags: {{ CURRENT_TAGS }}
```

### Proposed optimized frontmatter
```yaml
title: "{{ OPTIMIZED_TITLE }}"
summary: "{{ OPTIMIZED_SUMMARY }}"
description: "{{ OPTIMIZED_DESCRIPTION }}"
categories: {{ OPTIMIZED_CATEGORIES }}
tags: {{ OPTIMIZED_TAGS }}
```

- **Title analysis:** Length `{{ TITLE_LEN }}` chars, front-loaded with the primary entity.
- **Description vs. summary analysis:**
  - `summary` provides an editorial hook for on-site cards.
  - `description` provides a keyword-dense direct answer snippet for Google Search and LLMs.

---

## 3. Heading and content structure

- **Heading outline:**
  - `H1`: Provided via frontmatter title
  - `H2`: `{{ H2_COUNT }}` sections
  - `H3`: `{{ H3_COUNT }}` subsections
- **Hierarchy status:** `{{ HIERARCHY_STATUS }}` (zero skipped heading levels).
- **Inverted pyramid status:** Lead section states a direct one-sentence answer within the opening `150` words.

---

## 4. Accessibility and asset review

| Asset | Current alt text | Recommendation |
| :--- | :--- | :--- |
| `image.png` | `{{ CURRENT_ALT }}` | `{{ OPTIMIZED_ALT }}` |

---

## 5. Schema.org JSON-LD verification

- **Primary type:** `TechArticle`
- **Dependencies:** `{{ DEPENDENCIES }}`
- **Proficiency level:** `{{ PROFICIENCY_LEVEL }}`
- **Author entity:** {{ AUTHOR_NAME }}
- **Publisher entity:** {{ PUBLISHER_NAME }}

---

## 6. Actionable implementation checklist

- [ ] Update frontmatter with distinct `summary` and `description` values.
- [ ] Refine image `alt` text to explain diagrams clearly.
- [ ] Add a direct-answer definition block under the first major `H2`.
- [ ] Verify clean static build output and HTML `<head>` tags.
