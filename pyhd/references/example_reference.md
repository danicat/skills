# Reference Documentation for Pyhd

This document provides reference information for the Python development workflow.

## Ruff Rule Selection

The recommended linting configuration selects the following rule categories:

- **E / F**: Pycodestyle errors and Pyflakes.
- **I**: Isort import sorting.
- **UP**: Pyupgrade syntax upgrades.
- **B**: Bugbear common design issues.
- **SIM**: Flake8-simplify code simplifications.
- **PLC / PLE / PLW**: Pylint convention, error, and warning checks.

## Command Reference

### Linting and Formatting
- Format a file: `uv run ruff format <path>`
- Lint and apply safe fixes: `uv run ruff check --fix <path>`

### Testing
- Run pytest: `pytest`
- Run pytest with coverage: `pytest --cov`
