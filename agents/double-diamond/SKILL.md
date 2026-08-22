---
name: double-diamond
description: >
  Universal multi-agent orchestration workflow based on the Double Diamond
  framework (Inception -> Discovery -> Definition -> Development -> Delivery).
  Coordinates parallel subagents with context isolation to separate problem-space
  research from solution-space implementation. Activate for complex, high-ambiguity
  initiatives across software engineering, in-depth research, long-form writing,
  legal analysis, or product strategy requiring structured human alignment gates.
license: Apache-2.0
metadata:
  category: agents
  tags: "orchestration, workflow, research, planning, subagents, agile"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.2.0"
  canonical: https://skills.danicat.dev/agents/double-diamond/
---

# Double-Diamond Multi-Agent Orchestration

The `double-diamond` skill coordinates complex, high-ambiguity initiatives through the proven **Double Diamond** framework, preceded by an **Inception** alignment phase. It leverages **parallel subagents with context isolation** to thoroughly explore the problem space before committing to solution-space implementation.

```
                              INCEPTION PHASE
                          (Pre-Diamond Alignment)
                         /grill-me User Interview
                      Establish Shared Understanding
                                     │
                                     ▼
          DIAMOND 1: PROBLEM SPACE                  DIAMOND 2: SOLUTION SPACE
          (Research & Exploration)                   (Creation & Verification)

         /--- Discovery (Diverge) ---\             /--- Development (Diverge) ---\
        /  Parallel `research` sub-   \           /   Parallel creation sub-      \
       /   agents explore landscape,   \         /    agents craft disjoint        \
Start >    constraints & prior art      > Brief >     sections/modules in parallel  > Delivery
       \                               /  Gate   \                                 /  (Gates)
        \---  Definition (Converge) --/           \---   Delivery (Converge)  ----/
             Synthesize findings into                  Holistic review, integration,
             a Foundation Document                     and quality gate verification
```

---

## 🌐 Universal Domain Mapping

Double Diamond adapts seamlessly across technical, creative, and analytical domains:

| Phase | Software Engineering | Writing & Publishing | Legal & Policy Research | Product & Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **0. Inception** | Stack, constraints, latency, scope | Audience, tone, thesis, length | Jurisdiction, case theory, facts | Market, user persona, success metrics |
| **1. Discover** *(Diverge)* | Codebase, APIs, edge cases | Background research, angles, data | Precedents, statutes, case law | Competitor analysis, customer interviews |
| **2. Define** *(Converge)* | Technical Specification | Structured Editorial Outline | Legal Brief / Argument Structure | PRD / Feature Specification |
| **Steering Gate** | Approve architecture & trade-offs | Approve thesis & outline | Approve legal theory & approach | Sign off on product direction |
| **3. Develop** *(Diverge)* | Parallel module implementation | Parallel chapter/section drafting | Parallel argument/motion drafting | Parallel prototype/stream exploration |
| **4. Deliver** *(Converge)* | Build, tests, lint, spec compliance | Fact-check, style, voice, flow | Citation audit, counter-arguments | Executive synthesis, launch readiness |

---

## ⚡ Core Principles & Operational Rules

1. **Pre-Diamond Inception (Alignment Gate):**
   - Before launching research divergence, the Coordinator executes an **Inception** phase via the `/grill-me` interactive interview protocol (using `ask_question`).
   - The Coordinator explores the existing environment/context first, then interviews the user about goals, constraints, non-negotiables, target audience, and deliverable modality.
2. **Two Distinct Diamond Phases (Problem Space vs. Solution Space):**
   - **Diamond 1 (Problem Space):** Focuses exclusively on reconnaissance, constraint mapping, dependency analysis, and definition. No final deliverable code or prose is authored during Diamond 1.
   - **Diamond 2 (Solution Space):** Focuses on parallel creation against the approved definition, followed by rigorous quality gating.
3. **Context Isolation via Subagents:**
   - Deep exploration and multi-track creation happen in isolated subagent contexts (`research` for read-only exploration, `self` for creation). This prevents context pollution and hallucination in the Coordinator's session.
4. **Mandatory User Steering Gate (Human-in-the-Loop Alignment):**
   - Between Diamond 1 and Diamond 2, the Coordinator halts to present the synthesized **Foundation Document** (Spec, Outline, Brief, or PRD) and trade-offs to the user for explicit review and confirmation.
