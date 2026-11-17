---
name: godoctor
description: >
  Developer tooling and architectural safety rules for Go. Orchestrates
  high-level Go toolchain and static analysis utilities (gofmt, goimports,
  go vet, modernize, golangci-lint, deadcode), guards edits with compiler
  rollback gates, eliminates blind spots via Selene mutation testing, and
  enables fast test and coverage analytics with TestQuery SQLite queries.
  Activate when writing or refactoring Go code, fixing compilation or test
  failures, auditing test thoroughness, or enforcing idiomatic Go standards.
license: Apache-2.0
metadata:
  category: coding
  tags: "go, golang, testing, linting, mutation, refactoring"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Go developer tooling: GoDoctor

GoDoctor is a high-level Go workflow orchestrator that coordinates standard Go toolchain binaries and static analysis utilities. It provides guarded code edits, automated build and lint pipelines, mutation testing, and SQLite test analytics both as a CLI (`godoctor`) and as an MCP server (`godoctor mcp`).

## Go coding and architectural standards

### Google Go style and idiomatic practices

- **Standard toolchain enforcement**: Format all code with `gofmt`, organize imports with `goimports`, check with `go vet`, and lint with `golangci-lint`.
- **Naming conventions**:
  - Avoid repeating package names in exported types or functions (no stuttering). Use `user.Service` instead of `user.UserService`, `http.Server` instead of `http.HttpServer`, and `config.Load` instead of `config.LoadConfig`.
  - Use camelCase for unexported identifiers and PascalCase for exported identifiers. Keep acronyms uniform in case (for example, `JSONURL`, `dbID`, `xmlHTTP`).
- **Error handling**:
  - Return errors as the last return value.
  - Wrap errors with descriptive details using `fmt.Errorf("action description: %w", err)`.
  - Return explicit errors instead of panicking in libraries or business logic.

### Package architecture and layout

- **Flat package structure**: Prefer flat package layouts over deep enterprise layers (such as `adapters/`, `ports/`, `entities/`, `controllers/`, `repositories/`, `services/`, `usecases/`). Keep code flat at the root or grouped logically by domain.
- **Private vs. public API**: Use `internal/` for private packages that external modules must not import. Avoid `pkg/` outside Kubernetes-style libraries.
- **Test fixtures and golden files**: Store test fixtures, golden files, mock datasets, and external test inputs in `testdata/` folders, which the Go toolchain ignores during normal builds.
- **Focused source files**: Split package logic into clear files named after their primary role (such as `server.go`, `handler.go`, `config.go`, `types.go`).
- **No generic catch-all packages**: Never create generic `util`, `shared`, `common`, or `helpers` packages. Keep helpers in domain-specific packages or close to their callers.

### API design and HTTP architecture

- **Interface segregation**: Keep interfaces small and consumer-defined (accept interfaces, return structs). Avoid premature interfaces with one implementation; expose concrete types from producer packages.
- **HTTP service design**: Follow standard Go HTTP server patterns:
  - Constructor-based dependency injection (such as `NewServer(cfg, logger)`).
  - Route registration and handlers grouped on a single server struct.
  - Explicit HTTP middleware for cross-cutting concerns (logging, auth, tracing).

## Tool selection matrix

| Task / Goal | CLI Command (`godoctor call`) | MCP Tool Name | Behavior / Safeguards |
| :--- | :--- | :--- | :--- |
| **Guarded code edits** | `godoctor call edit` | `smart_edit` | Whitespace-insensitive fuzzy matching, `goimports` formatting, atomic write, and `go vet` rollback gate. |
| **Build and lint pipeline** | `godoctor call build` | `smart_build` | Orchestrates `go mod tidy`, `modernize -fix`, `gofmt`, `go build`, `go test`, `golangci-lint`, and `deadcode`. |
| **Test and benchmark runner** | `godoctor call test` | `smart_test` | Multi-tier runner (`fast`, `basic`, `benchmark`, `complete`) orchestrating `go test`, coverage, `tq`, and `selene`. |
| **Package and symbol docs** | `godoctor call docs` | `read_docs` | Inspects package docs, exported symbols, types, and examples via `go list` and `go/doc`. |
| **Mutation testing** | `godoctor call selene` | `selene` | Runs `selene` with parallel workers and `testquery.db` targeting. See [references/selene.md](references/selene.md). |
| **SQL test analytics** | `godoctor call tq` | `test_query` | Runs SQLite queries via TestQuery (`tq`) against `.godoctor/testquery.db`. See [references/testquery.md](references/testquery.md). |

