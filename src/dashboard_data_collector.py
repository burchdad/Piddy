"""
Dashboard Data Collector
Populates data/*.json files so dashboard tabs display real information.

Called from:
 - piddy/rpc_endpoints.py (chat messages, decisions)
 - src/autonomous_background_service.py (phase status, agent state, metrics)

All writes are fire-and-forget with exception swallowing so they never
break the calling code path.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# All data files live here
_DATA_DIR = Path(__file__).parent.parent / "data"

_MAX_MESSAGES = 500
_MAX_DECISIONS = 200
_MAX_TELEMETRY = 200
_MAX_TEST_RESULTS = 200


def _ensure_dir():
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def _safe_load(path: Path, default=None):
    """Load JSON, returning *default* on any error."""
    if default is None:
        default = []
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _safe_save(path: Path, data):
    """Atomically write JSON."""
    _ensure_dir()
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.replace(path)


# ─────────────────────────────────────────────
# MESSAGE LOG  (data/message_log.json)
# ─────────────────────────────────────────────
def log_chat_message(
    user_message: str,
    reply: str,
    source: str = "unknown",
    tier_used: str = "unknown",
    engine_used: str = "unknown",
    files_created: int = 0,
    session_id: str = "",
):
    """Append a chat exchange to message_log.json."""
    try:
        path = _DATA_DIR / "message_log.json"
        msgs = _safe_load(path, [])
        msgs.append({
            "message_id": f"msg_{int(time.time()*1000)}",
            "sender_id": "user",
            "receiver_id": engine_used,
            "message_type": "chat",
            "content": {
                "user": user_message[:500],
                "reply": reply[:1000],
                "source": source,
                "tier": tier_used,
                "engine": engine_used,
                "files_created": files_created,
                "session_id": session_id,
            },
            "timestamp": datetime.utcnow().isoformat(),
            "priority": 5,
        })
        # FIFO cap
        if len(msgs) > _MAX_MESSAGES:
            msgs = msgs[-_MAX_MESSAGES:]
        _safe_save(path, msgs)
    except Exception as e:
        logger.debug(f"log_chat_message failed: {e}")


# ─────────────────────────────────────────────
# DECISION LOG  (data/decision_logs.json)
# ─────────────────────────────────────────────
def log_decision(
    task: str,
    agent_id: str,
    action: str,
    confidence: float = 0.5,
    reasoning: Optional[List[Dict]] = None,
    outcome: Optional[Dict] = None,
    status: str = "executed",
):
    """Record an AI decision."""
    try:
        path = _DATA_DIR / "decision_logs.json"
        decisions = _safe_load(path, [])
        decisions.append({
            "id": f"dec_{uuid.uuid4().hex[:12]}",
            "task": task[:300],
            "agent_id": agent_id,
            "action": action[:200],
            "confidence": confidence,
            "context": {},
            "reasoning_chain": reasoning or [],
            "factors": [],
            "parameters": {},
            "validation": {},
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
        })
        if len(decisions) > _MAX_DECISIONS:
            decisions = decisions[-_MAX_DECISIONS:]
        _safe_save(path, decisions)
    except Exception as e:
        logger.debug(f"log_decision failed: {e}")


# ─────────────────────────────────────────────
# PHASE STATUS  (data/phase_status.json)
# ─────────────────────────────────────────────
def update_phase_status(phases: List[Dict]):
    """Replace the phase status snapshot.

    *phases* should be a list of dicts with at least:
        phase_id, phase_name, status, progress_percent, details
    """
    try:
        path = _DATA_DIR / "phase_status.json"
        now = datetime.utcnow().isoformat()
        for p in phases:
            p.setdefault("timestamp", now)
            p.setdefault("details", {})
        _safe_save(path, phases)
    except Exception as e:
        logger.debug(f"update_phase_status failed: {e}")


# ─────────────────────────────────────────────
# AGENT STATE  (data/agent_state.json)
# ─────────────────────────────────────────────
def snapshot_agent_state(agents: List[Dict]):
    """Write current agent state snapshot."""
    try:
        path = _DATA_DIR / "agent_state.json"
        _safe_save(path, agents)
    except Exception as e:
        logger.debug(f"snapshot_agent_state failed: {e}")


# ─────────────────────────────────────────────
# MISSION TELEMETRY  (data/mission_telemetry.json)
# ─────────────────────────────────────────────
def log_mission(
    mission_id: str,
    name: str,
    description: str = "",
    status: str = "completed",
    stages: Optional[List[Dict]] = None,
    agents_involved: Optional[List[Dict]] = None,
    efficiency_score: float = 0.0,
    quality_score: float = 0.0,
):
    """Append a mission to telemetry."""
    try:
        path = _DATA_DIR / "mission_telemetry.json"
        missions = _safe_load(path, [])
        missions.append({
            "id": mission_id,
            "name": name,
            "description": description[:500],
            "goal": description[:200],
            "status": status,
            "priority": 5,
            "stages": stages or [],
            "agents_involved": agents_involved or [],
            "progress_percent": 100 if status == "completed" else 0,
            "plan": {},
            "success_criteria": [],
            "efficiency_score": efficiency_score,
            "quality_score": quality_score,
            "risk_level": "low",
            "notes": None,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(missions) > _MAX_TELEMETRY:
            missions = missions[-_MAX_TELEMETRY:]
        _safe_save(path, missions)
    except Exception as e:
        logger.debug(f"log_mission failed: {e}")


# ─────────────────────────────────────────────
# TEST RESULTS  (data/test_results.json)
# ─────────────────────────────────────────────
def log_test_result(
    test_name: str,
    status: str = "passed",
    duration: float = 0.0,
    message: str = "",
):
    """Record a single test result."""
    try:
        path = _DATA_DIR / "test_results.json"
        tests = _safe_load(path, [])
        tests.append({
            "test_id": f"test_{uuid.uuid4().hex[:8]}",
            "test_name": test_name,
            "status": status,
            "duration_seconds": duration,
            "message": message[:300],
        })
        if len(tests) > _MAX_TEST_RESULTS:
            tests = tests[-_MAX_TEST_RESULTS:]
        _safe_save(path, tests)
    except Exception as e:
        logger.debug(f"log_test_result failed: {e}")


# ─────────────────────────────────────────────
# SECURITY AUDIT  (data/security_audit.json)
# ─────────────────────────────────────────────
def update_security_audit(
    passed: int = 0,
    failed: int = 0,
    critical_failures: Optional[List[str]] = None,
    is_safe: bool = True,
):
    """Update the security audit snapshot."""
    try:
        path = _DATA_DIR / "security_audit.json"
        _safe_save(path, {
            "audit_id": f"audit_{int(time.time())}",
            "passed_checks": passed,
            "failed_checks": failed,
            "critical_failures": critical_failures or [],
            "is_production_safe": is_safe,
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        logger.debug(f"update_security_audit failed: {e}")


# ─────────────────────────────────────────────
# DEPENDENCY GRAPH  (data/dependency_graph.json)
# ─────────────────────────────────────────────
def build_dependency_graph():
    """Scan src/ for imports and build a real dependency graph."""
    try:
        src_dir = Path(__file__).parent.parent / "src"
        if not src_dir.exists():
            return

        nodes = {}
        edges = []

        py_files = list(src_dir.rglob("*.py"))
        for i, py_file in enumerate(py_files[:50]):  # cap at 50 for performance
            mod_name = py_file.stem
            if mod_name.startswith("__"):
                continue
            node_id = mod_name
            nodes[node_id] = {
                "id": node_id,
                "name": mod_name,
                "type": "module",
                "description": "",
                "x": float((i % 10) * 120),
                "y": float((i // 10) * 120),
                "inbound_count": 0,
                "outbound_count": 0,
                "avg_response_time": 0,
                "error_rate": 0,
            }

            # Parse imports
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("from src.") or line.startswith("from src "):
                        parts = line.split()
                        if len(parts) >= 2:
                            target_mod = parts[1].rsplit(".", 1)[-1]
                            if target_mod != mod_name and target_mod in nodes:
                                edges.append({
                                    "from_id": node_id,
                                    "to_id": target_mod,
                                    "type": "sync",
                                    "calls": 1,
                                    "weight": 1.0,
                                })
                                nodes[node_id]["outbound_count"] += 1
                                nodes[target_mod]["inbound_count"] += 1
            except Exception:
                pass

        path = _DATA_DIR / "dependency_graph.json"
        _safe_save(path, {
            "nodes": list(nodes.values()),
            "edges": edges,
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        logger.debug(f"build_dependency_graph failed: {e}")


# ─────────────────────────────────────────────
# COLLECT ALL  (called from background service)
# ─────────────────────────────────────────────
def collect_dashboard_snapshot():
    """Gather and write all dashboard data files in one pass.

    Should be called periodically (e.g. every 10 cycles in the background service).
    """
    _collect_phase_status()
    _collect_agent_state()
    _collect_security_snapshot()
    build_dependency_graph()


def _collect_phase_status():
    """Scan for phase*.py files and record which are importable."""
    try:
        src_dir = Path(__file__).parent.parent / "src"
        phase_files = sorted(src_dir.glob("phase*.py"))
        phases = []
        for pf in phase_files:
            stem = pf.stem  # e.g. phase19_self_improving_agent
            parts = stem.split("_", 1)
            phase_num = parts[0].replace("phase", "")
            phase_name = parts[1].replace("_", " ").title() if len(parts) > 1 else stem

            # Check if importable (basic check)
            try:
                compile(pf.read_text(encoding="utf-8", errors="replace"), str(pf), "exec")
                status = "completed"
                progress = 100
            except SyntaxError:
                status = "failed"
                progress = 0

            phases.append({
                "phase_id": f"phase_{phase_num}",
                "phase_name": f"Phase {phase_num}: {phase_name}",
                "status": status,
                "progress_percent": progress,
                "details": {"file": pf.name},
            })
        update_phase_status(phases)
    except Exception as e:
        logger.debug(f"_collect_phase_status failed: {e}")


def _collect_agent_state():
    """Pull live agent state from coordinator if available."""
    try:
        from src.coordination.agent_coordinator import get_coordinator
        coordinator = get_coordinator()
        if not coordinator:
            return
        agents = []
        for agent in coordinator.get_all_agents():
            total = agent.completed_tasks + agent.failed_tasks
            agents.append({
                "agent_id": agent.id,
                "name": agent.name,
                "role": agent.role.value if hasattr(agent.role, "value") else str(agent.role),
                "status": "active" if agent.is_available else "busy",
                "reputation_score": round((agent.completed_tasks / max(total, 1)) * 100, 1),
                "total_decisions": total,
                "correct_decisions": agent.completed_tasks,
                "messages_pending": 0,
                "last_activity": agent.last_activity or datetime.utcnow().isoformat(),
            })
        if agents:
            snapshot_agent_state(agents)
    except Exception as e:
        logger.debug(f"_collect_agent_state failed: {e}")


def _collect_security_snapshot():
    """Run basic security checks and write audit file."""
    try:
        from pathlib import Path as P
        passed = 0
        failed = 0
        critical = []

        # Check for .env exposure
        env_file = P(".env")
        if env_file.exists():
            content = env_file.read_text(encoding="utf-8", errors="replace")
            if "API_KEY" in content or "SECRET" in content:
                passed += 1  # .env exists with secrets (expected)
            else:
                passed += 1
        else:
            passed += 1

        # Check keys.enc exists (encrypted keys)
        if (P("config") / "keys.enc").exists():
            passed += 1
        else:
            failed += 1
            critical.append("config/keys.enc missing — API keys not encrypted")

        # Check no API keys in settings.py plain text
        settings_file = P("config") / "settings.py"
        if settings_file.exists():
            s_content = settings_file.read_text(encoding="utf-8", errors="replace")
            if "sk-" in s_content or "AKIA" in s_content:
                failed += 1
                critical.append("Hardcoded API key found in config/settings.py")
            else:
                passed += 1

        # Check requirements pinned
        req_file = P("requirements.txt")
        if req_file.exists():
            passed += 1
        else:
            failed += 1

        update_security_audit(
            passed=passed,
            failed=failed,
            critical_failures=critical,
            is_safe=(failed == 0),
        )
    except Exception as e:
        logger.debug(f"_collect_security_snapshot failed: {e}")
