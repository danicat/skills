# RFC-0001: Turtle Local Locked-Checkout Version Control System

- Status: Rejected
- Date: 2026-07-24
- Author(s): Daniela Petruzalek (daniela@danicat.dev)
- Deciders/Reviewers: Daniela Petruzalek (daniela@danicat.dev)
- ADR Reference: N/A

## 1. Executive Summary
This RFC documents the design, implementation, pros, cons, and current limitations of **Turtle**, a lightweight, serverless local locked-checkout Version Control System (VCS) designed to prevent file-write conflicts in multi-agent parallel workspaces. Due to the high coordination overhead and limitations of locked-checkout VCS in optimistic modern coding pipelines, this proposal is documented and shelved as **Rejected** (Not Production Ready) for the time being.

## 2. Context and Problem Statement
When autonomous agents run in parallel in a single workspace, they frequently attempt to modify the same files concurrently. This leads to file-overwrite bugs, Git merge conflicts, and code duplication. Standard OS-level locking (like `flock`) is transient and does not persist across separate agent execution turns (which run as separate short-lived processes).

To prevent concurrent file writes, we proposed and prototyped a local locked-checkout mechanism named **Turtle** (in homage to TortoiseCVS/RCS) to lock files as read-only by default and require exclusive checkout locks for editing.

## 3. Proposed Solution & Prototype
The proposed solution implements a completely offline, serverless CLI utility `turtle.py` in standard Python. It uses file system read-only permissions (`0o444`) to protect files, combined with a central state metadata tracker `.turtle/metadata.json` to manage lock ownership.

### Workflows:
1. **`activate`**: Root coordinator locks all tracked project files as read-only, establishing a baseline.
2. **`checkout <file> --agent <id>`**: Backs up the file, assigns the lock to `<id>`, and makes the file writable.
3. **`commit <file>`**: Releases the lock, deletes the backup, and relocks the file as read-only.
4. **`cancel <file>`**: Restores the file from backup, releases the lock, and relocks the file as read-only.
5. **`deactivate`**: Validates that no dirty locks exist, releases global locks, and restores all files to their original permissions and write access.

---

## 4. Discussion: Pros, Cons, and Limitations

### Pros:
- **Offline & Serverless**: Operates purely on the local file system without network dependencies or daemon server processes.
- **Turn-Persistent Locks**: Unlike OS `flock` (which expires when the process terminates), Turtle's permissions-based and JSON-metadata-based locks persist across multiple agent turns and system reboots.
- **Strict Write Prevention**: Read-only attributes (`chmod 444`) provide real enforcement, preventing accidental writes from common editors or agent write APIs without checking out the file first.
- **Original Permission Preservation**: Correctly captures, stores, and restores the original permissions of files (such as keeping executable flags `0o755` intact on scripts).
- **Safe Undo (Rollbacks)**: Backups are automatically stored during checkout, ensuring a clean state restore if a task is cancelled.

### Cons:
- **No Concurrent Editing (Pessimistic Lockout)**: If two developers or agents need to edit the same file, they are entirely blocked from doing so in parallel. They must execute sequentially, which can slow down progress in multi-agent environments.
- **Easily Bypassed**: Any process or user with write/chmod permissions can easily bypass the read-only flag manually (e.g. `chmod 644 file`), making lock enforcement co-operative rather than secure.
- **Path and Rename Sensitivity**: Moving or renaming files outside Turtle CLI commands breaks lock metadata and orphans entries.
- **No Remote synchronization**: Bound strictly to a single machine workspace, making it unviable for multi-node agent grids.
- **Atomic Deactivation Risk**: If a sub-team or agent prematurely runs `deactivate`, it unlocks all workspace files and risks exposing or rolling back concurrent checkouts belonging to other agents.

---

## 5. Supporting Materials: The Turtle Script Prototype

Below is the complete executable prototype of `turtle.py` saved for historical reference:

