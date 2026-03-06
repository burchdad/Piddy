"""
Phase 27: PR-Based Workflow & Human Review Gates

Replace direct commits with branch-based development:
- Create feature branches for all changes
- Automatic PR generation with change summaries
- CI/CD integration for validation
- Optional human approval gates
- Safe auto-merge for low-risk changes
- Full rollback and branch cleanup

This is the single most important change for production safety.
"""

import asyncio
import subprocess
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)


class ChangeRisk(Enum):
    """Risk assessment for changes"""
    LOW = "low"              # Docs, comments, tests only
    MEDIUM = "medium"        # New isolated features
    HIGH = "high"            # Core logic changes
    CRITICAL = "critical"    # Breaking API changes


class PRStatus(Enum):
    """Status of a pull request"""
    CREATED = "created"
    VALIDATION_RUNNING = "validation_running"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    CLOSED = "closed"


class ApprovalGate(Enum):
    """Approval requirements"""
    NONE = "none"                    # Auto-merge allowed
    HUMAN_REVIEW = "human_review"    # Requires human approval
    TWO_APPROVALS = "two_approvals"  # Requires 2 approvers
    SECURITY_TEAM = "security_team"  # Needs security review


@dataclass
class FileChange:
    """Individual file change in a PR"""
    path: str
    change_type: str  # 'create', 'modify', 'delete'
    content_before: Optional[str] = None
    content_after: Optional[str] = None
    lines_added: int = 0
    lines_removed: int = 0

    def get_diff(self) -> str:
        """Generate unified diff"""
        before = (self.content_before or "").splitlines(keepends=True)
        after = (self.content_after or "").splitlines(keepends=True)
        
        # Simple diff representation
        diff = f"--- {self.path}\n+++ {self.path}\n"
        if self.change_type == "delete":
            diff += f"Deleted: {len(before)} lines\n"
        elif self.change_type == "create":
            diff += f"Created: {len(after)} lines\n"
        else:
            diff += f"Modified: -{len(before)} lines, +{len(after)} lines\n"
        return diff


@dataclass
class ValidationCheck:
    """Result of a validation check"""
    check_name: str
    passed: bool
    message: str
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    required: bool = True  # If False, failure doesn't block merge

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PullRequest:
    """Represents a GitHub-style PR"""
    pr_id: str
    branch_name: str
    title: str
    description: str
    author_agent: str
    
    # Changes
    files_changed: List[FileChange] = field(default_factory=list)
    risk_assessment: ChangeRisk = ChangeRisk.MEDIUM
    
    # Status
    status: PRStatus = PRStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    
    # Validation
    validation_checks: List[ValidationCheck] = field(default_factory=list)
    validation_passed: bool = False
    
    # Approval
    approval_gate: ApprovalGate = ApprovalGate.HUMAN_REVIEW
    approvals: List[str] = field(default_factory=list)
    rejections: List[Dict[str, str]] = field(default_factory=list)
    
    # Merge info
    auto_merge_enabled: bool = False
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None

    @property
    def is_approved(self) -> bool:
        """Check if PR meets approval requirements"""
        if self.approval_gate == ApprovalGate.NONE:
            return True
        if self.approval_gate == ApprovalGate.HUMAN_REVIEW:
            return len(self.approvals) >= 1
        if self.approval_gate == ApprovalGate.TWO_APPROVALS:
            return len(self.approvals) >= 2
        if self.approval_gate == ApprovalGate.SECURITY_TEAM:
            # In real system, this would check specific security team member
            return len(self.approvals) >= 1
        return False

    @property
    def can_merge(self) -> bool:
        """Check if PR can be merged"""
        return (
            self.status == PRStatus.APPROVED and
            self.validation_passed and
            self.is_approved and
            len(self.rejections) == 0
        )

    def to_dict(self) -> Dict:
        return {
            'pr_id': self.pr_id,
            'branch_name': self.branch_name,
            'title': self.title,
            'description': self.description,
            'author': self.author_agent,
            'status': self.status.value,
            'risk_level': self.risk_assessment.value,
            'files_changed': len(self.files_changed),
            'validation_passed': self.validation_passed,
            'approvals': len(self.approvals),
            'can_merge': self.can_merge,
            'created_at': self.created_at.isoformat()
        }


