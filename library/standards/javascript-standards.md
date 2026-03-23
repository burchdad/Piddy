# JavaScript Coding Standards

## Scope: ES2024+ conventions, module patterns, async best practices
**Authority:** Airbnb Style Guide, StandardJS, ESLint recommended  
**Tools:** ESLint, Prettier, Biome  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Variable / Function | `camelCase` | `getUserById` |
| Class / Component | `PascalCase` | `UserService` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| File (module) | `camelCase` or `kebab-case` | `userService.js` |
| Private (convention) | `#prefix` (class) or `_prefix` | `#cache`, `_internal` |
| Boolean variable | `is/has/can/should` prefix | `isActive`, `hasPermission` |
| Event handler | `handle` + event | `handleClick`, `handleSubmit` |

## Variable Declaration

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
```

## Functions

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
```

## Module Patterns

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
```

## Equality & Comparisons

```javascript
// ALWAYS use === and !== (strict equality)
if (value === null) { }
if (typeof x === 'string') { }

// Use optional chaining for safe access
const city = user?.address?.city;

// Use nullish coalescing for defaults (not ||)
const port = config.port ?? 3000;   // only null/undefined
// Avoid: config.port || 3000       // also catches 0, ""
```

## Anti-Patterns to Avoid

| Anti-Pattern | Better |
|-------------|--------|
| `var` declarations | `const` / `let` |
| `==` loose equality | `===` strict equality |
| Callback hell | `async/await` |
| `for...in` on arrays | `for...of`, `.map()`, `.forEach()` |
| Modifying function arguments | Clone first: `{...args}` |
| `new Array(5)` | `Array.from({length: 5})` |
| Silent catch `catch(e) {}` | Log and re-throw or handle meaningfully |
| `arguments` object | Rest parameters `...args` |