```python
#!/usr/bin/env python3
"""
Turtle Version Control System (VCS) Prototype
Saved as reference for RFC-0001.
"""

import os
import sys
import json
import stat
import shutil
import argparse
import fnmatch
from pathlib import Path
from datetime import datetime

def find_project_root():
    curr = Path.cwd().resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / '.turtle').is_dir() or (parent / '.git').is_dir():
            return parent
    return curr

def load_gitignore_patterns(root):
    patterns = {
        ".git", ".turtle", ".DS_Store", "node_modules",
        "__pycache__", ".pytest_cache", ".venv", "venv", "env"
    }
    gitignore_path = root / ".gitignore"
    if gitignore_path.is_file():
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore: {e}", file=sys.stderr)

    turtleignore_path = root / ".turtleignore"
    if turtleignore_path.is_file():
        try:
            with open(turtleignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)
        except Exception as e:
            print(f"Warning: Could not read .turtleignore: {e}", file=sys.stderr)

    return patterns

def is_ignored(path, root, ignore_patterns):
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        return True

    parts = rel_path.parts
    for part in parts:
        if part in ignore_patterns:
            return True

    rel_str = str(rel_path)
    for pat in ignore_patterns:
        if fnmatch.fnmatch(rel_str, pat) or fnmatch.fnmatch(rel_str + "/", pat):
            return True

    return False

def load_metadata(root):
    meta_path = root / ".turtle" / "metadata.json"
    if not meta_path.is_file():
        return {"version": "1.0.0", "active": False, "files": {}, "locks": {}}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}", file=sys.stderr)
        sys.exit(1)

def save_metadata(root, data):
    meta_path = root / ".turtle" / "metadata.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving metadata: {e}", file=sys.stderr)
        sys.exit(1)

def make_readonly(path, original_mode):
    try:
        readonly_mode = original_mode & ~stat.S_IWRITE & ~stat.S_IWGRP & ~stat.S_IWOTH
        os.chmod(path, readonly_mode)
    except Exception as e:
        print(f"Warning: could not make {path} read-only: {e}", file=sys.stderr)

def make_writable(path, original_mode):
    try:
        os.chmod(path, original_mode)
    except Exception as e:
        print(f"Warning: could not make {path} writable: {e}", file=sys.stderr)

def cmd_init(args=None):
    root = find_project_root()
    turtle_dir = root / ".turtle"
    turtle_dir.mkdir(parents=True, exist_ok=True)
    (turtle_dir / "backups").mkdir(parents=True, exist_ok=True)

    data = load_metadata(root)
    ignore_patterns = load_gitignore_patterns(root)

    print(f"Initializing Turtle repository at: {root}")
    count = 0
    for p in root.rglob("*"):
        if p.is_file():
            if is_ignored(p, root, ignore_patterns):
                continue

            rel_path = str(p.relative_to(root))
            if rel_path not in data["files"]:
                orig_mode = stat.S_IMODE(p.stat().st_mode)
                data["files"][rel_path] = {
                    "mode": orig_mode
                }
            count += 1

    save_metadata(root, data)
    print(f"Successfully tracked {count} files under Turtle.")
    return root, data

def cmd_activate(args):
    root, data = cmd_init()
    data["active"] = True

    for f_rel, file_info in data["files"].items():
        f_path = root / f_rel
        if f_path.is_file():
            make_readonly(f_path, file_info["mode"])

    save_metadata(root, data)
    print("Turtle workspace activated. All tracked files are now locked as read-only.")

def cmd_deactivate(args):
    root = find_project_root()
    data = load_metadata(root)

    locks = data.get("locks", {})
    if locks:
        print("Warning: There are currently checked out (dirty) files in the workspace:", file=sys.stderr)
        for f, info in locks.items():
            print(f" - {f} (Agent: {info['agent']})", file=sys.stderr)

        if not args.force:
            print("Error: Deactivation aborted due to dirty files. Commit, cancel, or run with --force to discard.", file=sys.stderr)
            sys.exit(1)

        print("Force deactivation requested. Cancelling all active checkouts...")
        for f_rel in list(locks.keys()):
            class MockArgs:
                file = str(root / f_rel)
            cmd_cancel(MockArgs())

        data = load_metadata(root)

    data["active"] = False
    for f_rel, file_info in data["files"].items():
        f_path = root / f_rel
        if f_path.is_file():
            make_writable(f_path, file_info["mode"])

    save_metadata(root, data)
    print("Turtle workspace deactivated. Original permissions restored.")

def cmd_checkout(args):
    root = find_project_root()
    file_path = Path(args.file).resolve()
    if not file_path.is_file():
        print(f"Error: File does not exist: {args.file}", file=sys.stderr)
        sys.exit(1)

    rel_path = str(file_path.relative_to(root))
    data = load_metadata(root)

    if not data.get("active", False):
        data["active"] = True

    if rel_path in data["locks"]:
        lock_info = data["locks"][rel_path]
        print(f"Error: File {rel_path} is already checked out by agent '{lock_info['agent']}'...", file=sys.stderr)
        sys.exit(1)

    backup_path = root / ".turtle" / "backups" / rel_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)

    if rel_path not in data["files"]:
        orig_mode = stat.S_IMODE(file_path.stat().st_mode)
        if not (orig_mode & stat.S_IWRITE):
            orig_mode |= stat.S_IWRITE
        data["files"][rel_path] = {"mode": orig_mode}

    agent_id = args.agent or os.environ.get("AGENT_ID", "default-agent")
    data["locks"][rel_path] = {
        "agent": agent_id,
        "time": datetime.now().isoformat()
    }

    make_writable(file_path, data["files"][rel_path]["mode"])
    save_metadata(root, data)
    print(f"Checked out and unlocked {rel_path} (Agent: {agent_id}).")

def cmd_commit(args):
    root = find_project_root()
    file_path = Path(args.file).resolve()
    rel_path = str(file_path.relative_to(root))
    data = load_metadata(root)

    if rel_path not in data["locks"]:
        print(f"Error: File {rel_path} is not checked out.", file=sys.stderr)
        sys.exit(1)

    backup_path = root / ".turtle" / "backups" / rel_path
    if backup_path.is_file():
        backup_path.unlink()

    data["locks"].pop(rel_path)

    if data.get("active", False):
        make_readonly(file_path, data["files"][rel_path]["mode"])
    else:
        make_writable(file_path, data["files"][rel_path]["mode"])

    save_metadata(root, data)
    print(f"Committed changes for {rel_path}.")

def cmd_cancel(args):
    root = find_project_root()
    file_path = Path(args.file).resolve()
    rel_path = str(file_path.relative_to(root))
    data = load_metadata(root)

    if rel_path not in data["locks"]:
        print(f"Error: File {rel_path} is not checked out.", file=sys.stderr)
        sys.exit(1)

    backup_path = root / ".turtle" / "backups" / rel_path
    if backup_path.is_file():
        make_writable(file_path, stat.S_IREAD | stat.S_IWRITE)
        shutil.copy2(backup_path, file_path)
        backup_path.unlink()
        print(f"Rolled back {rel_path}.")

    data["locks"].pop(rel_path)

    if data.get("active", False):
        make_readonly(file_path, data["files"][rel_path]["mode"])
    else:
        make_writable(file_path, data["files"][rel_path]["mode"])

    save_metadata(root, data)
    print(f"Lock cancelled for {rel_path}.")
```

## 6. Open Questions
- Is there any interest in pursuing optimistic non-blocking locks using localized Git sub-branches for concurrent agent coordination instead?
- How should multi-agent systems coordinate conflicts in single-file repositories without locked checkout controls?

## 7. References
- [Turtle VCS Implementation Prototype](#5-prototype-code-listing)
- RFC Template Framework (rfc-template skill)
