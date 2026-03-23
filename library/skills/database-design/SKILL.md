---
name: database-design
description: Design schemas, write efficient queries, manage migrations, and optimize database performance for SQLite and PostgreSQL
---

# Database Design & Optimization

## Schema Design Principles

- Normalize to 3NF unless performance requires denormalization
- Use appropriate data types (don't store numbers as strings)
- Add indexes for frequently queried columns
- Use foreign keys for referential integrity
- Include `created_at` / `updated_at` timestamps on every table
- Use `NOT NULL` by default — only allow NULL when absence is meaningful

## SQLite Patterns (Piddy Default)

```sql
-- Enable WAL mode for better concurrent read performance
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active', 'suspended', 'deleted')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,  -- UUID as text in SQLite
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'Untitled',
    message_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC);
```

### SQLite-Specific Tips

- Use `TEXT` for UUIDs and dates (no native UUID/datetime types)
- `INTEGER PRIMARY KEY` = implicit rowid alias (fastest lookups)
- WAL mode allows concurrent readers with one writer
- Transactions are critical — batch inserts are 10-100x faster in a transaction
- Use `UPSERT` via `INSERT ... ON CONFLICT DO UPDATE`

## PostgreSQL Patterns

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    total_cents INTEGER NOT NULL CHECK(total_cents >= 0),
    items JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial index: only index rows that matter
CREATE INDEX idx_orders_active ON orders(customer_id)
    WHERE status NOT IN ('delivered', 'cancelled');

-- GIN index for JSONB queries
CREATE INDEX idx_orders_items ON orders USING GIN (items);
```

## Index Strategy

**When to add indexes:**
- Columns in WHERE clauses (frequent filters)
- Columns in JOIN conditions (foreign keys)
- Columns in ORDER BY (avoid filesort)
- Columns in GROUP BY

**When NOT to index:**
- Tables with < 1000 rows (full scan is faster)
- Columns with very low cardinality (boolean flags)
- Write-heavy tables where read speed isn't critical

**Composite indexes:**
```sql
-- Covers queries filtering by user_id AND/OR status
-- Also covers queries filtering by user_id alone
-- Does NOT cover queries filtering by status alone
CREATE INDEX idx_sessions_user_status ON sessions(user_id, status);
```

## Migration Strategy

```
migrations/
├── 001_initial_schema.sql
├── 002_add_users_table.sql
├── 003_add_session_title.sql
└── 004_add_message_index.sql
```

Each migration file:
```sql
-- 003_add_session_title.sql
-- UP
ALTER TABLE sessions ADD COLUMN title TEXT NOT NULL DEFAULT 'Untitled';

-- DOWN
ALTER TABLE sessions DROP COLUMN title;
```

**Rules:**
- Migrations are append-only — never edit a deployed migration
- Always include both UP and DOWN
- Test on a copy before applying to production
- Back up before any schema change
- Use transactions for multi-statement migrations

## Query Optimization

```sql
-- Use EXPLAIN to analyze query plans
EXPLAIN QUERY PLAN
SELECT s.id, s.title, COUNT(m.id) as msg_count
FROM sessions s
LEFT JOIN messages m ON m.session_id = s.id
WHERE s.user_id = ?
GROUP BY s.id
ORDER BY s.created_at DESC
LIMIT 20;
```

**Common optimizations:**
- Avoid `SELECT *` — specify columns
- Use parameterized queries (prevent SQL injection, enable plan caching)
- Batch inserts in transactions
- Use `EXISTS` instead of `IN` for subqueries with large result sets
- Paginate with `LIMIT/OFFSET` or keyset pagination for large datasets

### Keyset Pagination (faster than OFFSET for deep pages)

```sql
-- Instead of: SELECT ... LIMIT 20 OFFSET 10000
-- Use cursor-based:
SELECT id, title, created_at
FROM sessions
WHERE created_at < ?  -- cursor from last page's last row
ORDER BY created_at DESC
LIMIT 20;
```

## SQLAlchemy ORM Patterns

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="Untitled")
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="sessions")
```

## Anti-Patterns to Avoid

1. **God table** — one table with 50+ columns → split into related tables
2. **EAV (Entity-Attribute-Value)** — use JSONB if you need flexibility
3. **No foreign keys** — "we'll enforce it in the app" → data WILL become inconsistent
4. **N+1 queries** — use JOINs or eager loading, not loops of single queries
5. **Storing money as floats** — use integer cents or DECIMAL types
