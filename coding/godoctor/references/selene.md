# Selene mutation testing guide

[Selene](https://github.com/danicat/selene) (`v0.4.0`) evaluates Go unit test suites by injecting AST syntax defects and verifying whether existing tests fail cleanly.

## Key features and safeguards

- **Zero-fallback binary execution**: Selene runs directly from `$PATH` or `.godoctor.yaml`. Dynamic `go run` fallbacks are banned to eliminate startup delays.
- **Targeted mode with TestQuery**: Reads `.godoctor/testquery.db` to run only tests covering each mutated line using `-run` filters.
- **In-memory compilation**: Uses Go's `-overlay` flag to compile mutated packages without writing defects to source files on disk.
- **Safety exclusions**: Skips mutations inside destructive system calls (`os.RemoveAll`, `exec.Command`, `syscall.*`) and their guards.
- **Worker pool and timebox**: Runs parallel workers (`-workers N`) with per-test (`-timeout`, default `10s`) and total suite (`-timebox`) limits.
- **Zero-kill detection**: Flags tests that execute without catching any mutant.

## Mutant status reference

| Status | Meaning | Action |
| :--- | :--- | :--- |
| `KILLED` | At least one test caught the mutation and failed. | None. Assertions caught the defect. |
| `SURVIVED` | All covering tests passed despite the mutated AST. | Add assertions covering that logic, return value, or boundary. |
| `UNCOVERED` | No test executed across the mutated line. | Add unit tests reaching this branch. |
| `TIMEOUT` | Mutation triggered an infinite loop or exceeded `-timeout`. | Treated as killed. |
| `EXCLUDED` | Mutation skipped by safety rules. | None. |

## Installation and environment verification

Verify installed tools using GoDoctor:

```bash
godoctor check
selene -version
```

Install or upgrade Selene via Go:

```bash
go install github.com/danicat/selene/cmd/selene@latest
```

## Configuration via `.godoctor.yaml`

Configure Selene parameters using `godoctor v0.34.0` keys (`binary_name` and `testquery_compat`):

```yaml
tools:
  selene:
    binary_name: "selene"
    recommended_version: "latest"
    pkg: "github.com/danicat/selene/cmd/selene@latest"
    packages: "./..."
    timeout: "3m"
    workers: 0                    # 0 defaults to runtime.GOMAXPROCS
    testquery_compat: true
    db_path: ".godoctor/testquery.db"
    disabled: false

features:
  testquery_compat: true
```

## Running Selene

### 1. Via GoDoctor CLI (recommended)

```bash
# Run mutation testing directly
godoctor call selene '{"dir": "/absolute/path/to/project"}'

# Run tests, coverage indexing, and mutation testing together
godoctor call test '{"dir": "/absolute/path/to/project", "level": "complete"}'
```

### 2. Standalone targeted run with TestQuery

Build coverage data first, then run Selene against `.godoctor/testquery.db` or `testquery.db` using single-dash Go flags:

```bash
tq build --output testquery.db ./...
selene -db testquery.db -workers 8 -v ./...
```

### 3. Timeboxed and JSON CI runs

```bash
# Limit total wall-clock budget for large suites
selene -db testquery.db -timebox 5m ./...

# JSON output for CI pipelines
selene -db testquery.db -json ./...

# Untargeted run without a database
selene -workers 8 ./...
```

## Querying results in `testquery.db`

Selene (`v0.4.0`) writes mutant records to `selene` (lowercase statuses `'killed'`, `'survived'`, `'uncovered'`, `'timeout'`, `'excluded'`), kill edges to `selene_kills`, and per-test summaries to `selene_tests`, plus four helper views:

### 1. Surviving mutants (assertion gaps)

```sql
SELECT id, mutator, package, function_name, file, line, col
FROM selene_survived
ORDER BY file, line;
```

### 2. Breakdown by mutator

```sql
SELECT mutator,
       COUNT(*) AS total,
       SUM(CASE WHEN status = 'killed' THEN 1 ELSE 0 END) AS killed,
       SUM(CASE WHEN status = 'survived' THEN 1 ELSE 0 END) AS survived,
       SUM(CASE WHEN status = 'uncovered' THEN 1 ELSE 0 END) AS uncovered,
       SUM(CASE WHEN status = 'timeout' THEN 1 ELSE 0 END) AS timeouts
FROM selene
GROUP BY mutator
ORDER BY total DESC;
```

### 3. Zero-kill tests

```sql
SELECT test_name, package
FROM selene_zero_kill_tests;
```

### 4. Safety-excluded mutations

```sql
SELECT id, mutator, package, function_name, file, line, col, reason
FROM selene_excluded;
```

### 5. Mutation summary metrics

```sql
SELECT * FROM selene_summary;
```

### 6. Top 10 most effective tests

```sql
SELECT test_name, package, mutations_killed, killed_mutant_ids
FROM selene_tests
WHERE mutations_killed > 0
ORDER BY mutations_killed DESC
LIMIT 10;
```

## Zero-kill test remediation

A **zero-kill test** ran during mutation testing without failing on any mutant:

| Root Cause | Pattern | Remediation |
| :--- | :--- | :--- |
| **Shallow assertions** | Checks only `err == nil` or exit status `0`. | Assert stdout, stderr, return fields, or parsed payloads. |
| **Redundant subtest** | Covered already by a broader case. | Consolidate duplicate table entries or test distinct boundaries. |
| **Tautological check** | Trivial constructor or getter with zero logic branches. | Merge into behavior tests or drop redundant cases. |
| **Empty input guard** | Early-return smoke case. | Keep only when guarding a public invariant. |

## Fixing surviving mutants

When mutants survive, strengthen boundary, payload, and branch checks:

### 1. Boundary mutations (such as `>=` mutated to `>`)

Cover values below, at, and above every threshold:

```go
tests := []struct {
    name     string
    val      int
    expected bool
}{
    {name: "below threshold", val: 17, expected: false},
    {name: "at threshold", val: 18, expected: true},
    {name: "above threshold", val: 19, expected: true},
}
```

### 2. Return value mutations (such as `return token, nil` mutated to `return "", nil`)

Assert non-empty payloads and concrete fields rather than `err == nil` alone:

```go
res, err := GenerateToken("user123")
if err != nil {
    t.Fatalf("unexpected error: %v", err)
}
if res == "" {
    t.Errorf("expected non-empty token")
}
```

### 3. Inverted conditionals (`if ok` vs `if !ok`)

Exercise both `true` and `false` branches for every conditional check.

## Notes and best practices

- **Pick the right test tier**: Use `level: "fast"` for rapid edits and reserve `level: "complete"` or standalone `selene` runs for release audits.
- **Avoid concurrent test runs**: Selene runs `-workers N` child compilers; avoid parallel `go test` or `tq build` processes during mutation runs.
- **Green baseline first**: Fix failing unit tests before running mutation analysis.
- **Refresh coverage first**: Run `tq build` or `godoctor call test` before targeted `selene -db` runs so coverage indexes reflect current lines.
- **Absolute paths in GoDoctor**: Always pass an absolute `dir` path to `godoctor call selene`.
