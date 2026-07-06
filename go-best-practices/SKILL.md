---
name: go-best-practices
description: >
  Go development practices and style guidelines covering concurrency safety, package layout (avoiding pkg/), and PR review checklists.
---

# Go Best Practices

Guides layout design, package structures, and code reviews.

## Core Rules

*   **Architecture**: Do not use a `pkg/` directory. Keep package structures flat unless complexity requires nested packages. Put private logic in `internal/` and entrypoints in `cmd/`.
*   **Style**: Read `references/style_cheatsheet.md` before editing. Use `references/senior_review_checklist.md` for reviews. Prefer Go generics (`[T any]`) to `interface{}`.
*   **Concurrency**: Every goroutine needs a defined exit trigger via context or wait group. Use `errgroup` for parallel operations.

## Work Processes

### 1. Audit and Analysis

1.  Check the file layout. Suggest moving files out of `pkg/` if present.
2.  Review code structure against `style_cheatsheet.md`.
3.  Verify that errors are handled, contexts are passed first, and mutexes are not copied.

### 2. Refactoring

1.  Plan the structural changes, such as decoupling with interfaces.
2.  Apply edits incrementally.
3.  Run `go build ./...`, `go test ./...`, and `golangci-lint run` to verify changes.

### 3. Review

1.  Apply the checks in `senior_review_checklist.md`.
2.  Provide specific feedback with file references.

### 4. Special Domains

*   **HTTP**: Routing and middleware patterns are in `references/http_services.md`.
*   **Testing**: Benchmark, fuzz, and integration setups are in `references/advanced_testing.md`.
*   **Games**: Ebitengine patterns are in `references/ebitengine_docs.md`.
*   **Idioms**: General rules are in `references/go_proverbs.md`.
*   **Linting**: Configuration guidelines are in `references/linting.md`.

## Reference Files

*   `references/style_cheatsheet.md`: Critical style rules.
*   `references/senior_review_checklist.md`: Quality criteria for reviews.
*   `references/project_layout.md`: Standard module layout guide.
*   `references/architectural_decisions.md`: Template for ADRs.
*   `references/http_services.md`: HTTP service structure.
*   `references/advanced_testing.md`: Fuzzing and benchmarking.
*   `references/ebitengine_docs.md`: Game engine layout.
*   `references/go_proverbs.md`: Idiomatic Go proverbs.
*   `references/linting.md`: Linter rules and tools.
