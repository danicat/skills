---
name: double-diamond
description: >
  Universal multi-agent orchestration workflow based on the Double Diamond
  framework (Inception -> Discovery -> Definition -> Development -> Delivery).
  Coordinates parallel subagents with context isolation to separate
  problem-space research from solution-space implementation. Activate for
  complex, high-ambiguity initiatives across software engineering, in-depth
  research, long-form writing, legal analysis, or product strategy requiring
  structured human alignment gates.
license: Apache-2.0
metadata:
  category: workflows
  tags: "orchestration, research, planning, subagents, agile"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.3.0"
  catalog: https://skills.danicat.dev
---

# Double-Diamond multi-agent orchestration

The `double-diamond` skill coordinates complex, high-ambiguity initiatives through the **Double Diamond** framework, preceded by an **Inception** alignment phase. It uses **parallel subagents with context isolation** to explore the problem space thoroughly before committing to solution-space implementation.

```text
                              INCEPTION PHASE
                          (Pre-Diamond Alignment)
                    One-Decision-at-a-Time Interview
                      Establish Shared Understanding
                                     │
                                     ▼
          DIAMOND 1: PROBLEM SPACE                  DIAMOND 2: SOLUTION SPACE
          (Research & Exploration)                   (Creation & Verification)

         /--- Discovery (Diverge) ---\             /--- Development (Diverge) ---\
        /  Parallel read-only sub-    \           /   Parallel creator sub-       \
       /   agents explore landscape,   \         /    agents craft disjoint        \
Start >    constraints & prior art      > Brief >     sections/modules in parallel  > Delivery
       \                               /  Gate   \                                 /  (Gates)
        \---  Definition (Converge) --/           \---   Delivery (Converge)  ----/
             Synthesize findings into                  Holistic review, integration,
             a Foundation Document                     and quality gate verification
```

---

## Universal domain mapping

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

## Core principles and operational rules

1. **Pre-Diamond Inception (Alignment Gate):**
   - Before launching research divergence, the Coordinator runs an **Inception** phase using a one-decision-at-a-time interview.
   - Inspect the existing repository, local environment, or provided materials first so you never ask questions you can answer directly. Then ask one focused decision at a time with concise choices and a `(Recommended)` default about goals, constraints, non-negotiables, audience, and deliverable modality.
2. **Two Distinct Diamond Phases (Problem Space vs. Solution Space):**
   - **Diamond 1 (Problem Space):** Focuses exclusively on reconnaissance, constraint mapping, dependency analysis, and definition. Author no final deliverable code or prose during Diamond 1.
   - **Diamond 2 (Solution Space):** Focuses on parallel creation against the approved definition, followed by rigorous quality gating.
3. **Context Isolation via Subagents:**
   - Deep exploration and multi-track creation happen in isolated subagent contexts: read-only discovery subagents in Diamond 1 and write-enabled creator subagents in Diamond 2. This keeps noisy exploration logs out of the Coordinator session and enforces clean read-only versus write-enabled boundaries.
4. **Mandatory User Steering Gate (Human-in-the-Loop Alignment):**
   - Between Diamond 1 and Diamond 2, the Coordinator halts to present the synthesized **Foundation Document** (Spec, Outline, Brief, or PRD) and trade-offs to the user for explicit review and confirmation.
5. **Disjoint Work Allocation (Zero Collision):**
   - In Diamond 2 (Development), parallel creator subagents receive strictly disjoint assignments (such as distinct source files, separate article sections, or independent legal claims) to prevent overwrite collisions.
6. **Domain-Specific Delivery Quality Gates:**
   - Deliver work only after all domain-specific quality gates pass: structural integrity, localized unit or section verification, holistic consistency, and compliance with the approved Foundation Document.

---

## Agent budget and degree of parallelism (DOP)

* **Definition:** **Agent Budget** is synonymous with **Degree of Parallelism (`DOP`)**. It defines the maximum number of **active, concurrent subagents** allowed to run at the same time.
* **Active vs. Past Capacity:** Completed or terminated subagents do not consume budget. The budget applies strictly to currently running subagents. When a subagent finishes, its concurrency slot is freed.
* **Elastic Scaling:** While the baseline default is `DOP = 4`, the framework scales elastically to any user-requested budget (such as `DOP = 10`, `20`, or `50+`) for massive parallel surveys, parameter sweeps, or multi-module initiatives.
* **High-DOP High-Signal Mandate (Micro-Probe Rule):** When operating with elevated concurrency (`DOP >= 8`), subagents must act as focused micro-probes. Instruct each subagent to return a dense, high-signal, structured summary (at most 150 words or tabular format) rather than a verbose essay, enabling clean synthesis without flooding the Coordinator.

### Recommended baseline sizing

| Initiative Scale | Agent Budget (DOP) | Active Discovery Workers | Active Creation Workers | Typical Scope |
| :--- | :---: | :---: | :---: | :--- |
| **Focused / Targeted** | **2** | **2** (Landscape + Standards) | **2** (Core + Surface) | Single module, short article, targeted feature |
| **Standard (Default)** | **4** | **4** (Landscape, Standards, Edge Cases, Comparative) | **4** (WPs 1 to 4 disjoint modules/sections) | Multi-module service, comprehensive whitepaper, PRD |
| **Complex / Deep** | **6 to 8+** | **6 to 8+** (Subsystem reconnaissance / micro-probes) | **6 to 8+** (Distributed package authors) | Full architectural rewrite, multi-chapter publication |
| **Massive Swarm** | **20 to 50+** | **20 to 50+** (Broad API surveys, micro-benchmarks, fuzzing) | **20 to 50+** (Massive parallel module/asset generation) | Wide ecosystem sweeps, multi-file migrations |

