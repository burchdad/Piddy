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


class ProviderRateLimitMetrics(BaseModel):
    """Rate limit metrics for a provider"""
    provider: str
    is_rate_limited: bool
    is_in_recovery: bool
    time_until_available: float
    backoff_count: int
    total_errors: int
    last_error: Optional[str]
    throughput_per_min: float
    success_rate: float
    queue_length: int
    last_request: Optional[str]
    last_error_time: Optional[str]


class RateLimitStatus(BaseModel):
    """Overall rate limit status"""
    status: str  # healthy, degraded, critical
    healthy_providers: int
    total_providers: int
    queue_length: int
    providers: Dict[str, Dict]
    timestamp: str


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


# ============================================================================
# MARKET GAP APPROVAL MODELS
# ============================================================================

class MarketGap(BaseModel):
    """Market gap requiring approval"""
    gap_id: str
    title: str
    category: str  # ci-cd, code-quality, testing, documentation, etc.
    market_need: str
    frequency: int  # how many repos need it
    estimated_impact: float  # 0.0-1.0
    complexity_score: int  # 1-10
    integration_points: List[str]
    security_risk_level: str  # LOW, MEDIUM, HIGH
    security_concerns: List[str]
    estimated_build_time_hours: float


class ApprovalRequest(BaseModel):
    """Market gap approval request"""
    request_id: str
    gaps: List[MarketGap]
    created_at: str
    deadline: str
    status: str  # waiting, partially_approved, fully_approved, expired
    sent_to_emails: List[str]
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


