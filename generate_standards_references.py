#!/usr/bin/env python3
"""
Coding Standards & Best Practices Generator for Piddy

Generates comprehensive, consistent coding standards reference cards
in library/standards/ for Piddy's knowledge base.

Usage:
    python generate_standards_references.py              # Generate all
    python generate_standards_references.py --list       # List available standards
    python generate_standards_references.py python git   # Generate specific ones
    python generate_standards_references.py --force      # Overwrite existing files

Each standard is defined as structured data. Adding a new standard
is just adding another dict to the STANDARDS list.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path(__file__).parent / "library" / "standards"

# ---------------------------------------------------------------------------
# Standards definitions
# ---------------------------------------------------------------------------

STANDARDS = [
    # ── Language-Specific Standards ────────────────────────────────────
    {
        "filename": "python-standards",
        "title": "Python Coding Standards",
        "meta": {
            "scope": "PEP 8, PEP 20, type hints, project layout",
            "authority": "PEP 8 (Style Guide), PEP 257 (Docstrings), Google Python Style",
            "tools": "ruff, mypy, black, isort",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
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

**Avoid:** single-letter names except `i/j/k` in loops, `x/y` in math, `e` in except, `_` for unused.""",
            },
            {
                "heading": "Formatting Rules",
                "body": """\
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
```""",
            },
            {
                "heading": "Type Hints (PEP 484/604)",
                "body": """\
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
```""",
            },
            {
                "heading": "Docstrings (PEP 257 / Google Style)",
                "body": """\
```python
def fetch_data(url: str, timeout: float = 30.0) -> dict:
    \"\"\"Fetch JSON data from a remote URL.

    Args:
        url: The endpoint URL to fetch from.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        ConnectionError: If the endpoint is unreachable.
        ValueError: If response is not valid JSON.
    \"\"\"
```""",
            },
            {
                "heading": "Project Layout",
                "body": """\
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
```""",
            },
            {
                "heading": "Anti-Patterns to Avoid",
                "body": """\
| Anti-Pattern | Better |
|-------------|--------|
| `except Exception: pass` | Catch specific exceptions, log errors |
| Mutable default args `def f(x=[])` | Use `def f(x=None): x = x or []` |
| `type(x) == int` | `isinstance(x, int)` |
| Bare `assert` in production | Use `if`/`raise` (asserts stripped with `-O`) |
| Star imports `from x import *` | Explicit imports |
| Global mutable state | Dependency injection or module-level constants |
| Nested `try/except` blocks | Flatten or extract helper functions |""",
            },
        ],
    },
    {
        "filename": "javascript-standards",
        "title": "JavaScript Coding Standards",
        "meta": {
            "scope": "ES2024+ conventions, module patterns, async best practices",
            "authority": "Airbnb Style Guide, StandardJS, ESLint recommended",
            "tools": "ESLint, Prettier, Biome",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Variable / Function | `camelCase` | `getUserById` |
| Class / Component | `PascalCase` | `UserService` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| File (module) | `camelCase` or `kebab-case` | `userService.js` |
| Private (convention) | `#prefix` (class) or `_prefix` | `#cache`, `_internal` |
| Boolean variable | `is/has/can/should` prefix | `isActive`, `hasPermission` |
| Event handler | `handle` + event | `handleClick`, `handleSubmit` |""",
            },
            {
                "heading": "Variable Declaration",
                "body": """\
```javascript
// ALWAYS use const by default
const config = loadConfig();
const users = [];

// Use let only when reassignment is needed
let count = 0;
for (let i = 0; i < 10; i++) { count += i; }

// NEVER use var (function-scoped, hoisted, error-prone)

// Prefer destructuring
const { name, age } = user;
const [first, ...rest] = items;

// Prefer template literals over concatenation
const msg = `Hello ${name}, you have ${count} items`;
```""",
            },
            {
                "heading": "Functions",
                "body": """\
```javascript
// Prefer arrow functions for callbacks / inline
const doubled = items.map(x => x * 2);

// Use regular functions for methods and when `this` matters
// or when hoisting is needed

// Always handle async errors
async function fetchUser(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    logger.error('fetchUser failed', { id, err });
    throw err;  // re-throw after logging
  }
}

// Prefer early returns over deep nesting
function process(input) {
  if (!input) return null;
  if (!input.valid) return { error: 'invalid' };
  return transform(input);
}
```""",
            },
            {
                "heading": "Module Patterns",
                "body": """\
```javascript
// Use ES modules (import/export), not CommonJS (require)
import { readFile } from 'node:fs/promises';

// Named exports (preferred for most files)
export function createUser(data) { }
export const MAX_RETRIES = 3;

// Default export (only for main component / class per file)
export default class Router { }

// Barrel files — only for public API boundaries
// index.js
export { UserService } from './userService.js';
export { AuthService } from './authService.js';
```""",
            },
            {
                "heading": "Equality & Comparisons",
                "body": """\
```javascript
// ALWAYS use === and !== (strict equality)
if (value === null) { }
if (typeof x === 'string') { }

// Use optional chaining for safe access
const city = user?.address?.city;

// Use nullish coalescing for defaults (not ||)
const port = config.port ?? 3000;   // only null/undefined
// Avoid: config.port || 3000       // also catches 0, ""
```""",
            },
            {
                "heading": "Anti-Patterns to Avoid",
                "body": """\
| Anti-Pattern | Better |
|-------------|--------|
| `var` declarations | `const` / `let` |
| `==` loose equality | `===` strict equality |
| Callback hell | `async/await` |
| `for...in` on arrays | `for...of`, `.map()`, `.forEach()` |
| Modifying function arguments | Clone first: `{...args}` |
| `new Array(5)` | `Array.from({length: 5})` |
| Silent catch `catch(e) {}` | Log and re-throw or handle meaningfully |
| `arguments` object | Rest parameters `...args` |""",
            },
        ],
    },
    {
        "filename": "typescript-standards",
        "title": "TypeScript Coding Standards",
        "meta": {
            "scope": "Type safety, strict config, interface patterns",
            "authority": "TypeScript Handbook, Google TS Style, ts-reset",
            "tools": "tsc --strict, ESLint + typescript-eslint, Biome",
        },
        "sections": [
            {
                "heading": "Strict Configuration",
                "body": """\
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true
  }
}
```

**Never disable strict checks** — they catch real bugs.""",
            },
            {
                "heading": "Types vs Interfaces",
                "body": """\
```typescript
// Use `type` for unions, intersections, mapped types, primitives
type Status = 'active' | 'inactive' | 'pending';
type Result<T> = { ok: true; data: T } | { ok: false; error: string };
type UserMap = Map<string, User>;

// Use `interface` for object shapes (especially public APIs)
interface UserService {
  getUser(id: number): Promise<User>;
  createUser(data: CreateUserInput): Promise<User>;
}

// interfaces are extendable / mergeable:
interface Config { host: string; }
interface Config { port: number; }  // declaration merging
```""",
            },
            {
                "heading": "Avoid Type Escape Hatches",
                "body": """\
```typescript
// NEVER use `any` — use `unknown` and narrow
function parse(input: unknown): Config {
  if (typeof input !== 'object' || input === null) {
    throw new Error('Expected object');
  }
  // ... validate and narrow
}

// AVOID non-null assertions (!) — guard instead
// Bad:  const name = user!.name;
// Good: if (!user) throw new Error('No user');
//       const name = user.name;

