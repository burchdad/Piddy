---
name: architecture-patterns
description: Software architecture patterns including microservices, monolith, event-driven, and system design principles
---

# Architecture Patterns

Choose and implement the right architecture for the problem at hand.

## Monolith (Start Here)

Best for: most projects, especially early stage.

```
app/
├── api/           # HTTP handlers
├── services/      # Business logic
├── models/        # Data models
├── repositories/  # Data access
└── main.py        # Entry point
```

**When monolith is right:**
- Team < 10 developers
- Domain not yet well understood
- Need to ship fast and iterate
- Single deployment target

**Monolith rules:**
- Keep modules loosely coupled internally
- Use clear boundaries (services don't call other services' repositories)
- Extract microservices ONLY when a specific pain point demands it

## Microservices

Best for: large teams, independently deployable features, different scaling needs.

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  API GW   │───▶│  Users   │    │  Orders  │
└──────────┘    └──────────┘    └──────────┘
                      │               │
                 ┌────▼────┐    ┌────▼────┐
                 │ Users DB │    │Orders DB │
                 └─────────┘    └─────────┘
```

**Key principles:**
- Each service owns its data (no shared databases)
- Communicate via APIs or events, never direct DB access
- Independently deployable
- Failure isolation — one service down doesn't take everything down

**Common pitfalls:**
- Distributed monolith (tight coupling via synchronous calls)
- Shared database (defeats the purpose)
- Too many services too early (operational overhead)

## Event-Driven Architecture

Best for: decoupled systems, async workflows, audit trails.

```
Producer → Event Bus → Consumer(s)

Order Service ──▶ [order.created] ──▶ Payment Service
                                  ──▶ Notification Service
                                  ──▶ Inventory Service
```

**Event design:**
```json
{
  "event_type": "order.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "order_id": "ord_123",
    "customer_id": "cust_456",
    "total": 99.99
  }
}
```

**Patterns:**
- **Event Sourcing**: Store events as source of truth, derive state
- **CQRS**: Separate read and write models
- **Saga**: Coordinate multi-service transactions via events

## Layered Architecture

Standard separation of concerns:

```
┌─────────────────────┐
│   Presentation      │  ← HTTP handlers, CLI, WebSocket
├─────────────────────┤
│   Application       │  ← Use cases, orchestration
├─────────────────────┤
│   Domain            │  ← Business logic, entities, rules
├─────────────────────┤
│   Infrastructure    │  ← Database, external APIs, file I/O
└─────────────────────┘
```

**Rule**: Dependencies point DOWN only. Domain never imports from Infrastructure.

## Repository Pattern

Abstracts data access behind a clean interface:

```python
class UserRepository:
    def get_by_id(self, user_id: str) -> User | None: ...
    def save(self, user: User) -> None: ...
    def find_by_email(self, email: str) -> User | None: ...

class SqlUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, user_id: str) -> User | None:
        return self._session.get(User, user_id)
```

## API Gateway Pattern

Single entry point for multiple backend services:

```
Client ──▶ API Gateway ──▶ Auth Service
                       ──▶ User Service
                       ──▶ Order Service
```

Handles: routing, auth, rate limiting, request aggregation, protocol translation.

## Circuit Breaker

Prevent cascading failures when calling external services:

```python
# States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing)
# CLOSED: requests pass through, failures counted
# OPEN: requests fail immediately, no calls made
# HALF_OPEN: allow one test request to check recovery
```

**Thresholds:**
- Open after 5 consecutive failures
- Stay open for 30 seconds
- Half-open allows 1 probe request
- Success in half-open → close; failure → re-open

## Choosing an Architecture

| Factor | Monolith | Microservices | Event-Driven |
|--------|----------|---------------|--------------|
| Team size | 1-10 | 10+ | Any |
| Deploy frequency | Weekly | Daily per service | Event-triggered |
| Data consistency | Strong (ACID) | Eventual | Eventual |
| Complexity | Low | High | Medium-High |
| Latency | Low | Higher (network) | Async |
| Best for | MVPs, most apps | Large orgs | Workflows, auditing |

## Design Principles

1. **YAGNI** — Don't build for hypothetical future needs
2. **Start simple** — Monolith → extract services when pain is real
3. **Loose coupling** — Services know interfaces, not implementations
4. **High cohesion** — Related logic lives together
5. **Fail gracefully** — Timeouts, retries, circuit breakers, fallbacks
6. **Observe everything** — Logs, metrics, traces from day one
