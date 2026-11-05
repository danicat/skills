---
name: router
description: >
  Automatic model and thinking-effort router that dispatches tasks as headless
  agy CLI background jobs. Scores prompt complexity to choose between
  gemini-3.5-flash-lite, gemini-3.8-flash, and gemini-4-argon across low,
  medium, and high thinking levels while keeping the main chat unblocked.
  Activate on router, router(N), router(auto), /router, or when routing tasks
  to right-sized tiers and parallel worker counts.
license: Apache-2.0
metadata:
  category: workflows
  tags: "models, subagents, parallel, orchestration, dispatch, cost-optimization"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.1.0"
  catalog: https://skills.danicat.dev
---

# Automatic tier and effort router

Native subagent tools only expose coarse tiers and can't pin exact families or thinking effort levels. `router` solves this by acting as a non-blocking coordinator. It scores task complexity, picks the right tier and thinking level, and runs every worker only through the `agy` CLI.

```text
+-------------------------------------------------------------------------+
|                         ROUTER DISPATCH TOPOLOGY                        |
|                                                                         |
|                             ROOT COORDINATOR                            |
|           (Scores complexity -> Picks tier & effort -> Yields)          |
|                     /               |               \                   |
|                    v                v                v                  |
|         +------------------+ +------------------+ +------------------+  |
|         | agy CLI Worker 1 | | agy CLI Worker 2 | | agy CLI Worker N |  |
|         |  --model <tier>  | |  --model <tier>  | |  --model <tier>  |  |
|         |  --effort <lvl>  | |  --effort <lvl>  | |  --effort <lvl>  |  |
|         +------------------+ +------------------+ +------------------+  |
|                    \                |                /                  |
|                     v               v               v                   |
|                            REDUCE & RECONCILE                           |
|              (Read staged outputs, verify build/tests, deliver)         |
+-------------------------------------------------------------------------+
```

---

## ⚡ Run modes

Read the user's input to set the worker count (`DOP`):

| Input syntax | Worker count | Coordinator action |
| :--- | :--- | :--- |
| **`router`** *(or `/router`)* | `1` | Scores the current ask, picks the best `--model` and `--effort` flags, and starts **1 background `agy` worker** so the main chat stays unblocked. |
| **`router(N)`** *(or `/router N`)* | `N` | Picks the best `--model` and `--effort` flags for the ask and spins up **`N` concurrent `agy` workers** across disjoint slices or racing bets. |
| **`router(auto)`** *(or `/router auto`)* | `K` | Picks the best `--model` and `--effort` flags and computes the **right-sized worker count `K`** from the task's natural splits. |

### How `router(auto)` picks `K`

When called with `router(auto)`, count the independent work units `M`—such as files, packages, doc sections, search angles, or design bets—before starting workers:

- **`K = 1`: Single-file or tight state**: Use 1 worker when edits change a single file or share tight state where splitting causes merge conflicts.
- **`K = 2..4`: Focused parallel**: Use 2 to 4 workers when the ask splits cleanly into a few modules, test suites, or search angles, or 3 workers for best-of-3 design races.
- **`K = 5..8`: Broad sweep**: Use 5 to 8 workers for multi-package refactors, codebase-wide audits, or multi-section drafting (`K = min(M, 8)`).

---

## 🧠 Complexity scoring and tier routing

Before starting any worker, score the ask across four signals:

1. **Rule clarity**: Is the change mechanical with exact rules (`gemini-3.5-flash-lite`), a standard coding or writing task (`gemini-3.8-flash`), or an open-ended design problem (`gemini-4-argon`)?
2. **Blast radius**: Does it edit isolated text or one file (`gemini-3.5-flash-lite`), a module of 2 to 5 files (`gemini-3.8-flash`), or cross-cutting system contracts (`gemini-4-argon`)?
3. **Thinking depth**: Does it need direct pattern matching (`low`), multi-step logic and edge-case checks (`medium`), or deep trade-off proofs (`high`)?
4. **Error cost**: Are mistakes caught right away by syntax checks (`gemini-3.5-flash-lite`), unit tests (`gemini-3.8-flash`), or only by subtle runtime traces (`gemini-4-argon`)?

### The 9-tier routing matrix

Map the complexity score to one of the three `--model` families (`gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-4-argon`) and three `--effort` thinking levels (`low`, `medium`, `high`):

| `--model` family | `--effort` level | Scope band | Example tasks |
| :--- | :--- | :--- | :--- |
| **`gemini-3.5-flash-lite`** | `low` | **1. Trivial / Mechanical** | Format conversions, `regex` extraction, file renames, template stubs, log filtering, simple syntax fixes. |
| **`gemini-3.5-flash-lite`** | `medium` | **2. Structured / Single-file** | Transcript or doc summaries, filling templates, settings edits, drafting simple table-driven unit tests. |
| **`gemini-3.5-flash-lite`** | `high` | **3. Rule-bound / Batch** | Checking files against a strict checklist, mechanical multi-file renames, structured triage sweeps. |
| **`gemini-3.8-flash`** | `low` | **4. Standard / Direct** | Writing scoped functions or UI views, drafting doc sections, targeted codebase searches, clear bug fixes. |
| **`gemini-3.8-flash`** | `medium` | **5. Multi-file / Feature** | Standard feature builds across 2 to 5 files, package refactors, full unit test suites, research memos. |
| **`gemini-3.8-flash`** | `high` | **6. Deep module / Audit** | Fixing state or timing bugs, profiling bottlenecks, security and a11y audits, schema and API design. |
| **`gemini-4-argon`** | `low` | **7. Cross-cutting / Merge** | Cross-package refactors with shared rules, merging clashing research, reviewing complex RFCs or diffs. |
| **`gemini-4-argon`** | `medium` | **8. System design** | Designing distributed systems or compilers, solving hard algorithms, root-causing multi-layer bugs. |
| **`gemini-4-argon`** | `high` | **9. Frontier / High-stakes** | Proving concurrency safety, hunting zero-day flaws, untangling legacy migrations, best-of-N design races. |

