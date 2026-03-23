#!/usr/bin/env python3
"""
Piddy Language Reference Generator

Populates library/languages/ with comprehensive reference cards
for every programming language Piddy uses and is learning.

Usage:
    python scripts/populate_languages.py          # Generate all
    python scripts/populate_languages.py --list   # List languages
    python scripts/populate_languages.py python   # Generate one

Each file is a concise, structured cheatsheet optimized for:
- Quick reference by Piddy's local LLM (Ollama)
- Knowledge base ingestion and search
- Offline learning without cloud APIs
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

LANGUAGES_DIR = Path(__file__).resolve().parent.parent / "library" / "languages"

# ─── Language Definitions ──────────────────────────────────────────────
# Each entry: (filename, display_name, category, reference_content_func)

def _python():
    return """# Python Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, multi-paradigm
- **File Extension**: `.py`
- **Package Manager**: pip, poetry, conda
- **REPL**: `python` or `ipython`
- **Version**: 3.11+ recommended

## Data Types
```python
# Primitives
x = 42              # int
y = 3.14            # float
z = 1 + 2j          # complex
s = "hello"          # str
b = True             # bool
n = None             # NoneType

# Collections
lst = [1, 2, 3]           # list (mutable, ordered)
tup = (1, 2, 3)           # tuple (immutable, ordered)
st = {1, 2, 3}            # set (mutable, unordered, unique)
dct = {"a": 1, "b": 2}    # dict (mutable, ordered since 3.7)
```

## Control Flow
```python
# Conditionals
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
else:
    print("negative")

# Loops
for item in iterable:
    if skip: continue
    if done: break
else:
    print("loop completed without break")

while condition:
    pass

# Match statement (3.10+)
match command:
    case "quit": sys.exit()
    case "go" | "move": move()
    case _: unknown()
```

## Functions
```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# Lambda
square = lambda x: x ** 2

# *args, **kwargs
def func(*args, **kwargs):
    pass

# Decorators
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def my_func():
    pass
```

## Classes & OOP
```python
class Animal:
    class_var = "shared"

    def __init__(self, name: str):
        self.name = name          # instance variable

    def speak(self) -> str:
        raise NotImplementedError

    @classmethod
    def create(cls, name):
        return cls(name)

    @staticmethod
    def info():
        return "Animal class"

    @property
    def upper_name(self):
        return self.name.upper()

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

# Dataclasses (3.7+)
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0
```

## Error Handling
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except (TypeError, ValueError):
    print("Type or value error")
else:
    print("No error occurred")
finally:
    print("Always runs")

# Custom exceptions
class AppError(Exception):
    pass

raise AppError("something failed")
```

## Comprehensions
```python
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
flat = [x for row in matrix for x in row]

# Dict comprehension
d = {k: v for k, v in pairs}

# Set comprehension
s = {x.lower() for x in words}

# Generator expression
gen = (x**2 for x in range(10))
```

## File I/O
```python
# Read
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
    # or: lines = f.readlines()

# Write
with open("file.txt", "w") as f:
    f.write("hello\\n")

# JSON
import json
data = json.loads(json_string)
json_string = json.dumps(data, indent=2)

# Path operations
from pathlib import Path
p = Path("dir") / "file.txt"
p.exists(), p.is_file(), p.read_text()
```

## Common Standard Library
```python
import os, sys, re, json, csv, math, random
import datetime, collections, itertools, functools
import pathlib, subprocess, logging, typing
import asyncio, concurrent.futures, threading
import urllib.request, http.server, socket
import hashlib, secrets, base64
import unittest, dataclasses, enum
```

## Async/Await
```python
import asyncio

async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

async def main():
    tasks = [fetch(url) for url in urls]
    results = await asyncio.gather(*tasks)

asyncio.run(main())
```

## Type Hints (3.9+)
```python
from typing import Optional, Union, TypeAlias

def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

Vector: TypeAlias = list[float]
OptStr = Optional[str]  # same as str | None
```

## Virtual Environments
```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
.venv\\Scripts\\activate       # Windows
pip install -r requirements.txt
pip freeze > requirements.txt
```

## Key Ecosystem
- **Web**: FastAPI, Django, Flask, Starlette
- **Data**: pandas, numpy, scipy, polars
- **ML/AI**: pytorch, tensorflow, scikit-learn, transformers
- **Testing**: pytest, unittest, hypothesis
- **CLI**: click, typer, argparse
- **Async**: asyncio, aiohttp, httpx
- **Type Check**: mypy, pyright
- **Format**: black, ruff, isort
"""


def _javascript():
    return """# JavaScript Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, multi-paradigm
- **File Extension**: `.js`, `.mjs`, `.cjs`
- **Package Manager**: npm, yarn, pnpm
- **Runtime**: Browser, Node.js, Deno, Bun
- **Standard**: ECMAScript 2024+

## Data Types
```javascript
// Primitives (7 types)
let num = 42;              // number (64-bit float)
let big = 9007199254740991n; // bigint
let str = "hello";         // string
let bool = true;           // boolean
let undef = undefined;     // undefined
let nul = null;            // null (object in typeof)
let sym = Symbol("id");    // symbol

// Objects
let arr = [1, 2, 3];
let obj = { name: "Piddy", version: 1 };
let map = new Map([["key", "value"]]);
let set = new Set([1, 2, 3]);
let date = new Date();
let regex = /pattern/gi;
```

## Variables
```javascript
const PI = 3.14;    // block-scoped, no reassignment
let count = 0;      // block-scoped, reassignable
var old = "legacy";  // function-scoped (avoid)
```

## Control Flow
```javascript
// Conditionals
if (x > 0) {
} else if (x === 0) {
} else {
}

// Ternary
const result = condition ? "yes" : "no";

// Switch
switch (action) {
    case "start": start(); break;
    case "stop": stop(); break;
    default: idle();
}

// Loops
for (let i = 0; i < arr.length; i++) {}
for (const item of iterable) {}      // values
for (const key in obj) {}             // keys
while (condition) {}
do {} while (condition);
```

## Functions
```javascript
// Declaration
function add(a, b) { return a + b; }

// Expression
const add = function(a, b) { return a + b; };

// Arrow (lexical this)
const add = (a, b) => a + b;
const greet = name => `Hello, ${name}!`;

// Default params, rest, spread
function func(a, b = 10, ...rest) {}
func(...array);

// Destructuring params
function draw({ x = 0, y = 0, color = "black" } = {}) {}
```

## Async/Await & Promises
```javascript
// Promise
const p = new Promise((resolve, reject) => {
    setTimeout(() => resolve("done"), 1000);
});

p.then(val => console.log(val))
 .catch(err => console.error(err))
 .finally(() => cleanup());

// Async/Await
async function fetchData(url) {
    try {
        const res = await fetch(url);
        return await res.json();
    } catch (err) {
        console.error(err);
    }
}

// Parallel
const [a, b] = await Promise.all([fetchA(), fetchB()]);
const first = await Promise.race([fetchA(), fetchB()]);
```

## Classes
```javascript
class Animal {
    #name;  // private field

    constructor(name) {
        this.#name = name;
    }

    get name() { return this.#name; }

    speak() {
        throw new Error("Not implemented");
    }

    static create(name) {
        return new this(name);
    }
}

class Dog extends Animal {
    speak() { return "Woof!"; }
}
```

## Destructuring & Spread
```javascript
// Array destructuring
const [first, second, ...rest] = [1, 2, 3, 4, 5];

// Object destructuring
const { name, age, city = "Unknown" } = person;
const { name: personName } = person; // rename

// Spread
const merged = { ...obj1, ...obj2 };
const combined = [...arr1, ...arr2];
```

## Array Methods
```javascript
arr.map(x => x * 2);
arr.filter(x => x > 0);
arr.reduce((acc, x) => acc + x, 0);
arr.find(x => x.id === 1);
arr.findIndex(x => x > 5);
arr.some(x => x > 10);
arr.every(x => x > 0);
arr.flat(Infinity);
arr.flatMap(x => [x, x * 2]);
arr.at(-1);                    // last element
arr.toSorted((a, b) => a - b); // non-mutating sort
```

## Modules (ESM)
```javascript
// Named exports
export const PI = 3.14;
export function add(a, b) { return a + b; }

// Default export
export default class App {}

// Imports
import App from "./App.js";
import { PI, add } from "./math.js";
import * as math from "./math.js";
```

## Error Handling
```javascript
try {
    throw new Error("oops");
} catch (err) {
    console.error(err.message, err.stack);
} finally {
    cleanup();
}

// Custom error
class AppError extends Error {
    constructor(message, code) {
        super(message);
        this.code = code;
    }
}
```

## Modern Features (ES2020+)
```javascript
obj?.nested?.prop;         // Optional chaining
value ?? "default";        // Nullish coalescing
arr.at(-1);                // Array.at()
Object.hasOwn(obj, "key"); // hasOwn
structuredClone(obj);       // Deep clone
using resource = getRes();  // Explicit resource mgmt
```

## Key Ecosystem
- **Frontend**: React, Vue, Angular, Svelte, Solid
- **Backend**: Express, Fastify, Hono, Koa
- **Build**: Vite, esbuild, webpack, Turbopack
- **Test**: Jest, Vitest, Playwright, Cypress
- **Lint/Format**: ESLint, Prettier, Biome
- **Type**: TypeScript
"""


def _typescript():
    return """# TypeScript Quick Reference

## Overview
- **Type**: Statically typed superset of JavaScript
- **File Extension**: `.ts`, `.tsx`, `.d.ts`
- **Compiler**: `tsc` (TypeScript Compiler)
- **Config**: `tsconfig.json`

## Basic Types
```typescript
let num: number = 42;
let str: string = "hello";
let bool: boolean = true;
let arr: number[] = [1, 2, 3];
let tuple: [string, number] = ["age", 25];
let any: any = "anything";
let unknown: unknown = getValue();
let never: never = throwError();
let nul: null = null;
let undef: undefined = undefined;
let vd: void = undefined;
```

## Type Aliases & Interfaces
```typescript
// Type alias
type Point = { x: number; y: number };
type ID = string | number;
type Direction = "north" | "south" | "east" | "west";

// Interface
interface User {
    readonly id: number;
    name: string;
    email?: string;              // optional
    greet(): string;
}

// Extends
interface Admin extends User {
    role: "admin" | "superadmin";
}

// Type vs Interface:
// - Interface: extendable, declaration merging
// - Type: unions, intersections, mapped types
```

## Generics
```typescript
function identity<T>(arg: T): T { return arg; }
const result = identity<string>("hello");

// Constraints
function getLength<T extends { length: number }>(arg: T): number {
    return arg.length;
}

// Generic interfaces & classes
interface Repository<T> {
    findById(id: string): Promise<T>;
    save(entity: T): Promise<void>;
}

class Stack<T> {
    private items: T[] = [];
    push(item: T): void { this.items.push(item); }
    pop(): T | undefined { return this.items.pop(); }
}
```

## Utility Types
```typescript
Partial<T>       // All properties optional
Required<T>      // All properties required
Readonly<T>      // All properties readonly
Pick<T, K>       // Subset of properties
Omit<T, K>       // Exclude properties
Record<K, V>     // Map of K to V
Exclude<U, M>    // Remove from union
Extract<U, M>    // Keep in union
NonNullable<T>   // Remove null/undefined
ReturnType<F>    // Function return type
Parameters<F>    // Function parameter types
Awaited<T>       // Unwrap Promise type
```

## Advanced Types
```typescript
// Discriminated unions
type Shape =
    | { kind: "circle"; radius: number }
    | { kind: "square"; side: number };

function area(s: Shape): number {
    switch (s.kind) {
        case "circle": return Math.PI * s.radius ** 2;
        case "square": return s.side ** 2;
    }
}

// Template literal types
type EventName = `on${Capitalize<string>}`;

// Mapped types
type Mutable<T> = { -readonly [P in keyof T]: T[P] };

// Conditional types
type IsString<T> = T extends string ? true : false;

// Infer
type UnpackPromise<T> = T extends Promise<infer U> ? U : T;
```

## Type Guards
```typescript
// typeof
if (typeof value === "string") { /* string here */ }

// instanceof
if (error instanceof AppError) { /* AppError here */ }

// Custom type guard
function isUser(obj: unknown): obj is User {
    return typeof obj === "object" && obj !== null && "name" in obj;
}

// Assertion function
function assertDefined<T>(val: T): asserts val is NonNullable<T> {
    if (val == null) throw new Error("Value is null");
}
```

## Enums
```typescript
enum Direction { Up, Down, Left, Right }
enum Status { Active = "ACTIVE", Inactive = "INACTIVE" }

// Prefer const enum for perf (inlined at compile time)
const enum Color { Red, Green, Blue }

// Or use union types instead
type Color = "red" | "green" | "blue";
```

## Module Declaration
```typescript
// Ambient declaration (.d.ts)
declare module "my-lib" {
    export function doThing(): void;
}

declare global {
    interface Window {
        myGlobal: string;
    }
}
```

## tsconfig.json Essentials
```json
{
    "compilerOptions": {
        "target": "ES2022",
        "module": "ESNext",
        "moduleResolution": "bundler",
        "strict": true,
        "noUncheckedIndexedAccess": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "outDir": "./dist",
        "declaration": true
    },
    "include": ["src/**/*"]
}
```
"""


def _java():
    return """# Java Quick Reference

## Overview
- **Type**: Compiled, statically typed, OOP
- **File Extension**: `.java`
- **Build Tools**: Maven, Gradle
- **Runtime**: JVM (Java Virtual Machine)
- **Version**: Java 21 LTS (latest LTS)

## Data Types
```java
// Primitives
byte b = 127;            // 8-bit   [-128, 127]
short s = 32000;         // 16-bit
int i = 42;              // 32-bit
long l = 100L;           // 64-bit
float f = 3.14f;         // 32-bit float
double d = 3.14;         // 64-bit float
char c = 'A';            // 16-bit Unicode
boolean flag = true;

// Wrapper classes (auto-boxing)
Integer num = 42;
String str = "hello";    // immutable

// var (type inference, Java 10+)
var list = new ArrayList<String>();
```

## Control Flow
```java
// If-else
if (x > 0) {
} else if (x == 0) {
} else {
}

// Switch expression (Java 14+)
String label = switch (day) {
    case MONDAY, FRIDAY -> "Busy";
    case SATURDAY, SUNDAY -> "Relax";
    default -> "Normal";
};

// Enhanced for
for (var item : collection) { }

// Traditional for
for (int i = 0; i < n; i++) { }

// While
while (condition) { }
```

## Classes & OOP
```java
public class Animal {
    private String name;

