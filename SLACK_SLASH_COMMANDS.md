# Piddy Self-Healing - Slack Commands

## Available Slack Commands

All commands follow this pattern:
```
/piddy [self] [command] [options]
```

---

## Quick Commands

### 🚀 Go Live (Most Important)
```
/piddy self go live
```
**What it does:**
- Runs complete system audit
- Auto-fixes ALL issues
- Removes ALL mock data
- Creates comprehensive PR
- System becomes 100% operational

**Response:**
```
🚀 Piddy Autonomous Go-Live

Status: go_live_complete
Message: PIDDY IS NOW FULLY OPERATIONAL AND LIVE

System Status:
• Mock Data: ❌ REMOVED
• Production Ready: ✅ YES
• All Systems: ✅ ONLINE
• Ready to Merge: ✅ YES

Next Step: Review and merge the auto-generated PR on GitHub
```

---

### 🔍 Audit System
```
/piddy self audit
```
**What it does:**
- Scans all code for issues
- Checks security vulnerabilities
- Analyzes database performance
- Validates integrations
- Reports findings

**Response:**
```
🔍 System Audit Complete

Issues Found: 521
• Critical: 0
• High: 3
• Medium: 18

Next Step: Run 'self go live' to auto-fix
```

---

### 🔧 Auto-Fix All Issues
```
/piddy self fix
```
**What it does:**
- Removes hardcoded mock data
- Fixes code quality issues
- Fixes security vulnerabilities
- Optimizes database
- Runs full test suite
- Creates PR with fixes

**Response:**
```
🔧 Autonomous Self-Fix Complete

Status: self-fix_complete
Message: All systems auto-fixed! Review and merge the PR to go live.

Fixes Applied:
• Mock Data Removal: ✅
• Code Quality: ✅
• Security Issues: ✅
• Database Optimization: ✅
• Tests: ✅
• Integration: ✅
• PR Created: ✅

Next Step: Review PR on GitHub
```

---

### 📊 Check Status
```
/piddy self status
```
**What it does:**
- Shows current system status
- Reports monitoring status
- Shows issues detected/fixed
- Displays autonomous capability

**Response:**
```
📊 Piddy System Status

Monitoring: 🟢 ENABLED
Capability: fully_operational
Issues Detected: 521
Issues Fixed: 47

Type `/piddy self go live` to start autonomous go-live
```

---

## Setup (Slack Workspace Admin)

### Prerequisites
1. Slack app must have Socket Mode enabled
2. Your app must have these permissions:
   - `commands` - To receive slash commands
   - `chat:write` - To send messages back

### Register Commands

In Slack App Settings, go to **Slash Commands** and add:

1. **Create slash command `/piddy`**
   - Command: `/piddy`
   - Request URL: `http://your-domain/slack/events` (via Socket Mode)
   - Short Description: "Piddy autonomous system commands"
   - Usage Hint: `[self] [command]`

2. **Socket Mode** enables the following automatically:
   - All slash commands route through Socket Mode
   - No public URL needed
   - Real-time bidirectional connection

### Enable Socket Mode
1. In your Slack App settings
2. Go to **Socket Mode**
3. Toggle **Enable Socket Mode** on
4. Set up your Token scope with `commands`

---

## Examples

### Complete Go-Live Flow
```
User: /piddy self go live
↓
Piddy: 🚀 Starting autonomous go-live...
↓
Piddy: ✅ Audit complete (found 521 issues)
↓
Piddy: ✅ Auto-fixed all issues and removed mock data
↓
Piddy: ✅ Created PR with all changes
↓
Piddy: Ready to deploy! Review and merge the PR
```

### Usage Flow
```bash
# 1. Check status
/piddy self status

# 2. Run audit to see what needs fixing
/piddy self audit

# 3. Auto-fix everything
/piddy self fix

# 4. Or go direct to live
/piddy self go live
```

---

## Alternative: Use Curl/API Directly

If you prefer the terminal:

```bash
# Go live
curl -X POST http://localhost:8000/api/self/go-live | jq

# Audit
curl -X POST http://localhost:8000/api/self/audit | jq

# Fix
curl -X POST http://localhost:8000/api/self/fix-all | jq

# Status
curl http://localhost:8000/api/self/status | jq
```

---

## Troubleshooting

### Command not responding
- Ensure Socket Mode is enabled
- Check `/slack/events` endpoint is accessible
- Verify Slack token has `commands` scope

### "Connection refused"
- Ensure Piddy backend is running on port 8000
- Check firewall allows localhost connections

### PR not created
- Verify GitHub token is set in environment
- Check `~/.github` or `GITHUB_TOKEN` is configured

---

## For Developers

The slash command handler is in:
```
src/integrations/socket_mode.py
_handle_slash_command() method
```

To add new commands, add a new `elif` branch:
```python
elif "your_command" in text:
    self._handle_your_command(channel_id, user_id, response_url)
```

---

## Summary

| Command | What It Does | When to Use |
|---------|-------------|-----------|
| `/piddy self go live` | Complete go-live automation | Deploy everything at once |
| `/piddy self audit` | Scan system for issues | Before fixing anything |
| `/piddy self fix` | Auto-fix everything | After audit, before merge |
| `/piddy self status` | Check system health | Monitor ongoing operations |

**Most common:** Just type `/piddy self go live` and let Piddy handle the rest! 🚀
