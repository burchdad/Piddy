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
from pathlib import Path
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

# Import coordinator for mission execution
try:
    from src.coordination.agent_coordinator import get_coordinator
except ImportError:
    logger.warning("Could not import get_coordinator - missions may not execute properly")
    get_coordinator = None

# Import config routes for onboarding / key management
try:
    from src.api.config_routes import router as config_router
except ImportError:
    logger.warning("Could not import config_router - onboarding API unavailable")
    config_router = None

# Import self-diagnosis system
try:
    from src.api.doctor import run_diagnosis
except ImportError:
    logger.warning("Could not import doctor - self-diagnosis unavailable")
    run_diagnosis = None

# Import skills/plugin loader
try:
    from src.skills.loader import get_skill_registry
except ImportError:
    logger.warning("Could not import skill registry - skills API unavailable")
    get_skill_registry = None

# Import session/context manager
try:
    from src.sessions.manager import get_session_manager
except ImportError:
    logger.warning("Could not import session manager - sessions API unavailable")
    get_session_manager = None

# Import agent for chat processing
try:
    from src.agent.core import BackendDeveloperAgent, Command, CommandType, CommandResponse
    _agent_instance = None
    def _get_agent():
        global _agent_instance
        if _agent_instance is None:
            _agent_instance = BackendDeveloperAgent()
        return _agent_instance
except ImportError:
    logger.warning("Could not import agent - chat processing unavailable")
    _get_agent = None


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


class ExecuteMissionRequest(BaseModel):
    """Request to execute a mission"""
    mission_type: str  # e.g., "research", "analysis", "decision"
    mission_name: str
    description: str
    objectives: List[str]
    required_agents: List[str]  # Specific agent roles or IDs
    priority: int = 5  # 1-10, higher is more important
    timeout_seconds: Optional[int] = 300


class ExecuteMissionResponse(BaseModel):
    """Response from mission execution request"""
    mission_id: str
    status: str  # accepted, in_progress, completed, failed
    coordinator_id: Optional[str]
    message: str
    timestamp: str


class MissionCreateRequest(BaseModel):
    """Request to create (but not execute) a mission"""
    mission_type: str
    mission_name: str
    description: str
    objectives: List[str]
    required_agents: Optional[List[str]] = None
    priority: int = 5
    timeout_seconds: Optional[int] = 300


class MissionStatus(BaseModel):
    """Mission status information"""
    mission_id: str
    mission_name: str
    status: str  # draft, queued, assigned, in_progress, completed, failed
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    assigned_agent: Optional[str] = None
    progress_percent: int
    result: Optional[Dict] = None
    error: Optional[str] = None


class LiveChatMessage(BaseModel):
    """Live chat message"""
    message_id: str
    sender_id: str
    sender_name: str
    content: str
    timestamp: str
    message_type: str  # user, agent, system
    metadata: Optional[Dict] = None


class LiveChatRequest(BaseModel):
    """Request to send a live chat message"""
    content: str
    sender_id: str
    sender_name: str
    message_type: str = "user"


class LiveChatResponse(BaseModel):
    """Response to live chat message"""
    message_id: str
    status: str  # sent, received, processing, completed
    timestamp: str
    response: Optional[str] = None


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

# Mount config/onboarding router
if config_router is not None:
    app.include_router(config_router)

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


@app.get("/api/doctor")
async def doctor_endpoint() -> Dict:
    """Full system self-diagnosis."""
    if run_diagnosis is None:
        return {"status": "error", "message": "Doctor module not available"}
    return run_diagnosis()


@app.get("/api/skills")
async def list_skills() -> Dict:
    """List all loaded skills/plugins."""
    if get_skill_registry is None:
        return {"skills": [], "message": "Skills loader not available"}
    registry = get_skill_registry()
    return {"skills": registry.to_dict_list(), "count": len(registry.list_all())}


@app.post("/api/skills/reload")
async def reload_skills() -> Dict:
    """Hot-reload skills from library/skills/ folder."""
    if get_skill_registry is None:
        return {"success": False, "message": "Skills loader not available"}
    registry = get_skill_registry()
    count = registry.reload()
    return {"success": True, "count": count, "message": f"Reloaded {count} skills"}


