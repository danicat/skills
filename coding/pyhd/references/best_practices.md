# Python Development Best Practices

## Code Style and Structure

- **Style compliance**: Use PEP 8 guidelines. Ruff enforces these rules automatically.
- **Naming**: Choose clear, descriptive names for variables, functions, and classes.
- **Readability**: Write simple loops instead of complex list comprehensions.
- **Documentation**: Write descriptive docstrings for all modules, classes, and functions.

## Type Hinting

Annotate all function signatures with type hints from the `typing` module:
- Use specific types for parameters and return values.
- Use `Optional[T]` for values that can be `None`.
- Use `Union[T, U]` when multiple types are expected.
- Use collection types like `List[T]` and `Dict[K, V]` to specify inner types.

## Imports and Error Handling

- **Organization**: Group and sort imports. Ruff organizes imports using `isort` rules.
- **Wildcards**: Do not use wildcard imports (`from module import *`).
- **Exception handling**: Catch specific exceptions (such as `ValueError`) rather than generic `Exception` or bare `except:` clauses.
- **Resource management**: Use `with` statements to ensure file handles and network connections close correctly.

## Ruff Configuration

Configure Ruff in `pyproject.toml` using these settings:

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

## Testing Guidelines

- **Unit tests**: Write tests for logical components using `pytest`. Use mocks to isolate external systems, APIs, and databases.
- **Integration tests**: Write integration tests to check how different modules work together.
