---
name: find-examples
description: Find and inspect GitHub code examples for specific dependencies and languages. Use this to see how a library or framework is used in projects.
---

# Find Examples

Find GitHub code examples for dependencies.

## Workflow

### 1. Search for Repositories (Multi-Language)
Run the `github_search.py` script. If the target language lacks examples, include related languages supported by the SDK.

```bash
python3 scripts/github_search.py <dependency> --lang <lang1,lang2> --limit 5
```

**Example (Genkit Go/JS):**
```bash
python3 find-examples/scripts/github_search.py "genkit" --lang "go,typescript"
```

### 2. Prioritize and Select
Review the results. The script tags each repository with its language.
Prefer the target language when high-quality results exist. If the target language has few results, select a repository from a related language instead. For example, a TypeScript Genkit example can guide a Go implementation.

### 3. Create Examples Directory
```bash
mkdir -p _examples
```

### 4. Clone and Inspect
Clone the selected repositories into the `_examples` folder.

```bash
cd _examples && git clone <repo_url>
```

After cloning, search for implementation details with `list_files`, `smart_read`, or `grep_search`.

## Polyglot Translation Strategy
When translating an example from another language:
1. Identify the primary classes or functions (e.g., `DefineFlow` in JS usually maps to `DefineFlow` in Go).
2. Map objects/interfaces to Go structs or Python classes.
3. Observe how the SDK handles authentication, configuration, and error handling. These patterns usually persist across supported languages.

## Tips
- Check for high star counts and official or well-known organizations.
- Prefer repositories updated in the last 6 months to ensure compatibility with modern versions of the dependency.
- Search for specific symbol usages with `grep_search` inside cloned repositories of large frameworks.
