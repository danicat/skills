# Review & Architectural Feedback: KungFu CLI Reference Implementation

- **Review Target**: [`_design/spec/0001-kungfu-cli-specification.md`](../spec/0001-kungfu-cli-specification.md)
- **Author**: Antigravity Core Implementation Team (`github.com/danicat/kungfu`)
- **Recipient**: Agent Skills Catalog & Spec Architects (`../skills`)
- **Date**: 2026-08-22
- **Status**: Implemented & Proposed Alignment

---

## 1. Executive Summary & Implementation Status

The reference implementation of the **KungFu CLI** (`github.com/danicat/kungfu`) has been built in native Go 1.24, fully tested, and verified against the `agentskills.io` standard.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KUNGFU CORE IMPLEMENTATION STATUS                     │
├────────────────────────────────┬────────────┬───────────────────────────────┤
│ Spec Feature                   │ Status     │ Implementation Detail         │
├────────────────────────────────┼────────────┼───────────────────────────────┤
│ Sub-10ms Startup & Zero Dep    │ ✅ 100%    │ Native Go, zero cgo/heavy deps│
│ Strict Frontmatter Stripper    │ ✅ 100%    │ In-memory zero-alloc scanner  │
│ Hybrid BM25 + TF-IDF Search    │ ✅ 100%    │ Custom pure Go inverted index │
│ HTTP ETag Conditional Cache    │ ✅ 100%    │ ~/.cache/kungfu/ with retries │
│ Multi-Runtime Script Sandbox   │ ✅ 100%    │ PEP 723, uv, bun, node, bash  │
│ 3-Way State & Dirty Tracking   │ ✅ 100%    │ SHA-256 package digests       │
└────────────────────────────────┴────────────┴───────────────────────────────┘
```

---

## 2. Key Architectural Decisions & Uno-Reverse Simplifications

During implementation and agent ergonomics testing, we applied the **Uno-Reverse Simplification Principle** (avoiding speculative abstractions, eliminating cognitive friction for AI agents, and pruning redundant verbs). 

We present the following architectural feedback and refinements to the specification:

### 2.1 Primitive Collapsing: Universal Subpath Loading (`load` vs. `read` / `refs`)

* **SPEC-0001 Proposal (§3.4 & §3.7)**:
  - Restricted `kungfu load` strictly to `SKILL.md`.
  - Introduced a separate `kungfu read <skill/path>` command for companion references, scripts, and assets.
* **Implementation Finding & Refinement**:
  - Forcing AI agents to remember multiple retrieval verbs (`load` vs `read` vs `refs`) causes tool-calling confusion and hallucinations.
  - We unified content retrieval into **Strict Relative Subpath Addressing** under `kungfu load`:
    ```bash
    # Root Playbook (Tier 2)
    kungfu load buffer

    # Companion References, Scripts, Assets, Evals (Tier 3)
    kungfu load buffer/references/pitfalls.md
    kungfu load buffer/scripts/sync.py
    kungfu load buffer/assets/init.sql
    kungfu load buffer/evals/evals.json
    ```
  - **Zero Speculative Compatibility**: Because this is a greenfield v0.1 application, we avoid accumulating tech debt by maintaining redundant legacy aliases. `load` is the **only** verb for reading content; `run` is the **only** verb for script execution.

---

### 2.2 Separation of Concerns: Omission of `--tier1` / `--tier2` Flags on `load`

* **SPEC-0001 Proposal (§3.4)**:
  - Proposed `--tier1` flag on `load` to output only `name` and `description`.
* **Implementation Finding & Refinement**:
  - Tier 1 discovery (name, description, tags, category) is already cleanly handled by `kungfu show`, `kungfu find`, and `kungfu list --json`.
  - Adding `--tier1` / `--tier2` flags to `load` muddies its single responsibility. `kungfu load` strictly emits verbatim markdown instructions stripped of control metadata.

---

### 2.3 Centralized State Architecture (`state.json` vs. `.kungfu.lock`)

* **SPEC-0001 Proposal (§3.5)**:
  - Proposed creating a `.kungfu.lock` file in the root of every project workspace.
* **Implementation Finding & Refinement**:
  - Polluting user project roots with tool-specific lockfiles causes git noise and friction.
  - We implemented a centralized state manifest at `~/.config/kungfu/state.json`.
  - **Capabilities**:
    1. Tracks both workspace-local (`.agents/skills/`) and user-global (`~/.agents/skills/`) skills.
    2. Tracks cryptographic package digests (SHA-256) for 3-way dirty-state detection.
    3. Manages soft-deletes / uninstallations via `kungfu forget`.
    4. Records JIT load history and telemetry for offline auditing.

---

## 3. Pruned & Streamlined Command Taxonomy

We recommend updating Section 3 of SPEC-0001 to reflect the finalized 9-command suite:

| Command | Syntax | Primary Role |
| :--- | :--- | :--- |
| **`list`** | `kungfu list [-c <cat>] [-t <tags>] [--all]` | Catalog discovery & status table |
| **`find`** | `kungfu find <query> [-c <cat>] [-t <tags>]` | Hybrid ranking search |
| **`show`** | `kungfu show <skills...> [--json]` | Metadata, tools, preview, & auxiliary file index |
| **`load`** | `kungfu load <skill>[/<relpath>] [--raw] [--json]` | **Universal content streamer** (Root, Refs, Scripts, Assets) |
| **`learn`** | `kungfu learn <skills...> [-g] [-f] [--load]` | Atomic package installation to workspace or global |
| **`forget`** | `kungfu forget <skills...> [-g] [-f] [--all]` | Soft-delete / uninstall installed skills |
| **`update`** | `kungfu update [skills...] [-g] [--all] [-y]` | 3-way state diff & upstream sync |
| **`status`** | `kungfu status [skills...] [-g] [--json]` | State manifest, versions, and telemetry |
| **`run`** | `kungfu run <skill> <script> [args...]` | **Universal script execution gateway** |

---

## 4. Next Steps for SPEC-0001 Alignment

1. **Update SPEC-0001**: Merge the unified `load <skill>/<path>` syntax into §3.4 and remove the standalone `read` (§3.7) and `--tier1`/`--tier2` flags.
2. **Incorporate `forget` & `status`**: Add explicit specifications for uninstallation lifecycle and state inspection in §3.
3. **Align State Architecture**: Update §4 to document the centralized `~/.config/kungfu/state.json` structure.
