"""
Approval Workflow Manager - Orchestrates market gap review and approval process

Coordinates:
1. Market analyzer identifies gaps
2. Gap reporter sends email to user
3. User reviews and approves/disapproves via dashboard
4. Approved gaps queued for building
5. Disapproved gaps skipped
6. System waits for approvals before building

Ensures security review before autonomous builds.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class WorkflowState:
    """Tracks state of approval workflow"""
    request_id: str
    market_gaps: List[Dict]  # Gaps from market analyzer
    sent_at: Optional[str] = None
    approval_deadline: Optional[str] = None
    status: str = "waiting"  # waiting, partially_approved, fully_approved, expired
    approved_gaps: List[str] = field(default_factory=list)
    rejected_gaps: List[str] = field(default_factory=list)
    rejection_reasons: Dict[str, str] = field(default_factory=dict)


class ApprovalWorkflow:
    """Manages the complete approval workflow"""
    
    def __init__(self,
                 approval_timeout_hours: int = 24,
                 auto_build_delay_minutes: int = 5):
        """
        Initialize workflow manager
        
        approval_timeout_hours: How long to wait for user approval (default: 24 hours)
        auto_build_delay_minutes: How long after approval before building (default: 5 min)
        """
        self.approval_timeout = timedelta(hours=approval_timeout_hours)
        self.auto_build_delay = timedelta(minutes=auto_build_delay_minutes)
        
        self.workflow_states: Dict[str, WorkflowState] = {}
        self.state_file = Path("data/approval_workflow_state.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_state()
    
    def _load_state(self):
        """Load workflow state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    for req_id, state_dict in data.items():
                        self.workflow_states[req_id] = WorkflowState(**state_dict)
            except:
                self.workflow_states = {}
    
    def _save_state(self):
        """Save workflow state to file"""
        with open(self.state_file, 'w') as f:
            data = {
                req_id: asdict(state) 
                for req_id, state in self.workflow_states.items()
            }
            json.dump(data, f, indent=2)
    
    async def initiate_approval_workflow(self, 
                                        request_id: str,
                                        market_gaps: List[Dict],
                                        recipient_email: str) -> WorkflowState:
        """
        Start new approval workflow
        
        1. Register workflow
        2. Set timeout deadline
        3. Mark as waiting for approval
        """
        print(f"\n📋 INITIATING APPROVAL WORKFLOW")
        print(f"   Request ID: {request_id}")
        print(f"   Gaps: {len(market_gaps)}")
        print(f"   To: {recipient_email}")
        print(f"   Deadline: {(datetime.now() + self.approval_timeout).isoformat()}")
        
        state = WorkflowState(
            request_id=request_id,
            market_gaps=market_gaps,
            sent_at=datetime.now().isoformat(),
            approval_deadline=(datetime.now() + self.approval_timeout).isoformat(),
            status="waiting",
        )
        
        self.workflow_states[request_id] = state
        self._save_state()
        
        return state
    
    async def record_approval(self,
                             request_id: str,
                             gap_id: str,
                             approved: bool,
                             reason: Optional[str] = None):
        """
        Record user's approval decision for a gap
        """
        if request_id not in self.workflow_states:
            print(f"❌ Unknown request: {request_id}")
            return False
        
        state = self.workflow_states[request_id]
        
        if approved:
            if gap_id not in state.approved_gaps:
                state.approved_gaps.append(gap_id)
            # Remove from rejected if was there
            if gap_id in state.rejected_gaps:
                state.rejected_gaps.remove(gap_id)
            print(f"✅ APPROVED: {gap_id}")
        else:
            if gap_id not in state.rejected_gaps:
                state.rejected_gaps.append(gap_id)
            # Remove from approved if was there
            if gap_id in state.approved_gaps:
                state.approved_gaps.remove(gap_id)
            if reason:
                state.rejection_reasons[gap_id] = reason
            print(f"❌ REJECTED: {gap_id}")
            if reason:
                print(f"   Reason: {reason}")
        
        self._update_workflow_status(request_id)
        self._save_state()
        
        return True
    
    def _update_workflow_status(self, request_id: str):
        """Update workflow status based on approvals"""
        state = self.workflow_states[request_id]
        total = len(state.market_gaps)
        approved = len(state.approved_gaps)
        
        if approved == 0:
            state.status = "waiting"
        elif approved == total:
            state.status = "fully_approved"
        else:
            state.status = "partially_approved"
    
    async def get_approved_gaps(self, request_id: str) -> List[Dict]:
        """
        Get list of gaps approved for building
        """
        if request_id not in self.workflow_states:
            return []
        
        state = self.workflow_states[request_id]
        approved = []
        
        for gap in state.market_gaps:
            if gap.get("gap_id") in state.approved_gaps:
                approved.append(gap)
        
        return approved
    
    async def should_build_gap(self, request_id: str, gap_id: str) -> bool:
        """
        Check if gap should be built
        
        Approved gaps are queued for building
        """
        if request_id not in self.workflow_states:
            return False
        
        state = self.workflow_states[request_id]
        return gap_id in state.approved_gaps
    
    async def check_workflow_timeout(self, request_id: str) -> bool:
        """
        Check if approval deadline has passed
        
        If yes, proceed with approved gaps or fail
        """
        if request_id not in self.workflow_states:
            return False
        
        state = self.workflow_states[request_id]
        deadline = datetime.fromisoformat(state.approval_deadline)
        
        if datetime.now() > deadline:
            print(f"⏰ APPROVAL DEADLINE PASSED: {request_id}")
            
            if len(state.approved_gaps) > 0:
                print(f"   Proceeding with {len(state.approved_gaps)} approved gaps")
                state.status = "expired_with_approvals"
            else:
                print(f"   No approved gaps, skipping")
                state.status = "expired_no_approvals"
            
            self._save_state()
            return True
        
        return False
    
    async def get_build_queue(self) -> List[Dict]:
        """
        Get all gaps ready to build
        (all approved gaps across all requests)
        """
        build_queue = []
        
        for request_id, state in self.workflow_states.items():
            for gap in state.market_gaps:
                if gap.get("gap_id") in state.approved_gaps:
                    gap["request_id"] = request_id
                    gap["approved_at"] = datetime.now().isoformat()
                    build_queue.append(gap)
        
        return build_queue
    
    async def get_workflow_status(self, request_id: str) -> Optional[Dict]:
        """
        Get status of a specific workflow
        """
        if request_id not in self.workflow_states:
            return None
        
        state = self.workflow_states[request_id]
        return {
            "request_id": request_id,
            "status": state.status,
            "sent_at": state.sent_at,
            "deadline": state.approval_deadline,
            "total_gaps": len(state.market_gaps),
            "approved_count": len(state.approved_gaps),
            "rejected_count": len(state.rejected_gaps),
            "gaps": [
                {
                    "gap_id": gap.get("gap_id"),
                    "title": gap.get("title"),
                    "status": "approved" if gap.get("gap_id") in state.approved_gaps 
                             else "rejected" if gap.get("gap_id") in state.rejected_gaps
                             else "pending",
                    "rejection_reason": state.rejection_reasons.get(gap.get("gap_id")),
                }
                for gap in state.market_gaps
            ],
        }
    
    async def list_all_workflows(self) -> List[Dict]:
        """List all active workflows"""
        return [
            await self.get_workflow_status(req_id)
            for req_id in self.workflow_states.keys()
        ]


