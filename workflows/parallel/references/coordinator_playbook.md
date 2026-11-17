# Coordinator playbook and operational protocols

This guide covers the step-by-step operational protocol for the Root Coordinator running the parallel workflow.

---

## 1. The Coordinator mandate

The Root Coordinator is an architectural director and workflow manager.

> [!IMPORTANT]
> **The three invariants of the parallel Coordinator:**
> 1. **Immediate Yield (Hard Constraint):** End your turn immediately after dispatching workers so the main chat session remains unblocked and responsive.
> 2. **Delegation over Execution:** Never perform heavy execution directly (such as writing bulk production code, running long benchmark sweeps, or crawling large doc sets). Subagents execute; the Coordinator plans, dispatches, and reconciles.
> 3. **Sole User Interface:** Subagents never prompt the user directly. Route all user clarifications through the Coordinator.

---

## 2. Budget resolution and auto sizing

Resolve the user's requested concurrency budget (`DOP`) before slicing the task:

| User Specification | Resolved DOP / Action |
| :--- | :--- |
| **Numeric budget** (`DOP = 6`, `budget 4`, `6 workers`) | `DOP = N` |
| **Automatic sizing** (`parallel(auto)`, `DOP = auto`, keyword `auto`) | Coordinator selects optimal `DOP` balancing orthogonality, isolation, and cost |
| **Multi-phase budget** (`plan with DOP 3, build with 8`, or `plan with auto, build with 10`) | Phase-specific `DOP` applied at each stage barrier |
| **No budget specified** | Resolve using `auto` (typically `3` to `5` workers, or `8` to `10` for large codebases) |
| **Minimum budget** (`DOP = 1`) | Spawns `1` worker subagent so the main session remains unblocked |

### `parallel(auto)` sizing procedure

When `DOP` is set to `auto` (via `parallel(auto)`, `DOP = auto`, or an omitted count):
1. **Find natural orthogonal slices:** Count distinct modules, files, research facets, or chapters that have no shared write targets.
2. **Preserve context isolation:** Keep noisy reads, deep logs, or competing designs in separate workers so one slice does not pollute another.
3. **Avoid over-splitting:** Merge tiny or tightly coupled micro-tasks into a single worker whenever dispatch and Reduce overhead would outweigh parallel speedup.
4. **Declare your chosen `DOP`:** Briefly state the chosen worker count and rationale when acknowledging dispatch to the user.

### Budget utilization rule
- When the user sets an **explicit numeric `DOP`**, use the full allocated budget whenever enough independent slices exist.
- At minimum, delegate to **1 subagent** (`DOP >= 1`) so the Coordinator session never blocks on inline execution.

---

## 3. Worker briefing and dispatch standards

Dispatch parallel workers concurrently using clear, self-contained briefings:

```markdown
Role: [Specific Slice Role, e.g., Facet A Researcher or Package Author]
Slice Scope: [Exclusive topic facet, module, or target file paths]
Off-Limits Paths: [Everything outside assigned slice]
Output File: Write full findings, raw logs, or staged draft to staging/worker_<id>.md
Return Summary (< 2,000 chars):
- Status: pass, fail, or blocked
- Output file path on disk
- Must-Keep Mental Models and Deal-Breakers (concise bullets)
```

### Mandatory worker configuration rules
1. **Model Inheritance:** By default, workers inherit the parent session's model, reasoning effort, and workspace capabilities unless the user explicitly asks for a specific tier.
2. **Two-Tier Output Contract:** Workers save exhaustive outputs, logs, or staged drafts to disk (`staging/worker_<id>.md`) and return only a compact status summary (`< 2,000` characters) to the Coordinator.
3. **No Sibling Messaging:** Workers operate independently and communicate only upward to the Coordinator.

---

## 4. The fire-and-yield execution step

After launching workers, execute this sequence cleanly:

```text
[ Dispatch N parallel worker briefings ]
                  |
                  v
[ Post brief user acknowledgement ]
  "Dispatched N parallel workers (DOP = N). Standing by for results..."
                  |
                  v
[ STOP CALLING TOOLS IMMEDIATELY ]
  (Turn ends. Main session stays completely unblocked.)
```

### Never do
- Never run `sleep`, busy-wait timers, or synchronous polling loops while waiting for workers.
- Never check worker status in a tight loop; rely on reactive wakeups when workers finish.

---

## 5. Reactive event handling

While workers run in the background, the Coordinator responds to three event types:

### Event A: worker completion or progress update
1. Ingest the worker's summary and verify the output file on disk.
2. Mark the completed slice in your internal tracking list.
3. If queued items remain (`Tasks > DOP`), launch a fresh worker for the next slice.
4. Once all phase tasks finish, run the **Reduce** phase.
5. If part of a multi-phase pipeline, verify the stage barrier and dispatch the next phase.

### Event B: user in-flight interruption or steering
Because the main session stays unblocked, the user can send messages mid-run:

1. **Status inquiry (`"What is the status?"`):** Inspect active worker states, present a crisp summary, and yield immediately.
2. **Scope revision (`"Also inspect Z"`, `"Prioritize Y"`):** Redirect active workers or update remaining queued slices; cancel obsolete tasks if needed.
3. **Cancellation (`"Stop this"`):** Cancel all running workers, confirm cancellation to the user, and yield.

### Event C: worker escalation or ambiguity
If a worker hits a missing decision or requirement conflict:
1. Worker pauses and reports the ambiguity upward to the Coordinator.
2. Coordinator checks existing workspace files and specs to see whether the answer is already on disk.
3. If user judgment is genuinely needed, Coordinator asks the user directly and relays the decision back to the worker.

---

## 6. The Reduce and delivery protocol

When all workers finish:

1. **Audit deliverables:** Verify that all expected output files exist on disk and contain no leftover placeholders (`TODO`, `FIXME`, or stubs).
2. **Reconcile Must-Keep models:** Check off every worker's `Must-Keep Mental Models and Deal-Breakers` bullets so critical constraints are not lost during synthesis.
3. **Merge and integrate:** Assemble staged files into the final target, wire modules together, or compile the comparison matrix.
4. **Validate:** Run integrated build, test, lint, or link verification across the combined output.
5. **Deliver:** Present the final verified result with concise execution stats (workers deployed, slices completed, and key findings).
