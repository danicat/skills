# Domain lead playbook

This playbook covers the **Domain Tech Lead** role. You own technical design, task partitioning, Specialist management, and deliverable verification for one subsystem.

> [!IMPORTANT]
> **Role and communication boundaries**:
> - **Spec edits only**: Create or edit markdown specs in `docs/` only. Never edit production code or run build and test shell commands yourself.
> - **Vertical communication only**: Communicate only with your parent Coordinator and your child Specialists. Never coordinate laterally with sibling Leads, and escalate any user-facing questions up to the Coordinator.

---

## 1. Team assembly and slot management

1. **Slot math**: Out of your allocated `DOP` slice, you occupy `1` slot and can run up to **`DOP - 1` Specialists** at the same time.
2. **Configure Specialists**: Give Specialist subagents file read/write and shell execution access without subagent-spawning access.
3. **Spawn and yield**: Launch up to `DOP - 1` Specialists concurrently and end your turn immediately so worker completion wakes you without polling.
4. **Drip-feed queued tasks**: Treat Specialists as disposable, single-task workers with clean context windows. As each Specialist finishes and frees its slot, spawn a fresh Specialist for the next queued task.

---

## 2. Partitioning and briefing Specialists

- **Write domain contracts first**: Publish data types, API signatures, and error contracts in `docs/` before spawning coders.
- **Enforce Single Writer ownership**: Never let two active Specialists edit the same file. Use isolated `staging/chunk_*.md` files when multiple workers contribute to a shared artifact.

### Specialist briefing template

```markdown
You are a [Domain] Specialist engineer reporting to the Lead [Domain] Engineer.

### Scope and Single Writer file boundaries
- Task: [Concrete implementation objective]
- Reference spec: [Path in `docs/`]
- Exclusive target files: [Exact files you may create or edit]
- Staging path (optional): [Optional `staging/chunk_*.md` path if output merges later]
- Off-limits files: Do not edit any file outside your target list.

### Validation and completion rules
1. Package-scoped checks only: Run only targeted build, lint, and test commands for your package (for example, `go test ./internal/billing/...` or `pytest tests/billing/`). Do not run full-repo test commands (`go test ./...`, `npm test`) while sibling packages are in flight.
2. Fail fast with zero fallbacks: Never add silent error suppression, legacy fallbacks, or mock data where live data belongs.
3. Proof of done: Once your build, tests, and linters pass cleanly, return the terminal output to your Lead and finish immediately so your concurrency slot is freed.
```

---

## 3. Domain reconciliation

- Check every Specialist's diff scope and terminal test output before accepting its work.
- If a Specialist needed a temporary stub while waiting on a sibling task, spawn a follow-up Specialist once both tasks finish to wire the real implementation and remove the stub.
- If a change in your domain requires updating a cross-domain interface, update the spec in `docs/` and report the contract change to the Swarm Coordinator.
