# Advanced Testing Patterns

Beyond simple unit tests, sophisticated Go projects rely on advanced verification strategies.

## Fuzz Testing
Use the native `testing.F` to find edge cases in parsers and complex logic.

```go
func FuzzParser(f *testing.F) {
    f.Add("initial seed")
    f.Fuzz(func(t *testing.T, input string) {
        // 1. Run target
        parsed, err := Parse(input)
        if err != nil {
            return // Expected error
        }
        // 2. Validate invariants
        if parsed.String() != input {
            t.Errorf("Roundtrip failed: %q != %q", parsed.String(), input)
        }
    })
}
```

## Benchmarking
Measure performance and allocations.

```go
func BenchmarkProcess(b *testing.B) {
    data := generateData()
    b.ResetTimer() // Don't count setup
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```
*Run with:* `go test -bench=. -benchmem`

## Golden Files
For complex outputs (JSON, large structs), use "Golden Files" to compare against a saved expected version.

1.  Write output to a file `testdata/name.golden` if `update` flag is set.
2.  Otherwise, read `testdata/name.golden` and compare with actual output.

## Subprocess Mocking
To mock `exec.Command`, use the "Helper Process" pattern.

```go
func TestShell(t *testing.T) {
    if os.Getenv("GO_WANT_HELPER_PROCESS") == "1" {
        fmt.Fprint(os.Stdout, "mock stdout")
        os.Exit(0)
    }
    // Set cmd.Env to trigger the helper
}
```

## Tooling Ecosystem

### Mutation Testing: Selene
Use [Selene](https://github.com/danicat/selene) to verify test quality by introducing artificial bugs (mutants) and checking if tests fail.
*   **Goal:** Ensure tests actually catch regressions.
*   **Usage:** Run against critical logic packages.

### Test Exploration: TestQuery
Use [TestQuery](https://github.com/danicat/testquery) to analyze and filter test execution.
*   **Goal:** Efficiently run specific test subsets or understand complex test suites.
*   **Usage:** Query tests by name, package, or attributes.
