# Double-Diamond Development Phase (Diamond 2: Solution Space)

The Development Phase implements the approved Foundation Document. It consists of two distinct steps: **Develop (Divergence)** and **Deliver (Convergence)**.

---

## 1. Step 1: Develop (Divergence)

### 1.1 Objective
Execute creation tasks in parallel without coordination bottlenecks or write collisions. The Coordinator assigns each creator subagent a strictly disjoint Work Package (WP) derived from the approved Foundation Document.

### 1.2 Disjoint Partitioning Rules
To prevent concurrency collisions and race conditions:
* **Strict Context & File Isolation:** Each creator subagent is assigned a distinct set of files, article sections, or argument claims (e.g., Creator 1 writes `pkg/model/...` or `Chapters 1-2`, Creator 2 writes `pkg/service/...` or `Chapters 3-4`).
* **Contract Adherence:** Creators must adhere to the exact interfaces, data schemas, outlines, or narrative arcs defined in the Foundation Document.
* **Localized Verification:** Creators execute targeted, localized verification (e.g., package-scoped tests `go test ./internal/model/...`, or section citation checks) rather than broad project-wide sweeps while peer subagents are actively authoring adjacent modules.

### 1.3 Launching Creator Subagents
The Coordinator spawns creator subagents using `invoke_subagent` with the `self` subagent type (which inherits full tool and write access):

```json
{
  "Subagents": [
    {
      "TypeName": "self",
      "Role": "Module Developer / Section Author",
      "Prompt": "Implement Work Package 1 (Core Foundation) per Section 3 of the Foundation Document. Target files/sections: [Files or Chapter Path]. Implement contracts, write comprehensive localized tests/checks, and report completion."
    },
    {
      "TypeName": "self",
      "Role": "Service Developer / Section Author",
      "Prompt": "Implement Work Package 2 (Service Layer / Body) per Section 3 of the Foundation Document. Target files/sections: [Files or Chapter Path]. Adhere strictly to Foundation contracts, run localized checks, and report completion."
    }
  ]
}
```

---

## 2. Step 2: Deliver (Convergence & Quality Gating)

### 2.1 Objective
Integrate all parallel deliverables into a single cohesive artifact, execute end-to-end verification suites, and enforce delivery quality gates.

### 2.2 The 4 Delivery Quality Gates
The Coordinator executes the convergence verification pipeline in sequence:

1. **Gate 1: Structural & Syntactic Integrity**
   - *Software*: Full root compilation (`go build ./...`, `npm run build`) with 0 syntax or type errors.
   - *Writing/Legal*: Markdown and document formatting valid with 0 broken anchors or broken links.
2. **Gate 2: Verification & Test Execution**
   - *Software*: Full automated test suite passes with 0 failures (`go test -v -race ./...`, `pytest`).
   - *Writing/Legal*: All empirical claims, statistical data, and legal precedents verified against primary sources.
3. **Gate 3: Quality, Style & Consistency Audit**
   - *Software*: Linters and formatters clean (`go vet`, `golangci-lint`, `npm run lint`).
   - *Writing/Legal*: Prose reviewed for narrative voice consistency, readability (Fog Index), and grammar.
4. **Gate 4: Foundation Document Compliance**
   - Cross-check the final deliverable against all acceptance criteria listed in Section 4 of the Foundation Document.

---

## 3. Failure Recovery Protocol & User Handover

If any gate fails during convergence:
1. **Isolate**: Identify the specific failing test, broken link, or contradictory section.
2. **Targeted Fix**: Spawn a single repair subagent or fix directly using the exact error log and contract specification.
3. **Re-Verify**: Re-run the full 4-gate verification suite until 100% pass.
4. **Handover**: Present a concise summary of deliverables, modified assets, and verification results to the user.
