"""
Market Gap Reporter - Generates reports and sends email notifications
Integrates with approval workflow for human security review

This prevents risky autonomous builds and ensures human oversight.
"""

import asyncio
import json
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, asdict, field


@dataclass
class GapAnalysis:
    """Analysis of a market gap with security considerations"""
    gap_id: str
    agent_name: str
    category: str
    market_need: str
    repos_affected: int
    criticality_percent: float
    complexity_score: int
    estimated_build_time_hours: int = 24
    security_risk_level: str = "LOW"  # "LOW", "MEDIUM", "HIGH"
    security_concerns: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False
    approval_timestamp: Optional[str] = None
    rejected: bool = False
    rejection_reason: Optional[str] = None
    rejection_timestamp: Optional[str] = None


@dataclass
class ApprovalRequest:
    """Request sent to user for approval"""
    request_id: str
    gaps: List[GapAnalysis]
    total_gaps: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    created_at: str
    sent_to_email: str
    sent_at: Optional[str] = None
    status: str = "pending"  # pending, approved, partially_approved, rejected


class SecurityAssessor:
    """Evaluates security risks of proposed agents"""
    
    # Categories that require extra security scrutiny
    HIGH_RISK_CATEGORIES = {
        "ci-cd": ["Can modify build pipelines", "Could affect deployments"],
        "dependency-management": ["Could inject malicious deps", "High attack surface"],
        "refactoring": ["Could modify production code", "Broad codebase access"],
    }
    
    MEDIUM_RISK_CATEGORIES = {
        "code-quality": ["Could suppress important warnings", "Modify analysis rules"],
        "documentation": ["Could leak sensitive info", "Documentation access"],
    }
    
    def __init__(self):
        self.assessments: Dict[str, Dict] = {}
    
    async def assess_security(self, gap: Dict) -> GapAnalysis:
        """
        Assess security risks of a proposed agent
        Returns risk level and specific concerns
        """
        gap_analysis = GapAnalysis(
            gap_id=gap.get("gap_id", "unknown"),
            agent_name=gap.get("title", "Unknown"),
            category=gap.get("category", "general"),
            market_need=gap.get("market_need", ""),
            repos_affected=gap.get("frequency", 0),
            criticality_percent=gap.get("estimated_impact", 0) * 100,
            complexity_score=gap.get("complexity_score", 5),
            estimated_build_time_hours=gap.get("complexity_score", 5) * 4,
            integration_points=gap.get("integration_points", []),
        )
        
        # Assess security risks
        security_concerns = []
        risk_level = "LOW"
        
        # Check high-risk categories
        if gap_analysis.category in self.HIGH_RISK_CATEGORIES:
            risk_level = "HIGH"
            security_concerns.extend(
                self.HIGH_RISK_CATEGORIES[gap_analysis.category]
            )
            security_concerns.append(
                f"⚠️  {gap_analysis.category.upper()} agent may require code modification"
            )
        
        # Check medium-risk categories
        elif gap_analysis.category in self.MEDIUM_RISK_CATEGORIES:
            risk_level = "MEDIUM"
            security_concerns.extend(
                self.MEDIUM_RISK_CATEGORIES[gap_analysis.category]
            )
        
        # Complexity assessment
        if gap_analysis.complexity_score >= 8:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            security_concerns.append(
                f"⚠️  High complexity ({gap_analysis.complexity_score}/10) agent"
            )
        
        # Integration point assessment
        if len(gap_analysis.integration_points) > 3:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            elif risk_level == "MEDIUM":
                risk_level = "HIGH"
            security_concerns.append(
                f"⚠️  {len(gap_analysis.integration_points)} integration points = broad system access"
            )
        
        gap_analysis.security_risk_level = risk_level
        gap_analysis.security_concerns = security_concerns
        
        return gap_analysis


