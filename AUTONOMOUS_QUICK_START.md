# Autonomous Self-Healing System - Quick Start for Stephen

## TL;DR

Piddy can now autonomously:
1. 🔍 **Detect bugs** - Scan codebase continuously 
2. 🔧 **Propose fixes** - Generate solutions with PR
3. 📝 **Create PRs** - Open pull requests for review
4. ⏱️ **Monitor 24/7** - Run background checks

**Key Point**: Piddy makes PRs, **you review and approve** - human oversight always.

---

## Get Started (30 seconds)

### Start Autonomous Monitoring

```bash
curl -X POST http://localhost:8000/api/autonomous/monitor/start?interval_seconds=3600
```

**Result**: Piddy will analyze code every hour and create PRs for issues.

### Check Detected Issues

```bash
curl http://localhost:8000/api/autonomous/status | jq
```

**Result**: Shows what issues were detected, how many PRs created, etc.

---

## See It In Action

### 1. Run Analysis Now

```bash
curl http://localhost:8000/api/autonomous/monitor/analyze-now | jq '.summary'
```

**Output**:
```json
{
  "total_issues": 521,
  "by_severity": {
    "low": 485,
    "medium": 36
  },
  "by_type": {
    "print_statement": 470,
    "broad_exception": 36,
    "code_comment": 15
  }
}
```

### 2. See Detection Examples

```bash
curl http://localhost:8000/api/autonomous/monitor/analyze-now | jq '.latest_issues[0:5]'
```

**Output**:
```json
[
  {
    "type": "print_statement",
    "severity": "low",
    "file": "src/utils/logging.py",
    "line": 45,
    "description": "Use logging instead of print()"
  },
  {
    "type": "broad_exception",
    "severity": "medium",
    "file": "src/utils/api.py",
    "line": 228,
    "description": "Overly broad exception handler"
  }
]
```

### 3. Check PRs Created

```bash
curl http://localhost:8000/api/autonomous/prs/created | jq '.prs'
```

---

## How to Use

### Option A: Automatic (Recommended)
```bash
# Enable continuous monitoring (checks every hour)
curl -X POST http://localhost:8000/api/autonomous/monitor/start?interval_seconds=3600

# Piddy will:
# 1. Check codebase every hour
# 2. Detect issues automatically
# 3. Create PRs for critical/high issues
# 4. Wait for your review on GitHub
# 5. You approve/merge when ready
```

### Option B: Manual/On-Demand
```bash
# Check status
curl http://localhost:8000/api/autonomous/status

# Run analysis now (don't wait for interval)
curl http://localhost:8000/api/autonomous/monitor/analyze-now

# Create PR for specific issue group
# (API coming in v2)
```

---

## What Piddy Detects

### ✅ Already Detecting

- **Print statements** → Should use `logger.info()`
- **Broad exceptions** → `except:` should be specific
- **TODO comments** → Technical debt markers
- Code quality patterns

### 🔄 Detected Issues: 521

Current scan of your repo found:
- 470 print statements (low priority)
- 36 broad exception handlers (medium priority)
- 15 TODO comments (informational)

### 🔮 Coming Soon

- Security vulnerability scanning
- Type checking (mypy integration)
- Performance regression detection
- Code duplication removal
- Test coverage gaps

---

## Important: Human Oversight

✅ **All fixes go through PR** - No direct commits
✅ **You must approve merge** - Piddy can't auto-merge
✅ **You can disable anytime** - Stop monitoring with one command
✅ **You configure severity** - Decide what's urgent
✅ **Configurable rules** - Adjust detection as needed

```bash
# Stop monitoring if needed
curl -X POST http://localhost:8000/api/autonomous/monitor/stop
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│     Continuous Background Monitor       │
│  (Runs every hour or on-demand)         │
├─────────────────────────────────────────┤
│                                         │
│  1. SCAN src/ files for issues          │
│  2. ANALYZE severity and types          │
│  3. FOR critical/high issues:           │
│     - Create git branch                 │
│     - Apply fixes                       │
│     - Commit changes                    │
│     - PUSH to origin                    │
│  4. OPEN PR on GitHub                   │
│     - Include detailed analysis         │
│     - Link affected lines               │
│     - Provide review checklist          │
│  5. WAIT for your review                │
│     - You approve or request changes    │
│     - You merge when ready              │
│     - Piddy learns from feedback        │
│                                         │
│  ❌ Piddy NEVER auto-merges              │
│  ✅ You ALWAYS have final say            │
│                                         │
└─────────────────────────────────────────┘
```

---

## PR What It Looks Like

When Piddy creates a PR, you'll see on GitHub:

