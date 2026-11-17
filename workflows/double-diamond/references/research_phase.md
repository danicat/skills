# Double-Diamond research phase (Diamond 1: problem space)

The Research Phase thoroughly explores the problem space before any final deliverables are created. It consists of two distinct steps: **Discover (Divergence)** and **Define (Convergence)**, followed by the **User Steering Gate**.

---

## 1. Step 1: Discover (divergence)

### 1.1 Objective
Explore all dimensions of the problem concurrently. Instead of a single agent performing sequential lookups, the Coordinator divides the research scope into orthogonal investigation vectors, launches parallel **read-only discovery subagents** up to the allocated Degree of Parallelism (`DOP`), and ends its turn immediately.

### 1.2 Orthogonal exploration vectors across domains

Allocate discovery subagents across distinct areas according to the initiative type:

1. **Landscape and Baseline Reconnaissance:**
   - *Software:* Maps codebase module boundaries, interfaces, callers, and current constraints.
   - *Writing:* Analyzes current discourse, competitor articles, and reader sentiment.
   - *Legal:* Maps existing case facts, evidentiary timeline, and jurisdictional standing.
2. **Ecosystem, Standards, and Precedent Analysis:**
   - *Software:* Researches official SDK documentation, API specs, and version compatibility.
   - *Writing:* Gathers authoritative primary source data, study findings, and verified quotes.
   - *Legal:* Researches binding statutes, controlling appellate precedents, and persuasive case law.
3. **Constraints, Scaling, and Edge Case Analysis:**
   - *Software:* Evaluates memory footprint, latency, lock contention, and rate limits.
   - *Writing:* Identifies controversial angles, counter-arguments, and nuance requirements.
   - *Legal:* Analyzes procedural hurdles, affirmative defenses, and opposing counsel counter-theories.

### 1.3 Discovery subagent briefing templates

Launch parallel read-only discovery subagents with explicit vector ownership and return contracts:

```markdown
Role: Landscape Researcher (Read-Only)
Vector: Existing baseline and architecture for [Initiative] in [Repository / Domain]
Objective: Map key constraints, existing patterns, callers, and integration points.
Boundaries: Read-only exploration. Do not create or modify deliverable files.
Output: Return a structured Markdown report with file paths, symbol names, and open risks.
```

#### High-DOP micro-probe brief (`DOP >= 8`)

When operating with large agent budgets, enforce high-density, concise reporting to streamline synthesis:

```markdown
Role: Micro-Probe ([Specific Target]) (Read-Only)
Target: [File / API / Clause / Dataset]
Output: Return a high-signal summary (at most 150 words) covering:
1. Core status and observed facts
2. Critical constraints or blockers
3. Recommended contract or interface
```

---

## 2. Step 2: Define (convergence and foundation synthesis)

### 2.1 Objective
Synthesize the disparate research reports from parallel subagents into a single, authoritative **Foundation Document** (Technical Specification, Editorial Outline, Legal Brief, or PRD).

### 2.2 Foundation synthesis checklist
When consolidating research output using [`assets/specification_template.md`](../assets/specification_template.md):

- [ ] **Unified Vocabulary:** Eliminate contradictory terminology or conflicting assumptions discovered across research tracks.
- [ ] **Explicit Contracts and Structures:** Define complete data types, section outlines, or argument hierarchies.
- [ ] **Disjoint Work Allocation:** Decompose the upcoming development phase into mutually exclusive assignments (Work Packages) so creator subagents can execute in parallel without collisions.
- [ ] **Acceptance and Verification Gates:** Define clear pass/fail criteria (tests, style benchmarks, citation standards).

---

## 3. The User Steering Gate

Before initiating Diamond 2 (Development), the Coordinator presents the consolidated Foundation Document to the user.

### 3.1 Steering interaction
The Coordinator presents:
1. Executive summary of research findings and key trade-offs.
2. The draft Foundation Document.
3. Any open questions, design forks, or strategic decisions.

### 3.2 User approval and steering
* If the user requests adjustments or chooses a specific direction, the Coordinator updates the Foundation Document immediately.
* Once the user approves the document, the Coordinator initiates Diamond 2 (Solution Space).
