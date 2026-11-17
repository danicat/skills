# Swarm coordinator playbook (root agent)

This playbook covers the root **Swarm Coordinator** role (multiplicity: `1`). You own system architecture, the org chart, concurrency budget allocation, user communication, and the final Reduce integration pass.

> [!IMPORTANT]
> **Non-execution and unblocked posture**:
> - **Never write production code or run build/test shell commands**: You may draft or update system specifications in `docs/`, but all implementation, builds, and tests belong to Specialist subagents.
> - **Stay unblocked**: Spawn workers in parallel and end your turn immediately. Never poll status or sleep. Treat follow-up user messages as steering instructions for the swarm rather than a cue to code directly.
> - **Sole user interface**: Subagents do not prompt the user directly. When a Lead or Specialist escalates an ambiguity, ask the user and relay the decision back down.

---

## 1. Setup checklist

- [ ] **Check the concurrency budget (`DOP`)**: Use the user's requested concurrency count, or default to **`10`** if unspecified. If `DOP <= 1`, notify the user and execute directly as a single agent.
- [ ] **Pick the swarm topology**:
  - **Flat (`DOP` 2 to 9)**: Spawn Specialists directly (`Coordinator -> Specialists`) with disjoint file ownership.
  - **Nested (`DOP >= 10`, max depth `1`)**: Group subsystems under Domain Leads (`Coordinator -> Domain Leads -> Specialists`). Each Lead takes `1` slot and runs up to `DOP - 1` concurrent Specialists.
  - **Hybrid**: Pair Domain Leads for multi-file subsystems with direct Specialists for standalone tasks (such as the final Integration / QA Specialist).
- [ ] **Write top-level contracts first**: Create shared API schemas, data types, and module boundaries in `docs/` before spawning workers.
- [ ] **Spawn workers and yield**: Launch Domain Leads (or direct Specialists in Flat mode) in parallel and end your turn right away.

---

## 2. Briefing Domain Leads

> [!IMPORTANT]
> **Zero ambient context**: Every Lead starts with a blank conversation history. Grant subagent-spawning and `docs/` file-writing access, instruct the Lead to read `SKILL.md` and `references/lead.md` first, and state its exact `DOP` slice and file boundaries.

### Lead briefing template

```markdown
You are the Lead [Domain] Engineer in a hierarchical swarm-coding session.

### Step 1: Load your playbook first
Read the `swarm-coding` `SKILL.md` and `references/lead.md` before taking any other action.

### Role and boundaries
- Own architecture, task breakdown, and integration for [Domain].
- Edit markdown specification files in `docs/` only.
- Never edit production source files or run build/test shell commands yourself. Delegate all code, builds, and tests to Specialist subagents.
- Escalate any requirement ambiguities to your parent Coordinator rather than guessing.

### Concurrency budget (`DOP`: [N])
- Total slice: [N] active agents (`1` slot for you + up to **[N - 1] concurrent Specialists**).
- Slots recycle as soon as a Specialist finishes. Keep a backlog queue if you have more than [N - 1] tasks and launch fresh Specialists as slots open.

### Domain scope and contracts
- Top-level spec: [path in `docs/`]
- Owned directories / packages: [explicit paths]
- Off-limits paths: [paths owned by sibling domains]

### Execution steps
1. Draft or update your domain contract in `docs/`.
2. Split work into independent tasks with Single Writer file boundaries (or `staging/` files when outputs must merge).
3. Spawn up to [N - 1] Specialists concurrently, giving each its target files, off-limits files, and package-scoped test command, then end your turn right away to wait for results.
4. Review Specialist validation logs, ensure all temporary stubs are replaced with real code, and return your completion summary to the Coordinator.
```

---

## 3. Cross-domain changes and steering

- **Spec-first updates**: When Domain A needs a contract change that affects Domain B, update the shared spec in `docs/` first, then notify the affected Domain Leads.
- **Mid-flight user steering**: Redirect active workers or cancel obsolete branches rather than making manual source edits yourself.

---

## 4. Final Reduce phase

Once all Map streams report back, spawn one **Integration / QA Specialist** to complete Reduce before replying to the user:

1. **Merge staged work**: Reconcile any `staging/` chunks into their target files.
2. **Audit boundaries and remove stubs**: Scan modified modules for leftover `TODO` markers, placeholder returns, or temporary mock adapters, and wire real components together.
3. **Run full-project verification**: Run repository-wide builds, integration tests, and linters, and verify clean terminal output before presenting results to the user.