// AVOID type assertions unless truly necessary
// Bad:  const data = response as UserData;
// Good: const data = schema.parse(response);  // runtime validation
```""",
            },
            {
                "heading": "Function Signatures",
                "body": """\
```typescript
// Return types on public functions (inference for private/internal)
export function calculateTotal(items: LineItem[]): number { }

// Use discriminated unions over optional fields
// Bad:
type Response = { data?: User; error?: string; };
// Good:
type Response = { ok: true; data: User } | { ok: false; error: string };

// Generics: name descriptively when >1
function merge<TBase, TOverride>(base: TBase, over: TOverride): TBase & TOverride { }
```""",
            },
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Type / Interface | `PascalCase` | `UserProfile`, `ApiResponse` |
| Type parameter | `T` prefix or descriptive | `T`, `TKey`, `TValue` |
| Enum | `PascalCase` (members too) | `Direction.North` |
| File | `camelCase` or `kebab-case` | `userService.ts` |
| No `I` prefix | ~~`IUserService`~~ | `UserService` |
| No `Enum` suffix | ~~`StatusEnum`~~ | `Status` |""",
            },
        ],
    },
    {
        "filename": "java-standards",
        "title": "Java Coding Standards",
        "meta": {
            "scope": "Naming, structure, modern idioms (Java 17-21)",
            "authority": "Google Java Style, Oracle Code Conventions, Effective Java",
            "tools": "Checkstyle, SpotBugs, Error Prone, google-java-format",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Package | `lowercase.dotted` | `com.example.service` |
| Class / Interface | `PascalCase` | `UserService` |
| Method | `camelCase` (verb) | `getUserById()` |
| Variable | `camelCase` | `userCount` |
| Constant | `UPPER_SNAKE` | `MAX_CONNECTIONS` |
| Type parameter | Single uppercase / descriptive | `T`, `K`, `V`, `E` |
| Boolean method | `is/has/can` prefix | `isActive()` |
| Enum member | `UPPER_SNAKE` | `Status.ACTIVE` |""",
            },
            {
                "heading": "Modern Idioms",
                "body": """\
```java
// Prefer records for data carriers
record UserDTO(String name, String email) {}

// Prefer sealed hierarchies for known subtypes
sealed interface Shape permits Circle, Rectangle {}

// Prefer var for local variables with obvious types
var users = new ArrayList<User>();
var config = loadConfig();

// Prefer switch expressions over statements
var label = switch (status) {
    case 200 -> "OK";
    case 404 -> "Not Found";
    default -> "Unknown";
};

// Prefer Optional over null returns
Optional<User> findById(int id) { }
// NEVER: Optional as method parameter or field
```""",
            },
            {
                "heading": "Error Handling",
                "body": """\
```java
// Prefer specific exceptions
throw new UserNotFoundException("ID: " + id);

// Catch specific, not generic
try { parseConfig(path); }
catch (IOException e) { logger.error("Config read failed", e); throw; }

// NEVER catch Throwable/Error (except at top-level)
// NEVER swallow exceptions silently
// Use try-with-resources for AutoCloseable
try (var conn = dataSource.getConnection();
     var stmt = conn.prepareStatement(sql)) {
    // ...
}
```""",
            },
            {
                "heading": "Project Structure",
                "body": """\
```
src/main/java/com/example/
├── config/              # Configuration classes
├── controller/          # REST controllers
├── service/             # Business logic
├── repository/          # Data access
├── model/               # Domain objects
│   ├── entity/
│   └── dto/
└── exception/           # Custom exceptions

src/test/java/com/example/
└── (mirrors main structure)
```""",
            },
        ],
    },
    {
        "filename": "csharp-standards",
        "title": "C# Coding Standards",
        "meta": {
            "scope": "Naming, patterns, modern C# 10-12 idioms",
            "authority": "Microsoft .NET Framework Design Guidelines, Roslyn analyzers",
            "tools": "dotnet format, Roslynator, SonarAnalyzer",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Class / Struct / Record | `PascalCase` | `UserService` |
| Interface | `IPascalCase` | `IUserRepository` |
| Method / Property | `PascalCase` | `GetUser()`, `IsActive` |
| Local variable / parameter | `camelCase` | `userName`, `retryCount` |
| Private field | `_camelCase` | `_logger`, `_cache` |
| Constant | `PascalCase` | `MaxRetries` |
| Enum | `PascalCase` (singular) | `Color.Red` |
| Namespace | `Company.Product.Area` | `Piddy.Core.Services` |
| Async method | `...Async` suffix | `GetUserAsync()` |""",
            },
            {
                "heading": "Modern Idioms (C# 10-12)",
                "body": """\
```csharp
// Use file-scoped namespaces
namespace MyApp.Services;

// Use records for immutable data
record UserDto(string Name, string Email);

// Use primary constructors for DI (C# 12)
class UserService(IRepository repo, ILogger<UserService> logger)
{
    public User? Find(int id) => repo.GetById(id);
}

// Use pattern matching over type checks
if (shape is Circle { Radius: > 10 } c)
    Console.WriteLine($"Big circle: {c.Radius}");

// Use collection expressions (C# 12)
int[] primes = [2, 3, 5, 7, 11];
```""",
            },
            {
                "heading": "Async Best Practices",
                "body": """\
```csharp
// ALWAYS await async calls (no fire-and-forget)
await SendEmailAsync(user);

// ALWAYS pass CancellationToken
async Task<User> GetUserAsync(int id, CancellationToken ct = default)
{
    return await repo.FindAsync(id, ct);
}

// NEVER use .Result or .Wait() (deadlock risk)
// NEVER return async void (except event handlers)
// ALWAYS use ConfigureAwait(false) in libraries
```""",
            },
            {
                "heading": "Error Handling",
                "body": """\
```csharp
// Throw specific exceptions with context
throw new InvalidOperationException($"User {id} not found");

// Use exception filters
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    return null;
}

// Prefer Result<T> pattern for expected failures
record Result<T>(T? Value, string? Error)
{
    public bool IsSuccess => Error is null;
}
```""",
            },
        ],
    },
    {
        "filename": "c-cpp-standards",
        "title": "C / C++ Coding Standards",
        "meta": {
            "scope": "Modern C++ (17/20/23), memory safety, RAII",
            "authority": "C++ Core Guidelines (Stroustrup/Sutter), Google C++ Style, MISRA C",
            "tools": "clang-tidy, cppcheck, AddressSanitizer, Valgrind",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
**Google C++ Style (most common):**

| Element | Convention | Example |
|---------|-----------|---------|
| Type / Class / Struct | `PascalCase` | `UserManager` |
| Function / Method | `PascalCase` or `camelCase` | `GetUser()` |
| Variable | `snake_case` | `user_count` |
| Member variable | `snake_case_` (trailing) | `cache_size_` |
| Constant | `kPascalCase` | `kMaxRetries` |
| Enum member | `kPascalCase` | `Color::kRed` |
| Macro | `UPPER_SNAKE` | `MY_MACRO` |
| Namespace | `snake_case` | `my_project` |
| File | `snake_case` | `user_service.cpp` |""",
            },
            {
                "heading": "Memory Safety Rules",
                "body": """\
```cpp
// 1. RAII: every resource is owned by an object
auto ptr = std::make_unique<Widget>();        // unique ownership
auto shared = std::make_shared<Config>();     // shared ownership

