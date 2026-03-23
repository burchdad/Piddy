# SQL Coding Standards

## Scope: Naming, query patterns, schema design, performance
**Authority:** SQL Style Guide (Simon Holywell), Postgres conventions  
**Applies To:** PostgreSQL, MySQL, SQLite, SQL Server  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Table | `snake_case`, plural | `users`, `order_items` |
| Column | `snake_case` | `first_name`, `created_at` |
| Primary key | `id` | `users.id` |
| Foreign key | `singular_table_id` | `user_id`, `order_id` |
| Index | `idx_table_columns` | `idx_users_email` |
| Boolean column | `is_/has_` prefix | `is_active`, `has_verified` |
| Timestamp | `_at` suffix | `created_at`, `updated_at` |
| Enum-like | explicit values, not magic numbers | Use lookup table or CHECK |

## Query Formatting

```sql
-- Keywords: UPPERCASE
-- Identifiers: lowercase snake_case
-- One clause per line
-- Indent subqueries and conditions

SELECT
    u.id,
    u.name,
    u.email,
    COUNT(o.id) AS order_count
FROM users u
INNER JOIN orders o
    ON o.user_id = u.id
WHERE u.is_active = true
    AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC
LIMIT 20;
```

## Schema Design Rules

| Rule | Details |
|------|---------|
| Always have a primary key | Prefer `BIGINT GENERATED ALWAYS AS IDENTITY` |
| Add `created_at` / `updated_at` | Use `TIMESTAMPTZ DEFAULT NOW()` |
| Foreign keys always | Enforce referential integrity |
| Index foreign keys | JOINs use them constantly |
| Avoid `NULL` when possible | Use `NOT NULL` + sensible defaults |
| Normalize first, denormalize for performance | Don't premature optimize |
| Use migrations | Never modify schema by hand in production |

## Performance Anti-Patterns

| Anti-Pattern | Better |
|-------------|--------|
| `SELECT *` | List only needed columns |
| No index on WHERE/JOIN cols | Add indexes |
| N+1 queries from app code | Use JOINs or batch queries |
| Implicit type conversion | Match types in comparisons |
| Functions in WHERE clause | Compute upfront or use expression index |
| Missing LIMIT on unbounded queries | Always paginate |
| `COUNT(*)` to check existence | Use `EXISTS(SELECT 1 ...)` |
