# Double-Diamond Research Phase (Diamond 1: Problem Space)

The Research Phase thoroughly explores the problem space before any final deliverables are created. It consists of two distinct steps: **Discover (Divergence)** and **Define (Convergence)**, followed by the **User Steering Gate**.

---

## 1. Step 1: Discover (Divergence)

### 1.1 Objective
Explore all dimensions of the problem concurrently. Instead of a single agent performing sequential lookups, the Coordinator divides the research scope into orthogonal investigation vectors and launches parallel `research` subagents up to the allocated Degree of Parallelism (DOP).

### 1.2 Orthogonal Exploration Vectors Across Domains

Allocate research subagents across distinct areas according to the initiative type:

1. **Landscape & Baseline Reconnaissance (`Landscape Researcher`):**
   - *Software*: Maps codebase module boundaries, interfaces, callers, and current constraints.
   - *Writing*: Analyzes current discourse, competitor articles, and reader sentiment.
   - *Legal*: Maps existing case facts, evidentiary timeline, and jurisdictional standing.
2. **Ecosystem, Standards & Precedent Analyst (`Precedent Analyst`):**
   - *Software*: Researches official SDK documentation, API specs, and version compatibility.
   - *Writing*: Gathers authoritative primary source data, study findings, and verified quotes.
   - *Legal*: Researches binding statutes, controlling appellate precedents, and persuasive case law.
3. **Constraints, Scaling & Edge Case Analyst (`Risk Analyst`):**
   - *Software*: Evaluates memory footprint, latency, lock contention, and rate limits.
   - *Writing*: Identifies controversial angles, counter-arguments, and nuance requirements.
   - *Legal*: Analyzes procedural hurdles, affirmative defenses, and opposing counsel counter-theories.

### 1.3 Launching Research Subagents
The Coordinator invokes subagents using `invoke_subagent` with the `research` subagent type:

```json
{
  "Subagents": [
    {
      "TypeName": "research",
      "Role": "Landscape Researcher",
      "Prompt": "Investigate existing baseline/context for [Initiative] in [Repository/Domain]. Map key constraints, existing patterns, and integration points. Return a structured markdown report."
    },
    {
      "TypeName": "research",
      "Role": "Precedent Analyst",
      "Prompt": "Research the latest authoritative standards, documentation, and precedents for [Topic/API/Law]. Report core rules, requirements, and critical edge cases."
    }
  ]
}
```

#### High-DOP Micro-Probe Template ($\text{DOP} \ge 8$):
When operating with large agent budgets, enforce high-density, concise reporting to streamline map-reduce synthesis:

```json
{
  "Subagents": [
    {
      "TypeName": "research",
      "Role": "Micro-Probe [Target]",
      "Prompt": "Probe [Specific Target/File/API]. Return a concise, high-signal summary (<= 150 words) with: (1) Core status/facts, (2) Critical constraints/blockers, (3) Recommended contract/interface."
    }
  ]
}
```

---

## 2. Step 2: Define (Convergence & Foundation Synthesis)

### 2.1 Objective
Synthesize the disparate research reports from parallel subagents into a single, authoritative **Foundation Document** (Technical Specification, Editorial Outline, Legal Brief, or PRD).

### 2.2 Foundation Synthesis Checklist
When consolidating research output (using [`assets/specification_template.md`](../assets/specification_template.md)):

- [ ] **Unified Vocabulary:** Eliminate contradictory terminology or conflicting assumptions discovered across research tracks.
- [ ] **Explicit Contracts & Structures:** Define complete data types, section outlines, or argument hierarchies.
- [ ] **Disjoint Work Allocation:** Decompose the upcoming development phase into mutually exclusive assignments (Work Packages) so creator agents can execute in parallel without collisions.
- [ ] **Acceptance & Verification Gates:** Define clear pass/fail criteria (tests, style benchmarks, citation standards).

---

## 3. The User Steering Gate

Before initiating Diamond 2 (Development), the Coordinator MUST present the consolidated Foundation Document to the user.

### 3.1 Steering Interaction
The Coordinator presents:
1. Executive summary of research findings and key trade-offs.
2. The draft Foundation Document.
3. Any open questions, design forks, or strategic decisions.

### 3.2 User Approval & Steering
* If the user requests adjustments or chooses a specific direction, the Coordinator updates the Foundation Document immediately.
* Once the user approves the document, the Coordinator initiates Diamond 2 (Solution Space).