### Test runner tiers (`smart_test` / `godoctor call test`)

- `level: "fast"`: Sub-second inner-loop execution. Runs `go test -v` directly without coverage profiling or `testquery.db` sync.
- `level: "basic"` (default): Standard tier. Runs unit tests with coverage profiling (`go tool cover -func`) and updates `.godoctor/testquery.db` via `tq`.
- `level: "benchmark"`: Runs Go benchmark suites (`go test -bench=<pattern> -benchmem -run=NONE`) and prints throughput and allocations in a Markdown table.
- `level: "complete"`: Release quality gate. Runs `basic` tests, coverage indexing, and multi-worker `selene` mutation testing across packages.

## Core safeguards

- **Zero-fallback policy**: Pre-install external binaries (`golangci-lint`, `modernize`, `deadcode`, `selene`, `tq` / `testquery`) on `$PATH` or configure them in `.godoctor.yaml`. GoDoctor bans on-demand `go run` compilation to avoid 1.5 to 4.5 seconds of startup latency and guarantee repeatable builds.
- **Tool version tracking**: `godoctor check` compares installed tool versions against recommended baselines and prints non-blocking upgrade hints.
- **Absolute paths required**: Always pass absolute paths for `dir` and `filename` parameters (for example, `/path/to/project`).
- **Atomic edit transactions**: `edit` (`smart_edit`) locates target blocks with whitespace-insensitive Levenshtein matching, runs `goimports`, writes a temp file before atomic rename, runs `go vet ./...`, and rolls back automatically with spelling hints if checks fail.
- **Resource limits**: Full mutation runs (`level: "complete"` or `selene`) saturate CPU cores. Never run concurrent test or build commands alongside mutation testing to prevent CPU contention and SQLite lock waits.
- **Configuration precedence**: Subsystems resolve settings in strict order:

$$\text{Per-Call Payload (JSON)} \succ \text{Config File } (\texttt{.godoctor.yaml}) \succ \text{Built-in Defaults}$$

## Environment diagnostics

Inspect installed binaries, versions (tested with Go `1.27.0`, `golangci-lint v2.13.2`, `selene v0.4.0`, and `tq v0.3.0`), and SafeShell status:

```bash
# Formatted diagnostic table
godoctor check

# Machine-readable JSON output
godoctor check --json
```

## Centralized configuration

Generate a full `.godoctor.yaml` configuration file (verified against `godoctor v0.34.0`):

```bash
godoctor init
```

Key configuration sections in `.godoctor.yaml`:

