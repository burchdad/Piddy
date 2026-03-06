"""
Piddy Dashboard API Backend
Real-time monitoring and observability for Piddy autonomous system

Provides REST endpoints for:
- System overview and health
- Agent status and reputation
- Real-time message feeds
- Phase deployment status
- Security audit results
- Performance metrics
- Log streaming
- Test results
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class SystemStatus(BaseModel):
    """Overall system status"""
    status: str  # healthy, degraded, unhealthy
    uptime_seconds: int
    version: str
    environment: str
    timestamp: str


class AgentStatus(BaseModel):
    """Individual agent status"""
    agent_id: str
    role: str
    status: str  # active, idle, error
    reputation_score: float
    total_decisions: int
    correct_decisions: int
    messages_pending: int
    last_activity: str


class AgentMessage(BaseModel):
    """Message between agents"""
    message_id: str
    sender_id: str
    receiver_id: Optional[str]
    message_type: str
    content: Dict
    timestamp: str
    priority: int


class PhaseStatus(BaseModel):
    """Status of a phase deployment"""
    phase_id: str
    phase_name: str
    status: str  # pending, in_progress, completed, failed
    progress_percent: int
    timestamp: str
    details: Dict


class SecurityAuditResult(BaseModel):
    """Security audit results"""
    audit_id: str
    passed_checks: int
    failed_checks: int
    critical_failures: List[str]
    is_production_safe: bool
    timestamp: str


class PerformanceMetric(BaseModel):
    """Performance metric"""
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float]
    status: str  # ok, warning, critical
    timestamp: str


class LogEntry(BaseModel):
    """Log entry"""
    timestamp: str
    level: str  # INFO, WARNING, ERROR, DEBUG
    source: str
    message: str
    details: Optional[Dict]


class TestResult(BaseModel):
    """Test result"""
    test_id: str
    test_name: str
    status: str  # passed, failed, skipped
    duration_seconds: float
    message: str


class DashboardMetrics(BaseModel):
    """Overall dashboard metrics"""
    agents_online: int
    agents_offline: int
    recent_messages: int
    phases_in_progress: int
    security_issues: int
    performance_warnings: int
    tests_passed: int
    tests_failed: int


class Decision(BaseModel):
    """AI decision with reasoning"""
    id: str
    task: str
    agent_id: str
    action: str
    confidence: float  # 0.0-1.0
    context: Dict
    reasoning_chain: List[Dict]
    factors: List[Dict]
    parameters: Dict
    validation: Dict
    outcome: Optional[Dict]
    timestamp: str


class Mission(BaseModel):
    """Mission timeline"""
    id: str
    name: str
    description: str
    goal: str
    status: str  # pending, in_progress, completed, failed
    priority: int
    stages: List[Dict]
    agents_involved: List[Dict]
    progress_percent: int
    plan: Dict
    success_criteria: List[str]
    efficiency_score: float
    quality_score: float
    risk_level: str
    notes: Optional[str]
    timestamp: str


class DependencyGraphNode(BaseModel):
    """Dependency graph node"""
    id: str
    name: str
    type: str  # function, module, service, external
    description: str
    x: float
    y: float
    inbound_count: int
    outbound_count: int
    avg_response_time: float
    error_rate: float


class DependencyGraphEdge(BaseModel):
    """Dependency graph edge"""
    from_id: str
    to_id: str
    type: str  # sync, async
    calls: int
    weight: float


class DependencyGraph(BaseModel):
    """Dependency graph"""
    nodes: List[DependencyGraphNode]
    edges: List[DependencyGraphEdge]
    timestamp: str


class MissionReplayStep(BaseModel):
    """Single step in mission replay"""
    step_number: int
    type: str  # agent_action, service_call, decision, validation, error, deployment
    title: str
    description: str
    timestamp: str
    timestamp_display: str
    agent_id: Optional[str] = None
    service_call: Optional[str] = None
    decision: Optional[Dict] = None
    active_services: List[Dict] = []
    performance: Optional[Dict] = None


class MissionReplayData(BaseModel):
    """Complete mission replay sequence"""
    mission_id: str
    mission_name: str
    mission_description: str
    status: str
    steps: List[MissionReplayStep]
    agents_involved: List[Dict]
    total_duration: str
    efficiency_score: float
    quality_score: float
    timestamp: str


# ============================================================================
# MOCK DATA GENERATORS (Replace with real data from Piddy)
# ============================================================================

class MockDataGenerator:
    """Generate mock data for dashboard"""
    
    @staticmethod
    def get_system_status() -> SystemStatus:
        """Get system status"""
        return SystemStatus(
            status="healthy",
            uptime_seconds=86400,
            version="2.0.0",
            environment="production",
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def get_agents() -> List[AgentStatus]:
        """Get all agent statuses"""
        return [
            AgentStatus(
                agent_id="analyzer_1",
                role="analyzer",
                status="active",
                reputation_score=1.25,
                total_decisions=156,
                correct_decisions=149,
                messages_pending=3,
                last_activity=datetime.utcnow().isoformat()
            ),
            AgentStatus(
                agent_id="validator_1",
                role="validator",
                status="active",
                reputation_score=1.15,
                total_decisions=142,
                correct_decisions=135,
                messages_pending=1,
                last_activity=datetime.utcnow().isoformat()
            ),
            AgentStatus(
                agent_id="executor_1",
                role="executor",
                status="active",
                reputation_score=1.32,
                total_decisions=128,
                correct_decisions=124,
                messages_pending=2,
                last_activity=datetime.utcnow().isoformat()
            ),
            AgentStatus(
                agent_id="guardian_1",
                role="guardian",
                status="active",
                reputation_score=1.42,
                total_decisions=95,
                correct_decisions=93,
                messages_pending=0,
                last_activity=datetime.utcnow().isoformat()
            ),
        ]
    
    @staticmethod
    def get_agent_messages() -> List[AgentMessage]:
        """Get recent agent messages"""
        return [
            AgentMessage(
                message_id="msg_001",
                sender_id="analyzer_1",
                receiver_id=None,
                message_type="proposal",
                content={"action": "analyze_code", "file": "app.py"},
                timestamp=datetime.utcnow().isoformat(),
                priority=7
            ),
            AgentMessage(
                message_id="msg_002",
                sender_id="validator_1",
                receiver_id="analyzer_1",
                message_type="vote",
                content={"proposal_id": "prop_001", "outcome": "approved", "confidence": 0.95},
                timestamp=datetime.utcnow().isoformat(),
                priority=8
            ),
            AgentMessage(
                message_id="msg_003",
                sender_id="executor_1",
                receiver_id="guardian_1",
                message_type="query",
                content={"query": "Is refactoring safe?"},
                timestamp=datetime.utcnow().isoformat(),
                priority=9
            ),
            AgentMessage(
                message_id="msg_004",
                sender_id="guardian_1",
                receiver_id="executor_1",
                message_type="report",
                content={"decision": "approved", "risk_level": "low"},
                timestamp=datetime.utcnow().isoformat(),
                priority=9
            ),
        ]
    
    @staticmethod
    def get_phases() -> List[PhaseStatus]:
        """Get phase status"""
        return [
            PhaseStatus(
                phase_id="phase_19",
                phase_name="Production Hardening",
                status="completed",
                progress_percent=100,
                timestamp=datetime.utcnow().isoformat(),
                details={"security_checks": 11, "passed": 11, "failed": 0}
            ),
            PhaseStatus(
                phase_id="phase_20",
                phase_name="Production Launch",
                status="in_progress",
                progress_percent=75,
                timestamp=datetime.utcnow().isoformat(),
                details={"step": "monitoring", "instances": 3, "healthy": 3}
            ),
            PhaseStatus(
                phase_id="phase_50",
                phase_name="Multi-Agent Orchestration",
                status="in_progress",
                progress_percent=50,
                timestamp=datetime.utcnow().isoformat(),
                details={"agents": 4, "proposals": 12, "consensus_rate": 0.92}
            ),
            PhaseStatus(
                phase_id="phase_51",
                phase_name="Graph Reasoning",
                status="pending",
                progress_percent=0,
                timestamp=datetime.utcnow().isoformat(),
                details={"scheduled": True}
            ),
        ]
    
    @staticmethod
    def get_security_info() -> SecurityAuditResult:
        """Get security audit results"""
        return SecurityAuditResult(
            audit_id="audit_001",
            passed_checks=10,
            failed_checks=0,
            critical_failures=[],
            is_production_safe=True,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def get_performance_metrics() -> List[PerformanceMetric]:
        """Get performance metrics"""
        return [
            PerformanceMetric(
                metric_name="API Latency",
                value=45.2,
                unit="ms",
                threshold=100,
                status="ok",
                timestamp=datetime.utcnow().isoformat()
            ),
            PerformanceMetric(
                metric_name="Graph Query Speed",
                value=156.5,
                unit="ops/sec",
                threshold=100,
                status="ok",
                timestamp=datetime.utcnow().isoformat()
            ),
            PerformanceMetric(
                metric_name="Simulation Speed",
                value=285.3,
                unit="ops/sec",
                threshold=200,
                status="ok",
                timestamp=datetime.utcnow().isoformat()
            ),
            PerformanceMetric(
                metric_name="Memory Usage",
                value=58.2,
                unit="%",
                threshold=80,
                status="ok",
                timestamp=datetime.utcnow().isoformat()
            ),
            PerformanceMetric(
                metric_name="CPU Usage",
                value=32.5,
                unit="%",
                threshold=75,
                status="ok",
                timestamp=datetime.utcnow().isoformat()
            ),
        ]
    
    @staticmethod
    def get_logs(limit: int = 50) -> List[LogEntry]:
        """Get recent logs"""
        logs = [
            LogEntry(
                timestamp=datetime.utcnow().isoformat(),
                level="INFO",
                source="phase_20",
                message="Deployment canary phase 1 completed successfully",
                details={"deployment_id": "deploy_001", "percent": 10}
            ),
            LogEntry(
                timestamp=(datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                level="INFO",
                source="phase_50",
                message="Agent consensus reached for refactoring proposal",
                details={"proposal_id": "prop_001", "votes": 4, "approved": 4}
            ),
            LogEntry(
                timestamp=(datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                level="INFO",
                source="phase_51",
                message="New architectural insight generated",
                details={"insight_type": "hotspot", "confidence": 0.92}
            ),
            LogEntry(
                timestamp=(datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                level="WARNING",
                source="phase_19",
                message="Memory usage elevated",
                details={"current": 72, "threshold": 80}
            ),
            LogEntry(
                timestamp=(datetime.utcnow() - timedelta(minutes=20)).isoformat(),
                level="INFO",
                source="system",
                message="System health check passed",
                details={"checks": 15, "passed": 15}
            ),
        ]
        return logs[:limit]
    
    @staticmethod
    def get_test_results() -> List[TestResult]:
        """Get test results"""
        return [
            TestResult(
                test_id="test_001",
                test_name="test_phases_19_20_50_51::TestProductionSecurityValidator::test_validator_initialization",
                status="passed",
                duration_seconds=0.245,
                message="PASSED"
            ),
            TestResult(
                test_id="test_002",
                test_name="test_phases_19_20_50_51::TestAgentOrchestrator::test_agent_registration",
                status="passed",
                duration_seconds=0.156,
                message="PASSED"
            ),
            TestResult(
                test_id="test_003",
                test_name="test_phases_19_20_50_51::TestAdvancedGraphReasoner::test_hotspot_analysis",
                status="passed",
                duration_seconds=0.512,
                message="PASSED"
            ),
            TestResult(
                test_id="test_004",
                test_name="test_infrastructure_phases39_42::TestMissionScheduler::test_schedule_daily_mission",
                status="passed",
                duration_seconds=0.089,
                message="PASSED"
            ),
        ]
    
    @staticmethod
    def get_dashboard_metrics() -> DashboardMetrics:
        """Get overall metrics"""
        return DashboardMetrics(
            agents_online=4,
            agents_offline=0,
            recent_messages=24,
            phases_in_progress=2,
            security_issues=0,
            performance_warnings=0,
            tests_passed=38,
            tests_failed=0
        )
    
    @staticmethod
    def get_decisions() -> List[Decision]:
        """Get AI decisions with reasoning"""
        now = datetime.utcnow()
        return [
            Decision(
                id="dec_001",
                task="Optimize resource allocation",
                agent_id="analyzer_1",
                action="increase_pool_size",
                confidence=0.92,
                context={
                    "goal": "Maximize throughput while minimizing cost",
                    "constraints": "Budget: $5000/month, Max instances: 50",
                    "available_options": "scale_up, scale_down, optimize_instances"
                },
                reasoning_chain=[
                    {
                        "stage": "Analysis",
                        "thought": "Current load is 85% of capacity. Trend shows 10% increase daily."
                    },
                    {
                        "stage": "Evaluation",
                        "thought": "Scaling costs $200/month per instance, ROI is 3:1 based on throughput gains"
                    },
                    {
                        "stage": "Decision",
                        "thought": "Increase pool by 3 instances for next 30 days, monitor performance"
                    }
                ],
                factors=[
                    {"name": "Current Load", "weight": 0.35, "contribution": "High priority signal"},
                    {"name": "Cost Analysis", "weight": 0.30, "contribution": "ROI positive"},
                    {"name": "Historical Trend", "weight": 0.25, "contribution": "Growing demand"},
                    {"name": "Risk Assessment", "weight": 0.10, "contribution": "Low risk"}
                ],
                parameters={
                    "pool_size_delta": 3,
                    "instance_type": "t3.large",
                    "duration_days": 30
                },
                validation={
                    "passed": True,
                    "score": 0.94,
                    "checks": [
                        {"name": "Budget Check", "passed": True, "detail": "Within 5K monthly budget"},
                        {"name": "Capacity Check", "passed": True, "detail": "Below 50 instance limit"},
                        {"name": "Safety Check", "passed": True, "detail": "No breaking changes"},
                    ]
                },
                outcome={
                    "success": True,
                    "result_description": "Successfully scaled to 13 instances. Throughput +12%, Load: 72%",
                    "learning_point": "Conservative scaling works better than aggressive"
                },
                timestamp=(now - timedelta(hours=2)).isoformat()
            ),
            Decision(
                id="dec_002",
                task="Validate security compliance",
                agent_id="validator_1",
                action="approve_deployment",
                confidence=0.87,
                context={
                    "goal": "Ensure security standards met before prod deployment",
                    "constraints": "Zero critical vulns, <3% medium severity",
                    "available_options": "approve, block, approve_with_conditions"
                },
                reasoning_chain=[
                    {"stage": "Assessment", "thought": "Scanning report shows 0 critical, 2 medium vulns"},
                    {"stage": "Evaluation", "thought": "Medium vulns are in dev dependencies, low prod impact"},
                    {"stage": "Approval", "thought": "Approve with condition: update dependencies in next sprint"}
                ],
                factors=[
                    {"name": "Vulnerability Count", "weight": 0.40, "contribution": "Within thresholds"},
                    {"name": "Patch Readiness", "weight": 0.35, "contribution": "2-3 day timeline"},
                    {"name": "Risk Tolerance", "weight": 0.25, "contribution": "Acceptable for prod"}
                ],
                parameters={"approval_status": "conditional", "next_review": "7_days"},
                validation={
                    "passed": True,
                    "score": 0.91,
                    "checks": [
                        {"name": "CVE Check", "passed": True, "detail": "All CVEs <7.0 severity"},
                        {"name": "Dependency Audit", "passed": True, "detail": "Licensed compliant"},
                        {"name": "SAST Scan", "passed": True, "detail": "No insecure patterns"}
                    ]
                },
                outcome=None,
                timestamp=(now - timedelta(hours=1)).isoformat()
            ),
            Decision(
                id="dec_003",
                task="Route request to optimal service",
                agent_id="executor_1",
                action="route_to_service_3",
                confidence=0.78,
                context={
                    "goal": "Minimize latency for API request",
                    "constraints": "Max 200ms response time",
                    "available_options": ["service_1", "service_2", "service_3", "service_backup"]
                },
                reasoning_chain=[
                    {"stage": "Status Check", "thought": "Service latencies: s1=145ms, s2=210ms, s3=89ms, backup=340ms"},
                    {"stage": "Load Assessment", "thought": "s3 has 40% capacity, can handle load"},
                    {"stage": "Routing", "thought": "Route to service_3 for lowest latency"}
                ],
                factors=[
                    {"name": "Service Latency", "weight": 0.45, "contribution": "s3 is fastest"},
                    {"name": "Load Capacity", "weight": 0.35, "contribution": "s3 has headroom"},
                    {"name": "Reliability", "weight": 0.20, "contribution": "All services healthy"}
                ],
                parameters={"target_service": "service_3", "timeout_ms": 200},
                validation={
                    "passed": True,
                    "score": 0.88,
                    "checks": [
                        {"name": "Service Health", "passed": True, "detail": "All services up"},
                        {"name": "Capacity", "passed": True, "detail": "Route has capacity"},
                        {"name": "SLA", "passed": True, "detail": "Meets <200ms SLA"}
                    ]
                },
                outcome={"success": True, "result_description": "Request completed in 92ms", "learning_point": "s3 consistently performs well"},
                timestamp=now.isoformat()
            )
        ]
    
    @staticmethod
    def get_missions() -> List[Mission]:
        """Get mission timelines"""
        now = datetime.utcnow()
        return [
            Mission(
                id="mis_001",
                name="Q1 2026 Production Hardening",
                description="Enterprise-grade security and performance upgrade",
                goal="Achieve SOC2 Type II compliance and 99.99% uptime SLA",
                status="in_progress",
                priority=1,
                stages=[
                    {
                        "name": "Goal",
                        "status": "completed",
                        "description": "Define hardening requirements and success criteria",
                        "start_time": (now - timedelta(days=14)).isoformat(),
                        "end_time": (now - timedelta(days=10)).isoformat(),
                        "milestones": ["Security audit completed", "Compliance framework selected"],
                        "issues": []
                    },
                    {
                        "name": "Plan",
                        "status": "completed",
                        "description": "Create implementation roadmap and resource allocation",
                        "start_time": (now - timedelta(days=10)).isoformat(),
                        "end_time": (now - timedelta(days=5)).isoformat(),
                        "milestones": ["Design docs approved", "Sprint plan finalized"],
                        "issues": []
                    },
                    {
                        "name": "Execute",
                        "status": "in_progress",
                        "description": "Implement security hardening and infrastructure updates",
                        "start_time": (now - timedelta(days=5)).isoformat(),
                        "end_time": None,
                        "milestones": ["TLS 1.3 enabled", "Rate limiting deployed"],
                        "issues": ["Delayed vendor cert responses"]
                    },
                    {
                        "name": "Validate",
                        "status": "pending",
                        "description": "Run comprehensive security and performance tests",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    },
                    {
                        "name": "PR",
                        "status": "pending",
                        "description": "Deploy to production with staged rollout",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    }
                ],
                agents_involved=[
                    {"agent_id": "security_lead", "role": "Security Architect", "status": "active"},
                    {"agent_id": "infra_coord", "role": "Infrastructure Orchestrator", "status": "active"},
                    {"agent_id": "validator_1", "role": "Quality Validator", "status": "active"}
                ],
                progress_percent=43,
                plan={
                    "strategy": "Multi-phase rollout with automated testing and gradual traffic migration",
                    "resources": {"engineers": 5, "budget_usd": 25000, "timeline_weeks": 8},
                    "estimated_duration": "2 weeks"
                },
                success_criteria=[
                    "SOC2 Type II audit passed",
                    "99.99% uptime achieved",
                    "All security tests passed",
                    "Zero data breaches"
                ],
                efficiency_score=0.87,
                quality_score=0.93,
                risk_level="medium",
                notes="On track for completion by end of month",
                timestamp=now.isoformat()
            ),
            Mission(
                id="mis_002",
                name="Multi-Agent Coordination Enhancement",
                description="Improve agent collaboration and decision consensus",
                goal="Reduce decision latency by 40% while improving consensus score to 95%",
                status="pending",
                priority=2,
                agents_involved=[
                    {"agent_id": "analyzer_1", "role": "Analysis Agent", "status": "active"},
                    {"agent_id": "validator_1", "role": "Validation Agent", "status": "active"},
                    {"agent_id": "executor_1", "role": "Execution Agent", "status": "active"}
                ],
                stages=[
                    {
                        "name": "Goal",
                        "status": "pending",
                        "description": "Define collaboration metrics and KPIs",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    },
                    {
                        "name": "Plan",
                        "status": "pending",
                        "description": "Design improved consensus algorithm",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    },
                    {
                        "name": "Execute",
                        "status": "pending",
                        "description": "Implement and test new protocol",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    },
                    {
                        "name": "Validate",
                        "status": "pending",
                        "description": "Benchmark improvements",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    },
                    {
                        "name": "PR",
                        "status": "pending",
                        "description": "Deploy enhanced coordination",
                        "start_time": None,
                        "end_time": None,
                        "milestones": [],
                        "issues": []
                    }
                ],
                progress_percent=0,
                plan={
                    "strategy": "Phased rollout with A/B testing of new consensus algorithm",
                    "resources": {"engineers": 3, "budget_usd": 15000, "timeline_weeks": 6},
                    "estimated_duration": "6 weeks"
                },
                success_criteria=[
                    "40% latency reduction",
                    "95% consensus score",
                    "Backward compatibility maintained"
                ],
                efficiency_score=0.0,
                quality_score=0.0,
                risk_level="low",
                notes="Scheduled to start next sprint",
                timestamp=now.isoformat()
            )
        ]
    
    @staticmethod
    def get_dependency_graph() -> DependencyGraph:
        """Get dependency graph"""
        now = datetime.utcnow()
        
        # Create nodes positioned in a logical graph layout
        nodes = [
            DependencyGraphNode(
                id="api_gateway",
                name="API Gateway",
                type="service",
                description="Main API entry point",
                x=300, y=100,
                inbound_count=120,
                outbound_count=4,
                avg_response_time=45.2,
                error_rate=0.001
            ),
            DependencyGraphNode(
                id="auth_svc",
                name="Auth Service",
                type="service",
                description="Authentication and authorization",
                x=100, y=250,
                inbound_count=115,
                outbound_count=2,
                avg_response_time=31.5,
                error_rate=0.0005
            ),
            DependencyGraphNode(
                id="agent_mgr",
                name="Agent Manager",
                type="module",
                description="Manages autonomous agents",
                x=300, y=250,
                inbound_count=45,
                outbound_count=8,
                avg_response_time=78.3,
                error_rate=0.002
            ),
            DependencyGraphNode(
                id="msg_bus",
                name="Message Bus",
                type="module",
                description="Agent-to-agent messaging",
                x=500, y=250,
                inbound_count=340,
                outbound_count=340,
                avg_response_time=12.1,
                error_rate=0.0002
            ),
            DependencyGraphNode(
                id="validator",
                name="Validator",
                type="function",
                description="Decision validation",
                x=200, y=400,
                inbound_count=89,
                outbound_count=5,
                avg_response_time=145.2,
                error_rate=0.003
            ),
            DependencyGraphNode(
                id="logger_svc",
                name="Logger Service",
                type="service",
                description="Centralized logging",
                x=600, y=400,
                inbound_count=450,
                outbound_count=1,
                avg_response_time=8.5,
                error_rate=0.0001
            ),
            DependencyGraphNode(
                id="cache",
                name="Cache Layer",
                type="module",
                description="Distributed caching",
                x=350, y=450,
                inbound_count=200,
                outbound_count=0,
                avg_response_time=3.2,
                error_rate=0.001
            ),
            DependencyGraphNode(
                id="db",
                name="Database",
                type="service",
                description="Persistent storage",
                x=100, y=550,
                inbound_count=95,
                outbound_count=0,
                avg_response_time=234.5,
                error_rate=0.0008
            ),
        ]
        
        edges = [
            DependencyGraphEdge(
                from_id="api_gateway",
                to_id="auth_svc",
                type="sync",
                calls=115,
                weight=2.0
            ),
            DependencyGraphEdge(
                from_id="api_gateway",
                to_id="agent_mgr",
                type="sync",
                calls=45,
                weight=1.5
            ),
            DependencyGraphEdge(
                from_id="agent_mgr",
                to_id="msg_bus",
                type="async",
                calls=340,
                weight=7.5
            ),
            DependencyGraphEdge(
                from_id="agent_mgr",
                to_id="validator",
                type="sync",
                calls=87,
                weight=2.0
            ),
            DependencyGraphEdge(
                from_id="agent_mgr",
                to_id="cache",
                type="sync",
                calls=120,
                weight=2.5
            ),
            DependencyGraphEdge(
                from_id="msg_bus",
                to_id="logger_svc",
                type="async",
                calls=340,
                weight=6.0
            ),
            DependencyGraphEdge(
                from_id="validator",
                to_id="logger_svc",
                type="async",
                calls=89,
                weight=2.0
            ),
            DependencyGraphEdge(
                from_id="cache",
                to_id="db",
                type="sync",
                calls=95,
                weight=2.0
            ),
            DependencyGraphEdge(
                from_id="auth_svc",
                to_id="db",
                type="sync",
                calls=80,
                weight=1.8
            ),
        ]
        
        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            timestamp=now.isoformat()
        )
    
    @staticmethod
    def get_mission_replay(mission_id: str) -> MissionReplayData:
        """Get detailed mission replay data with step-by-step execution"""
        now = datetime.utcnow()
        
        steps = [
            MissionReplayStep(
                step_number=1,
                type="agent_action",
                title="Repository Diff Detection",
                description="Agent scanned repository and detected significant changes in core modules",
                timestamp=(now - timedelta(minutes=10)).isoformat(),
                timestamp_display="00:00",
                agent_id="analyzer_1",
                active_services=[
                    {"name": "GitHub API", "status": "Reading repository"},
                    {"name": "Diff Engine", "status": "Analyzing changes"}
                ],
                performance={
                    "latency_ms": 245,
                    "status": "success",
                    "impact": "High"
                }
            ),
            MissionReplayStep(
                step_number=2,
                type="service_call",
                title="Load LLM Context",
                description="Loaded project context, architecture docs, and design patterns",
                timestamp=(now - timedelta(minutes=9)).isoformat(),
                timestamp_display="00:30",
                service_call="llm_context_loader.fetch('/docs/architecture')",
                active_services=[
                    {"name": "Cache Layer", "status": "Cache hit (82%)"},
                    {"name": "Document Store", "status": "Fetching context"}
                ],
                performance={
                    "latency_ms": 132,
                    "status": "success",
                    "impact": "Medium"
                }
            ),
            MissionReplayStep(
                step_number=3,
                type="decision",
                title="Impact Analysis Decision",
                description="LLM analyzed changes and determined impact scope",
                timestamp=(now - timedelta(minutes=8)).isoformat(),
                timestamp_display="01:00",
                agent_id="analyzer_1",
                decision={
                    "action": "Full integration testing required",
                    "confidence": 0.94,
                    "reasoning": "Changes touch security and auth layers"
                },
                active_services=[
                    {"name": "LLM Service", "status": "Processing analysis"},
                    {"name": "Knowledge Base", "status": "Pattern matching"}
                ],
                performance={
                    "latency_ms": 1850,
                    "status": "success",
                    "impact": "Critical"
                }
            ),
            MissionReplayStep(
                step_number=4,
                type="agent_action",
                title="Plan Generation",
                description="Orchestrator generated detailed execution plan with checkpoints",
                timestamp=(now - timedelta(minutes=7)).isoformat(),
                timestamp_display="01:30",
                agent_id="executor_1",
                active_services=[
                    {"name": "Planning Engine", "status": "Generating plan"},
                    {"name": "Resource Allocator", "status": "Reserving capacity"}
                ],
                performance={
                    "latency_ms": 892,
                    "status": "success",
                    "impact": "High"
                }
            ),
            MissionReplayStep(
                step_number=5,
                type="service_call",
                title="Dependency Resolution",
                description="Resolved all affected modules and generated call graph",
                timestamp=(now - timedelta(minutes=6)).isoformat(),
                timestamp_display="02:00",
                service_call="dependency_mapper.resolve_graph(changed_modules)",
                active_services=[
                    {"name": "Graph Database", "status": "Querying dependencies"},
                    {"name": "Module Analyzer", "status": "Processing graph"}
                ],
                performance={
                    "latency_ms": 445,
                    "status": "success",
                    "impact": "High"
                }
            ),
            MissionReplayStep(
                step_number=6,
                type="agent_action",
                title="Code Review Preparation",
                description="Generated comprehensive code review with detailed comments",
                timestamp=(now - timedelta(minutes=5)).isoformat(),
                timestamp_display="02:30",
                agent_id="validator_1",
                active_services=[
                    {"name": "Code Analyzer", "status": "Analyzing patterns"},
                    {"name": "Test Generator", "status": "Creating test cases"}
                ],
                performance={
                    "latency_ms": 1234,
                    "status": "success",
                    "impact": "High"
                }
            ),
            MissionReplayStep(
                step_number=7,
                type="decision",
                title="Test Strategy Selection",
                description="Decided on comprehensive testing approach with regression tests",
                timestamp=(now - timedelta(minutes=4)).isoformat(),
                timestamp_display="03:00",
                agent_id="validator_1",
                decision={
                    "action": "Run full test suite + integration tests",
                    "confidence": 0.89,
                    "reasoning": "Security changes require comprehensive validation"
                },
                active_services=[
                    {"name": "Test Orchestrator", "status": "Planning tests"},
                    {"name": "CI/CD Pipeline", "status": "Preparing environment"}
                ],
                performance={
                    "latency_ms": 678,
                    "status": "success",
                    "impact": "Critical"
                }
            ),
            MissionReplayStep(
                step_number=8,
                type="service_call",
                title="Unit Tests Execution",
                description="Executed 156 unit tests across all affected modules",
                timestamp=(now - timedelta(minutes=3)).isoformat(),
                timestamp_display="03:45",
                service_call="ci_pipeline.run_unit_tests()",
                active_services=[
                    {"name": "Test Runner", "status": "Executing 156 tests"},
                    {"name": "Result Aggregator", "status": "Collecting results"}
                ],
                performance={
                    "latency_ms": 3200,
                    "status": "success",
                    "impact": "High"
                }
            ),
            MissionReplayStep(
                step_number=9,
                type="service_call",
                title="Integration Tests Execution",
                description="Executed 42 integration tests to verify module interactions",
                timestamp=(now - timedelta(minutes=2)).isoformat(),
                timestamp_display="04:30",
                service_call="ci_pipeline.run_integration_tests()",
                active_services=[
                    {"name": "Integration Test Suite", "status": "Running 42 tests"},
                    {"name": "Mock Services", "status": "Simulating dependencies"}
                ],
                performance={
                    "latency_ms": 4100,
                    "status": "success",
                    "impact": "Critical"
                }
            ),
            MissionReplayStep(
                step_number=10,
                type="validation",
                title="Validation Results",
                description": "All tests passed: 156 unit + 42 integration. 100% coverage on changed code",
                timestamp=(now - timedelta(minutes=1)).isoformat(),
                timestamp_display="05:00",
                agent_id="validator_1",
                active_services=[
                    {"name": "Validation Engine", "status": "Complete ✓"},
                    {"name": "Report Generator", "status": "Generating report"}
                ],
                performance={
                    "latency_ms": 234,
                    "status": "success",
                    "impact": "High"
                }
            ),
            MissionReplayStep(
                step_number=11,
                type="decision",
                title="Deployment Approval",
                description="All validation passed. Decision: Proceed with deployment",
                timestamp=now.isoformat(),
                timestamp_display="05:30",
                agent_id="executor_1",
                decision={
                    "action": "Approved for production deployment",
                    "confidence": 0.96,
                    "reasoning": "All tests passed, validation complete, ready for prod"
                },
                active_services=[
                    {"name": "Approval Engine", "status": "Approved ✓"}
                ],
                performance={
                    "latency_ms": 145,
                    "status": "success",
                    "impact": "Critical"
                }
            ),
            MissionReplayStep(
                step_number=12,
                type="deployment",
                title="PR Creation and Deployment",
                description="Created PR with all comments and pushed to production with canary deployment",
                timestamp=(now + timedelta(minutes=1)).isoformat(),
                timestamp_display="06:00",
                service_call="github_api.create_pr() + deploy_service.canary_deploy()",
                active_services=[
                    {"name": "GitHub API", "status": "PR created #3847"},
                    {"name": "Deploy Pipeline", "status": "Canary: 10% live"},
                    {"name": "Monitoring", "status": "Watching metrics"}
                ],
                performance={
                    "latency_ms": 892,
                    "status": "success",
                    "impact": "Critical"
                }
            )
        ]
        
        return MissionReplayData(
            mission_id="mis_001",
            mission_name="Q1 2026 Production Hardening",
            mission_description="Enterprise-grade security and performance upgrade",
            status="completed",
            steps=steps,
            agents_involved=[
                {"agent_id": "analyzer_1", "role": "Analysis Agent"},
                {"agent_id": "executor_1", "role": "Execution Agent"},
                {"agent_id": "validator_1", "role": "Validation Agent"}
            ],
            total_duration="06:00",
            efficiency_score=92.5,
            quality_score=97.8,
            timestamp=now.isoformat()
        )


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Piddy Dashboard API",
    description="Real-time monitoring for Piddy autonomous system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use mock data for now (replace with real data integration)
generator = MockDataGenerator()


# ============================================================================
# API ENDPOINTS - OVERVIEW
# ============================================================================

@app.get("/api/health")
async def health_check() -> Dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/system/overview")
async def system_overview() -> Dict:
    """Get system overview"""
    return {
        "system": generator.get_system_status(),
        "metrics": generator.get_dashboard_metrics(),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# API ENDPOINTS - AGENTS
# ============================================================================

@app.get("/api/agents")
async def get_agents() -> List[AgentStatus]:
    """Get all agent statuses"""
    return generator.get_agents()


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str) -> AgentStatus:
    """Get specific agent status"""
    agents = generator.get_agents()
    for agent in agents:
        if agent.agent_id == agent_id:
            return agent
    return None


# ============================================================================
# API ENDPOINTS - MESSAGES & COMMUNICATION
# ============================================================================

@app.get("/api/messages")
async def get_messages(limit: int = 100) -> List[AgentMessage]:
    """Get recent agent messages"""
    messages = generator.get_agent_messages()
    return messages[:limit]


@app.get("/api/messages/{agent_id}")
async def get_agent_messages(agent_id: str, limit: int = 50) -> List[AgentMessage]:
    """Get messages for specific agent"""
    all_messages = generator.get_agent_messages()
    filtered = [
        m for m in all_messages
        if m.sender_id == agent_id or m.receiver_id == agent_id
    ]
    return filtered[:limit]


@app.websocket("/ws/messages")
async def websocket_messages(websocket: WebSocket):
    """WebSocket for real-time message stream"""
    await websocket.accept()
    try:
        while True:
            # Send latest messages every 2 seconds
            messages = generator.get_agent_messages()
            await websocket.send_json({
                "type": "messages",
                "data": [m.dict() for m in messages],
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass


# ============================================================================
# API ENDPOINTS - PHASES
# ============================================================================

@app.get("/api/phases")
async def get_phases() -> List[PhaseStatus]:
    """Get all phase statuses"""
    return generator.get_phases()


@app.get("/api/phases/{phase_id}")
async def get_phase(phase_id: str) -> PhaseStatus:
    """Get specific phase status"""
    phases = generator.get_phases()
    for phase in phases:
        if phase.phase_id == phase_id:
            return phase
    return None


# ============================================================================
# API ENDPOINTS - SECURITY
# ============================================================================

@app.get("/api/security/audit")
async def get_security_audit() -> SecurityAuditResult:
    """Get latest security audit results"""
    return generator.get_security_info()


@app.get("/api/security/issues")
async def get_security_issues() -> Dict:
    """Get security issues"""
    audit = generator.get_security_info()
    return {
        "critical_failures": audit.critical_failures,
        "failed_checks": audit.failed_checks,
        "is_safe": audit.is_production_safe,
        "timestamp": audit.timestamp
    }


# ============================================================================
# API ENDPOINTS - PERFORMANCE
# ============================================================================

@app.get("/api/metrics/performance")
async def get_performance_metrics() -> List[PerformanceMetric]:
    """Get all performance metrics"""
    return generator.get_performance_metrics()


@app.get("/api/metrics/graph")
async def get_metric_graph(metric_name: str, period_hours: int = 24) -> Dict:
    """Get metric data for graphing"""
    return {
        "metric_name": metric_name,
        "period_hours": period_hours,
        "data_points": 288,  # 5-minute intervals for 24 hours
        "samples": [
            {"timestamp": datetime.utcnow().isoformat(), "value": 45.2 + (i * 0.1)}
            for i in range(12)  # Last 12 samples
        ]
    }


# ============================================================================
# API ENDPOINTS - LOGS
# ============================================================================

@app.get("/api/logs")
async def get_logs(limit: int = 50, level: Optional[str] = None) -> List[LogEntry]:
    """Get logs"""
    logs = generator.get_logs(limit)
    if level:
        logs = [l for l in logs if l.level == level]
    return logs


@app.get("/api/logs/{source}")
async def get_logs_by_source(source: str, limit: int = 50) -> List[LogEntry]:
    """Get logs from specific source"""
    all_logs = generator.get_logs(100)
    filtered = [l for l in all_logs if l.source == source]
    return filtered[:limit]


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket for real-time log stream"""
    await websocket.accept()
    try:
        while True:
            # Send latest logs every 5 seconds
            logs = generator.get_logs(20)
            await websocket.send_json({
                "type": "logs",
                "data": [l.dict() for l in logs],
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass


# ============================================================================
# API ENDPOINTS - TESTS
# ============================================================================

@app.get("/api/tests")
async def get_tests() -> List[TestResult]:
    """Get test results"""
    return generator.get_test_results()


@app.get("/api/tests/summary")
async def get_tests_summary() -> Dict:
    """Get test summary"""
    tests = generator.get_test_results()
    passed = len([t for t in tests if t.status == "passed"])
    failed = len([t for t in tests if t.status == "failed"])
    skipped = len([t for t in tests if t.status == "skipped"])
    
    return {
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": (passed / len(tests) * 100) if len(tests) > 0 else 0
    }


# ============================================================================
# API ENDPOINTS - ANALYTICS
# ============================================================================

@app.get("/api/analytics/agent-reputation")
async def get_agent_reputation() -> Dict:
    """Get agent reputation analytics"""
    agents = generator.get_agents()
    return {
        "agents": [
            {
                "agent_id": a.agent_id,
                "role": a.role,
                "reputation_score": a.reputation_score,
                "success_rate": (a.correct_decisions / a.total_decisions * 100) if a.total_decisions > 0 else 0,
            }
            for a in agents
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/analytics/message-activity")
async def get_message_activity() -> Dict:
    """Get message activity analytics"""
    messages = generator.get_agent_messages()
    
    # Group by type
    by_type = {}
    for msg in messages:
        by_type[msg.message_type] = by_type.get(msg.message_type, 0) + 1
    
    return {
        "total_messages": len(messages),
        "by_type": by_type,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/analytics/deployment-history")
async def get_deployment_history() -> Dict:
    """Get deployment history"""
    return {
        "deployments": [
            {
                "deployment_id": "deploy_001",
                "version": "2.0.0",
                "status": "success",
                "duration_seconds": 1245,
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            },
            {
                "deployment_id": "deploy_000",
                "version": "1.9.5",
                "status": "success",
                "duration_seconds": 892,
                "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()
            },
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# NEW TRANSPARENCY ENDPOINTS - Phase 3 Enhancement
# ============================================================================

@app.get("/api/decisions")
async def get_decisions() -> List[Decision]:
    """Get AI decisions with reasoning chains and validation"""
    return MockDataGenerator.get_decisions()


@app.get("/api/missions")
async def get_missions() -> List[Mission]:
    """Get mission timelines with stage progression"""
    return MockDataGenerator.get_missions()


@app.get("/api/missions/{mission_id}/replay")
async def get_mission_replay(mission_id: str) -> MissionReplayData:
    """Get detailed mission replay with step-by-step execution"""
    return MockDataGenerator.get_mission_replay(mission_id)


@app.get("/api/graph/dependencies")
async def get_dependency_graph() -> DependencyGraph:
    """Get system dependency graph"""
    return MockDataGenerator.get_dependency_graph()


# ============================================================================
# SERVE DASHBOARD FRONTEND
# ============================================================================

@app.get("/")
async def root():
    """Serve dashboard homepage"""
    return FileResponse("frontend/dist/index.html", media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
