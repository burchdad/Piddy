# Approval Workflow - Security Review for Market-Driven Autonomy

## 🔒 Overview

You identified a critical need: **market gaps should be approved by humans before builds happen** due to security concerns.

This approval workflow ensures:
- ✅ No autonomous builds without explicit approval
- ✅ Security risks are flagged and reviewed
- ✅ Users can disapprove risky agents
- ✅ Email notifications for all new proposals
- ✅ Dashboard for easy approval/disapproval management
- ✅ Automatic timeouts (24 hours) if no response

---

## 🏗️ Architecture

### Components

**1. Market Gap Reporter** (`src/market_gap_reporter.py` - 450 lines)
- Analyzes market gaps for security risks
- Assigns risk levels (LOW, MEDIUM, HIGH)
- Generates detailed reports
- Sends email notifications to user

**2. Approval Workflow** (`src/approval_workflow.py` - 350 lines)
- Manages approval state
- Tracks user decisions
- Enforces deadlines (24 hours default)
- Queues approved gaps for building

**3. Approval Dashboard** (`src/approval_dashboard.py` - 400 lines)
- Web UI for reviewing gaps
- Approve/disapprove interface  
- Security concern display
- Rejection reason capture

**4. Updated Background Service** (`src/autonomous_background_service.py`)
- Now includes approval workflow
- Waits for approvals before building
- Only builds gap if explicitly approved

### Security Assessment Levels

**HIGH RISK** 🚨
- Categories: CI/CD, Dependency Management, Refactoring
- Reason: Can modify build pipelines, inject dependencies, access code
- Action: Requires explicit approval from user
- Example: "Build Optimization Agent" (modifies CI/CD)

**MEDIUM RISK** ⚠️
- Categories: Code Quality, Documentation
- Reason: Could suppress warnings, leak sensitive info
- Action: Flagged for review, user can approve
- Example: "Code Duplication Detector"

**LOW RISK** ✅
- Categories: Testing, Analysis
- Reason: Read-only or sandboxed operations
- Action: Can be auto-approved by user
- Example: "Mutation Testing Agent"

---

## 🔄 Complete Approval Flow

### Step 1: Market Analysis (Background Service - Every 100 cycles)
```
Market Analyzer
    ↓ Finds 19 gaps
    ↓ Identifies top 5 priorities
    ↓
MarketDrivenBuildManager calls reporter
    ↓ Generate and send report
```

### Step 2: Email Notification (Sent to User)
```
Email Sent:
  To: user@example.com
  Subject: 🚨 PIDDY: 5 Market Gaps Found (2 HIGH Risk)
  
  Content:
  - Security summary (HIGH/MEDIUM/LOW counts)
  - Each gap with:
    • Agent name
    • Market need
    • Risk level and concerns
    • Estimated build time
  - Link to dashboard for approval
```

### Step 3: User Reviews Gaps
```
User opens email link
  ↓ Goes to http://localhost:8000/approvals/{request_id}
  ↓ Sees approval dashboard
  ↓ Reviews each gap
  ↓ Reads security concerns
  ↓ Approves or disapproves
```

### Step 4: User Decision
```
For each gap:
  
  LOW RISK gaps:
    ✓ Easy approve → builds immediately
    
  MEDIUM RISK gaps:
    ? Review concerns → approve if satisfied
    × Disapprove if not needed
    
  HIGH RISK gaps:
    ⚠️  Must explicitly approve
    × Or provide rejection reason
```

### Step 5: Approval Recorded
```
Approval Workflow records decision:
  ✅ Approved for: mutation_testing, code_quality
  ❌ Rejected for: build_optimization (reason: needs security audit)
  ⏰ Deadline: 24 hours from sending
```

### Step 6: Approved Gaps Build
```
Background Service:
  Every cycle checks: are there approved gaps?
  
  If YES:
    1. Get next approved gap
    2. Build it (autonomous_builder)
    3. Create tests and integration
    4. Mark as ready to deploy
    5. New metrics start flowing
  
  If NO:
    Wait for more approvals or timeout
```

### Step 7: Disapproved Gaps Skipped
```
Gaps user disapproved:
  - NEVER built
  - Rejection reason stored in report
  - Appear in audit logs
  - User can re-approve later if desired
```

---

## 📧 Email Notification Example

