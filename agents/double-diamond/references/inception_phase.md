# Double-Diamond Inception Phase (Pre-Diamond Alignment)

The **Inception Phase** is the foundational alignment gate that precedes Diamond 1 (Discovery). It aligns the agent swarm with the human stakeholder before research divergence begins.

```
                              INCEPTION PHASE
                          (Pre-Diamond Alignment)
                         /grill-me User Interview
                      Establish Shared Understanding
                                     │
                                     ▼
                      DIAMOND 1: DISCOVERY & DEFINITION
```

---

## 1. Objectives & Rationale

1. **Eliminate False Assumptions Early:** Prevents subagents from exploring irrelevant branches or solving the wrong problem.
2. **Uncover Non-Negotiables & Constraints:** Surfaces critical boundaries (e.g., target language/framework, offline requirements, word count limits, jurisdictional scope, licensing, security).
3. **Establish Deliverable Modality:** Clarifies whether the output is a standalone CLI, a microservice, an editorial article, a legal motion, a PRD, or an architecture document.
4. **Map Decision Dependencies:** Traverses the design tree systematically, resolving foundational choices before secondary ones.

---

## 2. The `/grill-me` Interactive Interview Protocol

During Inception, the Coordinator conducts an interactive interview using the `/grill-me` methodology via the `ask_question` tool.

### Operational Rules for Inception Grilling:

1. **One Decision at a Time:** Focus each question on a distinct architectural, editorial, or business decision node. Avoid overwhelming the user with multi-part questionnaires.
2. **Explore Before Asking:** If an answer can be unambiguously determined by inspecting the existing repository, local environment, or provided materials, inspect them first. Only ask about user intent, trade-offs, and uncommitted requirements.
3. **Always Provide a Recommended Default:** Prefix the recommended choice with `(Recommended)` and clearly articulate the rationale.
4. **Format Options as Direct User Responses:** Provide concise, direct options representing distinct architectural or editorial branches.

---

## 3. The 4-Tier Decision Tree Traversal

Traverse these 4 tiers in order, formulating targeted questions with `ask_question`:

1. **Tier 1: Mission & Scope Boundaries**
   - What is explicitly in scope? What is explicitly out of scope?
   - *Software*: Standalone tool vs modifying existing repository.
   - *Writing*: Core thesis, narrative angle, target audience.
   - *Legal*: Primary claims, causes of action, target forum.
2. **Tier 2: Core Foundation & Technical / Editorial Stack**
   - *Software*: Programming language, runtime, key frameworks, persistence tier.
   - *Writing*: Style guide, length/depth target, source citation format.
   - *Legal*: Governing statutes, applicable jurisdiction, standard of review.
3. **Tier 3: Operational Constraints & Non-Negotiables**
   - *Software*: Offline vs cloud dependencies, latency budgets, security requirements.
   - *Writing*: Editorial voice, prohibited terms, factual evidence thresholds.
   - *Legal*: Procedural deadlines, evidentiary boundaries, precedent hierarchy.
4. **Tier 4: Deliverable Modality & Interaction Surface**
   - *Software*: CLI commands, REST/gRPC endpoints, TUI vs headless JSON.
   - *Writing*: Markdown publication, PDF report, slide deck summary.
   - *Legal*: Formal brief, motion memorandum, advisory opinion.

---

## 4. Inception Exit Criteria (Transition to Diamond 1)

The Coordinator concludes the Inception Phase and transitions to Diamond 1 (Discovery) when:

- [ ] Core mission, thesis, and scope boundaries are established without ambiguity.
- [ ] Primary foundation, frameworks, and deliverable modality are confirmed.
- [ ] Key trade-offs, non-negotiables, and user preferences are recorded.
- [ ] Research vectors for Diamond 1 are cleanly defined based on user steering.
