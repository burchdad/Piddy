#!/usr/bin/env python3
"""
Language Reference Card Generator for Piddy

Generates comprehensive, consistent language reference cards
in library/languages/ for Piddy's knowledge base.

Usage:
    python generate_language_references.py              # Generate all
    python generate_language_references.py --list       # List available languages
    python generate_language_references.py python rust   # Generate specific ones
    python generate_language_references.py --force      # Overwrite existing files

Each language is defined as structured data with sections containing
code examples, tables, and explanatory text. The generator produces
consistent markdown files that Piddy's KB ingestion picks up automatically.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path(__file__).parent / "library" / "languages"

# ---------------------------------------------------------------------------
# Language definitions
# ---------------------------------------------------------------------------
# Each language dict has:
#   filename: str - output filename (without .md)
#   title:    str - display title
#   meta:     dict - header metadata (language, paradigm, typing, runtime/compiled)
#   sections: list[dict] - ordered content sections
#       Each section: { heading: str, body: str }
# ---------------------------------------------------------------------------

LANGUAGES = [
    # ── Core Languages ─────────────────────────────────────────────────
    {
        "filename": "python",
        "title": "Python Quick Reference",
        "meta": {
            "language": "Python 3.11+",
            "paradigm": "Multi-paradigm (OOP, functional, procedural, structured)",
            "typing": "Dynamic, strong",
            "runtime": "CPython interpreter, also PyPy, GraalPy",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
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
```""",
            },
            {
                "heading": "Control Flow",
                "body": """\
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
```""",
            },
            {
                "heading": "OOP",
                "body": """\
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
```""",
            },
            {
                "heading": "Async",
                "body": """\
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
```""",
            },
            {
                "heading": "Standard Library Highlights",
                "body": """\
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
| `argparse` | CLI argument parsing |""",
            },
            {
                "heading": "Package Management",
                "body": """\
```bash
pip install package
pip install -r requirements.txt
python -m venv .venv
pip freeze > requirements.txt
# Modern: pyproject.toml + pip install -e .
```""",
            },
            {
                "heading": "Common Patterns",
                "body": """\
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
```""",
            },
        ],
    },
    {
        "filename": "javascript",
        "title": "JavaScript Quick Reference",
        "meta": {
            "language": "JavaScript (ES2024)",
            "paradigm": "Multi-paradigm (OOP, functional, event-driven)",
            "typing": "Dynamic, weak",
            "runtime": "V8 (Chrome/Node), SpiderMonkey (Firefox), JavaScriptCore (Safari)",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```javascript
// Variables
const name = "Piddy";       // block-scoped, no reassign
let count = 0;               // block-scoped, reassignable
// var — avoid (function-scoped, hoisted)

// Template literals
console.log(`Hello ${name}, count=${count}`);

// Destructuring
const { port, host = "localhost" } = config;
const [first, ...rest] = items;
const { data: result } = response;

// Spread
const merged = { ...defaults, ...overrides };
const all = [...arr1, ...arr2];

// Optional chaining & nullish coalescing
const city = user?.address?.city ?? "unknown";

// Arrow functions
const double = (x) => x * 2;
const greet = (name) => `Hello ${name}`;
```""",
            },
            {
                "heading": "Data Structures",
                "body": """\
```javascript
// Array methods
arr.map(x => x * 2)
arr.filter(x => x > 0)
arr.reduce((acc, x) => acc + x, 0)
arr.find(x => x.id === id)
arr.findIndex(x => x.id === id)
arr.some(x => x > 10)
arr.every(x => x > 0)
arr.flat(Infinity)
arr.flatMap(x => x.items)
arr.at(-1)                    // last element

// Object
Object.keys(obj)  /  Object.values(obj)  /  Object.entries(obj)
Object.fromEntries(entries)
structuredClone(obj)          // deep clone

// Map & Set
const map = new Map([["key", "val"]]);
map.get("key"); map.set("k", "v"); map.has("k");
const set = new Set([1, 2, 3]);
set.add(4); set.has(2); set.delete(1);
```""",
            },
            {
                "heading": "Async",
                "body": """\
```javascript
// Promises
fetch(url)
  .then(res => res.json())
  .then(data => process(data))
  .catch(err => handle(err))
  .finally(() => cleanup());

// async/await
async function getData(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed:", err.message);
  }
}

// Parallel
const [users, posts] = await Promise.all([
  fetch("/api/users").then(r => r.json()),
  fetch("/api/posts").then(r => r.json()),
]);

// Promise.allSettled — doesn't short-circuit on failure
const results = await Promise.allSettled(promises);
```""",
            },
            {
                "heading": "Classes",
                "body": """\
```javascript
class Animal {
  #name;  // private field
  static count = 0;

  constructor(name) {
    this.#name = name;
    Animal.count++;
  }

  get name() { return this.#name; }

  speak() { return `${this.#name} speaks`; }
}

class Dog extends Animal {
  #breed;
  constructor(name, breed) {
    super(name);
    this.#breed = breed;
  }
  speak() { return `${this.name} barks`; }
}
```""",
            },
            {
                "heading": "Modules",
                "body": """\
```javascript
// Named exports
export const PI = 3.14;
export function add(a, b) { return a + b; }

// Default export
export default class Router { }

// Import
import Router from "./router.js";
import { add, PI } from "./math.js";
import * as utils from "./utils.js";

// Dynamic import
const module = await import("./heavy.js");
```""",
            },
            {
                "heading": "Modern Features (ES2022-2024)",
                "body": """\
```javascript
// Top-level await (modules)
const config = await loadConfig();

// Array grouping
const grouped = Object.groupBy(items, item => item.category);

// Structured clone
const copy = structuredClone(original);
```""",
            },
            {
                "heading": "Error Handling Patterns",
                "body": """\
```javascript
// Custom errors
class AppError extends Error {
  constructor(message, code) {
    super(message);
    this.name = "AppError";
    this.code = code;
  }
}

// Result pattern (no exceptions)
function safeParse(json) {
  try {
    return { ok: true, value: JSON.parse(json) };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}
```""",
            },
        ],
    },
    {
        "filename": "typescript",
        "title": "TypeScript Quick Reference",
        "meta": {
            "language": "TypeScript 5.x",
            "paradigm": "Multi-paradigm with static type system",
            "typing": "Static, structural",
            "compiled": "JavaScript (any target)",
        },
        "sections": [
            {
                "heading": "Type Basics",
                "body": """\
```typescript
// Primitives
let name: string = "Piddy";
let age: number = 1;
let active: boolean = true;

// Arrays & tuples
let nums: number[] = [1, 2, 3];
let pair: [string, number] = ["age", 25];
let readonly: readonly number[] = [1, 2, 3];

// Object types
type User = {
  id: number;
  name: string;
  email?: string;           // optional
  readonly createdAt: Date;  // immutable
};

// Union & intersection
type Result = Success | Failure;
type Admin = User & { permissions: string[] };

// Literal types
type Direction = "north" | "south" | "east" | "west";
```""",
            },
            {
                "heading": "Generics",
                "body": """\
```typescript
function identity<T>(value: T): T { return value; }

// Constraints
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}

// Conditional types
type IsString<T> = T extends string ? true : false;

// Infer
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
```""",
            },
            {
                "heading": "Utility Types",
                "body": """\
```typescript
Partial<T>          // all properties optional
Required<T>         // all properties required
Readonly<T>         // all properties readonly
Pick<T, K>          // select properties
Omit<T, K>          // exclude properties
Record<K, V>        // construct object type
Extract<T, U>       // extract union members
Exclude<T, U>       // remove union members
NonNullable<T>      // remove null/undefined
ReturnType<F>       // function return type
Parameters<F>       // function parameter types
Awaited<T>          // unwrap Promise
```""",
            },
            {
                "heading": "Discriminated Unions",
                "body": """\
```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":   return Math.PI * s.radius ** 2;
    case "rect":     return s.width * s.height;
    case "triangle": return 0.5 * s.base * s.height;
  }
}
```""",
            },
            {
                "heading": "Mapped & Template Literal Types",
                "body": """\
```typescript
// Mapped type
type Optional<T> = { [K in keyof T]?: T[K] };