5. **Disjoint Work Allocation (Zero Collision):**
   - In Diamond 2 (Development), parallel creator subagents receive strictly disjoint assignments (e.g., distinct source files, separate article sections, independent legal claims) to prevent overwrite collisions.
6. **Domain-Specific Delivery Quality Gates:**
   - Work is not delivered until all domain-specific quality gates pass: structural integrity, localized unit/section verification, holistic consistency, and compliance with the approved Foundation Document.

---

## 🎯 Agent Budget & Degree of Parallelism (DOP)

* **Definition**: **Agent Budget** is synonymous with **Degree of Parallelism (DOP)**. It defines the maximum number of **active, concurrent subagents** allowed to execute at the exact same time.
* **Active vs. Past Capacity**: Completed or terminated subagents do **not** consume budget. The budget applies strictly to currently running subagents. When a subagent completes its work, its concurrency slot is immediately freed.
* **Elastic Scaling**: While the baseline default is $\text{DOP} = 4$, the framework scales elastically to any user-requested budget (e.g., $\text{DOP} = 10, 20, 50+$) for massive parallel surveys, parameter sweeps, or multi-module initiatives.
* **High-DOP High-Signal Mandate (Micro-Probe Rule)**: When operating with elevated concurrency ($\text{DOP} \ge 8$), subagents must act as focused micro-probes. The Coordinator instructs subagents to return dense, high-signal, structured summaries ($\le 150$ words or tabular format) rather than verbose essays, enabling clean Map-Reduce synthesis without context dilution.

### Recommended Baseline Sizing:

| Initiative Scale | Agent Budget ($\text{DOP}$) | Active Discovery Workers | Active Creation Workers | Typical Scope |
| :--- | :---: | :---: | :---: | :--- |
| **Focused / Targeted** | **2** | **2** (Landscape + Standards) | **2** (Core + Surface) | Single module, short article, targeted feature |
| **Standard (Default)** | **4** | **4** (Landscape, Standards, Edge Cases, Comparative) | **4** (WPs 1–4 disjoint modules/sections) | Multi-module service, comprehensive whitepaper, PRD |
| **Complex / Deep** | **6–8+** | **6–8+** (Subsystem reconnaissance / micro-probes) | **6–8+** (Distributed package authors) | Full architectural rewrite, multi-chapter publication |
| **Massive Swarm** | **20–50+** | **20–50+** (Broad API surveys, micro-benchmarks, fuzzing) | **20–50+** (Massive parallel module/asset generation) | Wide ecosystem sweeps, multi-file migrations |

---

## 📡 Non-Blocking Coordinator & Reactive Concurrency

The Coordinator is the primary conversational interface and strategic conductor. It must remain **permanently unblocked** to respond to user messages at any point during execution.

1. **Role Separation (Delegation over Execution):**
   - The Coordinator orchestrates, synthesizes, and interfaces with the user. It **never** blocks itself with long, sequential manual execution—heavy exploration and drafting are delegated to subagents.
2. **Fire-and-Yield Concurrency:**
   - When the Coordinator spawns subagents via `invoke_subagent`, it **immediately halts tool calls to end its turn**. It never loops, sleeps, or polls.
3. **Always Unblocked for User Queries:**
   - Because the Coordinator never enters busy-wait polling loops, it is always available to process incoming user messages while subagents work in the background:
     - **Status Inquiries**: The Coordinator can immediately provide progress updates or inspect active workers via `manage_subagents (Action="list")`.
     - **In-Flight Steering / Scope Changes**: If the user provides new constraints or changes requirements mid-run, the Coordinator can steer active subagents via `send_message` or cancel/restart them via `manage_subagents (Action="kill")`.
4. **Automatic Reactive Wakeup:**
   - When subagents finish their tasks, the messaging platform automatically wakes up the Coordinator with their full results.

---

## 🧭 The 6-Step Double-Diamond Workflow

### 1. Step 0: Inception (Pre-Diamond Alignment)
* Coordinator activates the `/grill-me` protocol, systematically interviewing the user one decision node at a time via `ask_question`.
* Explores existing materials first, then clarifies scope boundaries, deliverable modality, non-negotiables, and user preferences.
* **Reference Guide:** Read [`references/inception_phase.md`](references/inception_phase.md) for interview patterns and decision-tree traversal.