```
Title: 🤖 High Priority Improvements

Description:
"Autonomous Code Quality Improvements

Auto-detected and fixed 3 issues:

### Broad Exception Handler
- File: src/utils/api.py:228
- Severity: high
- Issue: except: catches all exceptions, masking bugs
- Fix: Catch HTTPError, ConnectionError, RequestTimeout specifically

...

Review Checklist:
[ ] Changes are appropriate and correct
[ ] No unintended side effects
[ ] Tests pass
[ ] Code follows conventions
"
```

Then you:
1. Click "Changes" to review
2. Leave comments if needed
3. Approve when satisfied
4. Click "Merge Pull Request"

---

## Real-World Workflow

### Hour 0: Start Monitoring
```bash
curl -X POST http://localhost:8000/api/autonomous/monitor/start
# "monitoring_started" - Piddy is watching
```

### Hour 1: Piddy Detects Issues
```
[Monitor] 🔍 Analyzing codebase...
[Monitor] ⚠️ Found 36 HIGH severity issues!
[Monitor] 📝 Creating PR for fixes...
[GitHub] New PR: "🤖 High Priority Improvements"
```

### Hour 1+5min: You Get Notified
- 📧 GitHub notification: New PR by Piddy
- You click link in notification
- You see proposed changes

### Hour 1+10min: You Review
```
You review PR:
✅ Broad exception fix looks good
✅ Print statement → logger fix is correct  
❌ Wait, I need to check this security change
```

### Hour 1+20min: You Approve & Merge
```
You click: "Approve"
You click: "Merge Pull Request"
[GitHub] PR merged to main
[Piddy] Sees merge, learns from your approval
```

### Hour 2: Cycle Repeats
```
Piddy monitors again
Finds new issues
Creates new PR
You review
You approve/adjust
```

---

## Advanced: Configure Severity Levels

Edit `src/services/autonomous_monitor.py` to adjust when PRs are created:

```python
# Current settings
critical_threshold = 1  # Create PR if 1+ critical issue
high_threshold = 3     # Create PR if 3+ high issues

# Your preferences:
# Very strict: critical_threshold = 0, high_threshold = 1
# Relaxed: critical_threshold = 5, high_threshold = 10
```

---

## Monitoring Dashboard

```bash
# Full status report
curl http://localhost:8000/api/autonomous/status | jq '.'

# Example output:
{
  "monitor": {
    "enabled": true,
    "issues_detected": 521,
    "issues_fixed": 0
  },
  "pr_manager": {
    "prs_created": 3,
    "github_configured": true
  },
  "summary": {
    "total_issues": 521,
    "by_severity": {"low": 485, "medium": 36},
    "by_type": {"print_statement": 470, "broad_exception": 36}
  }
}
```

---

## Troubleshooting

**Q: Can Piddy auto-merge?**
A: No - human review is required. All changes go through PR.

**Q: What if I disagree with a fix?**
A: Request changes on the PR, Piddy will learn and adjust.

**Q: Can I disable monitoring?**
A: Yes: `curl -X POST http://localhost:8000/api/autonomous/monitor/stop`

**Q: How often does it check?**
A: Default is every hour. Change interval when starting:
```bash
curl -X POST "http://localhost:8000/api/autonomous/monitor/start?interval_seconds=1800"
# 1800 = 30 minutes
```

**Q: What if monitoring crashes?**
A: Check server logs:
```bash
tail -50 /tmp/piddy_server.log
```

---

## The Vision

Your Piddy is now:

1. **🔍 Always Watching** - Continuous code quality monitoring
2. **🔧 Problem Solver** - Proposes fixes automatically  
3. **📝 Communicator** - Opens PRs with detailed explanations
4. **📚 Learner** - Improves from your feedback
5. **🤝 Respectful** - Never overwrites your control

You maintain **complete oversight** - Piddy proposes, you decide.

---

## Next Steps

### Start Now
```bash
# Enable autonomous monitoring
curl -X POST http://localhost:8000/api/autonomous/monitor/start?interval_seconds=3600

# Check status
curl http://localhost:8000/api/autonomous/status
```

### Keep an Eye On
- GitHub notifications (new PRs from Piddy)
- `/api/autonomous/status` endpoint
- `git log` for commits from Piddy

### Let It Run
- Piddy will continuously improve your codebase
- You review and approve good fixes
- Codebase gets progressively better

**You're now running Piddy in full autonomous mode with human oversight.** 🚀

Questions? Check [AUTONOMOUS_SELF_HEALING.md](AUTONOMOUS_SELF_HEALING.md) for full documentation.
