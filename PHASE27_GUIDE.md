# Phase 27: PR-Based Workflow & Human Review Gates

**Status:** ✅ Complete and Tested  
**Lines of Code:** 800+  
**Core Achievement:** Replace direct commits with safe branch-based development  

## Overview

Phase 27 is the **critical safety upgrade** to Piddy. It transforms the agent from:

```
❌ Agent → Write files → Direct commit to main
           └─ High risk of breakage
```

To:

```
✅ Agent → Create branch → Validate → PR with approval gates
           └─ Safe, reviewable, reversible
```

This is the single most important change for production safety.

## Architecture

### Core Components

```
AutonomousDeveloperWithPRWorkflow
├── BranchManager (git operations)
│   ├── create_branch()
│   ├── commit_changes()
│   ├── push_branch()
│   ├── merge_branch()
│   └── delete_branch()
├── PullRequestManager (PR lifecycle)
│   ├── create_pr()
│   ├── validate_pr()
│   ├── approve_pr()
│   ├── reject_pr()
│   └── merge_pr()
├── PRValidator (validation checks)
│   ├── syntax validation
│   ├── linting
│   ├── import checking
│   ├── type checking
│   ├── security scan
│   └── test execution
└── RiskAssessor (risk calculation)
    └── assess()  → LOW|MEDIUM|HIGH|CRITICAL
```

## Workflow

### Execution Flow

```
1. Agent receives task: "Generate auth endpoint"
   ↓
2. Plan changes locally (no side effects)
   ↓
3. PullRequestManager.create_pr()
   - Generate PR ID: "6d70e6f6"
   - Generate branch: "piddy-6d70e6f6"
   - Assess risk level: MEDIUM
   ↓
4. BranchManager.create_branch()
   - git checkout -b piddy-6d70e6f6
   ↓
5. Apply file changes to branch
   - File operations isolated to branch
   - No impact on main
   ↓
6. BranchManager.commit_changes()
   - git add -A
   - git commit -m "feat: Generate auth endpoint"
   ↓
7. BranchManager.push_branch()
   - git push -u origin piddy-6d70e6f6
   ↓
8. PRValidator runs 6 checks:
   ✓ Syntax validation
   ✓ Linting
   ✓ Import checking
   ✓ Type checking
   ✓ Security scan
   ✓ Test execution
   ↓
9. Risk-based approval gate:
   - LOW risk → auto-merge (no approval needed)
   - MEDIUM risk → need 1 human approval
   - HIGH risk → need 2 approvals
   - CRITICAL risk → need security team approval
   ↓
10a. If auto-mergeable:
   - merge_pr() → merge branch to main
   - Branch cleaned up
   - Task complete
   ↓
10b. If needs approval:
   - PR awaits code review
   - Human or automated reviewer approves
   - Then merge_pr() proceeds
```

## Key Features

### 1. Risk Assessment

```python
risk = RiskAssessor.assess(pr)
```

Risk levels based on:
- **File patterns:** Core files (agent/, main.py) = higher risk
- **Change type:** Deletion = higher risk than addition
- **Scope:** Documentation-only = LOW risk
- **API changes:** Breaking changes = CRITICAL risk

### 2. Approval Gates

```python
ApprovalGate.NONE              # Auto-merge allowed
ApprovalGate.HUMAN_REVIEW      # 1 human approval
ApprovalGate.TWO_APPROVALS     # 2 approvers required
ApprovalGate.SECURITY_TEAM     # Security team review
```

Automatically determined by risk level.

### 3. Validation Checks

Run in parallel (in production):

| Check | Passes | Blocks Merge |
|-------|--------|-------------|
| Syntax validation | ✅ | Yes (required) |
| Linting | ✅ | No (optional) |
| Import checking | ✅ | Yes (required) |
| Type checking | ✅ | No (optional) |
| Security scan | ✅ | Yes (required) |
| Test suite | ✅ | Yes (required) |

### 4. Auto-Merge Logic

```python
can_merge = (
    pr.validation_passed and
    pr.is_approved and 
    len(pr.rejections) == 0
)

if pr.auto_merge_enabled and can_merge:
    merge_pr()  # No human intervention needed
```

**Conditions for auto-merge:**
- All required validation checks passed ✅
- Sufficient approvals received ✅
- No rejections ✅
- Auto-merge enabled (LOW risk) ✅

### 5. Branch Isolation

All changes happen on feature branch:

```
main (protected)
  └─ foo-auth-endpoint (ephemeral)
     ├─ src/auth.py (modified)
     ├─ tests/test_auth.py (created)
     └─ commit history
```

Allows:
- Safe testing before merge
- Multiple PRs in parallel
- Easy rollback (just delete branch)
- CI/CD integration per-branch

## Data Structures

### PullRequest

```python
@dataclass
class PullRequest:
    pr_id: str                           # Unique ID
    branch_name: str                     # "piddy-6d70e6f6"
    title: str                           # Human-readable title
    description: str                     # Why this change
    
    files_changed: List[FileChange]      # What changed
    risk_assessment: ChangeRisk          # LOW/MEDIUM/HIGH/CRITICAL
    
    status: PRStatus                     # Lifecycle state
    validation_checks: List[Check]       # 6 validation results
    validation_passed: bool              # All required checks?
    
    approval_gate: ApprovalGate          # What approval needed?
    approvals: List[str]                 # Who approved
    rejections: List[Dict]               # Who rejected + reason
    
    can_merge: bool                      # Computed property
```

### Approval Gates

