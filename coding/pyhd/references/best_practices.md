# Python Development Best Practices

This reference guide establishes idiomatic coding standards, modern type annotations, Ruff configuration, and testing practices for Python development.

---

## 1. Modern Type Hinting (Python 3.10+)

Always annotate function signatures and module interfaces with explicit type hints. Use Python 3.10+ native typing syntax rather than importing legacy containers from the `typing` module.

### Built-in Collections & Generics

```python
# ✅ Correct (Modern Python 3.10+)
def get_user_scores(names: list[str]) -> dict[str, float]:
    return {name: 0.0 for name in names}

def get_unique_ids(records: list[dict[str, int]]) -> set[int]:
    return {item["id"] for item in records}

def get_coordinates() -> tuple[float, float, str]:
    return (37.7749, -122.4194, "San Francisco")
```

### Union & Optional Types

Use the pipe operator (`|`) for union and optional types:

```python
# ✅ Correct
def find_user(user_id: int) -> User | None: ...

def parse_identifier(raw: str | int) -> str: ...
```

### Type Checking Guards

Prevent runtime circular dependencies while maintaining full static type safety:

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from my_package.services.payment import PaymentProcessor
    from my_package.models.user import User

def process_order(user: User, processor: PaymentProcessor) -> bool:
    ...
```

---

## 2. Idiomatic Code Style & Architecture

- **Clarity over Cleverness**: Prefer explicit loops and generator expressions over nested list comprehensions or cryptic `lambda` / `reduce` chains.
- **PEP 8 Compliance**: Adhere to PEP 8 standards enforced automatically via Ruff.
- **Resource Management**: Always use `with` statements (context managers) for files, locks, database sessions, and network connections.
- **Data Modeling**: Use standard `dataclasses` (or `pydantic.BaseModel` for runtime validation/serialization):
  ```python
  from dataclasses import dataclass, field

  @dataclass(frozen=True, slots=True)
  class UserProfile:
      username: str
      email: str
      roles: list[str] = field(default_factory=list)
  ```

---

## 3. Exception Handling & Error Boundaries

- **Specific Exceptions**: Always catch specific exception classes (e.g., `KeyError`, `ValueError`, `httpx.HTTPError`). Never use bare `except:` or catch generic `Exception` unless creating a top-level error boundary.
- **Explicit Cause Chaining**: Preserve original tracebacks when wrapping low-level errors into domain exceptions:
  ```python
  class ServiceUnavailableError(Exception):
      """Raised when external dependency is unreachable."""

  try:
      client.connect()
  except ConnectionRefusedError as err:
      raise ServiceUnavailableError("Failed to reach auth service") from err
  ```
- **Custom Exceptions**: Define a common base exception for each package to enable callers to catch package-scoped errors cleanly.

---

## 4. Recommended `pyproject.toml` Configuration for Ruff

Configure Ruff in `pyproject.toml` with strict linting and formatting rules:

```toml
[tool.ruff]
line-length = 88
target-version = "py310"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # Pyflakes
    "I",     # isort (import sorting)
    "B",     # flake8-bugbear (common bug prevention)
    "UP",    # pyupgrade (modernize Python syntax)
    "SIM",   # flake8-simplify
    "RUF",   # Ruff-specific rules
    "PLC",   # Pylint conventions
    "PLE",   # Pylint errors
    "PLW",   # Pylint warnings
]
ignore = [
    "E501",  # Line length handled by formatter
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.ruff.lint.isort]
known-first-party = ["my_package"]
combine-as-imports = true
```

---

## 5. Testing with Pytest

Structure test suites for fast inner-loop iteration and isolation:

### Test Fixtures (`tests/conftest.py`)

```python
import pytest
from my_package.core import Engine

@pytest.fixture
def engine() -> Engine:
    """Provides a fresh Engine instance with clean state per test."""
    return Engine(debug=False)
```

### Parametrized Unit Tests

```python
import pytest
from my_package.utils import slugify

@pytest.mark.parametrize(
    ("input_text", "expected_slug"),
    [
        ("Hello World", "hello-world"),
        ("Python 3.12 & uv!", "python-312-uv"),
        ("   leading trailing   ", "leading-trailing"),
    ],
)
def test_slugify(input_text: str, expected_slug: str) -> None:
    assert slugify(input_text) == expected_slug
```
