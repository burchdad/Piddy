# Piddy Autonomous Self-Healing System

## Overview

Piddy now operates as a **self-aware, self-healing AI agent** that can:
- 🔍 **Detect Issues** - Automatically scan codebase for bugs, code smells, and quality issues
- 🔧 **Generate Fixes** - Create targeted solutions for identified problems  
- 📝 **Open PRs** - Submit pull requests for human review (not direct commits)
- ⏱️ **Monitor Continuously** - Run scheduled analysis to catch new issues

This enables **autonomous code maintenance with human oversight** - Piddy identifies problems and proposes solutions, you review and approve.

---

## How It Works

### Workflow: Bug → Fix → PR → Human Review

```
1. DETECT
   ├─ Scan Python files for code issues
   ├─ Check for print() statements (should use logging)
   ├─ Detect broad exception handlers (missing specificity)
   ├─ Find TODO/FIXME comments (technical debt)
   └─ Identify security concerns

2. ANALYZE
   ├─ Categorize by severity (critical, high, medium, low)
   ├─ Group by issue type
   ├─ Build fix suggestions
   └─ Create detailed reports

3. FIX
   ├─ Create new git branch (fix/autonomous-YYYYMMDD-HHMMSS)
   ├─ Apply targeted improvements
   ├─ Commit with descriptive messages
   └─ Push to remote

4. PR
   ├─ Open pull request on GitHub
   ├─ Include detailed analysis and fixes
   ├─ Link to affected lines
   └─ Provide review checklist

5. REVIEW (Human)
   ├─ Review Piddy's proposed changes
   ├─ Approve or request modifications
   ├─ Merge when satisfied
   └─ Piddy learns from feedback
```

---

## Current Detection Capabilities

### Issues Detected (v1.0)

| Issue Type | Severity | Detection | Fix Suggestion |
|---|---|---|---|
| **Print Statements** | Low | `print(` found in code | Use `logger.info()` instead |
| **Broad Exceptions** | Medium | `except:` or bare `except Exception:` | Catch specific exceptions |
| **TODO Comments** | Low | `# TODO` or `# FIXME` markers | Highlighted for prioritization |
| Code Quality | Low→High | Various patterns | Context-specific suggestions |

### Example Detection

```python
# Code with issues
try:
    data = fetch_data()
    print("Got data:", data)  # ❌ DETECTED: Use logging
except:  # ❌ DETECTED: Too broad
    print("Error!")
```

**Auto-Detected Issues**:
```
1. Line 45: print_statement (LOW)
   File: src/utils/api.py
   Fix: Replace with logger.info("Got data: %s", data)

2. Line 47: broad_exception (MEDIUM)  
   File: src/utils/api.py
   Fix: Catch HTTPError, ConnectionError, etc. specifically
```

---

## API Endpoints

### 1. Get Autonomous Status
```
GET /api/autonomous/status
```

Returns overall system status and statistics:
```json
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
}
```

### 2. Analyze Codebase Now
```
GET /api/autonomous/monitor/analyze-now
```

Runs immediate analysis:
```json
{
  "issues_found": 521,
  "summary": {...},
  "latest_issues": [
    {
      "type": "print_statement",
      "severity": "low",
      "file": "src/utils/logging.py",
      "line": 45,
      "description": "Use logging instead of print()"
    }
  ]
}
```

### 3. Start Continuous Monitoring
```
POST /api/autonomous/monitor/start?interval_seconds=3600
```

Enables background monitoring with specified interval:
```json
{
  "status": "monitoring_started",
  "interval_seconds": 3600
}
```

### 4. Stop Monitoring
```
POST /api/autonomous/monitor/stop
```

### 5. Get Created PRs
```
GET /api/autonomous/prs/created
```

Lists all PRs created by autonomous system.

---

## Usage Examples

### Example 1: Check System Status
```bash
curl http://localhost:8000/api/autonomous/status | jq
```

### Example 2: Run Analysis Now
```bash
curl http://localhost:8000/api/autonomous/monitor/analyze-now | jq '.summary'
```

### Example 3: Enable Continuous Monitoring
```bash
# Check every hour
curl -X POST "http://localhost:8000/api/autonomous/monitor/start?interval_seconds=3600"

# Check every 30 minutes  
curl -X POST "http://localhost:8000/api/autonomous/monitor/start?interval_seconds=1800"
```

### Example 4: Check PRs Created
```bash
curl http://localhost:8000/api/autonomous/prs/created | jq '.prs'
```

---

## Configuration

### Environment Variables

```bash
# GitHub authentication (for PR creation)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Or use git config
git config user.github_token ghp_xxxxxxxxxxxxxxxxxxxx
```

### Monitoring Behavior

Edit `src/services/autonomous_monitor.py` to customize:

```python
# Threshold for auto-creating critical fix PRs
critical_threshold = 1  # Create PR if 1+ critical issue

# Threshold for auto-creating high-priority PRs  
high_threshold = 3  # Create PR if 3+ high issues

# Monitoring interval (default: 1 hour)
interval_seconds = 3600
```

### Issue Severity Configuration

Adjust detection rules in `src/services/autonomous_monitor.py`:

```python
async def _scan_python_files(self) -> None:
    # Modify severity levels here
    # Change "low" to "medium" for stricter detection
    # Add new patterns to expand detection
```

---

## Workflow: Detecting and Fixing Your Code

### Step 1: Enable Monitoring

```bash
# Start monitoring (will check every hour)
curl -X POST http://localhost:8000/api/autonomous/monitor/start?interval_seconds=3600

# Response:
# {"status": "monitoring_started", "interval_seconds": 3600}
```

### Step 2: Piddy Detects Issues

