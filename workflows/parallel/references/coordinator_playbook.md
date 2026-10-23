# Coordinator Playbook & Operational Protocols

This reference guide provides the step-by-step operational protocol for the ROOT Coordinator agent executing under the `/parallel` skill.

---

## 1. The Coordinator Mandate

The Root Coordinator is an architectural director and workflow manager.

> [!IMPORTANT]
> **The Three Invariants of the Parallel Coordinator:**
> 1. **Immediate Yield (Hard Constraint)**: You MUST stop calling tools immediately after spawning workers so the user chat session remains unblocked and responsive.
> 2. **Delegation over Execution**: You MUST NEVER perform the execution tasks yourself (e.g., writing large production code, running full benchmark sweeps, doing deep web crawls). Subagents do the work; the Coordinator coordinates and synthesizes.
> 3. **Sole User Interface**: Subagents do not possess `ask_question`. All user clarifications must be routed through the Coordinator.

---

## 2. Invocation Parsing & Budget Calculation

When invoked with `/parallel`, parse the user's intent systematically:

```
+--------------------------------------------------------------------------+
|                       BUDGET RESOLUTION RULES                            |
|                                                                          |
|  Expression                              Calculated DOP / Action         |
|  ----------------------------------------------------------------------  |
|  /parallel 6                             DOP = 6                         |
|  /parallel dop: 8                        DOP = 8                         |
|  /parallel budget 4                      DOP = 4                         |
|  /parallel 3 planning, 8 execution       Phase 1: DOP = 3; Phase 2: 8    |
|  /parallel (no number provided)          Default DOP = 5 (or 10 if large)|
|  /parallel 1 (minimum budget)            DOP = 1 (spawns 1 worker subagent|
|                                          to keep main session unblocked!)|
+--------------------------------------------------------------------------+
```

### Budget Utilization Principle:
- It is strongly recommended to use the **full allocated budget** to maximize concurrency and throughput.
- At minimum, the task must use at least **1 subagent**. Even with `DOP = 1`, the Coordinator dispatches the task to a subagent and yields the turn, ensuring the main chat session remains unblocked for user interaction.

---

## 3. Subagent Definition & Dispatch Standards

When invoking workers via `invoke_subagent`:

```json
{
  "Subagents": [
    {
      "TypeName": "research",
      "Role": "Facet A Researcher",
      "Prompt": "Investigate ... Return findings via send_message to parent.",
      "Model": "inherit"
    }
  ]
}
```

### Mandatory Subagent Configuration Rules:
1. **Model Selection**: ALWAYS set `Model: 'inherit'`. Never hardcode a specific model name. This guarantees seamless model and reasoning effort inheritance.
2. **Explicit Output Contract**: Every worker prompt must instruct the subagent:
   - What specific slice or angle to investigate or build.
   - Where to write intermediate artifacts (e.g., `staging/worker_<id>.md`).
   - To send its final report back to the parent using `send_message`.
3. **No Sibling Messaging**: Workers do not know about other workers. They report strictly up to the parent.

---

## 4. The Fire-and-Yield Execution Step

After calling `invoke_subagent`, the Coordinator executes the following sequence:

```
[ Call invoke_subagent(Subagents=[...]) ]
                  |
                  v
[ Provide brief, clean user acknowledgement ]
  "Dispatched N parallel workers. Standing by for progress..."
                  |
                  v
[ STOP CALLING TOOLS IMMEDIATELY ]
  (Turn ends. Main session is completely unblocked.)
```

### DO NOT:
- Do NOT call `sleep` or schedule arbitrary timers to wait for workers.
- Do NOT call `manage_task(Action="status")` or poll in a loop.
- The messaging system will automatically wake the Coordinator when a worker calls `send_message`.

---

## 5. Reactive Event Handling

While workers execute in the background, the Coordinator will wake up on two distinct events:

### Event A: Subagent Progress or Completion Message
1. Ingest the worker's findings or verification logs.
2. Check off the completed subtask in the coordinator's internal state.
3. If more tasks remain in the backlog (`Tasks > DOP`), immediately dispatch the next task to a fresh worker.
4. If all tasks for the current phase are complete, trigger the **Reduce** step.
5. If the phase is part of a multi-phase pipeline, prepare and dispatch the next phase.

### Event B: User In-Flight Interruption or Steering
Because the main session is unblocked, the user may send messages at any time:

1. **Status Inquiry ("What's the status?", "How is it going?"):**
   - Call `manage_subagents(Action="list")` to inspect live states.
   - Present a concise, crisp progress report.
   - Yield turn immediately.
2. **Scope Revision ("Also look into aspect Z", "Prioritize Y"):**
   - If workers are already in-flight, send guidance via `send_message` or adjust the backlog.
   - If necessary, terminate obsolete workers via `manage_subagents(Action="kill")`.
3. **Cancellation ("Stop this"):**
   - Call `manage_subagents(Action="kill_all")`.
   - Acknowledge cancellation to user and yield.

### Event C: Subagent Escalation / Question
If a subagent encounters an ambiguous requirement:
1. Subagent sends message to Coordinator.
2. Coordinator evaluates whether user input is needed.
3. If yes, Coordinator calls `ask_question` to clarify with user.
4. Coordinator relays the user's answer back to the subagent via `send_message`.

---

## 6. The Reduce & Delivery Protocol

When all worker tasks conclude:

1. **Audit**: Verify all deliverables are present and free of dummy placeholders.
2. **Reconcile**: Merge staged files, wire modules, or build the synthesized comparison matrix.
3. **Validate**: If applicable, run verification checks (lint, build, unit test, link audit).
4. **Deliver**: Present the consolidated outcome to the user with a concise summary of parallel execution statistics:
   - Total workers executed.
   - Tasks completed.
   - Key findings / architectural deliverables.
