---
name: code-review
description: Perform thorough code reviews checking quality, bugs, performance, and security
---

# Code Review

## Review Checklist (Priority Order)
1. **Correctness** — Does it do what it's supposed to?
2. **Security** — Any injection, XSS, auth bypass, data exposure?
3. **Error handling** — Edge cases, null/undefined, network failures?
4. **Performance** — N+1 queries, unnecessary re-renders, memory leaks?
5. **Readability** — Can someone else understand this in 6 months?
6. **Tests** — Are the important paths covered?

## Common Bug Patterns
- Off-by-one errors in loops and slicing
- Race conditions in async code (missing await)
- Mutations of shared state (objects passed by reference)
- String comparison when numeric comparison is needed
- Forgotten cleanup (event listeners, intervals, connections)
- Truthy/falsy confusion (0, "", null, undefined, NaN are all falsy)

## Code Smells to Flag
- Functions > 50 lines — suggest extraction
- Deeply nested conditionals (> 3 levels) — suggest early returns/guard clauses
- Magic numbers/strings — suggest named constants
- Copy-pasted code blocks — suggest shared utility
- Boolean parameters — suggest separate methods or options object
- Commented-out code — suggest removal (git has history)

## Refactoring Strategies
- **Extract method** — Long function → smaller named functions
- **Guard clauses** — Replace nested if/else with early returns
- **Strategy pattern** — Replace switch/if chains with a map of handlers
- **Compose** — Replace inheritance with composition
- **Null object** — Replace null checks with default objects

## Review Response Format
When reviewing code, respond with:
1. Summary: one-line assessment (LGTM / needs changes / major issues)
2. Critical issues (must fix before merge)
3. Suggestions (improvements, not blockers)
4. Positive callouts (what's done well)