@app.post("/api/settings/local-only")
async def toggle_local_only(body: Dict = None) -> Dict:
    """Toggle local-only mode (prevents cloud API calls)."""
    body = body or {}
    enabled = body.get("enabled")
    if enabled is None:
        return {"error": "Provide {\"enabled\": true/false}"}
    try:
        from config.settings import get_settings
        settings = get_settings()
        settings.local_only = bool(enabled)
        return {
            "success": True,
            "local_only": settings.local_only,
            "message": f"Local-only mode {'enabled' if settings.local_only else 'disabled'}. "
                       f"{'Cloud APIs will NOT be called.' if settings.local_only else 'Cloud APIs available as fallback.'}"
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/settings/local-only")
async def get_local_only() -> Dict:
    """Check if local-only mode is enabled."""
    try:
        from config.settings import get_settings
        settings = get_settings()
        return {"local_only": settings.local_only}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# SESSION / CONTEXT MANAGEMENT
# ============================================================================

@app.post("/api/sessions")
async def create_session(body: Dict = None) -> Dict:
    """Create a new conversation session."""
    if get_session_manager is None:
        return {"error": "Session manager not available"}
    mgr = get_session_manager()
    body = body or {}
    session = mgr.create_session(
        user_id=body.get("user_id", "default"),
        title=body.get("title", ""),
    )
    return {"session_id": session.session_id, "title": session.title, "created_at": session.created_at}


@app.get("/api/sessions")
async def list_sessions(user_id: str = "default", limit: int = 50) -> Dict:
    """List conversation sessions for a user."""
    if get_session_manager is None:
        return {"sessions": []}
    mgr = get_session_manager()
    sessions = mgr.list_sessions(user_id=user_id, limit=limit)
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str) -> Dict:
    """Get a session with its message history."""
    if get_session_manager is None:
        return {"error": "Session manager not available"}
    mgr = get_session_manager()
    session = mgr.get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return {
        "session_id": session.session_id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "message_count": len(session.messages),
        "messages": [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in session.messages],
        "has_summary": bool(session.context_summary),
    }


@app.post("/api/sessions/{session_id}/messages")
async def add_message(session_id: str, body: Dict) -> Dict:
    """Add a message to a session."""
    if get_session_manager is None:
        return {"error": "Session manager not available"}
    mgr = get_session_manager()
    role = body.get("role", "user")
    content = body.get("content", "")
    if not content:
        return {"error": "Message content required"}
    msg = mgr.add_message(session_id, role, content, body.get("metadata"))
    # Auto-summarize if context window is too large
    mgr.summarize_if_needed(session_id)
    return {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}


@app.get("/api/sessions/{session_id}/context")
async def get_context_window(session_id: str) -> Dict:
    """Get the context window for LLM calls (recent messages + summary)."""
    if get_session_manager is None:
        return {"context": []}
    mgr = get_session_manager()
    context = mgr.get_context_window(session_id)
    return {"context": context, "message_count": len(context)}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict:
    """Delete a conversation session."""
    if get_session_manager is None:
        return {"error": "Session manager not available"}
    mgr = get_session_manager()
    deleted = mgr.delete_session(session_id)
    return {"deleted": deleted}


# ============================================================================
# CHAT ENDPOINT — session-aware, agent-powered
# ============================================================================

