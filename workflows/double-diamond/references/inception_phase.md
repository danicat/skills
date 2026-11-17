# Double-Diamond inception phase (pre-diamond alignment)

The **Inception Phase** is the foundational alignment gate that precedes Diamond 1 (Discovery). It aligns the Coordinator with the human stakeholder before research divergence begins.

```text
                              INCEPTION PHASE
                          (Pre-Diamond Alignment)
                    One-Decision-at-a-Time Interview
                      Establish Shared Understanding
                                     │
                                     ▼
                      DIAMOND 1: DISCOVERY & DEFINITION
```

---

## 1. Objectives and rationale

1. **Eliminate False Assumptions Early:** Prevents discovery subagents from exploring irrelevant branches or solving the wrong problem.
2. **Uncover Non-Negotiables and Constraints:** Surfaces critical boundaries (such as target language or framework, offline requirements, word count limits, jurisdictional scope, licensing, and security).
3. **Establish Deliverable Modality:** Clarifies whether the output is a standalone CLI, a microservice, an editorial article, a legal motion, a PRD, or an architecture document.
4. **Map Decision Dependencies:** Traverses the design tree systematically, resolving foundational choices before secondary ones.

---

## 2. One-decision-at-a-time interview rules

During Inception, the Coordinator interviews the user directly before dispatching research subagents.

### Operational rules for inception interviews

1. **One Decision at a Time:** Focus each question on a distinct architectural, editorial, or business decision node. Avoid overwhelming the user with multi-part questionnaires.
2. **Explore Before Asking:** If an answer can be unambiguously determined by inspecting the existing repository, local environment, or provided materials, inspect them first. Only ask about user intent, trade-offs, and uncommitted requirements.
3. **Always Provide a Recommended Default:** Prefix the recommended choice with `(Recommended)` and clearly state the rationale.
4. **Format Options as Direct User Responses:** Provide concise, direct options representing distinct architectural or editorial branches.

---

## 3. The 4-tier decision tree traversal

Traverse these 4 tiers in order, formulating targeted questions one decision at a time:

1. **Tier 1: Mission and Scope Boundaries**
   - What is explicitly in scope? What is explicitly out of scope?
   - *Software:* Standalone tool vs. modifying existing repository.
   - *Writing:* Core thesis, narrative angle, target audience.
   - *Legal:* Primary claims, causes of action, target forum.
2. **Tier 2: Core Foundation and Technical or Editorial Stack**
   - *Software:* Programming language, runtime, key frameworks, persistence tier.
   - *Writing:* Style guide, length and depth target, source citation format.
   - *Legal:* Governing statutes, applicable jurisdiction, standard of review.
3. **Tier 3: Operational Constraints and Non-Negotiables**
   - *Software:* Offline vs. cloud dependencies, latency budgets, security requirements.
   - *Writing:* Editorial voice, prohibited terms, factual evidence thresholds.
   - *Legal:* Procedural deadlines, evidentiary boundaries, precedent hierarchy.
4. **Tier 4: Deliverable Modality and Interaction Surface**
   - *Software:* CLI commands, REST/gRPC endpoints, TUI vs. headless JSON.
   - *Writing:* Markdown publication, PDF report, slide deck summary.
   - *Legal:* Formal brief, motion memorandum, advisory opinion.

---

## 4. Inception exit criteria (transition to Diamond 1)

The Coordinator concludes the Inception Phase and transitions to Diamond 1 (Discovery) when:

- [ ] Core mission, thesis, and scope boundaries are established without ambiguity.
- [ ] Primary foundation, frameworks, and deliverable modality are confirmed.
- [ ] Key trade-offs, non-negotiables, and user preferences are recorded.
- [ ] Research vectors for Diamond 1 are cleanly defined based on user steering.
