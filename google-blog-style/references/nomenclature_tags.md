# Nomenclature Tags for Codelabs

To ensure your codelab appears across Google and on the [codelabs homepage](https://codelabs.developers.google.com/), you must include specific tags in the `keywords` field of your YAML frontmatter.

## Required Tags

1.  **Document Type**: `docType:Codelab` (Mandatory for all codelabs).
2.  **Product/API**: Add specific tags for the primary focus (e.g., `product:VertexAI`, `product:BigQuery`, `api:GmpGeocodingApi`). Use the most specific tag available.
3.  **Skill Level**:
    - `skill:Beginner`
    - `skill:Intermediate`
    - `skill:Advanced`
4.  **Programming Language**: Add a tag for each language used (e.g., `language:Python`, `language:Java`).

## Optional Tags

- **Category**: Add if the industry/use-case is not inherited (e.g., `category:Financial`).
- **Event**: Add if created for a specific event (e.g., `event:GoogleIO2024`).

## Syntax
Tags must be a comma-separated list **without whitespace** between items.

### Example
```yaml
keywords: docType:Codelab,product:VertexAI,skill:Intermediate,language:Python
```
