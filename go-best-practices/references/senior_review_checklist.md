# Senior Go Review Checklist

Review criteria for code health.

## Interface Design

*   Check that interfaces are defined where they are consumed, not where they are implemented. Foundational libraries (like `io.Reader`) are exceptions.
*   Keep interfaces small, containing only 1-3 methods.

## Concurrency

*   Verify that every goroutine (`go func()`) has a clear lifecycle managed by a context or wait group.
*   Ensure structs containing a `sync.Mutex` are passed by pointer to avoid copying the lock.
*   Confirm that channels are closed by the sending goroutine, and that `select` blocks handle timeouts to prevent deadlocks.

## API Design

*   Ensure functions return concrete types or struct pointers (like `*Service`) rather than interface types. This allows consumers to define their own interfaces.
*   Check that complex constructors use configuration structs or functional options.

## Error Handling

*   Verify that error types are checked using `errors.Is` and `errors.As`.
*   Check that errors are wrapped with context using `fmt.Errorf("doing x: %w", err)`.

