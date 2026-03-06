"""
Approval & Notification System
Manages approvals and notifications for high-risk missions

Supports:
- Phase 40: High-risk mission approval
- Phase 42: Auto-merge decision notifications
- Phase 50+: Agent coordination
"""

from typing import Optional, Dict, Callable, List
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime, timedelta


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Represents a request for approval"""
    
    mission_id: str                  # Unique mission ID
    mission_name: str                # Readable mission name
    mission_type: str                # Type of mission
    description: str                 # What will be done
    prediction: Dict                 # Predicted outcomes
    confidence: float                # How confident (0.0-1.0)
    risk_level: str                  # "low", "medium", "high"
    requires_approval: bool          # Whether approval is required
    expires_in: int = 3600           # Seconds until expiration
    
    # Additional context
    impact_summary: str = ""         # Summary of changes
    files_affected: List[str] = field(default_factory=list)
    estimated_duration: int = 300    # Seconds
    created_at: Optional[str] = None
    approved_by: Optional[str] = None
    approval_time: Optional[str] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    
    def is_expired(self) -> bool:
        """Check if approval request has expired"""
        if not self.created_at:
            return False
        
        created = datetime.fromisoformat(self.created_at)
        expiry = created + timedelta(seconds=self.expires_in)
        return datetime.utcnow() > expiry


@dataclass
class ApprovalResponse:
    """Response to an approval request"""
    
    mission_id: str
    status: ApprovalStatus
    approved_by: str                 # Who approved
    message: str                     # Additional message
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    conditions: Dict = field(default_factory=dict)  # Conditions for approval


class ApprovalManager:
    """Manage approvals for high-risk missions"""
    
    def __init__(self):
        """Initialize approval manager"""
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_responses: Dict[str, ApprovalResponse] = {}
        self.notification_handlers: List[Callable] = []
        self.approval_handlers: List[Callable] = []
    
    def register_notification_handler(self, handler: Callable) -> None:
        """Register handler for notifications (e.g., Slack, email)"""
        self.notification_handlers.append(handler)
    
    def register_approval_handler(self, handler: Callable) -> None:
        """Register handler for approval decisions"""
        self.approval_handlers.append(handler)
    
    async def request_approval(self, request: ApprovalRequest) -> bool:
        """Request approval from humans"""
        
        # Set timestamps
        request.created_at = datetime.utcnow().isoformat()
        request.status = ApprovalStatus.PENDING
        
        # Store request
        self.pending_approvals[request.mission_id] = request
        
        # Notify all handlers
        await self._notify_approvers(request)
        
        # Wait for response (with timeout)
        try:
            response = await asyncio.wait_for(
                self._wait_for_approval(request.mission_id),
                timeout=request.expires_in
            )
            return response.status == ApprovalStatus.APPROVED
        except asyncio.TimeoutError:
            request.status = ApprovalStatus.EXPIRED
            return False
    
    async def _notify_approvers(self, request: ApprovalRequest) -> None:
        """Notify all registered handlers about approval request"""
        tasks = []
        for handler in self.notification_handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(request))
            else:
                handler(request)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _wait_for_approval(self, mission_id: str) -> ApprovalResponse:
        """Wait for approval response"""
        while True:
            if mission_id in self.approval_responses:
                return self.approval_responses.pop(mission_id)
            
            await asyncio.sleep(1)  # Poll every second
    
    async def approve(self, mission_id: str, approved_by: str, 
                     message: str = "", conditions: Dict = None) -> None:
        """Approve a mission"""
        response = ApprovalResponse(
            mission_id=mission_id,
            status=ApprovalStatus.APPROVED,
            approved_by=approved_by,
            message=message,
            conditions=conditions or {}
        )
        
        # Update request status
        if mission_id in self.pending_approvals:
            request = self.pending_approvals[mission_id]
            request.status = ApprovalStatus.APPROVED
            request.approved_by = approved_by
            request.approval_time = datetime.utcnow().isoformat()
        
        # Store response
        self.approval_responses[mission_id] = response
        
        # Notify handlers
        for handler in self.approval_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(response)
            else:
                handler(response)
    
    async def reject(self, mission_id: str, rejected_by: str, 
                    reason: str = "") -> None:
        """Reject a mission"""
        response = ApprovalResponse(
            mission_id=mission_id,
            status=ApprovalStatus.REJECTED,
            approved_by=rejected_by,
            message=reason
        )
        
        # Update request status
        if mission_id in self.pending_approvals:
            request = self.pending_approvals[mission_id]
            request.status = ApprovalStatus.REJECTED
        
        # Store response
        self.approval_responses[mission_id] = response
        
        # Notify handlers
        for handler in self.approval_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(response)
            else:
                handler(response)
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        return [r for r in self.pending_approvals.values() 
                if r.status == ApprovalStatus.PENDING and not r.is_expired()]
    
    def get_approval_status(self, mission_id: str) -> Optional[ApprovalStatus]:
        """Get status of approval request"""
        if mission_id in self.pending_approvals:
            return self.pending_approvals[mission_id].status
        return None
    
    def clear_expired(self) -> int:
        """Clear expired approval requests"""
        expired = []
        for mission_id, request in self.pending_approvals.items():
            if request.is_expired() and request.status == ApprovalStatus.PENDING:
                expired.append(mission_id)
                request.status = ApprovalStatus.EXPIRED
        
        return len(expired)


class NotificationService:
    """Handles notifications for approvals"""
    
    def __init__(self):
        """Initialize notification service"""
        self.notifications: List[Dict] = []
    
    async def send_approval_notification(self, request: ApprovalRequest) -> None:
        """Send approval notification"""
        notification = {
            'type': 'approval_request',
            'mission_id': request.mission_id,
            'mission_name': request.mission_name,
            'description': request.description,
            'risk_level': request.risk_level,
            'confidence': request.confidence,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        self.notifications.append(notification)
        
        # In production, send to Slack, PagerDuty, email, etc.
        print(f"[NOTIFICATION] Approval needed for: {request.mission_name}")
        print(f"[NOTIFICATION] Risk: {request.risk_level}, Confidence: {request.confidence}")
    
    async def send_approval_response_notification(self, response: ApprovalResponse) -> None:
        """Send notification about approval response"""
        notification = {
            'type': 'approval_response',
            'mission_id': response.mission_id,
            'status': response.status.value,
            'approved_by': response.approved_by,
            'message': response.message,
            'timestamp': response.timestamp,
        }
        
        self.notifications.append(notification)
        
        print(f"[NOTIFICATION] Mission {response.mission_id} {response.status.value}")
        print(f"[NOTIFICATION] By: {response.approved_by}")
    
    async def send_mission_complete_notification(self, mission_id: str, result: Dict) -> None:
        """Send notification when mission completes"""
        notification = {
            'type': 'mission_complete',
            'mission_id': mission_id,
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        self.notifications.append(notification)
        
        print(f"[NOTIFICATION] Mission {mission_id} complete")
        print(f"[NOTIFICATION] Result: {result}")
    
    async def send_mission_failed_notification(self, mission_id: str, error: str) -> None:
        """Send notification when mission fails"""
        notification = {
            'type': 'mission_failed',
            'mission_id': mission_id,
            'error': error,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        self.notifications.append(notification)
        
        print(f"[NOTIFICATION] Mission {mission_id} failed")
        print(f"[NOTIFICATION] Error: {error}")
    
    def get_notifications(self, notification_type: str = None) -> List[Dict]:
        """Get all notifications or by type"""
        if notification_type:
            return [n for n in self.notifications if n['type'] == notification_type]
        return self.notifications
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()
