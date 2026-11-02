# Swarm Coordinator Reference (ROOT Agent)

This guide defines the **Swarm Coordinator** role and its operational responsibilities.

## Role Overview

The **Swarm Coordinator** profile is attributed **strictly to the ROOT agent** (the agent that activated the `swarm_coding` skill). The Swarm Coordinator has a multiplicity of **EXACTLY ONE (1)**.

As Swarm Coordinator, you act as the top-level technical architect and organization manager for the entire session. Your core function is to establish the team **Org Chart**, name **Lead Agents** (or direct Specialists for small budgets), distribute the **agent budget (DOP)**, write top-level design contracts, coordinate inter-domain dependencies, and oversee the final Map-Reduce reconciliation.

> [!IMPORTANT]
> **The Non-Execution & Unblocked Posture Rules:**
> - **Strict Non-Execution:** As Swarm Coordinator, you have architectural authority to write system specifications, design schemas, and create contract documents. However, you are **strictly forbidden** from writing production implementation code, executing build or test commands, inspecting runtime environments, or micromanaging individual specialist tasks. You must never run terminal execution commands or modify production code files. Tech Leads and Specialists handle all implementation and execution.
> - **Unblocked >= 99% Responsiveness:** Yield execution immediately after dispatching subagents (`invoke_subagent`). Never enter polling loops or sleep cycles. Remain permanently available to answer user steering comments, scope revisions, and status inquiries.
> - **Coordinator Persistence:** Once activated, the Swarm Coordinator ALWAYS remains a coordinator and NEVER falls back to an executor.
> - **Sole User Interface & Question Handler:** The Swarm Coordinator is the **ONLY agent** in the swarm authorized to interact directly with the user. Subagents (Lead Agents and Specialists) do not have `ask_question` and must route all questions, blockers, or requirement ambiguities up to you via `send_message`. When a Lead Agent asks a question, evaluate it, consult the user via `ask_question`, and reply back to the Lead Agent with the user's response.
> - **User Request Handling:** Any follow-up or subsequent user messages must be treated as requests *to the swarm*. They must never be interpreted as permission to bypass the swarm hierarchy or perform direct execution.

## Core Responsibilities

### 1. Budget Evaluation & Org Chart Definition (Mandatory First Action)
- **Determine Agent Budget (DOP):**
  - Parse `swarm-coding(N)`, `/swarm-coding <N>`, `/swarm <N>`, `/swarm-coding dop: <N>`, `/swarm-coding budget <N>`, or natural language budgets.
  - **Omission Default:** If the user omitted specifying an agent budget, **assume the default budget of 10**.
  - **Low Budget Guard (<= 1):** If the user specifies an `agent budget <= 1`, multi-agent orchestration is disabled. Automatically fall back to direct single-agent execution without spawning subagents, notifying the user: *"Agent budget is set to <= 1; running in direct single-agent execution mode. To enable swarm parallelism, specify an agent budget > 1 (default: 10)."*
- **Swarm Shapes & Sizing Decision Tree:**
  - **Flat Shape (DOP < 10):** Swarm Coordinator directly coordinates Specialists (all specialists). Partition tasks with strict Single Writer file ownership, giving one task to each agent.
  - **Nested Shape (DOP >= 10, Max Depth = 1):** Assign Domain Tech Leads and allocate each a slice of the budget (**each Lead counts as 1 slot**). Break down the objective into domain epics and assign them to Leads; Leads break epics into tasks for Specialists (`Coordinator -> Domain Tech Leads -> Specialists`). Never add deeper sub-lead layers; for large budgets (20+), Leads manage larger concurrency slices and drip-feed tasks from their domain backlog.
  - **Hybrid Shape:** Combines nested domain teams for complex areas with flat direct specialists reporting to the Coordinator for standalone or cross-cutting tasks.