// 2. NEVER use raw new/delete
// Bad:  Widget* w = new Widget();
// Good: auto w = std::make_unique<Widget>();

// 3. Use span/string_view for non-owning references
void process(std::span<const int> data);
void log(std::string_view message);

// 4. Prefer stack allocation
std::array<int, 100> buffer;     // not: int* buf = new int[100];

// 5. Use AddressSanitizer in CI
// g++ -fsanitize=address -fno-omit-frame-pointer
```""",
            },
            {
                "heading": "Modern C++ Idioms",
                "body": """\
```cpp
// Prefer auto for complex types (readability)
auto result = computeMatrix();
auto it = container.find(key);

// Structured bindings
auto [key, value] = *map.begin();

// constexpr for compile-time computation
constexpr auto factorial(int n) -> int {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// Concepts for constrained templates
template<typename T>
concept Sortable = std::totally_ordered<T> && std::movable<T>;

template<Sortable T>
void sort(std::vector<T>& v);
```""",
            },
            {
                "heading": "Header Hygiene",
                "body": """\
```cpp
// Use #pragma once (or include guards)
#pragma once

// Forward declare instead of including when possible
class UserService;   // in header
#include "user_service.h"  // in .cpp

// Include order (Google style):
// 1. Related header (foo.h for foo.cpp)
// 2. C system headers
// 3. C++ standard headers
// 4. Third-party library headers
// 5. Project headers
```""",
            },
        ],
    },
    {
        "filename": "go-standards",
        "title": "Go Coding Standards",
        "meta": {
            "scope": "Effective Go, naming, error handling, project layout",
            "authority": "Effective Go, Go Code Review Comments, Go Proverbs",
            "tools": "gofmt, go vet, golangci-lint, staticcheck",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Exported | `PascalCase` | `UserService`, `GetUser` |
| Unexported | `camelCase` | `userCache`, `parseConfig` |
| Package | Short, lowercase, no underscores | `http`, `user`, `config` |
| Interface (1 method) | method + `er` | `Reader`, `Writer`, `Stringer` |
| Acronyms | All caps or all lower | `HTTPClient`, `xmlParser` |
| Getter | No `Get` prefix | `Name()` not ~~`GetName()`~~ |
| File | `snake_case.go` | `user_service.go` |

**Go proverb:** "A name's length should be proportional to the distance between declaration and use.\"""",
            },
            {
                "heading": "Error Handling",
                "body": """\
```go
// ALWAYS check errors — never ignore
result, err := doWork()
if err != nil {
    return fmt.Errorf("doWork failed: %w", err)
}

// Sentinel errors for known conditions
var ErrNotFound = errors.New("not found")

// Check with errors.Is / errors.As
if errors.Is(err, ErrNotFound) { return nil }

// Error types for extra context
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// NEVER panic in library code
// NEVER use _ to discard errors (except in tests/examples)
```""",
            },
            {
                "heading": "Interface Design",
                "body": """\
```go
// Keep interfaces small (1-3 methods)
type Reader interface { Read(p []byte) (n int, err error) }

// Accept interfaces, return structs
func NewService(repo UserRepository) *UserService { }

// Define interfaces at the consumer, not the implementor
// package handler (consumer)
type UserFinder interface {
    FindByID(ctx context.Context, id int) (*User, error)
}
```""",
            },
            {
                "heading": "Project Layout",
                "body": """\
```
myapp/
├── cmd/
│   └── myapp/
│       └── main.go          # entry point
├── internal/                 # private packages
│   ├── user/
│   │   ├── service.go
│   │   ├── repository.go
│   │   └── service_test.go
│   └── config/
├── pkg/                      # public packages (optional)
├── go.mod
├── go.sum
└── README.md
```""",
            },
            {
                "heading": "Concurrency Rules",
                "body": """\
```go
// ALWAYS pass context.Context as first parameter
func GetUser(ctx context.Context, id int) (*User, error) { }

// Use errgroup for structured concurrency
g, ctx := errgroup.WithContext(ctx)
g.Go(func() error { return fetchA(ctx) })
g.Go(func() error { return fetchB(ctx) })
if err := g.Wait(); err != nil { return err }

// Share by communicating, don't communicate by sharing
// Prefer channels over mutexes where practical
// Keep goroutine lifetimes obvious and bounded
```""",
            },
        ],
    },
    {
        "filename": "rust-standards",
        "title": "Rust Coding Standards",
        "meta": {
            "scope": "Naming, ownership idioms, error handling, API design",
            "authority": "Rust API Guidelines, Clippy lints, Rust RFC style",
            "tools": "cargo clippy, cargo fmt, miri, cargo audit",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Type / Trait / Enum | `PascalCase` | `UserService`, `Display` |
| Function / Method | `snake_case` | `get_user_by_id` |
| Variable / field | `snake_case` | `user_count` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| Module / crate | `snake_case` | `user_service`, `my_crate` |
| Type parameter | Short uppercase | `T`, `K`, `V` |
| Lifetime | Short lowercase `'a` | `'a`, `'static` |
| Conversion | `from_*`, `to_*`, `into_*`, `as_*` | `from_str`, `to_string` |
| Fallible | `try_*` | `try_parse` |
| Bool getter | `is_*`, `has_*` | `is_empty`, `has_value` |""",
            },
            {
                "heading": "Error Handling",
                "body": """\
```rust
// Use Result<T, E> for fallible operations (never panic for expected errors)
fn load_config(path: &Path) -> Result<Config, AppError> { }

// Use thiserror for library error types
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("io error")]
    Io(#[from] std::io::Error),
}

// Use anyhow for application-level error handling
fn main() -> anyhow::Result<()> {
    let config = load_config("config.toml")
        .context("Failed to load configuration")?;
    Ok(())
}

// NEVER .unwrap() in production — use .expect("reason") at minimum
// Prefer ? operator over manual match on Result
```""",
            },
            {
                "heading": "Ownership Patterns",
                "body": """\
```rust
// Take ownership only when you need it
fn process(data: Vec<u8>) { }         // takes ownership
fn inspect(data: &[u8]) { }           // borrows (preferred if not consuming)
fn modify(data: &mut Vec<u8>) { }     // mutable borrow

// Prefer &str over &String, &[T] over &Vec<T>
fn greet(name: &str) { }              // accepts String, &str, Cow<str>

// Use Cow<str> for "maybe owned" data
fn normalize(input: &str) -> Cow<str> {
    if input.contains(' ') {
        Cow::Owned(input.replace(' ', "_"))
    } else {
        Cow::Borrowed(input)
    }
}

// Clone is a code smell — justify each .clone()
```""",
            },
            {
                "heading": "Derive & Traits",
                "body": """\
```rust
// Derive common traits on data types
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct UserId(u64);

// Implement Display for user-facing output
impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "user:{}", self.0)
    }
}

// Use From/Into for conversions
impl From<u64> for UserId {
    fn from(id: u64) -> Self { UserId(id) }
}
```""",
            },
        ],
    },
    # ── Web Framework Standards ────────────────────────────────────────
    {
        "filename": "react-standards",
        "title": "React Coding Standards",
        "meta": {
            "scope": "Component patterns, hooks rules, state management, performance",
            "authority": "React docs, React Compiler requirements, Airbnb React guide",
            "tools": "eslint-plugin-react, eslint-plugin-react-hooks, React DevTools",
        },
        "sections": [
            {
                "heading": "Component Rules",
                "body": """\
```jsx
// One component per file (name matches filename)
// UserProfile.tsx → export default function UserProfile()

// Props: destructure with defaults
function Button({ label, variant = 'primary', onClick }) {
  return <button className={variant} onClick={onClick}>{label}</button>;
}

// NEVER mutate props or state directly
// Bad:  props.items.push(newItem);
// Good: setItems(prev => [...prev, newItem]);

// Prefer composition over prop drilling
<Layout>
  <Sidebar />
  <Main>{children}</Main>
</Layout>
```""",
            },
            {
                "heading": "Hooks Rules",
                "body": """\
```jsx
// 1. ONLY call hooks at the top level (never inside conditions/loops)
// 2. ONLY call hooks from React components or custom hooks
// 3. Custom hooks MUST start with "use"

// useEffect: always clean up side effects
useEffect(() => {
  const controller = new AbortController();
  fetchData(url, { signal: controller.signal }).then(setData);
  return () => controller.abort();
}, [url]);

// Correct dependencies — never lie about deps
// If a function is a dependency, memoize it:
const handleUpdate = useCallback((id) => {
  setItems(prev => prev.filter(i => i.id !== id));
}, []);  // stable reference
```""",
            },
            {
                "heading": "Performance Patterns",
                "body": """\
```jsx
// Memoize expensive computations
const sorted = useMemo(() => items.sort(compare), [items]);

// Lazy load heavy components
const Dashboard = React.lazy(() => import('./Dashboard'));

// Use key prop correctly (NEVER use array index for dynamic lists)
{items.map(item => <Card key={item.id} {...item} />)}

// Avoid creating objects/functions in render
// Bad:  <Comp style={{color: 'red'}} />  (new object every render)
// Good: const style = useMemo(() => ({color: 'red'}), []);
```""",
            },
            {
                "heading": "File Structure",
                "body": """\
```
src/
├── components/
│   ├── ui/              # Reusable primitives (Button, Input, Modal)
│   └── features/        # Feature-specific (UserCard, OrderTable)
├── hooks/               # Custom hooks
├── pages/               # Route-level components
├── services/            # API calls
├── utils/               # Pure helper functions
└── types/               # Shared TypeScript types
```""",
            },
        ],
    },
    # ── Cross-Cutting Standards ────────────────────────────────────────
    {
        "filename": "git-standards",
        "title": "Git Conventions & Standards",
        "meta": {
            "scope": "Commit messages, branching, PR workflow",
            "authority": "Conventional Commits, Git Flow, GitHub Flow",
            "tools": "commitlint, husky, lint-staged",
        },
        "sections": [
            {
                "heading": "Conventional Commits",
                "body": """\
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting (no logic change) |
| `refactor` | Code restructure (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding/fixing tests |
| `chore` | Build, CI, dependencies |
| `ci` | CI/CD configuration |

**Examples:**
```
feat(auth): add JWT refresh token support
fix(api): handle null response from user endpoint
docs(readme): add deployment instructions
refactor(db): extract connection pooling to module
feat!: drop support for Node 16  (BREAKING CHANGE)
```""",
            },
            {
                "heading": "Branching Strategy (GitHub Flow)",
                "body": """\
```
main (always deployable)
 └── feature/add-user-auth
 └── fix/null-pointer-dashboard
 └── chore/upgrade-dependencies
```

**Rules:**
- `main` is always deployable
- Branch from `main`, PR back to `main`
- Branch names: `type/short-description` (kebab-case)
- Delete branch after merge
- Use squash merge for clean history""",
            },
            {
                "heading": "Commit Best Practices",
                "body": """\
| Rule | Example |
|------|---------|
| Imperative mood | "Add feature" not "Added feature" |
| Subject ≤ 72 chars | Keep it scannable |
| No period at end | `feat: add login` not `feat: add login.` |
| Body: explain WHY | What changed is in the diff; commit says why |
| One logical change | Don't mix refactor + feature |
| Never commit secrets | Use `.env` + `.gitignore` |""",
            },
            {
                "heading": "Pull Request Guidelines",
                "body": """\
- **Title:** follows conventional commit format
- **Description:** What, Why, How, Testing
- **Size:** < 400 lines changed (split larger PRs)
- **Self-review:** before requesting review
- **CI green** before requesting review
- **One approval minimum** before merge
- **Link issues:** `Closes #123` in description""",
            },
        ],
    },
    {
        "filename": "api-design-standards",
        "title": "API Design Standards",
        "meta": {
            "scope": "REST conventions, versioning, error responses, pagination",
            "authority": "Microsoft REST API Guidelines, JSON:API, Google API Design Guide",
            "applies_to": "HTTP/REST APIs",
        },
        "sections": [
            {
                "heading": "URL Structure",
                "body": """\
```
GET    /api/v1/users              # list
GET    /api/v1/users/123          # get one
POST   /api/v1/users              # create
PUT    /api/v1/users/123          # full update
PATCH  /api/v1/users/123          # partial update
DELETE /api/v1/users/123          # delete

# Sub-resources
GET    /api/v1/users/123/orders   # user's orders

# Query params for filtering / pagination
GET    /api/v1/users?role=admin&sort=-created_at&page=2&limit=20
```

**Rules:**
- Nouns, not verbs: `/users` not `/getUsers`
- Plural: `/users` not `/user`
- Kebab-case: `/user-profiles` not `/userProfiles`
- No trailing slashes""",
            },
            {
                "heading": "HTTP Status Codes",
                "body": """\
| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Successful GET/PUT/PATCH |
| `201` | Created | Successful POST (return resource + Location header) |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Validation failure |
| `401` | Unauthorized | Missing/invalid authentication |
| `403` | Forbidden | Authenticated but insufficient permissions |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate / state conflict |
| `422` | Unprocessable | Semantically invalid request |
| `429` | Too Many Requests | Rate limited |
| `500` | Server Error | Unhandled exception |""",
            },
            {
                "heading": "Error Response Format",
                "body": """\
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Must be a valid email address" },
      { "field": "age", "message": "Must be at least 0" }
    ]
  }
}
```

**Rules:**
- Consistent error shape across all endpoints
- Machine-readable `code` + human-readable `message`
- Never leak stack traces or internal details to clients""",
            },
            {
                "heading": "Pagination",
                "body": """\
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 156,
    "totalPages": 8
  }
}
```

