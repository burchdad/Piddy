---
name: error-handling
description: Robust error handling strategies — exception hierarchies, retry logic, graceful degradation, and user-friendly error messages
---

# Error Handling Patterns

Build systems that fail gracefully — proper exception handling, retries, fallbacks, and meaningful error messages.

## Exception Hierarchy

### Python

```python
class AppError(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} '{id}' not found", code="NOT_FOUND")

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation failed on '{field}': {message}", code="VALIDATION")

class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="AUTH_REQUIRED")

class RateLimitError(AppError):
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s", code="RATE_LIMIT")
```

### JavaScript/TypeScript

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string = 'UNKNOWN',
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} '${id}' not found`, 'NOT_FOUND', 404);
  }
}

class ValidationError extends AppError {
  constructor(field: string, message: string) {
    super(`Validation failed on '${field}': ${message}`, 'VALIDATION', 422);
  }
}
```

## Error Handling in APIs

### FastAPI Exception Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    status_map = {
        "NOT_FOUND": 404,
        "VALIDATION": 422,
        "AUTH_REQUIRED": 401,
        "FORBIDDEN": 403,
        "RATE_LIMIT": 429,
    }
    return JSONResponse(
        status_code=status_map.get(exc.code, 500),
        content={"error": exc.code, "message": exc.message},
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL", "message": "An unexpected error occurred"},
    )
```

### Error Response Format

```json
{
  "error": "VALIDATION",
  "message": "Validation failed on 'email': invalid email format",
  "details": {
    "field": "email",
    "value": "not-an-email",
    "constraint": "Must be a valid email address"
  }
}
```

## Retry Logic

### Exponential Backoff

```python
import asyncio
import random

async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_errors: tuple = (ConnectionError, TimeoutError),
):
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_errors as e:
            if attempt == max_retries:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}")
```

### What to retry

| Error Type | Retry? | Why |
|------------|--------|-----|
| Network timeout | Yes | Transient issue |
| 429 Rate limited | Yes | Wait and retry |
| 500 Server error | Yes (2-3x) | May be transient |
| 503 Unavailable | Yes | Temporary outage |
| 400 Bad request | No | Input is wrong, won't change |
| 401 Unauthorized | No | Need new credentials |
| 404 Not found | No | Resource doesn't exist |
| 422 Validation | No | Fix the input first |

## Graceful Degradation

### Multi-tier Fallback (Piddy Pattern)

```python
async def get_response(query: str) -> str:
    """Try each tier in order, fall back on failure."""
    tiers = [
        ("local_engine", local_engine.process),
        ("ollama", ollama_client.chat),
        ("anthropic", anthropic_client.complete),
        ("openai", openai_client.complete),
    ]

    for name, handler in tiers:
        try:
            result = await handler(query)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Tier '{name}' failed: {e}")
            continue

    return "All providers unavailable. Please check the Health page."
```

### Feature Flags for Degradation

```python
def get_recommendations(user_id: str):
    try:
        return ml_model.predict(user_id)    # Full personalization
    except ModelUnavailable:
        return get_popular_items()            # Fallback to popular
    except DatabaseError:
        return get_cached_defaults()          # Fallback to cache
```

## Logging Errors

```python
import logging

logger = logging.getLogger(__name__)

# Log levels for different error types
logger.debug("Processing request for user_id=123")          # Debugging detail
logger.info("User 123 logged in successfully")               # Normal events
logger.warning("Slow query detected: 2.3s for /api/users")  # Concerning but not broken
logger.error("Failed to process payment", exc_info=True)     # Broken, needs attention
logger.critical("Database connection pool exhausted")         # System down
```

### What to include in error logs

```python
logger.error(
    "Payment processing failed",
    extra={
        "order_id": order_id,
        "amount": amount,
        "provider": "stripe",
        "error_code": e.code,
        # NEVER log: credit card numbers, passwords, tokens
    },
    exc_info=True,  # Include stack trace
)
```

## Anti-Patterns

1. **Catching everything silently** — `except: pass` hides bugs
2. **Logging and re-raising** — Creates duplicate log entries
3. **Leaking internals** — Don't show stack traces to end users
4. **No context in errors** — "Error occurred" is useless
5. **Retrying non-retryable errors** — 400s won't fix themselves
6. **Nested try/except** — Keep error handling at the right layer