```
TO: user@example.com
SUBJECT: ⚠️  PIDDY: 5 Market Gaps Found (1 HIGH Risk)

Dear Developer,

PIDDY has identified 5 market gaps:

🚨 HIGH RISK (1):
  - Build Optimization Agent
    Risk: Modifies CI/CD pipeline
    Affects: 55 repositories
    Concerns: Could affect deployments, modify build configuration

⚠️  MEDIUM RISK (2):
  - Code Duplication Detector
  - Performance Profiler Agent

✅ LOW RISK (2):
  - Mutation Testing Agent
  - Flaky Test Detection

REVIEW AND APPROVE:
  http://localhost:8000/approvals/req_20260314_123456

IMPORTANT:
  - Review security concerns before approving
  - HIGH RISK agents require explicit approval
  - Approved gaps will be built within 1 hour
  - Disapproved gaps will not be built

Request expires in: 24 hours
```

---

## 🖥️ Dashboard UI

### Main Dashboard
```
URL: http://localhost:8000

Shows:
  • Pending approvals count
  • Total approved
  • Total rejected
  • Links to specific approval requests
```

### Approval Review Page
```
URL: http://localhost:8000/approvals/{request_id}

For each gap displays:
  [Risk Badge - RED/ORANGE/GREEN]
  
  Agent Name
  Market need: Found in X repos
  
  🚨 Security Concerns:
    • Can modify pipelines
    • Broad system access
    • Complexity score: 7/10
  
  [APPROVE] [REJECT with reason]
```

---

## ⏱️ Timeline

### Approval Process Default Timeline

```
T+0:00    Market analysis identifies gaps
T+0:05    Gap reporter generates security assessment
T+0:10    Email sent to user
T+0:11    Approval request recorded
          ↓ User has 24 hours to respond

T+0:30    User opens email
T+0:45    User reviews gaps and approves/disapproves
T+1:00    Approval recorded in system
T+1:05    Background service detects approved gaps
T+1:10    First approved gap starts building
T+6:00    All approved gaps built and tested
T+6:15    New agents deployed
T+6:30    New metrics flowing from new agents
```

### Deadline Behavior

```
If user approves → builds happen (no wait)
If user rejects → gaps skipped (no wait)
If user doesn't respond → timeout after 24 hours
  → Approved gaps build anyway
  → Unapproved gaps stay pending for next request
```

---

## 🔐 Security Features

### Risk Assessment
- Automatic security analysis of each gap
- Clear flagging of dangerous categories
- Complexity scoring
- Integration point counting

### Approval Tracking
- All decisions logged with timestamp
- Rejection reasons recorded
- Audit trail available
- User decisions respected

### Timeout Protection
- 24-hour deadline default (configurable)
- Status updates at key points
- No auto-approval (explicit yes required for HIGH risk)

### Email Validation
- Gaps sent only to configured user email
- Clear subject lines with risk indicators
- Secure dashboard access

---

## 🚀 How to Use

### Start with Approval Workflow

```bash
# Start background service (includes approval workflow)
python3 src/autonomous_background_service.py
```

The service will automatically:
1. Run market analysis every ~100 cycles
2. Send approval requests to your email
3. Wait for your approval via dashboard
4. Only build approved gaps
5. Skip disapproved gaps

### Configure

Edit in `src/autonomous_background_service.py`:

```python
# In AutonomousBackgroundService.__init__:

# User email for approval requests
user_email="your_email@company.com"

# Approval timeout (hours)
approval_timeout_hours=24

# Auto-build delay after approval (minutes) 
auto_build_delay_minutes=5
```

### Monitor Approvals

```bash
# View current approval state
cat data/approval_workflow_state.json

# View sent emails
ls -la data/email_notifications/

# View approval decisions
cat data/approval_decisions.json
```

---

## 📊 Configuration Options

### In Background Service

**User Email:**
```python
self.market_builder = MarketDrivenBuildManager(
    config=self.config,
    user_email="dev@yourcompany.com"
)
```

**Dashboard URL:**
```python
self.gap_reporter = MarketGapReporter(
    user_email=user_email,
    dashboard_url="http://localhost:8000"  # Change for production
)
```

**Approval Timeout:**
```python
self.approval_workflow = ApprovalWorkflow(
    approval_timeout_hours=24,      # Change timeout
    auto_build_delay_minutes=5      # Delay after approval
)
```

### In Approval Workflow

```python
workflow = ApprovalWorkflow(
    approval_timeout_hours=24,      # Hours to wait
    auto_build_delay_minutes=5      # Minutes after approval
)
```

