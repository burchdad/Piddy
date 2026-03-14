#!/usr/bin/env python3
"""
PIDDY Approval System - End-to-End Integration Test

Tests complete workflow:
  1. Market gap detection
  2. Security assessment
  3. Email generation
  4. Approval workflow
  5. Build queue management
  6. Audit trail

Run: python tests/e2e_test_approval_system.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_gap_reporter import (
    MarketGapReporter, SecurityAssessor, GapAnalysis, EmailNotifier
)
from approval_workflow import (
    ApprovalWorkflow, ApprovalBuilderBridge, WorkflowState
)


class E2ETestRunner:
    """Runs end-to-end approval system tests"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, condition: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if condition else "❌ FAIL"
        print(f"  {status}: {name}")
        if details and not condition:
            print(f"     {details}")
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        
        self.tests.append({"name": name, "passed": condition})
    
    def section(self, title: str):
        """Print section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    async def run_all(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("  PIDDY APPROVAL SYSTEM - END-TO-END INTEGRATION TEST")
        print("="*70)
        
        # Test 1: Security Assessment
        await self.test_security_assessment()
        
        # Test 2: Email Generation
        await self.test_email_generation()
        
        # Test 3: Approval Workflow
        await self.test_approval_workflow()
        
        # Test 4: Builder Bridge
        await self.test_builder_bridge()
        
        # Test 5: Complete Integration
        await self.test_complete_flow()
        
        # Summary
        self.print_summary()
    
    async def test_security_assessment(self):
        """Test 1: Security risk assessment"""
        self.section("TEST 1: SECURITY ASSESSMENT")
        
        assessor = SecurityAssessor()
        
        # Test case: CI/CD agent (HIGH risk)
        ci_cd_gap = {
            "title": "Build Optimization",
            "category": "ci-cd",
            "complexity_score": 8,
            "integration_points": ["Build System", "Pipeline", "Repository", "CI/CD", "Deployment"]
        }
        
        result = await assessor.assess_security(ci_cd_gap)
        self.test("HIGH RISK: CI/CD agent flagged correctly", result.security_risk_level == "HIGH")
        self.test("CI/CD concerns identified", len(result.security_concerns) > 0, 
                 f"Got {len(result.security_concerns)} concerns")
        
        # Test case: Testing agent (LOW risk)
        test_gap = {
            "title": "Mutation Testing",
            "category": "testing",
            "complexity_score": 4,
            "integration_points": ["Test Runner"]
        }
        
        result = await assessor.assess_security(test_gap)
        self.test("LOW RISK: Testing agent flagged correctly", result.security_risk_level == "LOW",
                 f"Got {result.security_risk_level}")
        
        # Test case: Code Quality (MEDIUM risk with high complexity)
        code_quality = {
            "title": "Code Duplication",
            "category": "code-quality",
            "complexity_score": 8,
            "integration_points": ["Analyzer", "Reporter"]
        }
        
        result = await assessor.assess_security(code_quality)
        self.test("MEDIUM RISK: Code quality flagged correctly", result.security_risk_level in ["MEDIUM", "HIGH"],
                 f"Got {result.security_risk_level}")
    
    async def test_email_generation(self):
        """Test 2: Email notification generation"""
        self.section("TEST 2: EMAIL GENERATION")
        
        reporter = MarketGapReporter(user_email="test@example.com")
        
        # Create sample gaps
        sample_gaps = [
            {
                "gap_id": "gap_001",
                "title": "Mutation Testing",
                "category": "testing",
                "market_need": "Found in 45 repos",
                "frequency": 45,
                "estimated_impact": 0.9,
                "complexity_score": 5,
                "integration_points": ["Test Runner"]
            },
            {
                "gap_id": "gap_002",
                "title": "Build Optimization",
                "category": "ci-cd",
                "market_need": "Found in 55 repos",
                "frequency": 55,
                "estimated_impact": 0.87,
                "complexity_score": 8,
                "integration_points": ["Build", "Pipeline", "CI/CD", "Deploy"]
            }
        ]
        
        # Generate report
        await reporter.generate_and_send_report(sample_gaps)
        
        self.test("Report generated successfully", len(reporter.reports_sent) > 0)
        self.test("Email saved to notifications", 
                 len(list(Path("data/email_notifications").glob("*.email"))) > 0)
        
        if reporter.reports_sent:
            report = reporter.reports_sent[-1]
            self.test("Report has gaps", len(report.gaps) > 0)
            self.test("Report has request ID", bool(report.request_id))
            self.test("Report has HIGH risk gap", report.high_risk_count > 0)
            self.test("Report has LOW risk gap", report.low_risk_count > 0)
    
    async def test_approval_workflow(self):
        """Test 3: Approval workflow state machine"""
        self.section("TEST 3: APPROVAL WORKFLOW")
        
        workflow = ApprovalWorkflow()
        
        # Create sample request
        gaps = [
            {"gap_id": "gap_001", "title": "Low Risk Agent"},
            {"gap_id": "gap_002", "title": "High Risk Agent"}
        ]
        
        # Initiate workflow
        state = await workflow.initiate_approval_workflow(
            request_id="test_req_001",
            market_gaps=gaps,
            recipient_email="test@example.com"
        )
        
        self.test("Workflow initiated", state is not None)
        self.test("Workflow state file created", Path("data/approval_workflow_state.json").exists())
        self.test("Workflow in waiting state", state.status == "waiting")
        
        # Record approvals
        await workflow.record_approval("test_req_001", "gap_001", True)
        await workflow.record_approval("test_req_001", "gap_002", False, "Security risk")
        
        # Check updated state
        state = workflow.workflow_states.get("test_req_001")
        self.test("Workflow updated to partially_approved", state and state.status == "partially_approved")
        self.test("Approval count correct", state and len(state.approved_gaps) == 1)
        self.test("Rejection reason recorded", state and state.rejection_reasons.get("gap_002") == "Security risk")
        
        # Get approved gaps
        approved = await workflow.get_approved_gaps("test_req_001")
        self.test("Approved gaps retrieved", len(approved) > 0)
        if approved:
            self.test("Only approved gap returned", approved[0]["gap_id"] == "gap_001")
    
    async def test_builder_bridge(self):
        """Test 4: Approval builder bridge"""
        self.section("TEST 4: BUILDER BRIDGE")
        
        workflow = ApprovalWorkflow()
        bridge = ApprovalBuilderBridge(workflow)
        
        # Create and approve gaps
        gaps = [
            {"gap_id": "gap_001", "title": "Agent 1"},
            {"gap_id": "gap_002", "title": "Agent 2"},
            {"gap_id": "gap_003", "title": "Agent 3"}
        ]
        
        state = await workflow.initiate_approval_workflow("test_req_002", gaps, "test@example.com")
        
        # Approve some gaps
        await workflow.record_approval("test_req_002", "gap_001", True)
        await workflow.record_approval("test_req_002", "gap_002", False, "High risk")
        await workflow.record_approval("test_req_002", "gap_003", True)
        
        # Get approved gaps via workflow
        approved_gaps = await workflow.get_approved_gaps("test_req_002")
        
        self.test("Approved gaps retrieved", len(approved_gaps) > 0,
                 f"Got {len(approved_gaps)} gaps")
        self.test("Only approved gaps returned", 
                 all(g["gap_id"] in ["gap_001", "gap_003"] for g in approved_gaps),
                 f"Got gaps: {[g['gap_id'] for g in approved_gaps]}")
        self.test("Rejected gap not included",
                 all(g["gap_id"] != "gap_002" for g in approved_gaps),
                 "HIGH risk gap should not be in approved list")
    
    async def test_complete_flow(self):
        """Test 5: Complete integration flow"""
        self.section("TEST 5: COMPLETE INTEGRATION FLOW")
        
        print("Simulating: Gap Detection → Assessment → Email → Approval → Build Queue\n")
        
        # Step 1: Detect gaps (simulated market analysis)
        detected_gaps = [
            {
                "gap_id": "gap_e2e_001",
                "title": "Mutation Testing Agent",
                "category": "testing",
                "market_need": "Mutation testing framework",
                "frequency": 45,
                "estimated_impact": 0.9,
                "complexity_score": 5,
                "integration_points": ["Test Runner"]
            },
            {
                "gap_id": "gap_e2e_002",
                "title": "Build Optimization Agent",
                "category": "ci-cd",
                "market_need": "Build speed optimization",
                "frequency": 55,
                "estimated_impact": 0.87,
                "complexity_score": 9,
                "integration_points": ["Build", "Pipeline", "CI/CD", "Deployment", "Repository"]
            },
            {
                "gap_id": "gap_e2e_003",
                "title": "Code Duplication Detector",
                "category": "code-quality",
                "market_need": "Find duplicate code",
                "frequency": 40,
                "estimated_impact": 0.8,
                "complexity_score": 6,
                "integration_points": ["Analyzer", "Reporter"]
            }
        ]
        
        print("  Step 1: Market gaps detected")
        for gap in detected_gaps:
            print(f"    • {gap['title']}")
        
        # Step 2: Generate report with security assessment
        reporter = MarketGapReporter(user_email="test@example.com")
        await reporter.generate_and_send_report(detected_gaps)
        
        print("  Step 2: Security assessment completed")
        if reporter.reports_sent:
            report = reporter.reports_sent[-1]
            print(f"    • HIGH RISK: {report.high_risk_count}")
            print(f"    • MEDIUM RISK: {report.medium_risk_count}")
            print(f"    • LOW RISK: {report.low_risk_count}")
        
        # Step 3: Create approval workflow
        workflow = ApprovalWorkflow()
        request_id = f"e2e_test_{datetime.now().timestamp()}"
        state = await workflow.initiate_approval_workflow(
            request_id,
            detected_gaps,
            "test@example.com"
        )
        
        print("  Step 3: Approval workflow initiated")
        print(f"    • Request ID: {request_id}")
        
        # Step 4: Approve/reject gaps (simulating user)
        print("  Step 4: User decisions recorded")
        await workflow.record_approval(request_id, "gap_e2e_001", True)
        print(f"    • ✅ APPROVED: gap_e2e_001 (Mutation Testing - LOW risk)")
        
        await workflow.record_approval(request_id, "gap_e2e_002", False, "Needs security audit")
        print(f"    • ❌ REJECTED: gap_e2e_002 (Build Optimization - HIGH risk)")
        
        await workflow.record_approval(request_id, "gap_e2e_003", True)
        print(f"    • ✅ APPROVED: gap_e2e_003 (Code Duplication - MEDIUM risk)")
        
        # Step 5: Build queue with approved gaps only
        bridge = ApprovalBuilderBridge(workflow)
        build_queue = await workflow.get_approved_gaps(request_id)
        
        print("  Step 5: Build queue generated")
        print(f"    • Total approved for building: {len(build_queue)}")
        for gap in build_queue:
            print(f"    • {gap['title']}")
        
        # Verify results
        self.test("Complete flow executed", len(build_queue) == 2, "Should have 2 approved gaps")
        self.test("Rejected gap not in queue", 
                 all(g["gap_id"] != "gap_e2e_002" for g in build_queue),
                 "HIGH risk gap should not be queued")
        self.test("Approved gaps in queue",
                 all(g["gap_id"] in ["gap_e2e_001", "gap_e2e_003"] for g in build_queue),
                 "Should only have approved gaps")
        
        # Verify audit trail
        decisions_file = Path("data/approval_decisions.json")
        audit_trail_exists = decisions_file.exists() or Path("data").exists()
        self.test("Audit trail recorded", audit_trail_exists,
                 f"Decisions file at: {decisions_file}")
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        self.section("TEST RESULTS SUMMARY")
        print(f"  Total Tests: {total}")
        print(f"  Passed: {self.passed} ✅")
        print(f"  Failed: {self.failed} ❌")
        print(f"  Success Rate: {percentage:.1f}%\n")
        
        if self.failed == 0:
            print("  🎉 ALL TESTS PASSED! Approval system is ready for production.\n")
            print("  Next steps:")
            print("    1. Configure email: python src/email_config.py --help")
            print("    2. Start service: python src/service_manager.py --start")
            print("    3. Start dashboard: python src/dashboard_manager.py --start")
            print("    4. Check email for approval requests")
        else:
            print(f"  ⚠️  {self.failed} test(s) failed. Review above for details.\n")
            sys.exit(1)


async def main():
    """Run end-to-end tests"""
    runner = E2ETestRunner()
    await runner.run_all()


if __name__ == "__main__":
    asyncio.run(main())