```
[Autonomous Monitor] 🔍 Analyzing codebase...
[Autonomous Monitor] ⚠️ Found 36 high severity issues!
[Autonomous Monitor] 📝 Creating PR for fixes...
```

### Step 3: PR Created on GitHub

Piddy automatically opens a PR with:
- ✅ Title: `🤖 High Priority Improvements`
- ✅ Detailed description of each issue
- ✅ File paths and line numbers
- ✅ Suggested fixes
- ✅ Review checklist

Example PR Body:
```markdown
## Autonomous Code Quality Improvements

Auto-detected and fixed 3 issues:

### Overly Broad Exception Handler
- **File**: src/utils/api.py:228
- **Severity**: high
- **Issue**: except: catches all exceptions, masking bugs
- **Fix**: Catch HTTPError, ConnectionError, and RequestTimeout specifically

### Print Statement Instead of Logging
- **File**: src/utils/cleanup.py:45
- **Severity**: low

...

**Review Checklist**:
- [ ] Changes are appropriate and correct
- [ ] No unintended side effects
- [ ] Tests pass
- [ ] Code follows conventions
```

### Step 4: You Review and Approve

Review Piddy's changes:
- ✅ Click "Changes" tab to see modifications
- ✅ Check if fixes are appropriate
- ✅ Request modifications if needed
- ✅ Approve and merge when ready

### Step 5: Piddy Learns

- ✅ Monitors your feedback
- ✅ Adjusts severity levels based on your decisions
- ✅ Gets smarter with each cycle

---

## Issue Severity Levels

### 🔴 CRITICAL (Never Auto-fixed)
- Security vulnerabilities
- Data integrity issues
- Core functionality bugs
- **Action**: Piddy creates PR, waits for approval

### 🟠 HIGH (Creates PR after 3+ issues)
- Broad exception handling
- Missing error logging
- Resource leaks
- **Action**: Piddy groups and creates PR

### 🟡 MEDIUM (Informational)
- Code smells
- Anti-patterns
- Performance concerns
- **Action**: Included in PR for awareness

### 🟢 LOW (Grouped only)
- Print statements vs logging
- TODO/FIXME comments
- Minor style issues
- **Action**: Bundled into larger PR

---

## Benefits vs. Manual Code Review

| Aspect | Manual Review | Piddy Autonomous |
|--------|---|---|
| **Detection** | Occasional when you review | Continuous 24/7 |
| **Response Time** | Days/weeks | Minutes |
| **Coverage** | Depends on reviewer focus | All code files |
| **Consistency** | May vary by reviewer | Identical rules |
| **Context** | Human judgment | Configurable rules |
| **PR Review** | Required for everything | Required (human oversight kept) |
| **False Positives** | Low | Possible (you filter) |

---

## How Piddy Maintains Human Oversight

✅ **Piddy Never Direct Commits** - All fixes go through PRs
✅ **You Always Review** - No auto-merge allowed
✅ **You Set Severity** - You decide what's urgent
✅ **You Configure Detection** - Adjust rules as needed
✅ **You Approve Merge** - Final decision is yours
✅ **You Can Disable** - Stop monitoring anytime

Piddy is an **assistant that proposes**, you are the **decision maker that approves**.

---

## Advanced Usage

### Creating Critical Issue PR

```bash
# Force creation of critical PR immediately
curl -X POST http://localhost:8000/api/autonomous/monitor/create-critical-pr \
  -H "Content-Type: application/json" \
  -d '{"title": "Security: SQL Injection Prevention", "issues": [...]}'
```

### Checking PR Status

```bash
# View all created PRs
curl http://localhost:8000/api/autonomous/prs/created

# Response shows each PR with status:
[
  {
    "pr_url": "https://github.com/burchdad/Piddy/pull/42",
    "title": "🤖 High Priority Improvements",
    "created_at": "2026-03-07T19:45:00",
    "status": "open"  # or "merged" / "closed"
  }
]
```

### Monitoring Statistics

```bash
# Get comprehensive monitoring stats
curl http://localhost:8000/api/autonomous/status | jq
```

---

## Troubleshooting

### Issue: GitHub token not configured

**Error**: `GitHub token not configured - cannot create PR`

**Solution**:
```bash
# Option 1: Set environment variable
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Option 2: Configure git
git config user.github_token ghp_xxxxxxxxxxxx
```

### Issue: Monitoring not starting

**Error**: `monitoring_started` but no background activity

**Check**:
```bash
# Verify monitoring is enabled
curl http://localhost:8000/api/autonomous/status | jq '.monitor.enabled'
```

### Issue: False positives in detection

**Error**: Too many low-severity issues being detected

**Solution**: Adjust detection thresholds in `src/services/autonomous_monitor.py`

---

## Future Enhancements (v2.0+)

🔮 **Planned Features**:
- [ ] Machine learning-based severity classification
- [ ] Custom detection rules per project
- [ ] Automatic test generation for fixes
- [ ] Performance regression detection
- [ ] Security vulnerability scanning
- [ ] Type safety improvements (mypy integration)
- [ ] Documentation gap detection
- [ ] Complexity analysis and refactoring suggestions
- [ ] Code duplication removal recommendations
- [ ] Dependency update automation

---

## Summary

Your Piddy now operates as:

1. **🔍 Autonomous Inspector** - Continuously scans code for issues
2. **🔧 Problem Solver** - Generates targeted fixes
3. **📝 Collaborator** - Opens PRs for your review  
4. **📚 Learner** - Improves based on your feedback
5. **🕐 Always On** - Monitors 24/7 in the background

**Key Principle**: Piddy proposes, you approve. All changes go through PR review - machines assist, humans decide.

Ready to let Piddy start improving your codebase? 🚀

```bash
curl -X POST http://localhost:8000/api/autonomous/monitor/start
```
