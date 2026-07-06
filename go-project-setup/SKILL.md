---
name: go-project-setup
description: >
  Standardized setup for new Go (Golang) projects and services. Activate to ensure clean, idiomatic project structures (Standard Layout) and implement production-ready patterns (graceful shutdown, package separation) from day one.
---

# Go Project Setup

Create clean, idiomatic Go project structures.

## Core Mandates
1.  **Standard Layout**: Use the official Go layout (`cmd/`, `internal/`). Never create a `pkg/` directory.
2.  **Flat by Default**: Start with a flat structure (files in root) for simple apps. Introduce `cmd/` and `internal/` only when needed for private packages or multiple binaries.
3.  **Modern Go**: Set `go.mod` to the latest stable Go version (currently 1.24+).

## Workflow

### 1. Scope
Ask the user if this is a simple tool, a library, or a multi-service repository.

### 2. Choose Template
Read and use the templates in the `assets/` directory to establish patterns like graceful shutdown, `run` functions, and package separation.

*   **Simple CLI**: `assets/cli-simple`. Flat structure.
*   **Cobra CLI**: `assets/cli-cobra`. For complex CLI tools.
*   **Library**: `assets/library`. Package in root, `internal/` for hidden logic.
*   **Service**: `assets/webservice`. Entry point in `cmd/app-name/main.go` using a run function, private logic in `internal/`.
*   **MCP Server**: `assets/mcp-server`.
*   **Game**: `assets/game`. Uses Ebitengine.

### 3. Initialize
1.  **Create Directory**: `mkdir my-app`
2.  **Init Module**: `go mod init github.com/user/my-app`
3.  **Linting**: (Optional) Initialize `.golangci.yml` if style enforcement is required.
4.  **Apply Template**: Copy files from the template and update module names.
5.  **Verify**: Run `go mod tidy` and `go build ./...`.

## References
*   `references/project_layout.md`: Official Go Module Layout guide.