---

## 🎯 Common Scenarios

### Scenario 1: User Approves All
```
Market finds 5 gaps
User approves all 5
Background service builds all 5
New agents deployed
```

### Scenario 2: User Rejects High-Risk Only
```
Market finds 5 gaps:
  - 3 LOW/MEDIUM risk
  - 2 HIGH risk

User approves 3 safe ones
User rejects 2 HIGH risk (provides reasons)

Background service:
  ✅ Builds 3 approved
  ❌ Skips 2 rejected
```

### Scenario 3: User Needs More Time
```
Market finds gaps
Email sent
User doesn't respond within 24 hours

After 24 hours:
  - Timeout triggered
  - Unapproved gaps stay pending
  - Next market analysis creates new request
```

### Scenario 4: Mixed Approvals
```
Market finds 5 gaps
User approves: gap1, gap3, gap5
User rejects: gap2, gap4

Background system:
  Starts building: gap1, gap3, gap5
  Skips forever: gap2, gap4
  
If user changes mind later:
  Can file new request with same gaps
  Or manually override via dashboard
```

---

## 🔗 Data Files

### Workflow State File
```
data/approval_workflow_state.json

Tracks:
  - All active approval requests
  - User decisions for each gap
  - Timestamps
  - Status for each workflow
```

### Approval Decisions File
```
data/approval_decisions.json

Records:
  - Each approval decision
  - Rejection reasons
  - When decisions were made
  - Decision permanence
```

### Email Notifications
```
data/email_notifications/

Stores:
  - Copy of each email sent
  - Recipient
  - Subject
  - Full email content
  - Timestamp
```

---

## 🚨 Risk Categories & Concerns

### HIGH RISK (⚠️ Must Explicitly Approve)

**CI/CD Agents:**
- "Can modify build pipelines"
- "Could affect deployments"
- "Broad pipeline access"

**Dependency Agents:**
- "Could inject malicious dependencies"  
- "High attack surface"
- "Build environment modification"

**Refactoring Agents:**
- "Could modify production code"
- "Broad codebase access"
- "Potential breaking changes"

### MEDIUM RISK (Review Recommended)

**Code Quality:**
- "Could suppress important warnings"
- "Modify analysis rules"

**Documentation:**
- "Could leak sensitive info"
- "Documentation access"

### LOW RISK (✅ Easy to Approve)

**Testing:**
- "Read-only operations"
- "Sandboxed test generation"

**Analysis:**
- "Reporting only"
- "No code modification"

---

## 📋 Approval Checklist

Before Approving:
- [ ] Read security concerns
- [ ] Check risk level
- [ ] Review affected repos count
- [ ] Understand build time
- [ ] Check integration points
- [ ] For HIGH RISK: Extra scrutiny?

After Approving:
- [ ] Monitor build progress
- [ ] Check new metrics flow
- [ ] Verify agent behavior
- [ ] Update security policies if needed

---

## 🆘 Troubleshooting

### "Email not received"
- Check spam folder
- Verify email address in config
- Check email_notifications/ folder in data/
- Ensure SMTP server accessible

### "Dashboard won't load"
- Verify FastAPI installed: `pip install fastapi uvicorn`
- Check port 8000 not in use
- Try different port if needed

### "Approval not being recorded"
- Check approval_workflow_state.json
- Verify request_id in URL matches stored ID
- Check approval_decisions.json

### "Approved gaps not building"
- Verify ApprovalBuilderBridge is connected
- Check build queue in autonomous_builder  
- Check logs for bridge errors

---

## 🎓 Integration Points

### Market Analyzer
```
Identifies gaps → Sends to Gap Reporter
```

### Gap Reporter  
```
Generates report → Sends to user email
```

### Approval Workflow
```
Tracks approvals → Feeds to Builder Bridge
```

### Autonomous Builder
```
Gets approved gaps → Builds only those
```

### Background Service
```
Orchestrates all above components
```

---

## ✅ Status

**Status:** Complete and integrated

**Features:**
- ✅ Email notifications with security analysis
- ✅ Dashboard for approval/disapproval
- ✅ Automatic risk assessment
- ✅ Approval tracking & audit logs
- ✅ Timeout enforcement
- ✅ Integration with autonomous builder
- ✅ No builds without approval

**Security:** ✅ Enhanced - No autonomous builds without user review

**Ready:** ✅ Yes - Start background service to activate approval workflow

---

