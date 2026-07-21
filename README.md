# Agent Skills Repository

This repository contains a collection of specialized skills for autonomous agents.


## Installation

### From GitHub (Recommended)
You can install any skill directly from this repository using its URL and the `--path` flag to specify the skill name:

```bash
agy skills install https://github.com/danicat/skills --path <skill-name>
```

### From Local Source
If you have cloned this repository locally, you can install or link skills from their directory:

```bash
# Full installation
agy skills install ./<skill-name>

# Link for development (symlinks the directory)
agy skills link ./<skill-name>
```



## Available Skills

### `a2ui_developer_guide`
A comprehensive guide and reference suite for the Agent-Driven User Interface (A2UI) streaming protocol, specifications, SDKs, and component catalog validations.

### `experiment-analyst` (DEPRECATED)
⚠️ *Legacy Only*: Analyzes Tenkai agent experiment runs. This skill is kept solely for backward compatibility with external resources.

### `find-examples`
Finds, clones, and inspects real-world code examples from GitHub for specific dependencies, frameworks, or libraries, using strict workspace isolation and git safety rules.

### `go-best-practices`
Comprehensive Go (Golang) development best practices, structural layout guidelines, concurrency gotchas, and automated validation loops (supporting the GoDoctor MCP server).

### `google-blog-style`
Official style guide and compliance rules for Google Developers blog posts, including Gunning Fog readability metrics and Vale-powered style linter checks (supporting the Speedgrapher MCP server).

### `google-codelab-authoring`
Structured workflow for writing step-by-step developer tutorials in Google Codelabs format (`.lab.md`) using strict Claat metadata, durations, and aside block linting.

### `latest-version`
Modular batch query tool and instructions to retrieve, verify, and resolve the absolute latest stable versions of software packages, dependencies (NPM, PyPI, Go proxy, Cargo, RubyGems), and Gemini models.

### `pyhd`
Python development workflow incorporating strict virtual environments via `uv`, Ruff static linting, auto-formatting, and unified unit testing reports.

### `skill-optimizer`
Meta-skill and developer workflow guides for writing, auditing, and optimizing Agent Skills (`SKILL.md` layout, trigger-precision, and progressive disclosure).

### `swarm-coding`
Orchestrator and specialist patterns to decompose complex engineering tasks, full-stack designs, or large-scale refactorings across a swarm of parallelized subagents safely.
