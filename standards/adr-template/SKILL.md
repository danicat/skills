---
name: adr-template
description: >
  Guide and template for authoring and maintaining Architecture Decision
  Records (ADRs). Captures structural decisions, background context, trade-offs,
  and compliance verification in lightweight, immutable markdown records to
  preserve engineering context. Activate when making significant architectural
  choices, documenting technical trade-offs, proposing major refactorings, or
  authoring ADRs.
license: Apache-2.0
metadata:
  category: standards
  tags: "adr, architecture, standards, documentation, design"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.1"
  homepage: https://skills.danicat.dev/standards/adr-template/
  canonical: https://skills.danicat.dev/standards/adr-template/SKILL.md
  repository: https://github.com/danicat/skills/tree/main/standards/adr-template
---

# Architecture Decision Records (ADRs)

Use this skill to write and maintain Architecture Decision Records (ADRs). ADRs are lightweight, plain-text files that capture architectural choices, their context, and their consequences.

---

## 1. Core Philosophy

Architecture consists of decisions that are hard to change. ADRs prevent two primary engineering problems:

- Context Loss: Future developers often struggle to understand why code was written a certain way, leading to regressions when they remove constraints they do not see. ADRs record the underlying rationale.
- Discussion Decay: ADRs capture the final conclusion and the forces that shaped it, rather than every detail of the debate.

---

## 2. Rules of ADRs

> [!IMPORTANT]
> - Keep ADRs lightweight. Limit each record to one or two pages. An ADR is a record of a decision, not a comprehensive design specification.
> - ADRs are immutable logs. Do not edit an approved and committed ADR. If a decision changes, write a new ADR and update the status of the old one to "Superseded by ADR-NNNN".
> - Document consequences and trade-offs. Every architectural choice has downsides. Explicitly list negative consequences, technical debt, and new constraints.

---

## 3. Directory and Naming Conventions

Store all ADRs in the project documentation folder:

```text
design/adr/
  ├── 0001-record-architecture-decisions.md
  ├── 0002-use-stdio-mcp-transport.md
  └── 0003-transactional-compiler-gated-editing.md
```

- File format: Markdown (`.md`)
- Naming pattern: `NNNN-short-descriptive-title.md` where `NNNN` is a sequential four-digit number starting at `0001`.

---

## 4. Standard ADR Template

Use this template when creating an ADR:

```markdown
# ADR-[Number]: [Active Verb Title]

- Status: [Proposed | Approved | Superseded by ADR-XXXX | Rejected]
- Date: [YYYY-MM-DD]
- Author(s): [Names]
- Deciders: [Names of participants in the decision]

## 1. Context
Describe the current situation, background context, and the problem to solve. What technical, organizational, or operational factors are at play? What constraints apply? State facts objectively.

## 2. Decision
State the chosen architectural path clearly. Explain why this path was selected over alternatives. List the other options considered and the reasons for rejecting them.

## 3. Consequences
Detail the impact of this decision. Explicitly list positive gains, negative trade-offs or constraints, and neutral structural shifts.

## 4. Compliance and Verification
How will the team verify that this decision is respected and implemented correctly? Detail the specific automated tests, pipeline checks, or manual hooks that enforce compliance.
```

---

## 5. Verification Checklist

Before finalizing an ADR, verify the following:

- [ ] Does the ADR clearly state the forces involved?
- [ ] Does it document the alternatives that were discarded?
- [ ] Is the tone objective and factual, avoiding unquantifiable words like "perfect", "flawless", or "elegant"?
