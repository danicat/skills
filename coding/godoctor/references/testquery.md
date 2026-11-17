# TestQuery SQL test analytics guide

[TestQuery](https://github.com/danicat/testquery) (`tq`, verified against `v0.3.0`) indexes Go test execution logs and statement coverage into SQLite (`.godoctor/testquery.db` or `testquery.db`), allowing fast SQL queries over failures, slow tests, and uncovered branches.

## Key features and execution modes

- **Offline mode**: Build a persistent database once with `tq build` (or `godoctor call test`), then query repeatedly with `--db`.
- **Live mode**: Run tests and query results in memory in a single step using `--pkg ./...` (without `--db`).
- **Zero-fallback binary lookup**: GoDoctor runs `tq` or `testquery` directly from `$PATH` or `.godoctor.yaml` without slow dynamic `go run` compilation.
- **Concurrent SQLite WAL mode**: Multiple readers can query `.godoctor/testquery.db` while GoDoctor stores test results.
- **Unrestricted SQL queries**: SafeShell permits SQLite comparison operators (`<`, `>`, `<=`, `>=`), multiline queries, string concatenation (`||`), and semicolons.

## Database schema reference (`tq v0.3.0`)

All tables normalize `package` to the full Go module import path and `file` to the workspace-relative path.

### Core `tq` tables

| Table | Purpose | Columns |
| :--- | :--- | :--- |
| `all_tests` | Test outcomes, hierarchy, duration, and output (`PRIMARY KEY (package, test)`). | `time`, `action` (`'pass'`/`'fail'`), `status`, `package`, `test`, `parent_test`, `is_subtest`, `is_parent`, `elapsed`, `output` |
| `all_coverage` | Statement execution counts per basic block. | `package`, `file`, `start_line`, `start_col`, `end_line`, `end_col`, `stmt_num`, `count`, `function_name` |
| `test_coverage` | Leaf test-to-block mapping (populated when `--per-test-coverage` is enabled; `true` by default). | `test_package`, `test_name`, `package`, `file`, `start_line`, `start_col`, `end_line`, `end_col`, `stmt_num`, `count`, `function_name` |
| `all_code` | Indexed Go source lines for SQL joins. | `package`, `file`, `line_number`, `content` |
| `metadata` | Key-value build properties (`pkg`, `per_test_coverage`). | `key`, `value` |

> [!TIP]
> Parent table-driven tests (`t.Run`) appear in `all_tests` with `is_parent = 1`. Always filter `WHERE is_parent = 0` or query `leaf_tests` so parent containers are not double-counted alongside subtests.

### Selene extension tables

Populated when `selene -db` runs against the same SQLite database (see [references/selene.md](selene.md)):

| Table | Purpose | Columns |
| :--- | :--- | :--- |
| `selene` | AST mutant records and statuses (`'killed'`, `'survived'`, `'uncovered'`, `'timeout'`, `'excluded'`). | `id`, `mutator`, `file`, `package`, `function_name`, `line`, `col`, `status`, `killed_by` |
| `selene_kills` | Many-to-many link between killed mutants and catching tests. | `mutant_id`, `package`, `test_name` |
| `selene_tests` | Per-test kill totals across mutation runs. | `test_name`, `package`, `status`, `mutations_killed`, `killed_mutant_ids` |

### Built-in views

10 views built by `tq v0.3.0`:

- `leaf_tests`: All columns from `all_tests` with `is_parent = 0` (executable leaf tests and subtests only).
- `passed_tests`: Passing leaf tests (`package`, `test`, `elapsed`).
- `failed_tests`: Failing leaf tests (`package`, `test`, `elapsed`, `output`).
- `slow_tests`: Leaf tests ordered by `elapsed DESC` (`package`, `test`, `action`, `elapsed`).
- `test_summary`: Per-package counts (`leaf_tests`, `subtests`, `total_events`, `passed`, `failed`, `total_elapsed`).
- `missing_coverage`: Uncovered statement blocks (`package`, `function_name`, `file`, `start_line`, `start_col`, `end_line`, `end_col`).
- `code_coverage`: Non-test Go source lines joined with execution counts (`package`, `file`, `line_number`, `content`, `covered`).
- `file_coverage`: Per-file statement totals (`package`, `file`, `covered_stmts`, `total_stmts`, `coverage_pct`).
- `package_coverage`: Per-package statement totals (`package`, `covered_stmts`, `total_stmts`, `coverage_pct`).
- `uncovered_lines`: Distinct non-test source lines inside uncovered blocks (`package`, `file`, `line_number`, `content`, `function_name`).

4 additional views created by `selene -db`:

- `selene_survived`, `selene_zero_kill_tests`, `selene_summary`, and `selene_excluded`.

## Installation and environment verification

Verify binaries and versions through GoDoctor:

```bash
godoctor check
tq version
```

Install or upgrade the `tq` CLI via Go:

```bash
go install github.com/danicat/testquery@latest
```

## Configuration via `.godoctor.yaml`

Settings in `godoctor init` (`v0.34.0`) use `binary_name` and `db_path`:

```yaml
tools:
  testquery:
    binary_name: "testquery"
    recommended_version: "latest"
    pkg: "github.com/danicat/testquery@latest"
    db_path: ".godoctor/testquery.db"
    format: "table"
    timeout: "2m"
    disabled: false

testquery:
  db_path: ".godoctor/testquery.db"
  wal_mode: true
  busy_timeout: "5s"
  format: "table"

features:
  testquery_sync: true
  testquery_compat: true
```

## Querying test analytics

### 1. Via GoDoctor CLI (`godoctor call tq`)

Always supply an absolute directory path for `dir`:

```bash
godoctor call tq '{"dir": "/absolute/path/to/project", "query": "SELECT package, test, elapsed FROM failed_tests"}'
```

### 2. Via MCP (`test_query`)

```json
{
  "dir": "/absolute/path/to/project",
  "query": "SELECT package, test, elapsed FROM failed_tests;"
}
```

### 3. Direct `tq` CLI commands

```bash
# Offline mode: build once, then query fast
tq build --output .godoctor/testquery.db --pkg ./...
tq query "SELECT * FROM failed_tests" --db .godoctor/testquery.db
tq query "SELECT * FROM package_coverage ORDER BY coverage_pct ASC" --db .godoctor/testquery.db --format json

# Find all tests covering a specific file line
tq explain internal/auth/token.go:42 --db .godoctor/testquery.db

# Live mode: run tests and query in memory without writing a database file
tq query "SELECT * FROM slow_tests LIMIT 10" --pkg ./...

# Print the full built-in schema and example queries
tq schema
```

## Common SQL query recipes

### 1. Show recent test failures with full output

```sql
SELECT package, test, elapsed, output
FROM failed_tests
ORDER BY elapsed DESC;
```

### 2. Rank packages by lowest statement coverage

```sql
SELECT package, covered_stmts, total_stmts, coverage_pct
FROM package_coverage
ORDER BY coverage_pct ASC;
```

### 3. Find uncovered functions in a specific package

```sql
SELECT file, function_name, start_line, end_line, stmt_num
FROM all_coverage
WHERE count = 0 AND package LIKE '%auth%'
ORDER BY file, start_line;
```

### 4. List exact uncovered source lines

```sql
SELECT package, file, line_number, function_name, content
FROM uncovered_lines
ORDER BY file, line_number;
```

### 5. Find slowest leaf tests (`> 0.25s`)

```sql
SELECT package, test, elapsed
FROM slow_tests
WHERE action = 'pass' AND elapsed > 0.25
LIMIT 20;
```

### 6. Find tests exercising a specific file line

```sql
SELECT DISTINCT test_package, test_name
FROM test_coverage
WHERE file LIKE '%token.go'
  AND start_line <= 42 AND end_line >= 42
  AND count > 0
ORDER BY test_name;
```

## Notes and best practices

- **Automatic database updates**: `godoctor call test` (except `level: "fast"`) updates `.godoctor/testquery.db` automatically. If no database exists when calling `godoctor call tq`, GoDoctor builds it first.
- **Inspect leaf counts properly**: Use `leaf_tests`, `passed_tests`, `failed_tests`, `slow_tests`, or `test_summary` instead of raw `COUNT(*)` over `all_tests` so subtest parents (`is_parent = 1`) are excluded.
- **JSON escaping**: In SQLite, quote string literals with single quotes (`'...'`). Escape single quotes when wrapping queries in single-quoted bash arguments.
- **Avoid write contention**: WAL mode supports concurrent reads, but avoid running `godoctor call test` or `tq build` in parallel with `selene` mutation testing.