    public Animal(String name) {
        this.name = name;
    }

    public String speak() {
        return "...";
    }
}

public class Dog extends Animal {
    public Dog(String name) { super(name); }

    @Override
    public String speak() { return "Woof!"; }
}

// Sealed classes (Java 17+)
public sealed class Shape permits Circle, Square { }
public final class Circle extends Shape { }
public non-sealed class Square extends Shape { }
```

## Records (Java 16+)
```java
public record Point(double x, double y) {
    // Compact constructor
    public Point {
        if (x < 0 || y < 0) throw new IllegalArgumentException();
    }
}

var p = new Point(1.0, 2.0);
p.x(); p.y(); // accessor methods
```

## Interfaces
```java
public interface Printable {
    void print();

    default String format() { return toString(); }

    static Printable empty() { return () -> {}; }
}

// Functional interface
@FunctionalInterface
public interface Transformer<T, R> {
    R transform(T input);
}
```

## Collections
```java
// List
List<String> list = List.of("a", "b", "c");       // immutable
List<String> mutable = new ArrayList<>(list);

// Map
Map<String, Integer> map = Map.of("a", 1, "b", 2);
var mutableMap = new HashMap<>(map);

// Set
Set<Integer> set = Set.of(1, 2, 3);

// Stream API
list.stream()
    .filter(s -> s.length() > 3)
    .map(String::toUpperCase)
    .sorted()
    .collect(Collectors.toList());
```

## Exception Handling
```java
try {
    riskyOperation();
} catch (IOException | SQLException e) {
    logger.error("Failed", e);
} finally {
    cleanup();
}

// Try-with-resources
try (var reader = new BufferedReader(new FileReader("file.txt"))) {
    String line = reader.readLine();
}

// Custom exception
public class AppException extends RuntimeException {
    public AppException(String msg, Throwable cause) {
        super(msg, cause);
    }
}
```

## Generics
```java
public class Box<T extends Comparable<T>> {
    private T value;
    public T getValue() { return value; }
}

// Wildcards
void process(List<? extends Number> nums) { }   // upper bound
void add(List<? super Integer> list) { }         // lower bound
```

## Pattern Matching (Java 21+)
```java
// instanceof pattern
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.toUpperCase());
}

// Switch pattern matching
String describe(Object obj) {
    return switch (obj) {
        case Integer i when i > 0 -> "positive int: " + i;
        case String s -> "string: " + s;
        case null -> "null";
        default -> "other";
    };
}
```

## Virtual Threads (Java 21+)
```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
        executor.submit(() -> processRequest(i))
    );
}
```

## Key Ecosystem
- **Frameworks**: Spring Boot, Quarkus, Micronaut
- **Build**: Maven, Gradle
- **Test**: JUnit 5, Mockito, AssertJ
- **ORM**: Hibernate, jOOQ
- **HTTP**: HttpClient (built-in), OkHttp
- **JSON**: Jackson, Gson
"""


def _csharp():
    return """# C# Quick Reference

## Overview
- **Type**: Compiled, statically typed, multi-paradigm
- **File Extension**: `.cs`
- **Platform**: .NET 8+ (cross-platform)
- **Build**: dotnet CLI, MSBuild
- **IDE**: Visual Studio, Rider, VS Code

## Data Types
```csharp
int i = 42;              // 32-bit signed
long l = 100L;           // 64-bit signed
float f = 3.14f;         // 32-bit float
double d = 3.14;         // 64-bit float
decimal m = 3.14m;       // 128-bit (financial)
bool b = true;
char c = 'A';
string s = "hello";      // immutable reference type

// Nullable value types
int? nullable = null;

// var (implicit)
var list = new List<string>();
```

## Control Flow
```csharp
// Pattern matching switch
var result = shape switch
{
    Circle { Radius: > 10 } c => $"Big circle: {c.Radius}",
    Square s => $"Square: {s.Side}",
    null => "null",
    _ => "unknown"
};

// for, foreach, while
foreach (var item in collection) { }
for (int i = 0; i < n; i++) { }
while (condition) { }
```

## Classes
```csharp
public class Animal
{
    public string Name { get; init; }
    public virtual string Speak() => "...";
}

public class Dog : Animal
{
    public override string Speak() => "Woof!";
}

// Records (immutable reference types)
public record Person(string Name, int Age);
public record struct Point(double X, double Y);

// Primary constructors (C# 12)
public class Service(ILogger logger, IDb db)
{
    public void Run() => logger.Log("running");
}
```

## Interfaces
```csharp
public interface IRepository<T> where T : class
{
    Task<T?> FindAsync(int id);
    Task SaveAsync(T entity);

    // Default interface method
    void Log(string msg) => Console.WriteLine(msg);
}
```

## LINQ
```csharp
var results = collection
    .Where(x => x.Age > 18)
    .OrderBy(x => x.Name)
    .Select(x => new { x.Name, x.Age })
    .ToList();

// Query syntax
var query = from p in people
            where p.Age > 18
            orderby p.Name
            select p;
```

## Async/Await
```csharp
public async Task<string> FetchAsync(string url)
{
    using var client = new HttpClient();
    var response = await client.GetAsync(url);
    return await response.Content.ReadAsStringAsync();
}

// Parallel
var tasks = urls.Select(url => FetchAsync(url));
var results = await Task.WhenAll(tasks);

// Cancellation
public async Task DoWork(CancellationToken ct)
{
    ct.ThrowIfCancellationRequested();
    await Task.Delay(1000, ct);
}
```

## Null Safety
```csharp
string? nullable = null;
string safe = nullable ?? "default";
int? length = nullable?.Length;
string definite = nullable!; // null-forgiving (use carefully)
```

## Collections
```csharp
List<int> list = [1, 2, 3];                     // collection expression
Dictionary<string, int> dict = new() { ["a"] = 1 };
HashSet<int> set = [1, 2, 3];
int[] arr = [1, 2, 3];

// Immutable
ImmutableList<int> imm = [1, 2, 3];

// Span (stack-based slicing)
Span<int> span = arr.AsSpan(1..3);
```

## Error Handling
```csharp
try
{
    await RiskyAsync();
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    logger.LogWarning("Not found: {}", ex.Message);
}
catch (Exception ex)
{
    logger.LogError(ex, "Unexpected error");
    throw;  // re-throw preserving stack trace
}
finally
{
    Cleanup();
}
```

## Key Ecosystem
- **Web**: ASP.NET Core, Minimal APIs, Blazor
- **ORM**: Entity Framework Core, Dapper
- **Desktop**: WPF, WinUI, MAUI, Avalonia
- **Test**: xUnit, NUnit, Moq, FluentAssertions
- **IoC**: Microsoft.Extensions.DependencyInjection
- **Messaging**: MassTransit, MediatR
"""


def _c():
    return """# C Quick Reference

## Overview
- **Type**: Compiled, statically typed, procedural
- **File Extension**: `.c`, `.h`
- **Compilers**: GCC, Clang, MSVC
- **Standard**: C17 / C23
- **Build**: Make, CMake, Meson

## Data Types
```c
// Integer types
char c = 'A';           // at least 8 bits
short s = 32000;        // at least 16 bits
int i = 42;             // at least 16 bits (usually 32)
long l = 100L;          // at least 32 bits
long long ll = 100LL;   // at least 64 bits

// Fixed-width (stdint.h)
int8_t, int16_t, int32_t, int64_t
uint8_t, uint16_t, uint32_t, uint64_t
size_t, ptrdiff_t

// Floating point
float f = 3.14f;        // 32-bit
double d = 3.14;        // 64-bit

// Boolean (stdbool.h)
bool flag = true;
```

## Pointers & Memory
```c
int x = 42;
int *p = &x;            // pointer to x
int val = *p;           // dereference

// Dynamic allocation
int *arr = malloc(n * sizeof(int));
int *arr2 = calloc(n, sizeof(int));  // zero-initialized
arr = realloc(arr, new_n * sizeof(int));
free(arr);

// Arrays
int arr[10] = {0};
int matrix[3][3] = {{1,0,0},{0,1,0},{0,0,1}};

// Pointer arithmetic
*(arr + i) == arr[i];   // equivalent
```

## Strings
```c
#include <string.h>

char str[] = "hello";
size_t len = strlen(str);
strcmp(a, b);    // 0 if equal
strncpy(dst, src, n);
strncat(dst, src, n);

// Safe alternatives
snprintf(buf, sizeof(buf), "value: %d", val);
```

## Structs & Unions
```c
typedef struct {
    char name[64];
    int age;
    double salary;
} Employee;

Employee e = { .name = "Alice", .age = 30, .salary = 75000.0 };

// Unions (shared memory)
typedef union {
    int i;
    float f;
    char bytes[4];
} Value;
```

## Functions
```c
// Declaration (prototype)
int add(int a, int b);

// Definition
int add(int a, int b) {
    return a + b;
}

// Function pointers
typedef int (*Comparator)(const void *, const void *);
qsort(arr, n, sizeof(int), compare_ints);
```

## Preprocessor
```c
#include <stdio.h>      // system header
#include "mylib.h"      // local header

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

#ifdef DEBUG
    #define LOG(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
#else
    #define LOG(fmt, ...)
#endif

#pragma once            // include guard (non-standard but universal)
```

## File I/O
```c
FILE *f = fopen("data.txt", "r");
if (!f) { perror("fopen"); return 1; }

char buf[256];
while (fgets(buf, sizeof(buf), f)) {
    printf("%s", buf);
}
fclose(f);

// Binary I/O
fwrite(data, sizeof(int), count, f);
fread(data, sizeof(int), count, f);
```

## Error Handling Patterns
```c
// Return codes
int result = do_something();
if (result < 0) {
    fprintf(stderr, "Error: %s\\n", strerror(errno));
    goto cleanup;
}

