# 🤖 Autonomous Monitoring Activation Guide

**Status**: ✅ **READY TO ACTIVATE**

All autonomous tools are now integrated into Piddy's agent toolkit. The system is deployed and waiting for your command to begin.

---

## Quick Start Command

Send this command to Piddy in Slack:

```
@Piddy start autonomous monitoring
```

**Expected Response**:
```
🤖 Autonomous monitoring enabled. I'll analyze the codebase every 3600s (60 minutes) 
and create PRs for issues.
```

---

## What Happens Next

1. **Immediate**: Piddy's autonomous monitor activates in the background
2. **Every 60 minutes** (default interval):
   - Piddy scans the entire codebase
   - Detects issues: print statements (low severity), broad exceptions (medium), TODO comments (low)
   - Analyzes findings by severity and type
3. **When Issues Found**:
   - Piddy creates a GitHub PR with:
     - Issue analysis and summary
     - Suggested fixes (if applicable)
     - File locations and line numbers
     - Review checklist for human approval
4. **Human Oversight**:
   - You review the PR on GitHub
   - Approve or request changes
   - Auto-merge is NOT enabled (requires manual approval)

---

## Autonomous Commands

Once monitoring is started, you can also:

### Check Status
```
@Piddy check autonomous status
```
Shows: monitor status, total issues detected, issues fixed, PRs created, breakdown by severity

### Analyze Now (Don't Wait)
```
@Piddy analyze code now
```
Runs immediate code analysis without waiting for the scheduled interval

### Stop Monitoring
```
@Piddy stop autonomous monitoring
```
Disables autonomous monitoring. Piddy will no longer analyze or create PRs automatically.

### View Created PRs
```
@Piddy show created PRs
```
Lists all PRs created by the autonomous system with links

---

## Configuration Options

If you want a different monitoring interval, you can specify it:

```
@Piddy start autonomous monitoring every 1800 seconds
```
This would scan every 30 minutes instead of the default 60 minutes.

Available intervals:
- **600** = 10 minutes (frequent, lots of PRs)
- **1800** = 30 minutes (moderate)
- **3600** = 60 minutes (default, once per hour)
- **7200** = 2 hours (less frequent)
- **86400** = 1 day (daily scan only)

---

## Technical Details

### Issues Detected

| Type | Severity | Description |
|------|----------|-------------|
| Print statements | Low | Debug print statements that should be removed |
| Broad exceptions | Medium | Catch-all except clauses (except Exception, except:) |
| TODO comments | Low | Code marked with TODO for future work |

### Current System Status

✅ **Server Running**: Yes (PID 3453)
✅ **Tools Loaded**: 67 total (10 autonomous)
✅ **Autonomous API**: Ready
✅ **GitHub Integration**: Configured
✅ **Response Storage**: Enabled

### Tools Now Available to Piddy

Autonomous Monitoring (NEW):
- `autonomous_monitor_start` - Enable monitoring
- `autonomous_monitor_stop` - Disable monitoring  
- `autonomous_monitor_status` - Get system status
- `autonomous_analyze_now` - Run immediate analysis
- `autonomous_get_prs` - List created PRs

Autonomous Planning (Existing):
- `execute_autonomous_mission` - Multi-step missions
- `extract_service_autonomously` - Service extraction
- `improve_coverage_autonomously` - Test coverage improvement
- `cleanup_dead_code_autonomously` - Dead code removal
- `fix_architecture_autonomously` - Architecture fixes

---

## How It Works (Technical)

1. **Command Recognition**: When you say "start autonomous monitoring", Piddy's ReAct agent recognizes this as an autonomous system command

2. **Tool Execution**: The `autonomous_monitor_start` tool is called with an interval (default 3600 seconds)

3. **Background Process**: A background task starts monitoring on the configured interval

4. **Codebase Scanning**: Every interval:
   - Scans all Python files in `src/` directory
   - Analyzes for issues using pattern detection
   - Groups issues by severity and type
   - Creates summary statistics

5. **PR Generation**: When issues are found:
   - Creates feature branch: `autonomous/issues-{timestamp}`
   - Commits findings with detailed commit message
   - Pushes branch to GitHub
   - Opens PR with issue analysis and suggested fixes
   - Returns to main branch

6. **Response Format**: All responses are formatted for Slack with:
   - Emoji indicators (✅, 🤖, 📊, etc.)
   - Clear markdown tables and lists
   - Links to GitHub PRs
   - Status summaries

---

## Next Steps

1. **Send Command**: Tell Piddy to start autonomous monitoring
2. **Verify**: Check that the status shows "🟢 ENABLED"
3. **Wait**: Monitor will run on the configured interval (default 60 minutes)
4. **Review**: When PR appears on GitHub, review and approve
5. **Monitor**: Keep watching for additional PRs as Piddy finds more issues

---

## Troubleshooting

If Piddy doesn't recognize the command:

1. **Verify Integration**: 
   ```bash
   python -c "from src.tools import get_all_tools; tools = get_all_tools(); auto_tools = [t.name for t in tools if 'autonomous' in t.name]; print(f'Found {len(auto_tools)} autonomous tools')"
   ```

2. **Check Server Status**:
   ```bash
   curl http://localhost:8000/api/autonomous/status
   ```

3. **View Logs**:
   ```bash
   tail -f /tmp/piddy_server.log
   ```

4. **Restart Server**:
   ```bash
   pkill -f "python.*src.main"
   cd /workspaces/Piddy && python -m src.main &
   ```

---

## Success Indicators

✅ **Monitoring Started**: Response says "🤖 Autonomous monitoring enabled"
✅ **Status Enabled**: `@Piddy check status` shows 🟢 ENABLED
✅ **PR Created**: GitHub shows new PR from `autonomous-monitor` branch
✅ **Issue Analysis**: PR contains detailed issue breakdown and file locations
✅ **GitHub Link**: You can review and approve the PR

---

## Full Feature Summary

| Feature | Status | Details |
|---------|--------|---------|
| Tool Integration | ✅ Complete | 10 autonomous tools registered |
| Server Running | ✅ Yes | PID 3453 |
| API Endpoints | ✅ Ready | All 5 endpoints functional |
| Code Analysis | ✅ Ready | Detects 3 issue types |
| PR Generation | ✅ Ready | GitHub integration configured |
| Background Monitoring | ✅ Ready | Async event loop ready |
| Response Formatting | ✅ Ready | Slack markdown support |
| Error Handling | ✅ Yes | Comprehensive error detection |

---

## Questions?

For issues or questions about the autonomous system:

1. Check the deployment logs:
   ```bash
   tail /tmp/piddy_server.log
   ```

2. View autonomous system status:
   ```bash
   curl http://localhost:8000/api/autonomous/status | jq
   ```

3. Run immediate analysis (no wait):
   ```bash
   @Piddy analyze code now
   ```

**You're all set! Send the activation command whenever you're ready.** 🚀