// Key remapping
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

// Template literal
type EventName = `on${Capitalize<string>}`;
```""",
            },
            {
                "heading": "Key tsconfig Options",
                "body": """\
```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```""",
            },
        ],
    },
    {
        "filename": "java",
        "title": "Java Quick Reference",
        "meta": {
            "language": "Java 21+ (LTS)",
            "paradigm": "OOP, functional elements",
            "typing": "Static, strong, nominal",
            "runtime": "JVM (HotSpot, GraalVM)",
        },
        "sections": [
            {
                "heading": "Modern Syntax (Java 17-21)",
                "body": """\
```java
// Records — immutable data classes
record Point(double x, double y) {
    Point {
        if (x < 0 || y < 0) throw new IllegalArgumentException();
    }
}

// Sealed classes — restricted hierarchy
sealed interface Shape permits Circle, Rectangle {}
record Circle(double radius) implements Shape {}
record Rectangle(double w, double h) implements Shape {}

// Pattern matching (switch)
String describe(Shape s) {
    return switch (s) {
        case Circle c when c.radius() > 10   -> "big circle";
        case Circle c                         -> "circle r=" + c.radius();
        case Rectangle r                      -> "rect " + r.w() + "x" + r.h();
    };
}

// Text blocks
String json = \"\"\"
    {
        "name": "%s",
        "port": %d
    }
    \"\"\".formatted(name, port);

// Virtual threads (Project Loom)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
        executor.submit(() -> doWork(i))
    );
}
```""",
            },
            {
                "heading": "Collections & Streams",
                "body": """\
```java
// Immutable collections
var list = List.of("a", "b", "c");
var set = Set.of(1, 2, 3);
var map = Map.of("k1", "v1", "k2", "v2");

// Streams
var names = users.stream()
    .filter(u -> u.isActive())
    .map(User::name)
    .sorted()
    .distinct()
    .toList();  // Java 16+

// Collectors
var grouped = items.stream()
    .collect(Collectors.groupingBy(Item::category));

// Optional
Optional<User> user = findById(id);
String name = user.map(User::name).orElse("anonymous");
user.ifPresent(u -> process(u));
```""",
            },
            {
                "heading": "Concurrency",
                "body": """\
```java
// CompletableFuture
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(data -> transform(data))
    .thenAccept(result -> save(result))
    .exceptionally(ex -> { log(ex); return null; });

// Structured concurrency (preview)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user  = scope.fork(() -> findUser(id));
    var order = scope.fork(() -> findOrder(id));
    scope.join().throwIfFailed();
    return new Response(user.get(), order.get());
}
```""",
            },
            {
                "heading": "Build Tools",
                "body": """\
```bash
# Maven
mvn clean package
mvn dependency:tree

# Gradle (Kotlin DSL)
./gradlew build
./gradlew test
```""",
            },
        ],
    },
    {
        "filename": "csharp",
        "title": "C# Quick Reference",
        "meta": {
            "language": "C# 12 / .NET 8+",
            "paradigm": "OOP, functional elements, concurrent",
            "typing": "Static, strong, nominal",
            "runtime": ".NET CLR (cross-platform)",
        },
        "sections": [
            {
                "heading": "Modern Syntax",
                "body": """\
```csharp
// Top-level statements
Console.WriteLine("Hello Piddy");

// Records
record Person(string Name, int Age);
record struct Point(double X, double Y);

// Primary constructors (C# 12)
class UserService(IRepository repo, ILogger<UserService> logger)
{
    public User? Find(int id) => repo.GetById(id);
}

// Pattern matching
string Classify(object obj) => obj switch
{
    int n when n > 0   => "positive",
    int n when n < 0   => "negative",
    int                => "zero",
    string s           => $"string: {s}",
    null               => "null",
    _                  => "unknown"
};

// Collection expressions (C# 12)
int[] nums = [1, 2, 3, 4, 5];
List<string> names = ["Alice", "Bob"];

// Nullable reference types
string? nullable = null;
string nonNull = nullable ?? "default";
```""",
            },
            {
                "heading": "LINQ",
                "body": """\
```csharp
var result = users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .Select(u => new { u.Name, u.Email })
    .ToList();

var grouped = orders.GroupBy(o => o.Category)
    .Select(g => new { Category = g.Key, Total = g.Sum(o => o.Amount) });
```""",
            },
            {
                "heading": "Async/Await",
                "body": """\
```csharp
async Task<User> GetUserAsync(int id, CancellationToken ct = default)
{
    var response = await httpClient.GetAsync($"/api/users/{id}", ct);
    response.EnsureSuccessStatusCode();
    return await response.Content.ReadFromJsonAsync<User>(ct)
        ?? throw new InvalidOperationException("User not found");
}

// Parallel async
var tasks = ids.Select(id => GetUserAsync(id));
var users = await Task.WhenAll(tasks);
```""",
            },
            {
                "heading": "Dependency Injection",
                "body": """\
```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();

var app = builder.Build();
app.MapGet("/users/{id}", async (int id, IUserService svc) =>
    await svc.GetAsync(id) is { } user ? Results.Ok(user) : Results.NotFound());
app.Run();
```""",
            },
            {
                "heading": "CLI",
                "body": """\
```bash
dotnet new webapi -n MyApi
dotnet build
dotnet run
dotnet test
dotnet publish -c Release
```""",
            },
        ],
    },
    # ── Systems Languages ──────────────────────────────────────────────
    {
        "filename": "c-cpp",
        "title": "C / C++ Quick Reference",
        "meta": {
            "language": "C17 / C++23",
            "paradigm": "Procedural (C), Multi-paradigm (C++)",
            "typing": "Static, strong (with implicit conversions)",
            "compiled": "GCC, Clang, MSVC",
        },
        "sections": [
            {
                "heading": "C Essentials",
                "body": """\
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

// Fixed-width integers
int32_t x = 42;
uint8_t byte = 0xFF;
size_t len = strlen(str);

// Pointers
int val = 10;
int *ptr = &val;
int deref = *ptr;

// Dynamic memory
int *buf = malloc(n * sizeof(int));
if (!buf) { /* handle OOM */ }
free(buf);
buf = NULL;

// Structs
typedef struct {
    char name[64];
    int age;
} Person;

Person p = {.name = "Piddy", .age = 1};  // designated init (C99)

// Function pointers
typedef int (*Comparator)(const void*, const void*);
qsort(arr, n, sizeof(int), compare_ints);
```""",
            },
            {
                "heading": "C++ Modern (C++17/20/23)",
                "body": """\
