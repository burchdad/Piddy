"""
RPC Endpoint Definitions

Exposes all API functions as RPC-callable endpoints.
These are pure Python functions that can be called directly from Electron via IPC,
bypassing the HTTP layer entirely for maximum performance.

Format: function_name = "category.endpoint"
Example: "system.overview" → system_overview()
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Import Nova executor for code execution endpoints
try:
    from piddy.nova_executor import execute_task, get_execution_status, get_all_executions
    logger.info("✅ Nova executor available for RPC")
except ImportError:
    logger.warning("⚠️ Nova executor not available")
    def execute_task(*args, **kwargs) -> Any:
        return {"error": "Nova executor not available"}
    def get_execution_status(*args, **kwargs) -> Any:
        return {"error": "Nova executor not available"}
    def get_all_executions(*args, **kwargs) -> Any:
        return {"error": "Nova executor not available"}

# Import offline support for mission queueing when offline
try:
    from piddy.offline_sync import get_offline_queue, get_sync_manager
    HAS_OFFLINE_SUPPORT = True
    logger.info("✅ Offline support available for RPC")
except ImportError:
    HAS_OFFLINE_SUPPORT = False
    logger.warning("⚠️ Offline support not available")
    def get_offline_queue(*args, **kwargs) -> Any:
        return None
    def get_sync_manager(*args, **kwargs) -> Any:
        return None

# Import Scanner functions
try:
    from src.api.host_scanner import scan_host, analyze_repo, scan_installed_programs
    logger.info("✅ Host scanner available for RPC")
except ImportError:
    logger.warning("⚠️ Host scanner not available")
    def scan_host(*args, **kwargs): return {"error": "Host scanner not available"}
    def analyze_repo(*args, **kwargs): return {"error": "Host scanner not available"}
    def scan_installed_programs(*args, **kwargs): return {"error": "Host scanner not available"}

# Import Updater functions
try:
    from src.api.updater import check_for_updates, apply_update
    logger.info("✅ Updater available for RPC")
except ImportError:
    logger.warning("⚠️ Updater not available")
    def check_for_updates(*args, **kwargs): return {"error": "Updater not available"}
    def apply_update(*args, **kwargs): return {"error": "Updater not available"}

# Import Platform runtime
try:
    from src.platform.runtime import platform_summary
    logger.info("✅ Platform runtime available for RPC")
except ImportError:
    logger.warning("⚠️ Platform runtime not available")
    def platform_summary(*args, **kwargs): return {"error": "Platform runtime not available"}

# Import Skills loader
try:
    from src.skills.loader import get_skill_registry
    HAS_SKILLS = True
    logger.info("✅ Skills loader available for RPC")
except ImportError:
    HAS_SKILLS = False
    logger.warning("⚠️ Skills loader not available")
    def get_skill_registry(*args, **kwargs): return None

# ============================================================================
# GLOBAL STATE - Initialize on first call
# ============================================================================

_coordinator = None
_telemetry_collector = None
_loop = None

def _get_event_loop():
    """Get or create event loop for async functions."""
    global _loop
    if _loop is None:
        try:
            _loop = asyncio.get_running_loop()
        except RuntimeError:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
    return _loop


def _get_coordinator():
    """Lazy load coordinator on first call, with agents registered.
    Uses the shared singleton so doctor checks see the same agents."""
    global _coordinator
    if _coordinator is None:
        try:
            from src.coordination.agent_coordinator import get_coordinator, AgentRole
            _coordinator = get_coordinator()
            logger.info("✅ Agent Coordinator initialized (shared singleton)")
            # Register agents so agent counts are accurate
            try:
                if not _coordinator.get_all_agents():
                    agents_to_spawn = [
                        ("Guardian", AgentRole.SECURITY_SPECIALIST, ["security_scan", "vulnerability_detection"]),
                        ("Architect", AgentRole.ARCHITECT, ["design_review", "system_planning"]),
                        ("CodeMaster", AgentRole.BACKEND_DEVELOPER, ["code_generation", "bug_fixing"]),
                        ("Reviewer", AgentRole.CODE_REVIEWER, ["code_review", "quality_assurance"]),
                        ("DevOps Pro", AgentRole.DEVOPS_ENGINEER, ["deployment", "infrastructure"]),
                        ("Data Expert", AgentRole.DATA_ENGINEER, ["data_pipeline", "analytics"]),
                        ("Coordinator", AgentRole.COORDINATOR, ["task_distribution", "orchestration"]),
                        ("Perf Analyst", AgentRole.PERFORMANCE_ANALYST, ["profiling", "optimization"]),
                        ("Tech Debt Hunter", AgentRole.TECH_DEBT_HUNTER, ["code_debt_detection", "refactoring"]),
                        ("API Compat", AgentRole.API_COMPATIBILITY, ["api_testing", "compatibility_check"]),
                        ("DB Migration", AgentRole.DATABASE_MIGRATION, ["schema_migration", "data_migration"]),
                        ("Arch Reviewer", AgentRole.ARCHITECTURE_REVIEWER, ["architecture_review", "design_patterns"]),
                        ("Cost Optimizer", AgentRole.COST_OPTIMIZER, ["cost_analysis", "resource_optimization"]),
                        ("Frontend Dev", AgentRole.FRONTEND_DEVELOPER, ["ui_development", "react_components"]),
                        ("Doc Writer", AgentRole.DOCUMENTATION, ["documentation", "api_docs"]),
                        ("SecTool Dev", AgentRole.SECURITY_TOOLING, ["scanner_development", "rule_authoring"]),
                        ("Sec Monitor", AgentRole.SECURITY_MONITORING, ["alert_management", "anomaly_detection"]),
                        ("Load Tester", AgentRole.LOAD_TESTING, ["load_testing", "stress_testing"]),
                        ("Data Guardian", AgentRole.DATA_SECURITY, ["pii_detection", "data_encryption"]),
                        ("KB Monitor", AgentRole.KNOWLEDGE_MONITOR, ["kb_sync", "content_validation"]),
                        ("Automator", AgentRole.TASK_AUTOMATION, ["workflow_building", "script_generation"]),
                    ]
                    for name, role, caps in agents_to_spawn:
                        agent = _coordinator.register_agent(name, role, caps)
                        agent.is_available = True
                        agent.completed_tasks = 1
                    logger.info(f"✅ Registered {len(agents_to_spawn)} agents in coordinator")
                else:
                    logger.info(f"✅ Coordinator already has {len(_coordinator.get_all_agents())} agents")
            except Exception as e:
                logger.debug(f"Could not register agents in coordinator: {e}")
        except ImportError:
            logger.warning("⚠️ AgentCoordinator not available (optional dependency)")
            _coordinator = None
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize coordinator: {e}")
            _coordinator = None
    return _coordinator


def _get_telemetry_collector():
    """Lazy load telemetry on first call."""
    global _telemetry_collector
    if _telemetry_collector is None:
        try:
            from src.phase34_mission_telemetry import MissionTelemetryCollector
            _telemetry_collector = MissionTelemetryCollector('.piddy_telemetry.db')
            logger.info("✅ Telemetry initialized for RPC")
        except ImportError:
            logger.warning("⚠️ MissionTelemetryCollector not available (optional dependency)")
            _telemetry_collector = None
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize telemetry: {e}")
            _telemetry_collector = None
    return _telemetry_collector


def _run_async(coro):
    """Run async function synchronously."""
    try:
        loop = _get_event_loop()
        if loop.is_running():
            # If loop is already running, we need to use a different approach
            import concurrent.futures
            import threading
            result: list[Any] = [None]
            exception: list[Any] = [None]
            
            def run_in_new_loop():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result[0] = new_loop.run_until_complete(coro)
                    new_loop.close()
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=run_in_new_loop, daemon=True)
            thread.start()
            thread.join(timeout=30)
            
            if exception[0]:
                raise exception[0]
            return result[0]
        else:
            return loop.run_until_complete(coro)
    except Exception as e:
        logger.error(f"Error running async function: {e}")
        raise


def _run_async_long(coro):
    """Run async function with a longer timeout (for LLM calls)."""
    try:
        loop = _get_event_loop()
        if loop.is_running():
            import concurrent.futures
            import threading
            result: list[Any] = [None]
            exception: list[Any] = [None]
            
            def run_in_new_loop():
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result[0] = new_loop.run_until_complete(coro)
                    new_loop.close()
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=run_in_new_loop, daemon=True)
            thread.start()
            thread.join(timeout=120)
            
            if thread.is_alive():
                return {"reply": "Response is taking longer than expected. The language model may be slow or unreachable. Check the Health page.", "source": "timeout", "session_id": None}
            if exception[0]:
                raise exception[0]
            return result[0]
        else:
            return loop.run_until_complete(coro)
    except Exception as e:
        logger.error(f"Error running long async function: {e}")
        return {"reply": f"Error: {e}", "source": "error", "session_id": None}


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

def system_overview() -> Dict:
    """Get system overview with REAL agent and mission counts."""
    try:
        coordinator = _get_coordinator()
        telemetry = _get_telemetry_collector()
        
        # Real data from coordinator if available
        if coordinator:
            stats = coordinator.get_stats()
            agents_online = stats["agents"]["available"]
            total_agents = stats["agents"]["total"]
            missions_active = stats["tasks"]["in_progress"]
            decisions_pending = stats["tasks"]["queued"]
        else:
            agents_online = 0
            total_agents = 0
            missions_active = 0
            decisions_pending = 0
        
        # Real telemetry if available
        if telemetry:
            try:
                telemetry_stats = telemetry.get_all_stats()
                success_rate = telemetry_stats.get('success_rate', 0) if telemetry_stats else 0
            except Exception as e:
                logger.debug(f"Could not get telemetry stats: {e}")
                success_rate = 0
        else:
            success_rate = 0
        
        # Real system metrics
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_mb = memory_info.rss / 1024 / 1024
            uptime_seconds = int(datetime.now().timestamp() - process.create_time())
        except (ImportError, Exception) as e:
            logger.debug(f"Could not get psutil metrics: {e}")
            memory_mb = 0
            cpu_percent = 0
            uptime_seconds = 0
        
        return {
            "status": "operational",
            "uptime_seconds": uptime_seconds,
            "agents_online": agents_online,
            "agents_total": total_agents,
            "missions_active": missions_active,
            "decisions_pending": decisions_pending,
            "success_rate": success_rate,
            "metrics": {
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent,
                "agents_online": agents_online,
                "agents_offline": total_agents - agents_online,
            },
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error in system_overview: {e}", exc_info=True)
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }


def system_health() -> Dict:
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "3.1-rpc"
        }
    except Exception as e:
        logger.error(f"Error in system_health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


def system_config() -> Dict:
    """Get system configuration."""
    try:
        from config.settings import get_settings
        settings = get_settings()
        return {
            "debug": settings.debug if hasattr(settings, 'debug') else False,
            "agent_model": settings.agent_model if hasattr(settings, 'agent_model') else "unknown",
            "environment": "PRODUCTION",
            "rpc_mode": True,
            "version": "3.1-rpc",
            "timestamp": datetime.utcnow().isoformat()
        }
    except ImportError:
        logger.warning("⚠️ Settings not available")
        return {
            "debug": False,
            "environment": "PRODUCTION",
            "rpc_mode": True,
            "version": "3.1-rpc",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in system_config: {e}")
        return {
            "error": str(e),
            "rpc_mode": True
        }


# ============================================================================
# AGENTS ENDPOINTS
# ============================================================================

def agents_list() -> List[Dict]:
    """Get all agents."""
    try:
        coordinator = _get_coordinator()
        if not coordinator:
            return []
        
        agents = coordinator.get_all_agents()
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "role": agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
                "status": "online" if agent.is_available else "busy",
                "reputation": agent.completed_tasks / max(agent.completed_tasks + agent.failed_tasks, 1),
                "completed_tasks": agent.completed_tasks,
                "failed_tasks": agent.failed_tasks,
                "current_task_id": agent.current_task_id,
                "last_activity": agent.last_activity,
            }
            for agent in agents
        ]
    except Exception as e:
        logger.error(f"Error in agents_list: {e}", exc_info=True)
        return []


def agents_get(agent_id: str) -> Dict:
    """Get specific agent."""
    try:
        coordinator = _get_coordinator()
        if not coordinator:
            return {"error": "Coordinator not initialized"}
        
        agent = coordinator.get_agent(agent_id)
        if not agent:
            return {"error": "Agent not found"}
        
        return {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
            "status": "online" if agent.is_available else "busy",
            "reputation": agent.completed_tasks / max(agent.completed_tasks + agent.failed_tasks, 1),
            "completed_tasks": agent.completed_tasks,
            "failed_tasks": agent.failed_tasks,
            "current_task_id": agent.current_task_id,
            "last_activity": agent.last_activity,
            "capabilities": agent.capabilities if hasattr(agent, 'capabilities') else [],
        }
    except Exception as e:
        logger.error(f"Error in agents_get: {e}")
        return {"error": str(e)}


def agents_create(name: str, role: str = "backend_developer", capabilities: Optional[List[str]] = None) -> Dict:
    """Create a new agent."""
    try:
        coordinator = _get_coordinator()
        if not coordinator:
            return {"error": "Coordinator not initialized"}
        
        from src.coordination.agent_coordinator import AgentRole
        agent_role = AgentRole(role)
        
        agent = coordinator.register_agent(
            name=name,
            role=agent_role,
            capabilities=capabilities or []
        )
        
        logger.info(f"✅ Agent created via RPC: {agent.name}")
        return {
            "id": agent.id,
            "name": agent.name,
            "role": role,
            "status": "online",
            "message": "Agent created successfully"
        }
    except Exception as e:
        logger.error(f"Error in agents_create: {e}")
        return {"error": str(e)}


# ============================================================================
# MESSAGES ENDPOINTS
# ============================================================================

def messages_list(limit: int = 50) -> Dict:
    """Get recent messages."""
    try:
        coordinator = _get_coordinator()
        if not coordinator:
            return {"messages": [], "total": 0}
        
        messages = coordinator.get_recent_messages(limit=limit)
        return {
            "messages": messages if isinstance(messages, list) else list(messages),
            "total": len(messages),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in messages_list: {e}")
        return {"messages": [], "total": 0, "error": str(e)}


def messages_send(sender_id: str, content: str, receiver_id: Optional[str] = None, priority: int = 1) -> Dict:
    """
    Send a message and handle direct commands to Piddy.
    
    Supports:
    - Direct messages to agents
    - Commands to Piddy (e.g., "create mission", "analyze data")
    - Broadcast messages
    """
    try:
        coordinator = _get_coordinator()
        if not coordinator:
            return {"error": "Coordinator not initialized"}
        
        # Generate message ID
        message_id = f"msg_{datetime.utcnow().timestamp()}"
        timestamp = datetime.utcnow().isoformat()
        
        # Store message in coordinator
        message_obj = {
            "id": message_id,
            "sender": sender_id,
            "receiver": receiver_id or "broadcast",
            "content": content,
            "timestamp": timestamp,
            "priority": priority,
            "status": "received"
        }
        
        # If sender is "user" (from dashboard) and no specific receiver, route to Piddy
        if sender_id == "user" and (receiver_id is None or receiver_id == "Piddy"):
            # Parse command or query
            user_command = content.strip().lower()
            
            # Handle common Piddy commands
            if any(cmd in user_command for cmd in ["create mission", "start mission", "new mission"]):
                message_obj["status"] = "processing"
                message_obj["action"] = "create_mission"
                # Coordinator will handle mission creation
                coordinator.send_message("user", "mission_planner", "mission_request", {"text": content})
                
            elif any(cmd in user_command for cmd in ["what's happening", "status", "show me what you're doing"]):
                message_obj["status"] = "processing"
                message_obj["action"] = "status_query"
                
            elif any(cmd in user_command for cmd in ["execute", "run", "do this"]):
                message_obj["status"] = "processing"
                message_obj["action"] = "execute_task"
                coordinator.send_message("user", "executor", "task_request", {"text": content})
                
            else:
                message_obj["status"] = "processing"
                message_obj["action"] = "general_query"
        
        # Store the message via coordinator
        try:
            coordinator.send_message(sender_id, receiver_id or "broadcast", "message", {"text": content})
        except Exception:
            pass
        
        # Log for debugging
        logger.info(f"[LIVE] Message from {sender_id} → {receiver_id or 'broadcast'}: {content}")
        
        return {
            "status": "sent",
            "message_id": message_id,
            "timestamp": timestamp,
            "action": message_obj.get("action"),
            "live": True
        }
    except Exception as e:
        logger.error(f"Error in messages_send: {e}")
        return {"error": str(e), "live": False}


# ============================================================================
# SKILLS ENDPOINTS
# ============================================================================

def skills_list() -> Dict:
    """List all loaded skills/plugins."""
    try:
        if not HAS_SKILLS:
            return {"skills": [], "count": 0, "message": "Skills loader not available"}
        registry = get_skill_registry()
        return {"skills": registry.to_dict_list(), "count": len(registry.list_all())}
    except Exception as e:
        logger.error(f"Error in skills_list: {e}")
        return {"skills": [], "count": 0, "error": str(e)}


def skills_reload() -> Dict:
    """Hot-reload skills from library/skills/ folder."""
    try:
        if not HAS_SKILLS:
            return {"success": False, "message": "Skills loader not available"}
        registry = get_skill_registry()
        count = registry.reload()
        return {"success": True, "count": count, "message": f"Reloaded {count} skills"}
    except Exception as e:
        logger.error(f"Error in skills_reload: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# PROJECT / FILE BROWSER ENDPOINTS
# ============================================================================

def _get_projects_dir() -> Path:
    """Get the projects directory path."""
    return Path(__file__).parent.parent / "projects"


def projects_list() -> Dict:
    """List all projects in the projects/ directory."""
    try:
        projects_dir = _get_projects_dir()
        if not projects_dir.exists():
            return {"projects": [], "root": str(projects_dir)}

        projects = []
        for item in sorted(projects_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                # Count files recursively
                file_count = sum(1 for f in item.rglob('*') if f.is_file() and not any(p.startswith('.') for p in f.relative_to(item).parts))
                total_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file() and not any(p.startswith('.') for p in f.relative_to(item).parts))
                # Get modification time
                try:
                    mtime = max(f.stat().st_mtime for f in item.rglob('*') if f.is_file())
                except ValueError:
                    mtime = item.stat().st_mtime

                projects.append({
                    "name": item.name,
                    "path": str(item.relative_to(projects_dir)),
                    "file_count": file_count,
                    "total_size": total_size,
                    "modified": datetime.fromtimestamp(mtime).isoformat(),
                })
        return {"projects": projects, "root": str(projects_dir)}
    except Exception as e:
        logger.error(f"Error in projects_list: {e}")
        return {"projects": [], "error": str(e)}


def _build_tree(dir_path: Path, base_path: Path, depth: int = 0, max_depth: int = 10) -> List[Dict]:
    """Recursively build a file tree."""
    if depth > max_depth:
        return []
    entries = []
    try:
        for item in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.'):
                continue
            rel = str(item.relative_to(base_path)).replace('\\', '/')
            if item.is_dir():
                children = _build_tree(item, base_path, depth + 1, max_depth)
                entries.append({
                    "name": item.name,
                    "path": rel,
                    "type": "directory",
                    "children": children,
                })
            else:
                entries.append({
                    "name": item.name,
                    "path": rel,
                    "type": "file",
                    "size": item.stat().st_size,
                    "extension": item.suffix.lstrip('.'),
                })
    except PermissionError:
        pass
    return entries


def projects_tree(project_name=None) -> Dict:
    """Get file tree for a project."""
    try:
        # IPC POST sends data as a dict positional arg
        if isinstance(project_name, dict):
            project_name = project_name.get('project_name')
        projects_dir = _get_projects_dir()
        if project_name:
            target = projects_dir / project_name
        else:
            target = projects_dir

        if not target.exists():
            return {"error": f"Project not found: {project_name}", "tree": []}

        # Ensure we're not escaping the projects directory
        resolved = target.resolve()
        if not str(resolved).startswith(str(projects_dir.resolve())):
            return {"error": "Invalid path", "tree": []}

        tree = _build_tree(target, target)
        return {"project": project_name or "all", "tree": tree}
    except Exception as e:
        logger.error(f"Error in projects_tree: {e}")
        return {"tree": [], "error": str(e)}


def projects_file(file_path=None) -> Dict:
    """Read a file from a project. Path is relative to projects/ dir."""
    try:
        # IPC POST sends data as a dict positional arg
        if isinstance(file_path, dict):
            file_path = file_path.get('file_path')
        if not file_path:
            return {"error": "No file path provided"}

        projects_dir = _get_projects_dir()
        target = (projects_dir / file_path).resolve()

        # Path traversal protection
        if not str(target).startswith(str(projects_dir.resolve())):
            return {"error": "Invalid path"}

        if not target.exists():
            return {"error": f"File not found: {file_path}"}

        if not target.is_file():
            return {"error": f"Not a file: {file_path}"}

        # Don't read huge files
        size = target.stat().st_size
        if size > 1_000_000:  # 1MB limit
            return {
                "path": file_path,
                "size": size,
                "error": "File too large to display (>1MB)",
                "truncated": True,
            }

        # Detect binary
        try:
            content = target.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return {
                "path": file_path,
                "size": size,
                "binary": True,
                "error": "Binary file — cannot display",
            }

        ext = target.suffix.lstrip('.')
        return {
            "path": file_path,
            "name": target.name,
            "content": content,
            "size": size,
            "extension": ext,
            "language": _ext_to_language(ext),
            "lines": content.count('\n') + 1,
        }
    except Exception as e:
        logger.error(f"Error in projects_file: {e}")
        return {"error": str(e)}


def _ext_to_language(ext: str) -> str:
    """Map file extension to language name."""
    mapping = {
        'py': 'python', 'js': 'javascript', 'jsx': 'jsx', 'ts': 'typescript',
        'tsx': 'tsx', 'java': 'java', 'c': 'c', 'cpp': 'cpp', 'h': 'c',
        'cs': 'csharp', 'go': 'go', 'rs': 'rust', 'rb': 'ruby', 'php': 'php',
        'swift': 'swift', 'kt': 'kotlin', 'scala': 'scala', 'r': 'r',
        'html': 'html', 'css': 'css', 'scss': 'scss', 'less': 'less',
        'json': 'json', 'yaml': 'yaml', 'yml': 'yaml', 'xml': 'xml',
        'md': 'markdown', 'txt': 'plaintext', 'sh': 'bash', 'bat': 'batch',
        'ps1': 'powershell', 'sql': 'sql', 'toml': 'toml', 'ini': 'ini',
        'cfg': 'ini', 'env': 'plaintext', 'dockerfile': 'dockerfile',
        'makefile': 'makefile',
    }
    return mapping.get(ext.lower(), 'plaintext')


# ============================================================================
# MISSIONS/TASKS ENDPOINTS
# ============================================================================

def missions_list(limit: int = 50) -> Dict:
    """Get recent missions."""
    try:
        # Read from mission_telemetry.json (same source as HTTP /api/missions)
        missions_file = Path("data/mission_telemetry.json")
        missions = []
        if missions_file.exists():
            with open(missions_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    missions = data[:limit]
                elif isinstance(data, dict):
                    missions = list(data.values())[:limit]
        
        return {
            "missions": missions,
            "total": len(missions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in missions_list: {e}")
        return {"missions": [], "total": 0, "error": str(e)}


def missions_get(mission_id: str) -> Dict:
    """Get mission details."""
    try:
        telemetry = _get_telemetry_collector()
        if not telemetry:
            return {"error": "Telemetry not initialized"}
        
        metrics = telemetry.get_mission_metrics(mission_id)
        if not metrics:
            return {"error": "Mission not found"}
        
        return metrics
    except Exception as e:
        logger.error(f"Error in missions_get: {e}")
        return {"error": str(e)}


# ============================================================================
# DECISIONS ENDPOINTS
# ============================================================================

def decisions_list(limit: int = 50) -> Dict:
    """Get recent decisions."""
    try:
        # Try to load from decision logs file
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        decisions_file = data_dir / "decision_logs.json"
        
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                if isinstance(decisions, list):
                    return {
                        "decisions": decisions[:limit],
                        "total": len(decisions),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return {
            "decisions": [],
            "total": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in decisions_list: {e}")
        return {"decisions": [], "total": 0, "error": str(e)}


def decisions_get(decision_id: str) -> Dict:
    """Get decision details."""
    try:
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        decisions_file = data_dir / "decision_logs.json"
        
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                if isinstance(decisions, list):
                    for decision in decisions:
                        if decision.get("id") == decision_id:
                            return decision
        
        return {"error": "Decision not found"}
    except Exception as e:
        logger.error(f"Error in decisions_get: {e}")
        return {"error": str(e)}


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

def metrics_performance() -> Dict:
    """Get performance metrics."""
    try:
        telemetry = _get_telemetry_collector()
        if telemetry:
            try:
                stats = telemetry.get_all_stats()
                return {
                    "success_rate": stats.get('success_rate', 0) if stats else 0,
                    "avg_mission_time": stats.get('avg_mission_time', 0) if stats else 0,
                    "total_missions": stats.get('total_missions', 0) if stats else 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.debug(f"Could not get telemetry stats: {e}")
                return {
                    "success_rate": 0,
                    "avg_mission_time": 0,
                    "total_missions": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
        else:
            return {
                "success_rate": 0,
                "avg_mission_time": 0,
                "total_missions": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error in metrics_performance: {e}")
        return {"error": str(e)}


# ============================================================================
# LOGS ENDPOINTS
# ============================================================================

def logs_get(limit: int = 100) -> Dict:
    """Get recent logs."""
    try:
        # Return recent system logs
        return {
            "logs": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "source": "System",
                    "message": "System operational via RPC",
                }
            ],
            "total": 1,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in logs_get: {e}")
        return {"error": str(e)}


# ============================================================================
# APPROVALS ENDPOINTS
# ============================================================================

def approvals_list(limit: int = 50) -> Dict:
    """Get pending approvals."""
    try:
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        approval_file = data_dir / "approval_workflow_state.json"
        
        if approval_file.exists():
            with open(approval_file, 'r') as f:
                approvals = json.load(f)
                if isinstance(approvals, dict):
                    # File is keyed by request_id
                    return {
                        "requests": approvals,
                        "total": len(approvals),
                        "pending": len([a for a in approvals.values() if a.get("status") == "pending"]),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                if isinstance(approvals, list):
                    return {
                        "requests": {a.get("request_id", str(i)): a for i, a in enumerate(approvals)},
                        "total": len(approvals),
                        "pending": len([a for a in approvals if a.get("status") == "pending"]),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return {
            "requests": {},
            "total": 0,
            "pending": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in approvals_list: {e}")
        return {"requests": {}, "total": 0, "error": str(e)}


def approvals_summary_stats() -> Dict:
    """Get approval summary statistics."""
    try:
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        approval_file = data_dir / "approval_workflow_state.json"

        total_decisions = 0
        approved_count = 0
        rejected_count = 0
        pending_requests = 0

        if approval_file.exists():
            with open(approval_file, 'r') as f:
                data = json.load(f)
                items = data.values() if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    status = item.get("status", "")
                    if status in ("waiting", "pending"):
                        pending_requests += 1
                    approved = item.get("approved_gaps", [])
                    rejected = item.get("rejected_gaps", [])
                    approved_count += len(approved)
                    rejected_count += len(rejected)
                    total_decisions += len(approved) + len(rejected)

        return {
            "total_decisions": total_decisions,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "pending_requests": pending_requests,
            "approval_rate": ((approved_count / total_decisions * 100) if total_decisions > 0 else 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in approvals_summary_stats: {e}")
        return {"total_decisions": 0, "approved_count": 0, "rejected_count": 0, "pending_requests": 0, "approval_rate": 0, "error": str(e)}


def approvals_approve_request(data: Dict = None) -> Dict:
    """Approve all gaps in a request."""
    try:
        request_id = (data or {}).get("request_id", "")
        if not request_id:
            return {"error": "Missing request_id"}

        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        workflow_file = data_dir / "approval_workflow_state.json"

        if not workflow_file.exists():
            return {"error": "No workflow data found"}

        with open(workflow_file, 'r') as f:
            workflows = json.load(f)

        if request_id not in workflows:
            return {"error": "Request not found"}

        request = workflows[request_id]
        gap_ids = [g.get("gap_id") for g in request.get("market_gaps", [])]
        request["status"] = "fully_approved"
        request["approved_gaps"] = gap_ids
        request["rejected_gaps"] = []
        request["rejection_reasons"] = {}

        with open(workflow_file, 'w') as f:
            json.dump(workflows, f, indent=2)

        _add_notification_rpc(data_dir, "approval", f"Request {request_id} fully approved ({len(gap_ids)} gaps)")
        return {"success": True, "request_id": request_id, "action": "approved_all", "gap_count": len(gap_ids)}
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        return {"error": str(e)}


def approvals_reject_request(data: Dict = None) -> Dict:
    """Reject all gaps in a request."""
    try:
        data = data or {}
        request_id = data.get("request_id", "")
        reason = data.get("reason", "Rejected by reviewer")
        if not request_id:
            return {"error": "Missing request_id"}

        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        workflow_file = data_dir / "approval_workflow_state.json"

        if not workflow_file.exists():
            return {"error": "No workflow data found"}

        with open(workflow_file, 'r') as f:
            workflows = json.load(f)

        if request_id not in workflows:
            return {"error": "Request not found"}

        request = workflows[request_id]
        gap_ids = [g.get("gap_id") for g in request.get("market_gaps", [])]
        request["status"] = "rejected"
        request["approved_gaps"] = []
        request["rejected_gaps"] = gap_ids
        request["rejection_reasons"] = {gid: reason for gid in gap_ids}

        with open(workflow_file, 'w') as f:
            json.dump(workflows, f, indent=2)

        _add_notification_rpc(data_dir, "rejection", f"Request {request_id} rejected ({len(gap_ids)} gaps)")
        return {"success": True, "request_id": request_id, "action": "rejected_all", "gap_count": len(gap_ids)}
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        return {"error": str(e)}


def approvals_approve_gap(data: Dict = None) -> Dict:
    """Approve a specific gap."""
    try:
        data = data or {}
        request_id = data.get("request_id", "")
        gap_id = data.get("gap_id", "")
        if not request_id or not gap_id:
            return {"error": "Missing request_id or gap_id"}

        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        decisions_file = data_dir / "approval_decisions.json"
        decisions_file.parent.mkdir(parents=True, exist_ok=True)

        decisions = {}
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)

        if request_id not in decisions:
            decisions[request_id] = []
        decisions[request_id].append({
            "gap_id": gap_id, "approved": True,
            "decision_time": datetime.utcnow().isoformat(), "reason": None
        })
        with open(decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)

        return {"success": True, "gap_id": gap_id, "action": "approved"}
    except Exception as e:
        logger.error(f"Error approving gap: {e}")
        return {"error": str(e)}


def approvals_reject_gap(data: Dict = None) -> Dict:
    """Reject a specific gap."""
    try:
        data = data or {}
        request_id = data.get("request_id", "")
        gap_id = data.get("gap_id", "")
        reason = data.get("reason", "No reason provided")
        if not request_id or not gap_id:
            return {"error": "Missing request_id or gap_id"}

        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        data_dir = package_root / "data"
        decisions_file = data_dir / "approval_decisions.json"
        decisions_file.parent.mkdir(parents=True, exist_ok=True)

        decisions = {}
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)

        if request_id not in decisions:
            decisions[request_id] = []
        decisions[request_id].append({
            "gap_id": gap_id, "approved": False,
            "decision_time": datetime.utcnow().isoformat(), "reason": reason
        })
        with open(decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)

        return {"success": True, "gap_id": gap_id, "action": "rejected", "reason": reason}
    except Exception as e:
        logger.error(f"Error rejecting gap: {e}")
        return {"error": str(e)}


# ============================================================================
# NOTIFICATION ENDPOINTS (RPC)
# ============================================================================

def _add_notification_rpc(data_dir: Path, ntype: str, message: str, metadata: dict = None):
    """Helper to add a notification."""
    notifications_file = data_dir / "notifications.json"
    notifications = []
    if notifications_file.exists():
        try:
            with open(notifications_file, 'r') as f:
                notifications = json.load(f)
        except (json.JSONDecodeError, ValueError):
            notifications = []
    notifications.insert(0, {
        "id": f"notif_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(notifications)}",
        "type": ntype,
        "message": message,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat(),
        "read": False
    })
    notifications = notifications[:100]
    with open(notifications_file, 'w') as f:
        json.dump(notifications, f, indent=2)


def notifications_list(**kwargs) -> Dict:
    """Get all notifications."""
    try:
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        notifications_file = package_root / "data" / "notifications.json"

        if not notifications_file.exists():
            return {"notifications": [], "unread_count": 0, "timestamp": datetime.utcnow().isoformat()}

        with open(notifications_file, 'r') as f:
            notifications = json.load(f)

        unread_only = kwargs.get("unread_only", False)
        if unread_only:
            notifications = [n for n in notifications if not n.get("read")]

        unread_count = sum(1 for n in notifications if not n.get("read"))
        return {"notifications": notifications, "unread_count": unread_count, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return {"notifications": [], "unread_count": 0, "error": str(e)}


def notifications_mark_read(data: Dict = None) -> Dict:
    """Mark a notification as read."""
    try:
        notification_id = (data or {}).get("id", "")
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        notifications_file = package_root / "data" / "notifications.json"

        if not notifications_file.exists():
            return {"error": "No notifications"}

        with open(notifications_file, 'r') as f:
            notifications = json.load(f)

        for n in notifications:
            if n.get("id") == notification_id:
                n["read"] = True
                break

        with open(notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)

        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def notifications_read_all(**kwargs) -> Dict:
    """Mark all notifications as read."""
    try:
        script_dir = Path(__file__).parent
        package_root = script_dir.parent
        notifications_file = package_root / "data" / "notifications.json"

        if not notifications_file.exists():
            return {"success": True}

        with open(notifications_file, 'r') as f:
            notifications = json.load(f)

        for n in notifications:
            n["read"] = True

        with open(notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)

        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# TASKS ENDPOINTS
# ============================================================================

def tasks_create(name: str, task_type: str, **kwargs) -> Dict:
    """Create a new task"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        task = executor.create_task(name, task_type, **kwargs)
        
        return {
            "success": True,
            "task_id": task.id,
            "task": task.to_dict()
        }
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {"success": False, "error": str(e)}


