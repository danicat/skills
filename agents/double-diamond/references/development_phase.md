# Double-Diamond Development Phase (Diamond 2: Solution Space)

The Development Phase implements the approved Technical Specification. It consists of two distinct steps: **Develop (Divergence)** and **Deliver (Convergence)**.

---

## 1. Step 1: Develop (Divergence)

### 1.1 Objective
Execute implementation tasks in parallel without coordination bottlenecks or file conflicts. The Coordinator assigns each developer subagent a strictly disjoint Work Package (WP) derived from the approved specification.

### 1.2 Disjoint File Partitioning Rules
To prevent concurrency collisions and race conditions:
* **Strict File Isolation:** Each developer subagent is assigned a distinct set of files or a unique package directory (e.g. Developer 1 modifies `internal/model/...`, Developer 2 implements `internal/service/...`).
* **Contract Adherence:** Developers must implement the exact function signatures, interfaces, and types defined in the specification.
* **Package-Scoped Testing:** Developers execute targeted, package-scoped unit tests (e.g. `go test ./internal/model/...`) rather than broad repository sweeps (`go test ./...`) to avoid false failures while peer subagents are actively editing adjacent modules.

### 1.3 Launching Developer Subagents
The Coordinator spawns developer subagents using `invoke_subagent` with the `self` subagent type (which inherits full tool access, file creation, editing, and terminal commands):

```json
{
  "Subagents": [
    {
      "TypeName": "self",
      "Role": "Backend Developer",
      "Prompt": "Implement Work Package 1 (Core Models) per Section 3 of SPECIFICATION.md. Target files: internal/model/types.go, internal/model/validation.go. Write comprehensive unit tests in internal/model/types_test.go. Verify with `go test ./internal/model/...` and report completion."
    },
    {
      "TypeName": "self",
      "Role": "Service Developer",
      "Prompt": "Implement Work Package 2 (Service Layer) per Section 3 of SPECIFICATION.md. Target files: internal/service/engine.go. Implement service business logic adhering to model contracts. Verify with `go test ./internal/service/...` and report completion."
    }
  ]
}
```

---

## 2. Step 2: Deliver (Convergence & Quality Gating)

### 2.1 Objective
Integrate all parallel deliverables, run comprehensive project-wide verification suites, and enforce delivery quality gates.

### 2.2 The Delivery Quality Gates
The Coordinator executes the convergence verification pipeline in sequence:

1. **Gate 1: Full Project Compilation**
   - Execute root build command (e.g. `go build ./...` or `npm run build`).
   - All modules must compile cleanly with 0 syntax or type errors.
2. **Gate 2: End-to-End Test Suite Execution**
   - Execute full test suite (e.g. `go test -v -race ./...` or `npm test`).
   - All unit, integration, and regression tests must pass with 0 failures.
3. **Gate 3: Static Analysis & Lint Verification**
   - Run project linters and formatters (e.g. `go vet ./...`, `golangci-lint run`, `npm run lint`).
   - Fix any style violations or unused imports.
4. **Gate 4: Specification Compliance Verification**
   - Cross-check the final codebase against all acceptance criteria listed in Section 4 of the Technical Specification Document.

---

## 3. Completion & User Handover

Once all delivery gates pass:
1. The Coordinator presents a clean summary of implemented work packages, modified files, and verification test logs.
2. Directs the user to the completed deliverables and invites final review.