```cpp
#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <variant>
#include <ranges>
#include <span>
#include <expected>   // C++23

// Auto & structured bindings
auto [key, value] = *map.begin();

// Smart pointers
auto ptr = std::make_unique<Widget>(args...);
auto shared = std::make_shared<Config>();

// std::optional
std::optional<int> find(const std::string& key) {
    if (auto it = map.find(key); it != map.end())
        return it->second;
    return std::nullopt;
}

// Ranges (C++20)
auto evens = numbers | std::views::filter([](int n){ return n%2==0; })
                     | std::views::transform([](int n){ return n*2; })
                     | std::views::take(10);

// Concepts (C++20)
template<typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

// Lambdas
auto add = [](int a, int b) { return a + b; };

// std::format (C++20)
auto msg = std::format("Hello {}, port={}", name, port);
```""",
            },
            {
                "heading": "Containers",
                "body": """\
| Container | Access | Insert | Find | Notes |
|-----------|--------|--------|------|-------|
| `vector` | O(1) | O(1)* | O(n) | Default choice |
| `array` | O(1) | - | O(n) | Fixed size |
| `deque` | O(1) | O(1)* | O(n) | Front/back insert |
| `unordered_map` | O(1) | O(1) | O(1) | Hash map |
| `map` | O(log n) | O(log n) | O(log n) | Red-black tree |
| `unordered_set` | - | O(1) | O(1) | Hash set |
| `span` | O(1) | - | - | Non-owning view |""",
            },
            {
                "heading": "Build Tools",
                "body": """\
```bash
# CMake (standard)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# Compiler flags
g++ -std=c++23 -O2 -Wall -Wextra -Wpedantic main.cpp -o main

# Package managers
vcpkg install fmt spdlog
conan install . --build=missing
```""",
            },
            {
                "heading": "Memory Safety Patterns",
                "body": """\
