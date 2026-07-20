---
name: swarm-coding
description: Activate this skill to tackle tasks using a divide to conquer approach with a swarm of sub-agents.
---
# Swarm Coding

Swarm Coding divides complex objectives among multiple specialized subagents. This divide-and-conquer strategy isolates context and improves response quality by keeping subagent tasks small and focused.

> [!NOTE]
> In this guide, the terms "agent" and "subagent" are used interchangeably.

### Core Principles

* **Single Responsibility:** Every agent maintains exactly one focus. Coordinators plan, design contracts, and integrate; specialists execute. They never cross roles.
* **Agent Budget:** The user defines a maximum budget (the limit of concurrent or total agents) when initiating the swarm.
* **Design Document Contracts:** Subagents working in parallel must use clear, shared design documents (e.g., API specifications) to establish firm contracts.
* **Continuous Documentation Sync:** Documentation is critical for parallel workflows. Any implementation change requires immediate impact analysis and documentation updates.

## Mechanics and Roles

Subagents in a Swarm Coding session assume one of two roles:

1. **Swarm Coordinator**: Acts as the technical lead for the swarm—breaking down complex tasks, planning high-level objectives, designing technical contracts/schemas, building teams, coordinating subagents, and integrating deliverables.
2. **Specialist**: Designs and implements a narrowly scoped task within their specific technical domain, adhering strictly to the coordinator's shared specifications.

Upon activation, you receive a ROLE and a TASK. If no role is specified, assume this is the initial activation and take the role of Swarm Coordinator.

#### Role References
- [references/coordinator.md](references/coordinator.md)
- [references/specialist.md](references/specialist.md)

## Task Complexity

* **Simple Tasks:** High technical certainty with a straightforward execution path suitable for a single team.
* **Complex Tasks:** Low technical certainty or multi-team requirements. These demand decomposition and coordination. High-uncertainty components may require a SPIKE (exploratory task) before execution.

## Team Composition

### Flat Teams (Simple Tasks)
Flat teams consist of one coordinator (acting as the tech lead) and one or more specialists. The minimum team composition requires:

* Root (Swarm Coordinator) x1
* Tech Writer (Specialist) x1

Every team MUST include a Tech Writer to maintain documentation in real time.

#### Example: Web Development Team (e.g., CRUD implementation)
* Root (Swarm Coordinator) x1
* Frontend Engineer (Specialist) x1
* Backend Engineer (Specialist) x1
* Test Engineer (Specialist) x1
* Tech Writer (Specialist) x1

#### Example: Game Development Team
* Root (Swarm Coordinator) x1
* UI/UX Designer (Specialist) x1
* Level/Gameplay Engineer (Specialist) x1
* Art Direction (Specialist) x1
* Sound Engineer (Specialist) x1
* Tester (Specialist) x1
* Tech Writer (Specialist) x1

> [!TIP]
> The Swarm Coordinator must customize team composition to fit the task. Do not treat these examples as rigid templates.

> [!TIP]
> Specialist multiplicity can be greater than one (e.g., Backend Engineer x2) to achieve a greater degree of parallelism, or to assign competing exploratory tasks when evaluating alternative solutions.

### Nested Teams (Complex Tasks)
For complex tasks, the coordinator decomposes objectives into smaller sub-tasks and delegates them to **Lead Agents**. Lead Agents act as coordinators for their sub-swarms and receive an allocated portion of the total agent budget.

## Exploratory Tasks (SPIKEs)

An exploratory task (SPIKE) is characterized by low technical certainty, requiring research, alternative comparison, or prototype evaluation before execution.

### SPIKE Sandbox and Rules:
1. **Timeboxed Search:** The Coordinator must set a strict agent budget and scope boundaries to prevent open-ended searching.
2. **User-Assisted Sandboxing:** For exploratory tasks that require coding, the Specialist **must explicitly request user support to set up an isolated sandbox, ideally on a dedicated `spike/` git branch**.
3. **Sandbox Isolation:** Specialists are strictly forbidden from committing to or merging with the main production branch. All prototype coding must remain isolated within the designated spike branch.
4. **Artifact Exit Criteria:** A SPIKE must conclude with:
   - Evaluated benchmarks or research notes saved in the scratch folder.
   - A synthesized Technical Specification (such as an RFC or ADR) detailing high-certainty, actionable tasks ready for subsequent execution swarms.