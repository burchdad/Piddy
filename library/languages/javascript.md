# JavaScript Quick Reference

## Language: JavaScript (ES2024)
**Paradigm:** Multi-paradigm (OOP, functional, event-driven)  
**Typing:** Dynamic, weak  
**Runtime:** V8 (Chrome/Node), SpiderMonkey (Firefox), JavaScriptCore (Safari)  

## Syntax Essentials

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
```

## Data Structures

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
```

## Async

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
```

## Classes

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
```

## Modules

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
```

## Modern Features (ES2022-2024)

```javascript
// Top-level await (modules)
const config = await loadConfig();

// Array grouping
const grouped = Object.groupBy(items, item => item.category);

// Structured clone
const copy = structuredClone(original);
```

## Error Handling Patterns

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
```