// Goto cleanup pattern
int func(void) {
    int ret = -1;
    char *buf = malloc(1024);
    if (!buf) goto done;

    FILE *f = fopen("file", "r");
    if (!f) goto free_buf;

    ret = 0;
    fclose(f);
free_buf:
    free(buf);
done:
    return ret;
}
```

## Common Standard Library Headers
```c
<stdio.h>    // printf, scanf, FILE, fopen
<stdlib.h>   // malloc, free, atoi, exit, qsort
<string.h>   // strlen, strcpy, memcpy, memset
<math.h>     // sin, cos, sqrt, pow, fabs
<stdint.h>   // int32_t, uint64_t, SIZE_MAX
<stdbool.h>  // bool, true, false
<assert.h>   // assert()
<errno.h>    // errno, EINVAL, ENOMEM
<limits.h>   // INT_MAX, CHAR_BIT
<stdarg.h>   // va_list, va_start, va_end
<time.h>     // time, clock, difftime
<signal.h>   // signal, raise, SIGINT
<pthread.h>  // threads (POSIX)
```
"""


def _cpp():
    return """# C++ Quick Reference

## Overview
- **Type**: Compiled, statically typed, multi-paradigm
- **File Extension**: `.cpp`, `.hpp`, `.h`, `.cc`
- **Compilers**: GCC (g++), Clang++, MSVC
- **Standard**: C++20 / C++23
- **Build**: CMake, Meson, Bazel

## Modern C++ Core
```cpp
// auto type deduction
auto x = 42;
auto s = "hello"s;  // std::string literal

// Structured bindings (C++17)
auto [name, age] = std::pair{"Alice", 30};
auto& [key, value] = *map.begin();

// Range-based for
for (const auto& item : container) { }

// if with initializer (C++17)
if (auto it = map.find(key); it != map.end()) {
    use(it->second);
}
```

## Smart Pointers
```cpp
#include <memory>

auto p1 = std::make_unique<Widget>(args...);  // exclusive ownership
auto p2 = std::make_shared<Widget>(args...);   // shared ownership
std::weak_ptr<Widget> wp = p2;                  // non-owning observer

// NEVER use raw new/delete for ownership
```

## Containers (STL)
```cpp
#include <vector>
#include <map>
#include <unordered_map>
#include <string>
#include <array>
#include <span>

std::vector<int> v = {1, 2, 3};
std::array<int, 3> a = {1, 2, 3};
std::map<std::string, int> m = {{"a", 1}};
std::unordered_map<std::string, int> um;

// span (C++20) - non-owning view
void process(std::span<const int> data) { }
```

## Algorithms & Ranges (C++20)
```cpp
#include <algorithm>
#include <ranges>

// Traditional
std::sort(v.begin(), v.end());
auto it = std::find(v.begin(), v.end(), 42);

// Ranges (C++20)
namespace rv = std::views;

auto result = v
    | rv::filter([](int x) { return x > 0; })
    | rv::transform([](int x) { return x * 2; })
    | rv::take(5);

std::ranges::sort(v);
```

## Classes
```cpp
class Widget {
public:
    Widget(std::string name) : name_(std::move(name)) {}

    // Rule of 5 (or Rule of 0 - prefer this)
    Widget(const Widget&) = default;
    Widget(Widget&&) = default;
    Widget& operator=(const Widget&) = default;
    Widget& operator=(Widget&&) = default;
    ~Widget() = default;

    std::string_view name() const { return name_; }

private:
    std::string name_;
};
```

## Templates
```cpp
template<typename T>
concept Printable = requires(T t) {
    { std::cout << t } -> std::same_as<std::ostream&>;
};

template<Printable T>
void print(const T& value) {
    std::cout << value << '\\n';
}

// Variadic templates
template<typename... Args>
auto sum(Args... args) {
    return (args + ...);  // fold expression
}
```

## Lambda Expressions
```cpp
auto add = [](int a, int b) { return a + b; };
auto capture = [&vec, factor](int x) { return x * factor; };
auto generic = [](auto a, auto b) { return a + b; };  // C++14

// Immediately invoked
auto value = [&]() {
    // complex initialization
    return computed_result;
}();
```

## Error Handling
```cpp
#include <stdexcept>
#include <expected>  // C++23

// Exceptions
try {
    throw std::runtime_error("oops");
} catch (const std::exception& e) {
    std::cerr << e.what() << '\\n';
}

// std::expected (C++23)
std::expected<int, std::string> parse(std::string_view s) {
    if (auto val = try_parse(s))
        return *val;
    return std::unexpected("parse failed");
}

// std::optional
std::optional<int> find(const std::string& key);
```

## Concurrency
```cpp
#include <thread>
#include <mutex>
#include <future>

// Threads
auto t = std::jthread([](std::stop_token st) {
    while (!st.stop_requested()) { work(); }
});

// Mutex
std::mutex mtx;
{
    std::lock_guard lock(mtx);
    shared_data++;
}

// Async
auto future = std::async(std::launch::async, compute, args);
auto result = future.get();
```

## Key Ecosystem
- **Build**: CMake, vcpkg, Conan
- **Test**: Catch2, Google Test, doctest
- **Format**: clang-format
- **Lint**: clang-tidy, cppcheck
- **Frameworks**: Qt, Boost, Abseil
"""


def _go():
    return """# Go Quick Reference

## Overview
- **Type**: Compiled, statically typed, concurrent
- **File Extension**: `.go`
- **Build**: `go build`, `go run`
- **Package Manager**: Go Modules (`go.mod`)
- **Version**: Go 1.22+

## Basics
```go
package main

import (
    "fmt"
    "strings"
)

func main() {
    // Variables
    var x int = 42
    y := 3.14            // short declaration
    const Pi = 3.14159

    // Multiple
    var a, b, c int
    d, e := "hello", true

    fmt.Println(x, y, d, e)
}
```

## Types
```go
// Basic types
bool, string
int, int8, int16, int32, int64
uint, uint8, uint16, uint32, uint64
float32, float64
complex64, complex128
byte  // alias for uint8
rune  // alias for int32 (Unicode code point)

// Composite types
[5]int                    // array (fixed size)
[]int                     // slice (dynamic)
map[string]int            // map
struct { Name string }    // struct
chan int                   // channel
func(int) int             // function type
*int                      // pointer
```

## Slices & Maps
```go
// Slices
s := []int{1, 2, 3}
s = append(s, 4, 5)
sub := s[1:3]              // [2, 3]
s2 := make([]int, 0, 100)  // len=0, cap=100

// Maps
m := map[string]int{"a": 1, "b": 2}
m["c"] = 3
val, ok := m["key"]       // comma-ok idiom
delete(m, "a")

// Iteration
for i, v := range slice { }
for k, v := range mapVar { }
```

## Structs & Methods
```go
type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age,omitempty"`
}

// Methods
func (u User) String() string {
    return fmt.Sprintf("%s <%s>", u.Name, u.Email)
}

func (u *User) SetName(name string) {
    u.Name = name  // pointer receiver to modify
}

// Embedding (composition)
type Admin struct {
    User          // embedded
    Role string
}
```

## Interfaces
```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Composition
type ReadWriter interface {
    Reader
    Writer
}

// Implicit implementation - no "implements" keyword
// Any type with matching methods satisfies the interface
```

## Error Handling
```go
// Standard pattern
func readFile(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("readFile %s: %w", path, err)
    }
    return data, nil
}

// Custom errors
type NotFoundError struct {
    ID string
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("not found: %s", e.ID)
}

// Error checking
if errors.Is(err, os.ErrNotExist) { }
var nfe *NotFoundError
if errors.As(err, &nfe) { }
```

## Goroutines & Channels
```go
// Goroutine
go func() {
    doWork()
}()

// Channels
ch := make(chan int, 10)    // buffered
ch <- 42                     // send
val := <-ch                  // receive

// Select
select {
case msg := <-ch1:
    handle(msg)
case ch2 <- result:
    // sent
case <-time.After(5 * time.Second):
    // timeout
case <-ctx.Done():
    return ctx.Err()
}

// WaitGroup
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(it Item) {
        defer wg.Done()
        process(it)
    }(item)
}
wg.Wait()
```

## Generics (Go 1.18+)
```go
func Map[T any, R any](s []T, f func(T) R) []R {
    result := make([]R, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

// Constraints
type Number interface {
    ~int | ~float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}
```

## Testing
```go
// file: math_test.go
func TestAdd(t *testing.T) {
    got := Add(2, 3)
    if got != 5 {
        t.Errorf("Add(2,3) = %d, want 5", got)
    }
}

func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(2, 3)
    }
}

// Run: go test ./... -v -race
```

## Key Ecosystem
- **Web**: net/http, Gin, Echo, Chi, Fiber
- **ORM**: GORM, sqlx, sqlc
- **gRPC**: google.golang.org/grpc
- **CLI**: cobra, urfave/cli
- **Test**: testing (stdlib), testify
- **Containers**: Docker (written in Go), Kubernetes
"""


def _rust():
    return """# Rust Quick Reference

## Overview
- **Type**: Compiled, statically typed, systems language
- **File Extension**: `.rs`
- **Build**: cargo (build, test, run, publish)
- **Package Registry**: crates.io
- **Key Feature**: Memory safety without GC (ownership system)

## Basics
```rust
fn main() {
    let x = 42;                // immutable by default
    let mut y = 0;             // mutable
    y += 1;
    const MAX: u32 = 100_000;

    let s = String::from("hello"); // owned string
    let slice: &str = "hello";      // string slice (borrowed)

    println!("x={x}, y={y}");
}
```

## Types
```rust
// Scalar
i8, i16, i32, i64, i128, isize
u8, u16, u32, u64, u128, usize
f32, f64
bool
char  // 4 bytes, Unicode scalar

// Compound
(i32, f64, bool)          // tuple
[i32; 5]                   // array (fixed)
Vec<i32>                   // vector (dynamic)
HashMap<String, i32>       // hash map
String                     // owned string
&str                       // string slice
Box<T>                     // heap allocation
Option<T>                  // Some(T) | None
Result<T, E>               // Ok(T) | Err(E)
```

## Ownership & Borrowing
```rust
// Ownership rules:
// 1. Each value has exactly one owner
// 2. When owner goes out of scope, value is dropped
// 3. Value can be moved or borrowed

let s1 = String::from("hello");
let s2 = s1;          // s1 is MOVED, can't use s1 anymore

// Borrowing (references)
fn len(s: &str) -> usize { s.len() }      // immutable borrow
fn push(s: &mut String) { s.push('!'); }    // mutable borrow

// Rules: either ONE &mut OR any number of & at a time

// Lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

## Structs & Enums
```rust
struct User {
    name: String,
    email: String,
    age: u32,
}

impl User {
    fn new(name: String, email: String) -> Self {
        Self { name, email, age: 0 }
    }

    fn greet(&self) -> String {
        format!("Hi, I'm {}", self.name)
    }
}

// Enums (algebraic data types)
enum Shape {
    Circle(f64),
    Rectangle { width: f64, height: f64 },
    Triangle(f64, f64, f64),
}

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(r) => std::f64::consts::PI * r * r,
            Shape::Rectangle { width, height } => width * height,
            Shape::Triangle(a, b, c) => { /* Heron's formula */ 0.0 }
        }
    }
}
```

## Pattern Matching
```rust
match value {
    0 => println!("zero"),
    1..=9 => println!("single digit"),
    n if n < 0 => println!("negative"),
    _ => println!("other"),
}

// if let (single pattern)
if let Some(val) = optional {
    use(val);
}

// let else (Rust 1.65+)
let Some(val) = optional else {
    return Err("missing");
};
```

## Traits
```rust
trait Summary {
    fn summarize(&self) -> String;

    // Default implementation
    fn preview(&self) -> String {
        format!("{}...", &self.summarize()[..20])
    }
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, self.content)
    }
}

// Trait bounds
fn notify(item: &impl Summary) { }
fn notify<T: Summary + Display>(item: &T) { }

// Where clause
fn process<T>(item: T) -> String
where
    T: Summary + Clone + Send,
{
    item.summarize()
}
```

## Error Handling
```rust
use std::io;

fn read_file(path: &str) -> Result<String, io::Error> {
    let content = std::fs::read_to_string(path)?;  // ? operator
    Ok(content)
}

// Custom error with thiserror
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
    #[error("Not found: {0}")]
    NotFound(String),
}

// anyhow for application errors
fn main() -> anyhow::Result<()> {
    let data = std::fs::read("file.txt")?;
    Ok(())
}
```

## Async
```rust
async fn fetch(url: &str) -> Result<String, reqwest::Error> {
    let body = reqwest::get(url).await?.text().await?;
    Ok(body)
}

#[tokio::main]
async fn main() {
    let (a, b) = tokio::join!(fetch("url1"), fetch("url2"));
}
```