class BranchManager:
    """Manage git branches"""

    def __init__(self, repo_root: str = '/workspaces/Piddy'):
        self.repo_root = Path(repo_root)

    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Create a new branch from main"""
        try:
            # Ensure we're on main
            subprocess.run(
                ['git', 'checkout', 'main'],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            
            # Create and checkout new branch
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            
            return True, f"Branch '{branch_name}' created successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to create branch: {e.stderr.decode()}"

    def commit_changes(self, message: str) -> Tuple[bool, str]:
        """Stage and commit all changes"""
        try:
            # Stage all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            
            # Commit with message
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            
            return True, "Changes committed successfully"
        except subprocess.CalledProcessError as e:
            error = e.stderr.decode()
            if 'nothing to commit' in error:
                return True, "No changes to commit"
            return False, f"Commit failed: {error}"

    def push_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Push branch to remote"""
        try:
            subprocess.run(
                ['git', 'push', '-u', 'origin', branch_name],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            return True, f"Branch pushed to origin/{branch_name}"
        except subprocess.CalledProcessError as e:
            return False, f"Push failed: {e.stderr.decode()}"

    def merge_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Merge branch into main"""
        try:
            # Checkout main
            subprocess.run(
                ['git', 'checkout', 'main'],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            
            # Merge branch
            result = subprocess.run(
                ['git', 'merge', branch_name],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            
            return True, "Branch merged successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Merge failed: {e.stderr.decode()}"


class RiskAssessor:
    """Assess risk level of changes"""

    @staticmethod
    def assess(pr: PullRequest) -> ChangeRisk:
        """Assess overall risk of PR"""
        risk = ChangeRisk.MEDIUM
        
        # Increase risk for core files
        core_patterns = ['agent/', 'core.py', 'main.py']
        for file_change in pr.files_changed:
            if any(pattern in file_change.path for pattern in core_patterns):
                if risk != ChangeRisk.CRITICAL:
                    risk = ChangeRisk.HIGH
        
        # Reduce risk for documentation/test-only changes
        test_patterns = ['test_', 'tests/', '.md', 'docs/']
        if all(any(pattern in fc.path for pattern in test_patterns) for fc in pr.files_changed):
            risk = ChangeRisk.LOW
        
        return risk


class PullRequestManager:
    """Orchestrate PR-based workflow"""

    def __init__(self, repo_root: str = '/workspaces/Piddy'):
        self.repo_root = Path(repo_root)
        self.branch_manager = BranchManager(repo_root)
        self.risk_assessor = RiskAssessor()
        
        self.pull_requests: Dict[str, PullRequest] = {}
        self.pr_history: List[PullRequest] = []

    def create_pr(
        self,
        title: str,
        description: str,
        agent_name: str,
        file_changes: List[FileChange]
    ) -> Tuple[bool, PullRequest]:
        """Create a new PR for proposed changes"""
        
        # Generate PR ID and branch name
        pr_id = hashlib.md5(f"{title}-{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        branch_name = f"piddy-{pr_id}"
        
        # Assess risk
        pr = PullRequest(
            pr_id=pr_id,
            branch_name=branch_name,
            title=title,
            description=description,
            author_agent=agent_name,
            files_changed=file_changes
        )
        
        pr.risk_assessment = self.risk_assessor.assess(pr)
        
        # Set approval requirements based on risk
        if pr.risk_assessment == ChangeRisk.LOW:
            pr.approval_gate = ApprovalGate.NONE
            pr.auto_merge_enabled = True
        elif pr.risk_assessment == ChangeRisk.MEDIUM:
            pr.approval_gate = ApprovalGate.HUMAN_REVIEW
        elif pr.risk_assessment == ChangeRisk.HIGH:
            pr.approval_gate = ApprovalGate.TWO_APPROVALS
        else:  # CRITICAL
            pr.approval_gate = ApprovalGate.SECURITY_TEAM
        
        self.pull_requests[pr_id] = pr
        return True, pr

    def get_pr(self, pr_id: str) -> Optional[PullRequest]:
        """Get PR by ID"""
        return self.pull_requests.get(pr_id)

    def list_open_prs(self) -> List[PullRequest]:
        """List all open PRs"""
        return [
            pr for pr in self.pull_requests.values()
            if pr.status not in [PRStatus.MERGED, PRStatus.CLOSED]
        ]

    def get_pr_summary(self, pr_id: str) -> Dict[str, Any]:
        """Get summary of PR status"""
        pr = self.get_pr(pr_id)
        if not pr:
            return {}
        
        return {
            'pr_id': pr.pr_id,
            'title': pr.title,
            'status': pr.status.value,
            'risk_level': pr.risk_assessment.value,
            'files_changed': len(pr.files_changed),
            'approval_gate': pr.approval_gate.value,
            'can_merge': pr.can_merge,
            'created_at': pr.created_at.isoformat()
        }


if __name__ == "__main__":
    # Demo
    mgr = PullRequestManager()
    print("Phase 27: PR-Based Workflow - Ready")