def tasks_list() -> Dict:
    """Get all tasks"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        tasks = list(executor.tasks.values())
        
        return {
            "tasks": [t.to_dict() for t in tasks],
            "total": len(tasks),
            "stats": executor.get_stats()
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return {"tasks": [], "total": 0, "error": str(e)}


def tasks_get(task_id: str) -> Dict:
    """Get task details"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        task = executor.get_task(task_id)
        
        if not task:
            return {"error": "Task not found"}
        
        return task.to_dict()
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return {"error": str(e)}


def tasks_start(task_id: str) -> Dict:
    """Start a task"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.start_task(task_id)
        
        if success:
            task = executor.get_task(task_id)
            return {"success": True, "task": task.to_dict() if task and hasattr(task, 'to_dict') else {"id": task_id}}
        else:
            return {"success": False, "error": "Failed to start task"}
    except Exception as e:
        logger.error(f"Error starting task: {e}")
        return {"success": False, "error": str(e)}


def tasks_update_progress(task_id: str, current_step: int, total_steps: int, 
                         estimated_remaining: int = 0) -> Dict:
    """Update task progress"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.update_progress(task_id, current_step, total_steps, estimated_remaining)
        
        if success:
            task = executor.get_task(task_id)
            return {"success": True, "progress_percent": task.progress_percent if task else 0}
        else:
            return {"success": False, "error": "Failed to update progress"}
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        return {"success": False, "error": str(e)}


