---
name: rfc-template
description: >
  Activate this skill when proposing major features, exploring complex design alternatives under high ambiguity, or gathering technical consensus. Use this skill to draft, review, and progress collaborative Request for Comments (RFC) documents. Trigger this skill whenever a systematic design proposal is needed before drafting immutable Architecture Decision Records.
---

# Request for Comments (RFC) Framework

Use this skill to draft, review, and manage Request for Comments (RFC) documents. RFCs are collaborative design proposals used to explore options, solicit feedback, and build consensus on complex or ambiguous engineering problems.

---

## 1. RFC and ADR Integration

RFCs and ADRs form a continuous design workflow:

- RFC (Request for Comments): A fluid, collaborative document used for discussion. It outlines multiple options, highlights uncertainties, and gathers feedback. It can be modified or rejected during debate.
- ADR (Architecture Decision Record): An immutable record of a final technical decision.
- Workflow pipeline: Approved RFCs typically transition into one or more immutable ADRs. Rejections and postponements should also be documented within the RFC directory for historical reference.

---

## 2. Directory and Naming Conventions

Store all RFC documents in the project RFC directory:

```text
design/rfc/
  ├── 0001-use-structured-logging.md
  ├── 0002-migrate-to-sqlite-cache.md
  └── 0003-parallelize-type-enrichment.md
```

- File format: Markdown (`.md`)
- Naming pattern: `NNNN-short-descriptive-title.md` where `NNNN` is a sequential four-digit number starting at `0001`.

---

## 3. Standard RFC Template

Use this template when authoring an RFC:

```markdown
# RFC-[Number]: [Descriptive Proposal Title]

- Status: [Draft | Ready for Review | In Review | Approved | Rejected]
- Date: [YYYY-MM-DD]
- Author(s): [Names]
- Deciders/Reviewers: [Names of requested reviewers]
- ADR Reference: [Link to ADR-XXXX if approved]

## 1. Executive Summary
Provide a high-level summary of the proposal, the problem it addresses, and the recommended solution. Keep this to two or three sentences.

## 2. Context and Problem Statement
Explain the current situation, the technical constraints, and the specific pain points to solve. Outline user requirements or performance bottlenecks clearly.

## 3. Proposed Solution
Detail the technical design. Describe the architecture, API changes, package splits, or tooling requirements. Include diagrams or code blocks to clarify the implementation.

## 4. Discarded Alternatives
List other options considered and why they were rejected. Be specific about their limitations.

## 5. Supporting Materials and Prototypes
Document spikes, benchmark results, or code prototypes. Reference any temporary exploration code.

## 6. Open Questions
List unresolved issues or specific design points where you are seeking feedback.

## 7. References
Provide links to documentation, source code, or relevant technical articles.
```

---

## 4. Lifecycle States

An RFC progresses through five distinct states:

- Draft: The author is writing the proposal and it is not yet complete.
- Ready for Review: The proposal is complete and open for feedback.
- In Review: Active debate and refinement are ongoing.
- Approved: Technical consensus is reached, guiding future ADR creation.
- Rejected: The proposal was found to be unviable, and reasons for rejection are documented.
