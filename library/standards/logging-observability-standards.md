# Logging & Observability Standards

## Scope: Structured logging, log levels, metrics, tracing
**Authority:** 12-Factor App, OpenTelemetry, ELK/Grafana best practices  
**Tools:** Pino, Winston, structlog, OpenTelemetry, Prometheus, Grafana  

## Structured Logging

```json
{
  "timestamp": "2024-03-15T10:30:00.000Z",
  "level": "error",
  "message": "Failed to process order",
  "service": "order-service",
  "request_id": "abc-123",
  "user_id": 456,
  "order_id": 789,
  "error": "PaymentDeclined",
  "duration_ms": 1230
}
```

**Rules:**
- JSON format for machine parsing
- Always include: timestamp, level, message, service, request_id
- Add context fields (user_id, order_id) for traceability
- One log entry per event (not multi-line)

## Log Levels

| Level | When | Example |
|-------|------|---------|
| `ERROR` | Action needed, something failed | DB connection lost, payment failed |
| `WARN` | Concerning but handled | Retry succeeded, rate limit approaching |
| `INFO` | Business events, milestones | User registered, order completed |
| `DEBUG` | Developer diagnostics | Query executed, cache hit/miss |
| `TRACE` | Very verbose (rarely in production) | Function entry/exit, full payloads |

**Production default:** `INFO`
**Never log:** passwords, tokens, full credit cards, PII in plain text

## What to Log

| Log | Don't Log |
|-----|-----------|
| Request start/end with duration | Request/response bodies (PII risk) |
| Authentication success/failure | Passwords, tokens, session IDs |
| Authorization failures | Full credit card numbers |
| External service calls + latency | Health check successes (too noisy) |
| Error details + stack trace | Expected/handled errors at ERROR level |
| Business events (order placed) | Every loop iteration |

## Observability Pillars

| Pillar | What | Tool Examples |
|--------|------|---------------|
| **Logs** | Discrete events | ELK, Loki, CloudWatch |
| **Metrics** | Aggregated measurements | Prometheus, Grafana, Datadog |
| **Traces** | Request flow across services | Jaeger, Zipkin, OpenTelemetry |

**Key Metrics to Track:**
- Request rate (req/s)
- Error rate (4xx, 5xx)
- Latency (p50, p95, p99)
- Saturation (CPU, memory, connections)
