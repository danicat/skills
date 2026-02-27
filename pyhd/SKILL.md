---
name: pyhd
description: Python development workflow for editing, formatting (ruff), and documentation. Use when writing, refactoring, or updating Python code.
---

# Pyhd (Python Development)

## Overview

This skill enforces a rigorous development workflow for Python projects, centering on the `ruff` linter and formatter. It ensures that all code changes are automatically formatted and linted to meet industry standards. It also provides guidance on accessing documentation.

## Core Workflow

When editing Python files, you **MUST** follow this cycle for **EVERY** file modification:

1.  **Read & Understand**:
    *   Read the file content to understand the context.
    *   If using external packages, **verify their API** first (see "Documentation" below).
2.  **Edit**:
    *   Apply your changes using `smart_edit` or `replace`.
3.  **Sanitize (Ruff)**:
    *   Immediately after editing, run the following commands to format and fix linting issues:
        ```bash
        uv run ruff check --fix <filename>
        uv run ruff format <filename>
        ```
    *   If `ruff` reports errors that cannot be automatically fixed, you **MUST** fix them manually before proceeding.
4.  **Verify**:
    *   Run tests to ensure your changes didn't break functionality.

## Documentation

Before using a Python package or library, you **MUST** ensure you are using the correct API.

1.  **Search Online**: Use `google_web_search` to find the official documentation.
    *   Query format: `python <package_name> documentation` or `python <package_name> <function_name> usage`.
2.  **Inspect Installed Packages**:
    *   If the package is installed, you can inspect it in the virtual environment (e.g., `.venv/lib/python3.x/site-packages/<package>`).
3.  **Use `help()`**:
    *   You can run a one-off script to print help:
        ```bash
        uv run python -c "import <package>; help(<package>.<symbol>)"
        ```

## Best Practices

See [best_practices.md](references/best_practices.md) for detailed coding standards and idiomatic Python patterns.
