# 🚨 PRODUCTION TRUST LAYER - CRITICAL ROADMAP

**Date**: March 18, 2026  
**Status**: EXECUTION AUTHORITY EXISTS, TRUST LAYER MISSING  
**Risk Level**: MEDIUM - Powerful but not yet enterprise-safe

---

## 🧠 Current State Analysis

### What We Built (Correctly)
✅ Execution - Real code, tests, commits, PRs  
✅ Decision System - 12 agents, consensus, reputation weighting  
✅ Persistence - Missions stored, KB grows  
✅ Resilience - Offline queue, sync, fallback DB  

### What We're Missing (CRITICAL)

#### 1. ❌ TRUE Approval Enforcement
**Reality Check**: Voting ≠ Approval
```
Current Flow (Unsafe):
Slack → Nova → Execute → Commit → Push  
(voting happens but can't actually STOP execution)

Required Flow (Safe):
Slack → Plan → APPROVAL GATE → Execute → Commit → Push
                    ↑ BLOCKING
         (no execution without human sign-off)
```

**Enterprise Impact**: 
- Can't claim "approval workflow" without blocking mechanism
- Accidental commits can happen
- Compliance claims are weak

#### 2. ❌ Provable Sandbox Isolation
**Questions Enterprises Will Ask**:
- Can Nova access host filesystem? 
- Can it access network?
- Can it leak secrets?
- Where's the proof?

**Currently Missing**:
- Strict container policies
- Read-only mounts documentation
- Network restrictions
- Secrets isolation verification
- "Proof of Isolation" document

#### 3. ❌ Scope Control
**Current Risk**: Nova can modify ANY repo, ANY files, unlimited scope

**Missing Controls**:
- Repo allowlist (only certain repos allowed)
- Path restrictions (only certain directories)
- Operation limits (max files changed)
- Execution time limits
- Resource caps

---

## 🎯 PRIORITY ROADMAP (Trust Layer Only)

### 🥇 PHASE 1: Approval Enforcement (CRITICAL)
**Timeline**: 2-4 hours  
**Impact**: Converts voting → hard enforcement gate

#### What to Build
```python
# Add to nova_coordinator.py

class ApprovalGate:
    """Hard blocking approval gate - no execution without sign-off"""
    
    async def check_approval(self, mission_id: str, risk_level: str):
        """
        Blocks execution until:
        1. Plan is created
        2. Stored in database
        3. Human approves OR auto-approved (low risk)
        """
        plan = await self.get_plan(mission_id)
        
        if risk_level == "HIGH":
            # HARD BLOCK - requires manual approval
            approval = await self.wait_for_approval(mission_id)
            if not approval.approved:
                raise ApprovalDenied(f"Mission rejected: {approval.reason}")
        
        return True
```

#### Slack UX Changes
```
Current:
❌ Plan: Medium risk → [Executing...]

New:
✅ PLAN SUBMITTED
   Files: 3, Risk: MEDIUM
   [Approve] [Reject]
   
(execution blocked, waiting...)

After approval:
✅ APPROVED - Executing...
```

#### Database Changes
```sql
-- Mission approval tracking
CREATE TABLE mission_approvals (
    mission_id UUID PRIMARY KEY,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'AUTO_APPROVED'),
    requested_by VARCHAR,
    approved_by VARCHAR,
    approval_reason TEXT,
    auto_approved_threshold FLOAT,
    created_at TIMESTAMP,
    approved_at TIMESTAMP
);
```

### 🥈 PHASE 2: Execution Modes
**Timeline**: 2-3 hours  
**Impact**: Allows enterprise to configure safety level

#### Four Execution Modes
```python
class ExecutionMode(Enum):
    SAFE = "safe"          # Default: All high-risk blocked
    AUTO = "auto"          # Dev: Auto-approve low-risk  
    PR_ONLY = "pr_only"    # No direct push, PR only
    DRY_RUN = "dry_run"    # Show consequences, no execution

# Usage in Slack
/nova --mode=safe create unit tests
/nova --mode=pr-only optimize database
/nova --mode=dry-run refactor auth

# Per-mission enforcement
if execution_mode == "SAFE":
    await approval_gate.block_until_approved()
elif execution_mode == "AUTO":
    if risk_level < THRESHOLD:
        auto_approve()
    else:
        await approval_gate.block_until_approved()
elif execution_mode == "PR_ONLY":
    create_pr_only()  # No direct push to main
elif execution_mode == "DRY_RUN":
    show_simulation()  # No actual execution
```

### 🥉 PHASE 3: Sandbox Hardening
**Timeline**: 3-4 hours  
**Impact**: Provable isolation for enterprises

#### Proof-of-Isolation Document
Create `SANDBOX_SECURITY.md`:
```markdown
# Sandbox Security & Isolation Proof

## Docker Container Isolation

### Network Isolation
✅ Outbound internet: BLOCKED by default (--network=none)
✅ Optional toggle: Can enable for package downloads
✅ Ports exposed: Only internal communication ports
✅ No external DNS: Uses local resolver only

### Filesystem Isolation
✅ Read-only mounts: /etc, /usr, /bin, /lib (immutable)
✅ Temp workspace: /tmp/nova_work (ephemeral, auto-cleanup)
✅ No host access: Cannot access /, /home, /root
✅ Secrets: Mounted via tmpfs, cleared after execution

### Resource Limits
✅ CPU: 2 cores max
✅ Memory: 4GB max
✅ Disk: 10GB max
✅ Runtime: 10 minutes max (configurable)

### Secrets Protection
✅ Injected as environment variables only
✅ Never written to filesystem
✅ Cleared after execution
✅ Not logged or persisted
```

