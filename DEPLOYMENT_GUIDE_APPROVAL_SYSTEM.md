# PIDDY Approval System - Deployment Guide

**Status**: Production Ready ✅  
**Last Updated**: March 14, 2026  
**Version**: 1.0.0

---

## Quick Start (5 Minutes)

### 1. Configure Email

Choose your email provider and run the setup:

**Option A: Gmail (Recommended)**
```bash
python src/email_config.py --profile gmail \
  --username stephen.burch@ghostai.solutions \
  --password YOUR_APP_PASSWORD
```
[Get Gmail App Password](https://myaccount.google.com/apppasswords) (Enable 2FA first)

**Option B: Corporate Email**
```bash
python src/email_config.py --profile ghostai \
  --username stephen.burch@ghostai.solutions \
  --password YOUR_PASSWORD
```

**Option C: Local Testing (No Email)**
```bash
python src/email_config.py --profile localhost
```
Emails will be saved to `data/email_notifications/`

### 2. Verify Configuration

```bash
python src/email_config.py --show
```

Expected output:
```
📧 Current Email Configuration:
   Profile: gmail
   Server: smtp.gmail.com
   Port: 587
   Primary: stephen.burch@ghostai.solutions
   Secondary: burchsl4@gmail.com
```

### 3. Start Services

**Terminal 1: Background Service**
```bash
python src/service_manager.py --start

# Output:
# ✅ Service started successfully!
#    Process ID: 12345
#    Log file: data/service.log
#
# 💡 To view logs: tail -f data/service.log
```

**Terminal 2: Approval Dashboard**
```bash
python src/dashboard_manager.py --start

# Output:
# ✅ Dashboard started successfully!
#    Process ID: 12346
#    URL: http://localhost:8000
#    Browser opening...
```

### 4. Test the System

Run integration tests:
```bash
python tests/e2e_test_approval_system.py
```

Expected:
```
🎉 ALL TESTS PASSED! 
   Total Tests: 25
   Success Rate: 100.0%
```

### 5. Watch for Approvals

Market gaps will be detected and emailed to you:
- stephen.burch@ghostai.solutions
- burchsl4@gmail.com

Email subject: `🚨 PIDDY: X Market Gaps Found (Y HIGH Risk)`

Click the dashboard link in the email or visit `http://localhost:8000`

---

## Complete Deployment Steps

### Prerequisites

- Python 3.11+
- pip with latest version
- Git
- 2GB free disk space

### Step 1: Clone Repository

```bash
git clone https://github.com/burchdad/Piddy.git
cd Piddy
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi`: Dashboard web framework
- `uvicorn`: ASGI server
- `pydantic`: Data validation

### Step 3: Create Config Directory

```bash
mkdir -p config data/email_notifications
```

### Step 4: Configure Email

See "Quick Start > Step 1" above.

### Step 5: Run Tests

```bash
# Full integration test
python tests/e2e_test_approval_system.py

# Individual component tests
python src/market_gap_reporter.py    # Email & security assessment
python src/approval_workflow.py       # Workflow state machine
python src/approval_dashboard.py      # FastAPI dashboard
```

### Step 6: Start Services

**Option A: Separate Terminals (Development)**

```bash
# Terminal 1: Service
python src/service_manager.py --start-fg

# Terminal 2: Dashboard
python src/dashboard_manager.py --start-fg
```

**Option B: Background Mode (Production)**

```bash
# Start both as daemons
python src/service_manager.py --start
python src/dashboard_manager.py --start

# Check status
python src/service_manager.py --status
python src/dashboard_manager.py --status

# View logs
tail -f data/service.log
tail -f data/dashboard.log
```

---

## Configuration Reference

### Email Configuration

File: `config/email_config.json`

```json
{
  "profile": "gmail",
  "smtp": {
    "server": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "username": "stephen.burch@ghostai.solutions",
    "password": "xxxx xxxx xxxx xxxx",
    "from_email": "piddy@autonomous.local"
  },
  "recipients": {
    "primary": "stephen.burch@ghostai.solutions",
    "secondary": "burchsl4@gmail.com"
  }
}
```

### Service Configuration

File: `src/autonomous_background_service.py`

```python
# Edit line ~350:
user_email = "stephen.burch@ghostai.solutions,burchsl4@gmail.com"

# Market analysis frequency (cycles)
market_analysis_interval = 100  # ~1.7 hours in demo mode

# Approval timeout (hours)
approval_timeout_hours = 24
```

### Dashboard Configuration

File: `src/dashboard_manager.py`

```python
# Edit line ~40:
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000

# Access from: http://localhost:8000
```

---

## Monitoring & Troubleshooting

### Check Service Status

```bash
# Service status
python src/service_manager.py --status

# Dashboard status
python src/dashboard_manager.py --status
```

### View Logs

```bash
# Service logs
tail -f data/service.log

# Dashboard logs
tail -f data/dashboard.log

# Email notifications
ls -la data/email_notifications/
```

### Common Issues

**Issue: "SMTP connection refused"**
```
Solution:
1. Check email configuration: python src/email_config.py --show
2. Verify credentials are correct
3. For Gmail: Ensure app password (not regular password)
4. For localhost: Run: python -m smtpd -n -c DebuggingServer localhost:1025
```

**Issue: "Dashboard port already in use"**
```
Solution:
# Use different port
python src/dashboard_manager.py --start --port 9000
# Access at: http://localhost:9000
```

**Issue: "Service not starting"**
```
Solution:
# Check errors
python src/service_manager.py --start-fg  # Foreground mode shows errors

# View logs
tail -100 data/service.log

# Verify Python version
python --version  # Should be 3.11+
```

**Issue: "No emails received"**
```
Solution:
1. Check recipients in config
2. Verify email configured: python src/email_config.py --show
3. Run market gap reporter test:
   python src/market_gap_reporter.py
4. Check data/email_notifications/ for saved emails
```

---

## Operations Guide

### Starting Services

**Development Mode (Blocking)**
```bash
python src/service_manager.py --start-fg
python src/dashboard_manager.py --start-fg
```

**Production Mode (Background)**
```bash
python src/service_manager.py --start
python src/dashboard_manager.py --start

# Monitor
python src/service_manager.py --status
python src/dashboard_manager.py --status
```

### Stopping Services

```bash
python src/service_manager.py --stop
python src/dashboard_manager.py --stop
```

### Restarting Services

```bash
python src/service_manager.py --restart
python src/dashboard_manager.py --restart
```

### Viewing Real-Time Logs

```bash
# Service (in new terminal)
tail -f data/service.log

# Dashboard
tail -f data/dashboard.log

# Both (side-by-side)
tmux new-window -n 'logs'
tmux split-window -h
tmux send-keys -t 'logs:0' 'tail -f data/service.log' Enter
tmux send-keys -t 'logs:1' 'tail -f data/dashboard.log' Enter
```

---

## Approval Workflow

### Phase 1: Gap Detection & Email
1. Background service runs market analysis cycle
2. Gaps identified by market analyzer
3. Security assessment performed (HIGH/MEDIUM/LOW)
4. Email sent to configured addresses with:
   - Subject: `🚨 PIDDY: X Market Gaps Found (Y HIGH Risk)`
   - Risk summary
   - Dashboard link: `http://localhost:8000/approvals/{request_id}`

### Phase 2: User Review & Approval
1. User receives email with approval request
2. User clicks dashboard link or navigates to `http://localhost:8000`
3. User reviews each gap:
   - Gap name and market need
   - Security risk level (🚨 HIGH / ⚠️ MEDIUM / ✅ LOW)
   - Security concerns listed
   - Estimated build time
4. User clicks APPROVE or REJECT for each gap
   - For HIGH risk: Must provide rejection reason if rejecting
   - For MEDIUM/LOW: Can approve or reject

### Phase 3: Build Queue
1. Dashboard records user decisions
2. Only approved gaps are queued for building
3. Rejected gaps are archived (never built)
4. Background service picks up approved gaps from queue
5. Builds execute in order

### Phase 4: Audit Trail
All decisions logged to `data/approval_decisions.json`:
```json
{
  "request_id": "req_20260314_190228",
  "gaps": [
    {
      "gap_id": "gap_001",
      "title": "Mutation Testing",
      "approved": true,
      "approved_at": "2026-03-14T19:02:28.123456",
      "reason": null
    },
    {
      "gap_id": "gap_002",
      "title": "Build Optimization",
      "approved": false,
      "approved_at": "2026-03-14T19:02:30.987654",
      "reason": "Needs security audit before deploying to CI/CD pipeline"
    }
  ]
}
```

---

## Risk Categories

### 🚨 HIGH RISK (Explicit Approval Required)
- **CI/CD Modifications**: Build pipelines, deployment systems
- **Dependency Management**: Package managers, import systems  
- **Refactoring**: Large-scale code modifications
- **Deployment**: Production infrastructure changes

**Action**: Carefully review. Provide rejection reason if declining.

### ⚠️ MEDIUM RISK (Flagged for Review)
- **Code Quality**: Analysis rules, warning configuration
- **Documentation**: Auto-documentation systems
- **Complex Agents**: High complexity score (8+) with broad integration

**Action**: Review security concerns. Approve or reject as needed.

### ✅ LOW RISK (Easy to Approve)
- **Testing**: Unit tests, integration tests, mutation testing
- **Analysis**: Code metrics, static analysis
- **Simple Agents**: Low complexity, limited integration points

**Action**: Safe to approve. Reject only for specific reasons.

---

## Data Files & Locations

```
data/
├── service.log                          # Background service logs
├── service.pid                          # Service process ID
├── dashboard.log                        # Dashboard logs
├── dashboard.pid                        # Dashboard process ID
├── approval_workflow_state.json         # Active workflows
├── approval_decisions.json              # All user decisions (audit trail)
└── email_notifications/
    ├── approval_request_req_20260314_...  # Email copy 1
    ├── approval_request_req_20260314_...  # Email copy 2
    └── ...                                # More email copies

config/
└── email_config.json                    # Email configuration
```

---

## Maintenance

### Weekly

- Check logs for errors: `grep ERROR data/*.log`
- Verify disk space: `df -h`
- Review approval decisions: `tail -50 data/approval_decisions.json`

### Monthly

- Clear old email notifications: `rm data/email_notifications/*`
- Archive logs: `gzip data/*.log && mv data/*.log.gz archive/`
- Update dependencies: `pip install --upgrade -r requirements.txt`

### Quarterly

- Review security assessments: Are risk levels accurate?
- Update market analysis categories based on new gap types
- Rotate credentials (especially for corporate email)

---

## Security Considerations

### Email Security

- **Username/Password**: Stored in `config/email_config.json` (not in git!)
- **App Passwords**: Use app-specific passwords for Gmail (more secure)
- **Corporate Email**: Use temporary credentials or app tokens
- **Local Mode**: No credentials needed for localhost testing

### Dashboard Security

- **No Authentication**: This implementation is for internal use
- **Localhost Default**: By default runs only on localhost:8000
- **Network Access**: If exposing to network, add authentication layer
- **HTTPS**: Use reverse proxy (nginx) for HTTPS in production

### Approval Decisions

- **Audit Trail**: All decisions logged with timestamps
- **Immutable**: Once recorded, decisions cannot be modified
- **Traceability**: Each decision includes user action, gap ID, reason

---

## Advanced Configuration

### Custom Email Provider

Edit `src/email_config.py`:

```python
PROFILES = {
    "my_smtp": {
        "server": "mail.mycompany.com",
        "port": 587,
        "use_tls": True,
        "description": "My company SMTP",
    }
}
```

Then configure:
```bash
python src/email_config.py --profile my_smtp \
  --username user@mycompany.com \
  --password PASSWORD
```

### Custom Dashboard Port

```bash
python src/dashboard_manager.py --start --port 9000
# Access at: http://localhost:9000
```

### Custom Approval Timeout

Edit `src/autonomous_background_service.py`:

```python
self.approval_workflow = ApprovalWorkflow(
    approval_timeout_hours=48  # 48 hours instead of 24
)
```

### Multiple Email Addresses

Already configured! Supports comma-separated emails:

```bash
# In config/email_config.json:
"recipients": {
  "primary": "stephen.burch@ghostai.solutions",
  "secondary": "burchsl4@gmail.com"  
}
```

---

## Performance Tuning

### Increase Market Analysis Frequency

Edit `src/autonomous_background_service.py` line ~369:

```python
# More frequent (every ~50 cycles ≈ 50 minutes)
market_analysis_interval = 50

# Less frequent (every ~200 cycles ≈ 3+ hours)
market_analysis_interval = 200
```

### Increase Approval Timeout

Edit `src/autonomous_background_service.py` line ~268:

```python
self.approval_workflow = ApprovalWorkflow(
    approval_timeout_hours=72  # 3 days
)
```

### Change Dashboard Port

```bash
python src/dashboard_manager.py --start --port 8080
```

---

## Support & Troubleshooting

### Getting Help

1. **Check Logs**: `tail -100 data/service.log`
2. **Verify Config**: `python src/email_config.py --show`
3. **Run Tests**: `python tests/e2e_test_approval_system.py`
4. **Check Status**: `python src/service_manager.py --status`

### Debug Mode

```bash
# Service in foreground with full output
python src/service_manager.py --start-fg

# Dashboard in foreground with reload
python src/dashboard_manager.py --start-fg
```

### Reset State (Careful!)

```bash
# Clear all workflows
rm data/approval_workflow_state.json

# Clear all decisions
rm data/approval_decisions.json

# Clear all emails
rm data/email_notifications/*
```

---

## Next Steps

After deployment:

1. ✅ Configure email (see Quick Start)
2. ✅ Start services
3. ✅ Verify approval email received
4. ✅ Test approve/reject via dashboard
5. ✅ Check that only approved gaps build
6. ✅ Review audit trail (approval_decisions.json)
7. ✅ Monitor logs for first week
8. ✅ Adjust risk categories based on your needs

---

## Version History

**v1.0.0** (2026-03-14)
- Initial release
- Market gap analysis with security assessment
- Email notifications to dual email addresses  
- Web dashboard for approvals
- Background service with daemon mode
- Complete audit trail
- 25 integration tests (100% passing)

---

## License

Your project license here

---

**Deployment Date**: ________________  
**Deployed By**: ________________  
**Environment**: ☐ Development  ☐ Staging  ☐ Production  
**Email Profile**: ☐ Gmail  ☐ Corporate  ☐ Localhost  
**Notes**: _______________________________________________

---

For questions or issues, refer to test output or check `APPROVAL_WORKFLOW_GUIDE.md` for architectural details.
