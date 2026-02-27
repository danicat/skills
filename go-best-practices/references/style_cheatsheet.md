# Go Style Cheatsheet

Critical style rules derived from Go Code Review Comments.

## Error Handling
*   **Error Strings:** `fmt.Errorf("something failed")` (lowercase, no punctuation).
*   **Indent Error Flow:** Handle errors first and return. Avoid `else`.
    ```go
    // Bad
    if err != nil { return err } else { doWork() }
    // Good
    if err != nil { return err }
    doWork()
    ```
*   **In-Band Errors:** Return `(value, ok)` or `(value, error)`, never `-1` or `nil` to signal error.

## API Design
*   **Contexts:** First parameter `ctx context.Context`. Never store in structs.
*   **Crypto:** Use `crypto/rand`, never `math/rand` for keys.
*   **Copying:** Do not copy structs with `sync.Mutex`.
*   **Interfaces:** Define interfaces where they are *used* (consumer), not where implemented.
*   **Receiver Names:** Short (e.g., `c` for `Client`), consistent. No `this`, `self`, or `me`.
*   **Pass Values:** Pass small structs and `time.Time` by value. Only use pointers if mutating or struct is large.

## Philosophy & Concurrency
*   **Concurrency:** "Do not communicate by sharing memory; instead, share memory by communicating."
*   **Sync:** "Channels orchestrate; mutexes serialize."
*   **Abstraction:** "Accept interfaces, return structs." (Postel's Law applied to Go).
*   **Zero Values:** Make the zero value useful (e.g., `sync.Mutex` is ready to use).

## Testing
*   **Table-Driven:** Use `aa := []struct{...}` for tests.
*   **Error Messages:** `got != want`. `Errorf("F(%q) = %d; want %d", in, got, want)`.

## Imports
*   **Grouping:** Stdlib first, then 3rd party, then local. Separated by blank lines.
*   **Dot Imports:** Only in `_test.go` for circular dependencies.

## Linting
*   **Standard:** Use `golangci-lint` with `staticcheck`, `errcheck`, and `unused`.
*   **Exclusions:** Use `//nolint:lintername` sparingly and always justify with a comment.
*   **Verification:** Linting must pass before any code is considered "Done".