class ApprovalBuilderBridge:
    """
    Bridge between Approval Workflow and Autonomous Builder
    
    Ensures builder only builds approved gaps, with proper ordering
    """
    
    def __init__(self, approval_workflow: ApprovalWorkflow):
        self.workflow = approval_workflow
        self.build_history: List[Dict] = []
    
    async def get_next_gap_to_build(self) -> Optional[Dict]:
        """
        Get next gap approved for building
        
        Returns None if no approved gaps waiting
        """
        build_queue = await self.workflow.get_build_queue()
        
        if not build_queue:
            return None
        
        # Return first gap not yet built
        for gap in build_queue:
            if gap not in self.build_history:
                return gap
        
        return None
    
    async def notify_build_complete(self, gap_id: str, success: bool):
        """
        Record that a gap was built
        """
        self.build_history.append({
            "gap_id": gap_id,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        })
        print(f"{'✅' if success else '❌'} Build recorded: {gap_id}")


async def main():
    """Demo the approval workflow"""
    workflow = ApprovalWorkflow()
    
    # Sample market gaps
    gaps = [
        {
            "gap_id": "gap_001",
            "title": "Mutation Testing Agent",
            "category": "testing",
            "security_risk_level": "LOW",
        },
        {
            "gap_id": "gap_002",
            "title": "Build Optimization Agent",
            "category": "ci-cd",
            "security_risk_level": "HIGH",
        },
        {
            "gap_id": "gap_003",
            "title": "Code Duplication Detector",
            "category": "code-quality",
            "security_risk_level": "MEDIUM",
        },
    ]
    
    # Initiate workflow
    request_id = "test_approval_001"
    state = await workflow.initiate_approval_workflow(
        request_id=request_id,
        market_gaps=gaps,
        recipient_email="user@example.com"
    )
    
    print(f"\n🎬 WORKFLOW INITIATED")
    print(f"   Status: {state.status}")
    print(f"   Deadline: {state.approval_deadline}\n")
    
    # Simulate user approvals
    print("👤 SIMULATING USER APPROVALS:\n")
    
    # Approve gap 1
    await workflow.record_approval(request_id, "gap_001", approved=True)
    
    # Reject gap 2 (HIGH RISK)
    await workflow.record_approval(
        request_id,
        "gap_002",
        approved=False,
        reason="Needs security audit before deploying to CI/CD pipeline"
    )
    
    # Approve gap 3
    await workflow.record_approval(request_id, "gap_003", approved=True)
    
    # Get status
    print(f"\n📊 WORKFLOW STATUS:")
    status = await workflow.get_workflow_status(request_id)
    print(json.dumps(status, indent=2))
    
    # Get approved gaps ready to build
    print(f"\n✅ GAPS APPROVED FOR BUILDING:")
    approved = await workflow.get_approved_gaps(request_id)
    for gap in approved:
        print(f"   • {gap['title']}")
    
    # Demo the bridge
    print(f"\n🔗 BUILDER BRIDGE:")
    bridge = ApprovalBuilderBridge(workflow)
    next_gap = await bridge.get_next_gap_to_build()
    if next_gap:
        print(f"   Next gap to build: {next_gap['title']}")
        await bridge.notify_build_complete(next_gap['gap_id'], success=True)


if __name__ == "__main__":
    asyncio.run(main())
