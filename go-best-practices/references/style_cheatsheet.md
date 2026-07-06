# Go Style Cheatsheet

Style rules derived from Go Code Review Comments.

## Error Handling

*   Format error strings using `fmt.Errorf("something failed")` in lowercase and with no trailing punctuation.
*   Indent error flow by handling errors first and returning early to avoid `else` blocks.
    ```go
    // Bad
    if err != nil { return err } else { doWork() }
    // Good
    if err != nil { return err }
    doWork()
    ```
*   Do not use in-band errors. Return `(value, ok)` or `(value, error)`, never `-1` or `nil` to signal an error.

## API Design

*   Pass contexts as the first parameter `ctx context.Context`. Do not store them in structs.
*   Use `crypto/rand` for cryptographic keys, never `math/rand`.
*   Avoid copying structs that contain a `sync.Mutex`. Pass them by pointer instead.
*   Define interfaces in the package where they are used (consumer), not where they are implemented.
*   Use short, consistent receiver names like `c` for `Client`. Do not use `this`, `self`, or `me`.
*   Pass small structs and `time.Time` by value. Use pointers only when mutating or when the struct is large.

## Philosophy and Concurrency

*   Share memory by communicating; do not communicate by sharing memory.
*   Use channels to orchestrate and mutexes to serialize.
*   Accept interfaces and return concrete structs.
*   Make zero values useful so structures like `sync.Mutex` are ready to use without explicit initialization.

## Testing

*   Use table-driven tests with anonymous structs: `tests := []struct{...}`.
*   Write clear test error messages showing what was received versus what was expected: `Errorf("F(%q) = %d; want %d", in, got, want)`.

## Imports

*   Group imports with standard library first, then third-party, and then local packages, separating each group with a blank line.
*   Avoid dot imports, except in `_test.go` files to resolve circular dependencies.

## Linting

*   Configure `golangci-lint` to run `staticcheck`, `errcheck`, and `unused` linters.
*   Use `//nolint:lintername` comments sparingly and always include a comment justifying the exclusion.
*   Ensure all linting checks pass before marking code as complete.

