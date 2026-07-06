# Go Linting Guidelines

Linters help maintain a consistent, bug-free codebase.

## Recommended Tooling: golangci-lint

[golangci-lint](https://golangci-lint.run/) aggregates multiple linters and runs them in parallel.

### Essential Linters

Every Go project should configure these linters:
*   `govet` checks for standard issues such as variable shadowing, incorrect printf formats, and copied mutexes.
*   `staticcheck` runs deep static analysis for correctness and performance.
*   `errcheck` ensures that all returned errors are handled or assigned.
*   `unused` finds unused constants, variables, functions, and types.
*   `gofmt` and `goimports` enforce standard code formatting and group import statements.

## Best Practices

*   Integrate the linter into the CI pipeline to run on every pull request, and configure it to treat warnings as errors.
*   Avoid naked `nolint` statements. Use `//nolint:lintername` for specific exclusions, and always include a comment explaining the exclusion reason.
    ```go
    //nolint:gosec // Replay attack risk is mitigated by token TTL
    func unsafeProcess() { ... }
    ```
*   Run `golangci-lint run` locally before pushing changes.
*   Use the `--fix` flag to automatically resolve formatting and other simple issues.

## Project Configuration

Maintain a `.golangci.yml` file in the project root so all developers and CI pipelines run the same linter rules.