```python
class ApprovalGate(Enum):
    NONE = "none"                        # Auto-merge
    HUMAN_REVIEW = "human_review"        # 1 approval
    TWO_APPROVALS = "two_approvals"      # 2 approvals
    SECURITY_TEAM = "security_team"      # Security team
```

## API Usage

### Creating a PR

```python
from src.phase27_pr_workflow import PullRequestManager, FileChange

pr_manager = PullRequestManager()

# Create file changes
changes = [
    FileChange(
        path="src/auth.py",
        change_type="create",
        content_after="def login():\n    pass"
    )
]

# Create PR
success, pr = pr_manager.create_pr(
    title="Add login endpoint",
    description="JWT-based login",
    agent_name="PiddyAgent",
    file_changes=changes
)

print(f"PR created: {pr.pr_id}")
# Output: PR created: 6d70e6f6
```

### Validating a PR

```python
import asyncio

# Run all validation checks
validation_passed, checks = await pr_manager.validate_pr(pr.pr_id)

print(f"Validation: {validation_passed}")
for check in checks:
    print(f"  {check.check_name}: {'✅' if check.passed else '❌'}")
```

### Approving and Merging

```python
# Human approves
pr_manager.approve_pr(pr.pr_id, approver="security-team")

# Auto-merge if ready
success, msg = pr_manager.auto_merge_if_ready(pr.pr_id)
print(msg)
```

## Safety Features

### 1. Branch Protection

```
Protected: main branch
├── Requires PR review
├── Requires passing checks
├── Prevents force push
└── Backup on every merge
```

Feature branches can be reverted instantly:
```bash
git branch -D piddy-6d70e6f6  # Delete branch = rollback
```

### 2. Validation Before Merge

| Stage | Purpose | Blocks |
|-------|---------|--------|
| Syntax | Valid Python | Yes |
| Imports | Dependencies OK | Yes |
| Security | No hardcoded secrets | Yes |
| Tests | Suite passes | Yes |
| Linting | Code style | No |
| Types | Type checking | No |

### 3. Approval Gates

Can't merge without:
- ✅ All required checks passed
- ✅ Sufficient approvals (based on risk)
- ✅ No rejections

### 4. Immutable History

```
PR #6d70e6f6
├─ Created: 2026-03-06 04:15
├─ Validation: PASSED (6 checks)
├─ Approvals: [user@example.com]
├─ Merged: 2026-03-06 04:16
└─ Merge commit: abc123def
```

Each PR creates permanent record.

## Metrics & Monitoring

### PR Metrics

```python
pr_summary = pr_manager.get_pr_summary(pr_id)

{
    'pr_id': '6d70e6f6',
    'status': 'validation_passed',
    'risk_level': 'medium',
    'files_changed': 1,
    'additions': 4,
    'deletions': 0,
    'validation_checks': 6,
    'validation_passed': True,
    'approvals': 1,
    'rejections': 0,
    'can_merge': True
}
```

### Tracking Open PRs

```python
open_prs = pr_manager.list_open_prs()
for pr in open_prs:
    print(f"{pr.pr_id}: {pr.status.value} - {pr.risk_assessment.value}")
```

## Comparison: Before vs After

### Before (Direct Commits)

```
❌ Agent writes files directly
❌ No validation before commit
❌ No branch isolation
❌ Impossible to review changes
❌ No rollback if something breaks
❌ No approval tracking
```

**Result:** One bad commit breaks entire repo

### After (PR-Based Workflow)

```
✅ Agent creates feature branch
✅ 6 validation checks run automatically
✅ Changes isolated to branch
✅ PR shows exactly what changed
✅ Easy rollback (delete branch)
✅ Full approval audit trail
```

**Result:** Safe, reviewable, reversible development

## Integration with Phase 18-26

### Before Phase 27

```
Phase 18 (Read/Analyze)
    ↓
Phase 20 (Validate)
    ↓
Phase 20's AtomicCommitHandler
    └─ Commits directly to main ❌
```

### After Phase 27

```
Phase 18 (Read/Analyze)
    ↓
Phase 27 (Plan PR)
    ├─ Create branch
    ├─ Apply changes
    ├─ Run validation
    └─ Create PR ✅
    ↓
Phase 26 (Governance)
    ├─ Check policies
    ├─ Verify approvals
    └─ Merge PR
```

## Production Deployment

### Requirements

- Git repository with remote
- GitHub/GitLab/Gitea API access
- CI/CD pipeline for validation checks
- Approval workflow configured

### Configuration

```python
pr_manager = PullRequestManager(
    repo_root='/path/to/repo',
    approval_requirement=ApprovalGate.HUMAN_REVIEW
)
```

### Testing Locally

```bash
cd /workspaces/Piddy

# Run Phase 27 demo
python -m src.phase27_pr_workflow

# Check git status
git branch -a
git log --oneline | head -5
```

## Next Steps

Phase 27 is the **foundation** for:

- **Phase 28:** Persistent graph database (eliminates per-request rebuild)
- **Phase 29:** Sandboxed execution (runs tests in containers)
- **Phase 30:** Multi-agent protocol (agents call each other)
- **Phase 31:** Security & compliance (secrets, audit logs, permissions)

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Workflow | Direct commits | PR + review gates |
| Safety | Low | High |
| Auditability | Poor | Complete |
| Rollback | Manual | Instant (delete branch) |
| Risk | Production breaks | Managed |
| Approval | None | Configurable |
| Auto-merge | N/A | For LOW risk |

**Phase 27 transforms Piddy from a prototype to a defensible system.**
