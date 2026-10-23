# [Initiative / Project Name] Foundation Document

**Document Type:** [Technical Specification | Editorial Outline | Legal Brief | Product PRD]  
**Date:** YYYY-MM-DD  
**Status:** [Draft | Under Review | Approved]  
**Coordinator:** Double-Diamond Coordinator  
**DOP / Agent Budget:** Discovery: [N], Development: [M]  

---

## 1. Executive Summary & Problem Space

### 1.1 Context & Core Objectives
* State the primary objective, thesis, or problem statement in 2-3 clear sentences.
* Summarize the target audience, user persona, or stakeholder expectations.

### 1.2 Research Findings & Synthesis (Diamond 1 Convergence)
* **Current Landscape / Baseline:** Existing architecture, literature, case precedents, or market state.
* **External Standards & Ecosystem:** Relevant third-party tools, statutes, publications, or competitive benchmarks.
* **Trade-off Analysis:** Alternative approaches evaluated, pros/cons, and rationale for the selected direction.

---

## 2. System Contracts & Deliverable Structure

### 2.1 Core Structure / Architecture
* **Software**: Component architecture, data flow, subsystem boundaries.
* **Writing**: Narrative arc, chapter breakdown, section word count targets.
* **Legal**: Legal theory, cause of action, argument hierarchy.
* **Product**: Feature requirements, user journey, success metrics.

### 2.2 Detailed Schemas / Content Outlines / Argument Trees
* Explicit contracts, type definitions, function signatures, section outlines, or statutory references:
```
// Definitions, Outlines, or Contract Schemas
```

### 2.3 Edge Cases, Counter-Arguments & Risk Mitigations
* Anticipated failure modes, opposing arguments, latency/security risks, or editorial sensitivities.

---

## 3. Work Breakdown & Disjoint Work Allocation (Diamond 2 Divergence)

To ensure parallel creator subagents work without collision, all tasks must target mutually exclusive files or sections:

| Work Package (WP) | Target File / Section | Creator Role | Scope & Deliverable | Pre-requisites |
| :--- | :--- | :--- | :--- | :--- |
| **WP-1: Foundation/Core** | `pkg/core/...` or `Chapter 1-2` or `Claim I` | Primary Author / Dev | Core structures, definitions, baseline argument | None |
| **WP-2: Logic / Body** | `pkg/service/...` or `Chapter 3-4` or `Claim II` | Domain Specialist | Implementation logic, deep analysis, evidence | WP-1 |
| **WP-3: Surface / Transport** | `pkg/api/...` or `Chapter 5-6` or `Relief Sought` | Interface Specialist | API handlers, practical examples, conclusion | WP-1, WP-2 |
| **WP-4: Verification / QA** | `test/...` or `Fact-Checking & Citations` | Quality Reviewer | Unit tests, benchmark suite, citation audit | WP-1, WP-2 |

---

## 4. Verification & Quality Delivery Gates (Diamond 2 Convergence)

Before marking delivery complete, the following domain gates must pass:

- [ ] **Structural Integrity Gate:** Code compiles cleanly with 0 errors, or prose follows required chapter/section format.
- [ ] **Localized Verification Gate:** All package unit tests pass, or all section claims are backed by verified citations/data.
- [ ] **Quality & Consistency Gate:** Code meets linting/style rules, or writing passes readability, tone, and grammar audits.
- [ ] **Foundation Compliance Gate:** All requirements and acceptance criteria from Section 2 are fully satisfied.
- [ ] **Documentation / Attribution Gate:** All public interfaces, configuration flags, or source citations are fully documented.