**Cursor-based** (preferred for large/real-time datasets):
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "has_more": true
  }
}
```""",
            },
            {
                "heading": "Versioning",
                "body": """\
| Strategy | Example | Pros/Cons |
|----------|---------|-----------|
| URL path | `/api/v1/users` | Simple, explicit, easy to route |
| Header | `Accept: application/vnd.api+json;v=1` | Clean URLs, harder to test |
| Query param | `/api/users?version=1` | Easy to use, clutters params |

**Recommended:** URL path versioning (`/api/v1/`) — most widely adopted.""",
            },
        ],
    },
    {
        "filename": "security-standards",
        "title": "Security Coding Standards",
        "meta": {
            "scope": "OWASP Top 10, secrets, input validation, authentication",
            "authority": "OWASP Top 10 (2021), CWE/SANS Top 25, NIST",
            "tools": "Snyk, Dependabot, SonarQube, Trivy, gitleaks",
        },
        "sections": [
            {
                "heading": "Input Validation",
                "body": """\
```
RULE: Never trust user input. Validate at system boundaries.

1. Validate type, length, format, and range
2. Use allowlists over denylists
3. Sanitize output (context-dependent encoding)
4. Use parameterized queries (NEVER string concatenation for SQL)
```

```python
# SQL Injection prevention
# BAD:  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# GOOD:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```javascript
// XSS prevention — React auto-escapes by default
// NEVER use dangerouslySetInnerHTML with user data
// ALWAYS sanitize if rendering raw HTML (use DOMPurify)
```""",
            },
            {
                "heading": "Secrets Management",
                "body": """\
| Rule | Implementation |
|------|---------------|
| Never commit secrets | Use `.env` + `.gitignore`, run `gitleaks` in CI |
| Environment variables | `process.env.DB_PASSWORD`, `os.environ["API_KEY"]` |
| Rotate regularly | Automate via vault/secrets manager |
| Least privilege | Each service gets only the keys it needs |
| No secrets in logs | Redact sensitive fields before logging |
| No secrets in URLs | Use headers (Authorization: Bearer) |""",
            },
            {
                "heading": "Authentication & Authorization",
                "body": """\
```
- Use bcrypt/argon2 for password hashing (NEVER MD5/SHA1)
- JWT: short expiry (15min), refresh token rotation
- ALWAYS validate JWT signature server-side
- Enforce HTTPS everywhere
- Implement rate limiting on auth endpoints
- Use RBAC or ABAC for authorization
- Check permissions on every request (not just UI-side)
```""",
            },
            {
                "heading": "Dependency Security",
                "body": """\
```bash
# Audit dependencies regularly
npm audit                    # Node.js
pip-audit                    # Python
cargo audit                  # Rust
dotnet list package --vulnerable  # .NET

