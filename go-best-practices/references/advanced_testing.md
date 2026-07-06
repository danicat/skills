# Advanced Testing Patterns

Go testing strategies for complex verification needs.

## Fuzz Testing

Use native fuzzing `testing.F` to find edge cases in parsers and complex business logic.

```go
func FuzzParser(f *testing.F) {
    f.Add("initial seed")
    f.Fuzz(func(t *testing.T, input string) {
        parsed, err := Parse(input)
        if err != nil {
            return // Expected error
        }
        if parsed.String() != input {
            t.Errorf("Roundtrip failed: %q != %q", parsed.String(), input)
        }
    })
}
```

## Benchmarking

Measure performance metrics and memory allocations.

```go
func BenchmarkProcess(b *testing.B) {
    data := generateData()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        Process(data)
    }
}
```
Run benchmarks using: `go test -bench=. -benchmem`

## Golden Files

Use saved expected files (golden files) to verify complex outputs like large JSON structures.

1.  Write the actual output to `testdata/name.golden` when an update flag is supplied.
2.  Otherwise, read `testdata/name.golden` and compare it to the function output.

## Subprocess Mocking

To mock `exec.Command`, use a helper test process that is triggered via environment variables.

```go
func TestShell(t *testing.T) {
    if os.Getenv("GO_WANT_HELPER_PROCESS") == "1" {
        fmt.Fprint(os.Stdout, "mock stdout")
        os.Exit(0)
    }
}
```

## Verification Tooling

### Mutation Testing

Use [Selene](https://github.com/danicat/selene) to evaluate test coverage by injecting minor code faults (mutants) and verifying that tests fail. This confirms that test assertions are active. Run this tool on packages containing core application logic.

### Test Exploration

Use [TestQuery](https://github.com/danicat/testquery) to inspect and filter test execution. This helps identify and run specific subsets of large test suites by filtering on name, package, or attributes.