```cpp
// RAII — resources tied to scope
{
    std::lock_guard lock(mutex);
    // mutex released when lock goes out of scope
}

// Rule of 0: use smart pointers, no manual resource mgmt
class Widget {
    std::unique_ptr<Impl> pImpl;
public:
    Widget();
    ~Widget() = default;
};

// span for safe array views
void process(std::span<const int> data) {
    for (int x : data) { /* bounds-safe iteration */ }
}
```""",
            },
        ],
    },
    {
        "filename": "go",
        "title": "Go Quick Reference",
        "meta": {
            "language": "Go 1.22+",
            "paradigm": "Concurrent, procedural, structural typing",
            "typing": "Static, strong, inferred",
            "compiled": "Single binary, cross-compilation built in",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```go
package main

import (
    "fmt"
    "errors"
)

// Variables
var name string = "Piddy"
count := 42                    // short declaration
const MaxRetries = 3

// Functions — multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Closures
adder := func(x int) func(int) int {
    return func(y int) int { return x + y }
}
```""",
            },
            {
                "heading": "Structs & Interfaces",
                "body": """\
```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
}

func (u User) String() string {
    return fmt.Sprintf("%s <%s>", u.Name, u.Email)
}

// Interfaces — implicit satisfaction
type Reader interface {
    Read(p []byte) (n int, err error)
}
```""",
            },
            {
                "heading": "Generics (1.18+)",
                "body": """\
```go
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

type Number interface {
    ~int | ~float64 | ~int64
}
```""",
            },
            {
                "heading": "Concurrency",
                "body": """\
```go
// Goroutines
go processItem(item)

// Channels
ch := make(chan string)
ch := make(chan int, 100)     // buffered

// Select
select {
case msg := <-msgCh:
    handle(msg)
case <-time.After(5 * time.Second):
    fmt.Println("timeout")
case <-ctx.Done():
    return ctx.Err()
}

// errgroup (structured concurrency)
g, ctx := errgroup.WithContext(ctx)
for _, url := range urls {
    url := url
    g.Go(func() error { return fetch(ctx, url) })
}
if err := g.Wait(); err != nil { /* handle */ }
```""",
            },
            {
                "heading": "Error Handling",
                "body": """\
```go
var ErrNotFound = errors.New("not found")

// Wrapping
if err != nil {
    return fmt.Errorf("loading config: %w", err)
}

// Checking
if errors.Is(err, ErrNotFound) { /* ... */ }
var valErr *ValidationError
if errors.As(err, &valErr) { /* use valErr.Field */ }
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
go build ./...
go test ./... -v -race
go mod init module-name
go mod tidy
go vet ./...
golangci-lint run
```""",
            },
        ],
    },
    {
        "filename": "rust",
        "title": "Rust Quick Reference",
        "meta": {
            "language": "Rust (2024 Edition)",
            "paradigm": "Systems, functional, concurrent",
            "typing": "Static, strong, affine (ownership)",
            "compiled": "LLVM backend, no runtime/GC",
        },
        "sections": [
            {
                "heading": "Ownership & Borrowing",
                "body": """\
```rust
// Ownership rules:
// 1. Each value has exactly one owner
// 2. When owner goes out of scope, value is dropped
// 3. Value can be moved or borrowed

let s1 = String::from("hello");
let s2 = s1;              // s1 MOVED

// Borrowing (immutable — multiple allowed)
fn len(s: &str) -> usize { s.len() }

// Mutable borrow (exclusive — only one at a time)
fn push(v: &mut Vec<i32>, val: i32) { v.push(val); }

// Lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```""",
            },
            {
                "heading": "Enums & Structs",
                "body": """\
```rust
// Enum (algebraic data type)
enum Command {
    Quit,
    Move { x: i32, y: i32 },
    Say(String),
}

#[derive(Debug, Clone, PartialEq)]
struct User {
    name: String,
    age: u32,
    active: bool,
}

impl User {
    fn new(name: impl Into<String>) -> Self {
        Self { name: name.into(), age: 0, active: true }
    }
}
```""",
            },
            {
                "heading": "Traits",
                "body": """\
```rust
trait Summary {
    fn summarize(&self) -> String;
    fn preview(&self) -> String {
        format!("{}...", &self.summarize()[..50])
    }
}

fn notify(item: &impl Summary) { println!("{}", item.summarize()); }
fn process<T>(item: T) where T: Summary + Clone + Send { /* ... */ }
```""",
            },
            {
                "heading": "Error Handling",
                "body": """\
```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("io error")]
    Io(#[from] std::io::Error),
}

// ? operator propagates errors
fn load_config(path: &str) -> Result<Config, AppError> {
    let content = std::fs::read_to_string(path)?;
    let config = serde_json::from_str(&content)?;
    Ok(config)
}
```""",
            },
            {
                "heading": "Async",
                "body": """\
```rust
#[tokio::main]
async fn main() {
    let result = fetch_data("url").await;
}

// Concurrent tasks
let (a, b) = tokio::join!(task_a(), task_b());

let handle = tokio::spawn(async { heavy_computation().await });
let result = handle.await?;
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
cargo new project-name
cargo build --release
cargo test
cargo clippy              # lints
cargo fmt                 # format
cargo add serde tokio
```""",
            },
        ],
    },
    # ── Scripting Languages ────────────────────────────────────────────
    {
        "filename": "ruby",
        "title": "Ruby Quick Reference",
        "meta": {
            "language": "Ruby 3.3+",
            "paradigm": "OOP (everything is an object), functional elements",
            "typing": "Dynamic, strong, duck typing",
            "runtime": "CRuby (MRI), JRuby, TruffleRuby",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```ruby
name = "Piddy"
config = { host: "localhost", port: 8889 }
nums = [1, 2, 3, 4, 5]

# Symbols, string interpolation
puts "Hello #{name}"
status = :active

# Blocks
[1, 2, 3].each { |n| puts n }

# Lambda (strict arity)
greet = ->(name) { "Hello #{name}" }

# Yield
def with_logging
  puts "start"
  result = yield
  puts "end"
  result
end
```""",
            },
            {
                "heading": "Enumerable",
                "body": """\
```ruby
nums.map { |n| n * 2 }
nums.select { |n| n.even? }
nums.reduce(0) { |sum, n| sum + n }
nums.group_by { |n| n.even? ? :even : :odd }
nums.flat_map { |n| [n, n*2] }
nums.tally
```""",
            },
            {
                "heading": "Classes & Modules",
                "body": """\
```ruby
class Animal
  attr_reader :name
  attr_accessor :age

  def initialize(name, age = 0)
    @name = name
    @age = age
  end
end

class Dog < Animal
  def speak
    "#{name} says Woof!"
  end
end

module Cacheable
  def cache_key
    "#{self.class.name}:#{id}"
  end
end

# Data class (Ruby 3.2+, immutable)
Person = Data.define(:name, :age)
```""",
            },
            {
                "heading": "Pattern Matching (3.0+)",
                "body": """\
```ruby
case response
in { status: 200, body: String => body }
  process(body)
in { status: 404 }
  not_found
in { status: (500..) }
  server_error
end
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
gem install bundler
bundle init
bundle install
rspec spec/
rubocop
```""",
            },
        ],
    },
    {
        "filename": "php",
        "title": "PHP Quick Reference",
        "meta": {
            "language": "PHP 8.3+",
            "paradigm": "OOP, procedural, functional elements",
            "typing": "Gradual typing (dynamic to static annotations)",
            "runtime": "Zend Engine, also Swoole for async",
        },
        "sections": [
            {
                "heading": "Modern Syntax (PHP 8.x)",
                "body": """\
```php
<?php
declare(strict_types=1);

// Named arguments
str_contains(haystack: $text, needle: "search");

// Match expression
$label = match($status) {
    200 => 'OK',
    404 => 'Not Found',
    500, 503 => 'Server Error',
    default => 'Unknown',
};

// Null handling
$city = $user?->address?->city;
$name = $input ?? 'default';

// Enums (8.1+)
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';
}
```""",
            },
            {
                "heading": "Classes",
                "body": """\
```php
// Readonly classes & constructor promotion (8.2+)
readonly class Point {
    public function __construct(
        public float $x,
        public float $y,
    ) {}
}

// Traits
trait HasTimestamps {
    public DateTime $createdAt;
    public DateTime $updatedAt;
}

class User implements Cacheable, JsonSerializable {
    use HasTimestamps;

    public function __construct(
        private readonly int $id,
        private string $name,
    ) {}
}

// Intersection & union types
function process(Countable&Iterator $items): int|false { }
```""",
            },
            {
                "heading": "Arrays & Functional",
                "body": """\
```php
$names = array_map(fn($u) => $u['name'], $users);
$adults = array_filter($users, fn($u) => $u['age'] >= 18);
$total = array_reduce($items, fn($sum, $i) => $sum + $i['price'], 0);

// Spread
$merged = [...$defaults, ...$overrides];

// Arrow functions (auto-capture)
$multiplier = 3;
$result = array_map(fn($n) => $n * $multiplier, $nums);
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
composer init
composer require package/name
phpunit
phpstan analyse
php-cs-fixer fix
```""",
            },
        ],
    },
    {
        "filename": "elixir",
        "title": "Elixir Quick Reference",
        "meta": {
            "language": "Elixir 1.16+ / Erlang/OTP 26+",
            "paradigm": "Functional, concurrent, distributed",
            "typing": "Dynamic, strong",
            "runtime": "BEAM VM (Erlang VM) — fault-tolerant, hot code swapping",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```elixir
# Pattern matching (= is match, not assignment)
{:ok, result} = {:ok, 42}
[head | tail] = [1, 2, 3]
%{name: name} = user

# Functions
defmodule Math do
  def add(a, b), do: a + b
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)
end

# Pipe operator
"  Hello World  "
|> String.trim()
|> String.downcase()
|> String.split()
|> Enum.join(" ")
```""",
            },
            {
                "heading": "Control Flow",
                "body": """\
```elixir
# Case
case HTTP.get(url) do
  {:ok, %{status: 200, body: body}} -> parse(body)
  {:ok, %{status: 404}} -> :not_found
  {:error, reason} -> {:error, reason}
end

# With (happy path chaining)
with {:ok, user} <- find_user(id),
     {:ok, account} <- find_account(user),
     {:ok, balance} <- get_balance(account) do
  {:ok, balance}
end
```""",
            },
            {
                "heading": "Processes & OTP",
                "body": """\
```elixir
# GenServer
defmodule Counter do
  use GenServer

  def start_link(initial \\\\ 0) do
    GenServer.start_link(__MODULE__, initial, name: __MODULE__)
  end

  def increment, do: GenServer.call(__MODULE__, :increment)

  @impl true
  def init(count), do: {:ok, count}

  @impl true
  def handle_call(:increment, _from, count), do: {:reply, count + 1, count + 1}
end

# Task (async)
task = Task.async(fn -> expensive_work() end)
result = Task.await(task)
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
mix new project_name
mix deps.get
mix compile
mix test
mix format
iex -S mix
```""",
            },
        ],
    },
    {
        "filename": "scala",
        "title": "Scala Quick Reference",
        "meta": {
            "language": "Scala 3.4+",
            "paradigm": "OOP + functional, concurrent",
            "typing": "Static, strong, inferred",
            "runtime": "JVM (also Scala.js, Scala Native)",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```scala
val name = "Piddy"          // immutable (preferred)
var count = 0                // mutable

// String interpolation
s"Hello $name, count=$count"

def add(a: Int, b: Int): Int = a + b

// Extension methods
extension (s: String)
  def greet: String = s"Hello $s"
```""",
            },
            {
                "heading": "Algebraic Data Types",
                "body": """\
```scala
enum Shape:
  case Circle(radius: Double)
  case Rectangle(w: Double, h: Double)

def area(s: Shape): Double = s match
  case Shape.Circle(r)        => Math.PI * r * r
  case Shape.Rectangle(w, h)  => w * h

case class User(name: String, age: Int)
val u2 = user.copy(age = 2)
```""",
            },
            {
                "heading": "Collections & For-Comprehensions",
                "body": """\
```scala
list.map(_ * 2)
list.filter(_ > 1)
list.foldLeft(0)(_ + _)
list.groupBy(_ % 2)

// For-comprehension
for
  user <- users
  if user.active
  order <- user.orders
yield order.total
```""",
            },
            {
                "heading": "Effect Handling",
                "body": """\
```scala
// Option
val opt: Option[Int] = Some(42)
opt.map(_ * 2).getOrElse(0)

// Either
def parse(s: String): Either[String, Int] =
  s.toIntOption.toRight(s"Invalid: $s")

// Try
Try(riskyOp()) match
  case Success(v) => use(v)
  case Failure(e) => handle(e)
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
sbt compile
sbt test
sbt run
scala-cli run script.sc
```""",
            },
        ],
    },
    {
        "filename": "r-programming",
        "title": "R Quick Reference",
        "meta": {
            "language": "R 4.3+",
            "paradigm": "Functional, statistical computing",
            "typing": "Dynamic, vector-oriented",
            "runtime": "GNU R, also Microsoft R Open",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```r
name <- "Piddy"
nums <- c(1, 2, 3, 4, 5)

# Vectorized operations
nums * 2            # c(2, 4, 6, 8, 10)
sum(nums)           # 15
sqrt(nums)          # element-wise

# Indexing (1-based!)
nums[1]             # first element
nums[nums > 3]      # filter: c(4, 5)

# Data frame
df <- data.frame(name = c("A", "B"), age = c(30, 25))
df$name
subset(df, age > 28)
```""",
            },
            {
                "heading": "Functions & Pipes",
                "body": """\
```r
add <- function(a, b = 0) { a + b }

# Apply family
sapply(nums, function(x) x^2)
lapply(list_of_dfs, nrow)

# Pipe (R 4.1+)
result <- nums |> sort() |> unique() |> head(5)

# Tidyverse pipe
library(dplyr)
result <- df %>%
  filter(age > 25) %>%
  arrange(desc(score)) %>%
  mutate(grade = ifelse(score > 90, "A", "B"))
```""",
            },
            {
                "heading": "Tidyverse (Data Science Stack)",
                "body": """\
```r
library(tidyverse)

df %>%
  filter(year >= 2020) %>%
  group_by(category) %>%
  summarize(count = n(), avg = mean(price, na.rm=TRUE)) %>%
  arrange(desc(count))

# ggplot2
ggplot(df, aes(x=age, y=score, color=group)) +
  geom_point() + geom_smooth(method="lm") + theme_minimal()
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```r
install.packages("package_name")
renv::init()
renv::snapshot()
testthat::test_dir("tests/")
```""",
            },
        ],
    },
    # ── Mobile Languages ───────────────────────────────────────────────
    {
        "filename": "swift",
        "title": "Swift Quick Reference",
        "meta": {
            "language": "Swift 5.9+",
            "paradigm": "OOP, functional, protocol-oriented",
            "typing": "Static, strong, inferred",
            "platforms": "iOS, macOS, watchOS, tvOS, Linux, Windows",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```swift
let name = "Piddy"          // constant (preferred)
var count = 0                // mutable

// Optionals
var email: String? = nil
let len = email?.count ?? 0
guard let email = email else { return }

// Closures
let sorted = names.sorted { $0 < $1 }
let mapped = nums.map { $0 * 2 }
```""",
            },
            {
                "heading": "Enums & Structs",
                "body": """\
```swift
enum NetworkError: Error {
    case notFound
    case serverError(code: Int, message: String)
}

struct User: Codable, Hashable {
    let id: Int
    var name: String
    var email: String?
}
```""",
            },
            {
                "heading": "Protocols",
                "body": """\
```swift
protocol Drawable {
    func draw()
}

extension Collection where Element: Numeric {
    var sum: Element { reduce(.zero, +) }
}

func makeShape() -> some Drawable { Circle() }    // opaque
func anyShape() -> any Drawable { shapes.first! }  // existential
```""",
            },
            {
                "heading": "Concurrency (async/await)",
                "body": """\
```swift
func fetchUser(id: Int) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Structured concurrency
async let user = fetchUser(id: 1)
async let posts = fetchPosts(userId: 1)
let (u, p) = try await (user, posts)

// Actor (thread-safe state)
actor Counter {
    private var value = 0
    func increment() -> Int { value += 1; return value }
}
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
swift build
swift test
swift run
swift package init --type executable
```""",
            },
        ],
    },
    {
        "filename": "kotlin",
        "title": "Kotlin Quick Reference",
        "meta": {
            "language": "Kotlin 2.0+",
            "paradigm": "OOP, functional, concurrent",
            "typing": "Static, strong, inferred, null-safe",
            "targets": "JVM, Android, Kotlin/Native, Kotlin/JS, Kotlin/Wasm",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```kotlin
val name = "Piddy"          // immutable
var count = 0                // mutable

// Null safety
var email: String? = null
val len = email?.length ?: 0

// When expression
val label = when (status) {
    200 -> "OK"
    in 400..499 -> "Client error"
    else -> "Unknown"
}

// Scope functions
user.let { println(it.name) }
user.apply { name = "New" }
```""",
            },
            {
                "heading": "Data Classes & Sealed Types",
                "body": """\
```kotlin
data class User(val id: Int, val name: String, val email: String? = null)
val u2 = user.copy(name = "Updated")

sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val message: String) : Result<Nothing>
    data object Loading : Result<Nothing>
}

fun <T> handle(result: Result<T>) = when (result) {
    is Result.Success -> process(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showSpinner()
}
```""",
            },
            {
                "heading": "Coroutines",
                "body": """\
```kotlin
import kotlinx.coroutines.*

suspend fun fetchUser(id: Int): User {
    return httpClient.get("/users/$id").body()
}

coroutineScope {
    val user = async { fetchUser(1) }
    val posts = async { fetchPosts(1) }
    Result(user.await(), posts.await())
}

// Flow
fun numbers(): Flow<Int> = flow {
    for (i in 1..10) { delay(100); emit(i) }
}

numbers().filter { it % 2 == 0 }.map { it * 2 }.collect { println(it) }
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
gradle build
gradle test
gradle run
kotlin script.main.kts
```""",
            },
        ],
    },
    {
        "filename": "dart",
        "title": "Dart Quick Reference",
        "meta": {
            "language": "Dart 3.3+ / Flutter 3.x",
            "paradigm": "OOP, functional elements",
            "typing": "Static, strong, sound null safety",
            "targets": "Mobile (iOS/Android), Web, Desktop via Flutter; Server",
        },
        "sections": [
            {
                "heading": "Syntax Essentials",
                "body": """\
```dart
var name = 'Piddy';
final port = 8889;           // runtime constant
const pi = 3.14159;          // compile-time constant
String? email;               // nullable

// Collection if/for
var filtered = [
  for (var item in items)
    if (item.isActive) item.name,
];

// Cascade
var button = Button()
  ..text = 'Click'
  ..color = Colors.blue
  ..onPressed = handleClick;
```""",
            },
            {
                "heading": "Sealed Classes & Pattern Matching (Dart 3)",
                "body": """\
```dart
sealed class Shape {}
class Circle extends Shape { final double radius; Circle(this.radius); }
class Rectangle extends Shape { final double w, h; Rectangle(this.w, this.h); }

double area(Shape shape) => switch (shape) {
  Circle(radius: var r)     => 3.14159 * r * r,
  Rectangle(w: var w, h: var h) => w * h,
};

// Records
(String, int) userInfo = ('Piddy', 1);
var (name, age) = userInfo;
```""",
            },
            {
                "heading": "Async",
                "body": """\
```dart
Future<User> fetchUser(int id) async {
  final response = await http.get(Uri.parse('/api/users/$id'));
  if (response.statusCode != 200) throw HttpException('Failed');
  return User.fromJson(jsonDecode(response.body));
}

// Streams
Stream<int> countDown(int from) async* {
  for (var i = from; i >= 0; i--) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
dart create project_name
dart run
dart test
dart compile exe bin/main.dart
flutter create app_name
flutter run
flutter build apk / ios / web
```""",
            },
        ],
    },
    # ── Data & Query Languages ─────────────────────────────────────────
    {
        "filename": "sql",
        "title": "SQL Quick Reference",
        "meta": {
            "language": "SQL (ISO/ANSI SQL:2023)",
            "paradigm": "Declarative, set-based",
            "dialects": "PostgreSQL, MySQL, SQLite, SQL Server, Oracle",
            "purpose": "Database query, manipulation, and definition",
        },
        "sections": [
            {
                "heading": "Query Fundamentals",
                "body": """\
```sql
SELECT u.name, u.email, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.active = true
  AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC
LIMIT 20 OFFSET 0;
```""",
            },
            {
                "heading": "Joins",
                "body": """\
```sql
-- INNER JOIN (matching rows only)
SELECT * FROM users u INNER JOIN orders o ON o.user_id = u.id;

-- LEFT JOIN (all from left, matching from right)
SELECT u.name, o.total FROM users u LEFT JOIN orders o ON o.user_id = u.id;

-- Self join
SELECT e.name AS employee, m.name AS manager
FROM employees e LEFT JOIN employees m ON e.manager_id = m.id;
```""",
            },
            {
                "heading": "Window Functions",
                "body": """\
```sql
SELECT name, score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num,
    RANK() OVER (ORDER BY score DESC) AS rank
FROM students;

-- Running total
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM transactions;

-- LAG / LEAD
SELECT date, revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS change
FROM daily_sales;
```""",
            },
            {
                "heading": "CTEs & Recursive Queries",
                "body": """\
```sql
WITH active_users AS (
    SELECT * FROM users WHERE active = true
)
SELECT au.name FROM active_users au;

-- Recursive CTE (hierarchy)
WITH RECURSIVE tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, t.depth + 1
    FROM categories c INNER JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth, name;
```""",
            },
            {
                "heading": "Schema Definition",
                "body": """\
```sql
CREATE TABLE users (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    role        VARCHAR(50) DEFAULT 'user',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    metadata    JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users (email);
```""",
            },
            {
                "heading": "Performance Tips",
                "body": """\
| Pattern | Advice |
|---------|--------|
| `SELECT *` | List only needed columns |
| Missing index | Add indexes on WHERE/JOIN/ORDER BY columns |
| N+1 queries | Use JOINs or batch queries |
| `COUNT(*)` vs `EXISTS` | Use `EXISTS` for existence checks |""",
            },
        ],
    },
    {
        "filename": "graphql",
        "title": "GraphQL Quick Reference",
        "meta": {
            "language": "GraphQL (Oct 2021 Spec)",
            "paradigm": "Declarative query language for APIs",
            "typing": "Static, strong schema",
            "transport": "Typically HTTP POST, also WebSocket for subscriptions",
        },
        "sections": [
            {
                "heading": "Schema Definition",
                "body": """\
```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts(first: Int = 10): PostConnection!
}

input CreateUserInput {
  name: String!
  email: String!
}

enum Role { USER ADMIN MODERATOR }

type Query {
  user(id: ID!): User
  users(first: Int, after: String): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}
```""",
            },
            {
                "heading": "Queries",
                "body": """\
```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    name
    posts(first: 5) {
      edges { node { title } }
    }
  }
}

# Fragments
fragment UserFields on User { id name email }

query { user(id: "1") { ...UserFields } }
```""",
            },
            {
                "heading": "Pagination (Relay Cursor)",
                "body": """\
```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}

query {
  users(first: 10, after: "cursor123") {
    edges { node { id name } cursor }
    pageInfo { hasNextPage endCursor }
  }
}
```""",
            },
            {
                "heading": "Best Practices",
                "body": """\
| Pattern | Description |
|---------|-------------|
| Input types | Use dedicated input types for mutations |
| Connections | Cursor-based pagination for lists |
| Batching | Use DataLoader to avoid N+1 |
| Depth limiting | Prevent deeply nested queries |
| Persisted queries | Hash queries for security/performance |""",
            },
        ],
    },
    # ── Web & Infrastructure ───────────────────────────────────────────
    {
        "filename": "html-css",
        "title": "HTML & CSS Quick Reference",
        "meta": {
            "language": "HTML5 / CSS3+",
            "paradigm": "Document structure (HTML), Presentation (CSS)",
            "standard": "WHATWG Living Standard / CSS Modules Level 3-5",
        },
        "sections": [
            {
                "heading": "HTML Semantic Structure",
                "body": """\
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
</head>
<body>
  <header><nav aria-label="Main"><ul><li><a href="/">Home</a></li></ul></nav></header>
  <main>
    <article><h1>Title</h1><p>Content.</p></article>
    <aside>Sidebar</aside>
  </main>
  <footer><p>&copy; 2024</p></footer>
</body>
</html>
```""",
            },
            {
                "heading": "CSS Layout",
                "body": """\
```css
/* Flexbox */
.flex { display: flex; justify-content: center; align-items: center; gap: 1rem; }
.flex-item { flex: 1 1 200px; }

/* Grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
```""",
            },
            {
                "heading": "CSS Modern Features",
                "body": """\
```css
/* Custom properties */
:root { --color-primary: #3b82f6; --spacing: 1rem; }
.card { padding: var(--spacing); }

/* Container queries */
.card-container { container-type: inline-size; }
@container (min-width: 400px) { .card { flex-direction: row; } }

/* :has() parent selector */
form:has(:invalid) button { opacity: 0.5; }

/* Nesting (native) */
.card {
  padding: 1rem;
  & .title { font-size: 1.5rem; }
  &:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
}
```""",
            },
            {
                "heading": "Responsive Design",
                "body": """\
```css
@media (min-width: 768px) { /* tablet+ */ }
h1 { font-size: clamp(1.5rem, 4vw, 3rem); }
.video { aspect-ratio: 16 / 9; }
@media (prefers-color-scheme: dark) {
  :root { --color-bg: #0f172a; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}
```""",
            },
        ],
    },
    {
        "filename": "shell-bash",
        "title": "Shell / Bash Quick Reference",
        "meta": {
            "language": "Bash 5.x / POSIX sh",
            "paradigm": "Command-line scripting",
            "typing": "Untyped (everything is a string)",
            "platforms": "Linux, macOS, WSL, Git Bash",
        },
        "sections": [
            {
                "heading": "Script Setup",
                "body": """\
```bash
#!/usr/bin/env bash
set -euo pipefail    # exit on error, undefined vars, pipe failures

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <filename>" >&2
    exit 1
fi
```""",
            },
            {
                "heading": "Variables & Strings",
                "body": """\
```bash
name="Piddy"
echo "Hello $name"
echo "${#name}"               # length: 5
echo "${name,,}"              # lowercase
echo "${filename%.txt}"       # remove suffix
echo "${path##*/}"            # basename

# Default values
value="${VAR:-default}"       # use default if unset
value="${VAR:?'required'}"    # error if unset

# Arrays
arr=(one two three)
arr+=(four)
echo "${arr[@]}"              # all elements
echo "${#arr[@]}"             # length
```""",
            },
            {
                "heading": "Control Flow",
                "body": """\
```bash
if [[ -f "$file" ]]; then echo "exists"; fi

# Test operators
[[ -f file ]]       # file exists
[[ -d dir ]]        # directory exists
[[ -z "$var" ]]     # empty string
[[ "$a" == "$b" ]]  # string equal
[[ $n -gt 10 ]]     # numeric greater

for file in *.txt; do echo "$file"; done
for i in {1..10}; do echo "$i"; done

case "$action" in
    start)  start_service ;;
    stop)   stop_service ;;
    *)      echo "Unknown" >&2; exit 1 ;;
esac
```""",
            },
            {
                "heading": "Functions & Patterns",
                "body": """\
```bash
log() {
    local level="$1" message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >&2
}

# Cleanup trap
cleanup() { rm -f "$tmpfile"; }
trap cleanup EXIT
tmpfile=$(mktemp)
```""",
            },
            {
                "heading": "Essential Commands",
                "body": """\
| Command | Purpose |
|---------|---------|
| `grep -rn pattern dir/` | Search text recursively |
| `find . -name "*.ext"` | Find files by pattern |
| `sed 's/old/new/g' file` | Stream editing |
| `awk '{print $1, $3}'` | Column processing |
| `xargs` | Build command from stdin |
| `jq '.key'` | JSON processing |
| `curl -sL url` | HTTP requests |""",
            },
        ],
    },
    {
        "filename": "react",
        "title": "React Quick Reference",
        "meta": {
            "language": "React 18.2+ (with Hooks)",
            "paradigm": "UI component library",
            "typing": "JavaScript/TypeScript + JSX",
            "rendering": "Virtual DOM, concurrent features",
        },
        "sections": [
            {
                "heading": "Components",
                "body": """\
```jsx
function Greeting({ name, excited = false }) {
  return <h1>Hello {name}{excited ? "!" : "."}</h1>;
}

function Layout({ children }) {
  return <div className="layout"><main>{children}</main></div>;
}

function UserList({ users }) {
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```""",
            },
            {
                "heading": "Hooks",
                "body": """\
```jsx
const [count, setCount] = useState(0);
setCount(prev => prev + 1);

useEffect(() => {
  const ctrl = new AbortController();
  fetch(url, { signal: ctrl.signal }).then(r => r.json()).then(setData);
  return () => ctrl.abort();
}, [url]);

const sorted = useMemo(() => items.sort(compare), [items]);
const handler = useCallback((id) => setSelected(id), []);
const inputRef = useRef(null);

// Custom hook
function useLocalStorage(key, initial) {
  const [val, setVal] = useState(() => {
    const s = localStorage.getItem(key);
    return s ? JSON.parse(s) : initial;
  });
  useEffect(() => localStorage.setItem(key, JSON.stringify(val)), [key, val]);
  return [val, setVal];
}
```""",
            },
            {
                "heading": "Patterns",
                "body": """\
```jsx
// Lazy loading
const Dashboard = React.lazy(() => import('./Dashboard'));
<Suspense fallback={<Spinner />}><Dashboard /></Suspense>

// Context
const ThemeCtx = createContext('light');
const theme = useContext(ThemeCtx);

// useTransition (non-urgent updates)
const [isPending, startTransition] = useTransition();
startTransition(() => setItems(filter(items, query)));
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
npm create vite@latest app -- --template react-ts
npm run dev
npm run build
```""",
            },
        ],
    },
    {
        "filename": "vue",
        "title": "Vue.js Quick Reference",
        "meta": {
            "language": "Vue 3.4+ (Composition API)",
            "paradigm": "Progressive UI framework",
            "typing": "JavaScript/TypeScript + SFC (.vue)",
            "rendering": "Reactive system, virtual DOM",
        },
        "sections": [
            {
                "heading": "Single File Component",
                "body": """\
```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ title: string }>()
const emit = defineEmits<{ update: [value: string] }>()

const message = ref('Hello Piddy')
const reversed = computed(() => message.value.split('').reverse().join(''))
</script>

<template>
  <div>
    <h1>{{ title }}</h1>
    <input v-model="message">
    <p>{{ reversed }}</p>
    <ul><li v-for="item in items" :key="item.id">{{ item.name }}</li></ul>
  </div>
</template>

<style scoped>
div { padding: 1rem; }
</style>
```""",
            },
            {
                "heading": "Reactivity",
                "body": """\
```typescript
const count = ref(0)         // .value in script
const state = reactive({ user: null, loading: false })
const full = computed(() => `${first.value} ${last.value}`)

watch(count, (newVal, oldVal) => console.log(newVal))
watchEffect(() => console.log(count.value))
```""",
            },
            {
                "heading": "Composables",
                "body": """\
```typescript
export function useFetch<T>(url: MaybeRef<string>) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  async function execute() {
    loading.value = true
    try { data.value = await (await fetch(toValue(url))).json() }
    finally { loading.value = false }
  }
  watchEffect(() => execute())
  return { data, loading, execute }
}
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
npm create vue@latest
npm run dev
npm run build
```""",
            },
        ],
    },
    {
        "filename": "angular",
        "title": "Angular Quick Reference",
        "meta": {
            "language": "Angular 17+",
            "paradigm": "Full-featured application framework",
            "typing": "TypeScript",
            "architecture": "Component-based, dependency injection, RxJS",
        },
        "sections": [
            {
                "heading": "Standalone Components",
                "body": """\
```typescript
import { Component, signal, computed } from '@angular/core';

@Component({
  selector: 'app-counter',
  standalone: true,
  template: `
    <p>Count: {{ count() }}</p>
    <p>Double: {{ double() }}</p>
    <button (click)="increment()">+</button>
  `
})
export class CounterComponent {
  count = signal(0);
  double = computed(() => this.count() * 2);
  increment() { this.count.update(n => n + 1); }
}
```""",
            },
            {
                "heading": "Template Syntax (Angular 17+)",
                "body": """\
```html
@if (user) {
  <user-profile [user]="user" />
} @else {
  <login-form />
}

@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <p>No items</p>
}

@defer (on viewport) {
  <heavy-component />
} @loading {
  <spinner />
}
```""",
            },
            {
                "heading": "Services & DI",
                "body": """\
```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  getUsers() { return this.http.get<User[]>('/api/users'); }
}
```""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
ng new project-name --standalone
ng serve
ng build
ng test
ng generate component users/user-list
```""",
            },
        ],
    },
    {
        "filename": "nodejs",
        "title": "Node.js Quick Reference",
        "meta": {
            "language": "Node.js 20+ (LTS)",
            "paradigm": "Event-driven, non-blocking I/O",
            "engine": "V8 JavaScript engine",
            "packages": "npm, pnpm, yarn",
        },
        "sections": [
            {
                "heading": "Core Modules",
                "body": """\
```javascript
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```""",
            },
            {
                "heading": "File System",
                "body": """\
```javascript
const content = await readFile('data.json', 'utf-8');
await writeFile('output.json', JSON.stringify(data, null, 2));
await mkdir('output/sub', { recursive: true });

// Streams (large files)
import { createReadStream, createWriteStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
await pipeline(createReadStream('large.csv'), transform, createWriteStream('out.csv'));
```""",
            },
            {
                "heading": "HTTP Server & Express",
                "body": """\
```javascript
import express from 'express';
const app = express();
app.use(express.json());

app.get('/api/users', async (req, res) => {
  const users = await db.users.findAll();
  res.json(users);
});

app.post('/api/users', async (req, res) => {
  const user = await db.users.create(req.body);
  res.status(201).json(user);
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(3000);
```""",
            },
            {
                "heading": "Common Packages",
                "body": """\
| Package | Purpose |
|---------|---------|
| `express` / `fastify` | HTTP framework |
| `prisma` / `drizzle-orm` | Database ORM |
| `zod` | Schema validation |
| `pino` / `winston` | Logging |
| `vitest` / `jest` | Testing |
| `tsx` | TypeScript execution |""",
            },
            {
                "heading": "Tooling",
                "body": """\
```bash
npm init -y
npm install package
npx tsx src/index.ts
node --watch src/index.js  # built-in watch (18.11+)
node --test                # built-in test runner
```""",
            },
        ],
    },
    # ── Specialty ──────────────────────────────────────────────────────
    {
        "filename": "webassembly",
        "title": "WebAssembly Quick Reference",
        "meta": {
            "language": "WebAssembly (Wasm)",
            "paradigm": "Binary instruction format for stack-based VM",
            "standard": "W3C standard",
            "targets": "Browsers, Node.js, edge compute, embedded (WASI)",
        },
        "sections": [
            {
                "heading": "Source Languages to Wasm",
                "body": """\
| Language | Toolchain | Output |
|----------|-----------|--------|
| C/C++ | Emscripten (`emcc`) | .wasm + JS glue |
| Rust | `wasm-pack` + `wasm-bindgen` | .wasm + TS bindings |
| Go | `GOOS=js GOARCH=wasm` | .wasm + `wasm_exec.js` |
| AssemblyScript | `asc` compiler | .wasm (TS-like syntax) |""",
            },
            {
                "heading": "Rust to Wasm (Most Common)",
                "body": """\
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u64 {
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 2..=n { let t = a + b; a = b; b = t; }
    b
}
```""",
            },
            {
                "heading": "JavaScript Integration",
                "body": """\
```javascript
import init, { fibonacci } from './pkg/my_wasm.js';
await init();
const result = fibonacci(40);  // near-native speed

// Low-level
const { instance } = await WebAssembly.instantiate(bytes, imports);
instance.exports.main();
```""",
            },
            {
                "heading": "Build Commands",
                "body": """\
```bash
# Rust
wasm-pack build --target web

# C/C++
emcc main.c -o output.js -s WASM=1 -O2

# AssemblyScript
asc assembly/index.ts --outFile build/output.wasm --optimize
```""",
            },
            {
                "heading": "Use Cases",
                "body": """\
| Use Case | Example |
|----------|---------|
| Image/video processing | Filters, codecs, format conversion |
| Cryptography | Hashing, encryption in browser |
| Scientific computing | Physics simulation, ML inference |
| Gaming | Game engines (Unity, Unreal) |
| Code execution | Sandboxed language runtimes |""",
            },
        ],
    },
    {
        "filename": "cloud-devops",
        "title": "Cloud & DevOps Quick Reference",
        "meta": {
            "scope": "Cloud platforms, containers, CI/CD, infrastructure as code",
            "platforms": "AWS, GCP, Azure",
            "tools": "Docker, Kubernetes, Terraform, GitHub Actions",
        },
        "sections": [
            {
                "heading": "Docker",
                "body": """\
```dockerfile
# Multi-stage Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

```bash
docker build -t app:latest .
docker compose up -d
docker compose logs -f api
```""",
            },
            {
                "heading": "Kubernetes",
                "body": """\
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels: { app: api }
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/api:v1.2.3
          ports: [{ containerPort: 3000 }]
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits: { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /health, port: 3000 }
```

```bash
kubectl apply -f deployment.yaml
kubectl get pods -l app=api
kubectl logs -f deploy/api
kubectl rollout restart deploy/api
```""",
            },
            {
                "heading": "Terraform",
                "body": """\
```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

resource "aws_db_instance" "main" {
  identifier     = "prod-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t3.medium"
}
```

```bash
terraform init
terraform plan
terraform apply
```""",
            },
            {
                "heading": "GitHub Actions",
                "body": """\
```yaml
name: CI/CD
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm test
```""",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


def render_language(lang: dict) -> str:
    """Render a language definition to a markdown string."""
    lines = []

    # Title
    lines.append(f"# {lang['title']}")
    lines.append("")

    # Meta header
    meta = lang["meta"]
    # First key gets ## Language: treatment, rest are bold labels
    meta_keys = list(meta.keys())
    first_key = meta_keys[0]
    first_label = first_key.replace("_", " ").title()
    lines.append(f"## {first_label}: {meta[first_key]}")

    for key in meta_keys[1:]:
        label = key.replace("_", " ").title()
        lines.append(f"**{label}:** {meta[key]}  ")

    lines.append("")

    # Sections
    for section in lang["sections"]:
        lines.append(f"## {section['heading']}")
        lines.append("")
        lines.append(section["body"])
        lines.append("")

    return "\n".join(lines)


def generate(
    languages: list[dict],
    output_dir: Path,
    selected: Optional[list[str]] = None,
    force: bool = False,
) -> tuple[int, int, int]:
    """Generate language reference files. Returns (created, skipped, errors)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    errors = 0

    for lang in languages:
        filename = lang["filename"]

        # Filter if specific languages requested
        if selected and filename not in selected:
            continue

        filepath = output_dir / f"{filename}.md"

        if filepath.exists() and not force:
            print(f"  SKIP  {filepath.name} (exists, use --force to overwrite)")
            skipped += 1
            continue

        try:
            content = render_language(lang)
            filepath.write_text(content, encoding="utf-8")
            print(f"  CREATE {filepath.name} ({len(content):,} bytes)")
            created += 1
        except Exception as e:
            print(f"  ERROR  {filepath.name}: {e}")
            errors += 1

    return created, skipped, errors


def main():
    parser = argparse.ArgumentParser(
        description="Generate language reference cards for Piddy's knowledge base"
    )
    parser.add_argument(
        "languages",
        nargs="*",
        help="Specific languages to generate (default: all)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available languages and exit"
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
        print(f"Available languages ({len(LANGUAGES)}):")
        for lang in LANGUAGES:
            meta = lang["meta"]
            first_val = list(meta.values())[0]
            print(f"  {lang['filename']:20s} {first_val}")
        return

    print(f"Generating language references in {args.output}/")
    print()

    selected = args.languages if args.languages else None
    created, skipped, errors = generate(LANGUAGES, args.output, selected, args.force)

    print()
    print(f"Done: {created} created, {skipped} skipped, {errors} errors")
    print(f"Total available: {len(LANGUAGES)} languages")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