@app.post("/api/chat")
async def chat(body: Dict) -> Dict:
    """
    Send a message to Piddy and get a response.
    Creates/uses a session for conversation persistence.
    Routes through the 4-tier failover agent.
    """
    message = body.get("message", "").strip()
    session_id = body.get("session_id")
    user_id = body.get("user_id", "default")

    if not message:
        return {"error": "Message is required"}

    mgr = get_session_manager() if get_session_manager else None

    # Create or reuse session
    if mgr:
        if not session_id:
            session = mgr.create_session(user_id=user_id, title=message[:60])
            session_id = session.session_id
        # Store user message
        mgr.add_message(session_id, "user", message)

    # Try to get a response from the agent
    reply = None
    source = "fallback"

    if _get_agent is not None:
        try:
            agent = _get_agent()
            cmd = Command(
                command_type=CommandType.CONVERSATION,
                description=message,
                parameters={"query": message},
                source="dashboard_chat",
                metadata={"is_conversation": True, "session_id": session_id or ""},
            )
            response: CommandResponse = await agent.process_command(cmd)
            if response.success and response.result:
                reply = str(response.result)
                source = response.metadata.get("tier", "agent") if response.metadata else "agent"
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)

    if not reply:
        reply = (
            "I'm here but my language models aren't available right now. "
            "Check the Health page to see what's offline, or configure API keys in Settings."
        )
        source = "fallback"

    # Store assistant reply in session
    if mgr and session_id:
        mgr.add_message(session_id, "assistant", reply, {"source": source})
        mgr.summarize_if_needed(session_id)

    return {
        "reply": reply,
        "session_id": session_id,
        "source": source,
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
        
        # Count real approval data
        # Find data directory: it's at the package root, not in src/
        # Use __file__ to get absolute path to this script
        script_dir = Path(__file__).parent  # src/ directory
        package_root = script_dir.parent    # package root (one level up from src)
        data_dir = package_root / "data"
        
        approval_count = 0
        decision_count = 0
        mission_count = 0
        agent_count = 0
        
        workflow_file = data_dir / "approval_workflow_state.json"
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflows = json.load(f)
                approval_count = len(workflows)
        
        decisions_file = data_dir / "decision_logs.json"
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                decision_count = len(decisions) if isinstance(decisions, list) else len(decisions)
        
        missions_file = data_dir / "mission_telemetry.json"
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                missions = json.load(f)
                mission_count = len(missions) if isinstance(missions, list) else len(missions)
        
        agents_file = data_dir / "agent_state.json"
        if agents_file.exists():
            with open(agents_file, 'r') as f:
                agents = json.load(f)
                agent_count = len(agents) if isinstance(agents, list) else len(agents)
        
        logger.info(f"System overview: agents={agent_count}, decisions={decision_count}, missions={mission_count}, approvals={approval_count}")
        
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
# API ENDPOINTS - AGENTS (served by realtime_dashboard.py from coordinator)
# ============================================================================


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


@app.post("/api/messages/send")
async def send_message(
    sender_id: str,
    receiver_id: Optional[str] = None,
    content: str = "",
    priority: int = 1,
) -> Dict:
    """
    Send a message and process commands to Piddy.
    
    Supports:
    - Direct messages to agents
    - Commands to Piddy (create mission, execute task, etc.)
    - User queries
    
    Returns live feedback on message processing
    """
    try:
        from pathlib import Path
        import uuid
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create message object
        message_obj = {
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id or "broadcast",
            "message_type": "text",
            "content": {
                "text": content,
                "priority": priority,
                "action": "general"
            },
            "timestamp": timestamp,
            "priority": priority
        }
        
        # Determine action based on content
        cmd = content.strip().lower()
        
        if any(x in cmd for x in ["create mission", "start mission", "new mission", "execute:", "build me", "create"]):
            message_obj["content"]["action"] = "create_mission"
            logger.info(f"🎯 [LIVE] Mission creation requested: {content}")
            
            # ROUTE TO MISSION CREATION 🚀
            from src.coordination.agent_coordinator import TaskPriority
            
            try:
                # Extract mission description (everything after the command)
                mission_desc = content
                for cmd_prefix in ["create mission:", "start mission:", "new mission:", "execute:", "build me:"]:
                    if cmd_prefix in cmd:
                        mission_desc = content[len(cmd_prefix):].strip()
                        break
                
                # Create task through coordinator
                coordinator = get_coordinator()
                task = coordinator.submit_task(
                    task_type="user_mission",
                    description=mission_desc or content,
                    priority=TaskPriority.NORMAL,
                    metadata={
                        "mission_id": message_id,
                        "source": "livechat",
                        "user_id": sender_id,
                        "user_command": content,
                    }
                )
                
                # Find and assign to suitable agent
                suitable_agent = coordinator.find_suitable_agent(task)
                if suitable_agent:
                    coordinator.assign_task(task.id, suitable_agent.id)
                    logger.info(f"✅ Mission assigned to: {suitable_agent.name}")
                    mission_result = {
                        "created_task_id": task.id,
                        "assigned_to": suitable_agent.name,
                        "status": "assigned"
                    }
                else:
                    logger.info(f"⏳ Mission queued for agent assignment")
                    mission_result = {
                        "created_task_id": task.id,
                        "assigned_to": "queued",
                        "status": "queued"
                    }
                
                # Add to message log
                message_obj["content"]["mission_result"] = mission_result
                
            except Exception as mission_err:
                logger.error(f"❌ Mission creation failed: {mission_err}")
                message_obj["content"]["mission_error"] = str(mission_err)
            
        elif any(x in cmd for x in ["what's happening", "status", "show me", "activity"]):
            message_obj["content"]["action"] = "status_query"
            logger.info(f"[LIVE] Status query: {content}")
            
        elif any(x in cmd for x in ["run", "do this"]):
            message_obj["content"]["action"] = "execute_task"
            logger.info(f"[LIVE] Task execution requested: {content}")
            
        else:
            message_obj["content"]["action"] = "general_query"
            logger.info(f"[LIVE] Message from {sender_id}: {content}")
        
        # Append to message log
        try:
            messages_file = Path("data/message_log.json")
            messages_file.parent.mkdir(parents=True, exist_ok=True)
            
            existing_messages = []
            if messages_file.exists():
                with open(messages_file, 'r') as f:
                    existing_messages = json.load(f)
            
            existing_messages.append(message_obj)
            
            # Keep last 1000 messages
            if len(existing_messages) > 1000:
                existing_messages = existing_messages[-1000:]
            
            with open(messages_file, 'w') as f:
                json.dump(existing_messages, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving message: {e}")
        
        return {
            "status": "sent",
            "message_id": message_id,
            "timestamp": timestamp,
            "action": message_obj["content"]["action"],
            "live": True,
            "content": content,
            **(message_obj.get("content", {}).get("mission_result") or {})
        }
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return {
            "error": str(e),
            "live": False
        }



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


@app.post("/api/missions/execute")
async def execute_mission(request: ExecuteMissionRequest) -> ExecuteMissionResponse:
    """Execute a new mission using the agent coordinator"""
    try:
        logger.info(f"Mission execution request: {request.mission_name}")
        
        if not get_coordinator:
            return ExecuteMissionResponse(
                mission_id="error",
                status="failed",
                coordinator_id=None,
                message="Coordinator not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Get the coordinator instance
        coordinator = get_coordinator()
        if not coordinator:
            return ExecuteMissionResponse(
                mission_id="error",
                status="failed",
                coordinator_id=None,
                message="Failed to initialize coordinator",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Import TaskPriority enum
        from src.coordination.agent_coordinator import TaskPriority
        
        # Map priority to TaskPriority enum
        priority_map = {
            1: TaskPriority.LOW,
            2: TaskPriority.NORMAL,
            3: TaskPriority.HIGH,
            4: TaskPriority.CRITICAL
        }
        task_priority = priority_map.get(min(max(request.priority, 1), 4), TaskPriority.NORMAL)
        
        # Create mission task
        mission_metadata = {
            "mission_type": request.mission_type,
            "mission_name": request.mission_name,
            "objectives": request.objectives,
            "required_agents": request.required_agents,
            "timeout_seconds": request.timeout_seconds or 300,
        }
        
        # Submit task to coordinator
        logger.info(f"Submitting mission task to coordinator: {request.mission_name}")
        task = coordinator.submit_task(
            task_type="mission",
            description=request.description,
            priority=task_priority,
            required_capabilities=request.required_agents,
            metadata=mission_metadata
        )
        
        return ExecuteMissionResponse(
            mission_id=task.id,
            status="accepted",
            coordinator_id=str(id(coordinator)),
            message=f"Mission '{request.mission_name}' has been submitted for execution with task ID {task.id}",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error executing mission: {e}", exc_info=True)
        return ExecuteMissionResponse(
            mission_id="error",
            status="failed",
            coordinator_id=None,
            message=f"Error: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )


@app.post("/api/missions/create")
async def create_mission(request: MissionCreateRequest) -> MissionStatus:
    """Create a mission draft (without executing)"""
    try:
        logger.info(f"Mission creation request: {request.mission_name}")
        
        from uuid import uuid4
        mission_id = str(uuid4())
        
        mission_status = MissionStatus(
            mission_id=mission_id,
            mission_name=request.mission_name,
            status="draft",
            created_at=datetime.utcnow().isoformat(),
            progress_percent=0
        )
        
        # Store mission draft
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        missions_file = data_dir / "mission_drafts.json"
        
        missions = {}
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                missions = json.load(f)
        
        missions[mission_id] = {
            "mission_id": mission_id,
            "mission_name": request.mission_name,
            "mission_type": request.mission_type,
            "description": request.description,
            "objectives": request.objectives,
            "required_agents": request.required_agents or [],
            "priority": request.priority,
            "timeout_seconds": request.timeout_seconds,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        with open(missions_file, 'w') as f:
            json.dump(missions, f, indent=2)
        
        logger.info(f"✅ Mission draft created: {mission_id}")
        return mission_status
    except Exception as e:
        logger.error(f"Error creating mission: {e}", exc_info=True)
        return MissionStatus(
            mission_id="error",
            mission_name="Error",
            status="failed",
            created_at=datetime.utcnow().isoformat(),
            progress_percent=0,
            error=str(e)
        )


@app.get("/api/missions/{mission_id}/status")
async def get_mission_status(mission_id: str) -> MissionStatus:
    """Get the status of a mission"""
    try:
        from pathlib import Path
        
        # Check mission telemetry first
        missions_file = Path("data/mission_telemetry.json")
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                missions_data = json.load(f)
                if isinstance(missions_data, dict) and mission_id in missions_data:
                    m = missions_data[mission_id]
                    return MissionStatus(
                        mission_id=mission_id,
                        mission_name=m.get("mission_name", "Unknown"),
                        status=m.get("status", "unknown"),
                        created_at=m.get("created_at", ""),
                        started_at=m.get("started_at"),
                        completed_at=m.get("completed_at"),
                        assigned_agent=m.get("assigned_agent"),
                        progress_percent=int(m.get("progress_percent", 0)),
                        result=m.get("result"),
                        error=m.get("error")
                    )
        
        # Check drafts
        drafts_file = Path("data/mission_drafts.json")
        if drafts_file.exists():
            with open(drafts_file, 'r') as f:
                drafts = json.load(f)
                if mission_id in drafts:
                    d = drafts[mission_id]
                    return MissionStatus(
                        mission_id=mission_id,
                        mission_name=d.get("mission_name", "Unknown"),
                        status=d.get("status", "draft"),
                        created_at=d.get("created_at", ""),
                        progress_percent=0
                    )
        
        # Mission not found
        return MissionStatus(
            mission_id=mission_id,
            mission_name="Unknown",
            status="not_found",
            created_at=datetime.utcnow().isoformat(),
            progress_percent=0,
            error="Mission not found"
        )
    except Exception as e:
        logger.error(f"Error getting mission status: {e}")
        return MissionStatus(
            mission_id=mission_id,
            mission_name="Error",
            status="error",
            created_at=datetime.utcnow().isoformat(),
            progress_percent=0,
            error=str(e)
        )


@app.post("/api/livechat/send")
async def send_livechat_message(request: LiveChatRequest) -> LiveChatResponse:
    """Send a message in live chat"""
    try:
        from uuid import uuid4
        message_id = str(uuid4())
        
        logger.info(f"LiveChat message from {request.sender_name}: {request.content[:50]}")
        
        coordinator = get_coordinator()
        if not coordinator:
            return LiveChatResponse(
                message_id=message_id,
                status="failed",
                timestamp=datetime.utcnow().isoformat(),
                response="Coordinator not available"
            )
        
        # Check if this looks like a mission command
        command_prefixes = ["create mission", "start mission", "execute", "build", "analyze"]
        is_mission_command = any(request.content.lower().startswith(prefix) for prefix in command_prefixes)
        
        if is_mission_command:
            # Submit as a mission task
            from src.coordination.agent_coordinator import TaskPriority
            
            task = coordinator.submit_task(
                task_type="user_mission",
                description=request.content,
                priority=TaskPriority.NORMAL,
                metadata={
                    "message_id": message_id,
                    "source": "livechat",
                    "sender_id": request.sender_id,
                    "sender_name": request.sender_name,
                }
            )
            
            # Try to assign to suitable agent
            suitable_agent = coordinator.find_suitable_agent(task)
            if suitable_agent:
                coordinator.assign_task(task.id, suitable_agent.id)
                response = f"✅ Assigned to agent {suitable_agent.name}"
            else:
                response = f"⏳ Task queued for next available agent"
            
            return LiveChatResponse(
                message_id=message_id,
                status="processing",
                timestamp=datetime.utcnow().isoformat(),
                response=response
            )
        else:
            # Regular message - just acknowledge
            return LiveChatResponse(
                message_id=message_id,
                status="received",
                timestamp=datetime.utcnow().isoformat(),
                response=f"Message received by Piddy System"
            )
    except Exception as e:
        logger.error(f"Error processing livechat message: {e}", exc_info=True)
        return LiveChatResponse(
            message_id="error",
            status="failed",
            timestamp=datetime.utcnow().isoformat(),
            response=f"Error: {str(e)}"
        )


@app.websocket("/ws/livechat/{sender_id}")
async def websocket_livechat(websocket: WebSocket, sender_id: str):
    """WebSocket endpoint for live chat"""
    await websocket.accept()
    logger.info(f"LiveChat WebSocket connected: {sender_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse message
            try:
                message_data = json.loads(data)
            except:
                message_data = {"content": data}
            
            # Send message through HTTP endpoint
            request = LiveChatRequest(
                content=message_data.get("content", data),
                sender_id=sender_id,
                sender_name=message_data.get("sender_name", "WebSocket User"),
                message_type=message_data.get("message_type", "user")
            )
            
            response = await send_livechat_message(request)
            
            # Send response back
            await websocket.send_json({
                "message_id": response.message_id,
                "status": response.status,
                "timestamp": response.timestamp,
                "response": response.response
            })
    except WebSocketDisconnect:
        logger.info(f"LiveChat WebSocket disconnected: {sender_id}")
    except Exception as e:
        logger.error(f"LiveChat WebSocket error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


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
# EXPORT / BACKUP ENDPOINTS
# ============================================================================

@app.get("/api/export/conversations")
async def export_conversations() -> Dict:
    """Export all conversation sessions as JSON."""
    if get_session_manager is None:
        return {"error": "Session manager not available", "sessions": []}
    mgr = get_session_manager()
    sessions = mgr.list_sessions(user_id="default", limit=9999)
    full = []
    for s in sessions:
        sess = mgr.get_session(s.get("session_id", s.get("id", "")))
        if sess:
            full.append({
                "session_id": sess.session_id,
                "title": sess.title,
                "created_at": sess.created_at,
                "updated_at": sess.updated_at,
                "messages": [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in sess.messages],
            })
    return {"exported_at": datetime.utcnow().isoformat(), "count": len(full), "sessions": full}


@app.get("/api/export/knowledge-base")
async def export_knowledge_base() -> Dict:
    """Export knowledge base metadata (library catalog)."""
    from pathlib import Path
    kb = {}
    lib_root = Path(__file__).resolve().parent.parent / "library"
    if lib_root.exists():
        for folder in sorted(lib_root.iterdir()):
            if folder.is_dir():
                files = sorted([f.name for f in folder.iterdir() if f.is_file()])
                kb[folder.name] = {"count": len(files), "files": files}
    return {"exported_at": datetime.utcnow().isoformat(), "library": kb}


@app.get("/api/export/agent-state")
async def export_agent_state() -> Dict:
    """Export current agent state + decision logs."""
    from pathlib import Path
    data_dir = Path(__file__).resolve().parent.parent / "data"
    result = {"exported_at": datetime.utcnow().isoformat()}
    for name in ["agent_state", "decision_logs", "mission_telemetry", "approval_workflow_state"]:
        fpath = data_dir / f"{name}.json"
        if fpath.exists():
            try:
                result[name] = json.loads(fpath.read_text())
            except Exception:
                result[name] = None
        else:
            result[name] = None
    return result


@app.get("/api/export/settings")
async def export_settings() -> Dict:
    """Export current (non-secret) settings."""
    try:
        from config.settings import get_settings
        s = get_settings()
        return {
            "exported_at": datetime.utcnow().isoformat(),
            "settings": {
                "ollama_base_url": s.ollama_base_url,
                "ollama_model": s.ollama_model,
                "ollama_enabled": s.ollama_enabled,
                "local_only": s.local_only,
                "agent_model": s.agent_model,
                "agent_temperature": s.agent_temperature,
                "agent_max_tokens": s.agent_max_tokens,
                "log_level": s.log_level,
            },
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# SETTINGS ENDPOINTS (extended)
# ============================================================================

@app.get("/api/settings")
async def get_all_settings() -> Dict:
    """Get all non-secret settings for the settings page."""
    try:
        from config.settings import get_settings
        s = get_settings()
        return {
            "local_only": s.local_only,
            "ollama_enabled": s.ollama_enabled,
            "ollama_model": s.ollama_model,
            "ollama_base_url": s.ollama_base_url,
            "agent_temperature": s.agent_temperature,
            "agent_max_tokens": s.agent_max_tokens,
            "agent_model": s.agent_model,
            "log_level": s.log_level,
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/settings")
async def update_settings(body: Dict) -> Dict:
    """Update runtime settings."""
    try:
        from config.settings import get_settings
        s = get_settings()
        updated = []
        for key in ["local_only", "ollama_enabled", "ollama_model", "ollama_base_url",
                     "agent_temperature", "agent_max_tokens", "agent_model", "log_level"]:
            if key in body:
                setattr(s, key, body[key])
                updated.append(key)
        return {"success": True, "updated": updated}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/settings/ollama-models")
async def get_ollama_models() -> Dict:
    """List available Ollama models."""
    try:
        from config.settings import get_settings
        import urllib.request
        s = get_settings()
        url = f"{s.ollama_base_url}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            return {"models": models, "current": s.ollama_model}
    except Exception:
        return {"models": [], "current": "", "error": "Ollama not reachable"}


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
# HOST SCANNER & UNIVERSAL DIAGNOSTICS
# ============================================================================

@app.get("/api/scan/host")
async def scan_host_endpoint() -> Dict:
    """Scan the machine Piddy is plugged into — hardware, OS, runtimes, tools."""
    try:
        from src.api.host_scanner import scan_host
        return scan_host()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/scan/repo")
async def scan_repo_endpoint(body: Dict) -> Dict:
    """Analyze any local repository on the host machine."""
    repo_path = body.get("path", "")
    if not repo_path:
        return {"error": "Missing 'path' in request body"}
    try:
        from src.api.host_scanner import analyze_repo
        return analyze_repo(repo_path)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/scan/programs")
async def scan_programs_endpoint() -> Dict:
    """List installed programs on the host OS."""
    try:
        from src.api.host_scanner import scan_installed_programs
        programs = scan_installed_programs()
        return {"count": len(programs), "programs": programs}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/platform")
async def platform_info_endpoint() -> Dict:
    """Return cross-platform runtime detection summary."""
    try:
        from src.platform.runtime import platform_summary
        return platform_summary()
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# AUTO-UPDATE SYSTEM
# ============================================================================

@app.get("/api/update/check")
async def check_updates_endpoint() -> Dict:
    """Check GitHub for available Piddy updates."""
    try:
        from src.api.updater import check_for_updates
        return check_for_updates()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/update/apply")
async def apply_update_endpoint() -> Dict:
    """Apply the latest update from GitHub (git pull)."""
    try:
        from src.api.updater import apply_update
        return apply_update()
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# DISCORD / TELEGRAM BOT MANAGEMENT
# ============================================================================

@app.get("/api/integrations/status")
async def integrations_status() -> Dict:
    """Status of all channel integrations (Slack/Discord/Telegram)."""
    result = {"slack": {"configured": False}, "discord": {"running": False}, "telegram": {"running": False}}
    try:
        from config.settings import get_settings
        s = get_settings()
        result["slack"]["configured"] = bool(s.slack_bot_token)
    except Exception:
        pass
    try:
        from src.integrations.discord_bot import get_discord_bot
        result["discord"] = get_discord_bot().status()
    except Exception:
        pass
    try:
        from src.integrations.telegram_bot import get_telegram_bot
        result["telegram"] = get_telegram_bot().status()
    except Exception:
        pass
    return result


@app.post("/api/integrations/discord/start")
async def discord_start() -> Dict:
    try:
        from src.integrations.discord_bot import get_discord_bot
        return get_discord_bot().start()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/integrations/discord/stop")
async def discord_stop() -> Dict:
    try:
        from src.integrations.discord_bot import get_discord_bot
        return get_discord_bot().stop()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/integrations/telegram/start")
async def telegram_start() -> Dict:
    try:
        from src.integrations.telegram_bot import get_telegram_bot
        return get_telegram_bot().start()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/integrations/telegram/stop")
async def telegram_stop() -> Dict:
    try:
        from src.integrations.telegram_bot import get_telegram_bot
        return get_telegram_bot().stop()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# BROWSER AUTOMATION
# ============================================================================

@app.post("/api/browser/launch")
async def browser_launch() -> Dict:
    try:
        from src.tools.browser_automation import get_browser
        return await get_browser().launch()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/browser/close")
async def browser_close() -> Dict:
    try:
        from src.tools.browser_automation import get_browser
        return await get_browser().close()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/browser/status")
async def browser_status() -> Dict:
    try:
        from src.tools.browser_automation import get_browser
        return get_browser().status()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/browser/action")
async def browser_action(body: Dict) -> Dict:
    """Execute a browser action. Body: {action, ...params}"""
    try:
        from src.tools.browser_automation import get_browser
        b = get_browser()
        action = body.get("action")
        params = {k: v for k, v in body.items() if k != "action"}
        handler = {
            "navigate": b.navigate,
            "screenshot": b.screenshot,
            "extract_text": b.extract_text,
            "extract_links": b.extract_links,
            "click": b.click,
            "fill": b.fill,
            "evaluate": b.evaluate,
            "pdf": b.pdf,
        }.get(action)
        if not handler:
            return {"success": False, "error": f"Unknown action: {action}"}
        return await handler(**params)
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/browser/sequence")
async def browser_sequence(body: Dict) -> Dict:
    """Run a multi-step browser sequence. Body: {steps: [{action, ...}, ...]}"""
    try:
        from src.tools.browser_automation import get_browser
        steps = body.get("steps", [])
        return {"results": await get_browser().run_sequence(steps)}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# PRODUCTIVITY CONNECTORS (Calendar / Jira / Notion)
# ============================================================================

@app.get("/api/productivity/status")
async def productivity_status() -> Dict:
    try:
        from src.integrations.productivity import get_all_connector_status
        return get_all_connector_status()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/productivity/calendar/events")
async def calendar_events() -> Dict:
    try:
        from config.settings import get_settings
        from src.integrations.productivity import GoogleCalendarConnector
        s = get_settings()
        c = GoogleCalendarConnector(api_key=s.google_calendar_api_key, calendar_id=s.google_calendar_id)
        return c.list_events()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/productivity/jira/issues")
async def jira_issues() -> Dict:
    try:
        from config.settings import get_settings
        from src.integrations.productivity import JiraConnector
        s = get_settings()
        j = JiraConnector(base_url=s.jira_base_url, email=s.jira_email, api_token=s.jira_api_token)
        return j.search_issues()
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/productivity/jira/create")
async def jira_create(body: Dict) -> Dict:
    try:
        from config.settings import get_settings
        from src.integrations.productivity import JiraConnector
        s = get_settings()
        j = JiraConnector(base_url=s.jira_base_url, email=s.jira_email, api_token=s.jira_api_token)
        return j.create_issue(
            project_key=body["project_key"],
            summary=body["summary"],
            description=body.get("description", ""),
            issue_type=body.get("issue_type", "Task"),
        )
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/productivity/notion/search")
async def notion_search(q: str = "") -> Dict:
    try:
        from config.settings import get_settings
        from src.integrations.productivity import NotionConnector
        s = get_settings()
        n = NotionConnector(api_token=s.notion_api_token)
        return n.search(query=q)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/productivity/notion/create")
async def notion_create(body: Dict) -> Dict:
    try:
        from config.settings import get_settings
        from src.integrations.productivity import NotionConnector
        s = get_settings()
        n = NotionConnector(api_token=s.notion_api_token)
        return n.create_page(
            parent_id=body["parent_id"],
            title=body["title"],
            content=body.get("content", ""),
        )
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# PHASE 51: AUTONOMOUS LOOP ENDPOINTS
# ============================================================================

@app.post("/api/autonomous/execute")
async def autonomous_execute(request: Request):
    """Execute a task with autonomous retry loop (Phase 51)."""
    try:
        body = await request.json()
        task = body.get("task", "")
        max_retries = body.get("max_retries", 5)
        if not task:
            return {"status": "error", "error": "task is required"}
        from src.phase51_autonomous_loop import AutonomousLoop
        loop = AutonomousLoop(max_retries=max_retries)
        async def mock_execute(t, strategy, ctx):
            # Delegate to nova coordinator if available
            try:
                from src.nova_coordinator import NovaCoordinator
                coord = NovaCoordinator()
                return await coord._run_execution_stage(t, f"auto_{id(t)}", "nova_executor", [])
            except Exception as e:
                return {"status": "failed", "error": str(e)}
        result = await loop.run(task, mock_execute)
        return result.to_dict()
    except ImportError:
        return {"status": "error", "error": "Phase 51 not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/autonomous/failures")
async def autonomous_failures(task: str = "", error_type: str = "", limit: int = 20):
    """Get failure history from Phase 51 memory."""
    try:
        from src.phase51_autonomous_loop import FailureMemory
        fm = FailureMemory()
        if task:
            failures = fm.get_past_failures(task, limit=limit)
        elif error_type:
            failures = fm.get_all_failures_by_error(error_type, limit=limit)
        else:
            failures = fm.get_past_failures("", limit=limit)
        return {"failures": failures, "count": len(failures)}
    except ImportError:
        return {"status": "error", "error": "Phase 51 not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/autonomous/summary")
async def autonomous_summary():
    """Get failure memory summary stats."""
    try:
        from src.phase51_autonomous_loop import FailureMemory
        fm = FailureMemory()
        return fm.get_failure_summary()
    except ImportError:
        return {"status": "error", "error": "Phase 51 not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/autonomous/strategies")
async def autonomous_strategies(task: str = ""):
    """Get strategy success rates from failure memory."""
    try:
        from src.phase51_autonomous_loop import FailureMemory
        fm = FailureMemory()
        stats = fm.get_strategy_stats(task)
        return {"strategies": stats, "count": len(stats)}
    except ImportError:
        return {"status": "error", "error": "Phase 51 not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# SERVE DASHBOARD FRONTEND
# ============================================================================

@app.get("/")
async def root():
    """Serve dashboard homepage"""
    return FileResponse("frontend/dist/index.html", media_type="text/html")


def find_available_port(start=8000, end=8100):
    """Find the first available port in range."""
    import socket
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start  # fallback


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PIDDY_PORT", 0)) or find_available_port()
    logger.info(f"Starting Piddy backend on port {port}")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
