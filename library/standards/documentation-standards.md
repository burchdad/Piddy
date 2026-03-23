# Documentation Standards

## Scope: README, API docs, inline docs, architecture decision records
**Authority:** Write the Docs, Diátaxis framework, ADR standard  
**Tools:** Markdown, JSDoc/TSDoc, Sphinx, Swagger/OpenAPI, typedoc  

## README Template

```markdown
# Project Name

One-line description of what this project does.

## Quick Start

\`\`\`bash
git clone <url>
npm install
npm run dev
\`\`\`

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
```

## Inline Documentation

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
```

## API Documentation

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
- Keep docs in sync (generate from code when possible)

## Architecture Decision Records

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

Store in `docs/adr/` — one file per decision, numbered sequentially.