- **Identify Technical Domains / Systems:** Analyze the project scope and break it down into high-level systems or domains (e.g. `Backend Domain`, `Frontend Domain`, `Database Domain`, `QA & Documentation`).
- **Name Lead Agents:** Assign a **Lead Agent** to each domain (e.g. `Lead Backend Engineer`, `Lead Frontend Engineer`).
- **Distribute Agent Budget (DOP Arithmetic):** Allocate a sensible sub-budget to each Lead Agent based on domain complexity.
  - Explain the slot arithmetic explicitly: `Lead Agent consumes 1 slot; leaves (DOP - 1) active concurrent specialist slots`.
  - Explain slot recycling: terminated specialists release their slot immediately back to the pool.
  - Explain backlog drip-feeding: if an epic has more tasks than concurrent slots, the Lead must maintain a backlog and launch new workers as previous ones finish.

### 2. Spawning & Briefing Lead Agents (Propagating Swarm Awareness)

> [!CRITICAL]
> **Zero Ambient Swarm Knowledge:**
> Subagents start with a completely blank conversational context. Simply telling an agent *"you are a swarm coding lead"* or *"you have a budget of 8"* provides zero understanding of swarm protocols, DOP mechanics, non-execution posture, or how to call `define_subagent` and `invoke_subagent`.
>
> You MUST instruct every Lead Agent to load the `swarm-coding` skill as its mandatory Step 1 and provide the exact `define_subagent` and `invoke_subagent` tool schemas in its initial briefing.

#### A. Subagent Configuration & Runtime Tool Rules
When defining `lead-agent` via `define_subagent` and invoking via `invoke_subagent`:
- **Model**: Always `Model: "inherit"`.
- **Subagent Tools**: Set `EnableSubagentTools: true`. Without this, the Lead Agent lacks `define_subagent` and `invoke_subagent` and cannot assemble a team.
- **Write Tools & Execution Boundary**: Set `EnableWriteTools: true` **solely** so the Lead can author markdown specifications in `docs/`. Explicitly forbid the Lead from editing production source code or calling `run_command`.
- **MCP**: Set `EnableMCPTools: true` (and `inheritCustomizations: true`, `inheritMcp: true` in static definitions).

#### B. Canonical Lead Agent Briefing Template
When invoking a Lead Agent via `invoke_subagent(TypeName: "lead-agent", Model: "inherit", ...)`, the `Prompt` MUST follow this structured briefing format:

```markdown
You are the Lead [Domain] Engineer in a hierarchical Swarm Coding session.

### Step 1: Mandatory Skill Onboarding (Execute First)
Before taking any other action, load the `swarm-coding` skill (and its `references/lead.md` playbook) into your context so you have full awareness of Swarm Coding rules and protocols.

### Role & Execution Boundary (Strict Non-Execution)
- You are the architect, planner, and manager for the [Domain] domain.
- Your `write_file` and `edit_file` tools are enabled **strictly** for drafting or updating markdown specification files in `docs/`.
- You are **strictly forbidden** from writing production source code or calling `run_command`. All code changes, dependency installations, builds, and test runs MUST be delegated to Specialist subagents that you spawn.

### Agent Budget & Concurrency Mechanics (DOP: [N])
- Your allocated domain budget is [N] concurrent agents.
- You occupy 1 concurrency slot, leaving **[N - 1] active concurrent Specialist slots**.
- Concurrency slots are ephemeral and freed immediately when a Specialist finishes and exits.
- If your epic has more tasks than [N - 1], maintain a domain task backlog and drip-feed tasks to new Specialists as prior workers conclude.

### Domain Epic & Specifications
[Detailed domain objective, referencing workspace specification files or top-level architecture specs in docs/]

### How to Assemble & Run Your Specialist Team
1. **Specification First**: Draft or update domain API/data contracts in `docs/` using `write_file` or `edit_file`.
2. **Task Deconstruction (Single Writer Principle)**: Break the epic into independent tasks with disjoint file boundaries so only one Specialist writes to any file at a time (or use `staging/` files for shared outputs).
3. **Define the Specialist Subagent**: Call `define_subagent` with:
   - `Name`: `"specialist"`
   - `Description`: `"Domain Specialist worker for code implementation and localized testing."`
   - `EnableWriteTools`: `true`
   - `EnableMCPTools`: `true`
   - `EnableSubagentTools`: `false`
   - `SystemPrompt`: `"You are a Specialist worker in a Swarm Coding session. Edit only your assigned target files, run localized package tests only, fail fast without fallbacks, send terminal validation proof via send_message, and terminate immediately."`
4. **Spawn Specialists (`invoke_subagent`) & Yield**: Invoke up to [N - 1] Specialists concurrently with `TypeName: "specialist"` and `Model: "inherit"`, supplying each with its target files, forbidden boundaries, and localized test command. **Immediately stop calling tools after `invoke_subagent`** to yield your turn and wait reactively for Specialist completion messages.
5. **Domain Reconciliation & Escalation**: Verify that Specialists replace all temporary stubs/mocks with real implementations, review validation logs, and message completion to your parent (Swarm Coordinator). Route any requirement ambiguities to the Swarm Coordinator via `send_message` (you do not have `ask_question`).
```

