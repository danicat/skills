---
name: double-diamond
description: >
  Use this skill when executing complex engineering initiatives, architectural overhauls, high-ambiguity technical spikes, or full-stack features using the Agile Double-Diamond methodology (Discover -> Define -> Develop -> Deliver). Orchestrates two distinct phases: Diamond 1 (Problem Space: parallel research subagents discover constraints, coordinator converges on a formal Technical Specification, followed by an interactive User Steering Gate) and Diamond 2 (Solution Space: parallel developer subagents implement disjoint work packages, coordinator converges via end-to-end compiler verification and delivery quality gates). Configurable Degree of Parallelism (DOP) and agent budget. Trigger on any mention of "double-diamond", "double diamond", "two-phase swarm", or when the user requests an explicit research-then-implement workflow. Do NOT use for simple single-file edits or isolated bug fixes.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
---

# Double-Diamond Multi-Agent Orchestration

The `double-diamond` skill coordinates complex software engineering initiatives through the proven **Double Diamond** agile and design framework, separating problem space discovery from solution space implementation.

```
          DIAMOND 1: PROBLEM SPACE                  DIAMOND 2: SOLUTION SPACE
          (Research & Exploration)                   (Implementation & Gating)

         /--- Discovery (Diverge) ---\             /--- Development (Diverge) ---\
        /  Parallel `research` sub-   \           /   Parallel developer sub-     \
       /   agents explore codebase,    \         /    agents implement disjoint    \
Start >    APIs, dependencies & spikes  > Spec  >     modules in parallel           > Delivery
       \                               /  Gate   \                                 /  (Gates)
        \---  Definition (Converge) --/           \---   Delivery (Converge)  ----/
             Synthesize findings into                  End-to-end compiler verification,
             a Technical Specification                 test integration & quality gates
```

---

## ⚡ Core Principles & Operational Rules

1. **Two Distinct Phases (Problem Space vs Solution Space):**
   - **Diamond 1 (Problem Space):** Focuses exclusively on reconnaissance, constraint identification, dependency analysis, and technical specification. No implementation code is written during Diamond 1.
   - **Diamond 2 (Solution Space):** Focuses on parallel component implementation against the approved specification, followed by rigorous integration gating.
2. **Mandatory User Steering Gate (Human-in-the-Loop Alignment):**
   - Between Diamond 1 and Diamond 2, the Coordinator halts to present the Technical Specification and architectural trade-offs to the user.
   - Requires explicit user review and confirmation before launching developer agents into the solution space.
3. **Explicit Scope & Deliverable Modality:**
   - During Diamond 1, explicitly establish the nature and boundaries of the deliverable (e.g., application code, library, declarative configuration, documentation, or architecture design) rather than making assumptions.
4. **Disjoint Work Package Allocation (Zero Merge Conflicts):**
   - In Diamond 2 (Development), every parallel developer subagent is assigned a mutually exclusive set of files or package directories. Parallel agents must never write to the same files concurrently.
5. **Quality Delivery Gating:**
   - Implementation is not complete until all delivery gates pass: Full Project Compilation, Automated Test Suite, Static Analysis/Linting, and Specification Compliance.
6. **Configurable Degree of Parallelism (DOP):**
   - The user may specify a total agent budget or a Degree of Parallelism (`DOP`).
   - If unspecified, default to $\text{DOP} = 4$ for Research ($N=4$) and $\text{DOP} = 4$ for Development ($M=4$).

---

## 🧭 The 5-Step Double-Diamond Workflow

### 1. Step 1: Discover (Diamond 1 Divergence)
* Coordinator analyzes requirements and decomposes the problem space into 2 to 4 orthogonal research vectors (e.g., Codebase reconnaissance, API/SDK patterns, performance constraints, failure modes).
* Spawns $N$ parallel `research` subagents (read-only, fast exploration).
* **Reference Guide:** Read [`references/research_phase.md`](references/research_phase.md) when partitioning research vectors and formulating prompts for `research` subagents.

### 2. Step 2: Define (Diamond 1 Convergence)
* Coordinator synthesizes all research reports into a unified **Technical Specification Document**.
* Establishes system contracts, interfaces, data schemas, error recovery strategies, and work package breakdowns.
* **Specification Template:** Populate [`assets/specification_template.md`](assets/specification_template.md) with research findings, architecture decisions, and disjoint work allocations.

### 3. Step 3: User Steering Gate (Interactive Alignment)
* Coordinator presents the executive summary, specification document, and architectural trade-offs to the user.
* Solicits user feedback, resolves design forks, and obtains explicit confirmation before proceeding to development.

### 4. Step 4: Develop (Diamond 2 Divergence)
* Coordinator spawns $M$ parallel developer subagents (`self` subagents with write & tool access).
* Each developer receives a strictly disjoint Work Package (WP) with targeted package unit tests.
* **Reference Guide:** Read [`references/development_phase.md`](references/development_phase.md) when defining disjoint work packages and launching developer subagents.

### 5. Step 5: Deliver (Diamond 2 Convergence)
* Coordinator consolidates deliverables, runs root-level compilation and test suites, and verifies against all specification criteria.
* Delivers finished, verified solution to the user.

---

## ⚠️ Common Gotchas & Antipatterns

1. **Premature Implementation in Diamond 1:** Never write production code during the discovery and definition phase. Diamond 1 is strictly for reconnaissance, spike exploration, constraint mapping, and interface contract design.
2. **Bypassing the User Steering Gate:** Never transition directly from specification writing into developer spawning without presenting the specification and trade-offs to the user for explicit confirmation.
3. **Overlapping File Allocations:** Never assign two parallel developer agents to the same file or overlapping directory. Work Packages MUST be strictly disjoint to avoid merge conflicts and race conditions.
4. **Broad Root Test Execution during Development:** Developer agents must execute fine-grained, package-scoped unit tests (`go test ./internal/pkg/...` or `npm test -- path/to/test.ts`) rather than full repository sweeps (`go test ./...`), preventing false test failures while sibling agents are midway through edits.
5. **Passive Polling Loops:** Coordinator agents should never poll subagent statuses in a tight loop; leverage the messaging system's automatic reactive wakeup upon subagent task completion.

---

## 📚 Progressive Disclosure & References

- **Research Phase Guide**: [`references/research_phase.md`](references/research_phase.md) — Exploration vectors, research prompt templates, and synthesis rules.
- **Development Phase Guide**: [`references/development_phase.md`](references/development_phase.md) — Disjoint partitioning, developer prompt templates, and delivery gating.
- **Specification Template**: [`assets/specification_template.md`](assets/specification_template.md) — Standardized markdown template for the consolidated specification document.
- **Evaluation Suite**: [`evals/evals.json`](evals/evals.json) — Trigger benchmarks and scenario validation test cases.