```yaml
version: "1"

# CLI global execution settings
cli:
  timeout: "60s"
  output_format: "text"           # "text" | "json" | "yaml"
  color: true
  log_level: "info"               # "debug" | "info" | "warn" | "error"

# MCP server settings
server:
  name: "godoctor"
  transport: "stdio"              # "stdio" | "http"
  http:
    listen: ":8080"
    read_timeout: "30s"
    write_timeout: "5m"
    allowed_origins:
      - "http://localhost"
      - "http://localhost:*"
      - "http://127.0.0.1"
      - "http://127.0.0.1:*"

# External tools and version management
tools:
  golangci_lint:
    binary_name: "golangci-lint"
    recommended_version: "v2.12.2"
    min_version: "v1.60.0"
    pkg: "github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.12.2"
    config: ".golangci.yml"
  modernize:
    binary_name: "modernize"
    recommended_version: "latest"
    pkg: "golang.org/x/tools/go/analysis/passes/modernize/cmd/modernize@latest"
  deadcode:
    binary_name: "deadcode"
    recommended_version: "latest"
    pkg: "golang.org/x/tools/cmd/deadcode@latest"
  selene:
    binary_name: "selene"
    recommended_version: "latest"
    pkg: "github.com/danicat/selene/cmd/selene@latest"
    packages: "./..."
    timeout: "3m"
    workers: 0                    # 0 defaults to runtime.GOMAXPROCS
    testquery_compat: true
    db_path: ".godoctor/testquery.db"
  testquery:
    binary_name: "testquery"
    recommended_version: "latest"
    pkg: "github.com/danicat/testquery@latest"
    db_path: ".godoctor/testquery.db"
    format: "table"
    timeout: "2m"

# Subsystem flags and behavior
features:
  autofix: true
  deadcode_check: true
  vet_gate: true
  auto_rollback: true
  testquery_sync: true
  testquery_compat: true
  version_check_hints: true
```

Note: `godoctor init` specifies `v2.12.2` as the baseline `recommended_version` for `golangci_lint`; newer versions such as `v2.13.2` for Go `1.27+` pass `godoctor check` cleanly.

## Installation and surface setup

### Installing GoDoctor CLI

```bash
go install github.com/danicat/godoctor/cmd/godoctor@latest
```

### Managing MCP and skill surfaces (`godoctor install` / `uninstall`)

```bash
# Configure MCP and unpack embedded skills globally (default: ~/.gemini/config)
godoctor install

# Configure in workspace scope (.agents/)
godoctor install -w

# Install only one surface
godoctor install --mcp        # MCP server registration only
godoctor install --skills     # Unpack embedded skills only

# Clean removal
godoctor uninstall
godoctor uninstall -w
```

## Direct CLI invocation examples

### 1. `edit`: guarded fuzzy edits with `goimports` and compiler rollback

```bash
godoctor call edit '{"filename": "/absolute/path/to/main.go", "old_content": "fmt.Println(\"old\")", "new_content": "fmt.Println(\"new\")"}'
```

### 2. `build`: compile, test, modernize, and lint pipeline

```bash
# Standard workspace pipeline
godoctor call build '{"dir": "/absolute/path/to/project"}'

# Build with a binary output target
godoctor call build '{"dir": "/absolute/path/to/project", "packages": "./cmd/godoctor", "output": "bin/godoctor"}'
```

### 3. `test`: multi-tier test runner

```bash
# Levels: fast, basic, benchmark, complete
godoctor call test '{"dir": "/absolute/path/to/project", "level": "basic"}'
```

### 4. `docs`: package and symbol documentation via `go/doc`

```bash
godoctor call docs '{"import_path": "net/http", "symbol_name": "Client"}'
```

### 5. `selene`: mutation testing

```bash
godoctor call selene '{"dir": "/absolute/path/to/project"}'
```

### 6. `tq`: SQL test and coverage analytics

```bash
godoctor call tq '{"dir": "/absolute/path/to/project", "query": "SELECT package, test, elapsed FROM failed_tests"}'
```

## Detailed references

- **TestQuery SQL analytics and schema**: [references/testquery.md](references/testquery.md) covers `tq v0.3.0` core tables (`all_tests`, `all_coverage`, `test_coverage`, `all_code`, `metadata`), all 10 built-in views, Offline and Live CLI modes, `tq explain`, and SQL recipes.
- **Selene mutation testing guide**: [references/selene.md](references/selene.md) covers AST mutation operators, mutant states (`KILLED`, `SURVIVED`, `UNCOVERED`), `.godoctor.yaml` settings, and surviving mutant fixes.
