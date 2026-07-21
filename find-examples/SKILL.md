---
name: find-examples
description: >
  Use this skill when you need to find real-world code examples, learn how an unfamiliar third-party library, API, SDK, or framework is used, or translate code patterns from other languages. Trigger when implementing integrations, resolving SDK setup/usage issues, or bootstrapping features where the user asks "how do I use X?", "show me an example of Y", or "integrate Y into my project".
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
---

# Find Examples

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

### 3. Clone and Inspect
Clone the selected repositories.

> [!CAUTION]
> **Workspace Contamination Rule (Severe)**: Do NOT clone external repositories containing package manifests (`go.mod`, `package.json`, `Cargo.toml`) directly into your active project workspace directories. Build tools and compilers (like `go build ./...`) will scan all subdirectories, detect the cloned project, and fail with severe type or import compilation errors.
>
> **Safe Cloning Destinations**:
> * **Primary Choice**: Clone external projects to a temporary directory outside the workspace (e.g., `/tmp/example-clones/`).
> * **Secondary Choice**: If you must clone inside the workspace for persistence, clone to a nested folder (such as `_examples/`), immediately append that folder name to the project's `.gitignore`, and configure compilers to exclude it.

> [!WARNING]
> **Git Nesting Safety**: Cloning nested Git repositories can corrupt your workspace's Git state. If you clone an external repository into the workspace, you must immediately remove its `.git` folder (e.g. `rm -rf _examples/cloned-repo/.git`) to prevent git from treating it as an accidental submodule or an untracked nested tree.

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