# Pin dependency versions in production
# Review new dependencies before adding
# Use lockfiles (package-lock.json, Pipfile.lock)
# Run Dependabot / Renovate for automated updates
```""",
            },
            {
                "heading": "OWASP Top 10 Quick Reference",
                "body": """\
| # | Risk | Key Mitigation |
|---|------|----------------|
| 1 | Broken Access Control | Check auth on every request, deny by default |
| 2 | Cryptographic Failures | Use TLS, bcrypt, avoid rolling own crypto |
| 3 | Injection | Parameterized queries, input validation |
| 4 | Insecure Design | Threat modeling, secure defaults |
| 5 | Security Misconfiguration | Harden defaults, disable debug in prod |
| 6 | Vulnerable Components | Audit deps, automated updates |
| 7 | Auth Failures | MFA, rate limiting, secure session mgmt |
| 8 | Data Integrity Failures | Verify signatures, CI/CD security |
| 9 | Logging Failures | Log security events, centralize, alert |
| 10 | SSRF | Allowlist URLs, don't fetch user-supplied URLs |""",
            },
        ],
    },
    {
        "filename": "testing-standards",
        "title": "Testing Standards & Best Practices",
        "meta": {
            "scope": "Unit, integration, E2E testing patterns",
            "authority": "xUnit Patterns, Testing Trophy (Kent C. Dodds), Google Testing Blog",
            "tools": "pytest, Jest/Vitest, JUnit, xUnit, Playwright, Cypress",
        },
        "sections": [
            {
                "heading": "Test Naming",
                "body": """\
```python
# Python: descriptive snake_case
def test_create_user_returns_201_with_valid_input():
def test_create_user_raises_validation_error_for_missing_email():

# JavaScript/TypeScript: describe + it
describe('UserService', () => {
  it('should return user when valid ID provided', () => {});
  it('should throw NotFoundError for missing user', () => {});
});

# Java: methodName_condition_expectedResult
void createUser_validInput_returns201()
void createUser_missingEmail_throwsValidationException()
```""",
            },
            {
                "heading": "Test Structure (AAA / Given-When-Then)",
                "body": """\
```python
def test_apply_discount_reduces_total():
    # Arrange (Given)
    cart = Cart(items=[Item("Widget", price=100)])
    discount = Discount(percent=20)

    # Act (When)
    cart.apply_discount(discount)

    # Assert (Then)
    assert cart.total == 80
    assert cart.discount_applied is True
```

**Rules:**
- One logical assertion per test (related assertions OK)
- Test behavior, not implementation
- Tests should be independent (no shared mutable state)""",
            },
            {
                "heading": "Testing Pyramid / Trophy",
                "body": """\
```
       /  E2E  \\          Few: critical user paths
      /----------\\
     / Integration \\      More: API, DB, service boundaries
    /----------------\\
   /   Unit (logic)    \\  Most: pure functions, business rules
  /--------------------\\
 /   Static Analysis    \\  Baseline: types, lints
/========================\\
```

| Level | Speed | Scope | When |
|-------|-------|-------|------|
| Static | Instant | Types, lints | Every save |
| Unit | ms | Single function/class | Every commit |
| Integration | seconds | Service boundaries | Every PR |
| E2E | minutes | Full user flows | Pre-deploy |""",
            },
            {
                "heading": "Test Doubles",
                "body": """\
| Type | Purpose | Example |
|------|---------|---------|
| **Stub** | Return fixed data | `stub_repo.get_user = lambda id: User("test")` |
| **Mock** | Verify interactions | `mock_email.send.assert_called_once()` |
| **Fake** | Working implementation (simplified) | In-memory database |
| **Spy** | Record calls, delegate to real | Wrap real service, check call count |

**Prefer fakes over mocks** for complex dependencies.
**Never mock what you don't own** — wrap third-party APIs in your own interface.""",
            },
            {
                "heading": "Anti-Patterns to Avoid",
                "body": """\
| Anti-Pattern | Better |
|-------------|--------|
| Testing implementation details | Test observable behavior |
| Flaky tests (time, network) | Use clocks, stubs, deterministic data |
| Shared mutable test state | Fresh fixtures per test |
| Giant test setup | Builder/factory patterns |
| No assertions (test runs = passes) | Always assert expected outcomes |
| Testing trivial code (getters) | Focus on logic with branches |
| Copy-paste test code | Extract helpers / parameterize |""",
            },
        ],
    },
    {
        "filename": "code-review-standards",
        "title": "Code Review Standards",
        "meta": {
            "scope": "Review process, checklist, feedback etiquette",
            "authority": "Google Engineering Practices, Thoughtbot Code Review Guide",
            "applies_to": "All pull requests and merge requests",
        },
        "sections": [
            {
                "heading": "Author Checklist (Before Requesting Review)",
                "body": """\
- [ ] Self-reviewed the entire diff
- [ ] PR is small (< 400 lines, single purpose)
- [ ] Descriptive title (conventional commit format)
- [ ] Description: What, Why, How, Testing approach
- [ ] All CI checks pass (lint, test, build)
- [ ] No commented-out code or debug statements
- [ ] No merge conflicts
- [ ] Screenshots/recordings for UI changes""",
            },
            {
                "heading": "Reviewer Checklist",
                "body": """\
**Correctness:**
- Does the code do what the PR description claims?
- Are edge cases handled?
- Are errors handled properly (not swallowed)?

**Design:**
- Right level of abstraction?
- Single Responsibility — does each function/class do one thing?
- Would a simpler approach work?

**Security:**
- Input validated at boundaries?
- No secrets in code?
- SQL injection / XSS risks?

**Performance:**
- N+1 queries?
- Unnecessary allocations in hot paths?
- Missing indexes for new queries?

**Maintainability:**
- Clear naming?
- Would a new team member understand this?
- Tests cover the change?""",
            },
            {
                "heading": "Feedback Etiquette",
                "body": """\
| Do | Don't |
|----|-------|
| "Consider using X because..." | "This is wrong" |
| "Nit: rename to Y for clarity" | "Bad variable name" |
| Ask questions: "What happens if...?" | Make assumptions |
| Prefix: `nit:`, `suggestion:`, `blocking:` | Leave ambiguous severity |
| Approve with minor nits | Block on style preferences |
| Praise good patterns | Only point out negatives |

**Turnaround:** Review within 1 business day.
**Resolve promptly:** Author responds to all comments before re-requesting.""",
            },
        ],
    },
    {
        "filename": "documentation-standards",
        "title": "Documentation Standards",
        "meta": {
            "scope": "README, API docs, inline docs, architecture decision records",
            "authority": "Write the Docs, Diátaxis framework, ADR standard",
            "tools": "Markdown, JSDoc/TSDoc, Sphinx, Swagger/OpenAPI, typedoc",
        },
        "sections": [
            {
                "heading": "README Template",
                "body": """\
```markdown
# Project Name

