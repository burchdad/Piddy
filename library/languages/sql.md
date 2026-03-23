# SQL Quick Reference

## Language: SQL (ISO/ANSI SQL:2023)
**Paradigm:** Declarative, set-based  
**Dialects:** PostgreSQL, MySQL, SQLite, SQL Server, Oracle  
**Purpose:** Database query, manipulation, and definition  

## Query Fundamentals

```sql
SELECT u.name, u.email, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.active = true
  AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC
LIMIT 20 OFFSET 0;
```

## Joins

```sql
-- INNER JOIN (matching rows only)
SELECT * FROM users u INNER JOIN orders o ON o.user_id = u.id;

-- LEFT JOIN (all from left, matching from right)
SELECT u.name, o.total FROM users u LEFT JOIN orders o ON o.user_id = u.id;

-- Self join
SELECT e.name AS employee, m.name AS manager
FROM employees e LEFT JOIN employees m ON e.manager_id = m.id;
```

## Window Functions

```sql
SELECT name, score,
    ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num,
    RANK() OVER (ORDER BY score DESC) AS rank
FROM students;

-- Running total
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM transactions;

-- LAG / LEAD
SELECT date, revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS change
FROM daily_sales;
```

## CTEs & Recursive Queries

```sql
WITH active_users AS (
    SELECT * FROM users WHERE active = true
)
SELECT au.name FROM active_users au;

-- Recursive CTE (hierarchy)
WITH RECURSIVE tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, t.depth + 1
    FROM categories c INNER JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth, name;
```

## Schema Definition

```sql
CREATE TABLE users (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    role        VARCHAR(50) DEFAULT 'user',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    metadata    JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users (email);
```

## Performance Tips

| Pattern | Advice |
|---------|--------|
| `SELECT *` | List only needed columns |
| Missing index | Add indexes on WHERE/JOIN/ORDER BY columns |
| N+1 queries | Use JOINs or batch queries |
| `COUNT(*)` vs `EXISTS` | Use `EXISTS` for existence checks |
