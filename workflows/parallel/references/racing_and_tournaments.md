# Agent racing and tournament guide

This guide covers the primary exception to orthogonal task decomposition: **Agent Racing and Tournaments**.

While orthogonal partitioning splits a project into non-overlapping slices, **Racing** assigns multiple subagents to the *same* problem (or deliberate variations of it) to compare alternatives, generate diverse solutions, and select or merge the strongest result.

---

## 1. When to race: the strategic rationale

Standard parallel execution minimizes redundant work. Racing deliberately invests parallel budget in competitive redundancy.

```text
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

### Ideal scenarios for racing
1. **High-stakes architecture and design:** Multiple valid approaches have distinct trade-offs (such as event-driven vs. polling, or relational vs. document storage).
2. **Hard optimization and algorithmic problems:** The search space is large and non-deterministic, so diverse paths uncover better complexity bounds.
3. **Creative divergence:** Generating hooks, headlines, editorial angles, or UI layouts where variety improves final quality.
4. **Adversarial and security auditing:** Independent workers inspect the codebase without shared anchoring, catching subtle flaws.
5. **High-assurance verification:** Independent cross-checks on critical calculations, security rules, or policy analysis.

---

## 2. The four racing archetypes

### Archetype 1: identical replicated racing (pure stochastic race)
Dispatches `N` subagents with identical prompts and constraints.
- **Mechanism:** Uses independent search paths and sampling diversity across workers.
- **Primary use:** Bug hunting, creative brainstorming, and hard algorithmic puzzles.
- **Evaluation:** First valid solution passing all tests, or cleanest code structure.

### Archetype 2: perturbed or constrained angle racing
Dispatches `N` subagents with differing constraints, priorities, or paradigms.
- **Example (Backend API service design, `DOP = 3`):**
  - Worker 1 constraint: optimize for maximum write throughput and lowest tail latency.
  - Worker 2 constraint: optimize for strict ACID consistency and relational clarity.
  - Worker 3 constraint: optimize for operator simplicity and rapid iteration.
- **Evaluation:** Side-by-side comparison matrix weighing latency, complexity, and operational cost.

### Archetype 3: multi-persona or adversarial racing
Dispatches workers with opposing goals or specialized roles.
- **Example (Security audit, `DOP = 4`):**
  - Worker 1: Defender reviewing invariants and access controls.
  - Worker 2: Red-team tester crafting exploit inputs and race scenarios.
  - Worker 3: Performance specialist profiling hot paths and allocations.
  - Worker 4: Formal reviewer verifying state transitions and rollback safety.
- **Evaluation:** Validate exploit hypotheses discovered by Worker 2 directly against Worker 1's defenses.

### Archetype 4: tournament brackets (multi-stage Best-of-N)
Runs a structured multi-round tournament for complex problems.
- **Round 1 (Diverge):** Launch `4` to `8` workers producing independent prototypes.
- **Round 2 (Evaluate and Prune):** Benchmark or score every candidate and pick the top `2` finalists.
- **Round 3 (Converge and Polish):** Finalists fold in the strongest ideas from rival submissions, or a synthesis worker combines both.

---

## 3. Evaluation and selection paradigms

Once racing workers return candidates, the Coordinator applies one of three selection strategies:

```text
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

### Mechanism A: Best-of-N selection (winner take all)
- Score submissions against an explicit rubric:
  1. **Correctness:** Automated tests and invariants pass.
  2. **Performance:** Latency, throughput, and memory footprint.
  3. **Maintainability:** Clear abstractions and idiomatic style.
- Ship the highest-scoring candidate and discard the rest.

### Mechanism B: hybrid synthesis (cherry-pick and merge)
- Review every candidate to combine the strongest parts:
  - Take the data model from Candidate A.
  - Take the error-handling path from Candidate B.
  - Take the edge-case tests from Candidate C.
- Produce a composite solution stronger than any individual candidate.

### Mechanism C: majority voting and consensus
- Ideal for fact checks, classification, and risk triage.
- Accept findings confirmed by at least 2 of 3 independent workers; list minority outliers in an appendix for human review.

---

## 4. Operational playbook for racing

When running a parallel race or tournament:

### Step 1: formulate the racing specification
Define clearly:
- What stays fixed across all candidates (public interfaces, input data, test suites).
- What varies freely per worker (algorithms, data structures, creative angle, trade-offs).

### Step 2: set the budget (DOP)
- **Focused check:** `DOP = 2` to `3`
- **Standard tournament or creative divergence:** `DOP = 4` to `6`
- **Broad search space:** `DOP = 8` to `12`
- **Automatic sizing (`parallel(auto)` / `auto`):** Use `2` to `3` candidates for narrow engineering trade-offs, or `4` to `6` for high-ambiguity architecture or creative divergence so judge and synthesis cost stays proportional to task ambiguity.

### Step 3: dispatch and yield immediately
Dispatch all `N` racing workers concurrently into isolated staging targets (`staging/candidate_<id>/`) and end your turn immediately so the main chat stays unblocked.

### Step 4: adjudicate submissions
When all racing workers finish:
1. Verify each candidate meets invariant requirements.
2. Run test suites, benchmarks, or judging rubrics.
3. Build a concise comparison matrix.
4. Present the winner or hybrid synthesis along with trade-offs.

---

## 5. Comparative trade-off summary template

Format race outcomes in a scannable comparison table:

```markdown
### Parallel Race Results (Budget: 3 Workers)

| Criterion | Candidate 1 (In-Memory Map) | Candidate 2 (B-Tree Index) | Candidate 3 (LSM Tree) |
| :--- | :--- | :--- | :--- |
| **Write Throughput** | 120,000 ops/sec | 45,000 ops/sec | 95,000 ops/sec |
| **Memory Footprint** | High (O(N) in RAM) | Moderate | Low |
| **Recovery Time** | Slow (full rebuild) | Instant (WAL) | Fast (SSTable) |
| **Complexity** | 180 lines | 420 lines | 610 lines |
| **Status** | Verified (tests pass) | Verified (tests pass) | Verified (tests pass) |

**Verdict:** Selected Candidate 2 for balanced durability and index lookup speed.
```
