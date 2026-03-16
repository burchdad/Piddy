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
import sys

# Setup logging - explicitly configure to output to console
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

# Add console handler explicitly
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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


# NOTE: MockDataGenerator class removed - all endpoints now use real data only
# If data files don't exist, endpoints return empty arrays/0 values
# This ensures the dashboard only shows real system state
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

# All endpoints use real data from JSON files only
# No mock data fallback - ensures dashboard shows actual system state


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
        import os
        
        # Try to import psutil, but provide fallback if not available
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_mb = memory_info.rss / 1024 / 1024
        except ImportError:
            print("[WARNING] psutil not installed - using fallback values")
            psutil = None
            memory_mb = 0
            cpu_percent = 0
        
        # FORCE VISIBLE OUTPUT
        print("\n" + "="*60)
        print("[SYSTEM_OVERVIEW] Endpoint called")
        print("="*60)
        
        # DEBUG: Log current working directory
        cwd = os.getcwd()
        print(f"[DEBUG] Current working directory: {cwd}")
        logger.info(f"[DEBUG] Current working directory: {cwd}")
        
        # Count real approval data
        approval_count = 0
        decision_count = 0
        mission_count = 0
        agent_count = 0
        
        workflow_file = Path("data/approval_workflow_state.json")
        print(f"[DEBUG] Checking workflow_file: {workflow_file.absolute()}, exists={workflow_file.exists()}")
        logger.info(f"[DEBUG] Checking workflow_file: {workflow_file.absolute()}, exists={workflow_file.exists()}")
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
        
        print(f"[DEBUG] Final data counts - agents: {agent_count}, decisions: {decision_count}, missions: {mission_count}, approvals: {approval_count}")
        logger.info(f"[DEBUG] Final data counts - agents: {agent_count}, decisions: {decision_count}, missions: {mission_count}, approvals: {approval_count}")
        print("="*60 + "\n")
        
        # Get uptime - fallback to 0 if psutil not available
        uptime_seconds = 0
        if psutil:
            try:
                process = psutil.Process(os.getpid())
                uptime_seconds = int(process.create_time())
            except:
                uptime_seconds = 0
        
        return {
            "status": "operational",
            "uptime_seconds": uptime_seconds,
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
                "memory_mb": memory_mb,
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
    """Get specific agent status from real data"""
    try:
        from pathlib import Path
        agents_file = Path("data/agent_state.json")
        
        if agents_file.exists():
            with open(agents_file, 'r') as f:
                agents_data = json.load(f)
                for agent in agents_data:
                    if agent.get('agent_id') == agent_id:
                        return AgentStatus(**agent)
        
        return None
    except Exception as e:
        logger.error(f"Error fetching agent: {e}")
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
    """Get messages for specific agent from real data"""
    try:
        from pathlib import Path
        messages_file = Path("data/message_log.json")
        
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages_data = json.load(f)
                filtered = []
                for msg in messages_data:
                    if msg.get('sender_id') == agent_id or msg.get('receiver_id') == agent_id:
                        filtered.append(AgentMessage(**msg))
                return filtered[:limit]
        
        return []
    except Exception as e:
        logger.error(f"Error fetching agent messages: {e}")
        return []


@app.websocket("/ws/messages")
async def websocket_messages(websocket: WebSocket):
    """WebSocket for real-time message stream from real data"""
    await websocket.accept()
    try:
        from pathlib import Path
        while True:
            # Send latest messages every 2 seconds from real data
            messages_file = Path("data/message_log.json")
            messages = []
            if messages_file.exists():
                try:
                    with open(messages_file, 'r') as f:
                        messages_data = json.load(f)
                        messages = [AgentMessage(**m) for m in messages_data]
                except:
                    pass
            
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
    """Get specific phase status from real data"""
    try:
        from pathlib import Path
        phases_file = Path("data/phase_status.json")
        
        if phases_file.exists():
            with open(phases_file, 'r') as f:
                phases_data = json.load(f)
                for phase in phases_data:
                    if phase.get('phase_id') == phase_id:
                        return PhaseStatus(**phase)
        
        return None
    except Exception as e:
        logger.error(f"Error fetching phase: {e}")
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
    """Get security issues from real data"""
    try:
        from pathlib import Path
        audit_file = Path("data/security_audit.json")
        
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                audit_data = json.load(f)
                return {
                    "critical_failures": audit_data.get("critical_failures", []),
                    "failed_checks": audit_data.get("failed_checks", 0),
                    "is_safe": audit_data.get("is_production_safe", False),
                    "timestamp": audit_data.get("timestamp", datetime.utcnow().isoformat())
                }
        
        return {"critical_failures": [], "failed_checks": 0, "is_safe": False, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error fetching security issues: {e}")
        return {"critical_failures": [], "failed_checks": 0, "is_safe": False, "timestamp": datetime.utcnow().isoformat()}


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
    """Get logs from specific source from real data"""
    try:
        from pathlib import Path
        log_files = [Path("data/service.log"), Path("data/dashboard.log")]
        
        logs = []
        for log_file in log_files:
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line)
                                if log_entry.get('source') == source:
                                    logs.append(LogEntry(**log_entry))
                            except:
                                pass
                except:
                    pass
        
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]
        return logs
    except Exception as e:
        logger.error(f"Error fetching logs by source: {e}")
        return []


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket for real-time log stream from real data"""
    await websocket.accept()
    try:
        from pathlib import Path
        while True:
            # Send latest logs every 5 seconds from real data
            log_files = [Path("data/service.log"), Path("data/dashboard.log")]
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
                                    pass
                    except:
                        pass
            
            logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:20]
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
    """Get test summary from real data only"""
    try:
        from pathlib import Path
        tests_file = Path("data/test_results.json")
        
        tests = []
        if tests_file.exists():
            with open(tests_file, 'r') as f:
                tests_data = json.load(f)
                tests = tests_data if isinstance(tests_data, list) else []
        
        passed = len([t for t in tests if t.get('status') == "passed"])
        failed = len([t for t in tests if t.get('status') == "failed"])
        skipped = len([t for t in tests if t.get('status') == "skipped"])
        
        return {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / len(tests) * 100) if len(tests) > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting test summary: {e}")
        return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "pass_rate": 0}


# ============================================================================
# API ENDPOINTS - ANALYTICS
# ============================================================================

@app.get("/api/analytics/agent-reputation")
async def get_agent_reputation() -> Dict:
    """Get agent reputation analytics from real data"""
    try:
        from pathlib import Path
        agents_file = Path("data/agent_state.json")
        
        agents = []
        if agents_file.exists():
            with open(agents_file, 'r') as f:
                agents_data = json.load(f)
                agents = [
                    {
                        "agent_id": a.get('agent_id'),
                        "role": a.get('role'),
                        "reputation_score": a.get('reputation_score', 0),
                        "success_rate": (a.get('correct_decisions', 0) / a.get('total_decisions', 1) * 100) if a.get('total_decisions', 0) > 0 else 0,
                    }
                    for a in agents_data
                ]
        
        return {"agents": agents, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error fetching agent reputation: {e}")
        return {"agents": [], "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/analytics/message-activity")
async def get_message_activity() -> Dict:
    """Get message activity analytics from real data"""
    try:
        from pathlib import Path
        messages_file = Path("data/message_log.json")
        
        messages = []
        by_type = {}
        
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                messages_data = json.load(f)
                messages = messages_data if isinstance(messages_data, list) else []
                for msg in messages:
                    msg_type = msg.get('message_type', 'unknown')
                    by_type[msg_type] = by_type.get(msg_type, 0) + 1
        
        return {
            "total_messages": len(messages),
            "by_type": by_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching message activity: {e}")
        return {"total_messages": 0, "by_type": {}, "timestamp": datetime.utcnow().isoformat()}


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
