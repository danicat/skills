# Architectural Decision Records (ADRs)

Documenting architectural decisions helps teams track choices and maintain codebases over time. Use this template to record major design choices.

## ADR Template

```markdown
# [Short Title, e.g., Use Postgres for Metadata]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** [YYYY-MM-DD]
**Author:** [Name]

## Context
[Describe the problem or opportunity. What options were considered? Why is a decision needed now?]

## Decision
[Describe the decision clearly. "We will use X to do Y."]

## Consequences
**Positive:**
*   [Benefit 1]
*   [Benefit 2]

**Negative:**
*   [Drawback 1]
*   [Drawback 2]

**Risks:**
*   [Risk 1]
```

## Criteria for Writing an ADR

Create an ADR when:
*   Selecting or changing a database or storage engine.
*   Choosing a major framework (such as Echo versus Gin).
*   Defining a new API standard.
*   Introducing a dependency that significantly affects build size or codebase complexity.

