---
name: pyhd
description: Python development workflow using Ruff for linting and formatting. Use when writing, refactoring, or documenting Python code.
---

# Pyhd (Python Development)

This workflow outlines the standard development process for Python projects using Ruff to format and lint code.

## Development Cycle

Run these steps for each file change:

1. **Understand context**: Read the file to understand its purpose. If you use external packages, check their API documentation first.
2. **Apply changes**: Use editing tools or replacement methods to modify the code.
3. **Format and lint**: Format the code and fix style issues immediately after editing. Run:
   ```bash
   uv run ruff check --fix <filename>
   uv run ruff format <filename>
   ```
   Resolve any remaining errors manually before continuing.
4. **Test**: Run the test suite to verify that your changes did not introduce regressions.

## API Documentation

Verify package APIs before writing or modifying code.

- **Online search**: Use search tools to find the official documentation. Helpful search queries include `python <package_name> documentation` or `python <package_name> <function_name>`.
- **Local inspection**: If the package is already installed, inspect its source files under `.venv/lib/python3.x/site-packages/<package>`.
- **Interactive help**: Run a short command to read the Python help docstring:
  ```bash
  uv run python -c "import <package>; help(<package>.<symbol>)"
  ```

## Best Practices

Detailed coding standards and idiomatic Python patterns are located in [best_practices.md](references/best_practices.md).
