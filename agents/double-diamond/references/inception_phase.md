# Double-Diamond Inception Phase (Pre-Diamond Alignment)

The **Inception Phase** is the foundational alignment gate that precedes Diamond 1 (Discovery). Derived from agile engineering inception practices (pioneered at ThoughtWorks and modern product design), Inception aligns the agent swarm with the human stakeholder before research divergence begins.

```
                              INCEPTION PHASE
                          (Pre-Diamond Alignment)
                         /grill-me User Interview
                      Establish Shared Understanding
                                     │
                                     ▼
                        DIAMOND 1: DISCOVERY & SPECS
```

---

## 1. Objectives & Rationale

1. **Eliminate False Assumptions Early:** Prevents research agents from exploring irrelevant technical branches or solving the wrong problem.
2. **Uncover Non-Negotiables & Constraints:** Surfaces critical technical boundaries (e.g., target programming language, offline vs cloud requirements, strict latency budgets, zero-dependency rules).
3. **Establish Deliverable Modality:** Clarifies upfront whether the deliverable is a standalone CLI binary, a shared library, a schema, or documentation.
4. **Map Decision Dependencies:** Traverses the design tree systematically, resolving foundational architectural choices before secondary ones.

---

## 2. The `/grill-me` Interactive Interview Protocol

During Inception, the Coordinator conducts an interactive interview using the `/grill-me` methodology via the `ask_question` tool.

### Operational Rules for Inception Grilling:

1. **One Decision at a Time:** Focus each question on a distinct architectural or business decision node. Do not overwhelm the user with multi-part questionnaires.
2. **Explore Before Asking:** If an answer can be unambiguously determined by inspecting the existing repository or local environment, inspect the codebase first. Only ask about user intent, trade-offs, and uncommitted requirements.
3. **Always Provide a Recommended Default:** Prefix the recommended choice with `(Recommended)` and clearly articulate the engineering rationale.
4. **Format Options as Direct User Responses:** Provide concise, direct options representing distinct architectural branches.
5. **Traverse the Decision Tree in Order:**
   - **Level 1: Mission & Scope Boundaries** (What is in scope? What is explicitly out of scope?)
   - **Level 2: Core Runtime & Tech Stack** (Language, frameworks, dependencies, deployment targets)
   - **Level 3: Operational Constraints** (Offline-first vs Cloud, latency budgets, licensing, security)
   - **Level 4: UX & Integration Surfaces** (CLI flags, interactive TUI vs headless JSON, API contracts)

---

## 3. Inception Question Archetypes & Examples

### Archetype A: Tech Stack & Runtime Fork
```json
{
  "question": "Which language and runtime should we use to implement the new toolchain?",
  "options": [
    "(Recommended) Go (single static binary, zero runtime dependencies, instant <10ms startup)",
    "Python 3 (modern uv/PEP 723 scripting with rich ecosystem)",
    "TypeScript / Node.js (npx runnable, cross-platform JS ecosystem)"
  ]
}
```

### Archetype B: Agentic & Model Execution Tier
```json
{
  "question": "How should the agentic routing and intent-matching engine operate?",
  "options": [
    "(Recommended) Hybrid: Fast zero-token keyword/BM25 pre-filter (<1ms) with Gemma 4 / Gemini API fallback for ambiguous vibes",
    "Pure Cloud LLM: Always invoke hosted Gemini API (gemini-3.5-flash-lite / Gemma 4)",
    "Pure Local / Offline: Deterministic BM25 + Subword TF-IDF without any external LLM dependencies"
  ]
}
```

### Archetype C: Local Storage & Installation Scope
```json
{
  "question": "Where should the downloaded assets/skills be installed on the host system?",
  "options": [
    "(Recommended) Dual-scope: Default to workspace (.gemini/skills/ or .agent/skills/) with optional --global flag (~/.gemini/config/skills/)",
    "Workspace-only: Always install into the current project repository",
    "Global-only: Always install into user home directory"
  ]
}
```

---

## 4. Inception Exit Criteria (Transition to Diamond 1)

The Coordinator concludes the Inception Phase and transitions to Diamond 1 (Discovery) when:

- [ ] Core mission and scope boundaries are established without ambiguity.
- [ ] Primary language, runtime, and framework selections are confirmed.
- [ ] Key trade-offs and user preferences are recorded.
- [ ] Research vectors for Diamond 1 are cleanly defined based on user steering.
