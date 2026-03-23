# Piddy Dashboard System Integration Guide

This document provides comprehensive guidance for integrating the Piddy Dashboard with the Piddy autonomous system.

## Architecture Overview

The Piddy Dashboard is a three-tier architecture:

```
┌─────────────────────────────────────────────────────┐
│  Browser (React Frontend Dashboard)                 │
│  ├─ Real-time data fetching                         │
│  ├─ WebSocket subscriptions                         │
│  └─ Component rendering                             │
└────────────────┬────────────────────────────────────┘
                 │ REST + WebSocket
┌────────────────▼────────────────────────────────────┐
│  FastAPI Backend (Dashboard API)                    │
│  ├─ REST endpoints (/api/*)                         │
│  ├─ WebSocket streams (/ws/*)                       │
│  ├─ Mock data generator (for testing)               │
│  └─ Piddy integration hooks                         │
└────────────────┬────────────────────────────────────┘
                 │ Python imports + hooks
┌────────────────▼────────────────────────────────────┐
│  Piddy Core System                                  │
│  ├─ Agent management                                │
│  ├─ Message bus                                     │
│  ├─ Phase orchestration                             │
│  ├─ Logging system                                  │
│  ├─ Test framework                                  │
│  ├─ Metrics collection                              │
│  └─ Security/Compliance                             │
└─────────────────────────────────────────────────────┘
```

## Getting Started

### 1. Prerequisites

```bash
# Check your environment
python --version  # 3.8+
node --version   # 16+
npm --version    # 8+
```

### 2. Backend Setup

```bash
# 1. Start the Piddy backend (if not running)
cd /path/to/piddy
python src/main.py

# 2. Verify Piddy is running
curl http://127.0.0.1:8000/api/health
# Should return: {"status": "healthy"}

# 3. In another terminal, start the dashboard API
cd /workspaces/Piddy
python src/dashboard_api.py

# The dashboard API will:
# - Start on http://127.0.0.1:8000
# - Automatically connect to Piddy core
# - Begin collecting real-time data
```

### 3. Frontend Setup

```bash
# 1. Install dependencies
cd /workspaces/Piddy/frontend
npm install

# 2. Start development server
npm run dev

# 3. Dashboard opens at http://localhost:3000
```

## Integration Points

### Data Flow: System → Dashboard

The dashboard pulls data from Piddy through the API:

#### Agent Data
```python
# From Piddy agent manager to dashboard
GET /api/agents → Agent.__dict__ with:
  - agent_id
  - role
  - status (online/offline)
  - reputation_score
  - decisions_made
  - success_rate
  - messages_pending
```

#### Log Data
```python
# From Piddy logging system to dashboard
GET /api/logs → List of:
  - level (INFO, WARNING, ERROR, DEBUG)
  - source (module name)
  - message
  - timestamp
  - context (JSON)

# Real-time streaming via WebSocket
WS /ws/logs → Stream of log entries as generated
```

#### Message Data
```python
# From Piddy message bus to dashboard
GET /api/messages → List of:
  - message_id
  - from_agent_id
  - to_agent_id
  - message_type (proposal, vote, execute, report, query, alert)
  - content
  - priority (1-10)
  - timestamp

# Real-time streaming via WebSocket
WS /ws/messages → Stream of messages as exchanged
```

#### Test Data
```python
# From Piddy test framework to dashboard
GET /api/tests → List of:
  - test_name
  - test_path
  - status (passed/failed/skipped)
  - duration_seconds
  - error_message (if failed)
  - timestamp

GET /api/tests/summary → Aggregate statistics:
  - total_tests
  - passed_count
  - failed_count
  - skipped_count
  - pass_rate
```

#### Metrics Data
```python
# From Piddy monitoring to dashboard
GET /api/metrics/performance → List of:
  - metric_name
  - current_value
  - unit
  - threshold
  - status (ok/warning/critical)

GET /api/analytics/agent-reputation → List of:
  - agent_id
  - reputation_score (0.5-2.0)
  - success_rate (0-100%)
```

#### Phase Data
```python
# From Piddy phase manager to dashboard
GET /api/phases → List of:
  - phase_id
  - phase_name
  - status (pending, in_progress, completed, failed)
  - start_time
  - end_time
  - progress_percent
  - error_message (if failed)
```