One-line description of what this project does.

## Quick Start

\\`\\`\\`bash
git clone <url>
npm install
npm run dev
\\`\\`\\`

## Features
- Feature 1
- Feature 2

## Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Server port |

## Architecture
Brief description or link to architecture doc.

## Contributing
Link to CONTRIBUTING.md.

## License
MIT
```""",
            },
            {
                "heading": "Inline Documentation",
                "body": """\
**When to comment:**
- WHY, not WHAT (the code shows what)
- Complex algorithms or non-obvious logic
- Workarounds with links to issues/tickets
- Public API contracts (params, returns, throws)

**When NOT to comment:**
- Restating the code: `i += 1  # increment i`
- Commented-out code (delete it, git has history)
- TODO without a ticket number

```python
# Good: explains WHY
# Rate limit to 100 req/s per user to prevent abuse (see #1234)
limiter = RateLimiter(max_requests=100, window_seconds=1)

# Bad: restates WHAT
# Create a new rate limiter with 100 requests per second
limiter = RateLimiter(max_requests=100, window_seconds=1)
```""",
            },
            {
                "heading": "API Documentation",
                "body": """\
```yaml
# OpenAPI / Swagger for REST APIs
openapi: 3.0.3
paths:
  /api/users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
      responses:
        '200':
          description: List of users
```

**Rules:**
- Document every public endpoint
- Include request/response examples
- Document error responses (not just success)
- Keep docs in sync (generate from code when possible)""",
            },
            {
                "heading": "Architecture Decision Records",
                "body": """\
```markdown
# ADR-001: Use PostgreSQL for primary database

## Status
Accepted

## Context
We need a relational database that supports JSONB, full-text search,
and strong ACID guarantees.

## Decision
Use PostgreSQL 16 as the primary database.

## Consequences
- Pro: Rich feature set, mature ecosystem
- Pro: JSONB reduces need for separate document store
- Con: Operational complexity vs. SQLite for small deployments
```