class EmailNotifier:
    """Sends email notifications for market gap reports"""
    
    def __init__(self, 
                 smtp_server: str = "localhost",
                 smtp_port: int = 1025,
                 from_email: str = "piddy@autonomous.local"):
        """
        Initialize email notifier
        
        Note: For local testing, use:
          - smtp_server: "localhost"
          - smtp_port: 1025
          - Run: python -m smtpd -n -c DebuggingServer localhost:1025
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.sent_emails: List[Dict] = []
    
    async def send_approval_request(self, 
                                    approval_request: ApprovalRequest,
                                    dashboard_url: str = "http://localhost:8000") -> bool:
        """
        Send email requesting approval for market gaps
        
        In demo mode, save to file instead of sending
        """
        try:
            # Build email content
            subject = self._build_subject(approval_request)
            html_body = self._build_html_body(approval_request, dashboard_url)
            text_body = self._build_text_body(approval_request, dashboard_url)
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = approval_request.sent_to_email
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            # Try to send (or save to file for demo)
            success = await self._send_or_demo(msg, approval_request)
            
            if success:
                approval_request.sent_at = datetime.now().isoformat()
                self.sent_emails.append(asdict(approval_request))
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    async def _send_or_demo(self, msg, approval_request) -> bool:
        """Send email or save to file for demo"""
        
        # Save to file for inspection
        demo_dir = Path("data/email_notifications")
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"approval_request_{approval_request.request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.email"
        filepath = demo_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"TO: {approval_request.sent_to_email}\n")
            f.write(f"SUBJECT: {msg['Subject']}\n")
            f.write(f"\n{'='*80}\n\n")
            f.write(msg.as_string())
        
        print(f"✉️  Email saved to: {filepath}")
        return True
    
    def _build_subject(self, approval_request: ApprovalRequest) -> str:
        """Build email subject"""
        high_count = approval_request.high_risk_count
        total = approval_request.total_gaps
        
        if high_count > 0:
            return f"🚨 PIDDY: {total} Market Gaps Found ({high_count} HIGH Security Risk)"
        elif approval_request.medium_risk_count > 0:
            return f"⚠️  PIDDY: {total} Market Gaps Found ({approval_request.medium_risk_count} MEDIUM Risk)"
        else:
            return f"✅ PIDDY: {total} Market Gaps Found (Review & Approve)"
    
    def _build_text_body(self, approval_request: ApprovalRequest, dashboard_url: str) -> str:
        """Build plain text email body"""
        body = f"""
PIDDY AUTONOMOUS SYSTEM - MARKET GAP APPROVAL REQUEST

{len(approval_request.gaps)} market gaps have been identified and require your approval.

SECURITY SUMMARY:
  🚨 HIGH RISK: {approval_request.high_risk_count}
  ⚠️  MEDIUM RISK: {approval_request.medium_risk_count}
  ✅ LOW RISK: {approval_request.low_risk_count}

TO REVIEW AND APPROVE:
  {dashboard_url}/approvals/{approval_request.request_id}

GAPS IDENTIFIED:
"""
        for gap in approval_request.gaps:
            body += f"""
  {gap.agent_name}:
    - Market need: {gap.market_need}
    - Risk level: {gap.security_risk_level}
    - Affects: {gap.repos_affected} repositories
    - Build time: ~{gap.estimated_build_time_hours}h
"""
            if gap.security_concerns:
                body += "    Security concerns:\n"
                for concern in gap.security_concerns:
                    body += f"      • {concern}\n"
        
        body += f"""

INSTRUCTIONS:
  1. Review each gap
  2. Approve low-risk gaps (automatic approval to build)
  3. Disapprove high-risk gaps with security concerns
  4. Approved gaps will be auto-built within 1 hour
  5. Disapproved gaps will be skipped

APPROVAL STATUS:
  Status: {approval_request.status}
  Created: {approval_request.created_at}

Dashboard: {dashboard_url}/approvals/{approval_request.request_id}

