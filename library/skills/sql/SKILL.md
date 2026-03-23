---
name: sql
description: Complete SQL from fundamentals to advanced queries, optimization, window functions, CTEs, and database-specific features
---

# SQL Mastery

## Core SQL
- SELECT: columns, aliases (AS), DISTINCT, expressions
- WHERE: comparison, AND/OR/NOT, IN, BETWEEN, LIKE, IS NULL
- ORDER BY: ASC/DESC, multiple columns, NULLS FIRST/LAST
- LIMIT/OFFSET (MySQL, PostgreSQL, SQLite) vs TOP (SQL Server) vs FETCH FIRST (standard)
- INSERT: single row, multi-row, INSERT INTO...SELECT, RETURNING (PostgreSQL)
- UPDATE: SET, WHERE clause (never update without WHERE), RETURNING
- DELETE: WHERE clause (never delete without WHERE), TRUNCATE for full clear
- UPSERT: INSERT...ON CONFLICT (PostgreSQL), INSERT...ON DUPLICATE KEY (MySQL), MERGE (SQL Server)

## Joins
- INNER JOIN: matching rows in both tables
- LEFT/RIGHT JOIN: all rows from one side + matching from other
- FULL OUTER JOIN: all rows from both sides
- CROSS JOIN: cartesian product (rarely needed)
- Self-join: table joined to itself (hierarchies, comparisons)
- LATERAL JOIN (PostgreSQL): correlated subquery as join

## Aggregation
- GROUP BY: aggregate groups, with HAVING for filtering groups
- Aggregate functions: COUNT, SUM, AVG, MIN, MAX, STRING_AGG, ARRAY_AGG
- GROUP BY ROLLUP, CUBE, GROUPING SETS for subtotals
- FILTER clause (PostgreSQL): COUNT(*) FILTER (WHERE condition)

## Window Functions
- OVER (PARTITION BY ... ORDER BY ...): computation across related rows
- ROW_NUMBER(): sequential numbering within partition
- RANK() / DENSE_RANK(): ranking with/without gaps
- LAG(col, n) / LEAD(col, n): access previous/next rows
- SUM/AVG/COUNT OVER: running totals, moving averages
- FIRST_VALUE / LAST_VALUE / NTH_VALUE
- NTILE(n): distribute rows into n buckets
- Frame specification: ROWS/RANGE BETWEEN ... AND ...

## Common Table Expressions (CTEs)
- WITH clause: named temporary result sets for readability
- Multiple CTEs: WITH a AS (...), b AS (...)
- Recursive CTEs: WITH RECURSIVE for hierarchies, graphs, series generation
- Materialized CTEs (PostgreSQL): WITH ... AS MATERIALIZED

## Subqueries
- Scalar subqueries: single value in SELECT or WHERE
- EXISTS / NOT EXISTS: correlated existence checks
- IN (subquery) vs JOIN — prefer JOIN for performance
- Derived tables: subquery in FROM clause

## Indexing and Optimization
- B-tree indexes: default, good for equality and range queries
- Covering indexes: INCLUDE columns (avoid table lookup)
- Partial indexes: WHERE clause, index only relevant rows
- Expression indexes: CREATE INDEX ON table (LOWER(column))
- Composite indexes: leftmost prefix rule, column order matters
- EXPLAIN ANALYZE: read execution plans, spot sequential scans
- Index-only scans: covering indexes avoid heap fetches
- Query optimization: avoid SELECT *, use appropriate joins, limit result sets

## PostgreSQL-Specific
- JSONB: ->, ->>, @>, jsonb_array_elements, GIN indexes
- Arrays: ARRAY[1,2,3], ANY/ALL, unnest, array_agg
- Full-text search: tsvector, tsquery, to_tsvector, GIN index
- Range types: int4range, tsrange, containment operators
- GENERATED columns: STORED computed columns
- Partitioning: RANGE, LIST, HASH partitioning
- PL/pgSQL: functions, procedures, triggers

## MySQL-Specific
- AUTO_INCREMENT for primary keys
- JSON: JSON_EXTRACT, ->, ->>, JSON_TABLE
- Character sets: utf8mb4 (always use this, not utf8)
- InnoDB: default engine, transactions, row-level locking
- Generated columns: STORED and VIRTUAL

## SQLite-Specific
- Single file database, no server
- Dynamic typing (type affinity)
- JSON1 extension: json_extract, json_each
- WAL mode for concurrent read performance
- Strict tables (SQLite 3.37+): optional strict typing

## Transactions
- BEGIN, COMMIT, ROLLBACK
- SAVEPOINT for nested transaction points
- Isolation levels: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE
- Deadlock prevention: consistent lock ordering
- Advisory locks (PostgreSQL) for application-level coordination

## Best Practices
- Always use parameterized queries — never concatenate user input
- Use appropriate data types: don't store dates as strings
- Add indexes for columns used in WHERE, JOIN, ORDER BY
- Normalize to 3NF by default, denormalize intentionally for performance
- Use foreign keys for referential integrity
- Write idempotent migrations
- Test queries with EXPLAIN before deploying