Store in `docs/adr/` — one file per decision, numbered sequentially.""",
            },
        ],
    },
    {
        "filename": "sql-standards",
        "title": "SQL Coding Standards",
        "meta": {
            "scope": "Naming, query patterns, schema design, performance",
            "authority": "SQL Style Guide (Simon Holywell), Postgres conventions",
            "applies_to": "PostgreSQL, MySQL, SQLite, SQL Server",
        },
        "sections": [
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Table | `snake_case`, plural | `users`, `order_items` |
| Column | `snake_case` | `first_name`, `created_at` |
| Primary key | `id` | `users.id` |
| Foreign key | `singular_table_id` | `user_id`, `order_id` |
| Index | `idx_table_columns` | `idx_users_email` |
| Boolean column | `is_/has_` prefix | `is_active`, `has_verified` |
| Timestamp | `_at` suffix | `created_at`, `updated_at` |
| Enum-like | explicit values, not magic numbers | Use lookup table or CHECK |""",
            },
            {
                "heading": "Query Formatting",
                "body": """\
```sql
-- Keywords: UPPERCASE
-- Identifiers: lowercase snake_case
-- One clause per line
-- Indent subqueries and conditions

SELECT
    u.id,
    u.name,
    u.email,
    COUNT(o.id) AS order_count
FROM users u
INNER JOIN orders o
    ON o.user_id = u.id
WHERE u.is_active = true
    AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC
LIMIT 20;
```""",
            },
            {
                "heading": "Schema Design Rules",
                "body": """\
| Rule | Details |
|------|---------|
| Always have a primary key | Prefer `BIGINT GENERATED ALWAYS AS IDENTITY` |
| Add `created_at` / `updated_at` | Use `TIMESTAMPTZ DEFAULT NOW()` |
| Foreign keys always | Enforce referential integrity |
| Index foreign keys | JOINs use them constantly |
| Avoid `NULL` when possible | Use `NOT NULL` + sensible defaults |
| Normalize first, denormalize for performance | Don't premature optimize |
| Use migrations | Never modify schema by hand in production |""",
            },
            {
                "heading": "Performance Anti-Patterns",
                "body": """\
| Anti-Pattern | Better |
|-------------|--------|
| `SELECT *` | List only needed columns |
| No index on WHERE/JOIN cols | Add indexes |
| N+1 queries from app code | Use JOINs or batch queries |
| Implicit type conversion | Match types in comparisons |
| Functions in WHERE clause | Compute upfront or use expression index |
| Missing LIMIT on unbounded queries | Always paginate |
| `COUNT(*)` to check existence | Use `EXISTS(SELECT 1 ...)` |""",
            },
        ],
    },
    {
        "filename": "shell-standards",
        "title": "Shell / Bash Scripting Standards",
        "meta": {
            "scope": "Safe scripting, portability, error handling",
            "authority": "Google Shell Style Guide, ShellCheck wiki",
            "tools": "ShellCheck, shfmt, bats (testing)",
        },
        "sections": [
            {
                "heading": "Script Header",
                "body": """\
```bash
#!/usr/bin/env bash
#
# Description: Brief purpose of this script
# Usage: ./script.sh <arg1> [arg2]
#

set -euo pipefail  # ALWAYS — exit on error, undefined vars, pipe failures
```""",
            },
            {
                "heading": "Variable Rules",
                "body": """\
```bash
# ALWAYS quote variables
echo "$file"             # NOT: echo $file
rm -- "$path"            # -- prevents flag injection

# Use readonly for constants
readonly CONFIG_DIR="/etc/myapp"
readonly LOG_FILE="$CONFIG_DIR/app.log"

# Use local in functions
my_func() {
    local result
    result=$(compute_something)
    echo "$result"
}

# Use ${var} in strings for clarity
echo "Processing ${filename} in ${dir}/"
```""",
            },
            {
                "heading": "Safety Patterns",
                "body": """\
```bash
# Trap for cleanup
cleanup() { rm -f "$tmpfile"; }
trap cleanup EXIT
tmpfile=$(mktemp)

# Check dependencies
command -v jq >/dev/null 2>&1 || { echo "jq required" >&2; exit 1; }

# Validate inputs
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <filename>" >&2
    exit 1
fi
[[ -f "$1" ]] || { echo "File not found: $1" >&2; exit 1; }

# Use [[ ]] not [ ] (bash-specific but safer)
# Use $(cmd) not backticks `cmd`
```""",
            },
            {
                "heading": "Anti-Patterns",
                "body": """\
| Anti-Pattern | Better |
|-------------|--------|
| No `set -euo pipefail` | Always set strict mode |
| Unquoted variables | Always quote: `"$var"` |
| `cd dir; command` | `cd dir && command` or `(cd dir; command)` |
| Parsing `ls` output | Use globs: `for f in *.txt` |
| `cat file \\| grep` | `grep pattern file` |
| Backticks `` `cmd` `` | `$(cmd)` (nestable, readable) |
| `eval "$user_input"` | Never eval untrusted input |""",
            },
        ],
    },
    {
        "filename": "html-css-standards",
        "title": "HTML & CSS Standards",
        "meta": {
            "scope": "Semantic HTML, accessibility, CSS architecture, responsive design",
            "authority": "WCAG 2.2, BEM methodology, CUBE CSS, MDN best practices",
            "tools": "axe, Lighthouse, Stylelint, PurgeCSS",
        },
        "sections": [
            {
                "heading": "Semantic HTML",
                "body": """\
```html
<!-- Use semantic elements, not div soup -->
<header>          <!-- not <div class="header"> -->
<nav>             <!-- not <div class="nav"> -->
<main>            <!-- one per page, main content -->
<article>         <!-- self-contained content -->
<section>         <!-- thematic grouping with heading -->
<aside>           <!-- tangentially related -->
<footer>          <!-- not <div class="footer"> -->

<!-- Headings: proper hierarchy (never skip levels) -->
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
```""",
            },
            {
                "heading": "Accessibility (a11y) Essentials",
                "body": """\
| Rule | Implementation |
|------|---------------|
| Alt text on images | `<img alt="User profile photo">` (decorative: `alt=""`) |
| Labels on inputs | `<label for="email">` or `aria-label` |
| Keyboard navigation | All interactive elements focusable, logical tab order |
| Color contrast | 4.5:1 for text, 3:1 for large text (WCAG AA) |
| ARIA sparingly | Prefer semantic HTML; ARIA only when HTML isn't enough |
| Skip link | First focusable element skips to `<main>` |
| `lang` attribute | `<html lang="en">` |""",
            },
            {
                "heading": "CSS Naming (BEM)",
                "body": """\
```css
/* Block: standalone component */
.card { }

/* Element: part of a block */
.card__title { }
.card__body { }
.card__footer { }

/* Modifier: variation of block/element */
.card--featured { }
.card__title--large { }
```

**Rules:**
- One component per file
- Prefer custom properties over magic numbers
- Mobile-first: `min-width` media queries""",
            },
            {
                "heading": "CSS Custom Properties",
                "body": """\
```css
:root {
  /* Spacing scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;

  /* Colors */
  --color-primary: #3b82f6;
  --color-text: #1e293b;
  --color-bg: #ffffff;

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #e2e8f0;
    --color-bg: #0f172a;
  }
}
```""",
            },
        ],
    },
    {
        "filename": "docker-standards",
        "title": "Docker & Container Standards",
        "meta": {
            "scope": "Dockerfile best practices, compose patterns, security",
            "authority": "Docker Best Practices, CIS Docker Benchmark, Hadolint",
            "tools": "Hadolint, Trivy, Docker Scout, dive",
        },
        "sections": [
            {
                "heading": "Dockerfile Best Practices",
                "body": """\
```dockerfile
# 1. Use specific base image tags (never :latest in production)
FROM node:20.11-alpine AS builder

# 2. Use multi-stage builds to minimize image size
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# 3. Production stage — minimal image
FROM node:20.11-alpine AS runtime
WORKDIR /app

# 4. Run as non-root user
RUN addgroup -S app && adduser -S app -G app

# 5. Copy only what's needed
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# 6. Health check
HEALTHCHECK --interval=30s --timeout=3s \\
  CMD wget -qO- http://localhost:3000/health || exit 1

USER app
EXPOSE 3000
CMD ["node", "dist/index.js"]
```""",
            },
            {
                "heading": "Layer Optimization",
                "body": """\
| Rule | Why |
|------|-----|
| Order: least → most changing | Maximize cache hits |
| Merge RUN commands | Fewer layers, smaller image |
| `COPY package*.json` before `COPY .` | Cache dependency install layer |
| Use `.dockerignore` | Exclude `node_modules`, `.git`, `.env` |
| Clean up in same RUN | `apt install -y X && rm -rf /var/lib/apt/lists/*` |""",
            },
            {
                "heading": "Security Rules",
                "body": """\
| Rule | Implementation |
|------|---------------|
| Non-root user | `USER app` (never run as root) |
| Read-only filesystem | `--read-only` flag, mount tmp volumes |
| No secrets in image | Use build secrets, env vars at runtime |
| Scan images | `trivy image myapp:latest` in CI |
| Pin base image digest | `FROM node:20@sha256:abc...` for reproducibility |
| Minimal base | Alpine or distroless over full OS images |""",
            },
            {
                "heading": "Docker Compose Patterns",
                "body": """\
```yaml
services:
  api:
    build:
      context: .
      target: runtime
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/app
    depends_on:
      db: { condition: service_healthy }
    restart: unless-stopped
    deploy:
      resources:
        limits: { cpus: '1', memory: 512M }

  db:
    image: postgres:16-alpine
    volumes: [db_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
volumes:
  db_data:
```""",
            },
        ],
    },
    {
        "filename": "logging-observability-standards",
        "title": "Logging & Observability Standards",
        "meta": {
            "scope": "Structured logging, log levels, metrics, tracing",
            "authority": "12-Factor App, OpenTelemetry, ELK/Grafana best practices",
            "tools": "Pino, Winston, structlog, OpenTelemetry, Prometheus, Grafana",
        },
        "sections": [
            {
                "heading": "Structured Logging",
                "body": """\
```json
{
  "timestamp": "2024-03-15T10:30:00.000Z",
  "level": "error",
  "message": "Failed to process order",
  "service": "order-service",
  "request_id": "abc-123",
  "user_id": 456,
  "order_id": 789,
  "error": "PaymentDeclined",
  "duration_ms": 1230
}
```

**Rules:**
- JSON format for machine parsing
- Always include: timestamp, level, message, service, request_id
- Add context fields (user_id, order_id) for traceability
- One log entry per event (not multi-line)""",
            },
            {
                "heading": "Log Levels",
                "body": """\
| Level | When | Example |
|-------|------|---------|
| `ERROR` | Action needed, something failed | DB connection lost, payment failed |
| `WARN` | Concerning but handled | Retry succeeded, rate limit approaching |
| `INFO` | Business events, milestones | User registered, order completed |
| `DEBUG` | Developer diagnostics | Query executed, cache hit/miss |
| `TRACE` | Very verbose (rarely in production) | Function entry/exit, full payloads |

**Production default:** `INFO`
**Never log:** passwords, tokens, full credit cards, PII in plain text""",
            },
            {
                "heading": "What to Log",
                "body": """\
| Log | Don't Log |
|-----|-----------|
| Request start/end with duration | Request/response bodies (PII risk) |
| Authentication success/failure | Passwords, tokens, session IDs |
| Authorization failures | Full credit card numbers |
| External service calls + latency | Health check successes (too noisy) |
| Error details + stack trace | Expected/handled errors at ERROR level |
| Business events (order placed) | Every loop iteration |""",
            },
            {
                "heading": "Observability Pillars",
                "body": """\
| Pillar | What | Tool Examples |
|--------|------|---------------|
| **Logs** | Discrete events | ELK, Loki, CloudWatch |
| **Metrics** | Aggregated measurements | Prometheus, Grafana, Datadog |
| **Traces** | Request flow across services | Jaeger, Zipkin, OpenTelemetry |

**Key Metrics to Track:**
- Request rate (req/s)
- Error rate (4xx, 5xx)
- Latency (p50, p95, p99)
- Saturation (CPU, memory, connections)""",
            },
        ],
    },
    {
        "filename": "php-standards",
        "title": "PHP Coding Standards",
        "meta": {
            "scope": "PSR standards, modern PHP 8.x patterns",
            "authority": "PSR-1, PSR-4, PSR-12, PHP-FIG",
            "tools": "PHP-CS-Fixer, PHPStan, Psalm, Rector",
        },
        "sections": [
            {
                "heading": "PSR Standards Summary",
                "body": """\
| PSR | Name | Key Points |
|-----|------|-----------|
| PSR-1 | Basic Coding | UTF-8, `<?php` tags, PascalCase classes |
| PSR-4 | Autoloading | Namespace = directory structure |
| PSR-12 | Extended Coding | Indentation, braces, line length |
| PSR-7 | HTTP Messages | Request/Response interfaces |
| PSR-11 | Container | Dependency injection interface |
| PSR-15 | HTTP Handlers | Middleware interface |""",
            },
            {
                "heading": "Naming Conventions",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Class | `PascalCase` | `UserService` |
| Method | `camelCase` | `getUserById()` |
| Property | `camelCase` | `$userName` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| Namespace | `PascalCase` | `App\\Services` |
| File | `PascalCase` (matches class) | `UserService.php` |""",
            },
            {
                "heading": "Modern PHP Patterns",
                "body": """\
```php
<?php
declare(strict_types=1);   // ALWAYS at top of every file

// Readonly classes (8.2+) for DTOs
readonly class UserDTO {
    public function __construct(
        public string $name,
        public string $email,
    ) {}
}

// Enums (8.1+) instead of class constants
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}

// Named arguments for clarity
str_contains(haystack: $text, needle: 'search');

// Null-safe operator
$city = $user?->address?->city;
```""",
            },
        ],
    },
    {
        "filename": "swift-kotlin-standards",
        "title": "Swift & Kotlin Coding Standards",
        "meta": {
            "scope": "Mobile development conventions for iOS and Android",
            "authority": "Swift API Design Guidelines, Kotlin Coding Conventions",
            "tools": "SwiftLint, ktlint, detekt",
        },
        "sections": [
            {
                "heading": "Swift Naming",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Type / Protocol | `PascalCase` | `UserProfile`, `Drawable` |
| Method / Property | `camelCase` | `makeNoise()`, `isActive` |
| Factory method | `make` prefix | `makeIterator()` |
| Boolean | `is/has/should` prefix | `isEmpty`, `canEdit` |
| Protocol (capability) | `-able/-ible` suffix | `Codable`, `Hashable` |

**Swift API Design Guidelines:**
- Clarity at the point of use
- Prefer method names that read as English phrases
- `func move(from start: Point, to end: Point)` — label all arguments""",
            },
            {
                "heading": "Kotlin Naming",
                "body": """\
| Element | Convention | Example |
|---------|-----------|---------|
| Class / Object | `PascalCase` | `UserViewModel` |
| Function / Property | `camelCase` | `fetchUser()`, `isActive` |
| Constant | `UPPER_SNAKE` or `camelCase` | Top: `MAX_COUNT`, local: `maxCount` |
| Package | `lowercase.dotted` | `com.example.feature.user` |
| Backing property | `_prefix` | `private val _users = MutableStateFlow(...)` |
| Flow / LiveData | no `get` prefix | `val users: StateFlow<List<User>>` |""",
            },
            {
                "heading": "Shared Mobile Patterns",
                "body": """\
| Pattern | Do | Don't |
|---------|-----|-------|
| Nullability | Use platform null safety (`?`, `!!` sparingly) | Force unwrap everywhere |
| Immutability | `val`/`let` by default | `var` unless mutation needed |
| Error handling | Result types, sealed classes | Generic catch-all |
| Dependency injection | Constructor injection | Service locator |
| Architecture | MVVM / MVI with clean layers | God Activity / ViewController |
| Async | Coroutines (Kotlin) / async-await (Swift) | Callback pyramids |""",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Generator (same engine as generate_language_references.py)
# ---------------------------------------------------------------------------


def render_standard(std: dict) -> str:
    """Render a standard definition to a markdown string."""
    lines = []

    lines.append(f"# {std['title']}")
    lines.append("")

    meta = std["meta"]
    meta_keys = list(meta.keys())
    first_key = meta_keys[0]
    first_label = first_key.replace("_", " ").title()
    lines.append(f"## {first_label}: {meta[first_key]}")

    for key in meta_keys[1:]:
        label = key.replace("_", " ").title()
        lines.append(f"**{label}:** {meta[key]}  ")

    lines.append("")

    for section in std["sections"]:
        lines.append(f"## {section['heading']}")
        lines.append("")
        lines.append(section["body"])
        lines.append("")

    return "\n".join(lines)


def generate(
    standards: list[dict],
    output_dir: Path,
    selected: Optional[list[str]] = None,
    force: bool = False,
) -> tuple[int, int, int]:
    """Generate standards files. Returns (created, skipped, errors)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    errors = 0

    for std in standards:
        filename = std["filename"]

        if selected and filename not in selected:
            continue

        filepath = output_dir / f"{filename}.md"

        if filepath.exists() and not force:
            print(f"  SKIP  {filepath.name} (exists, use --force to overwrite)")
            skipped += 1
            continue

        try:
            content = render_standard(std)
            filepath.write_text(content, encoding="utf-8")
            print(f"  CREATE {filepath.name} ({len(content):,} bytes)")
            created += 1
        except Exception as e:
            print(f"  ERROR  {filepath.name}: {e}")
            errors += 1

    return created, skipped, errors


def main():
    parser = argparse.ArgumentParser(
        description="Generate coding standards reference cards for Piddy's knowledge base"
    )
    parser.add_argument(
        "standards",
        nargs="*",
        help="Specific standards to generate (default: all)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available standards and exit"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing files"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})",
    )

    args = parser.parse_args()

    if args.list:
        print(f"Available standards ({len(STANDARDS)}):")
        for std in STANDARDS:
            meta = std["meta"]
            first_val = list(meta.values())[0]
            print(f"  {std['filename']:35s} {first_val}")
        return

    print(f"Generating coding standards in {args.output}/")
    print()

    selected = args.standards if args.standards else None
    created, skipped, errors = generate(STANDARDS, args.output, selected, args.force)

    print()
    print(f"Done: {created} created, {skipped} skipped, {errors} errors")
    print(f"Total available: {len(STANDARDS)} standards")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