--
PIDDY Autonomous System
Continuous Market-Driven Development
"""
        return body
    
    def _build_html_body(self, approval_request: ApprovalRequest, dashboard_url: str) -> str:
        """Build HTML email body"""
        high_color = "#d32f2f" if approval_request.high_risk_count > 0 else "#4caf50"
        
        gaps_html = ""
        for gap in approval_request.gaps:
            risk_badge = f'<span style="padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; background-color: '
            
            if gap.security_risk_level == "HIGH":
                risk_badge += '#d32f2f">' + gap.security_risk_level + '</span>'
            elif gap.security_risk_level == "MEDIUM":
                risk_badge += '#ff9800">' + gap.security_risk_level + '</span>'
            else:
                risk_badge += '#4caf50">' + gap.security_risk_level + '</span>'
            
            concerns_html = ""
            if gap.security_concerns:
                concerns_html = '<ul>'
                for concern in gap.security_concerns:
                    concerns_html += f'<li>{concern}</li>'
                concerns_html += '</ul>'
            
            gaps_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                    <strong>{gap.agent_name}</strong><br/>
                    <small>{gap.market_need}</small>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">
                    {risk_badge}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;">
                    Affects {gap.repos_affected} repos<br/>
                    ~{gap.estimated_build_time_hours}h to build
                </td>
            </tr>
            {f'<tr><td colspan="3" style="padding: 8px 12px; background-color: #f5f5f5;"><strong>Security Concerns:</strong>{concerns_html}</td></tr>' if gap.security_concerns else ''}
            """
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h2 style="color: {high_color};">🤖 PIDDY Autonomous System</h2>
                    <h3>Market Gap Approval Request</h3>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4>Security Summary:</h4>
                        <p>
                            🚨 <strong>HIGH RISK:</strong> {approval_request.high_risk_count} | 
                            ⚠️  <strong>MEDIUM RISK:</strong> {approval_request.medium_risk_count} | 
                            ✅ <strong>LOW RISK:</strong> {approval_request.low_risk_count}
                        </p>
                    </div>
                    
                    <h4>Market Gaps Identified ({len(approval_request.gaps)}):</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #f0f0f0;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Agent</th>
                            <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">Risk</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Details</th>
                        </tr>
                        {gaps_html}
                    </table>
                    
                    <div style="margin: 30px 0; text-align: center;">
                        <a href="{dashboard_url}/approvals/{approval_request.request_id}" 
                           style="background-color: {high_color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Review & Approve in Dashboard
                        </a>
                    </div>
                    
                    <div style="background-color: #fffde7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>⚠️  Important:</strong>
                        <ul>
                            <li>Review security concerns before approving</li>
                            <li>HIGH RISK agents require explicit approval</li>
                            <li>Approved agents will be built within 1 hour</li>
                            <li>Disapproved agents will not be built</li>
                        </ul>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999;">
                        Created: {approval_request.created_at}<br/>
                        Request ID: {approval_request.request_id}
                    </p>
                </div>
            </body>
        </html>
        """
        return html


class MarketGapReporter:
    """
    Orchestrates market gap reporting and approval workflow
    
    Flow:
    1. Market analyzer identifies gaps
    2. Security assessor evaluates risks
    3. Report generated and sent to user
    4. User approves/disapproves via dashboard
    5. Approved gaps queued for building
    6. System waits for approval before building
    """
    
    def __init__(self, 
                 user_email: str = "user@example.com",
                 dashboard_url: str = "http://localhost:8000"):
        self.user_email = user_email
        self.dashboard_url = dashboard_url
        self.security_assessor = SecurityAssessor()
        self.email_notifier = EmailNotifier()
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_decisions: Dict[str, Dict[str, bool]] = {}  # {request_id: {gap_id: approved}}
        self.reports_sent: List[ApprovalRequest] = []
    
    async def generate_and_send_report(self, 
                                       gaps: List[Dict]) -> Optional[ApprovalRequest]:
        """
        Generate report from market gaps and send email to user
        
        Returns the approval request created
        """
        if not gaps:
            return None
        
        print(f"\n📊 GENERATING MARKET GAP REPORT ({len(gaps)} gaps)")
        print("-" * 60)
        
        # Assess security for each gap
        assessed_gaps = []
        for gap in gaps:
            assessed_gap = await self.security_assessor.assess_security(gap)
            assessed_gaps.append(assessed_gap)
        
        # Create approval request
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        high_risk = sum(1 for g in assessed_gaps if g.security_risk_level == "HIGH")
        medium_risk = sum(1 for g in assessed_gaps if g.security_risk_level == "MEDIUM")
        low_risk = sum(1 for g in assessed_gaps if g.security_risk_level == "LOW")
        
        approval_request = ApprovalRequest(
            request_id=request_id,
            gaps=assessed_gaps,
            total_gaps=len(assessed_gaps),
            high_risk_count=high_risk,
            medium_risk_count=medium_risk,
            low_risk_count=low_risk,
            created_at=datetime.now().isoformat(),
            sent_to_email=self.user_email,
        )
        
        # Send email
        print(f"\n✉️  SENDING APPROVAL REQUEST TO: {self.user_email}")
        print(f"   Request ID: {request_id}")
        print(f"   Gaps: {len(assessed_gaps)} total")
        print(f"   🚨 HIGH RISK: {high_risk}")
        print(f"   ⚠️  MEDIUM RISK: {medium_risk}")
        print(f"   ✅ LOW RISK: {low_risk}")
        
        sent = await self.email_notifier.send_approval_request(
            approval_request,
            self.dashboard_url
        )
        
        if sent:
            self.pending_approvals[request_id] = approval_request
            self.reports_sent.append(approval_request)
            print(f"   ✅ Email sent successfully")
            print(f"\n   📍 User can review and approve at:")
            print(f"      {self.dashboard_url}/approvals/{request_id}")
            return approval_request
        else:
            print(f"   ❌ Failed to send email")
            return None
    
    async def record_approval_decision(self, 
                                       request_id: str,
                                       gap_id: str,
                                       approved: bool,
                                       reason: Optional[str] = None) -> bool:
        """
        Record user's approval decision for a specific gap
        """
        if request_id not in self.approval_decisions:
            self.approval_decisions[request_id] = {}
        
        self.approval_decisions[request_id][gap_id] = {
            "approved": approved,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
        }
        
        print(f"{'✅ APPROVED' if approved else '❌ REJECTED'}: {gap_id}")
        return True
    
    async def get_approved_gaps(self, request_id: str) -> List[GapAnalysis]:
        """
        Get list of approved gaps ready to build
        """
        if request_id not in self.pending_approvals:
            return []
        
        approval_request = self.pending_approvals[request_id]
        approved_gaps = []
        
        if request_id in self.approval_decisions:
            decisions = self.approval_decisions[request_id]
            for gap in approval_request.gaps:
                if gap.gap_id in decisions and decisions[gap.gap_id].get("approved"):
                    approved_gaps.append(gap)
        
        return approved_gaps
    
    async def get_rejection_reasons(self, request_id: str) -> Dict[str, str]:
        """
        Get rejection reasons for denied gaps
        """
        rejections = {}
        
        if request_id in self.approval_decisions:
            decisions = self.approval_decisions[request_id]
            for gap_id, decision in decisions.items():
                if not decision.get("approved") and decision.get("reason"):
                    rejections[gap_id] = decision["reason"]
        
        return rejections
    
    def get_approval_status(self, request_id: str) -> Optional[Dict]:
        """
        Get status of an approval request
        """
        if request_id not in self.pending_approvals:
            return None
        
        request = self.pending_approvals[request_id]
        return {
            "request_id": request_id,
            "total_gaps": request.total_gaps,
            "status": request.status,
            "created_at": request.created_at,
            "gaps": [
                {
                    "gap_id": g.gap_id,
                    "agent_name": g.agent_name,
                    "security_risk_level": g.security_risk_level,
                    "concerns": g.security_concerns,
                }
                for g in request.gaps
            ],
        }


async def main():
    """Demo the market gap reporter"""
    reporter = MarketGapReporter(
        user_email="dev@example.com",
        dashboard_url="http://localhost:8000"
    )
    
    # Simulated market gaps
    sample_gaps = [
        {
            "gap_id": "gap_001",
            "title": "Mutation Testing Agent",
            "category": "testing",
            "market_need": "Found in 45 repos - 90% critical",
            "frequency": 45,
            "estimated_impact": 0.9,
            "complexity_score": 6,
            "integration_points": ["Phase 42", "Growth Engine", "Metrics"],
        },
        {
            "gap_id": "gap_002",
            "title": "Build Optimization Agent",
            "category": "ci-cd",
            "market_need": "Found in 55 repos - 87% critical",
            "frequency": 55,
            "estimated_impact": 0.87,
            "complexity_score": 7,
            "integration_points": ["Build System", "Pipeline", "Repository", "CI/CD"],
        },
        {
            "gap_id": "gap_003",
            "title": "Code Duplication Detector",
            "category": "code-quality",
            "market_need": "Found in 72 repos - 92% critical",
            "frequency": 72,
            "estimated_impact": 0.92,
            "complexity_score": 5,
            "integration_points": ["Analysis", "Reporting"],
        },
    ]
    
    # Generate and send report
    approval_request = await reporter.generate_and_send_report(sample_gaps)
    
    if approval_request:
        print(f"\n{'='*60}")
        print("SIMULATING USER APPROVALS")
        print(f"{'='*60}\n")
        
        # Simulate user decisions
        for gap in approval_request.gaps:
            if gap.security_risk_level == "HIGH":
                print(f"User: Disapproving {gap.agent_name} (HIGH RISK)")
                await reporter.record_approval_decision(
                    approval_request.request_id,
                    gap.gap_id,
                    approved=False,
                    reason="CI/CD agent needs security audit before approval"
                )
            else:
                print(f"User: Approving {gap.agent_name} ({gap.security_risk_level} risk)")
                await reporter.record_approval_decision(
                    approval_request.request_id,
                    gap.gap_id,
                    approved=True
                )
        
        # Get approved gaps
        approved = await reporter.get_approved_gaps(approval_request.request_id)
        print(f"\n✅ APPROVED FOR BUILDING: {len(approved)} gaps")
        for gap in approved:
            print(f"   • {gap.agent_name}")
        
        rejections = await reporter.get_rejection_reasons(approval_request.request_id)
        if rejections:
            print(f"\n❌ REJECTED: {len(rejections)} gaps")
            for gap_id, reason in rejections.items():
                print(f"   • {gap_id}: {reason}")


if __name__ == "__main__":
    asyncio.run(main())