## Iterators
```rust
let v = vec![1, 2, 3, 4, 5];
let sum: i32 = v.iter().filter(|&&x| x > 2).sum();
let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();

// Chaining
let result: Vec<String> = items
    .iter()
    .filter(|i| i.active)
    .map(|i| i.name.clone())
    .collect();
```

## Key Ecosystem
- **Web**: Actix-web, Axum, Rocket
- **Async**: Tokio, async-std
- **Serialization**: serde, serde_json
- **CLI**: clap, dialoguer
- **Error**: thiserror, anyhow
- **ORM**: Diesel, SeaORM, sqlx
- **WASM**: wasm-bindgen, wasm-pack
"""


def _ruby():
    return """# Ruby Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, OOP
- **File Extension**: `.rb`
- **Package Manager**: RubyGems, Bundler
- **REPL**: `irb` or `pry`
- **Philosophy**: "Optimized for programmer happiness"

## Basics
```ruby
# Variables
name = "Piddy"          # local
@instance_var = 42      # instance
@@class_var = 0         # class
$global = "avoid"       # global
CONSTANT = 3.14         # constant

# String interpolation
puts "Hello, #{name}!"
puts 'No interpolation here'

# Symbols (immutable, interned strings)
status = :active
```

## Data Types
```ruby
42                   # Integer
3.14                 # Float
"hello"              # String
:symbol              # Symbol
true, false, nil     # Boolean / nil
[1, 2, 3]           # Array
{a: 1, b: 2}        # Hash (symbol keys)
{"a" => 1}           # Hash (string keys)
(1..10)              # Range (inclusive)
(1...10)             # Range (exclusive end)
```

## Control Flow
```ruby
# if/elsif/else
if x > 0
  "positive"
elsif x == 0
  "zero"
else
  "negative"
end

# Inline
puts "yes" if condition
puts "no" unless condition

# Case/when (pattern matching)
case value
when 1..5 then "low"
when 6..10 then "high"
when String then "string: #{value}"
when /pattern/ then "matched regex"
else "other"
end

# Pattern matching (Ruby 3.0+)
case [1, 2, 3]
in [Integer => a, Integer => b, *rest]
  puts "a=#{a}, b=#{b}"
end
```

## Methods
```ruby
def greet(name, greeting: "Hello")
  "#{greeting}, #{name}!"
end

# Block, Proc, Lambda
[1, 2, 3].map { |x| x * 2 }
[1, 2, 3].each do |x|
  puts x
end

square = ->(x) { x ** 2 }
square.call(5)  # => 25

def with_logging(&block)
  puts "Start"
  block.call
  puts "End"
end
```

## Classes
```ruby
class Animal
  attr_accessor :name
  attr_reader :species

  def initialize(name, species)
    @name = name
    @species = species
  end

  def speak
    raise NotImplementedError
  end

  def to_s
    "#{@name} (#{@species})"
  end
end

class Dog < Animal
  def speak = "Woof!"
end

# Modules (mixins)
module Loggable
  def log(msg)
    puts "[#{self.class}] #{msg}"
  end
end

class Service
  include Loggable
end
```

## Enumerable
```ruby
arr = [1, 2, 3, 4, 5]

arr.map { |x| x * 2 }        # [2, 4, 6, 8, 10]
arr.select { |x| x.even? }   # [2, 4]
arr.reject { |x| x > 3 }     # [1, 2, 3]
arr.reduce(0) { |sum, x| sum + x }  # 15
arr.any? { |x| x > 4 }       # true
arr.all? { |x| x > 0 }       # true
arr.min, arr.max, arr.sort
arr.each_with_object({}) { |x, h| h[x] = x**2 }
arr.group_by(&:even?)
```

## Error Handling
```ruby
begin
  risky_operation
rescue ArgumentError => e
  puts "Bad arg: #{e.message}"
rescue StandardError => e
  puts "Error: #{e.message}"
  retry if should_retry?
ensure
  cleanup
end

# Custom error
class AppError < StandardError; end
raise AppError, "something failed"
```

## Key Ecosystem
- **Web**: Ruby on Rails, Sinatra, Hanami
- **Test**: RSpec, Minitest
- **ORM**: ActiveRecord, Sequel
- **Background**: Sidekiq, GoodJob
- **HTTP**: Faraday, HTTParty
- **Lint**: RuboCop
"""


def _php():
    return """# PHP Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, multi-paradigm
- **File Extension**: `.php`
- **Package Manager**: Composer
- **Version**: PHP 8.3+
- **Key Use**: Web development, server-side scripting

## Basics
```php
<?php

// Variables (always start with $)
$name = "Piddy";
$age = 3;
$pi = 3.14;
$active = true;
$nothing = null;

// Constants
const APP_NAME = "Piddy";
define('VERSION', '1.0');

// String interpolation
echo "Hello, {$name}!";
echo "Age: $age";

// Type declarations (PHP 8+)
function add(int $a, int $b): int {
    return $a + $b;
}
```

## Types (PHP 8+)
```php
// Union types
function process(string|int $value): string|false { }

// Intersection types
function handle(Countable&Iterator $collection): void { }

// Nullable
function find(int $id): ?User { }

// Enums (PHP 8.1+)
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}

// Named arguments
array_slice(array: $arr, offset: 2, length: 3);
```

## Arrays
```php
// Indexed
$arr = [1, 2, 3];

// Associative
$user = ['name' => 'Alice', 'age' => 30];

// Functions
array_map(fn($x) => $x * 2, $arr);
array_filter($arr, fn($x) => $x > 2);
array_reduce($arr, fn($carry, $item) => $carry + $item, 0);
in_array($needle, $arr);
array_key_exists('name', $user);
count($arr);
array_merge($arr1, $arr2);
[...$arr1, ...$arr2]; // spread operator
```

## Classes (Modern PHP)
```php
// Constructor promotion (PHP 8.0+)
class User {
    public function __construct(
        private readonly string $name,
        private readonly string $email,
        private int $age = 0,
    ) {}

    public function greet(): string {
        return "Hi, I'm {$this->name}";
    }
}

// Interface
interface Repository {
    public function find(int $id): ?Entity;
    public function save(Entity $entity): void;
}

// Trait
trait Loggable {
    public function log(string $msg): void {
        error_log("[" . static::class . "] $msg");
    }
}

class Service implements Repository {
    use Loggable;
    // ...
}
```

## Match Expression (PHP 8.0+)
```php
$result = match($status) {
    'active' => handleActive(),
    'inactive', 'disabled' => handleInactive(),
    default => throw new InvalidArgumentException(),
};
```

## Error Handling
```php
try {
    riskyOperation();
} catch (InvalidArgumentException|TypeError $e) {
    echo $e->getMessage();
} catch (Throwable $e) {
    logger()->error($e->getMessage(), ['exception' => $e]);
    throw $e;
} finally {
    cleanup();
}
```

## Key Ecosystem
- **Frameworks**: Laravel, Symfony, Slim
- **CMS**: WordPress, Drupal
- **ORM**: Eloquent, Doctrine
- **Test**: PHPUnit, Pest
- **Static Analysis**: PHPStan, Psalm
- **Lint**: PHP CS Fixer
"""


def _swift():
    return """# Swift Quick Reference

## Overview
- **Type**: Compiled, statically typed, multi-paradigm
- **File Extension**: `.swift`
- **Package Manager**: Swift Package Manager (SPM)
- **Platforms**: iOS, macOS, tvOS, watchOS, Linux, Windows
- **Version**: Swift 5.9+

## Basics
```swift
var mutable = 42
let immutable = "constant"
let pi: Double = 3.14159

// String interpolation
let msg = "Value is \\(mutable)"

// Optionals
var name: String? = nil
name = "Piddy"
let unwrapped = name!            // force unwrap (dangerous)
let safe = name ?? "default"     // nil coalescing

if let name = name {
    print("Has name: \\(name)")
}

guard let name = name else { return }
```

## Types
```swift
Int, Int8, Int16, Int32, Int64
UInt, UInt8, UInt16, UInt32, UInt64
Float, Double
Bool
String, Character
Array<T>, [T]
Dictionary<K,V>, [K:V]
Set<T>
Optional<T>, T?
(Int, String)                  // Tuple
```

## Collections
```swift
var arr = [1, 2, 3]
arr.append(4)
arr += [5, 6]

var dict = ["name": "Alice", "city": "NYC"]
dict["age"] = "30"

var set: Set = [1, 2, 3]
set.insert(4)

// Functional
arr.map { $0 * 2 }
arr.filter { $0 > 2 }
arr.reduce(0, +)
arr.compactMap { Int($0) }  // removes nils
arr.sorted { $0 < $1 }
```

## Enums
```swift
enum Direction {
    case north, south, east, west
}

// Associated values
enum Result<T> {
    case success(T)
    case failure(Error)
}

// Raw values
enum Planet: Int {
    case mercury = 1, venus, earth
}

// Pattern matching
switch result {
case .success(let value):
    print(value)
case .failure(let error):
    print(error)
}
```

## Structs & Classes
```swift
// Struct (value type, preferred)
struct Point {
    var x: Double
    var y: Double
    
    func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return (dx*dx + dy*dy).squareRoot()
    }
    
    mutating func translate(dx: Double, dy: Double) {
        x += dx; y += dy
    }
}

// Class (reference type, use when needed)
class ViewModel: ObservableObject {
    @Published var items: [Item] = []
}
```

## Protocols
```swift
protocol Drawable {
    var color: Color { get }
    func draw()
}

extension Drawable {
    func draw() { print("Drawing in \\(color)") }
}

struct Circle: Drawable {
    let color: Color
    let radius: Double
}
```

## Error Handling
```swift
enum AppError: Error {
    case notFound(String)
    case networkError(underlying: Error)
}

func load() throws -> Data {
    guard let data = try? fetchData() else {
        throw AppError.notFound("data")
    }
    return data
}

do {
    let data = try load()
} catch AppError.notFound(let what) {
    print("Not found: \\(what)")
} catch {
    print("Error: \\(error)")
}
```

## Concurrency (Swift 5.5+)
```swift
func fetchUser() async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Structured concurrency
async let a = fetchA()
async let b = fetchB()
let (resultA, resultB) = try await (a, b)

// Actor
actor Counter {
    private var value = 0
    func increment() { value += 1 }
    func get() -> Int { value }
}
```

## Key Ecosystem
- **UI**: SwiftUI, UIKit, AppKit
- **Networking**: URLSession, Alamofire
- **Reactive**: Combine, AsyncSequence
- **Data**: CoreData, SwiftData, GRDB
- **Test**: XCTest, Swift Testing
"""


def _kotlin():
    return """# Kotlin Quick Reference

## Overview
- **Type**: Compiled, statically typed, multi-paradigm
- **File Extension**: `.kt`, `.kts`
- **Build**: Gradle (Kotlin DSL)
- **Platforms**: JVM, Android, Native, JS, WASM
- **Version**: Kotlin 2.0+

## Basics
```kotlin
val immutable = 42        // val = final
var mutable = "hello"     // var = reassignable
const val PI = 3.14159    // compile-time constant

// Type inference
val name = "Piddy"        // String inferred
val list = listOf(1, 2)   // List<Int> inferred

// String templates
val msg = "Name: $name, Length: ${name.length}"

// Null safety
val nullable: String? = null
val safe = nullable?.length ?: 0  // Elvis operator
val forced = nullable!!.length    // throws if null
```

## Functions
```kotlin
fun add(a: Int, b: Int): Int = a + b

// Default & named params
fun greet(name: String, greeting: String = "Hello") =
    "$greeting, $name!"

greet("Piddy", greeting = "Hi")

// Extension functions
fun String.isPalindrome(): Boolean =
    this == this.reversed()

"racecar".isPalindrome() // true

// Higher-order functions
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> =
    filter(predicate)
```

## Classes
```kotlin
// Data class (equals, hashCode, toString, copy)
data class User(
    val name: String,
    val email: String,
    val age: Int = 0
)

val user = User("Alice", "alice@example.com")
val copy = user.copy(age = 30)
val (name, email) = user  // destructuring

// Sealed class
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val msg: String) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// Object (singleton)
object Database {
    fun connect() = "connected"
}
```

## Null Safety
```kotlin
val str: String? = possiblyNull()

// Safe call
str?.length

// Elvis
val len = str?.length ?: 0

// Smart cast
if (str != null) {
    println(str.length)  // str is smart-cast to String
}

// let
str?.let { nonNull ->
    println(nonNull.length)
}
```

