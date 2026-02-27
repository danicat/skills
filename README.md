# Gemini CLI Skills Repository

This repository contains a collection of specialized skills for the Gemini CLI.

## Installation

### From GitHub (Recommended)
You can install any skill directly from this repository using its URL and the `--path` flag to specify the skill name:

```bash
gemini skills install https://github.com/danicat/skills --path <skill-name>
```

### From Local Source
If you have cloned this repository locally, you can install or link skills from their directory:

```bash
# Full installation
gemini skills install ./<skill-name>

# Link for development (symlinks the directory)
gemini skills link ./<skill-name>
```


## Available Skills

### `experiment-analyst`
Expertise in analyzing Tenkai agent experiments. Use when asked to "analyze experiment X" to determine success factors, failure modes, and behavioral patterns.

### `find-examples`
Find and inspect real-world code examples from GitHub for specific dependencies and languages.

### `go-best-practices`
Comprehensive Go (Golang) development best practices and coding style guidelines.

### `go-project-setup`
Standardized setup for new Go (Golang) projects and services.

### `google-blog-style`
Official style guide and compliance rules for the Google Developers Blog.

### `google-codelab-authoring`
Definitive guide for authoring high-quality Google Codelabs.

### `latest-version`
The definitive real-time source of truth for software and model versions. Bypasses knowledge cutoffs by querying live registries.

### `pyhd`
Python development workflow for editing, formatting (ruff), and documentation.
