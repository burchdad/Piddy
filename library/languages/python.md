# Python Quick Reference

## Language: Python 3.11+
**Paradigm:** Multi-paradigm (OOP, functional, procedural, structured)  
**Typing:** Dynamic, strong  
**Runtime:** CPython interpreter, also PyPy, GraalPy  

## Syntax Essentials

```python
# Variables & types
x: int = 42
name: str = "Piddy"
items: list[str] = ["a", "b", "c"]
config: dict[str, int] = {"port": 8889}
active: bool = True
coords: tuple[float, float] = (1.0, 2.0)
unique: set[int] = {1, 2, 3}

# F-strings
print(f"Hello {name}, port={config['port']}")

# Comprehensions
squares = [x**2 for x in range(10)]
evens = {x for x in range(20) if x % 2 == 0}
lookup = {k: v for k, v in pairs}

# Functions
def greet(name: str, excited: bool = False) -> str:
    suffix = "!" if excited else "."
    return f"Hello {name}{suffix}"

# Lambda
double = lambda x: x * 2

# Unpacking
first, *rest = [1, 2, 3, 4]
a, b = b, a  # swap

# Walrus operator
if (n := len(items)) > 10:
    print(f"Too many: {n}")
```

## Control Flow

```python
# Match statement (3.10+)
match command:
    case "quit":
        exit()
    case ("go", direction):
        move(direction)
    case _:
        print("unknown")

# For/else
for item in items:
    if item == target:
        break
else:
    print("not found")

# Exception handling
try:
    result = operation()
except ValueError as e:
    handle(e)
except (TypeError, KeyError):
    fallback()
else:
    on_success(result)
finally:
    cleanup()
```

## OOP

```python
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Protocol

# Dataclass
@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"

# Abstract base
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

# Protocol (structural typing)
class Drawable(Protocol):
    def draw(self) -> None: ...

# Slots for memory efficiency
class Lightweight:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y
```

## Async

```python
import asyncio

async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

# Gather concurrent tasks
results = await asyncio.gather(fetch(u1), fetch(u2))

# Async generators
async def stream():
    async for chunk in reader:
        yield process(chunk)
```

## Standard Library Highlights

| Module | Purpose |
|--------|---------|
| `pathlib` | Path manipulation (prefer over os.path) |
| `json` | JSON encode/decode |
| `collections` | defaultdict, Counter, deque, namedtuple |
| `itertools` | chain, product, combinations, groupby |
| `functools` | lru_cache, partial, reduce, wraps |
| `typing` | Type hints (Optional, Union, TypeVar, Generic) |
| `contextlib` | contextmanager, suppress, asynccontextmanager |
| `dataclasses` | @dataclass decorator |
| `re` | Regular expressions |
| `sqlite3` | SQLite database |
| `subprocess` | Run external commands |
| `logging` | Structured logging |
| `unittest` | Testing framework |
| `argparse` | CLI argument parsing |

## Package Management

```bash
pip install package
pip install -r requirements.txt
python -m venv .venv
pip freeze > requirements.txt
# Modern: pyproject.toml + pip install -e .
```

## Common Patterns

```python
# Context manager
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.time()
    yield
    print(f"{label}: {time.time()-start:.3f}s")

# Decorator
def retry(n=3):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            for i in range(n):
                try: return fn(*a, **kw)
                except Exception:
                    if i == n-1: raise
        return wrapper
    return decorator

# Enum
from enum import Enum, auto
class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    DONE = auto()
```