#### Security Data
```python
# From Piddy security/compliance module
GET /api/security/audit → Audit result:
  - audit_id
  - timestamp
  - is_production_safe (boolean)
  - passed_checks (count)
  - failed_checks (count)

GET /api/security/issues → Issues list:
  - critical_failures (array of strings)
  - warnings (array)
  - recommendations (array)
```

## Implementation: Connecting Dashboard to Piddy

### Step 1: Update Dashboard API to Import Piddy

In `src/dashboard_api.py`:

```python
# Add Piddy imports
from src.agent.core import AgentManager
from src.models.dashboard import *
from src.service.logging import SystemLogger
from src.observability.metrics import MetricsCollector

class PiddyDataBridge:
    """Bridge between Piddy core and Dashboard API"""
    
    def __init__(self):
        # Connect to running Piddy instance
        self.agent_manager = AgentManager()
        self.logger = SystemLogger()
        self.metrics = MetricsCollector()
    
    async def get_agents(self):
        """Fetch live agent data from Piddy"""
        agents = self.agent_manager.list_agents()
        return [AgentStatus.from_piddy_agent(a) for a in agents]
    
    async def get_logs(self, limit=100):
        """Fetch logs from Piddy logging system"""
        return self.logger.get_recent_logs(limit)
    
    async def get_messages(self, limit=100):
        """Fetch messages from Piddy message bus"""
        return self.agent_manager.get_recent_messages(limit)
    
    # ... similar methods for tests, phases, metrics, security
```

### Step 2: Replace Mock Data with Live Data

In endpoint implementations, replace:

```python
# Before (mock data):
@app.get("/api/agents")
async def get_agents():
    return MockDataGenerator.generate_agents()

# After (live data):
@app.get("/api/agents")
async def get_agents():
    return await bridge.get_agents()
```

### Step 3: Implement WebSocket Real-Time Streams

```python
# In dashboard_api.py
@app.websocket("/ws/logs")
async def ws_logs(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to Piddy log stream
    log_stream = self.logger.subscribe_to_logs()
    
    async for log_entry in log_stream:
        await websocket.send_json(log_entry.dict())

@app.websocket("/ws/messages")
async def ws_messages(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to Piddy message stream
    msg_stream = self.agent_manager.subscribe_to_messages()
    
    async for message in msg_stream:
        await websocket.send_json(message.dict())
```

### Step 4: Configure Environment

Create `.env` in frontend:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
VITE_ENABLE_WEBSOCKETS=true
```

## Running the Full Stack

### Manual Startup

```bash
# Terminal 1: Piddy Core
cd /workspaces/Piddy
python src/main.py

# Terminal 2: Dashboard API
cd /workspaces/Piddy
python src/dashboard_api.py

# Terminal 3: Dashboard Frontend
cd /workspaces/Piddy/frontend
npm run dev
```

### Automated Startup Script

Create `start-dashboard.sh`:

```bash
#!/bin/bash

# Check if services are running
check_piddy_api() {
    curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1
}

# Start Piddy if not running
if ! check_piddy_api; then
    echo "Starting Piddy core..."
    python src/main.py &
    PIDDY_PID=$!
    sleep 3
fi

# Start Dashboard API
echo "Starting Dashboard API..."
python src/dashboard_api.py &
DASHBOARD_API_PID=$!
sleep 2

# Start Frontend
echo "Starting Dashboard Frontend..."
cd frontend
npm run dev

# Cleanup on exit
trap "kill $PIDDY_PID $DASHBOARD_API_PID" EXIT
```

## Data Model Reference

### Agent Status
```python
class AgentStatus(BaseModel):
    agent_id: str
    role: str
    status: str  # "online" | "offline"
    reputation_score: float  # 0.5-2.0
    total_decisions: int
    success_rate: float  # 0-100
    messages_pending: int
    last_update: datetime
```

### Message
```python
class AgentMessage(BaseModel):
    message_id: str
    from_agent_id: str
    to_agent_id: str
    message_type: str  # proposal, vote, execute, report, query, alert
    content: dict
    priority: int  # 1-10
    timestamp: datetime
```

### Log Entry
```python
class LogEntry(BaseModel):
    level: str  # INFO, WARNING, ERROR, DEBUG
    source: str  # module/component
    message: str
    timestamp: datetime
    context: dict