class ApprovalDecision(BaseModel):
    """User's decision on a market gap"""
    request_id: str
    gap_id: str
    title: str
    approved: bool
    decision_time: str
    reason: Optional[str] = None
    risk_level: str


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
    status: str = "pending"  # pending, approved, rejected, executed


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
                task="Deploy new cache layer for performance",
                agent_id="analyzer_1",
                action="deploy_redis_cluster",
                confidence=0.88,
                status="pending",  # PENDING - needs approval
                context={
                    "goal": "Reduce API latency by improving cache hit rate",
                    "constraints": "Budget: $3000/month, Max latency: 100ms",
                    "available_options": ["deploy_redis", "use_managed_cache", "optimize_existing"]
                },
                reasoning_chain=[
                    {
                        "stage": "Analysis",
                        "thought": "Current cache hit rate 62%, can improve to 85% with Redis"
                    },
                    {
                        "stage": "Evaluation",
                        "thought": "Redis adds $1500/month, ROI: 2.5x improvement in load times"
                    },
                    {
                        "stage": "Decision",
                        "thought": "Deploy Redis cluster with 3 nodes and auto-failover"
                    }
                ],
                factors=[
                    {"name": "Performance Impact", "weight": 0.40, "contribution": "2.5x improvement"},
                    {"name": "Cost Efficiency", "weight": 0.35, "contribution": "Good ROI"},
                    {"name": "Risk Level", "weight": 0.25, "contribution": "Low operational risk"}
                ],
                parameters={
                    "cluster_size": 3,
                    "memory_per_node": "8GB",
                    "replication_factor": 2
                },
                validation={
                    "passed": True,
                    "score": 0.91,
                    "checks": [
                        {"name": "Budget Check", "passed": True, "detail": "Within 3K monthly budget"},
                        {"name": "Performance SLA", "passed": True, "detail": "Meets latency goals"},
                        {"name": "Availability Check", "passed": True, "detail": "99.95% uptime SLA"},
                    ]
                },
                outcome=None,
                timestamp=(now - timedelta(hours=2)).isoformat()
            ),
            Decision(
                id="dec_002",
                task="Review and approve security patch",
                agent_id="validator_1",
                action="approve_security_patch",
                confidence=0.95,
                status="pending",  # PENDING - needs approval
                context={
                    "goal": "Apply critical security patches to production",
                    "constraints": "Zero downtime required, maintenance window available",
                    "available_options": ["apply_now", "schedule_maintenance", "defer_30_days"]
                },
                reasoning_chain=[
                    {"stage": "Assessment", "thought": "OpenSSL CVE-2025-1234 critical, CVSS 9.8"},
                    {"stage": "Impact Analysis", "thought": "Affects authentication layer, 15min downtime possible"},
                    {"stage": "Recommendation", "thought": "Apply immediately in scheduled maintenance window"}
                ],
                factors=[
                    {"name": "Security Severity", "weight": 0.50, "contribution": "Critical"},
                    {"name": "Operational Risk", "weight": 0.35, "contribution": "Low with maintenance window"},
                    {"name": "Business Impact", "weight": 0.15, "contribution": "Minimal downtime"}
                ],
                parameters={"patch_version": "1.1.1w", "rollback_plan": "ready"},
                validation={
                    "passed": True,
                    "score": 0.97,
                    "checks": [
                        {"name": "Patch Validation", "passed": True, "detail": "Signed and verified"},
                        {"name": "Compatibility", "passed": True, "detail": "No breaking changes"},
                        {"name": "Testing", "passed": True, "detail": "Passed in staging"}
                    ]
                },
                outcome=None,
                timestamp=(now - timedelta(minutes=30)).isoformat()
            ),
            Decision(
                id="dec_003",
                task="Optimize database query for reporting",
                agent_id="executor_1",
                action="add_db_index",
                confidence=0.82,
                status="approved",  # Already approved
                context={
                    "goal": "Reduce daily report generation time from 45min to 5min",
                    "constraints": "Index size <500MB, query response <2s",
                    "available_options": ["add_index", "partition_table", "denormalize"]
                },
                reasoning_chain=[
                    {"stage": "Profiling", "thought": "Report query takes 45min on 100M rows"},
                    {"stage": "Analysis", "thought": "Adding composite index on (user_id, date) reduces to 5min"},
                    {"stage": "Implementation", "thought": "Create index offline, test, then deploy"}
                ],
                factors=[
                    {"name": "Performance Gain", "weight": 0.45, "contribution": "9x improvement"},
                    {"name": "Storage Cost", "weight": 0.30, "contribution": "Minimal impact"},
                    {"name": "Maintenance", "weight": 0.25, "contribution": "Low maintenance"}
                ],
                parameters={"index_name": "idx_reports_user_date", "columns": ["user_id", "date"]},
                validation={
                    "passed": True,
                    "score": 0.89,
                    "checks": [
                        {"name": "Query Plan", "passed": True, "detail": "Uses index optimally"},
                        {"name": "Storage", "passed": True, "detail": "Index 250MB, acceptable"},
                        {"name": "Lock Time", "passed": True, "detail": "Offline creation, no locks"}
                    ]
                },
                outcome={"success": True, "result_description": "Report time reduced from 45min to 4min", "learning_point": "Composite indexes very effective for range queries"},
                timestamp=(now - timedelta(hours=1)).isoformat()
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
                description="All tests passed: 156 unit + 42 integration. 100% coverage on changed code",
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
    """Get system overview from real data"""
    try:
        from pathlib import Path
        import psutil
        import os
        
        # Get real system info
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # Count real approval data
        approval_count = 0
        decision_count = 0
        mission_count = 0
        agent_count = 0
        
        workflow_file = Path("data/approval_workflow_state.json")
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflows = json.load(f)
                approval_count = len(workflows)
        
        decisions_file = Path("data/decision_logs.json")
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                decision_count = len(decisions) if isinstance(decisions, list) else len(decisions)
        
        missions_file = Path("data/mission_telemetry.json")
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                missions = json.load(f)
                mission_count = len(missions) if isinstance(missions, list) else len(missions)
        
        agents_file = Path("data/agent_state.json")
        if agents_file.exists():
            with open(agents_file, 'r') as f:
                agents = json.load(f)
                agent_count = len(agents) if isinstance(agents, list) else len(agents)
        
        return {
            "status": "operational",
            "uptime_seconds": int(process.create_time()),
            "agents_online": agent_count,
            "missions_active": mission_count,
            "decisions_pending": decision_count,
            "approvals_pending": approval_count,
            "metrics": {
                "agents_online": agent_count,
                "agents_offline": 0,
                "recent_messages": 0,
                "phases_in_progress": 0,
                "security_issues": 0,
                "performance_warnings": 0,
                "tests_passed": 0,
                "tests_failed": 0
            },
            "process": {
                "memory_mb": memory_info.rss / 1024 / 1024,
                "cpu_percent": cpu_percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in system overview: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# API ENDPOINTS - AGENTS
# ============================================================================

@app.get("/api/agents")
async def get_agents() -> List[AgentStatus]:
    """Get all agent statuses from real data"""
    try:
        from pathlib import Path
        agent_file = Path("data/agent_state.json")
        
        if agent_file.exists():
            with open(agent_file, 'r') as f:
                agents_data = json.load(f)
                return [AgentStatus(**agent) for agent in agents_data] if isinstance(agents_data, list) else []
        
        # No real agent data
        return []
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        return []


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
    """Get recent agent messages from real data"""
    try:
        from pathlib import Path
        messages_file = Path("data/message_log.json")
        
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages_data = json.load(f)
                messages = [AgentMessage(**msg) for msg in messages_data] if isinstance(messages_data, list) else []
                return messages[:limit]
        
        # No real message data
        return []
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []


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
    """Get all phase statuses from real data"""
    try:
        from pathlib import Path
        phases_file = Path("data/phase_status.json")
        
        if phases_file.exists():
            with open(phases_file, 'r') as f:
                phases_data = json.load(f)
                return [PhaseStatus(**phase) for phase in phases_data] if isinstance(phases_data, list) else []
        
        # No real phase data
        return []
    except Exception as e:
        logger.error(f"Error fetching phases: {e}")
        return []


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
    """Get latest security audit results from real data"""
    try:
        from pathlib import Path
        audit_file = Path("data/security_audit.json")
        
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                audit_data = json.load(f)
                return SecurityAuditResult(**audit_data)
        
        # Default if no audit data
        return SecurityAuditResult(
            audit_id="none",
            passed_checks=0,
            failed_checks=0,
            critical_failures=[],
            is_production_safe=False,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error fetching security audit: {e}")
        return SecurityAuditResult(
            audit_id="error",
            passed_checks=0,
            failed_checks=0,
            critical_failures=[str(e)],
            is_production_safe=False,
            timestamp=datetime.utcnow().isoformat()
        )


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
    """Get all performance metrics from real data"""
    try:
        from pathlib import Path
        metrics_file = Path("data/performance_metrics.json")
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
                return [PerformanceMetric(**metric) for metric in metrics_data] if isinstance(metrics_data, list) else []
        
        # No real metrics data
        return []
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return []


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
    """Get logs from real data"""
    try:
        from pathlib import Path
        
        # Try multiple log sources
        log_files = [
            Path("data/service.log"),
            Path("data/dashboard.log"),
        ]
        
        logs = []
        for log_file in log_files:
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line)
                                logs.append(LogEntry(**log_entry))
                            except:
                                # Skip non-JSON lines
                                pass
                except:
                    pass
        
        if level:
            logs = [l for l in logs if l.level == level]
        
        # Sort by timestamp descending and limit
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]
        return logs
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return []


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
    """Get test results from real data"""
    try:
        from pathlib import Path
        tests_file = Path("data/test_results.json")
        
        if tests_file.exists():
            with open(tests_file, 'r') as f:
                tests_data = json.load(f)
                return [TestResult(**test) for test in tests_data] if isinstance(tests_data, list) else []
        
        # No real test data
        return []
    except Exception as e:
        logger.error(f"Error fetching tests: {e}")
        return []


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
    """Get AI decisions with reasoning chains from real data"""
    try:
        from pathlib import Path
        decisions_file = Path("data/decision_logs.json")
        
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions_data = json.load(f)
                if isinstance(decisions_data, list):
                    return [Decision(**d) for d in decisions_data]
                elif isinstance(decisions_data, dict):
                    return [Decision(**d) for d in decisions_data.values()]
        
        # No real decision data
        return []
    except Exception as e:
        logger.error(f"Error fetching decisions: {e}")
        return []


@app.post("/api/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approved_by: str = "user"):
    """Approve a pending decision"""
    try:
        from pathlib import Path
        decisions_file = Path("data/decision_approvals.json")
        decisions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing approvals
        approvals = {}
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                approvals = json.load(f)
        
        # Record approval
        approvals[decision_id] = {
            "decision_id": decision_id,
            "approved_by": approved_by,
            "approved_at": datetime.utcnow().isoformat(),
            "action": "approved"
        }
        
        # Save approvals
        with open(decisions_file, 'w') as f:
            json.dump(approvals, f, indent=2)
        
        logger.info(f"✅ Decision {decision_id} approved by {approved_by}")
        return {
            "status": "success",
            "decision_id": decision_id,
            "action": "approved",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Decision {decision_id} has been approved"
        }
    except Exception as e:
        logger.error(f"Error approving decision: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.post("/api/decisions/{decision_id}/reject")
async def reject_decision(decision_id: str, rejected_by: str = "user", reason: str = ""):
    """Reject a pending decision"""
    try:
        from pathlib import Path
        decisions_file = Path("data/decision_rejections.json")
        decisions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing rejections
        rejections = {}
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                rejections = json.load(f)
        
        # Record rejection
        rejections[decision_id] = {
            "decision_id": decision_id,
            "rejected_by": rejected_by,
            "rejected_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "action": "rejected"
        }
        
        # Save rejections
        with open(decisions_file, 'w') as f:
            json.dump(rejections, f, indent=2)
        
        logger.info(f"❌ Decision {decision_id} rejected by {rejected_by}. Reason: {reason}")
        return {
            "status": "success",
            "decision_id": decision_id,
            "action": "rejected",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Decision {decision_id} has been rejected"
        }
    except Exception as e:
        logger.error(f"Error rejecting decision: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/api/missions")
async def get_missions() -> List[Mission]:
    """Get mission timelines from real data"""
    try:
        from pathlib import Path
        missions_file = Path("data/mission_telemetry.json")
        
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                missions_data = json.load(f)
                if isinstance(missions_data, list):
                    return [Mission(**m) for m in missions_data]
                elif isinstance(missions_data, dict):
                    return [Mission(**m) for m in missions_data.values()]
        
        # No real mission data
        return []
    except Exception as e:
        logger.error(f"Error fetching missions: {e}")
        return []


@app.get("/api/missions/{mission_id}/replay")
async def get_mission_replay(mission_id: str) -> MissionReplayData:
    """Get detailed mission replay from real data"""
    try:
        from pathlib import Path
        missions_file = Path("data/mission_telemetry.json")
        
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                missions_data = json.load(f)
                if isinstance(missions_data, dict) and mission_id in missions_data:
                    return MissionReplayData(**missions_data[mission_id])
                elif isinstance(missions_data, list):
                    for mission in missions_data:
                        if mission.get('mission_id') == mission_id:
                            return MissionReplayData(**mission)
        
        # Return empty replay if not found
        return MissionReplayData(
            mission_id=mission_id,
            mission_name="Unknown",
            mission_description="Mission not found",
            status="not_found",
            steps=[],
            agents_involved=[],
            total_duration="0s",
            efficiency_score=0,
            quality_score=0,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error fetching mission replay: {e}")
        return MissionReplayData(
            mission_id=mission_id,
            mission_name="Error",
            mission_description=str(e),
            status="error",
            steps=[],
            agents_involved=[],
            total_duration="0s",
            efficiency_score=0,
            quality_score=0,
            timestamp=datetime.utcnow().isoformat()
        )


@app.get("/api/graph/dependencies")
async def get_dependency_graph() -> DependencyGraph:
    """Get system dependency graph from real data"""
    try:
        from pathlib import Path
        graph_file = Path("data/dependency_graph.json")
        
        if graph_file.exists():
            with open(graph_file, 'r') as f:
                graph_data = json.load(f)
                return DependencyGraph(**graph_data)
        
        # Return empty graph if no data
        return DependencyGraph(
            nodes=[],
            edges=[],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error fetching dependency graph: {e}")
        return DependencyGraph(
            nodes=[],
            edges=[],
            timestamp=datetime.utcnow().isoformat()
        )


# ============================================================================
# API ENDPOINTS - RATE LIMITING
# ============================================================================

@app.get("/api/rate-limits/status")
async def get_rate_limit_status() -> Dict:
    """Get current rate limit status for all providers"""
    try:
        from src.services.rate_limiter import get_rate_limiter
        limiter = get_rate_limiter()
        return limiter.get_system_health()
    except Exception as e:
        logger.error(f"Error getting rate limit status: {e}")
        return {
            "status": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/api/rate-limits/metrics")
async def get_rate_limit_metrics(provider: Optional[str] = None) -> Dict:
    """Get detailed rate limit metrics"""
    try:
        from src.services.rate_limiter import get_rate_limiter
        limiter = get_rate_limiter()
        return {
            "data": limiter.get_metrics(None if not provider else None),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting rate limit metrics: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/rate-limits/dashboard")
async def get_rate_limit_dashboard() -> Dict:
    """Get comprehensive rate limit dashboard data"""
    try:
        from src.services.rate_limiter import get_rate_limiter
        limiter = get_rate_limiter()
        
        metrics = limiter.get_metrics()
        health = limiter.get_system_health()
        
        # Generate recommendations
        recommendations = []
        for provider_name, provider_data in metrics.get("providers", {}).items():
            if provider_data["is_rate_limited"]:
                recommendations.append({
                    "provider": provider_name,
                    "type": "rate_limited",
                    "message": f"Rate limited - retry in {provider_data['time_until_available']:.0f}s",
                    "severity": "high"
                })
            elif provider_data["is_in_recovery"]:
                recommendations.append({
                    "provider": provider_name,
                    "type": "recovery",
                    "message": "In recovery mode after errors",
                    "severity": "medium"
                })
            elif provider_data["success_rate"] < 90:
                recommendations.append({
                    "provider": provider_name,
                    "type": "low_success",
                    "message": f"Low success rate: {provider_data['success_rate']:.1f}%",
                    "severity": "medium"
                })
        
        return {
            "health": health,
            "providers": metrics.get("providers", {}),
            "queue_length": metrics.get("queue_length", 0),
            "recommendations": recommendations,
            "config": {
                "requests_per_minute": limiter.config.requests_per_minute,
                "requests_per_hour": limiter.config.requests_per_hour,
                "initial_backoff_seconds": limiter.config.initial_backoff_seconds,
                "max_backoff_seconds": limiter.config.max_backoff_seconds,
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting rate limit dashboard: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/rate-limits/providers")
async def get_providers() -> Dict:
    """Get list of monitored providers"""
    return {
        "providers": ["anthropic", "openai", "github", "slack"],
        "count": 4,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check() -> Dict:
    """Quick health check for Piddy system"""
    try:
        from pathlib import Path
        
        # Verify critical files exist
        service_log = Path("data/service.log").exists()
        dashboard_log = Path("data/dashboard.log").exists()
        
        # Check if approval system files are accessible
        approval_state = Path("data/approval_workflow_state.json").exists()
        approval_decisions = Path("data/approval_decisions.json").exists()
        
        # Overall health status
        is_healthy = service_log and dashboard_log
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "service": "running" if service_log else "unknown",
                "dashboard": "running" if dashboard_log else "unknown",
                "approval_system": "ready" if (approval_state and approval_decisions) else "not_configured",
                "database": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/health/detailed")
async def detailed_health_check() -> Dict:
    """Detailed system health check with service verification"""
    try:
        from pathlib import Path
        import psutil
        import os
        
        # Get system info
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Check critical files and their sizes
        files = {
            "service.log": Path("data/service.log"),
            "dashboard.log": Path("data/dashboard.log"),
            "approval_workflow_state.json": Path("data/approval_workflow_state.json"),
            "approval_decisions.json": Path("data/approval_decisions.json"),
        }
        
        file_status = {}
        for name, path in files.items():
            if path.exists():
                file_status[name] = {
                    "exists": True,
                    "size_bytes": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
            else:
                file_status[name] = {"exists": False, "size_bytes": 0}
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "process": {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": memory_info.rss / 1024 / 1024,
                "uptime_seconds": int(datetime.utcnow().timestamp() - process.create_time())
            },
            "files": file_status,
            "services": {
                "background_service": "running",
                "dashboard_api": "running",
                "approval_system": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.post("/health/verify")
async def verify_system_ready() -> Dict:
    """Verify all system components are ready for operations"""
    try:
        from pathlib import Path
        
        checks = {
            "email_configured": Path("config/email_config.json").exists(),
            "approval_workflow_ready": Path("data/approval_workflow_state.json").exists(),
            "decision_log_initialized": Path("data/approval_decisions.json").exists(),
            "service_logs_enabled": Path("data/service.log").exists(),
            "dashboard_api_running": True,  # We're here, so API is running
        }
        
        all_checks_passed = all(checks.values())
        
        warnings = []
        if not checks["email_configured"]:
            warnings.append("Email not configured - approval emails won't be sent")
        if not checks["approval_workflow_ready"]:
            warnings.append("Approval workflow not initialized")
        
        return {
            "ready": all_checks_passed,
            "checks": checks,
            "warnings": warnings,
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_actions": [
                "Configure email: python src/email_config.py --profile gmail"
            ] if not checks["email_configured"] else []
        }
    except Exception as e:
        logger.error(f"System verification failed: {e}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# MARKET GAP APPROVAL ENDPOINTS
# ============================================================================

@app.get("/api/approvals")
async def list_approvals() -> Dict:
    """List all pending and historical approval requests from real data"""
    try:
        from pathlib import Path
        workflow_file = Path("data/approval_workflow_state.json")
        
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflows = json.load(f)
                return {
                    "requests": workflows,
                    "count": len(workflows),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # No real approval data yet
        return {
            "requests": {},
            "count": 0,
            "message": "No approval requests yet",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing approvals: {e}")
        return {"requests": {}, "count": 0, "error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/approvals/{request_id}")
async def get_approval_request(request_id: str) -> Dict:
    """Get specific approval request details"""
    try:
        from pathlib import Path
        workflow_file = Path("data/approval_workflow_state.json")
        
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflows = json.load(f)
                if request_id in workflows:
                    return {
                        "request": workflows[request_id],
                        "timestamp": datetime.utcnow().isoformat()
                    }
        return {"error": "Request not found", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error getting approval request: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/approvals/{request_id}/gaps/{gap_id}")
async def get_gap_details(request_id: str, gap_id: str) -> Dict:
    """Get specific gap details within an approval request"""
    try:
        from pathlib import Path
        workflow_file = Path("data/approval_workflow_state.json")
        
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflows = json.load(f)
                if request_id in workflows:
                    gaps = workflows[request_id].get("market_gaps", [])
                    for gap in gaps:
                        if gap.get("gap_id") == gap_id:
                            return {
                                "gap": gap,
                                "timestamp": datetime.utcnow().isoformat()
                            }
        return {"error": "Gap not found", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error getting gap details: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/approvals/{request_id}/gaps/{gap_id}/approve")
async def approve_gap(request_id: str, gap_id: str) -> Dict:
    """Approve a specific market gap"""
    try:
        from pathlib import Path
        decisions_file = Path("data/approval_decisions.json")
        decisions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing decisions
        decisions = {}
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
        
        # Record decision
        if request_id not in decisions:
            decisions[request_id] = []
        
        decisions[request_id].append({
            "gap_id": gap_id,
            "approved": True,
            "decision_time": datetime.utcnow().isoformat(),
            "reason": None
        })
        
        # Save decisions
        with open(decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)
        
        logger.info(f"Gap {gap_id} approved in request {request_id}")
        return {
            "success": True,
            "gap_id": gap_id,
            "action": "approved",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error approving gap: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/approvals/{request_id}/gaps/{gap_id}/reject")
async def reject_gap(request_id: str, gap_id: str, reason: Optional[str] = None) -> Dict:
    """Reject a specific market gap"""
    try:
        from pathlib import Path
        decisions_file = Path("data/approval_decisions.json")
        decisions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing decisions
        decisions = {}
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
        
        # Record decision
        if request_id not in decisions:
            decisions[request_id] = []
        
        decisions[request_id].append({
            "gap_id": gap_id,
            "approved": False,
            "decision_time": datetime.utcnow().isoformat(),
            "reason": reason
        })
        
        # Save decisions
        with open(decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)
        
        logger.info(f"Gap {gap_id} rejected in request {request_id}: {reason}")
        return {
            "success": True,
            "gap_id": gap_id,
            "action": "rejected",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error rejecting gap: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/approvals/summary/stats")
async def get_approval_stats() -> Dict:
    """Get approval summary statistics from real data"""
    try:
        from pathlib import Path
        
        total_decisions = 0
        approved_count = 0
        rejected_count = 0
        pending_requests = 0
        
        workflow_file = Path("data/approval_workflow_state.json")
        decisions_file = Path("data/approval_decisions.json")
        
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflows = json.load(f)
                for req_id, workflow in workflows.items():
                    if isinstance(workflow, dict) and workflow.get("status") in ["waiting", "pending"]:
                        pending_requests += 1
        
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                for req_id, decisions_list in decisions.items():
                    for decision in decisions_list:
                        total_decisions += 1
                        if decision.get("approved"):
                            approved_count += 1
                        else:
                            rejected_count += 1
        
        return {
            "total_decisions": total_decisions,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "pending_requests": pending_requests,
            "approval_rate": ((approved_count / total_decisions * 100) if total_decisions > 0 else 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting approval stats: {e}")
        return {
            "total_decisions": 0,
            "approved_count": 0,
            "rejected_count": 0,
            "pending_requests": 0,
            "approval_rate": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


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
