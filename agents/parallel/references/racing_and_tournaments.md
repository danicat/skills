# Agent Racing & Tournament Guide

This reference guide details the primary exception to orthogonal task decomposition: **Agent Racing and Tournaments**.

While orthogonal partitioning divides a project into non-overlapping pieces, **Racing** dispatches multiple subagents on the *same* problem (or deliberate variations of it) to compare alternatives, discover diverse solutions, and select or synthesize the best outcome.

---

## 1. When to Race: The Strategic Rationale

Standard parallel decomposition minimizes redundant work. Racing deliberately invests parallel budget into redundancy.

```
       ORTHOGONAL PARTITIONING                     RACING / TOURNAMENT
       (Disjoint Work Units)                      (Redundant Alternatives)

            Coordinator                                 Coordinator
           /     |     \                               /     |     \
          v      v      v                             v      v      v
      Task A   Task B  Task C                     Candidate Candidate Candidate
        |        |      |                            1         2         3
        +--------+------+                             \        |        /
                 |                                     v       v       v
                 v                                  +---------------------+
              Reduce                                |  Judge / Selection  |
          (Integration)                             |  Best-of-N / Merge  |
                                                    +---------------------+
                                                               |
                                                               v
                                                         Optimal Deliverable
```

### Ideal Scenarios for Racing:
1. **High-Stakes Architecture & Design**: Multiple valid approaches exist with distinct trade-offs (e.g., event-driven vs polling, relational vs document storage).
2. **Difficult Optimization & Algorithmic Problems**: The solution space is large and non-deterministic; different heuristic paths yield varying performance.
3. **Creative Divergence**: Generating slogans, hooks, editorial angles, or UI layouts where variety is essential before converging.
4. **Adversarial & Security Auditing**: Independent agents approach the codebase without shared bias, catching vulnerabilities others miss.
5. **High-Assurance Verification**: Consensus checks for critical calculations, security policies, or legal interpretations.

---

## 2. The Four Racing Archetypes

### Archetype 1: Identical Replicated Racing (Pure Stochastic Race)
Dispatches `N` subagents with the exact same instructions and constraints.
- **Mechanism**: Relies on model non-determinism, differing search pathways, and varied chain-of-thought exploration.
- **Primary Use**: Bug hunting, creative brainstorming, complex math/algorithmic problem-solving.
- **Evaluation**: The first valid solution that passes automated test harnesses, or the cleanest code structure.

### Archetype 2: Perturbed / Constrained Angle Racing
Dispatches `N` subagents with differing architectural constraints, priorities, or paradigms.
- **Example: Backend API Service Design (DOP = 3)**:
  - Worker 1 Constraint: "Optimize for maximum write throughput and ultra-low latency."
  - Worker 2 Constraint: "Optimize for strict ACID consistency and relational normalization."
  - Worker 3 Constraint: "Optimize for developer ergonomics and rapid iteration speed."
- **Evaluation**: Side-by-side trade-off matrix comparing latency, complexity, and operational cost.

### Archetype 3: Multi-Persona / Adversarial Racing
Dispatches agents with conflicting incentives or specialized roles.
- **Example: Smart Contract Audit (DOP = 4)**:
  - Worker 1: Defending Architect (explains invariants and safety proofs).
  - Worker 2: White-Hat Exploiter (actively crafts exploit payloads and re-entrancy attacks).
  - Worker 3: Gas Optimization Specialist (audits opcode efficiency).
  - Worker 4: Formal Verification Reviewer (validates state machine transitions).
- **Evaluation**: Exploits discovered by Worker 2 are tested against the defenses of Worker 1.

### Archetype 4: Tournament Brackets (Multi-Stage Best-of-N)
Executes a multi-tier tournament for complex deliverables.
- **Round 1 (Diverge)**: Spawn 4 to 8 agents generating independent prototypes.
- **Round 2 (Evaluate & Prune)**: Benchmark or score each prototype; select the top 2 finalists.
- **Round 3 (Converge & Polish)**: Finalists incorporate the best ideas discovered in competing submissions, or a designated Synthesis Agent merges both.

---