### 2. Step 1: Discover (Diamond 1 Divergence)
* Coordinator decomposes the problem space into up to $\text{DOP}$ orthogonal exploration vectors (e.g., Landscape reconnaissance, Standards & APIs, Constraints & Failure modes, Prior art).
* Spawns parallel `research` subagents using `invoke_subagent` and immediately yields execution.
* **Reference Guide:** Read [`references/research_phase.md`](references/research_phase.md) for vector decomposition and prompt templates.

### 3. Step 2: Define (Diamond 1 Convergence)
* Coordinator synthesizes research reports into a unified **Foundation Document** (Technical Specification, Editorial Outline, Legal Brief, or PRD).
* Establishes system contracts, interfaces, chapter structure, or argument trees, alongside disjoint work package allocations.
* **Document Template:** Populate [`assets/specification_template.md`](assets/specification_template.md) with research synthesis and work breakdowns.

### 4. Step 3: User Steering Gate (Interactive Alignment)
* Coordinator presents the executive summary, draft Foundation Document, and architectural/editorial trade-offs to the user.
* Solicits user feedback, resolves decision forks, and obtains explicit confirmation before proceeding to creation.

### 5. Step 4: Develop (Diamond 2 Divergence)
* Coordinator spawns up to $\text{DOP}$ parallel creator subagents (`self` subagents with write & tool access) and immediately yields execution.
* Each creator receives a strictly disjoint Work Package (WP) and executes localized verification:
  - **Software**: Package-scoped unit tests (`go test ./internal/pkg/...`, `pytest tests/unit/`, `npm test -- src/pkg/`).
  - **Writing**: Section drafting against word count, tone, and source citations.
  - **Legal/Policy**: Argument drafting with case citations and statutory cross-referencing.
* **Reference Guide:** Read [`references/development_phase.md`](references/development_phase.md) for disjoint allocation and creator prompt templates.

### 6. Step 5: Deliver (Diamond 2 Convergence & Quality Gating)
* Coordinator integrates all parallel deliverables into a coherent whole and executes end-to-end verification.
* **Failure Recovery Protocol**: If any integration test, fact-check, or consistency check fails:
  1. Isolate the failing component and review specific error traces or discrepancies.
  2. Launch a targeted repair subagent with the exact context and interface contract.
  3. Re-verify all delivery gates until 100% pass before presenting the final deliverable to the user.

---

## ⚠️ Common Gotchas & Antipatterns

1. **Skipping Inception & Assuming User Intent:** Never jump straight into research divergence without establishing core scope boundaries, audience, and constraints with the user.
2. **Premature Implementation in Diamond 1:** Never author production code or final prose during the discovery and definition phase. Diamond 1 is strictly for reconnaissance, constraint mapping, and interface/outline design.
3. **Bypassing the User Steering Gate:** Never transition directly from definition into creation without presenting the foundation document and trade-offs to the user for explicit confirmation.
4. **Overlapping Work Allocations:** Never assign two parallel creator subagents to the same file, section, or deliverable slice. Work Packages MUST be strictly disjoint to prevent race conditions and merge conflicts.
5. **Broad Integration Sweeps during Creation:** Creator subagents must perform fine-grained, localized verification (e.g. package unit tests, section fact-checks) rather than whole-project sweeps while sibling subagents are midway through edits.
6. **Passive Polling Loops:** Coordinator agents must NEVER poll subagent statuses in a loop. Spawning subagents is fire-and-yield; rely on automatic reactive wakeup to keep the Coordinator responsive to the user.

---

## 📚 Progressive Disclosure & References

- **Inception Phase Guide**: [`references/inception_phase.md`](references/inception_phase.md) — Pre-diamond alignment, decision-tree traversal, and `/grill-me` protocol rules.
- **Research Phase Guide**: [`references/research_phase.md`](references/research_phase.md) — Exploration vectors, subagent prompt templates, and synthesis rules across domains.
- **Development Phase Reference**: [`references/development_phase.md`](references/development_phase.md) — Delivery execution, specialized workers, and non-blocking coordination.
- **Specification Template**: [`assets/specification_template.md`](assets/specification_template.md) — Structured specification template for the Define phase.
