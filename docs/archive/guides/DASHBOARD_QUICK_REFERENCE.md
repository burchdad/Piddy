# Piddy Dashboard Quick Reference

## 🎯 Dashboard Overview

The Piddy Dashboard is a real-time monitoring system for your autonomous agents. It provides comprehensive visibility into agent behavior, system health, performance metrics, and security status.

## 🚀 Quick Start

### Option 1: Linux/macOS
```bash
cd /workspaces/Piddy
./start-dashboard.sh
```

### Option 2: Windows
```cmd
cd \path\to\piddy
start-dashboard.bat
```

### Option 3: Manual Setup
```bash
# Terminal 1: Start Piddy Core
python src/main.py

# Terminal 2: Start Dashboard API
python src/dashboard_api.py

# Terminal 3: Start Frontend
cd frontend
npm install
npm run dev
```

## 📊 Dashboard Pages

### 1. 📊 Overview (Home)
**What to see**: System health snapshot
- Total agents online/offline
- Recent messages count
- Active phases
- Security issues
- Passed/failed tests
- System version & uptime

**Use case**: Quick health check of entire system

---

### 2. 🤖 Agents
**What to see**: Individual agent monitoring
- Agent ID and role
- Status (online/offline)
- Reputation score (0.5-2.0)
- Decision count
- Success rate %
- Messages pending

**Use case**: Monitor specific agent performance and reliability
**Example**: "Why is Agent-3's reputation low?" → Check success rate and recent decisions

---

### 3. 💬 Messages (Read-Only)
**What to see**: AI-to-AI communication
- Sender → Recipient
- Message type (proposal, vote, execute, etc.)
- Message content (JSON)
- Priority level (1-10, color coded)
- Timestamp

**Use case**: Observe how agents cooperate without human interference
**Features**:
- Filter by message type
- Real-time auto-scroll
- Message statistics
- NOT editable (secure observation)

---

### 4. 📝 Logs
**What to see**: System event log stream
- Log level (DEBUG, INFO, WARNING, ERROR)
- Source component
- Message text
- Expandable JSON details
- Timestamp

**Use case**: Troubleshoot issues and trace system execution
**Features**:
- Filter by log level
- Search by source
- Expandable details
- Real-time streaming

**Common Issues**:
- `ERROR Agent communication` → Check Messages page
- `WARNING Phase timeout` → Check Phases page
- `ERROR Security check failed` → Check Security page

---

### 5. ✅ Tests
**What to see**: Test execution results
- Test name and path
- Status (PASSED/FAILED/SKIPPED)
- Duration in seconds
- Error message (if failed)
- Pass rate %

**Use case**: Verify system functionality and regressions
**Features**:
- Summary statistics
- Detailed test listing
- Pass/fail/skip counts

---

### 6. 📈 Metrics
**What to see**: Performance analytics
- Current metric values
- Thresholds and status
- Agent reputation analytics
- Success rate trends

**Metrics Tracked**:
- Response times
- Agent decisions/sec
- Message throughput
- System resource usage
- Agent reputation scores

---

### 7. 🚀 Phases
**What to see**: Deployment phase tracking
- Phase name and ID
- Current status
- Progress % (0-100)
- Start/end time
- Error message (if failed)

**Statuses**:
- `pending` - Waiting to start (grey)
- `in_progress` - Currently running (blue)
- `completed` - Successfully finished (green)
- `failed` - Error during execution (red)

---

### 8. 🔒 Security
**What to see**: Security and compliance status
- Production readiness
- Audit results
- Critical failures list
- Security checklist status
- Pass rate %

**Key Indicators**:
- ✅ Green = Safe for production
- ❌ Red = Not ready for production
- Critical failures = Must fix before deployment

---

## 🎮 Controls & Features

### Navigation
- **Sidebar**: Click icon or name to switch pages
- **Collapse**: Click arrow to collapse sidebar (saves space)
- **Status**: Green dot = Connected, Red dot = Disconnected

### Filtering
- **Log Level**: Click filter buttons (INFO, WARNING, ERROR, DEBUG)
- **Message Type**: Select from dropdown
- **Date/Time**: Use timestamp filters

### Expandable Details
- **Click arrow** (▼) to expand JSON details
- **Visible**: Log entries, messages, phases
- **Use**: Debug specific events

### Real-Time Updates
- **Auto-refresh**: Every 5-30 seconds (configurable)
- **WebSocket streams**: Logs and messages update live
- **Status indicator**: Shows connection status

---

## 🔧 Configuration

### Dashboard Environment
Create `frontend/.env`:
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000
VITE_ENABLE_WEBSOCKETS=true
```

### Polling Intervals
Adjust update frequency:
```env
VITE_REFRESH_INTERVAL=30000      # Main pages: 30 seconds
VITE_LOG_POLL_INTERVAL=10000     # Logs: 10 seconds
VITE_AGENT_POLL_INTERVAL=10000   # Agents: 10 seconds
VITE_MESSAGE_POLL_INTERVAL=5000  # Messages: 5 seconds
```

---

## 📱 Performance Tips

### Dashboard Is Slow?
1. Close unused browser tabs
2. Increase polling intervals in `.env`
3. Reduce log retention
4. Disable WebSockets if not needed

### High CPU Usage?
1. Check if agents are stuck in loops
2. Verify test suite isn't running continuously
3. Check if logging is set to DEBUG level
4. Consider running on more powerful machine

### Network Issues?
1. Verify backend is running: `curl http://127.0.0.1:8000/api/health`
2. Check firewall allows port 8000
3. Verify frontend env has correct API URL
4. Try WebSocket disabled mode (polling only)