def tasks_complete(task_id: str, result: Optional[Dict] = None) -> Dict:
    """Mark task as completed"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.complete_task(task_id, result)
        
        if success:
            return {"success": True, "task_id": task_id}
        else:
            return {"success": False, "error": "Failed to complete task"}
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {"success": False, "error": str(e)}


def tasks_fail(task_id: str, error: str) -> Dict:
    """Mark task as failed"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.fail_task(task_id, error)
        
        if success:
            return {"success": True, "task_id": task_id}
        else:
            return {"success": False, "error": "Failed to mark task as failed"}
    except Exception as e:
        logger.error(f"Error failing task: {e}")
        return {"success": False, "error": str(e)}


def tasks_cancel(task_id: str) -> Dict:
    """Cancel a task"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.cancel_task(task_id)
        
        if success:
            return {"success": True, "task_id": task_id}
        else:
            return {"success": False, "error": "Failed to cancel task"}
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        return {"success": False, "error": str(e)}


def tasks_pause(task_id: str) -> Dict:
    """Pause a task"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.pause_task(task_id)
        
        if success:
            return {"success": True, "task_id": task_id}
        else:
            return {"success": False, "error": "Failed to pause task"}
    except Exception as e:
        logger.error(f"Error pausing task: {e}")
        return {"success": False, "error": str(e)}