### Mixed-tier routing for `router(N)` and `router(auto)`

When a parallel task has slices of unequal difficulty, give each worker its own right-sized tier instead of overpaying across the board. For instance, run `gemini-4-argon` (`high`) for the core state machine slice and `gemini-3.8-flash` (`low`) or `gemini-3.5-flash-lite` (`medium`) for test fixtures and docs.

---

## 🖥️ `agy` CLI dispatch rules

Apply the lessons from `parallel` to every `router` run:

1. **Never call `invoke_subagent`**:
   `invoke_subagent` can't select `gemini-3.5-flash-lite`, `gemini-3.8-flash`, or `gemini-4-argon` with `low`, `medium`, or `high` thinking levels. Always spawn workers via `run_command` using the `agy` CLI.
2. **Check live identifiers**:
   Run `agy models` once per session to check the exact IDs in the local CLI. Pass `--model <base-id> --effort <low|medium|high>` or a combined ID from `agy models` such as `gemini-3.8-flash-medium` or `gemini-4-argon-high`. If a target family is missing from `agy models`, fail fast and report the live list rather than falling back.
3. **Pass prompts inline with `-p="..."`**:
   In text mode, `agy -p` ignores standard input (`stdin`). Always pass the worker prompt inside `-p="..."`.
4. **Stop recursive expansion and permission hangs**:
   Always pass `--mode auto` so headless workers can run tools and edit assigned files without hanging on prompts. Pass `--disable-slash-commands` so file paths or slash tokens in `-p` never trigger recursive skill loading.
5. **Keep single-writer boundaries**:
   Never let two `agy` workers edit the same file at the same time. Give each worker an exclusive file list or have it write to an isolated staging file such as `/tmp/router-worker-01.md`.
6. **Fire and yield right away**:
   Start each worker with a separate `run_command` call using `WaitMsBeforeAsync: 500`. As soon as all `1` or `N` background commands start, share the routing plan with the user and **stop calling tools right away** to end your turn.

### Worker command template

```bash
agy --model gemini-3.8-flash \
  --effort medium \
  --mode auto \
  --disable-slash-commands \
  -p="You are Worker 1 of N.
Task slice: <exact scope and acceptance criteria>.
Owned files: <exclusive workspace paths or read-only rule>.
Write your completion summary and check log to /tmp/router-worker-01.md." \
  > /tmp/router-worker-01.out 2>&1
```

---

## 🔄 Non-blocking flow and Reduce steps

### 1. Dispatch checklist
- [ ] **Step 1: Parse mode and score complexity**
  Read `router`, `router(N)`, or `router(auto)`. Score the prompt across the 4 signals and pick the target `--model` (`gemini-3.5-flash-lite`, `gemini-3.8-flash`, or `gemini-4-argon`) and `--effort` (`low`, `medium`, or `high`).
- [ ] **Step 2: Split into disjoint slices or racing bets**
  For `DOP > 1`, split the work into `N` disjoint slices with exclusive file ownership, or give all `N` workers the same prompt when running a design race.
- [ ] **Step 3: Start background `agy` jobs and yield**
  Start each worker via `run_command` (`WaitMsBeforeAsync: 500`), print a short routing summary for the user, and **end your turn right away**.

### 2. In-flight task control
While background `agy` jobs run, the main session stays open for user messages:
- **Status check**: Run `manage_task` with `Action: "list"` or `Action: "status"` to check live worker progress, then yield the turn again.
- **Scope change or cancel**: Run `manage_task` with `Action: "kill"` to stop old workers and start updated `agy` jobs if needed.
- **Zero polling**: Never run `sleep` or poll `manage_task` in a loop. Wait for the runtime to wake the session when each background task finishes.

### 3. Reduce and check steps
Once all background `agy` jobs finish and wake the coordinator:
- [ ] **Step 1: Check exit codes and read staged outputs**
  Confirm every background task exited with code `0`. Read all `/tmp/router-worker-*.md` and `.out` files. If any worker failed, fail fast with its exact `stderr` log.
- [ ] **Step 2: Reconcile and clean up**
  Merge staged Markdown or wire module contracts together, confirm no `TODO` or stub placeholders remain, and delete temporary `/tmp/router-*` files.
- [ ] **Step 3: Verify and deliver**
  Run project build, lint, or test checks and present the final result with the routing scorecard below.

---

## 📄 Output template

```markdown
## 🧭 Routing scorecard
- **Mode**: `router` | `router(<N>)` | `router(auto -> <K> workers)`
- **Complexity score**: <1-sentence summary of clarity, blast radius, and thinking depth>
- **Selected tier(s)**: `<model>` (`--effort <low|medium|high>`)

| Worker | Assigned slice / role | Model | Thinking effort | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Worker 1** | <Slice or candidate 1> | `<model>` | `<low\|medium\|high>` | Completed |

## 📦 Synthesized result
<Consolidated deliverable, code summary, or reconciled findings>

## ✅ Verification
- **Checks run**: <Build, test, lint, or output audit commands>
- **Staging cleanup**: Removed `/tmp/router-*` temporary files.
```
