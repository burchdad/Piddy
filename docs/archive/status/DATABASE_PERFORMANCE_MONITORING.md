# Database Performance Monitoring

## Overview

Piddy now includes comprehensive database performance analysis capabilities. The autonomous monitoring system can scan the database to identify performance optimization opportunities and generate recommendations.

## Features

### 1. **Database Metrics Analysis**
- **File Size Tracking**: Monitors SQLite database file size in bytes and MB
- **Table Introspection**: Lists all tables in the database
- **Row Count Analysis**: Calculates row counts per table
- **Optimization Detection**: Identifies when optimization is needed based on thresholds

### 2. **Smart Alert Thresholds**
The system monitors database size and provides recommendations:
- **< 100 MB**: Healthy, no action needed
- **100-500 MB**: Warning - Consider optimization strategies
- **500 MB - 1 GB**: Critical - Archive old data or optimize queries
- **> 1 GB**: Urgent - Implement partitioning and archival immediately

### 3. **Optimization Recommendations**
The system generates specific recommendations including:
- Index suggestions for frequently queried columns
- Archive strategies for old data
- Query optimization guidance
- Partitioning strategies for large tables

## API Endpoint

### Get Database Performance Metrics
```bash
GET /api/autonomous/database/performance
```

**Response (Database Not Yet Created):**
```json
{
  "status": "success",
  "database": {
    "status": "not_initialized",
    "message": "Database not created yet"
  },
  "last_check": null
}
```

**Response (Database Active):**
```json
{
  "status": "success",
  "database": {
    "status": "analyzed",
    "database_type": "SQLite",
    "size_bytes": 52428800,
    "size_mb": 50.0,
    "tables": 12,
    "table_list": [
      "users",
      "api_calls",
      "login_events",
      "webhook_logs"
    ],
    "table_statistics": {
      "users": {"rows": 1234},
      "api_calls": {"rows": 892103},
      "login_events": {"rows": 156234},
      "webhook_logs": {"rows": 45678}
    },
    "optimization_needed": false,
    "recommendations": [
      "Consider indexing frequently queried columns if query times exceed 100ms",
      "Archive records older than 90 days to optimize query performance"
    ]
  },
  "last_check": "2024-03-08T14:00:00"
}
```

## Integration with Smart Monitoring

### Daily Monitoring Schedule
The database performance check is automatically included in daily monitoring:
- **Time**: 06:00 UTC daily
- **Includes**: CPU, memory, disk, security, and **database performance**
- **Output**: Integrated into daily performance report

### Sample Daily Report Output
```json
{
  "performance": {
    "cpu_percent": 25.3,
    "memory_percent": 45.1,
    "disk_usage": 62.8,
    "database": {
      "size_mb": 50.0,
      "tables": 12,
      "optimization_needed": false,
      "recommendations": [...]
    },
    "status": "healthy"
  },
  "security": {...},
  "timestamp": "2024-03-08T06:00:00Z"
}
```

### PR Creation for Database Issues
When critical database optimization is needed:
1. Analysis detects database size > thresholds
2. Optimization recommendations are generated
3. Autonomous system creates PR with:
   - Title: `🗄️ Database Optimization: [Specific Recommendation]`
   - Description: Detailed optimization strategy and implementation steps
   - Branch: `database/optimize-[table-name]`
   - Labels: `performance`, `database`, `high-priority`

## Implementation Details

### Code Location
- **Analyzer**: `src/services/autonomous_monitor.py`
  - Method: `_analyze_database_performance()`
  - Lines: ~80+ lines of analysis logic
- **API Endpoint**: `src/api/autonomous.py`
  - Endpoint: `GET /api/autonomous/database/performance`

### Database Introspection Method
The system uses SQLAlchemy ORM for database introspection:

```python
async def _analyze_database_performance(self) -> Dict[str, Any]:
    """Analyze database performance and optimization opportunities."""
    from sqlalchemy import inspect
    from src.database import engine
    
    # Get database file size
    # List all tables using SQLAlchemy inspector
    # Calculate row count per table via COUNT queries
    # Generate recommendations based on thresholds
    # Return comprehensive metrics
```

## Usage Examples

### Check Database Status Now
```bash
# API call
curl http://localhost:8000/api/autonomous/database/performance

# Python code
import requests
response = requests.get("http://localhost:8000/api/autonomous/database/performance")
metrics = response.json()["database"]
```

### Monitor Database Size Over Time
```python
# Collect metrics weekly to track growth
import json
from datetime import datetime

# Call endpoint
metrics = requests.get("http://localhost:8000/api/autonomous/database/performance").json()

# Log the size
log_entry = {
    "timestamp": datetime.now().isoformat(),
    "size_mb": metrics["database"]["size_mb"],
    "tables": metrics["database"]["tables"]
}

with open("database_growth_log.json", "a") as f:
    json.dump(log_entry, f)
    f.write("\n")
```

### Trigger Manual Analysis
```bash
# Run analysis immediately (not on schedule)
curl http://localhost:8000/api/autonomous/monitor/analyze-now
```

## Troubleshooting

### Database Not Found
If the endpoint returns "Database not initialized":
1. This is normal on first startup
2. The database is created when data is first written
3. Check `/workspaces/Piddy/piddy.db` once data is written

### Large Database Detected
If recommendations mention database size issues:
1. Check table sizes with `/api/autonomous/database/performance`
2. Review logs for tables with most rows
3. Archive old data based on retention policy
4. Create indices on frequently queried columns

### Performance Degradation
If queries are slow:
1. Run `/api/autonomous/database/performance` to get metrics
2. Review recommendations for indexing strategies
3. Check for tables with high row counts
4. Monitor database growth over time

## Future Enhancements

Planned improvements to database monitoring:
- [ ] Query performance profiling
- [ ] Index effectiveness analysis
- [ ] Automatic vacuum scheduling
- [ ] Slow query log analysis
- [ ] Connection pool monitoring
- [ ] Transaction duration tracking
- [ ] Replication lag monitoring (if applicable)
- [ ] Backup verification

## Related Documentation

- [Smart Monitoring Strategy](SMART_MONITORING_STRATEGY.md)
- [Autonomous Monitoring](src/services/autonomous_monitor.py)
- [API Reference](API.md)
- [System Architecture](ARCHITECTURE_PHASE32_PHASE33.md)
