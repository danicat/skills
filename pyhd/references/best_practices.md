# Python Development Best Practices

## General

1.  **Code Style**:
    *   **Always** follow PEP 8 for style (handled by `ruff`).
    *   Use clear and descriptive variable names.
    *   Avoid complex list comprehensions; prefer simple loops if they are more readable.
    *   **Always** document functions and classes with docstrings.

2.  **Type Hinting**:
    *   Use type hints (`from typing import ...`) for all function arguments and return types.
    *   Use `Optional[T]` for nullable values.
    *   Use `Union[T, U]` for multiple types.
    *   Use `List[T]`, `Dict[K, V]`, etc. for collections.

3.  **Imports**:
    *   Keep imports organized (handled by `ruff` with `isort` rules).
    *   Avoid wildcard imports (`from module import *`).

4.  **Error Handling**:
    *   Use specific exception types (`except ValueError:`) instead of catching everything (`except Exception:` or bare `except:`).
    *   Always clean up resources (e.g., file handles) using `with` statements or `finally` blocks.

## Ruff Configuration

When setting up `ruff` in `pyproject.toml`, adhere to the following recommendations:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "PLC", "PLE", "PLW"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

## Testing

1.  **Unit Tests**:
    *   Write unit tests for all non-trivial logic.
    *   Use `pytest` as the test runner.
    *   Mock external dependencies (API calls, databases) to isolate tests.

2.  **Integration Tests**:
    *   Write integration tests to verify interaction between components.
