---
name: debugging
description: Systematic debugging strategies for tracking down and fixing bugs
---

# Debugging

## Systematic Approach
1. **Reproduce** — Get a consistent repro case (exact input, steps, environment)
2. **Isolate** — Narrow down: which file, function, line?
3. **Hypothesize** — Form a theory about root cause
4. **Test** — Verify hypothesis with a targeted experiment
5. **Fix** — Make the minimal change to correct the issue
6. **Verify** — Confirm the fix works AND doesn't break other things

## Common Root Causes by Error Type

### "It doesn't work" (no error message)
- Check the data flow: is the right data reaching the right place?
- Add logging at each boundary (API call, function entry/exit, state change)
- Compare expected vs actual at each step

### TypeError / AttributeError / KeyError
- Check the shape of incoming data (API response, config, user input)
- Look for null/undefined propagation from upstream
- Check for typos in property names

### "Works locally, fails in production"
- Environment variables missing or different
- File paths (relative vs absolute, OS-specific separators)
- Network/firewall differences
- Different dependency versions

### "Works sometimes, fails sometimes" (flaky)
- Race condition (async operations finishing in different order)
- Shared mutable state
- External dependency intermittent (network, disk, API rate limit)
- Time-dependent logic (timezone, day-of-week, DST)

## Logging Strategy
```python
import logging
logger = logging.getLogger(__name__)

# Log at boundaries
logger.info("Processing request: %s", request_id)
logger.debug("Input data: %s", sanitize(data))
logger.error("Failed to process: %s", error, exc_info=True)
```

- **DEBUG** — Internal state, variable values, flow tracing
- **INFO** — Business events (request received, job completed)
- **WARNING** — Recoverable problems (retry, fallback used)
- **ERROR** — Failures that need attention (with stack trace)

## When Stuck
- Read the FULL error message (stack trace, not just the last line)
- Check if the error is in YOUR code or a DEPENDENCY
- Simplify: strip down to the minimum code that still fails
- Check recent changes: what changed since it last worked?
- Sleep on it — fresh eyes find bugs faster