---

## 🛠️ Troubleshooting

### Dashboard Won't Load
```bash
# Check if services are running
curl http://127.0.0.1:8000/api/health

# Check frontend logs
tail -f /tmp/dashboard-frontend.log

# Check API logs
tail -f /tmp/dashboard-api.log

# Restart services
./start-dashboard.sh  # or start-dashboard.bat on Windows
```

### No Data Showing
1. Verify Piddy core is running and has agents
2. Check API endpoints: `curl http://127.0.0.1:8000/api/agents`
3. Check browser console for fetch errors (F12)
4. Mock data should load if Piddy unavailable

### Connection Errors
- Backend unreachable? → Start Dashboard API: `python src/dashboard_api.py`
- WebSocket failing? → Try disabling in `.env`: `VITE_ENABLE_WEBSOCKETS=false`
- CORS error? → Check vite.config.js proxy settings

### Crash or Freeze
- Browser console errors? (F12)
- Too much data? → Reduce log retention in settings
- Memory leak? → Restart dashboard: `./start-dashboard.sh`

---

## 📊 Interpreting the Data

### Agent Health
**Good**: 
- Status: online
- Reputation: 1.5-2.0
- Success rate: >95%
- Messages: reasonable volume

**Bad**:
- Status: offline
- Reputation: <1.0
- Success rate: <80%
- No recent messages

### System Load
**Normal**:
- Response times: <500ms
- Messages/sec: steady
- Error rate: <1%
- Tests: >95% pass rate

**Warning**:
- Response times: 500ms-2s
- Error rate: 1-5%
- Tests: 90-95% pass rate
- Phases: stalled >5 min

**Critical**:
- Response times: >2s
- Error rate: >5%
- Tests: <90% pass rate
- Phases: failed
- Security: not production safe

---

## 🔐 Security Notes

### Read-Only Operation
✅ **Safe**: View all pages
✅ **Safe**: Filter and search data
✅ **Safe**: Export data (future feature)
❌ **Blocked**: Cannot modify agents
❌ **Blocked**: Cannot inject messages
❌ **Blocked**: Cannot change configuration

### Data Privacy
- Dashboard data reflects agent actions
- No sensitive credentials displayed
- Logs may contain algorithm details (appropriate for operations)
- Security audit available to authorized users

---

## 📚 Data Definitions

### Reputation Score
- **Formula**: (Successes × 2 - Failures) / Total Decisions
- **Range**: 0.5 (worst) to 2.0 (best)
- **Baseline**: 1.0 (neutral)
- **Interpretation**:
  - <1.0: Unreliable (high failure rate)
  - 1.0-1.5: Acceptable
  - 1.5-2.0: Excellent
  - 2.0: Perfect

### Priority Levels
- **1-3**: Low (background operations)
- **4-7**: Medium (normal operations)
- **8-10**: High (critical or urgent)

### Phase Status
- **pending**: Not started, waiting for dependencies
- **in_progress**: Currently executing
- **completed**: Successfully finished
- **failed**: Error occurred, requires manual intervention

---

## 🎓 Common Workflows

### Debugging a Failed Agent
1. Go to **Agents** page
2. Find agent with low reputation
3. Go to **Messages** page, filter for that agent
4. Check sent/received messages for patterns
5. Go to **Logs** page, search agent ID
6. Review error messages and stack traces

### Investigating System Errors
1. Start at **Overview** (see error count)
2. Go to **Logs** page
3. Filter to ERROR level
4. Click to expand error details
5. Check timestamp against **Phases** and **Tests**
6. Correlate with agent behavior in **Agents** page

### Monitoring Deployment
1. Go to **Phases** page
2. Watch progress bars update
3. Check **Logs** for warnings during phase
4. Verify **Tests** pass after phase completion
5. Confirm **Security** audit once phase complete
6. Check **Metrics** for performance impact

### Performance Analysis
1. Go to **Metrics** page
2. Check all metrics vs. thresholds
3. Review **Agents** for busy agents
4. Check **Messages** frequency/throughput
5. Look at **Logs** for slow operations
6. Identify bottleneck (agent, network, storage)

---

## 🆘 Getting Help

### Documentation
- `frontend/README.md` - Frontend setup guide
- `DASHBOARD_INTEGRATION_GUIDE.md` - Backend integration
- Inline code comments in components

### Logs for Debugging
```bash
# Frontend logs
tail -f /tmp/dashboard-frontend.log

# API logs
tail -f /tmp/dashboard-api.log

# Browser console
Press F12 → Console tab
```

### Common Questions

**Q: Can I modify agents from dashboard?**
A: No, it's read-only monitoring for safety and integrity.

**Q: How often does data update?**
A: Configurable, default 5-30 seconds depending on page.

**Q: Can I export data?**
A: Not yet, but dashboard stores all data server-side for querying.

**Q: Is it secure?**
A: In development mode, add authentication Layer before production.

**Q: Can I run it on different machines?**
A: Yes, update `VITE_API_URL` to remote backend URL.

---

## 🎉 Next Steps

1. ✅ Start dashboard with `./start-dashboard.sh`
2. 📊 Explore each page to understand system
3. 🔗 Integrate with your Piddy deployment
4. 📈 Set up production monitoring
5. 🚀 Use for continuous operations

**Enjoy monitoring your autonomous system!** 🚀
