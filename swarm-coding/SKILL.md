---
name: swarm-coding
description: >
  Use this skill when executing complex, multi-component engineering tasks, large-scale refactorings, or full-stack features that can be decomposed into parallelizable work. Trigger immediately for: full-stack development (frontend + backend), multi-service integrations, complex database migrations, API contract designs, or high-ambiguity technical challenges requiring dedicated research (SPIKEs). Do NOT use for simple, isolated single-file edits, minor bug fixes, or basic script modifications where spawning subagents would introduce unnecessary communication overhead.
license: Apache-2.0
metadata:
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
---
# Swarm Coding

Swarm Coding divides complex objectives among multiple specialized subagents. This divide-and-conquer strategy isolates context and improves response quality by keeping subagent tasks small and focused.

> [!NOTE]
> In this guide, the terms "agent" and "subagent" are used interchangeably.

### Core Principles

* **Single Responsibility:** Every agent maintains exactly one focus. Coordinators plan, design contracts, and integrate; specialists execute. They never cross roles.
* **Parallelization Safety:** Subagents working in parallel are strictly forbidden from writing to the same file concurrently. All target file allocations must be isolated to prevent git merge conflicts and code overwrites.
* **Agent Budget:** The maximum number of concurrent or total agents allowed for the swarm.
  - If specified by the user, the budget is exactly as requested.
  - If NOT specified, the budget is the smallest of 10 or the number of task granules (the atomic functional/engineering requirements explicitly listed or implied in the user request).
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

## Team Hierarchy and Budget Allocation

The Swarm Coordinator MUST define the team hierarchy as the very first step before starting any task planning.

The team hierarchy is a sensible function of the agent budget and the task complexity, allowing the coordinator flexibility in allocating the budget:
* **Low Budget / Simple Tasks:** Prefer flat team structures consisting of a team lead (coordinator) and executor agents (specialists).
* **High Budget / Complex Tasks:** Utilize nested team structures with Lead Agents who act as coordinators for their own sub-swarms, receiving an allocated portion of the overall budget.
* **Vague Flexibility:** The exact allocation and structure are purposely flexible, allowing the Swarm Coordinator to adapt the organization dynamically to fit the technical demands of the task.

## Team Composition

### Team Size Limits
* **Maximum Size:** No individual team (including sub-teams or sub-swarms) should have more than 6 agents, including the team lead.
* **Minimum Size:** The absolute minimal team composition is one team lead (coordinator) and one executor agent (specialist).

### Specialist Roles
Teams consist of a coordinator and various specialist executor roles.
* **Technical Writers:** There is no hard requirement to include a Tech Writer on every team, but it is strongly recommended that one is always included to maintain documentation and sync contracts in real time.

#### Example: Web Development Team (e.g., CRUD implementation)
* Root (Swarm Coordinator) x1
* Frontend Engineer (Specialist) x1
* Backend Engineer (Specialist) x1
* Test Engineer (Specialist) x1
* Tech Writer (Specialist) x1 (Strongly Recommended)

#### Example: Game Development Team (6-agent limit compliant)
* Root (Swarm Coordinator) x1
* UI/UX Designer & Art Direction (Specialist) x1
* Level/Gameplay Engineer (Specialist) x1
* Sound Engineer (Specialist) x1
* Tester (Specialist) x1
* Tech Writer (Specialist) x1 (Strongly Recommended)

> [!TIP]
> The Swarm Coordinator must customize team composition to fit the task. Do not treat these examples as rigid templates.

> [!TIP]
> Specialist multiplicity can be greater than one (e.g., Backend Engineer x2) to achieve a greater degree of parallelism, or to assign competing exploratory tasks when evaluating alternative solutions, provided the individual team size does not exceed 6 agents.

### Nested Teams (Complex Tasks)
For complex tasks and larger budgets, the coordinator decomposes objectives into smaller sub-tasks and delegates them to **Lead Agents**. Lead Agents act as coordinators for their sub-swarms and receive an allocated portion of the total agent budget. Each nested sub-swarm must adhere to the same team size limits and composition rules.

## Exploratory Tasks (SPIKEs)

An exploratory task (SPIKE) is characterized by low technical certainty, requiring research, alternative comparison, or prototype evaluation before execution.

### SPIKE Sandbox and Rules:
1. **Timeboxed Search:** The Coordinator must set a strict agent budget and scope boundaries to prevent open-ended searching.
2. **User-Assisted Sandboxing:** For exploratory tasks that require coding, the Specialist **must explicitly request user support to set up an isolated sandbox, ideally on a dedicated `spike/` git branch**.
3. **Sandbox Isolation:** Specialists are strictly forbidden from committing to or merging with the main production branch. All prototype coding must remain isolated within the designated spike branch.
4. **Artifact Exit Criteria:** A SPIKE must conclude with:
   - Evaluated benchmarks or research notes saved in the scratch folder.
   - A synthesized Technical Specification (such as an RFC or ADR) detailing high-certainty, actionable tasks ready for subsequent execution swarms.

## Gotchas

* **Under-Utilization Mismatch:** Spawning too few agents or executing granular tasks sequentially when the agent budget and parallelizable workload allow for concurrent execution. This underutilizes the swarm's capabilities and prolongs feedback loops.
* **Over-Utilization Overhead:** Spawning too many subagents for straightforward or highly coupled sequential tasks. Approaching budget ceilings without architectural justification introduces heavy coordination overhead and wastes resources.
* **Disposable Asset Pitfall (Context Loss):** Treating subagents as disposable, single-use resources rather than persistent team members. Terminating subagents prematurely and spawning fresh ones for related tasks destroys accumulated context and wastes setup overhead. Active subagents should be aggressively reused across aligned technical domains.