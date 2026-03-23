---
name: performance-optimization
description: Profile, measure, and optimize application performance across stack
---

# Performance Optimization

## Golden Rules
1. **Measure first** — Never optimize without profiling data
2. **Optimize the bottleneck** — 90% of time is in 10% of code
3. **Set a target** — "< 200ms response time" is better than "make it fast"
4. **Benchmark before/after** — Prove the optimization actually helped

## Backend Optimization

### Database (Usually the #1 bottleneck)
- Add indexes for WHERE, JOIN, ORDER BY columns
- Use `EXPLAIN ANALYZE` to find slow queries
- Avoid N+1 queries — use JOINs or batch loading
- Connection pooling (don't open a new connection per request)
- Cache frequent queries (Redis, in-memory)

### Python Specific
```python
# Profile with cProfile
import cProfile
cProfile.run('my_function()', sort='cumulative')

# Measure with time
import time
start = time.perf_counter()
result = heavy_operation()
elapsed = time.perf_counter() - start
print(f"Took {elapsed:.3f}s")
```
- Use `async/await` for I/O-bound work
- Use generators for large data processing
- Use `lru_cache` for pure function memoization
- Profile memory with `tracemalloc`

### Caching Strategy
```
[Client] → [CDN cache] → [API Gateway] → [App cache] → [DB cache] → [DB]
```
- Cache at the layer closest to the user
- Set TTL based on data freshness requirements
- Invalidate on write (cache-aside pattern)
- Use cache keys that include relevant parameters

## Frontend Optimization
- Lazy load routes and heavy components
- Compress images (WebP, responsive srcset)
- Minimize bundle size (tree-shaking, code splitting)
- Debounce search/filter inputs
- Virtualize long lists (only render visible items)
- Use `loading="lazy"` on images below the fold

## Measuring Performance
- **TTFB** (Time to First Byte) — Server response time
- **FCP** (First Contentful Paint) — When user sees something
- **LCP** (Largest Contentful Paint) — When main content loads
- **P95/P99 latency** — Worst-case response times (not just average)