## Collections
```kotlin
val list = listOf(1, 2, 3)          // immutable
val mutableList = mutableListOf(1)   // mutable

val map = mapOf("a" to 1, "b" to 2)
val set = setOf(1, 2, 3)

// Operations
list.filter { it > 1 }
list.map { it * 2 }
list.flatMap { listOf(it, it * 2) }
list.groupBy { it % 2 }
list.associate { it to it.toString() }
list.any { it > 2 }
list.none { it < 0 }
list.sumOf { it * it }

// Sequences (lazy)
list.asSequence()
    .filter { it > 0 }
    .map { it * 2 }
    .toList()
```

## Coroutines
```kotlin
import kotlinx.coroutines.*

suspend fun fetchData(): String {
    delay(1000)
    return "data"
}

fun main() = runBlocking {
    val deferred = async { fetchData() }
    val result = deferred.await()

    // Parallel
    coroutineScope {
        val a = async { fetchA() }
        val b = async { fetchB() }
        println("${a.await()}, ${b.await()}")
    }
}

// Flow (reactive streams)
fun numbers(): Flow<Int> = flow {
    for (i in 1..10) {
        delay(100)
        emit(i)
    }
}
```

## When Expression
```kotlin
val result = when (value) {
    0 -> "zero"
    in 1..9 -> "single digit"
    is String -> "string: $value"
    else -> "other"
}

// Exhaustive when with sealed classes
when (result) {
    is Result.Success -> handleSuccess(result.value)
    is Result.Error -> handleError(result.msg)
    Result.Loading -> showLoading()
}
```

## Key Ecosystem
- **Android**: Jetpack Compose, ViewModel, Room
- **Server**: Ktor, Spring Boot
- **Multiplatform**: KMM, Compose Multiplatform
- **Serialization**: kotlinx.serialization
- **Async**: kotlinx.coroutines
- **Test**: JUnit, kotest, MockK
"""


def _sql():
    return """# SQL Quick Reference

## Overview
- **Type**: Declarative query language
- **Dialects**: PostgreSQL, MySQL, SQLite, SQL Server, Oracle
- **Key Use**: Relational database operations

## DDL (Data Definition)
```sql
-- Create table
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    age         INTEGER CHECK (age >= 0),
    role        VARCHAR(20) DEFAULT 'user',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alter table
ALTER TABLE users ADD COLUMN bio TEXT;
ALTER TABLE users ALTER COLUMN name SET NOT NULL;
ALTER TABLE users DROP COLUMN bio;

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name_role ON users(name, role);

-- Drop
DROP TABLE IF EXISTS users CASCADE;
```

## DML (Data Manipulation)
```sql
-- Insert
INSERT INTO users (name, email, age)
VALUES ('Alice', 'alice@example.com', 30);

INSERT INTO users (name, email, age) VALUES
    ('Bob', 'bob@example.com', 25),
    ('Charlie', 'charlie@example.com', 35);

-- Update
UPDATE users SET role = 'admin' WHERE email = 'alice@example.com';

-- Delete
DELETE FROM users WHERE age < 18;

-- Upsert (PostgreSQL)
INSERT INTO users (email, name) VALUES ('alice@example.com', 'Alice')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;
```

## Queries
```sql
-- Basic select
SELECT name, email FROM users WHERE age > 25 ORDER BY name;

-- Aliases
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.name;

-- Filtering
WHERE age BETWEEN 18 AND 65
WHERE name LIKE 'A%'
WHERE name ILIKE '%alice%'   -- case-insensitive (PostgreSQL)
WHERE role IN ('admin', 'moderator')
WHERE email IS NOT NULL

-- Pagination
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 40;
```

## Joins
```sql
-- INNER JOIN (matching rows only)
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON o.user_id = u.id;

-- LEFT JOIN (all left + matching right)
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;

-- RIGHT JOIN, FULL OUTER JOIN, CROSS JOIN also available

-- Self join
SELECT e.name, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

## Aggregation
```sql
SELECT
    role,
    COUNT(*) AS total,
    AVG(age) AS avg_age,
    MIN(age) AS youngest,
    MAX(age) AS oldest,
    SUM(salary) AS total_salary
FROM users
GROUP BY role
HAVING COUNT(*) > 5
ORDER BY total DESC;
```

## Subqueries & CTEs
```sql
-- Subquery
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 100);

