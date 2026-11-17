# Double-Diamond development phase (Diamond 2: solution space)

The Development Phase implements the approved Foundation Document. It consists of two distinct steps: **Develop (Divergence)** and **Deliver (Convergence)**.

---

## 1. Step 1: Develop (divergence)

### 1.1 Objective
Execute creation tasks in parallel without coordination bottlenecks or write collisions. The Coordinator assigns each creator subagent a strictly disjoint Work Package (`WP`) derived from the approved Foundation Document, launches them concurrently, and ends its turn immediately.

### 1.2 Disjoint partitioning rules
To prevent concurrency collisions and race conditions:
* **Strict File and Section Ownership:** Each creator subagent owns a distinct set of files, article sections, or argument claims (such as Creator 1 writing `pkg/model/...` or `Chapters 1 to 2`, and Creator 2 writing `pkg/service/...` or `Chapters 3 to 4`).
* **Shared File Staging:** If multiple tracks must append to a shared file (such as an index, changelog, or configuration map), route worker outputs to isolated staging files (`staging/wp_*.md`) and merge them centrally during Deliver.
* **Contract Adherence:** Creators must adhere to the exact interfaces, data schemas, outlines, or narrative arcs defined in the Foundation Document.
* **Localized Verification:** Creators run targeted, localized verification (such as package-scoped tests `go test ./internal/model/...` or section citation checks) rather than broad project-wide sweeps while peer subagents are actively authoring adjacent modules.

### 1.3 Creator subagent briefing template

Dispatch parallel write-enabled creator subagents with strict file ownership and localized checks:

```markdown
Role: Work Package Author (WP-[N])
Assignment: Implement Work Package [N] per Section 3 of the Foundation Document.
Exclusive Target Files / Sections: [Explicit paths or chapter slices]
Off-Limits Paths: All files outside your assigned Work Package (route any shared updates to staging/wp_[N].md).
Contract Alignment: Follow Section 2 schemas, interfaces, and tone rules verbatim.
Localized Verification: Run [scoped test / lint / citation command] on your target slice.
Return: Completion status, modified file list, and exact verification output.
```

---

## 2. Step 2: Deliver (convergence and quality gating)

### 2.1 Objective
Integrate all parallel deliverables into a single cohesive artifact, execute end-to-end verification suites, and enforce delivery quality gates.

### 2.2 The 4 delivery quality gates
The Coordinator executes the convergence verification pipeline in sequence:

1. **Gate 1: Structural and Syntactic Integrity**
   - *Software:* Full root compilation (`go build ./...`, `npm run build`) with 0 syntax or type errors.
   - *Writing/Legal:* Markdown and document formatting valid with 0 broken anchors or broken links.
2. **Gate 2: Verification and Test Execution**
   - *Software:* Full automated test suite passes with 0 failures (`go test -v -race ./...`, `pytest`).
   - *Writing/Legal:* All empirical claims, statistical data, and legal precedents verified against primary sources.
3. **Gate 3: Quality, Style, and Consistency Audit**
   - *Software:* Linters and formatters clean (`go vet`, `golangci-lint`, `npm run lint`).
   - *Writing/Legal:* Prose reviewed for narrative voice consistency, readability (Fog Index), and grammar.
4. **Gate 4: Foundation Document Compliance**
   - Cross-check the final deliverable against all acceptance criteria listed in Section 4 of the Foundation Document.

---

## 3. Failure recovery protocol and user handover

If any gate fails during convergence:
1. **Isolate:** Identify the specific failing test, broken link, or contradictory section.
2. **Targeted Fix:** Spawn a single repair subagent or fix directly using the exact error log and contract specification.
3. **Re-Verify:** Re-run the full 4-gate verification suite until 100% pass.
4. **Handover:** Present a concise summary of deliverables, modified assets, and verification results to the user.
