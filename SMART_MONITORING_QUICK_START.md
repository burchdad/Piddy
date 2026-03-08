# Smart Monitoring Quick Start

## Status Check

```bash
# Check if monitoring is running
curl -X GET http://localhost:8000/api/autonomous/status | jq .

# Expected output:
# {
#   "monitor": {
#     "enabled": false,
#     "strategy": "smart",
#     "last_daily_check": null,
#     "last_weekly_check": null,
#     ...
#   },
#   "schedule": {
#     "daily": "06:00 UTC - Performance & Security checks",
#     "weekly": "Sundays 02:00 UTC - Code Quality analysis",
#     "hourly": "⛔ DISABLED (redundant)"
#   }
# }
```

## Enable Smart Monitoring

```bash
# Start with smart strategy (RECOMMENDED)
curl -X POST http://localhost:8000/api/autonomous/monitor/start?strategy=smart

# Response:
# {
#   "status": "smart_monitoring_started",
#   "schedule": {
#     "daily": "06:00 UTC - Performance & Security checks",
#     "weekly": "Sundays 02:00 UTC - Code Quality analysis"
#   }
# }
```

## Run Immediate Analysis

```bash
# Run code analysis NOW (for testing/verification)
curl -X GET http://localhost:8000/api/autonomous/monitor/analyze-now | jq .

# Run performance/security check NOW
curl -X POST http://localhost:8000/api/autonomous/analyze/performance-security
```

## Stop Monitoring

```bash
curl -X POST http://localhost:8000/api/autonomous/monitor/stop

# Response:
# { "status": "monitoring_stopped" }
```

## Get Created PRs

```bash
# List all PRs created by autonomous system
curl -X GET http://localhost:8000/api/autonomous/prs/created | jq .
```

## How It Works

### Daily Run (06:00 UTC)
1. **Performance Analysis**
   - Response time monitoring
   - Memory/CPU usage
   - Database query performance
   - Cache efficiency

2. **Security Scan**
   - Dependency vulnerabilities (pip check)
   - Error rate tracking
   - Authentication events
   - Authorization violations

### Weekly Run (Sundays 02:00 UTC)
1. **Code Quality Review**
   - Print statement verification
   - Exception handling audit
   - TODO/FIXME tracking
   - Code metrics

2. **Architecture Health**
   - Circular dependency detection
   - Service boundary validation
   - Module coupling analysis

### Benefits vs Hourly Scanning
| Metric | Hourly (Old) | Smart (New) |
|--------|------|------|
| Scans per day | 24 | 1-2 |
| False positives | High | Low |
| Noise | Constant | Focused |
| Infrastructure load | Heavy | Light |
| Issue priority | Mixed | Strategic |

## Manual Triggers

### Force Daily Check
```python
import asyncio
from src.services.autonomous_monitor import get_autonomous_monitor

monitor = get_autonomous_monitor()
asyncio.run(monitor.analyze_performance_and_security())
```

### Force Weekly Check
```python
import asyncio
from src.services.autonomous_monitor import get_autonomous_monitor

monitor = get_autonomous_monitor()
asyncio.run(monitor.analyze_code_quality())
```

## Documentation
- [SMART_MONITORING_STRATEGY.md](SMART_MONITORING_STRATEGY.md) - Detailed strategy guide
- [comprehensive_cleanup.py](comprehensive_cleanup.py) - Cleanup script reference
- [src/services/autonomous_monitor.py](src/services/autonomous_monitor.py) - Implementation
- [src/api/autonomous.py](src/api/autonomous.py) - API endpoints

## Troubleshooting

**Q: Monitoring doesn't start?**
- A: Check that the server is running and `/api/autonomous/status` returns a response

**Q: Want to disable monitoring?**
- A: `curl -X POST http://localhost:8000/api/autonomous/monitor/stop`

**Q: Go back to hourly monitoring?**
- A: Use `strategy=hourly` (not recommended due to redundancy)

**Q: Tests failing?**
- A: Run full code quality check: `curl -X GET http://localhost:8000/api/autonomous/monitor/analyze-now`
