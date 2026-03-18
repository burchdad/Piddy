"""
Approval Gate - Hard execution blocking for enterprise safety

This module implements the critical approval enforcement layer that prevents
execution of high-risk missions without explicit human sign-off.

Key: Voting ≠ Approval. Approval must be able to BLOCK execution.
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval states"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"


class RiskLevel(Enum):
    """Mission risk levels"""
    LOW = "low"          # Auto-approve threshold: < 20% files, < 1000 lines, < 5 min execution
    MEDIUM = "medium"    # Requires approval if execution_mode=SAFE
    HIGH = "high"        # Always requires explicit approval


@dataclass
class ApprovalRequest:
    """Request for mission approval"""
    mission_id: str
    task_description: str
    risk_level: RiskLevel
    requester_id: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    estimated_execution_time_sec: int
    auto_approve_threshold: float = 0.7  # 70% confidence to auto-approve
    requested_at: str = None
    
    def __post_init__(self):
        if self.requested_at is None:
            self.requested_at = datetime.utcnow().isoformat()


@dataclass
class ApprovalDecision:
    """Decision on a mission approval"""
    mission_id: str
    status: ApprovalStatus
    approved_by: Optional[str] = None
    approval_reason: str = ""
    approved_at: Optional[str] = None
    expires_at: Optional[str] = None
    
    def __post_init__(self):
        if self.approved_at is None and self.status != ApprovalStatus.PENDING:
            self.approved_at = datetime.utcnow().isoformat()


class ApprovalGate:
    """
    Enforces hard execution gates based on approval status.
    
    This is the critical trust layer that prevents runaway execution.
    """
    
    def __init__(self, persistence_layer):
        """
        Initialize approval gate
        
        Args:
            persistence_layer: Database layer for storing approvals
        """
        self.db = persistence_layer
        logger.info("✅ Approval Gate initialized - HARD BLOCKING ENABLED")
    
    async def check_and_enforce(
        self,
        mission_id: str,
        task: str,
        risk_level: RiskLevel,
        requester_id: str,
        files_changed: List[str],
        lines_added: int,
        lines_deleted: int,
        estimated_execution_time_sec: int,
        execution_mode: str = "SAFE"
    ) -> bool:
        """
        Check if mission can execute. BLOCKS HIGH-RISK missions.
        
        Args:
            mission_id: Mission identifier
            task: Task description
            risk_level: Assessed risk level
            requester_id: Who requested the mission
            files_changed: Files that will be modified
            lines_added: Total lines added
            lines_deleted: Total lines deleted
            estimated_execution_time_sec: Execution time estimate
            execution_mode: SAFE, AUTO, PR_ONLY, DRY_RUN
        
        Returns:
            True if mission can execute, False if blocked
        
        Raises:
            ApprovalRequired: If mission requires approval and hasn't received it
            ApprovalDenied: If mission was explicitly rejected
        """
        # Create approval request
        approval_req = ApprovalRequest(
            mission_id=mission_id,
            task_description=task,
            risk_level=risk_level,
            requester_id=requester_id,
            files_changed=files_changed,
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            estimated_execution_time_sec=estimated_execution_time_sec
        )
        
        logger.info(f"🚨 Approval Gate: Checking mission {mission_id}")
        logger.info(f"   Risk Level: {risk_level.value}")
        logger.info(f"   Execution Mode: {execution_mode}")
        logger.info(f"   Files Changed: {len(files_changed)}")
        logger.info(f"   Lines: +{lines_added}/-{lines_deleted}")
        
        # Store the request
        await self._store_approval_request(approval_req)
        
        # Determine if approval is required
        requires_approval = self._requires_approval(
            risk_level=risk_level,
            execution_mode=execution_mode,
            files_changed=len(files_changed),
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            execution_time_sec=estimated_execution_time_sec
        )
        
        if not requires_approval:
            logger.info(f"✅ Auto-approved: {mission_id}")
            decision = ApprovalDecision(
                mission_id=mission_id,
                status=ApprovalStatus.AUTO_APPROVED,
                approved_by="system",
                approval_reason="Low-risk mission, auto-approved"
            )
            await self._store_approval_decision(decision)
            return True
        
        # HIGH-RISK: HARD BLOCK - Wait for human approval
        logger.warning(f"⛔ BLOCKING: High-risk mission {mission_id} requires explicit approval")
        logger.warning(f"   Waiting for human approval via Slack...")
        
        # Wait for approval decision (this is the hard gate)
        decision = await self._wait_for_approval(mission_id, timeout_seconds=3600)
        
        if decision.status == ApprovalStatus.APPROVED:
            logger.info(f"✅ APPROVED by {decision.approved_by}: {mission_id}")
            return True
        elif decision.status == ApprovalStatus.AUTO_APPROVED:
            logger.info(f"✅ Auto-approved: {mission_id}")
            return True
        elif decision.status == ApprovalStatus.REJECTED:
            logger.error(f"❌ REJECTED by {decision.approved_by}: {mission_id}")
            logger.error(f"   Reason: {decision.approval_reason}")
            raise ApprovalDenied(f"Mission rejected: {decision.approval_reason}")
        else:
            logger.error(f"❌ Approval expired: {mission_id}")
            raise ApprovalExpired(f"Approval not received within timeout")
    
    def _requires_approval(
        self,
        risk_level: RiskLevel,
        execution_mode: str,
        files_changed: int,
        lines_added: int,
        lines_deleted: int,
        execution_time_sec: int
    ) -> bool:
        """
        Determine if this mission requires human approval
        
        Rules:
        - SAFE mode: Block anything MEDIUM or HIGH risk
        - AUTO mode: Auto-approve LOW risk, block MEDIUM/HIGH
        - PR_ONLY: Always create PR, no direct execution
        - DRY_RUN: No execution, just show consequences
        """
        
        # DRY_RUN never needs approval (doesn't execute)
        if execution_mode == "DRY_RUN":
            return False
        
        # PR_ONLY mode always requires review (creates PR instead of direct push)
        if execution_mode == "PR_ONLY":
            return True
        
        # SAFE mode: Require approval for anything risky
        if execution_mode == "SAFE":
            return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
        
        # AUTO mode: Only auto-approve LOW risk
        if execution_mode == "AUTO":
            if risk_level == RiskLevel.LOW:
                # Additional checks for "low" risk
                return (files_changed > 50 or
                        lines_added > 5000 or
                        lines_deleted > 2000 or
                        execution_time_sec > 600)
            else:
                return True
        
        # Default: SAFE
        return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
    
    async def _store_approval_request(self, request: ApprovalRequest) -> None:
        """Store approval request in database"""
        try:
            self.db.execute("""
                INSERT INTO mission_approvals 
                (mission_id, task_description, risk_level, requester_id, 
                 files_changed, lines_added, lines_deleted, 
                 estimated_execution_time_sec, status, requested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.mission_id,
                request.task_description,
                request.risk_level.value,
                request.requester_id,
                json.dumps(request.files_changed),
                request.lines_added,
                request.lines_deleted,
                request.estimated_execution_time_sec,
                ApprovalStatus.PENDING.value,
                request.requested_at
            ))
            logger.info(f"✅ Stored approval request: {request.mission_id}")
        except Exception as e:
            logger.error(f"❌ Failed to store approval request: {e}")
            raise
    
    async def _store_approval_decision(self, decision: ApprovalDecision) -> None:
        """Store approval decision in database"""
        try:
            self.db.execute("""
                UPDATE mission_approvals
                SET status = ?, approved_by = ?, approval_reason = ?, approved_at = ?
                WHERE mission_id = ?
            """, (
                decision.status.value,
                decision.approved_by,
                decision.approval_reason,
                decision.approved_at,
                decision.mission_id
            ))
            logger.info(f"✅ Stored approval decision: {decision.mission_id} -> {decision.status.value}")
        except Exception as e:
            logger.error(f"❌ Failed to store approval decision: {e}")
            raise
    
    async def _wait_for_approval(self, mission_id: str, timeout_seconds: int = 3600):
        """
        Wait for human approval (blocking call)
        
        In production, this would:
        1. Send Slack notification with approval buttons
        2. Wait for user response
        3. Store decision when received
        
        For now, returns mock decision
        """
        logger.info(f"⏳ Waiting for approval ({timeout_seconds}s timeout): {mission_id}")
        
        # TODO: Integrate with Slack notification system
        # For now, wait a bit then check database
        import asyncio
        import time
        
        start = time.time()
        while time.time() - start < timeout_seconds:
            # Check if decision was made
            try:
                result = self.db.execute("""
                    SELECT status, approved_by, approval_reason, approved_at
                    FROM mission_approvals
                    WHERE mission_id = ?
                """, (mission_id,)).fetchone()
                
                if result and result[0] != ApprovalStatus.PENDING.value:
                    return ApprovalDecision(
                        mission_id=mission_id,
                        status=ApprovalStatus(result[0]),
                        approved_by=result[1],
                        approval_reason=result[2],
                        approved_at=result[3]
                    )
            except Exception as e:
                logger.warning(f"Error checking approval status: {e}")
            
            await asyncio.sleep(1)  # Check every second
        
        # Timeout - return expired
        return ApprovalDecision(
            mission_id=mission_id,
            status=ApprovalStatus.EXPIRED,
            approval_reason="Timeout waiting for approval"
        )
    
    async def approve_mission(
        self,
        mission_id: str,
        approved_by: str,
        reason: str = "Approved"
    ) -> None:
        """
        Explicitly approve a mission (called by Slack UI)
        
        Args:
            mission_id: Mission to approve
            approved_by: Who approved it (user ID)
            reason: Approval reason
        """
        logger.info(f"✅ APPROVING mission {mission_id} by {approved_by}")
        decision = ApprovalDecision(
            mission_id=mission_id,
            status=ApprovalStatus.APPROVED,
            approved_by=approved_by,
            approval_reason=reason
        )
        await self._store_approval_decision(decision)
    
    async def reject_mission(
        self,
        mission_id: str,
        rejected_by: str,
        reason: str
    ) -> None:
        """
        Explicitly reject a mission (called by Slack UI)
        
        Args:
            mission_id: Mission to reject
            rejected_by: Who rejected it (user ID)
            reason: Rejection reason
        """
        logger.info(f"❌ REJECTING mission {mission_id} by {rejected_by}")
        logger.info(f"   Reason: {reason}")
        decision = ApprovalDecision(
            mission_id=mission_id,
            status=ApprovalStatus.REJECTED,
            approved_by=rejected_by,
            approval_reason=reason
        )
        await self._store_approval_decision(decision)
    
    async def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all missions awaiting approval"""
        try:
            results = self.db.execute("""
                SELECT mission_id, task_description, risk_level, requester_id,
                       files_changed, lines_added, lines_deleted, 
                       estimated_execution_time_sec, requested_at
                FROM mission_approvals
                WHERE status = ?
                ORDER BY requested_at DESC
            """, (ApprovalStatus.PENDING.value,)).fetchall()
            
            approvals = []
            for row in results:
                approvals.append(ApprovalRequest(
                    mission_id=row[0],
                    task_description=row[1],
                    risk_level=RiskLevel(row[2]),
                    requester_id=row[3],
                    files_changed=json.loads(row[4]),
                    lines_added=row[5],
                    lines_deleted=row[6],
                    estimated_execution_time_sec=row[7],
                    requested_at=row[8]
                ))
            
            return approvals
        except Exception as e:
            logger.error(f"Error fetching pending approvals: {e}")
            return []


# Custom exceptions for approval system
class ApprovalException(Exception):
    """Base approval exception"""
    pass


class ApprovalRequired(ApprovalException):
    """Mission requires approval before execution"""
    pass


class ApprovalDenied(ApprovalException):
    """Mission was explicitly rejected"""
    pass


class ApprovalExpired(ApprovalException):
    """Approval request timed out"""
    pass
