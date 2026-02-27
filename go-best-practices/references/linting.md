# Go Linting Guidelines

Linting is essential for maintaining a consistent, bug-free codebase. 

## Recommended Tooling: golangci-lint
[golangci-lint](https://golangci-lint.run/) is the industry standard. It aggregates multiple linters and runs them in parallel.

### Essential Linters
Every project should enable at least:
*   **`govet`**: Standard Go vet tool (shadowing, printf, mutex copies).
*   **`staticcheck`**: Deep analysis for bugs and performance.
*   **`errcheck`**: Ensures all errors are handled.
*   **`unused`**: Finds unused constants, variables, functions, and types.
*   **`gofmt` / `goimports`**: Enforce standard formatting and import grouping.

## Best Practices
1.  **CI Integration**: Run lints on every Pull Request. Treat lint warnings as errors (`--halt-on-error`).
2.  **No Naked `nolint`**: Use `//nolint:lintername` for specific exclusions, and **always** add a comment explaining *why* the exclusion is necessary.
    ```go
    //nolint:gosec // Replay attack risk is mitigated by token TTL
    func unsafeProcess() { ... }
    ```
3.  **Local Pre-commit**: Encourage developers to run `golangci-lint run` locally before pushing.
4.  **Auto-fix**: Use `--fix` to automatically resolve trivial issues (formatting, minor nits).

## Project Configuration
Maintain a `.golangci.yml` file in the project root to ensure every developer and CI runner uses the same rules.
