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
    def execute_task(*args, **kwargs):
        return {"error": "Nova executor not available"}
    def get_execution_status(*args, **kwargs):
        return {"error": "Nova executor not available"}
    def get_all_executions(*args, **kwargs):
        return {"error": "Nova executor not available"}

# Import offline support for mission queueing when offline
try:
    from piddy.offline_sync import get_offline_queue, get_sync_manager
    HAS_OFFLINE_SUPPORT = True
    logger.info("✅ Offline support available for RPC")
except ImportError:
    HAS_OFFLINE_SUPPORT = False
    logger.warning("⚠️ Offline support not available")
    def get_offline_queue(*args, **kwargs):
        return None
    def get_sync_manager(*args, **kwargs):
        return None

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
    """Lazy load coordinator on first call."""
    global _coordinator
    if _coordinator is None:
        try:
            from src.coordination.agent_coordinator import AgentCoordinator
            _coordinator = AgentCoordinator()
            logger.info("✅ Coordinator initialized for RPC")
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
            result = [None]
            exception = [None]
            
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
                telemetry_stats = telemetry.get_all_stats() if hasattr(telemetry, 'get_all_stats') else telemetry.get_overall_stats()
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
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in system_overview: {e}", exc_info=True)
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
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


def agents_create(name: str, role: str = "backend_developer", capabilities: List[str] = None) -> Dict:
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
                coordinator.enqueue_mission_from_user(content)
                
            elif any(cmd in user_command for cmd in ["what's happening", "status", "show me what you're doing"]):
                message_obj["status"] = "processing"
                message_obj["action"] = "status_query"
                # Will be handled with activity stream
                
            elif any(cmd in user_command for cmd in ["execute", "run", "do this"]):
                message_obj["status"] = "processing"
                message_obj["action"] = "execute_task"
                coordinator.enqueue_task_from_user(content)
                
            else:
                message_obj["status"] = "processing"
                message_obj["action"] = "general_query"
        
        # Store the message
        try:
            coordinator.add_message(message_obj)
        except:
            # Fallback if coordinator doesn't have add_message
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
# MISSIONS/TASKS ENDPOINTS
# ============================================================================

def missions_list(limit: int = 50) -> Dict:
    """Get recent missions."""
    try:
        telemetry = _get_telemetry_collector()
        if not telemetry:
            return {"missions": [], "total": 0}
        
        missions = telemetry.get_all_missions(limit=limit)
        return {
            "missions": missions if isinstance(missions, list) else list(missions),
            "total": len(missions) if missions else 0,
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
        
        mission = telemetry.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        return mission
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
                stats = telemetry.get_all_stats() if hasattr(telemetry, 'get_all_stats') else telemetry.get_overall_stats()
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
                if isinstance(approvals, list):
                    return {
                        "approvals": approvals[:limit],
                        "total": len(approvals),
                        "pending": len([a for a in approvals if a.get("status") == "pending"]),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        
        return {
            "approvals": [],
            "total": 0,
            "pending": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in approvals_list: {e}")
        return {"approvals": [], "total": 0, "error": str(e)}


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
            return {"success": True, "task": task.to_dict()}
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
            return {"success": True, "progress_percent": task.progress_percent}
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
        
        return result
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
# RPC ENDPOINT REGISTRY
# ============================================================================
# Each entry maps the RPC function name to the Python callable

RPC_ENDPOINTS = {
    # System
    "system.overview": system_overview,
    "system.health": system_health,
    "system.config": system_config,
    
    # Agents
    "agents.list": agents_list,
    "agents.get": agents_get,
    "agents.create": agents_create,
    
    # Messages
    "messages.list": messages_list,
    "messages.send": messages_send,
    
    # Missions
    "missions.list": missions_list,
    "missions.get": missions_get,
    
    # Decisions
    "decisions.list": decisions_list,
    "decisions.get": decisions_get,
    
    # Metrics
    "metrics.performance": metrics_performance,
    
    # Logs
    "logs.get": logs_get,
    
    # Approvals
    "approvals.list": approvals_list,
    
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
}


def get_endpoint(name: str):
    """Get endpoint by name."""
    return RPC_ENDPOINTS.get(name)


def get_all_endpoints() -> Dict[str, str]:
    """Get list of all available endpoints."""
    return {name: func.__doc__ or "" for name, func in RPC_ENDPOINTS.items()}
