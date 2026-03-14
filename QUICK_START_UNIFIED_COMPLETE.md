# 🚀 Piddy Unified System - Complete Quick Start Guide

**Status**: ✅ **PRODUCTION READY**  
**Date**: March 14, 2026  
**Latest Integration**: Unified Dashboard (Monitoring + Approvals)

---

## 🎯 What You Have

Your Piddy system now includes:

### ✅ Core Components
- **Market Gap Detection** - Autonomous agent detects market needs
- **Security Assessment** - AI evaluates security risks
- **Email Notifications** - Automatic alerts to approvers
- **Approval Workflow** - Human security review before building
- **Unified Dashboard** - Monitor system + approve gaps in one interface
- **Health Checks** - System readiness verification

### ✅ New Features (Just Added)
- **Frontend UI** - Beautiful React approval interface
- **Startup Script** - One command to run everything
- **Email Triggers** - Listen for market gap emails and auto-create requests
- **Health Endpoints** - Monitor system status
- **Integration Tests** - Verify everything works

---

## ⚡ Quick Start (2 Minutes)

### 1. **Configure Email**

First time only - set up email notifications:

```bash
python src/email_config.py --profile gmail
```

This sets up your email to receive approval requests. Follow the prompts to enter:
- Your email address (stephen.burch@ghostai.solutions or burchsl4@gmail.com)
- Your Gmail app password (create at https://myaccount.google.com/apppasswords)

**Already configured?** Skip to step 2!

### 2. **Start Everything**

One command starts the entire system:

```bash
python start_piddy.py
```

This automatically:
- ✅ Installs frontend dependencies
- ✅ Starts background service (market gaps + emails)
- ✅ Starts dashboard (monitoring + approvals)
- ✅ Starts frontend dev server
- ✅ Runs health checks
- ✅ Opens dashboard in browser

### 3. **Access the Dashboard**

Open your browser to:

```
http://localhost:8000/
```

You should see:
- 📊 System monitoring dashboard
- 📋 Market Approvals tab (right in sidebar)
- 🤖 Agent status, metrics, logs
- ✅ Health status indicator

**Done!** Your system is running. Now wait for market gaps (or trigger one).

---

## 📋 Using the Approvals Feature

### Viewing Market Gaps

1. Click **"Approvals"** in the sidebar (📋 icon)
2. You'll see:
   - **Statistics** - Total decisions, approval rate
   - **Pending Requests** - Gaps waiting for your decision
   - **Risk Indicators** - HIGH/MEDIUM/LOW security levels

### Approving a Gap

1. Click on a request to expand it
2. Click on a gap to see details:
   - Market need description
   - Security concerns listed
   - Integration points required
   - Estimated build time
3. Click **✅ Approve** to let Piddy build it
4. Or click **❌ Reject** with a reason

### Gap Details

Each gap shows:

| Field | Meaning |
|-------|---------|
| **Risk Level** | 🔴 HIGH = Security concern, ⚠️ MEDIUM = Review needed, 🟢 LOW = Safe |
| **Category** | Type of feature (API, database, UI, etc.) |
| **Market Need** | Why customers want this |
| **Frequency** | How often was this requested |
| **Impact** | Potential benefit (0-1 scale) |
| **Complexity** | Build difficulty (1-10) |
| **Security Concerns** | List of potential risks |

---

## 🔧 Configuration Reference

### Email Setup

**Gmail (recommended):**
```bash
python src/email_config.py --profile gmail
```

**Corporate Email:**
```bash
python src/email_config.py --profile corporate
```

**Custom SMTP:**
```bash
python src/email_config.py --profile custom
```

### Configure Both Email Addresses

Edit `config/email_config.json` to add both emails:

```json
{
  "email": "stephen.burch@ghostai.solutions",
  "additional_emails": ["burchsl4@gmail.com"],
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "use_tls": true
}
```

---

## 💡 Advanced Usage

### Start Specific Components

**Dashboard only:**
```bash
python start_piddy.py --dashboard-only
```

**Background service only:**
```bash
python start_piddy.py --service-only
```

**Frontend only:**
```bash
python start_piddy.py --frontend-only
```

### Debug Mode

Run background service in foreground (see all output):
```bash
python start_piddy.py --foreground
```

### Configure Email Before Starting

```bash
python start_piddy.py --configure
```

---

## 🏥 System Health

### Check System Status

```bash
# Quick health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Verify system readiness
curl -X POST http://localhost:8000/health/verify
```

### Expected Response

```json
{
  "status": "healthy",
  "components": {
    "service": "running",
    "dashboard": "running",
    "approval_system": "ready",
    "database": "connected"
  }
}
```

---

## 📊 Approval API Endpoints

### List All Approvals

```bash
curl http://localhost:8000/api/approvals
```

### Get Specific Request

```bash
curl http://localhost:8000/api/approvals/{request_id}
```

### View Gap Details

```bash
curl http://localhost:8000/api/approvals/{request_id}/gaps/{gap_id}
```

### Approve a Gap

```bash
curl -X POST http://localhost:8000/api/approvals/{request_id}/gaps/{gap_id}/approve
```

### Reject a Gap

```bash
curl -X POST http://localhost:8000/api/approvals/{request_id}/gaps/{gap_id}/reject \
  -H "Content-Type: application/json" \
  -d '{"reason": "Needs more review"}'
```

### Get Statistics

```bash
curl http://localhost:8000/api/approvals/summary/stats
```

---

## 🚨 Troubleshooting

### Dashboard Won't Start

**Check if port 8000 is free:**
```bash
lsof -i :8000
```

**If something is using it:**
```bash
# Kill the process
kill -9 <PID>

# Or use different port
python src/dashboard_manager.py --start --port 8001
```

### No Approval Requests Appearing

1. **Check logs:**
   ```bash
   tail -f data/service.log
   ```

2. **Verify email config:**
   ```bash
   cat config/email_config.json
   ```

3. **Check approval workflow state:**
   ```bash
   cat data/approval_workflow_state.json
   ```

### Emails Not Sending

1. **Verify email configuration:**
   ```bash
   python src/email_config.py --profile gmail --verify
   ```

2. **Check SMTP settings:**
   - Gmail: smtp.gmail.com:587 (TLS)
   - Corporate: Check your IT department

3. **Check for app password (Gmail):**
   - https://myaccount.google.com/apppasswords
   - Generate if not yet created

### Testing Approval Workflow

```bash
# Run integration tests
python tests/integration_unified_system.py

# This will verify:
# ✅ Dashboard API responding
# ✅ All endpoints accessible
# ✅ Data models correct
# ✅ Approval workflow working
# ✅ Health checks passing
```

---

## 📁 Project Structure

```
Piddy/
├── start_piddy.py                      # 🚀 Main startup script
├── frontend/                            # React dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── Approvals.jsx           # 📋 NEW - Approval UI
│   │   │   └── ... (other components)
│   │   ├── styles/
│   │   │   └── components.css          # Updated with new styles
│   │   └── App.jsx                     # Updated routing
│   └── package.json
│
├── src/
│   ├── dashboard_api.py                # Dashboard backend
│   │   └── New endpoints: /health, /health/detailed, /health/verify
│   │   └── Plus 8 approval endpoints
│   ├── dashboard_manager.py            # Dashboard control
│   ├── service_manager.py              # Background service control
│   ├── email_config.py                 # Email configuration
│   ├── email_trigger_listener.py       # 📧 NEW - Email monitoring
│   ├── market_gap_reporter.py          # Gap detection
│   ├── autonomous_background_service.py # Gap processing
│   └── ... (other modules)
│
├── data/
│   ├── approval_workflow_state.json    # Active approval requests
│   ├── approval_decisions.json         # Audit trail
│   ├── service.log                     # Background service logs
│   └── dashboard.log                   # Dashboard logs
│
├── config/
│   └── email_config.json               # Email settings
│
├── tests/
│   └── integration_unified_system.py   # 🧪 NEW - Integration tests
│
└── docs/
    ├── UNIFIED_DASHBOARD_INTEGRATION.md
    └── APPROVAL_SYSTEM_QUICKSTART.md
```

---

## 📚 Documentation Files

- **[UNIFIED_DASHBOARD_INTEGRATION.md](UNIFIED_DASHBOARD_INTEGRATION.md)**
  - Architecture overview
  - API endpoint reference
  - Integration details

- **[APPROVAL_SYSTEM_QUICKSTART.md](APPROVAL_SYSTEM_QUICKSTART.md)**
  - Approval workflow basics
  - How decisions impact agent building

- **[DEPLOYMENT_GUIDE_APPROVAL_SYSTEM.md](DEPLOYMENT_GUIDE_APPROVAL_SYSTEM.md)**
  - Production deployment
  - Configuration best practices
  - Monitoring and alerts

---

## ✨ What Happens When...

### You Approve a Gap
1. ✅ **Decision recorded** in approval_decisions.json
2. ✅ **Status updated** to `approved`
3. ✅ **Agent is triggered** to build the feature
4. ✅ **Progress visible** in System → Phases tab
5. ✅ **Result shown** when complete

### You Reject a Gap
1. ❌ **Decision recorded** with your reason
2. ❌ **Status updated** to `rejected`
3. ❌ **Agent skips** building this feature
4. ❌ **Similar requests** are deprioritized

### Email Arrives
1. 📧 **Email trigger listener** detects market gap in subject
2. 📧 **Content is parsed** for gap details
3. 📧 **Approval request created** automatically
4. 📧 **You get notified** (goes to both emails)
5. 📋 **appears in dashboard** for your review

---

## 🎯 Success Looks Like

✅ **Dashboard opens**
```
http://localhost:8000/
```

✅ **Approvals tab shows**
- Statistics visible
- "No Approval Requests" or pending requests listed

✅ **Health checks pass**
```
curl http://localhost:8000/health
→ {"status": "healthy", ...}
```

✅ **Approval endpoints work**
```
curl http://localhost:8000/api/approvals
→ {"requests": {...}, "count": N, ...}
```

✅ **You can interact with UI**
- Click to expand requests
- See gap details
- Approve/reject gaps

---

## 🚀 Next Steps

### Step 1: Configuration ✅
- [x] Email configured
- [x] System verified with health check

### Step 2: Monitoring 📊
- Monitor the dashboard
- Watch for market gaps
- Review security assessments

### Step 3: Decision Making 📋
- Approve gaps that align with business
- Reject gaps with security concerns
- Set your decision reason

### Step 4: Continuous Operation 🔄
- System continues detecting gaps
- You review and decide
- Agents build approved features
- Audit trail recorded

---

## 📞 Support

### Logs to Check

```bash
# Background service log
tail -100 data/service.log

# Dashboard log
tail -100 data/dashboard.log

# Email trigger log
tail -100 data/email_trigger.log

# See all recent activity
tail -f data/service.log | grep -i "gap\|email\|approval"
```

### Common Commands

```bash
# Check system status
python src/service_manager.py --status
python src/dashboard_manager.py --status

# Stop everything
python src/service_manager.py --stop
python src/dashboard_manager.py --stop

# Restart
python src/service_manager.py --restart
python src/dashboard_manager.py --restart

# View approval decisions
cat data/approval_decisions.json | python -m json.tool

# View pending approvals
cat data/approval_workflow_state.json | python -m json.tool
```

---

## 🎓 Learning Path

1. **Day 1**: Get it running (this quick start)
2. **Day 2**: Review first approval requests
3. **Day 3**: Make approval/rejection decisions
4. **Week 1**: Observe built features
5. **Week 2**: Refine your approval strategy

---

## ✅ Checklist for Production

- [ ] Email configured for both addresses
- [ ] Health checks passing
- [ ] Dashboard accessible
- [ ] Approvals tab working
- [ ] Can view and approve test gaps
- [ ] Email notifications working (check inbox)
- [ ] Logs monitoring in place
- [ ] Backups configured

---

## 🎉 You're All Set!

Your Piddy unified system is ready to:

1. **Detect** market gaps automatically
2. **Assess** security implications
3. **Notify** you with email alerts
4. **Wait** for your approval decision
5. **Build** only what you approve
6. **Monitor** progress in dashboard

**Happy approving!** 🚀

---

**Questions?**  
Check the documentation files or review the logs:
```bash
tail -f data/service.log
```

**Version**: v1.0 - Unified Dashboard Integration Complete  
**Last Updated**: March 14, 2026