```

### Phase Status
```python
class PhaseStatus(BaseModel):
    phase_id: str
    phase_name: str
    status: str  # pending, in_progress, completed, failed
    progress_percent: float  # 0-100
    start_time: datetime
    end_time: Optional[datetime]
    error_message: Optional[str]
```

### Security Audit Result
```python
class SecurityAuditResult(BaseModel):
    audit_id: str
    timestamp: datetime
    is_production_safe: bool
    passed_checks: int
    failed_checks: int
    critical_failures: List[str]
```

## Performance Considerations

### Polling vs WebSocket

| Aspect | Polling | WebSocket |
|--------|---------|-----------|
| Latency | 5-30s | <100ms |
| Bandwidth | Higher | Lower |
| CPU | Moderate | Low |
| Simplicity | Simple | Complex |
| Browser Support | All | Modern |

**Recommendation**: Use polling for non-critical data (health, phases) and WebSocket for real-time streams (logs, messages).

### Scalability Tips

1. **Pagination**: Use limit/offset for large data sets
```python
@app.get("/api/logs?limit=100&offset=0")
```

2. **Filtering**: Allow client-side filtering
```python
@app.get("/api/logs?level=ERROR")
```

3. **Aggregation**: Pre-aggregate metrics on backend
```python
@app.get("/api/metrics/summary")  # Pre-computed stats
```

4. **Caching**: Cache infrequently updated data
```python
@app.get("/api/phases")  # Cache 30 seconds
```

## Troubleshooting Integration

### Connection Refused

```bash
# Check if Piddy is running
curl http://127.0.0.1:8000/api/health

# If not, start it:
python src/main.py

# Verify port is available:
lsof -i :8000
```

### WebSocket Connection Failed

```bash
# Browser console should show:
# WebSocket is open: ws://127.0.0.1:8000/ws/logs

# If not connecting:
# 1. Check CORS in dashboard_api.py
# 2. Verify WebSocket endpoints are implemented
# 3. Check firewall allows port 8000
```

### Data Not Updating

```bash
# Check API endpoints return data:
curl http://127.0.0.1:8000/api/agents

# If empty, check:
# 1. Piddy core is running and has agents
# 2. Dashboard API correctly imports Piddy
# 3. Data bridge methods are called
```

### Performance Issues

```python
# Profile dashboard_api.py
python -m cProfile src/dashboard_api.py

# Check MongoDB/cache performance
# Reduce polling intervals if too frequent
# Enable WebSocket for real-time data
```

## Security Considerations

1. **Authentication**: Add API key/JWT for production
```python
@app.post("/api/login")
async def login(credentials: LoginRequest):
    # Implement auth
```

2. **Authorization**: Restrict agent access
```python
@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str, user: User = Depends(get_current_user)):
    # Check user permissions
```

3. **Rate Limiting**: Prevent abuse
```python
@app.get("/api/logs", dependencies=[Depends(RateLimiter(calls=100, period=60))])
```

4. **Data Validation**: Validate all inputs
```python
@app.get("/api/logs?level={level}")
async def get_logs(level: LogLevel):  # Enum validation
```

5. **HTTPS**: Use HTTPS in production
```python
# In vite.config.js for local testing with HTTPS
```

## Deployment

### Docker Integration

See `Dockerfile` and `docker-compose.yml` for containerized deployment.

### Desktop Installation

Use Electron or Tauri to package as desktop application. See frontend/README.md for details.

### Cloud Deployment

Deploy to AWS/GCP/Azure with proper configurations:
- Set `VITE_API_URL` to cloud endpoint
- Use HTTPS/WSS
- Implement proper auth
- Set up monitoring and logging

## Next Steps

1. ✅ Run mock dashboard (current state)
2. 📝 Integrate dashboard API with running Piddy
3. 🔗 Connect frontend to live backend data
4. 🧪 Test all data flows
5. 🚀 Package as desktop application
6. 📊 Add additional monitoring features as needed

## Support Resources

- Dashboard API: `src/dashboard_api.py`
- Frontend Components: `frontend/src/components/`
- Piddy Core: `src/agent/core.py`, `src/service/`
- Documentation: This file + inline code comments
