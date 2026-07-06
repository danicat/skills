# Nomenclature Tags for Codelabs

Add tags to the `keywords` field of your YAML frontmatter. This helps your codelab appear on Google sites and the [codelabs homepage](https://codelabs.developers.google.com/).

## Required Tags

1.  **Document Type**: `docType:Codelab` (Required for all codelabs).
2.  **Product/API**: Add tags for the main product or API (e.g., `product:VertexAI`, `product:BigQuery`, `api:GmpGeocodingApi`). Use the most specific tag.
3.  **Skill Level**: Use one of these tags:
    - `skill:Beginner`
    - `skill:Intermediate`
    - `skill:Advanced`
4.  **Programming Language**: Add a tag for each language you use (e.g., `language:Python`, `language:Java`).

## Optional Tags

- **Category**: Add if the industry or use-case is not clear (e.g., `category:Financial`).
- **Event**: Add if you made the codelab for a specific event (e.g., `event:GoogleIO2024`).

## Syntax
Write tags as a comma-separated list. Do not use spaces.

### Example
```yaml
keywords: docType:Codelab,product:VertexAI,skill:Intermediate,language:Python
```
