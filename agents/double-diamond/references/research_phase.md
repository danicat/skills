# Double-Diamond Research Phase (Diamond 1: Problem Space)

The Research Phase maps the problem space thoroughly before any implementation code is written. It consists of two distinct steps: **Discover (Divergence)** and **Define (Convergence)**, followed by the **User Steering Gate**.

---

## 1. Step 1: Discover (Divergence)

### 1.1 Objective
Explore all dimensions of the problem concurrently. Instead of a single agent doing sequential lookups, the Coordinator divides the research scope into orthogonal investigation vectors and launches parallel `research` subagents up to the allocated Research Degree of Parallelism (DOP).

### 1.2 Orthogonal Research Vectors
Allocate research subagents across distinct areas:

1. **Codebase & Architecture Reconnaissance (`Codebase Researcher`):**
   - Maps existing module boundaries, interfaces, callers, data flows, and current implementation constraints.
   - Identifies exact file paths, exported types, and integration points.
2. **Ecosystem, SDK & Dependency Analyst (`Ecosystem Analyst`):**
   - Researches third-party libraries, official SDK documentation, API specs, breaking changes, and version compatibility.
   - Finds verified real-world implementation examples and best practices.
3. **Performance, Concurrency & Scaling Analyst (`Performance Analyst`):**
   - Evaluates memory footprints, lock contention, query latency, rate limits, and batching mechanisms.
4. **Failure Modes, Security & Edge Cases (`Reliability Analyst`):**
   - Identifies edge cases, timeout propagation, error recovery paths, authentication/permission risks, and data corruption scenarios.

### 1.3 Launching Research Subagents
The Coordinator invokes subagents using `invoke_subagent` with the `research` subagent type:

```json
{
  "Subagents": [
    {
      "TypeName": "research",
      "Role": "Codebase Researcher",
      "Prompt": "Investigate existing package structure and interfaces for [Feature] in repository. List all impacted files, type definitions, and call sites. Return a detailed markdown summary."
    },
    {
      "TypeName": "research",
      "Role": "Ecosystem Analyst",
      "Prompt": "Research the latest API documentation, SDK methods, and error types for [Dependency/API]. Report required configuration parameters, payload formats, and edge cases."
    }
  ]
}
```

---

## 2. Step 2: Define (Convergence & Specification)

### 2.1 Objective
Synthesize the disparate research reports from the parallel agents into a single, authoritative **Technical Specification Document**.

### 2.2 Specification Synthesis Checklist
When consolidating research output into the specification (using [`assets/specification_template.md`](../assets/specification_template.md)):

- [ ] **Unified Vocabulary:** Eliminate contradictory terminology or conflicting assumptions discovered across research tracks.
- [ ] **Explicit Interfaces:** Write out complete type definitions, function signatures, error codes, and configuration structs.
- [ ] **Disjoint Work Allocation:** Decompose the upcoming development phase into mutually exclusive file assignments (Work Packages) so developer agents can execute in parallel without write collisions.
- [ ] **Acceptance & Verification Gates:** Define clear pass/fail criteria (build commands, unit tests, integration scenarios).

---

## 3. The User Steering Gate

Before initiating Diamond 2 (Development), the Coordinator MUST present the consolidated specification to the user.

### 3.1 Steering Interaction
The Coordinator presents:
1. Executive summary of findings and key technical trade-offs.
2. The draft Technical Specification.
3. Any open architectural questions or decision forks.

### 3.2 User Approval & Steering
The Coordinator prompts the user for steering:
* If the user requests adjustments or chooses a specific architectural branch, the Coordinator updates the specification immediately.
* Once the user approves the specification, the Coordinator initiates Diamond 2 (Development Phase).