---

## Non-blocking coordinator and reactive concurrency

The Coordinator is the primary conversational interface and strategic conductor. It stays unblocked so it can respond to user messages at any point during execution.

1. **Role Separation (Delegation over Execution):**
   - The Coordinator orchestrates, synthesizes, and communicates with the user. It never blocks itself with long, sequential manual work; heavy exploration and drafting go to subagents.
2. **Fire-and-Yield Concurrency:**
   - After dispatching parallel subagents, the Coordinator **ends its turn immediately** so results arrive asynchronously. It never sleeps, loops, or polls for worker status.
3. **Always Unblocked for User Queries:**
   - Because the Coordinator never enters polling loops, it stays available to process incoming user messages while subagents work in the background:
     - **Status inquiries:** Inspect active workers and report progress immediately.
     - **In-flight steering and scope changes:** Redirect running subagents or cancel and restart obsolete tasks when constraints change mid-run.
4. **Automatic Reactive Wakeup:**
   - When subagents finish their tasks, the runtime wakes up the Coordinator with their results.

---

## The 6-step Double-Diamond workflow

### 1. Step 0: Inception (Pre-Diamond Alignment)
* Coordinator runs an interactive interview, resolving one decision node at a time.
* Explores existing materials first, then clarifies scope boundaries, deliverable modality, non-negotiables, and user preferences.
* **Reference Guide:** Read [`references/inception_phase.md`](references/inception_phase.md) for interview patterns and decision-tree traversal.

### 2. Step 1: Discover (Diamond 1 Divergence)
* Coordinator decomposes the problem space into up to `DOP` orthogonal exploration vectors (such as Landscape reconnaissance, Standards and APIs, Constraints and failure modes, and Prior art).
* Launches parallel read-only discovery subagents and ends its turn immediately.
* **Reference Guide:** Read [`references/research_phase.md`](references/research_phase.md) for vector decomposition and briefing templates.

### 3. Step 2: Define (Diamond 1 Convergence)
* Coordinator synthesizes research reports into a unified **Foundation Document** (Technical Specification, Editorial Outline, Legal Brief, or PRD).
* Establishes system contracts, interfaces, chapter structure, or argument trees, alongside disjoint work package allocations.
* **Document Template:** Populate [`assets/specification_template.md`](assets/specification_template.md) with research synthesis and work breakdowns.

### 4. Step 3: User Steering Gate (Interactive Alignment)
* Coordinator presents the executive summary, draft Foundation Document, and architectural or editorial trade-offs to the user.
* Solicits user feedback, resolves decision forks, and obtains explicit confirmation before proceeding to creation.

### 5. Step 4: Develop (Diamond 2 Divergence)
* Coordinator launches up to `DOP` parallel write-enabled creator subagents and ends its turn immediately.
* Each creator receives a strictly disjoint Work Package (WP) and runs localized verification:
  - **Software:** Package-scoped unit tests (`go test ./internal/pkg/...`, `pytest tests/unit/`, `npm test`).
  - **Writing:** Section drafting against word count, tone, and source citations.
  - **Legal/Policy:** Argument drafting with case citations and statutory cross-referencing.
* **Reference Guide:** Read [`references/development_phase.md`](references/development_phase.md) for disjoint allocation and creator briefing templates.

### 6. Step 5: Deliver (Diamond 2 Convergence & Quality Gating)
* Coordinator integrates all parallel deliverables into a coherent whole and executes end-to-end verification.
* **Failure Recovery Protocol:** If any integration test, fact-check, or consistency check fails:
  1. Isolate the failing component and review specific error traces or discrepancies.
  2. Launch a targeted repair subagent with the exact context and interface contract.
  3. Re-verify all delivery gates until 100% pass before presenting the final deliverable to the user.

---

## Common gotchas and antipatterns

1. **Skipping Inception and Assuming User Intent:** Never jump straight into research divergence without establishing core scope boundaries, audience, and constraints with the user.
2. **Premature Implementation in Diamond 1:** Never author production code or final prose during discovery and definition. Diamond 1 is strictly for reconnaissance, constraint mapping, and interface or outline design.
3. **Bypassing the User Steering Gate:** Never move from definition into creation without presenting the Foundation Document and trade-offs to the user for explicit confirmation.
4. **Overlapping Work Allocations:** Never assign two parallel creator subagents to the same file, section, or deliverable slice. Work Packages must stay strictly disjoint to prevent race conditions and merge conflicts.
5. **Broad Integration Sweeps during Creation:** Creator subagents must run fine-grained, localized verification (such as package unit tests or section fact-checks) rather than whole-project sweeps while peer subagents are mid-edit.
6. **Passive Polling Loops:** Coordinator agents must never poll subagent status in a loop. Spawning subagents is fire-and-yield; rely on automatic reactive wakeup to keep the Coordinator responsive to the user.

---

## Progressive disclosure and references

- **Inception Phase Guide**: [`references/inception_phase.md`](references/inception_phase.md): Pre-diamond alignment, decision-tree traversal, and interview rules.
- **Research Phase Guide**: [`references/research_phase.md`](references/research_phase.md): Exploration vectors, discovery briefing templates, and synthesis rules across domains.
- **Development Phase Reference**: [`references/development_phase.md`](references/development_phase.md): Delivery execution, disjoint creator rules, and quality gates.
- **Specification Template**: [`assets/specification_template.md`](assets/specification_template.md): Structured specification template for the Define phase.