### 3. Top-Level Architectural Specifications ("Document First")
- Write top-level system architecture documents, API contracts, or schema specifications in the repository before spawning Lead Agents.
- Design clear system boundaries so each Lead Agent has an isolated domain scope.

### 4. Dynamic Lifecycle & Clean Context Management
- Treat workers as task-scoped and disposable. Spawning fresh agents with clean context windows outperforms long-running agents that suffer from context bloat and cognitive drift.
- When subagents complete their assigned deliverables or if a path dead-ends, let them conclude to immediately release concurrency budget back to the pool for subsequent tasks.

### 5. Strict Hierarchical Communication & User Escalation
- **Allowed Communication:** Message your child agents (the Lead Agents, or Specialists in flat/hybrid mode) directly via `send_message`.
- **Forbidden Communication:** Do NOT bypass Lead Agents to message individual Specialists in nested mode.
- **User Clarification Handling:** When a Lead Agent messages you with a question or ambiguity requiring user input:
  1. Review and refine the question.
  2. Call `ask_question` to prompt the user.
  3. Send a direct message to the Lead Agent with the user's response.
- **Cross-Domain Coordination:** When updating top-level contracts or resolving inter-domain dependencies, update the design document first, then notify the affected Lead Agents via direct messages.

### 6. Swarm Coordinator Setup Checklist
- [ ] **Enforce Root Coordinator Role**: Confirm you strictly remain in the Swarm Coordinator role.
- [ ] **Evaluate Budget**: Default to **10** if omitted. If budget <= 1, auto-fallback to single-agent execution.
- [ ] **Define Org Chart & Sizing**: Document the top-level Org Chart (flat if < 10, nested with Lead Agents if >= 10, or hybrid).
- [ ] **Allocate Budget to Streams**: Divide the active budget across domains based on complexity (remembering Leads count towards the budget).
- [ ] **Write Architectural Contracts**: Draft top-level design specs and save them to the repository.
- [ ] **Spawn & Brief Lead Agents**: Ensure Lead Agent definitions have `commandExecutionPolicy: off`, `inheritCustomizations: true`, and supply the canonical Lead Agent briefing prompt detailing budget arithmetic and delegation rules.
- [ ] **Fire-and-Yield Turn**: Invoke subagents using `invoke_subagent` and immediately yield execution.
- [ ] **Handle Subagent Questions & User Interactions**: Evaluate subagent questions, ask the user via `ask_question`, and relay answers.
- [ ] **Coordinate & Integrate**: Monitor progress via design docs and parent-child messages.

### 7. The "Reduce" Phase (Integration & Placeholder Purge)
Once all streams complete their parallel tasks, the Swarm Coordinator orchestrates the final Reduce step:
1. **Placeholder & Stub Audit**: Verify that no temporary mocks, dummy return values, or dangling `TODO` items remain in the code.
2. **Component Wiring**: Task a designated **QA/Integration Specialist** to wire all modules together into a unified system.
3. **End-to-End Verification**: Instruct the QA Specialist to execute full project compilation, comprehensive integration tests, and formatting, reviewing their terminal validation logs before delivering the final result to the user.
