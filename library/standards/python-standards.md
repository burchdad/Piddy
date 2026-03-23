# Python Coding Standards

## Scope: PEP 8, PEP 20, type hints, project layout
**Authority:** PEP 8 (Style Guide), PEP 257 (Docstrings), Google Python Style  
**Tools:** ruff, mypy, black, isort  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Module | `snake_case` | `user_service.py` |
| Class | `PascalCase` | `UserService` |
| Function / Method | `snake_case` | `get_user_by_id()` |
| Variable | `snake_case` | `user_count` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| Private | `_leading_underscore` | `_internal_cache` |
| Type variable | `PascalCase` | `T`, `KeyType` |
| Enum member | `UPPER_SNAKE` | `Status.ACTIVE` |

**Avoid:** single-letter names except `i/j/k` in loops, `x/y` in math, `e` in except, `_` for unused.

## Formatting Rules

```python
# Line length: 88 (black default) or 79 (PEP 8)
# Indentation: 4 spaces (never tabs)
# Blank lines: 2 between top-level, 1 between methods

# Imports — grouped and ordered
import os                          # 1. stdlib
import sys
from pathlib import Path

import httpx                       # 2. third-party
from pydantic import BaseModel

from src.models import User        # 3. local
from src.utils import retry

# Trailing commas in multi-line (enables cleaner diffs)
config = {
    "host": "localhost",
    "port": 8889,
    "debug": True,  # <-- trailing comma
}
```

## Type Hints (PEP 484/604)

```python
# Modern syntax (3.10+): use | instead of Union
def find_user(user_id: int) -> User | None:
    ...

# Use built-in generics (3.9+): list, dict, tuple, set
def process(items: list[str]) -> dict[str, int]:
    ...

# TypeAlias for complex types
type UserMap = dict[int, list[User]]

# Protocol for structural typing (duck typing with safety)
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...
```

## Docstrings (PEP 257 / Google Style)

```python
def fetch_data(url: str, timeout: float = 30.0) -> dict:
    """Fetch JSON data from a remote URL.

    Args:
        url: The endpoint URL to fetch from.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        ConnectionError: If the endpoint is unreachable.
        ValueError: If response is not valid JSON.
    """
```

## Project Layout

```
project/
├── pyproject.toml          # project metadata + tool config
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── models.py
│       └── services.py
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   └── test_services.py
└── README.md
```

## Anti-Patterns to Avoid

| Anti-Pattern | Better |
|-------------|--------|
| `except Exception: pass` | Catch specific exceptions, log errors |
| Mutable default args `def f(x=[])` | Use `def f(x=None): x = x or []` |
| `type(x) == int` | `isinstance(x, int)` |
| Bare `assert` in production | Use `if`/`raise` (asserts stripped with `-O`) |
| Star imports `from x import *` | Explicit imports |
| Global mutable state | Dependency injection or module-level constants |
| Nested `try/except` blocks | Flatten or extract helper functions |