## 3. Evaluation & Selection Paradigms

Once racing subagents submit their candidates, the Coordinator applies one of three convergence mechanisms:

```
+-------------------------------------------------------------------------+
|                        CONVERGENCE MECHANISMS                           |
|                                                                         |
|  1. Best-of-N (Winner Take All)                                         |
|     Candidate 1  [Score: 78]                                            |
|     Candidate 2  [Score: 94]  ===>  WINNER: Candidate 2 Selected        |
|     Candidate 3  [Score: 82]                                            |
|                                                                         |
|  2. Hybrid Synthesis (Cherry-Pick & Merge)                              |
|     Candidate 1: Best caching strategy        \                         |
|     Candidate 2: Cleanest API ergonomics       ===>  Unified Synthesis |
|     Candidate 3: Comprehensive edge case tests/                         |
|                                                                         |
|  3. Consensus & Majority Voting                                         |
|     Worker 1: "Flag as critical vulnerability"                          |
|     Worker 2: "Flag as critical vulnerability" ===>  Consensus Verdict  |
|     Worker 3: "Flag as low severity issue"                              |
+-------------------------------------------------------------------------+
```

### Mechanism A: Best-of-N Selection (Winner Take All)
- Coordinator evaluates submissions against an objective rubric:
  1. Correctness (automated test suite passes).
  2. Performance (benchmark speed, memory efficiency).
  3. Elegance & readability (clean abstractions, idiomatic style).
- The highest-ranking candidate is chosen as the deliverable; runners-up are discarded.

### Mechanism B: Hybrid Synthesis (Merge & Cherry-Pick)
- Coordinator or a dedicated Synthesis Agent reviews all submissions to extract the best elements:
  - Take the data structures from Candidate A.
  - Take the error-handling patterns from Candidate B.
  - Take the integration test suite from Candidate C.
- Result: A composite solution superior to any single submission.

### Mechanism C: Majority Voting & Consensus
- Used for fact verification, classification, and sanity checks.
- If >= 2 out of 3 workers agree on a finding, it is accepted into the final report.
- Outliers and disagreements are highlighted in an appendix for user review.

---

## 4. Operational Playbook for Racing

When invoking `/parallel` for a racing objective:

### Step 1: Formulate the Racing Specification
Draft a core problem statement and define:
- What must remain invariant across all candidates (e.g., public API interface, test cases).
- What degrees of freedom each candidate may explore (e.g., algorithms, libraries, caching).

### Step 2: Set the Budget (DOP)
- Small race (quick alternative check): `DOP = 2` to `3`.
- Standard tournament / creative divergence: `DOP = 4` to `6`.
- High-assurance / broad space search: `DOP = 8` to `12`.

### Step 3: Dispatch & Immediately Yield
Dispatch all `N` racing workers simultaneously using `invoke_subagent`. End turn immediately so the main chat session remains unblocked for user input.

### Step 4: Adjudicate Submissions
Upon receiving completion messages from all racing workers:
1. Verify that all candidates satisfied invariant requirements.
2. Run test suites, benchmarks, or scoring rubrics.
3. Formulate the comparative evaluation table.
4. Deliver the winning candidate or merged synthesis to the user with a transparent trade-off summary.

---

## 5. Comparative Trade-Off Summary Template

When presenting race results to the user, format findings cleanly:

```markdown
### Parallel Race Results (Budget: 3 Workers)

| Criterion | Candidate 1 (In-Memory Map) | Candidate 2 (B-Tree Index) | Candidate 3 (LSM Tree) |
| :--- | :--- | :--- | :--- |
| **Write Throughput** | 120,000 ops/sec | 45,000 ops/sec | 95,000 ops/sec |
| **Memory Footprint** | High (O(N) in RAM) | Moderate | Low |
| **Recovery Time** | Slow (full rebuild) | Instant (WAL) | Fast (SSTable) |
| **Complexity** | 180 lines | 420 lines | 610 lines |
| **Status** | Verified (tests pass) | Verified (tests pass) | Verified (tests pass) |

**Verdict**: Selected Candidate 2 for production balance of durability and index speed.
```
