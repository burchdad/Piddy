---
name: documentation
description: Write clear READMEs, API docs, docstrings, and technical documentation
---

# Documentation

Write documentation that developers actually read — clear, concise, and well-structured.

## README Template

```markdown
# Project Name

One-line description of what this does.

## Quick Start

\```bash
git clone <repo>
cd project
pip install -e ".[dev]"
python -m project
\```

## Features

- Feature A — brief description
- Feature B — brief description

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## API Reference

See [API.md](API.md) for endpoints.

## Development

\```bash
pytest                    # Run tests
ruff check src/           # Lint
ruff format src/          # Format
\```

## License

MIT
```

## Python Docstrings (Google Style)

```python
def process_order(order_id: str, *, validate: bool = True) -> OrderResult:
    """Process a customer order and return the result.

    Validates the order, charges payment, and queues fulfillment.
    Skips validation if the order was pre-validated upstream.

    Args:
        order_id: The unique order identifier.
        validate: Whether to run validation checks. Defaults to True.

    Returns:
        OrderResult with status, tracking_id, and estimated_delivery.

    Raises:
        OrderNotFoundError: If order_id doesn't exist.
        PaymentFailedError: If payment processing fails.
    """
```

### When to write docstrings

- **Always**: Public functions, classes, modules
- **Skip**: Private helpers where name + types tell the story
- **Rule**: If someone unfamiliar with the code would need context, add a docstring

## TypeScript JSDoc

```typescript
/**
 * Fetches paginated user data from the API.
 *
 * @param page - The page number (1-indexed)
 * @param limit - Results per page (max 100)
 * @returns Paginated user list with total count
 * @throws {ApiError} When the request fails
 *
 * @example
 * const users = await getUsers(1, 25);
 * console.log(users.total); // 142
 */
async function getUsers(page: number, limit: number): Promise<PaginatedUsers> {
```

## API Documentation

### Endpoint format

```markdown
### POST /api/orders

Create a new order.

**Request Body:**
\```json
{
  "items": [{"product_id": "abc", "quantity": 2}],
  "shipping_address": "123 Main St"
}
\```

**Response 201:**
\```json
{
  "order_id": "ord_123",
  "status": "processing",
  "total": 49.98
}
\```

**Errors:**
- `400` — Invalid request body
- `409` — Duplicate order
- `422` — Out of stock
```

## Inline Comments

### Good comments explain WHY, not WHAT

```python
# Bad — restates the code
x = x + 1  # increment x

# Good — explains business logic
x = x + 1  # Account for the header row in CSV exports

# Good — explains non-obvious constraint
timeout = 30  # Must exceed the SLA response window (25s)
```

## Changelog Format (Keep a Changelog)

```markdown
## [1.2.0] - 2024-01-15

### Added
- Bulk import endpoint for CSV uploads
- Rate limiting on public API routes

### Changed
- Upgraded SQLAlchemy from 1.4 to 2.0

### Fixed
- Session timeout not resetting on activity
```

## Architecture Decision Records (ADRs)

```markdown
# ADR-003: Use SQLite for Local Storage

## Status: Accepted

## Context
Need a local database for the portable desktop app. Must work
without installation and support concurrent reads.

## Decision
Use SQLite with WAL mode. Single file, zero config, ships
with Python stdlib.

## Consequences
- (+) No database server to install or manage
- (+) Database is a single portable file
- (-) Write concurrency limited to one writer
- (-) No built-in replication
```

## Documentation Principles

1. **Start with the user's goal** — not your architecture
2. **Show, don't tell** — code examples > prose explanations
3. **Keep it current** — outdated docs are worse than no docs
4. **Layer detail** — README → guides → API reference → code comments
5. **Test your examples** — broken code samples destroy trust