-- CTE (Common Table Expression)
WITH active_users AS (
    SELECT * FROM users WHERE last_login > NOW() - INTERVAL '30 days'
),
top_spenders AS (
    SELECT user_id, SUM(total) AS total_spent
    FROM orders
    GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT au.name, ts.total_spent
FROM active_users au
JOIN top_spenders ts ON ts.user_id = au.id;

-- Recursive CTE
WITH RECURSIVE tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, t.depth + 1
    FROM categories c JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth, name;
```

## Window Functions
```sql
SELECT
    name,
    salary,
    department,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
    SUM(salary) OVER (PARTITION BY department) AS dept_total,
    AVG(salary) OVER (
        ORDER BY hire_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg
FROM employees;
```

## Transactions
```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- or ROLLBACK if something fails

-- Savepoints
SAVEPOINT sp1;
-- ... operations ...
ROLLBACK TO sp1;
```

## Useful PostgreSQL Features
```sql
-- JSON
SELECT data->>'name' FROM records WHERE data->>'type' = 'user';
SELECT jsonb_agg(name) FROM users;

-- Array
SELECT * FROM posts WHERE tags @> ARRAY['python'];

-- Full text search
SELECT * FROM articles
WHERE to_tsvector('english', body) @@ to_tsquery('rust & async');

-- LATERAL join
SELECT u.name, latest.*
FROM users u
LEFT JOIN LATERAL (
    SELECT * FROM orders WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1
) latest ON true;
```
"""


def _r():
    return """# R Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, functional
- **File Extension**: `.R`, `.Rmd`
- **Package Manager**: CRAN, install.packages()
- **IDE**: RStudio, VS Code
- **Key Use**: Statistical computing, data analysis, visualization

## Basics
```r
# Variables (no declaration keyword needed)
x <- 42              # preferred assignment
y = 3.14             # also works
name <- "Piddy"

# Data types
class(42)            # "numeric"
class(42L)           # "integer"
class("hello")       # "character"
class(TRUE)          # "logical"
class(1+2i)          # "complex"
class(NULL)          # "NULL"
class(NA)            # "logical" (missing value)
```

## Vectors
```r
# Atomic vectors (homogeneous)
nums <- c(1, 2, 3, 4, 5)
chars <- c("a", "b", "c")
bools <- c(TRUE, FALSE, TRUE)

# Sequences
1:10                # 1 to 10
seq(0, 1, by=0.1)  # 0.0, 0.1, ..., 1.0
rep(0, 10)          # ten zeros

# Vectorized operations
nums * 2            # element-wise
nums > 3            # logical vector
sum(nums), mean(nums), sd(nums)

# Indexing (1-based!)
nums[1]             # first element
nums[c(1, 3)]       # 1st and 3rd
nums[-1]            # all except first
nums[nums > 3]      # filtered
```

## Data Frames
```r
# Create
df <- data.frame(
    name = c("Alice", "Bob", "Charlie"),
    age = c(30, 25, 35),
    score = c(85, 92, 78)
)

# Access
df$name              # column vector
df[1, ]              # first row
df[, "age"]          # age column
df[df$age > 25, ]    # filter rows

# Tidyverse (dplyr)
library(dplyr)

result <- df %>%
    filter(age > 25) %>%
    mutate(grade = ifelse(score > 85, "A", "B")) %>%
    arrange(desc(score)) %>%
    select(name, grade)
```

## Functions
```r
add <- function(a, b = 0) {
    return(a + b)    # explicit return
}

# Last expression is returned implicitly
square <- function(x) x^2

# Apply family
sapply(1:5, square)           # simplified output
lapply(1:5, square)           # list output
apply(matrix, 1, sum)         # rows (1) or cols (2)
Map(function(x, y) x + y, a, b)
```

## Visualization (ggplot2)
```r
library(ggplot2)

ggplot(df, aes(x = age, y = score, color = name)) +
    geom_point(size = 3) +
    geom_smooth(method = "lm") +
    labs(title = "Score vs Age", x = "Age", y = "Score") +
    theme_minimal()

# Quick plots
hist(data$values)
plot(x, y)
boxplot(score ~ group, data = df)
```

## Control Flow
```r
# if/else
if (x > 0) {
    "positive"
} else if (x == 0) {
    "zero"
} else {
    "negative"
}

# Vectorized ifelse
ifelse(x > 0, "pos", "non-pos")

# for loop (prefer vectorized/apply when possible)
for (i in 1:10) {
    cat(i, "\\n")
}
```

## Key Ecosystem
- **Tidyverse**: dplyr, ggplot2, tidyr, readr, purrr, stringr
- **Stats/ML**: caret, randomForest, xgboost, glmnet
- **Reporting**: R Markdown, Quarto, Shiny
- **Data I/O**: readr, readxl, jsonlite, DBI
- **Spatial**: sf, terra, leaflet
"""


def _scala():
    return """# Scala Quick Reference

## Overview
- **Type**: Compiled (JVM), statically typed, multi-paradigm
- **File Extension**: `.scala`, `.sc`
- **Build**: sbt, Mill, Gradle
- **Version**: Scala 3 (Dotty)
- **Key Use**: Data engineering, distributed systems, FP

## Basics (Scala 3)
```scala
// Variables
val immutable = 42       // immutable (preferred)
var mutable = "hello"    // mutable

// Type inference
val name = "Piddy"       // String inferred
val nums = List(1, 2, 3) // List[Int] inferred

// String interpolation
val msg = s"Name: $name, length: ${name.length}"

// Top-level definitions (no class wrapper needed)
@main def hello(): Unit =
  println("Hello, Scala 3!")
```

## Types & Collections
```scala
// Collections
val list = List(1, 2, 3)
val vec = Vector(1, 2, 3)
val map = Map("a" -> 1, "b" -> 2)
val set = Set(1, 2, 3)
val tuple = (1, "hello", true)

// Operations
list.map(_ * 2)
list.filter(_ > 1)
list.flatMap(x => List(x, x * 2))
list.foldLeft(0)(_ + _)
list.zip(other)
list.groupBy(_ % 2)

// Option
val opt: Option[Int] = Some(42)
opt.map(_ + 1).getOrElse(0)
opt match
  case Some(v) => s"got $v"
  case None => "empty"
```

## Classes & Traits
```scala
// Class
class Animal(val name: String):
  def speak: String = "..."

// Case class (immutable data)
case class User(name: String, age: Int)
val u = User("Alice", 30)
val u2 = u.copy(age = 31)

// Trait (interface with implementation)
trait Printable:
  def print(): Unit
  def format: String = toString

// Enum
enum Color:
  case Red, Green, Blue

enum Result[+T]:
  case Ok(value: T)
  case Err(message: String)

// Extension methods
extension (s: String)
  def isPalindrome: Boolean = s == s.reverse
```

## Pattern Matching
```scala
value match
  case 0 => "zero"
  case n if n > 0 => s"positive: $n"
  case User(name, age) if age > 18 => s"adult: $name"
  case _: String => "some string"
  case _ => "other"
```

## Given / Using (Implicits in Scala 3)
```scala
trait Ordering[T]:
  def compare(a: T, b: T): Int

given intOrdering: Ordering[Int] with
  def compare(a: Int, b: Int) = a - b

def sort[T](list: List[T])(using ord: Ordering[T]): List[T] = ???
```

## Key Ecosystem
- **Big Data**: Apache Spark, Flink
- **Web**: Play Framework, http4s, Tapir
- **FP**: Cats, ZIO, Scalaz
- **Build**: sbt, Mill
- **Test**: ScalaTest, MUnit, specs2
"""


def _elixir():
    return """# Elixir Quick Reference

## Overview
- **Type**: Compiled (BEAM VM), dynamically typed, functional
- **File Extension**: `.ex`, `.exs`
- **Build**: mix
- **Package Manager**: Hex
- **Key Feature**: Fault-tolerant, concurrent, distributed (Erlang VM)

## Basics
```elixir
# Variables (immutable bindings, rebindable)
name = "Piddy"
age = 3

# Atoms (like Ruby symbols)
:ok
:error
true  # same as :true

# Strings
"Hello, #{name}!"     # interpolation
<<104, 101, 108>>     # binary/bitstring

# Integers
1_000_000
0xFF
0b1010
```

## Types
```elixir
42                    # integer
3.14                  # float
true, false           # boolean (atoms)
:atom                 # atom
"string"              # string (UTF-8 binary)
[1, 2, 3]            # list (linked list)
{1, 2, 3}            # tuple
%{key: "value"}       # map
%User{name: "Alice"}  # struct
<<1, 2, 3>>           # binary
fn x -> x end         # anonymous function
```

## Pattern Matching
```elixir
# Assignment IS pattern matching
{:ok, result} = {:ok, 42}
[head | tail] = [1, 2, 3, 4]
%{name: name} = %{name: "Alice", age: 30}

# Case
case response do
  {:ok, body} -> process(body)
  {:error, reason} -> handle_error(reason)
  _ -> :unknown
end

# With (chain pattern matches)
with {:ok, user} <- fetch_user(id),
     {:ok, profile} <- fetch_profile(user) do
  {:ok, build_response(user, profile)}
else
  {:error, reason} -> {:error, reason}
end
```

## Functions & Modules
```elixir
defmodule Math do
  # Public function
  def add(a, b), do: a + b

  # Private function
  defp validate(x) when is_number(x), do: :ok

  # Multiple clauses (pattern matching)
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)

  # Default args
  def greet(name, greeting \\\\ "Hello") do
    "#{greeting}, #{name}!"
  end
end

# Anonymous functions
add = fn a, b -> a + b end
add.(1, 2)  # => 3

# Capture operator
double = &(&1 * 2)
Enum.map([1,2,3], &(&1 * 2))
```

## Pipe Operator
```elixir
# Transform data through a pipeline
result =
  data
  |> Enum.filter(&(&1 > 0))
  |> Enum.map(&(&1 * 2))
  |> Enum.sum()
```

## Enum & Stream
```elixir
Enum.map([1, 2, 3], &(&1 * 2))
Enum.filter(list, &(&1 > 0))
Enum.reduce(list, 0, &(&1 + &2))
Enum.group_by(users, & &1.role)
Enum.chunk_every(list, 3)

# Lazy streams
1..1_000_000
|> Stream.filter(&(rem(&1, 2) == 0))
|> Stream.map(&(&1 * &1))
|> Enum.take(10)
```

## Concurrency (OTP)
```elixir
# Spawn process
pid = spawn(fn -> receive do msg -> IO.puts(msg) end end)
send(pid, "hello")

# GenServer
defmodule Counter do
  use GenServer

  def start_link(init), do: GenServer.start_link(__MODULE__, init)
  def increment(pid), do: GenServer.cast(pid, :increment)
  def get(pid), do: GenServer.call(pid, :get)

  @impl true
  def init(count), do: {:ok, count}

  @impl true
  def handle_cast(:increment, count), do: {:noreply, count + 1}

  @impl true
  def handle_call(:get, _from, count), do: {:reply, count, count}
end

# Supervisor
children = [
  {Counter, 0},
  {MyWorker, []}
]
Supervisor.start_link(children, strategy: :one_for_one)
```

## Key Ecosystem
- **Web**: Phoenix Framework, LiveView
- **Database**: Ecto
- **Test**: ExUnit (built-in)
- **HTTP Client**: Req, Finch
- **Background Jobs**: Oban
- **Distributed**: libcluster, Horde
"""


def _dart():
    return """# Dart Quick Reference

## Overview
- **Type**: Compiled (AOT & JIT), statically typed
- **File Extension**: `.dart`
- **Package Manager**: pub (pub.dev)
- **Platforms**: Mobile (Flutter), Web, Server, Desktop
- **Version**: Dart 3+

## Basics
```dart
void main() {
  var inferred = 42;         // type inferred
  int explicit = 42;         // explicit type
  final name = "Piddy";      // runtime constant
  const pi = 3.14;           // compile-time constant

  // String interpolation
  print('Hello, $name! Pi is ${pi.toStringAsFixed(2)}');

  // Null safety
  String? nullable = null;
  String safe = nullable ?? "default";
  int? len = nullable?.length;
}
```

## Types
```dart
int, double, num                // numbers
String                          // strings
bool                            // boolean
List<T>                         // list/array
Set<T>                          // set
Map<K, V>                       // map/dictionary
dynamic                         // opt-out of type checking
Object                          // base of all types
Future<T>, Stream<T>            // async types
Record (int, String)            // records (Dart 3)
```

## Classes
```dart
class Animal {
  final String name;
  Animal(this.name);           // shorthand constructor
  String speak() => '...';
}

class Dog extends Animal {
  Dog(super.name);             // super parameters (Dart 3)
  @override
  String speak() => 'Woof!';
}

// Mixins
mixin Loggable {
  void log(String msg) => print('[${runtimeType}] $msg');
}

class Service with Loggable {}
```

## Sealed Classes & Patterns (Dart 3)
```dart
sealed class Shape {}
class Circle extends Shape { final double radius; Circle(this.radius); }
class Square extends Shape { final double side; Square(this.side); }

double area(Shape s) => switch (s) {
  Circle(radius: var r) => 3.14 * r * r,
  Square(side: var s) => s * s,
};
```

## Async
```dart
Future<String> fetchData() async {
  final response = await http.get(Uri.parse(url));
  return response.body;
}

// Streams
Stream<int> countStream(int max) async* {
  for (var i = 0; i < max; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}

await for (final value in countStream(5)) {
  print(value);
}
```

## Collections
```dart
var list = [1, 2, 3];
var set = {1, 2, 3};
var map = {'key': 'value'};

// Spread & collection if/for
var combined = [...list1, ...list2];
var conditional = [1, 2, if (flag) 3];
var generated = [for (var i in list) i * 2];

// Methods
list.map((e) => e * 2).toList();
list.where((e) => e > 1).toList();
list.fold<int>(0, (sum, e) => sum + e);
```

## Key Ecosystem
- **Mobile/Desktop**: Flutter
- **Web**: dart:html, AngularDart
- **Server**: shelf, dart_frog
- **State**: Riverpod, Bloc, Provider
- **Test**: package:test (built-in)
"""


def _graphql():
    return """# GraphQL Quick Reference

## Overview
- **Type**: Query language for APIs
- **Schema Language**: SDL (Schema Definition Language)
- **Transport**: Typically HTTP POST
- **Key Feature**: Client specifies exact data shape needed

## Schema Definition
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  age: Int
  posts: [Post!]!
  role: Role!
}

type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
}

enum Role {
  USER
  ADMIN
  MODERATOR
}

input CreateUserInput {
  name: String!
  email: String!
  age: Int
}

type Query {
  user(id: ID!): User
  users(limit: Int = 10, offset: Int = 0): [User!]!
  searchPosts(query: String!): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

type Subscription {
  postCreated: Post!
  userStatusChanged(userId: ID!): User!
}
```

## Queries
```graphql
# Basic query
query GetUser {
  user(id: "123") {
    name
    email
    posts {
      title
    }
  }
}

# With variables
query GetUser($id: ID!) {
  user(id: $id) {
    name
    email
  }
}

# Fragments
fragment UserFields on User {
  id
  name
  email
}

query {
  user(id: "1") { ...UserFields }
  admin: user(id: "2") { ...UserFields role }
}

# Inline fragments (unions/interfaces)
query Search($q: String!) {
  search(query: $q) {
    ... on User { name email }
    ... on Post { title body }
  }
}
```

## Mutations
```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
  }
}

# Variables:
# { "input": { "name": "Alice", "email": "alice@example.com" } }
```

## Directives
```graphql
query GetUser($id: ID!, $withPosts: Boolean!) {
  user(id: $id) {
    name
    email
    posts @include(if: $withPosts) {
      title
    }
    secretField @skip(if: true)
  }
}
```

## Key Ecosystem
- **Server**: Apollo Server, GraphQL Yoga, Strawberry (Python)
- **Client**: Apollo Client, urql, Relay
- **Code Gen**: GraphQL Code Generator
- **Tools**: GraphiQL, Apollo Studio, Altair
- **Validation**: graphql-shield, graphql-armor
"""


def _bash():
    return """# Bash / Shell Quick Reference

## Overview
- **Type**: Interpreted, command language
- **File Extension**: `.sh`, `.bash`
- **Shebang**: `#!/usr/bin/env bash`
- **Key Use**: System administration, automation, scripting

## Basics
```bash
#!/usr/bin/env bash
set -euo pipefail  # strict mode: exit on error, undefined vars, pipe failures

# Variables
name="Piddy"
readonly VERSION="1.0"
count=42

# String interpolation
echo "Hello, $name!"
echo "Version: ${VERSION}"
echo "Files: $(ls | wc -l)"

# Quoting
echo "$name"     # interpolated
echo '$name'     # literal
echo "It's \"quoted\""
```

## Conditionals
```bash
# Test expressions
if [[ "$str" == "hello" ]]; then
    echo "match"
elif [[ -f "$file" ]]; then
    echo "file exists"
else
    echo "other"
fi

# Common tests
[[ -f file ]]      # file exists
[[ -d dir ]]       # directory exists
[[ -z "$var" ]]    # string is empty
[[ -n "$var" ]]    # string is not empty
[[ $a -eq $b ]]    # numeric equal
[[ $a -lt $b ]]    # numeric less than
[[ $a == $b ]]     # string equal
[[ $a =~ regex ]]  # regex match

# Inline
[[ -f config.yml ]] && source config.yml || echo "no config"
```

## Loops
```bash
# For
for file in *.txt; do
    echo "Processing $file"
done

for i in {1..10}; do echo "$i"; done

for ((i=0; i<10; i++)); do echo "$i"; done

# While
while read -r line; do
    echo "$line"
done < file.txt

# Until
until [[ $count -ge 10 ]]; do
    ((count++))
done
```

## Functions
```bash
greet() {
    local name="${1:?Name required}"
    local greeting="${2:-Hello}"
    echo "$greeting, $name!"
}

greet "World"
greet "Piddy" "Hey"

# Return values (exit codes)
is_valid() {
    [[ -f "$1" ]] && return 0 || return 1
}

if is_valid "file.txt"; then echo "valid"; fi
```

## Arrays
```bash
# Indexed
arr=(apple banana cherry)
echo "${arr[0]}"           # apple
echo "${arr[@]}"           # all elements
echo "${#arr[@]}"          # length
arr+=(date)                # append

# Associative
declare -A config
config[host]="localhost"
config[port]="8080"
echo "${config[host]}"

# Iteration
for item in "${arr[@]}"; do echo "$item"; done
for key in "${!config[@]}"; do echo "$key=${config[$key]}"; done
```

## String Operations
```bash
str="Hello, World!"
echo "${str,,}"            # lowercase: hello, world!
echo "${str^^}"            # uppercase: HELLO, WORLD!
echo "${str:0:5}"          # substring: Hello
echo "${str/World/Piddy}"  # replace: Hello, Piddy!
echo "${str#*,}"           # remove prefix: World!
echo "${str%,*}"           # remove suffix: Hello
echo "${#str}"             # length: 13
```

## Command Patterns
```bash
# Pipe
cat file.txt | grep "error" | sort | uniq -c | sort -rn

# Redirect
command > output.txt       # stdout to file
command 2> errors.txt      # stderr to file
command &> all.txt         # both to file
command >> append.txt      # append

# Process substitution
diff <(sort file1) <(sort file2)

# Here document
cat <<EOF
Hello, $name!
Today is $(date).
EOF

# Subshell
result=$(date +%Y-%m-%d)
```

## Error Handling
```bash
# Trap
cleanup() { rm -f "$tmpfile"; }
trap cleanup EXIT

# Error handling
command || { echo "Failed" >&2; exit 1; }

# Check exit code
if ! command; then
    echo "command failed with exit code $?" >&2
fi
```

## Useful One-liners
```bash
# Find and replace in files
find . -name "*.py" -exec sed -i 's/old/new/g' {} +

# Watch for changes
while inotifywait -r -e modify src/; do make build; done

# Parallel execution
cat urls.txt | xargs -P 4 -I{} curl -sO {}

# JSON parsing (jq)
curl -s api.example.com/data | jq '.items[] | {name, id}'
```
"""


def _html():
    return """# HTML Quick Reference

## Overview
- **Type**: Markup language
- **File Extension**: `.html`, `.htm`
- **Standard**: HTML5 (Living Standard)
- **Key Use**: Web page structure and content

## Document Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Page description">
    <title>Page Title</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <nav>...</nav>
    </header>
    <main>
        <article>...</article>
        <aside>...</aside>
    </main>
    <footer>...</footer>
    <script src="app.js" defer></script>
</body>
</html>
```

## Semantic Elements
```html
<header>    <!-- Page/section header -->
<nav>       <!-- Navigation links -->
<main>      <!-- Main content (one per page) -->
<article>   <!-- Self-contained content -->
<section>   <!-- Thematic grouping -->
<aside>     <!-- Sidebar/tangential content -->
<footer>    <!-- Page/section footer -->
<figure>    <!-- Self-contained media with caption -->
<figcaption>
<details>   <!-- Expandable content -->
<summary>   <!-- Summary for details -->
<dialog>    <!-- Modal/dialog box -->
<mark>      <!-- Highlighted text -->
<time>      <!-- Date/time -->
```

## Forms
```html
<form action="/submit" method="POST">
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" required
           placeholder="Enter name" minlength="2" maxlength="50">

    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>

    <label for="pass">Password:</label>
    <input type="password" id="pass" name="password"
           pattern="(?=.*\\d)(?=.*[a-z]).{8,}">

    <select name="role">
        <option value="">Choose...</option>
        <option value="dev">Developer</option>
        <option value="design">Designer</option>
    </select>

    <textarea name="bio" rows="4" cols="50"></textarea>

    <input type="checkbox" id="agree" name="agree">
    <label for="agree">I agree</label>

    <button type="submit">Submit</button>
</form>
```

## Input Types
```
text, password, email, url, tel, number, range,
date, time, datetime-local, month, week,
color, file, hidden, search,
checkbox, radio, submit, reset, button
```

## Media
```html
<img src="photo.jpg" alt="Description" loading="lazy"
     width="800" height="600">

<picture>
    <source srcset="photo.webp" type="image/webp">
    <source srcset="photo.jpg" type="image/jpeg">
    <img src="photo.jpg" alt="Fallback">
</picture>

<video controls width="640">
    <source src="video.mp4" type="video/mp4">
</video>

<audio controls>
    <source src="audio.mp3" type="audio/mpeg">
</audio>
```

## Common Attributes
```
id, class, style, title, hidden, tabindex,
data-*, aria-*, role,
draggable, contenteditable, spellcheck,
autofocus, disabled, readonly
```

## Key Companion Technologies
- **Styling**: CSS3, Tailwind, Bootstrap
- **Scripting**: JavaScript, TypeScript
- **Templating**: JSX, Jinja2, Handlebars, EJS
- **Accessibility**: ARIA roles, landmarks
"""


def _css():
    return """# CSS Quick Reference

## Overview
- **Type**: Stylesheet language
- **File Extension**: `.css`
- **Standard**: CSS3+ (modular)
- **Key Use**: Visual presentation of HTML

## Selectors
```css
/* Element, class, ID */
div { }
.class { }
#id { }

/* Combinators */
.parent .descendant { }     /* descendant */
.parent > .child { }        /* direct child */
.element + .adjacent { }    /* adjacent sibling */
.element ~ .general { }     /* general sibling */

/* Pseudo-classes */
:hover, :focus, :active, :visited
:first-child, :last-child, :nth-child(2n+1)
:not(.excluded), :is(.a, .b, .c)
:has(.child)                /* parent selector */
:where(.a, .b)              /* zero specificity */

/* Pseudo-elements */
::before, ::after, ::first-line, ::placeholder
```

## Box Model
```css
.box {
    /* Content → Padding → Border → Margin */
    box-sizing: border-box;  /* include padding/border in width */
    width: 300px;
    padding: 16px;
    border: 1px solid #ccc;
    margin: 0 auto;          /* center horizontally */
}
```

## Flexbox
```css
.flex-container {
    display: flex;
    flex-direction: row;          /* row | column */
    justify-content: center;      /* main axis */
    align-items: center;          /* cross axis */
    gap: 16px;
    flex-wrap: wrap;
}

.flex-item {
    flex: 1;                      /* grow: 1, shrink: 1, basis: 0 */
    flex: 0 0 200px;              /* fixed width item */
}
```

## Grid
```css
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto 1fr auto;
    gap: 16px;
}

.grid-item {
    grid-column: 1 / 3;          /* span 2 columns */
    grid-row: 1 / -1;            /* full height */
}

/* Named areas */
.layout {
    grid-template-areas:
        "header header"
        "sidebar main"
        "footer footer";
    grid-template-columns: 250px 1fr;
}
.header { grid-area: header; }
```

## Custom Properties (Variables)
```css
:root {
    --color-primary: #3b82f6;
    --color-bg: #0f172a;
    --spacing-md: 16px;
    --radius: 8px;
    --font-sans: system-ui, -apple-system, sans-serif;
}

.button {
    background: var(--color-primary);
    padding: var(--spacing-md);
    border-radius: var(--radius);
    font-family: var(--font-sans);
}
```

## Responsive Design
```css
/* Mobile first */
.container { width: 100%; padding: 16px; }

@media (min-width: 768px) {
    .container { max-width: 720px; margin: 0 auto; }
}

@media (min-width: 1024px) {
    .container { max-width: 960px; }
}

/* Container queries */
@container (min-width: 400px) {
    .card { grid-template-columns: 1fr 2fr; }
}

/* Prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    :root { --color-bg: #0f172a; --color-text: #f8fafc; }
}
```

## Animations
```css
/* Transitions */
.button {
    transition: all 0.2s ease-in-out;
}
.button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* Keyframes */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.element { animation: fadeIn 0.3s ease-out; }
```

## Modern CSS Features
```css
/* Container queries */
.card-container { container-type: inline-size; }

/* Nesting (native) */
.card {
    padding: 16px;
    & .title { font-size: 1.5rem; }
    &:hover { background: #f0f0f0; }
}

/* Subgrid */
.grid-item { display: grid; grid-template-rows: subgrid; }

/* Scroll snap */
.carousel {
    scroll-snap-type: x mandatory;
    overflow-x: auto;
}
.slide { scroll-snap-align: start; }

/* Aspect ratio */
.video { aspect-ratio: 16 / 9; }

/* Clamp */
h1 { font-size: clamp(1.5rem, 4vw, 3rem); }
```
"""


def _lua():
    return """# Lua Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, multi-paradigm
- **File Extension**: `.lua`
- **Version**: Lua 5.4
- **Key Use**: Game scripting (Love2D, Roblox), embedded systems, config

## Basics
```lua
-- Variables (global by default)
x = 42
local y = 3.14       -- local scope (preferred)

-- Types
type(42)         --> "number"
type("hello")    --> "string"
type(true)       --> "boolean"
type(nil)        --> "nil"
type({})         --> "table"
type(print)      --> "function"

-- String
local s = "hello"
local multi = [[
    multiline
    string
]]
local fmt = string.format("x=%d, y=%.2f", x, y)
print("Hello " .. "World")  -- concatenation
```

## Tables (The Universal Data Structure)
```lua
-- Array-style (1-indexed!)
local arr = {10, 20, 30}
print(arr[1])   --> 10
print(#arr)     --> 3

-- Dictionary-style
local config = {
    host = "localhost",
    port = 8080,
    debug = true,
}
print(config.host)
print(config["port"])

-- Mixed
local data = {
    "first",
    name = "Piddy",
    42,
}
```

## Control Flow
```lua
-- If/elseif/else
if x > 0 then
    print("positive")
elseif x == 0 then
    print("zero")
else
    print("negative")
end

-- For (numeric)
for i = 1, 10 do print(i) end
for i = 10, 1, -1 do print(i) end

-- For (generic)
for key, value in pairs(tbl) do print(key, value) end
for i, v in ipairs(arr) do print(i, v) end

-- While / repeat
while condition do end
repeat until condition
```

## Functions
```lua
local function add(a, b)
    return a + b
end

-- Multiple return values
local function divmod(a, b)
    return math.floor(a/b), a % b
end
local q, r = divmod(17, 5)

-- Variadic
local function sum(...)
    local args = {...}
    local total = 0
    for _, v in ipairs(args) do total = total + v end
    return total
end

-- Closures
local function counter()
    local count = 0
    return function()
        count = count + 1
        return count
    end
end
```

## OOP via Metatables
```lua
local Animal = {}
Animal.__index = Animal

function Animal:new(name)
    return setmetatable({name = name}, self)
end

function Animal:speak()
    return self.name .. " says ..."
end

local Dog = setmetatable({}, {__index = Animal})
Dog.__index = Dog

function Dog:speak()
    return self.name .. " says Woof!"
end

local d = Dog:new("Rex")
print(d:speak())  --> Rex says Woof!
```

## Error Handling
```lua
-- pcall (protected call)
local ok, err = pcall(function()
    error("something went wrong")
end)

if not ok then
    print("Error: " .. err)
end

-- xpcall (with error handler)
xpcall(risky_func, function(err)
    print(debug.traceback(err))
end)
```

## Key Ecosystem
- **Game**: Love2D, Defold, Roblox (Luau)
- **Embedded**: OpenResty (nginx), Redis, Neovim
- **Config**: Awesome WM, Hammerspoon, Pandoc
- **Package**: LuaRocks
"""


def _perl():
    return """# Perl Quick Reference

## Overview
- **Type**: Interpreted, dynamically typed, multi-paradigm
- **File Extension**: `.pl`, `.pm`
- **Package Manager**: CPAN, cpanminus
- **Version**: Perl 5.38+
- **Key Use**: Text processing, system admin, bioinformatics

## Basics
```perl
use strict;
use warnings;
use v5.36;  # enables signatures, say, etc.

# Variables (sigils)
my $scalar = 42;              # scalar: $
my @array = (1, 2, 3);       # array: @
my %hash = (a => 1, b => 2); # hash: %

# String
my $name = "Piddy";
say "Hello, $name!";         # interpolation
say 'Hello, $name';          # literal

# Regex
if ($text =~ /pattern/i) { }          # match
$text =~ s/old/new/g;                 # substitute
my @matches = ($text =~ /(\w+)/g);    # capture all
```

## Subroutines (Perl 5.36+ signatures)
```perl
sub greet($name, $greeting = "Hello") {
    return "$greeting, $name!";
}

# Classic style
sub add {
    my ($a, $b) = @_;
    return $a + $b;
}
```

## Arrays & Hashes
```perl
# Arrays
my @arr = (1, 2, 3);
push @arr, 4;
my $first = shift @arr;
my @sorted = sort @arr;
my @filtered = grep { $_ > 2 } @arr;
my @mapped = map { $_ * 2 } @arr;

# Hashes
my %config = (host => "localhost", port => 8080);
$config{debug} = 1;
my @keys = keys %config;
my @vals = values %config;
while (my ($k, $v) = each %config) { say "$k=$v"; }
exists $config{host};
delete $config{debug};
```

## File I/O
```perl
# Read
open(my $fh, '<', 'file.txt') or die "Cannot open: $!";
while (my $line = <$fh>) {
    chomp $line;
    say $line;
}
close $fh;

# Write
open(my $out, '>', 'output.txt') or die "Cannot open: $!";
print $out "Hello\\n";
close $out;

# One-liner read
my $content = do { local $/; open my $f, '<', 'file.txt'; <$f> };
```

## Regex Power
```perl
# Named captures
if ($str =~ /(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})/) {
    say "Year: $+{year}";
}

# Non-greedy
$str =~ /<.*?>/;

# Lookahead/lookbehind
$str =~ /(?<=@)\\w+/;     # word after @
$str =~ /\\w+(?=\\.com)/;  # word before .com
```

## Key Ecosystem
- **Web**: Mojolicious, Dancer2, Catalyst
- **ORM**: DBIx::Class, DBI
- **Test**: Test2, Test::More
- **Text**: Text::CSV, JSON::XS
- **System**: Sys::Syslog, File::Find
"""


def _haskell():
    return """# Haskell Quick Reference

## Overview
- **Type**: Compiled, statically typed, purely functional
- **File Extension**: `.hs`
- **Build**: cabal, stack
- **Package Registry**: Hackage
- **Key Feature**: Lazy evaluation, strong type system, purity

## Basics
```haskell
-- Functions (no parentheses for args)
add :: Int -> Int -> Int
add x y = x + y

-- Application
result = add 3 4  -- 7

-- Let bindings
let x = 42 in x + 1

-- Where clause
bmi weight height = category
  where
    bmi' = weight / height ^ 2
    category
      | bmi' < 18.5 = "underweight"
      | bmi' < 25.0 = "normal"
      | otherwise    = "overweight"
```

## Types
```haskell
-- Basic types
Int, Integer, Float, Double, Bool, Char, String

-- Type aliases
type Name = String
type Pair a b = (a, b)

-- Algebraic data types
data Shape = Circle Double
           | Rectangle Double Double
           deriving (Show, Eq)

area :: Shape -> Double
area (Circle r) = pi * r * r
area (Rectangle w h) = w * h

-- Record syntax
data Person = Person
  { firstName :: String
  , lastName  :: String
  , age       :: Int
  } deriving (Show)

-- Newtype (zero-cost wrapper)
newtype Email = Email String
```

## Lists
```haskell
[1, 2, 3]              -- list literal
1 : [2, 3]             -- cons
[1..10]                -- range
[1,3..20]              -- step range

-- Functions
head [1,2,3]           -- 1
tail [1,2,3]           -- [2,3]
length, null, reverse, take, drop, zip, unzip
map, filter, foldl, foldr, concatMap

-- List comprehension
[x * 2 | x <- [1..10], x > 5]
[(x, y) | x <- [1..3], y <- [1..3], x /= y]
```

## Type Classes
```haskell
-- Defining
class Describable a where
  describe :: a -> String

instance Describable Shape where
  describe (Circle r) = "Circle with radius " ++ show r
  describe (Rectangle w h) = "Rectangle " ++ show w ++ "x" ++ show h

-- Common type classes:
-- Eq, Ord, Show, Read, Enum, Bounded
-- Num, Integral, Floating
-- Functor, Applicative, Monad
-- Foldable, Traversable
-- Semigroup, Monoid
```

## Monads & Do Notation
```haskell
-- Maybe monad
safeDivide :: Double -> Double -> Maybe Double
safeDivide _ 0 = Nothing
safeDivide x y = Just (x / y)

-- Do notation (sugar for >>= chains)
main :: IO ()
main = do
  putStrLn "What's your name?"
  name <- getLine
  putStrLn ("Hello, " ++ name ++ "!")

-- IO
readFile :: FilePath -> IO String
writeFile :: FilePath -> String -> IO ()
```

## Key Ecosystem
- **Web**: Servant, Yesod, Scotty, IHP
- **Parser**: Megaparsec, Attoparsec
- **JSON**: Aeson
- **Database**: Persistent, Beam, Opaleye
- **Concurrency**: async, stm
- **Test**: HSpec, QuickCheck
"""


def _wasm():
    return """# WebAssembly (WASM) Quick Reference

## Overview
- **Type**: Binary instruction format for stack-based VM
- **File Extension**: `.wasm` (binary), `.wat` (text format)
- **Key Feature**: Near-native performance in browsers and servers
- **Source Languages**: Rust, C/C++, Go, AssemblyScript, Zig

## WAT (Text Format)
```wat
(module
  ;; Function that adds two integers
  (func $add (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.add
  )
  (export "add" (func $add))
)
```

## Compile from Rust
```bash
# Setup
rustup target add wasm32-unknown-unknown
cargo install wasm-pack

# Build
wasm-pack build --target web

# Or with cargo directly
cargo build --target wasm32-unknown-unknown --release
```

## JavaScript Integration
```javascript
// Load and instantiate
const response = await fetch('module.wasm');
const bytes = await response.arrayBuffer();
const { instance } = await WebAssembly.instantiate(bytes, imports);

// Call exported function
const result = instance.exports.add(2, 3);

// Shared memory
const memory = new WebAssembly.Memory({ initial: 256 });
const buffer = new Uint8Array(memory.buffer);
```

## WASI (Server-Side)
```bash
# Run WASM outside browser
wasmtime run module.wasm
wasmer run module.wasm

# Compile C to WASI
clang --target=wasm32-wasi -o hello.wasm hello.c
```

## Data Types
```
i32     32-bit integer
i64     64-bit integer
f32     32-bit float
f64     64-bit float
v128    128-bit SIMD vector
funcref function reference
externref external reference
```

## Key Ecosystem
- **Rust**: wasm-bindgen, wasm-pack, Yew
- **C/C++**: Emscripten
- **Go**: TinyGo, standard compiler
- **AssemblyScript**: TypeScript-like → WASM
- **Runtime**: Wasmtime, Wasmer, WasmEdge
- **Web**: wasm-pack, vite-plugin-wasm
"""


def _clojure():
    return """# Clojure Quick Reference

## Overview
- **Type**: Compiled (JVM), dynamically typed, functional
- **File Extension**: `.clj`, `.cljs` (ClojureScript), `.cljc` (portable)
- **Build**: Leiningen, deps.edn (tools.deps)
- **Key Feature**: Lisp dialect, immutable-first, concurrency primitives

## Basics
```clojure
;; Define
(def name "Piddy")
(def pi 3.14159)

;; Let binding (local)
(let [x 42
      y (+ x 1)]
  (println x y))

;; Data types
42          ; Long
3.14        ; Double
"hello"     ; String
:keyword    ; Keyword
'symbol     ; Symbol
true false  ; Boolean
nil         ; Null
```

## Collections (Persistent/Immutable)
```clojure
;; List (linked)
'(1 2 3)
(list 1 2 3)

;; Vector (indexed)
[1 2 3]
(get [1 2 3] 0)   ; => 1
(conj [1 2] 3)    ; => [1 2 3]

;; Map
{:name "Alice" :age 30}
(get {:a 1} :a)     ; => 1
(assoc m :key val)  ; add/update
(dissoc m :key)     ; remove

;; Set
#{1 2 3}
(contains? #{1 2 3} 2) ; => true
```

## Functions
```clojure
;; Define
(defn greet
  "Greets a person."
  [name]
  (str "Hello, " name "!"))

;; Multi-arity
(defn greet
  ([name] (greet name "Hello"))
  ([name greeting] (str greeting ", " name "!")))

;; Anonymous
(fn [x] (* x x))
#(* % %)           ; shorthand

;; Higher-order
(map inc [1 2 3])           ; => (2 3 4)
(filter even? [1 2 3 4])   ; => (2 4)
(reduce + [1 2 3 4])       ; => 10
```

## Threading Macros
```clojure
;; Thread-first (->): inserts as first arg
(-> {:name "Alice" :age 30}
    (assoc :role "admin")
    (update :age inc))

;; Thread-last (->>): inserts as last arg
(->> (range 10)
     (filter even?)
     (map #(* % %))
     (reduce +))
```

## Concurrency
```clojure
;; Atoms (uncoordinated, synchronous)
(def counter (atom 0))
(swap! counter inc)
@counter ; deref => 1

;; Refs (coordinated, synchronous via STM)
(def account (ref 1000))
(dosync (alter account - 100))

;; Agents (uncoordinated, asynchronous)
(def logger (agent []))
(send logger conj "message")
```

## Key Ecosystem
- **Web**: Ring, Compojure, Pedestal, Reitit
- **Database**: next.jdbc, HoneySQL
- **Frontend**: ClojureScript, Reagent, Re-frame
- **Build**: deps.edn, Leiningen
- **Test**: clojure.test, Kaocha
- **REPL**: nREPL, CIDER (Emacs)
"""


# ─── Language Registry ─────────────────────────────────────────────────

LANGUAGES = [
    ("python", "Python", "general-purpose", _python),
    ("javascript", "JavaScript", "web", _javascript),
    ("typescript", "TypeScript", "web", _typescript),
    ("java", "Java", "enterprise", _java),
    ("csharp", "C#", "enterprise", _csharp),
    ("c", "C", "systems", _c),
    ("cpp", "C++", "systems", _cpp),
    ("go", "Go", "systems", _go),
    ("rust", "Rust", "systems", _rust),
    ("ruby", "Ruby", "scripting", _ruby),
    ("php", "PHP", "web", _php),
    ("swift", "Swift", "mobile", _swift),
    ("kotlin", "Kotlin", "mobile", _kotlin),
    ("sql", "SQL", "data", _sql),
    ("r", "R", "data", _r),
    ("scala", "Scala", "enterprise", _scala),
    ("elixir", "Elixir", "concurrent", _elixir),
    ("dart", "Dart", "mobile", _dart),
    ("graphql", "GraphQL", "web", _graphql),
    ("bash", "Bash / Shell", "devops", _bash),
    ("html", "HTML", "web", _html),
    ("css", "CSS", "web", _css),
    ("lua", "Lua", "scripting", _lua),
    ("perl", "Perl", "scripting", _perl),
    ("haskell", "Haskell", "functional", _haskell),
    ("wasm", "WebAssembly", "systems", _wasm),
    ("clojure", "Clojure", "functional", _clojure),
]


def generate_all(target_dir: Path, languages=None):
    """Generate language reference files."""
    target_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    for filename, display_name, category, content_func in LANGUAGES:
        if languages and filename not in languages:
            continue

        filepath = target_dir / f"{filename}.md"
        content = content_func()

        # Add metadata header
        header = f"""---
language: {display_name}
category: {category}
generated: {datetime.now().strftime('%Y-%m-%d')}
source: Piddy Language Reference Generator
---

"""
        filepath.write_text(header + content.strip() + "\n", encoding="utf-8")
        generated.append((filename, display_name, category))
        print(f"  [+] {display_name} ({category}) -> {filepath.name}")

    return generated


def generate_index(target_dir: Path, generated):
    """Generate an index/README for the languages folder."""
    categories = {}
    for filename, display_name, category in sorted(generated, key=lambda x: (x[2], x[1])):
        categories.setdefault(category, []).append((filename, display_name))

    lines = [
        "# Piddy Language References",
        "",
        f"**{len(generated)} programming languages and technologies**",
        "",
        "Concise reference cards for every language Piddy uses and is learning.",
        "These files are auto-ingested into Piddy's knowledge base for offline reference.",
        "",
        "## Languages by Category",
        "",
    ]

    cat_labels = {
        "general-purpose": "General Purpose",
        "web": "Web Technologies",
        "systems": "Systems Programming",
        "enterprise": "Enterprise / JVM",
        "mobile": "Mobile Development",
        "data": "Data & Analytics",
        "scripting": "Scripting Languages",
        "functional": "Functional Programming",
        "concurrent": "Concurrent / Distributed",
        "devops": "DevOps & Automation",
    }

    for cat in ["general-purpose", "web", "systems", "enterprise", "mobile",
                "data", "scripting", "functional", "concurrent", "devops"]:
        if cat not in categories:
            continue
        label = cat_labels.get(cat, cat.title())
        lines.append(f"### {label}")
        for filename, display_name in categories[cat]:
            lines.append(f"- [{display_name}]({filename}.md)")
        lines.append("")

    lines.extend([
        "## Re-generate",
        "",
        "```bash",
        "python scripts/populate_languages.py",
        "```",
        "",
        "## Add a new language",
        "",
        "Add a new entry to the `LANGUAGES` list in `scripts/populate_languages.py`",
        "with a content function, then re-run the script.",
        "",
    ])

    readme = target_dir / "README.md"
    readme.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  [+] README.md (index)")


def main():
    parser = argparse.ArgumentParser(description="Populate Piddy's language references")
    parser.add_argument("languages", nargs="*", help="Specific languages to generate (default: all)")
    parser.add_argument("--list", action="store_true", help="List available languages")
    parser.add_argument("--dir", type=str, default=str(LANGUAGES_DIR), help="Target directory")
    args = parser.parse_args()

    if args.list:
        print(f"\n{'Language':<20} {'Category':<15} {'Filename'}")
        print("-" * 55)
        for filename, display_name, category, _ in LANGUAGES:
            print(f"{display_name:<20} {category:<15} {filename}.md")
        print(f"\nTotal: {len(LANGUAGES)} languages")
        return 0

    target_dir = Path(args.dir)
    langs = args.languages if args.languages else None

    print(f"\n{'='*60}")
    print(f"  Piddy Language Reference Generator")
    print(f"  Target: {target_dir}")
    print(f"{'='*60}\n")

    generated = generate_all(target_dir, langs)
    generate_index(target_dir, generated)

    print(f"\n{'='*60}")
    print(f"  Generated {len(generated)} language references")
    print(f"  Run 'POST /api/skills/reload' to refresh Piddy's knowledge")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