def tasks_resume(task_id: str) -> Dict:
    """Resume a paused task"""
    try:
        from piddy.task_engine import get_task_executor
        
        executor = get_task_executor()
        success = executor.resume_task(task_id)
        
        if success:
            return {"success": True, "task_id": task_id}
        else:
            return {"success": False, "error": "Failed to resume task"}
    except Exception as e:
        logger.error(f"Error resuming task: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# OFFLINE SUPPORT - Mission Queueing for Offline Mode
# ============================================================================

def offline_queue_mission(mission_id: str, agent: str, task: str, metadata: Optional[Dict] = None) -> Dict:
    """
    Queue a mission for execution (typically when offline)
    
    Returns mission in queue with status and timestamps
    """
    try:
        if not HAS_OFFLINE_SUPPORT:
            return {"error": "Offline support not available"}
        
        queue = get_offline_queue()
        result = queue.queue_mission(mission_id, agent, task, metadata)
        
        return {
            "success": True,
            "queued": result,
        }
    except Exception as e:
        logger.error(f"Error queuing mission: {e}")
        return {"success": False, "error": str(e)}


def offline_get_queue_status() -> Dict:
    """Get status of offline mission queue"""
    try:
        if not HAS_OFFLINE_SUPPORT:
            return {"error": "Offline support not available"}
        
        queue = get_offline_queue()
        stats = queue.get_queue_stats()
        
        return {
            "success": True,
            "queue_status": stats,
        }
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return {"success": False, "error": str(e)}


def offline_get_pending_missions(limit: int = 50) -> Dict:
    """Get list of pending missions in queue"""
    try:
        if not HAS_OFFLINE_SUPPORT:
            return {"error": "Offline support not available"}
        
        queue = get_offline_queue()
        missions = queue.get_pending_missions(limit)
        
        return {
            "success": True,
            "pending_missions": missions,
            "count": len(missions),
        }
    except Exception as e:
        logger.error(f"Error getting pending missions: {e}")
        return {"success": False, "error": str(e)}


def offline_set_connectivity_status(is_online: bool) -> Dict:
    """Update connectivity status (online/offline)"""
    try:
        if not HAS_OFFLINE_SUPPORT:
            return {"error": "Offline support not available"}
        
        queue = get_offline_queue()
        sync_manager = get_sync_manager(queue)
        
        sync_manager.set_connectivity_status(is_online)
        
        return {
            "success": True,
            "is_online": is_online,
            "queue_status": queue.get_queue_stats(),
        }
    except Exception as e:
        logger.error(f"Error setting connectivity status: {e}")
        return {"success": False, "error": str(e)}


def offline_clear_completed_missions(older_than_hours: int = 24) -> Dict:
    """Clean up old completed missions from queue"""
    try:
        if not HAS_OFFLINE_SUPPORT:
            return {"error": "Offline support not available"}
        
        queue = get_offline_queue()
        deleted_count = queue.clear_completed_missions(older_than_hours)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
        }
    except Exception as e:
        logger.error(f"Error clearing completed missions: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# NOVA COORDINATOR ENDPOINTS (Integrated Pipeline)
# ============================================================================

def nova_execute_with_consensus(task: str, requester: str = "system") -> Dict:
    """
    Execute a mission end-to-end with Phase 40 planning, Phase 50 voting, 
    code execution, PR generation, and GitHub push.
    
    This is the main entry point for AI-driven code execution.
    """
    try:
        from src.nova_coordinator import get_nova_coordinator
        coordinator = get_nova_coordinator()
        
        # Run async function synchronously
        coro = coordinator.execute_with_consensus(task, requester)
        result = _run_async(coro)
        
        return result or {"status": "failed", "error": "No result"}
    except Exception as e:
        logger.error(f"Error in nova_execute_with_consensus: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


def nova_get_mission_status(mission_id: str) -> Dict:
    """Get the status and details of a specific mission."""
    try:
        from src.nova_coordinator import get_nova_coordinator
        coordinator = get_nova_coordinator()
        
        result = coordinator.get_mission_status(mission_id)
        if result:
            return result
        else:
            return {"error": f"Mission {mission_id} not found", "mission_id": mission_id}
    except Exception as e:
        logger.error(f"Error in nova_get_mission_status: {e}")
        return {"error": str(e), "mission_id": mission_id}


def nova_list_recent_missions(limit: int = 10) -> List[Dict]:
    """List recent mission executions."""
    try:
        from src.nova_coordinator import get_nova_coordinator
        coordinator = get_nova_coordinator()
        
        return coordinator.list_recent_missions(limit)
    except Exception as e:
        logger.error(f"Error in nova_list_recent_missions: {e}")
        return []


# ============================================================================
# CONFIGURATION - Key Management Endpoints
# ============================================================================

def config_status() -> Dict:
    """Check whether Piddy is configured (keys present)."""
    try:
        from src.config.key_manager import get_config_status
        return get_config_status()
    except Exception as e:
        logger.error(f"Error getting config status: {e}")
        return {"configured": False, "error": str(e)}


def config_save(payload: Optional[Dict] = None) -> Dict:
    """Save / update API keys (encrypted at rest)."""
    try:
        from src.config.key_manager import save_keys, get_config_status
        if payload:
            save_keys(payload)
        return {"status": "saved", **get_config_status()}
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return {"status": "error", "error": str(e)}


def config_test(payload: Optional[Dict] = None) -> Dict:
    """Validate a single API key against its provider (sync stub - full test requires async)."""
    if not payload:
        return {"valid": False, "error": "No payload"}
    provider = (payload.get("provider") or "").lower()
    key = (payload.get("key") or "").strip()
    if not key:
        return {"valid": False, "error": "Key is empty"}
    # Sync key format validation (actual provider call is async in HTTP endpoint)
    if provider == "anthropic":
        return {"valid": key.startswith("sk-ant-"), "provider": "anthropic",
                "error": None if key.startswith("sk-ant-") else "Key should start with sk-ant-"}
    elif provider == "openai":
        return {"valid": key.startswith("sk-"), "provider": "openai",
                "error": None if key.startswith("sk-") else "Key should start with sk-"}
    return {"valid": False, "error": f"Unknown provider: {provider}"}


# ============================================================================
# Phase 51: Autonomous Loop Endpoints
# ============================================================================

def autonomous_execute(task: str, max_retries: int = 5, consensus_type: str = "UNANIMOUS") -> Dict:
    """Execute a task with autonomous retry loop (try -> diagnose -> fix -> retry)."""
    try:
        coordinator = _get_coordinator()
        from src.phase51_autonomous_loop import execute_with_autonomous_loop
        result = _run_async(execute_with_autonomous_loop(
            coordinator, task, max_retries=max_retries, consensus_type=consensus_type,
        ))
        return result
    except ImportError:
        return {"status": "error", "error": "Phase 51 not available"}
    except Exception as e:
        logger.error(f"Autonomous execute error: {e}")
        return {"status": "error", "error": str(e)}


def autonomous_failure_summary() -> Dict:
    """Get failure memory summary (total failures, fix rate, top error types)."""
    try:
        from src.phase51_autonomous_loop import FailureMemory
        fm = FailureMemory()
        return fm.get_failure_summary()
    except ImportError:
        return {"status": "error", "error": "Phase 51 not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def autonomous_failure_history(task: str = "", error_type: str = "", limit: int = 20) -> Dict:
    """Get past failures filtered by task or error type."""
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


def autonomous_strategy_stats(task: str = "") -> Dict:
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


def synthesized_tools_list() -> Dict:
    """List all tools that have been dynamically created by the ToolSynthesizer."""
    try:
        from src.tools.synthesized.synthesizer import ToolSynthesizer
        synth = ToolSynthesizer()
        tools = synth.list_synthesized_tools()
        return {"tools": tools, "count": len(tools)}
    except ImportError:
        return {"status": "error", "error": "ToolSynthesizer not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def synthesized_tools_run(tool_name: str, params: Optional[Dict] = None) -> Dict:
    """Run a synthesized tool by name with optional parameters."""
    try:
        from src.tools.synthesized.synthesizer import ToolSynthesizer
        synth = ToolSynthesizer()
        func = synth.get_tool_function(tool_name)
        if not func:
            return {"status": "error", "error": f"Synthesized tool '{tool_name}' not found"}
        result = func(**(params or {}))
        synth.record_usage(tool_name, result.get("status") == "success")
        return result
    except ImportError:
        return {"status": "error", "error": "ToolSynthesizer not available"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================================================
# DATABASE PERFORMANCE
# ============================================================================

def autonomous_database_performance() -> Dict:
    """Get database performance metrics from SQLite databases."""
    try:
        script_dir = Path(__file__).parent
        package_root = script_dir.parent

        db_files = list(package_root.glob("*.db")) + list((package_root / "data").glob("*.db"))
        total_size = 0
        table_count = 0
        total_rows = 0
        tables_info = []

        for db_path in db_files:
            try:
                import sqlite3
                db_size = db_path.stat().st_size
                total_size += db_size
                conn = sqlite3.connect(str(db_path), timeout=2)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                db_tables = cursor.fetchall()
                # Count indexes per table
                cursor.execute("SELECT tbl_name, COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' GROUP BY tbl_name")
                index_counts = dict(cursor.fetchall())
                db_table_count = len(db_tables)
                for (tname,) in db_tables:
                    table_count += 1
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM [{tname}]")
                        row_count = cursor.fetchone()[0]
                        total_rows += row_count
                        tables_info.append({
                            "name": tname,
                            "database": db_path.name,
                            "row_count": row_count,
                            "size_mb": round(db_size / (1024 * 1024) / max(db_table_count, 1), 4),
                            "index_count": index_counts.get(tname, 0),
                        })
                    except Exception:
                        tables_info.append({"name": tname, "database": db_path.name, "row_count": 0, "size_mb": 0, "index_count": 0})
                conn.close()
            except Exception as e:
                logger.debug(f"Could not read {db_path}: {e}")

        health_status = "healthy" if db_files else "no_databases"

        return {
            "database": {
                "size_mb": round(total_size / (1024 * 1024), 2),
                "table_count": table_count,
                "total_rows": total_rows,
                "db_files": len(db_files),
                "tables": tables_info,
                "health": {"status": health_status},
                "status": health_status,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error in autonomous_database_performance: {e}")
        return {"database": {"size_mb": 0, "table_count": 0, "total_rows": 0, "tables": [], "status": "error"}, "error": str(e)}


# ============================================================================
# CHAT (Agent conversation via 4-tier LLM failover)
# ============================================================================

_agent = None
_session_mgr = None
_agent_imports_done = False


def _ensure_agent_imports():
    """Lazy-import agent and session manager on first chat call."""
    global _agent, _session_mgr, _agent_imports_done
    if _agent_imports_done:
        return
    _agent_imports_done = True
    try:
        from src.agent.core import BackendDeveloperAgent
        _agent = BackendDeveloperAgent()
        logger.info("✅ Agent initialized for RPC chat")
    except Exception as e:
        logger.warning(f"⚠️ Agent not available for RPC chat: {e}")
    try:
        from src.sessions.manager import get_session_manager
        _session_mgr = get_session_manager()
    except Exception:
        pass


async def _chat_async(data: Dict) -> Dict:
    """Async chat handler — mirrors /api/chat REST endpoint."""
    import re as _re
    from src.agent.core import Command, CommandType, CommandResponse
    from src.agent.action_parser import parse_file_actions, execute_file_actions, strip_file_markers
    from src.agent.build_learnings import record_build_outcome, record_cloud_fix_lesson
    from src.agent.code_verifier import verify_files, format_issues_for_llm

    def _record_experience(file_actions, description, change_type="bug_fix",
                           outcome="success", success_score=0.85):
        """Record a code change to Phase 19 self-improving agent + KB."""
        try:
            from src.phase19_self_improving_agent import SelfImprovingAgent
            agent = SelfImprovingAgent()
            for fa in file_actions:
                agent.record_code_change(
                    file_path=fa.get("path", "unknown"),
                    change_type=change_type,
                    description=description[:500],
                    code_after=fa.get("content", "")[:2000],
                    outcome=outcome,
                    success_score=success_score,
                )
            logger.info(f"🧠 Phase 19: Recorded {len(file_actions)} experience(s) ({change_type})")
        except Exception as exp_err:
            logger.debug(f"Phase 19 recording skipped: {exp_err}")

    message = (data.get("message") or "").strip()
    session_id = data.get("session_id")
    user_id = data.get("user_id", "default")

    if not message:
        return {"error": "Message is required"}

    _ensure_agent_imports()

    # Session tracking
    if _session_mgr:
        if not session_id:
            session = _session_mgr.create_session(user_id=user_id, title=message[:60])
            session_id = session.session_id
        _session_mgr.add_message(session_id, "user", message)

    reply = None
    source = "fallback"
    actions_taken: List[Dict] = []

    def _looks_like_build_request(text: str) -> bool:
        """Heuristic: did the user ask to create/build/scaffold something?"""
        build_words = r"\b(build|create|scaffold|generate|make|write|implement|set up|setup)\b"
        return bool(_re.search(build_words, text, _re.IGNORECASE))

    def _response_has_unparsed_code(text: str) -> bool:
        """Heuristic: response has code blocks that look like file content."""
        code_blocks = _re.findall(r"```\w*\n", text)
        file_hints = _re.findall(r"(?:FILE:|file:|\.py|\.js|\.html|\.css|\.json)\b", text, _re.IGNORECASE)
        return len(code_blocks) >= 2 and len(file_hints) >= 2

    def _detect_parse_method(text: str) -> str:
        """Detect which parse method would match (for learning)."""
        if "===FILE:" in text and "===END_FILE===" in text:
            return "explicit_markers"
        if _re.search(r"#+\s*FILE:\s*\S+", text):
            return "file_heading"
        if _re.search(r"#+\s*[`*]*\S+\.\w{1,10}[`*]*\s*\n```", text):
            return "fenced_block"
        return "none"

    if _agent is not None:
        try:
            cmd = Command(
                command_type=CommandType.CONVERSATION,
                description=message,
                context={"query": message},
                source="desktop_chat",
                metadata={"is_conversation": True, "session_id": session_id or ""},
            )
            response: CommandResponse = await _agent.process_command(cmd)
            if response.success and response.result:
                raw_reply = str(response.result)
                tier_used = response.metadata.get("llm_used", "unknown") if response.metadata else "unknown"
                engine_used = response.metadata.get("engine", "unknown") if response.metadata else "unknown"
                source = response.metadata.get("tier", "agent") if response.metadata else "agent"

                # ── Agentic post-processing: extract & execute file actions ──
                file_actions = parse_file_actions(raw_reply)
                if file_actions:
                    actions_taken = execute_file_actions(file_actions)
                    # Attach file content to each action for the code panel
                    _content_map = {fa["path"].replace("\\", "/").strip("/"): fa["content"] for fa in file_actions}
                    for act in actions_taken:
                        act_path = act["path"].replace("\\", "/")
                        # Try exact match, then strip leading "projects/"
                        bare = act_path.removeprefix("projects/")
                        act["content"] = _content_map.get(bare, _content_map.get(act_path, ""))
                        # Derive language from extension
                        ext = bare.rsplit(".", 1)[-1] if "." in bare else ""
                        act["language"] = ext
                    reply = strip_file_markers(raw_reply)
                    logger.info(f"🛠️ Executed {len(actions_taken)} file action(s) from chat response")

                    # ── Phase 53: Verify generated code ──
                    verification = verify_files(file_actions)
                    for act in actions_taken:
                        act["verification"] = verification

                    # ── Auto-fix loop: if errors found, ask LLM to fix ──
                    if not verification["passed"] and not (_agent.settings.local_only if hasattr(_agent, 'settings') else False):
                        fix_prompt = format_issues_for_llm(verification)
                        max_fix_attempts = 2
                        for fix_attempt in range(1, max_fix_attempts + 1):
                            logger.info(
                                f"🔧 Auto-fix attempt {fix_attempt}/{max_fix_attempts}: "
                                f"{verification['error_count']} error(s) to fix"
                            )
                            # Build a targeted fix prompt with the original code + issues
                            fix_context = (
                                f"The user asked: {message}\n\n"
                                f"You generated code but it has issues:\n{fix_prompt}\n\n"
                                "Here are the original files you created:\n"
                            )
                            for fa in file_actions:
                                fix_context += f"\n===FILE: {fa['path']}===\n{fa['content']}===END_FILE===\n"
                            fix_context += (
                                "\nFix ALL issues listed above. Output ONLY the corrected files "
                                "using ===FILE: path=== ... ===END_FILE=== format."
                            )

                            # Try to get a fix from the LLM
                            fix_reply = None
                            try:
                                fix_cmd = Command(
                                    command_type=CommandType.CONVERSATION,
                                    description=fix_context,
                                    context={"query": fix_context},
                                    source="auto_fix",
                                    metadata={"is_conversation": True, "session_id": session_id or ""},
                                )
                                fix_response = await _agent.process_command(fix_cmd)
                                if fix_response.success and fix_response.result:
                                    fix_reply = str(fix_response.result)
                            except Exception as fix_err:
                                logger.warning(f"Auto-fix LLM call failed: {fix_err}")
                                break

                            if not fix_reply:
                                break

                            # Parse and apply fixes
                            fix_actions = parse_file_actions(fix_reply)
                            if not fix_actions:
                                logger.warning("Auto-fix produced no parseable files")
                                break

                            # Re-execute only the fixed files
                            fix_results = execute_file_actions(fix_actions)

                            # Merge fixed files into our tracking
                            fix_content_map = {fa["path"].replace("\\", "/").strip("/"): fa["content"] for fa in fix_actions}
                            for fa in fix_actions:
                                norm = fa["path"].replace("\\", "/").strip("/")
                                # Update the original file_actions content
                                for orig in file_actions:
                                    if orig["path"].replace("\\", "/").strip("/") == norm:
                                        orig["content"] = fa["content"]
                                        break
                                # Update actions_taken
                                for act in actions_taken:
                                    bare = act["path"].replace("\\", "/").removeprefix("projects/")
                                    if bare == norm:
                                        act["content"] = fa["content"]
                                        act["size"] = len(fa["content"])
                                        break

                            # Re-verify
                            verification = verify_files(file_actions)
                            for act in actions_taken:
                                act["verification"] = verification

                            if verification["passed"]:
                                logger.info(f"✅ Auto-fix succeeded on attempt {fix_attempt}")
                                reply = strip_file_markers(raw_reply) + (
                                    f"\n\n🔧 *Auto-fix applied ({fix_attempt} pass{'es' if fix_attempt > 1 else ''}) "
                                    f"— {verification['summary']}*"
                                )
                                # Phase 19: Record the successful fix for learning
                                _record_experience(
                                    file_actions,
                                    f"Auto-fix ({engine_used}): {message[:200]}",
                                    change_type="bug_fix", outcome="success",
                                    success_score=0.8,
                                )
                                break
                            else:
                                fix_prompt = format_issues_for_llm(verification)
                        else:
                            # Exhausted fix attempts — escalate to cloud if Ollama was the engine
                            logger.warning(
                                f"⚠️ Auto-fix exhausted {max_fix_attempts} attempts, "
                                f"{verification['error_count']} error(s) remain"
                            )

                            # ── Cloud LLM escalation: let Anthropic/OpenAI fix Ollama's mistakes ──
                            cloud_fixed = False
                            if engine_used == "ollama" and not (_agent.settings.local_only if hasattr(_agent, 'settings') else False):
                                logger.info(
                                    "🎓 Escalating to cloud LLM — Ollama couldn't self-fix "
                                    f"{verification['error_count']} error(s)"
                                )
                                # Capture Ollama's broken code before cloud fixes it
                                ollama_broken_code = {
                                    fa["path"]: fa["content"] for fa in file_actions
                                }
                                error_summary = format_issues_for_llm(verification)

                                # Build a cloud fix prompt with full context
                                cloud_fix_context = (
                                    f"The user asked: {message}\n\n"
                                    f"A local LLM generated code but it has errors that "
                                    f"couldn't be auto-fixed after {max_fix_attempts} attempts:\n"
                                    f"{error_summary}\n\n"
                                    "Here are the files with issues:\n"
                                )
                                for fa in file_actions:
                                    cloud_fix_context += f"\n===FILE: {fa['path']}===\n{fa['content']}===END_FILE===\n"
                                cloud_fix_context += (
                                    "\nFix ALL issues listed above. Output ONLY the corrected files "
                                    "using ===FILE: path=== ... ===END_FILE=== format."
                                )

                                try:
                                    cloud_fix_cmd = Command(
                                        command_type=CommandType.CONVERSATION,
                                        description=cloud_fix_context,
                                        context={"query": cloud_fix_context},
                                        source="cloud_escalation_fix",
                                        metadata={
                                            "is_conversation": True,
                                            "session_id": session_id or "",
                                            "force_cloud": True,
                                        },
                                    )
                                    # Call cloud LLMs directly (skip Ollama)
                                    cloud_prompt = _agent._format_command_prompt(cloud_fix_cmd)
                                    cloud_fix_resp = await _agent._try_cloud_llms(
                                        cloud_fix_cmd, cloud_prompt, True
                                    )

                                    if cloud_fix_resp and cloud_fix_resp.success and cloud_fix_resp.result:
                                        cloud_fix_raw = str(cloud_fix_resp.result)
                                        cloud_tier = (
                                            cloud_fix_resp.metadata.get("llm_used", "cloud")
                                            if cloud_fix_resp.metadata else "cloud"
                                        )
                                        cloud_fix_actions = parse_file_actions(cloud_fix_raw)

                                        if cloud_fix_actions:
                                            # Apply cloud fixes
                                            execute_file_actions(cloud_fix_actions)

                                            # Merge into tracking
                                            cloud_content_map = {
                                                fa["path"].replace("\\", "/").strip("/"): fa["content"]
                                                for fa in cloud_fix_actions
                                            }
                                            for fa in cloud_fix_actions:
                                                norm = fa["path"].replace("\\", "/").strip("/")
                                                for orig in file_actions:
                                                    if orig["path"].replace("\\", "/").strip("/") == norm:
                                                        orig["content"] = fa["content"]
                                                        break
                                                for act in actions_taken:
                                                    bare = act["path"].replace("\\", "/").removeprefix("projects/")
                                                    if bare == norm:
                                                        act["content"] = fa["content"]
                                                        act["size"] = len(fa["content"])
                                                        break

                                            # Verify the cloud fix
                                            cloud_verification = verify_files(file_actions)
                                            for act in actions_taken:
                                                act["verification"] = cloud_verification

                                            if cloud_verification["passed"]:
                                                cloud_fixed = True
                                                verification = cloud_verification
                                                logger.info(
                                                    f"✅ Cloud LLM ({cloud_tier}) fixed all errors!"
                                                )
                                                reply = strip_file_markers(raw_reply) + (
                                                    f"\n\n🎓 *{cloud_tier} fixed {len(verification.get('issues', []))} "
                                                    f"issue(s) that local LLM couldn't resolve — "
                                                    f"lesson recorded for future builds*"
                                                )
                                            else:
                                                logger.warning(
                                                    f"Cloud fix by {cloud_tier} still has "
                                                    f"{cloud_verification['error_count']} error(s)"
                                                )
                                                reply += (
                                                    f"\n\n⚠️ *Cloud LLM ({cloud_tier}) attempted fix but "
                                                    f"{cloud_verification['error_count']} issue(s) remain*"
                                                )

                                            # ── Record the lesson regardless ──
                                            # Even partial fixes teach Ollama something
                                            cloud_fixed_code = {
                                                fa["path"]: fa["content"] for fa in cloud_fix_actions
                                            }
                                            # Use Ollama's original errors as the lesson
                                            ollama_verification = verify_files(
                                                [{"path": p, "content": c} for p, c in ollama_broken_code.items()]
                                            )
                                            issues_list = [
                                                iss.get("message", str(iss))
                                                for iss in ollama_verification.get("issues", [])
                                            ]
                                            record_cloud_fix_lesson(
                                                ollama_model=tier_used,
                                                cloud_model=cloud_tier,
                                                user_prompt=message,
                                                error_summary=error_summary,
                                                ollama_code=ollama_broken_code,
                                                cloud_code=cloud_fixed_code,
                                                issues_fixed=issues_list,
                                            )

                                except Exception as cloud_err:
                                    logger.warning(f"Cloud escalation fix failed: {cloud_err}")

                            if not cloud_fixed:
                                reply += (
                                    f"\n\n⚠️ *Verification found {verification['error_count']} issue(s) "
                                    f"that couldn't be auto-fixed — see diagnostics panel*"
                                )

                    # Record build outcome (learning)
                    errors = [a["error"] for a in actions_taken if not a.get("success")]
                    record_build_outcome(
                        llm_tier=engine_used,
                        llm_model=tier_used,
                        user_prompt=message,
                        files_expected=len(file_actions),
                        files_created=sum(1 for a in actions_taken if a.get("success")),
                        errors=errors,
                        parse_method=_detect_parse_method(raw_reply),
                        raw_snippet=raw_reply[:300],
                    )

                    # ── Dashboard: Log verification as test results ──
                    try:
                        from src.dashboard_data_collector import log_test_result
                        for fa in file_actions:
                            log_test_result(
                                test_name=f"verify:{fa.get('path', 'unknown')}",
                                status="passed" if verification["passed"] else "failed",
                                duration=0.0,
                                message=verification.get("summary", ""),
                            )
                    except Exception:
                        pass

                    # ── Phase 19: Record experience for KB learning ──
                    if verification["passed"]:
                        _record_experience(
                            file_actions, f"Build success: {message[:200]}",
                            change_type="enhancement", outcome="success",
                            success_score=0.9,
                        )
                else:
                    # ── Parse-quality fallback ──
                    # If the user asked to build something and Ollama returned
                    # code that didn't parse, escalate to Anthropic/OpenAI
                    is_build = _looks_like_build_request(message)
                    has_code = _response_has_unparsed_code(raw_reply)

                    if is_build and has_code and engine_used == "ollama" and not (_agent.settings.local_only if hasattr(_agent, 'settings') else False):
                        logger.warning(
                            "⚠️ Ollama returned unparsed build output — escalating to cloud LLM"
                        )
                        # Record the parse failure
                        record_build_outcome(
                            llm_tier=engine_used,
                            llm_model=tier_used,
                            user_prompt=message,
                            files_expected=0,
                            files_created=0,
                            errors=["LLM output not parseable — no ===FILE: markers found"],
                            parse_method="none",
                            raw_snippet=raw_reply[:300],
                        )

                        # Retry with cloud LLMs
                        from src.agent.action_parser import AGENTIC_PROMPT_ADDON
                        from src.agent.build_learnings import build_lessons_prompt

                        prompt = _agent._format_command_prompt(cmd)
                        cloud_resp = await _agent._try_cloud_llms(cmd, prompt, True)
                        if cloud_resp and cloud_resp.success and cloud_resp.result:
                            cloud_raw = str(cloud_resp.result)
                            cloud_tier = cloud_resp.metadata.get("llm_used", "cloud") if cloud_resp.metadata else "cloud"
                            cloud_engine = cloud_resp.metadata.get("engine", "cloud") if cloud_resp.metadata else "cloud"

                            cloud_actions = parse_file_actions(cloud_raw)
                            if cloud_actions:
                                actions_taken = execute_file_actions(cloud_actions)
                                _content_map = {fa["path"].replace("\\", "/").strip("/"): fa["content"] for fa in cloud_actions}
                                for act in actions_taken:
                                    bare = act["path"].replace("\\", "/").removeprefix("projects/")
                                    act["content"] = _content_map.get(bare, _content_map.get(act["path"].replace("\\", "/"), ""))
                                    ext = bare.rsplit(".", 1)[-1] if "." in bare else ""
                                    act["language"] = ext
                                reply = strip_file_markers(cloud_raw)
                                source = cloud_tier
                                logger.info(
                                    f"✅ Cloud fallback created {len(actions_taken)} file(s) "
                                    f"via {cloud_tier}"
                                )
                                # Verify cloud-generated code too
                                cloud_verification = verify_files(cloud_actions)
                                for act in actions_taken:
                                    act["verification"] = cloud_verification
                                if not cloud_verification["passed"]:
                                    reply += (
                                        f"\n\n⚠️ *Verification: {cloud_verification['summary']}*"
                                    )
                                errors = [a["error"] for a in actions_taken if not a.get("success")]
                                record_build_outcome(
                                    llm_tier=cloud_engine,
                                    llm_model=cloud_tier,
                                    user_prompt=message,
                                    files_expected=len(cloud_actions),
                                    files_created=sum(1 for a in actions_taken if a.get("success")),
                                    errors=errors,
                                    parse_method=_detect_parse_method(cloud_raw),
                                    raw_snippet=cloud_raw[:300],
                                )
                                # Phase 19: Record cloud fallback build for learning
                                if cloud_verification["passed"]:
                                    _record_experience(
                                        cloud_actions,
                                        f"Cloud fallback build ({cloud_tier}): {message[:200]}",
                                        change_type="enhancement", outcome="success",
                                        success_score=0.9,
                                    )
                            else:
                                reply = cloud_raw
                                source = cloud_tier
                        else:
                            # Cloud also failed — use original Ollama reply
                            reply = raw_reply
                    else:
                        reply = raw_reply
        except Exception as e:
            logger.error(f"Agent error in RPC chat: {e}", exc_info=True)

    if not reply:
        reply = (
            "I'm here but my language models aren't available right now. "
            "Check the Health page to see what's offline, or configure API keys in Settings."
        )
        source = "fallback"

    if _session_mgr and session_id:
        try:
            _session_mgr.add_message(session_id, "assistant", reply, {"source": source})
            _session_mgr.summarize_if_needed(session_id)
        except Exception:
            pass

    # ── Dashboard data collection: log message + decision ──
    try:
        from src.dashboard_data_collector import log_chat_message, log_decision
        log_chat_message(
            user_message=message,
            reply=reply or "",
            source=source,
            tier_used=tier_used if 'tier_used' in dir() else "unknown",
            engine_used=engine_used if 'engine_used' in dir() else "unknown",
            files_created=len(actions_taken),
            session_id=session_id or "",
        )
        if actions_taken:
            log_decision(
                task=message[:200],
                agent_id=engine_used if 'engine_used' in dir() else "piddy",
                action=f"Created {len(actions_taken)} file(s)",
                confidence=0.8 if source != "fallback" else 0.1,
                status="executed",
            )
    except Exception:
        pass

    result: Dict[str, Any] = {"reply": reply, "session_id": session_id, "source": source}
    if actions_taken:
        result["actions"] = actions_taken
    return result


def chat_send(data: Optional[Dict] = None) -> Dict:
    """Send a chat message to Piddy and get AI response (4-tier failover)."""
    data = data or {}
    return _run_async_long(_chat_async(data))


# ============================================================================
# SETTINGS (runtime config — non-secret values)
# ============================================================================

def settings_get(data: Optional[Dict] = None) -> Dict:
    """Get all non-secret settings, or update if data is provided."""
    if data:
        return settings_update(data)
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


def settings_update(data: Optional[Dict] = None) -> Dict:
    """Update runtime settings."""
    data = data or {}
    try:
        from config.settings import get_settings
        s = get_settings()
        updated = []
        for key in ["local_only", "ollama_enabled", "ollama_model", "ollama_base_url",
                     "agent_temperature", "agent_max_tokens", "agent_model", "log_level"]:
            if key in data:
                setattr(s, key, data[key])
                updated.append(key)
        return {"success": True, "updated": updated}
    except Exception as e:
        return {"error": str(e)}


def settings_ollama_models() -> Dict:
    """List available Ollama models from the local Ollama instance."""
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
# SCANNER ENDPOINTS
# ============================================================================

def scan_host_rpc(*args, **kwargs) -> Dict:
    """Scan the host machine for development environment info."""
    try:
        return scan_host()
    except Exception as e:
        return {"error": str(e)}


def scan_repo_rpc(data=None, *args, **kwargs) -> Dict:
    """Analyze a repository."""
    try:
        repo_path = ""
        if isinstance(data, dict):
            repo_path = data.get("path", data.get("repo_path", ""))
        elif isinstance(data, str):
            repo_path = data
        return analyze_repo(repo_path) if repo_path else {"error": "No path provided"}
    except Exception as e:
        return {"error": str(e)}


def scan_programs_rpc(*args, **kwargs) -> Dict:
    """Scan installed programs on the host."""
    try:
        programs = scan_installed_programs()
        return {"programs": programs}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# BROWSER AUTOMATION ENDPOINTS
# ============================================================================

def browser_status_rpc(*args, **kwargs) -> Dict:
    """Get browser automation status."""
    try:
        from src.tools.browser_automation import get_browser_tool
        bt = get_browser_tool()
        return bt.status() if hasattr(bt, 'status') else {"status": "available", "launched": False}
    except ImportError:
        return {"status": "unavailable", "error": "Playwright not installed. Run: pip install playwright && python -m playwright install chromium"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def browser_launch_rpc(data=None, *args, **kwargs) -> Dict:
    """Launch browser instance."""
    try:
        from src.tools.browser_automation import get_browser_tool
        bt = get_browser_tool()
        url = data.get("url", "about:blank") if isinstance(data, dict) else "about:blank"
        result = bt.launch(url) if hasattr(bt, 'launch') else bt.navigate(url)
        return {"success": True, "result": result} if not isinstance(result, dict) else result
    except ImportError:
        return {"error": "Playwright not installed"}
    except Exception as e:
        return {"error": str(e)}


def browser_close_rpc(data=None, *args, **kwargs) -> Dict:
    """Close browser instance."""
    try:
        from src.tools.browser_automation import get_browser_tool
        bt = get_browser_tool()
        if hasattr(bt, 'close'):
            bt.close()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def browser_action_rpc(data=None, *args, **kwargs) -> Dict:
    """Execute a browser action (navigate, screenshot, extract)."""
    try:
        from src.tools.browser_automation import get_browser_tool
        bt = get_browser_tool()
        if not isinstance(data, dict):
            return {"error": "Expected dict with 'action' key"}
        action = data.get("action", "")
        url = data.get("url", "")
        if action == "navigate":
            result = bt.navigate(url)
        elif action == "screenshot":
            result = bt.screenshot()
        elif action == "extract_text":
            result = bt.extract_text()
        elif action == "extract_links":
            result = bt.extract_links()
        else:
            return {"error": f"Unknown action: {action}"}
        return {"success": True, "result": result} if not isinstance(result, dict) else result
    except ImportError:
        return {"error": "Playwright not installed"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# INTEGRATIONS (Slack, Discord, Telegram) ENDPOINTS
# ============================================================================

def integrations_status_rpc(*args, **kwargs) -> Dict:
    """Get status of all messaging integrations."""
    try:
        from config.settings import get_settings
        s = get_settings()
        integrations = {
            "slack": {
                "configured": bool(s.slack_bot_token and s.slack_app_token),
                "status": "offline",
            },
            "discord": {
                "configured": bool(s.discord_bot_token),
                "status": "offline",
            },
            "telegram": {
                "configured": bool(s.telegram_bot_token),
                "status": "offline",
            },
        }
        # Check running status
        try:
            from src.integrations.discord_bot import get_discord_bot
            db = get_discord_bot()
            if db and hasattr(db, 'is_running') and db.is_running():
                integrations["discord"]["status"] = "online"
        except Exception:
            pass
        try:
            from src.integrations.telegram_bot import get_telegram_bot
            tb = get_telegram_bot()
            if tb and hasattr(tb, 'is_running') and tb.is_running():
                integrations["telegram"]["status"] = "online"
        except Exception:
            pass
        return integrations
    except Exception as e:
        return {"error": str(e)}


def integrations_action_rpc(data=None, *args, **kwargs) -> Dict:
    """Start or stop a messaging integration. Data: {platform, action}"""
    try:
        if not isinstance(data, dict):
            return {"error": "Expected dict with 'platform' and 'action'"}
        platform = data.get("platform", "")
        action = data.get("action", "")
        if platform == "discord":
            from src.integrations.discord_bot import get_discord_bot
            bot = get_discord_bot()
            if action == "start":
                bot.start()
                return {"success": True, "status": "starting"}
            elif action == "stop":
                bot.stop()
                return {"success": True, "status": "stopped"}
        elif platform == "telegram":
            from src.integrations.telegram_bot import get_telegram_bot
            bot = get_telegram_bot()
            if action == "start":
                bot.start()
                return {"success": True, "status": "starting"}
            elif action == "stop":
                bot.stop()
                return {"success": True, "status": "stopped"}
        return {"error": f"Unknown platform/action: {platform}/{action}"}
    except ImportError as e:
        return {"error": f"Integration not installed: {e}"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# PRODUCTIVITY CONNECTORS (Calendar, Jira, Notion) ENDPOINTS
# ============================================================================

def productivity_status_rpc(*args, **kwargs) -> Dict:
    """Get status of all productivity connectors."""
    try:
        from config.settings import get_settings
        s = get_settings()
        return {
            "google_calendar": {"configured": bool(s.google_calendar_api_key), "status": "configured" if s.google_calendar_api_key else "not_configured"},
            "jira": {"configured": bool(s.jira_base_url and s.jira_api_token), "status": "configured" if s.jira_api_token else "not_configured"},
            "notion": {"configured": bool(s.notion_api_token), "status": "configured" if s.notion_api_token else "not_configured"},
        }
    except Exception as e:
        return {"error": str(e)}


def productivity_calendar_events_rpc(*args, **kwargs) -> Dict:
    """Get Google Calendar events."""
    try:
        from src.integrations.productivity import GoogleCalendarConnector
        gc = GoogleCalendarConnector()
        events = gc.list_events()
        return {"events": events}
    except ImportError:
        return {"error": "Productivity connectors not available"}
    except Exception as e:
        return {"error": str(e)}


def productivity_jira_issues_rpc(*args, **kwargs) -> Dict:
    """Get Jira issues."""
    try:
        from src.integrations.productivity import JiraConnector
        jc = JiraConnector()
        issues = jc.search_issues()
        return {"issues": issues}
    except ImportError:
        return {"error": "Productivity connectors not available"}
    except Exception as e:
        return {"error": str(e)}


def productivity_notion_search_rpc(*args, **kwargs) -> Dict:
    """Search Notion pages."""
    try:
        from src.integrations.productivity import NotionConnector
        nc = NotionConnector()
        q = kwargs.get("q", "") if kwargs else ""
        results = nc.search(q)
        return {"results": results}
    except ImportError:
        return {"error": "Productivity connectors not available"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# UPDATER ENDPOINTS
# ============================================================================

def update_check_rpc(*args, **kwargs) -> Dict:
    """Check for updates from GitHub."""
    try:
        return check_for_updates()
    except Exception as e:
        return {"error": str(e)}


def update_apply_rpc(data=None, *args, **kwargs) -> Dict:
    """Apply available update."""
    try:
        return apply_update()
    except Exception as e:
        return {"error": str(e)}


def platform_info_rpc(*args, **kwargs) -> Dict:
    """Get platform and runtime info."""
    try:
        return platform_summary()
    except Exception as e:
        return {"error": str(e)}


def doctor_rpc(*args, **kwargs) -> Dict:
    """Run full system health diagnostics."""
    try:
        from src.api.doctor import run_diagnosis
        result = run_diagnosis()
        # Map backend status names to what the frontend Doctor.jsx expects
        status_map = {"healthy": "ok", "degraded": "warn", "unhealthy": "error"}
        result["status"] = status_map.get(result.get("status"), result.get("status"))
        return result
    except ImportError:
        logger.warning("Doctor module not available")
        return {"status": "error", "checks": [], "summary": "Doctor module not available"}
    except Exception as e:
        logger.error(f"Error in doctor_rpc: {e}", exc_info=True)
        return {"status": "error", "checks": [], "summary": str(e)}


# ============================================================================
# RPC ENDPOINT REGISTRY
# ============================================================================
# Each entry maps the RPC function name to the Python callable

RPC_ENDPOINTS = {
    # Chat (AI conversation)
    "chat": chat_send,
    
    # System
    "system.overview": system_overview,
    "system.health": system_health,
    "system.config": system_config,
    
    # Configuration (key management)
    "config.status": config_status,
    "config.save": config_save,
    "config.test": config_test,
    
    # Agents
    "agents.list": agents_list,
    "agents.get": agents_get,
    "agents.create": agents_create,
    "agents": agents_list,  # bare-name alias for generic IPC GET /api/agents
    
    # Messages
    "messages.list": messages_list,
    "messages.send": messages_send,
    
    # Skills
    "skills": skills_list,
    "skills.list": skills_list,
    "skills.reload": skills_reload,
    
    # Missions
    "missions.list": missions_list,
    "missions.get": missions_get,
    "missions": missions_list,  # bare-name alias for generic IPC GET /api/missions
    
    # Decisions
    "decisions.list": decisions_list,
    "decisions.get": decisions_get,
    "decisions": decisions_list,  # bare-name alias for generic IPC GET /api/decisions
    
    # Metrics
    "metrics.performance": metrics_performance,
    
    # Logs
    "logs.get": logs_get,
    
    # Approvals
    "approvals": approvals_list,
    "approvals.list": approvals_list,
    "approvals.summary.stats": approvals_summary_stats,
    "approvals.approve": approvals_approve_request,
    "approvals.reject": approvals_reject_request,
    "approvals.gap.approve": approvals_approve_gap,
    "approvals.gap.reject": approvals_reject_gap,
    
    # Notifications
    "notifications": notifications_list,
    "notifications.list": notifications_list,
    "notifications.mark_read": notifications_mark_read,
    "notifications.read-all": notifications_read_all,
    
    # Tasks (Phase 3.3)
    "tasks.create": tasks_create,
    "tasks.list": tasks_list,
    "tasks.get": tasks_get,
    "tasks.start": tasks_start,
    "tasks.update_progress": tasks_update_progress,
    "tasks.complete": tasks_complete,
    "tasks.fail": tasks_fail,
    "tasks.cancel": tasks_cancel,
    "tasks.pause": tasks_pause,
    "tasks.resume": tasks_resume,
    
    # Nova Execution (Full Stack)
    "nova.execute_task": execute_task,
    "nova.get_execution_status": get_execution_status,
    "nova.get_all_executions": get_all_executions,
    
    # Nova Coordinator (Integrated Pipeline - Phase 40 → 50 → Execute → PR → Push)
    "nova.execute_with_consensus": nova_execute_with_consensus,
    "nova.get_mission_status": nova_get_mission_status,
    "nova.list_recent_missions": nova_list_recent_missions,
    
    # Offline Support (Full Stack)
    "offline.queue_mission": offline_queue_mission,
    "offline.get_queue_status": offline_get_queue_status,
    "offline.get_pending_missions": offline_get_pending_missions,
    "offline.set_connectivity_status": offline_set_connectivity_status,
    "offline.clear_completed_missions": offline_clear_completed_missions,
    
    # Phase 51: Autonomous Loop
    "autonomous.execute": autonomous_execute,
    "autonomous.failure_summary": autonomous_failure_summary,
    "autonomous.failure_history": autonomous_failure_history,
    "autonomous.strategy_stats": autonomous_strategy_stats,
    "autonomous.database.performance": autonomous_database_performance,
    
    # Phase 51: Tool Synthesis
    "synthesized.list": synthesized_tools_list,
    "synthesized.run": synthesized_tools_run,
    
    # Settings (runtime config)
    "settings": settings_get,
    "settings.get": settings_get,
    "settings.update": settings_update,
    "settings.ollama-models": settings_ollama_models,
    
    # Scanner (host machine, repos, programs)
    "scan.host": scan_host_rpc,
    "scan.repo": scan_repo_rpc,
    "scan.programs": scan_programs_rpc,
    
    # Browser Automation (Playwright)
    "browser.status": browser_status_rpc,
    "browser.launch": browser_launch_rpc,
    "browser.close": browser_close_rpc,
    "browser.action": browser_action_rpc,
    
    # Integrations (Slack, Discord, Telegram)
    "integrations.status": integrations_status_rpc,
    "integrations.discord.start": lambda data=None, *a, **kw: integrations_action_rpc({"platform": "discord", "action": "start"}),
    "integrations.discord.stop": lambda data=None, *a, **kw: integrations_action_rpc({"platform": "discord", "action": "stop"}),
    "integrations.telegram.start": lambda data=None, *a, **kw: integrations_action_rpc({"platform": "telegram", "action": "start"}),
    "integrations.telegram.stop": lambda data=None, *a, **kw: integrations_action_rpc({"platform": "telegram", "action": "stop"}),
    
    # Productivity Connectors (Google Calendar, Jira, Notion)
    "productivity.status": productivity_status_rpc,
    "productivity.calendar.events": productivity_calendar_events_rpc,
    "productivity.jira.issues": productivity_jira_issues_rpc,
    "productivity.notion.search": productivity_notion_search_rpc,
    
    # Updates & Platform
    "update.check": update_check_rpc,
    "update.apply": update_apply_rpc,
    "platform": platform_info_rpc,
    
    # Projects / File Browser
    "projects": projects_list,
    "projects.list": projects_list,
    "projects.tree": projects_tree,
    "projects.file": projects_file,
    
    # Doctor (system diagnostics)
    "doctor": doctor_rpc,
}


def get_endpoint(name: str):
    """Get endpoint by name."""
    return RPC_ENDPOINTS.get(name)


def get_all_endpoints() -> Dict[str, str]:
    """Get list of all available endpoints."""
    return {name: func.__doc__ or "" for name, func in RPC_ENDPOINTS.items()}