#### Implementation
```python
# Docker policy enforcement
DOCKER_POLICY = {
    "network_mode": "none",  # No network by default
    "read_only_rootfs": True,
    "cap_drop": ["ALL"],
    "cap_add": ["CHOWN", "DAC_OVERRIDE"],  # Minimal needed
    "security_opt": ["no-new-privileges:true"],
    "tmpfs": {
        "/tmp": "size=512M,noexec,nosuid,nodev",
        "/run": "size=64M,noexec,nosuid,nodev"
    },
    "volumes": {
        "/etc/ssl/certs": {"bind": "/etc/ssl/certs", "mode": "ro"},
    },
    "cpu_quota": 200000,  # 2 cores
    "memory": "4g",
    "pids_limit": 100,
}
```

### 🏅 PHASE 4: Scope Control
**Timeline**: 2-3 hours  
**Impact**: Prevents accidental/malicious modifications

#### Repo & Path Allowlist
```python
ALLOWED_REPOS = [
    "burchdad/Piddy",
    "burchdad/piddy-knowledge-base",
]

ALLOWED_PATHS = {
    "burchdad/Piddy": [
        "src/**",
        "tests/**",
        "frontend/**",
        "docs/**",
        # NOT: .git, .secrets, config files
    ],
}

MAX_OPERATION_LIMITS = {
    "max_files_changed": 50,
    "max_lines_added": 5000,
    "max_lines_deleted": 2000,
    "max_execution_time_seconds": 600,
    "max_api_calls": 100,
}

# Enforcement
async def validate_scope(mission: Mission, risk_level: str):
    # Verify repo is allowed
    if mission.repo not in ALLOWED_REPOS:
        raise ScopeViolation(f"Repo {mission.repo} not in allowlist")
    
    # Verify paths are allowed
    for file in mission.files:
        if not is_path_allowed(file, mission.repo):
            raise ScopeViolation(f"Path {file} not allowed")
    
    # Verify limits
    if file_count > MAX_OPERATION_LIMITS["max_files_changed"]:
        raise ScopeViolation("Too many files changed")
```

---

## 🔥 Positioning Shift (CRITICAL)

### Don't Say
❌ "AI that builds stuff"  
❌ "Autonomous developer"  
❌ "Production ready"

### DO Say
✅ **"AI executing engineering work under enterprise governance"**  
✅ **"Governed, auditable code execution system"**  
✅ **"Enterprise-safe autonomous agent"**

### The Difference
```
Risky: "Watch it code without supervision"
Safe:  "Watch it code, with built-in gates, isolation, and approvals"
```

---

## 📊 Trust Layer Completion Checklist

### Phase 1: Approval Enforcement
- [ ] Add ApprovalGate class
- [ ] Database schema: mission_approvals table
- [ ] Slack approval UI (Approve/Reject buttons)
- [ ] Blocking gate before execution
- [ ] Test: High-risk mission requires approval
- [ ] Test: Low-risk mission auto-approves (if enabled)
- [ ] Audit: Log all approval decisions

### Phase 2: Execution Modes
- [ ] Enum: SAFE, AUTO, PR_ONLY, DRY_RUN
- [ ] Slack command parsing: --mode=safe
- [ ] Mode selection dialog
- [ ] Mode-specific behavior
- [ ] Documentation per mode

### Phase 3: Sandbox Hardening
- [ ] SANDBOX_SECURITY.md created
- [ ] Docker policy constants
- [ ] Container enforcement code
- [ ] Test: Verify isolation
- [ ] Test: Secrets don't leak
- [ ] Test: Network blocked
- [ ] Proof-of-isolation audit

### Phase 4: Scope Control
- [ ] ALLOWED_REPOS allowlist
- [ ] Path restrictions per repo
- [ ] Operation limits enforced
- [ ] Validation before execution
- [ ] Scope violation handling

---

## 🚀 Timeline to Enterprise-Ready

**Phase 1 (Approval)**: 2-4 hours → Hard execution gating  
**Phase 2 (Modes)**: 2-3 hours → User control + safety  
**Phase 3 (Sandbox)**: 3-4 hours → Provable isolation  
**Phase 4 (Scope)**: 2-3 hours → Prevent runaway modifications  

**Total**: ~10-14 hours of focused work

**Result**: From "powerful but risky" → **"powerful AND safe"**

---

## 💡 Why This Matters

**Right now**:
- Developers: "This is insane!" ← True, it works
- Enterprises: "This is risky" ← Also true, no gates

**After Trust Layer**:
- Developers: "This is insane AND safe"
- Enterprises: "We can deploy this"

---

## 🧠 Why NOT to Skip This

Skipping this means:
- Can't claim "production ready"
- Won't pass security reviews
- Enterprises won't trust it
- Scope creep risks (accidental commits)
- No approval audit trail

Building this means:
- Provably safe execution
- Enterprise compliance
- Auditable decisions
- Scoped modifications
- **Genuinely sellable platform**

---

## Next Step

**Recommendation**: Start with Phase 1 (Approval Enforcement)

Why:
1. It's the most critical (makes execution actually controlled)
2. It's 2-4 hours (quick win)
3. It unblocks enterprise conversations
4. Everything else builds on it
5. Slack UI is already set up

---

**Decision**: Should we build the Trust Layer now?

If yes: I'll implement Phase 1 (Approval Enforcement) immediately
If no: We stay in the "advanced experimental system" category

Your call.
