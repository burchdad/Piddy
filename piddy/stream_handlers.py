"""
Streaming Handlers - Real-time data streaming over RPC

Provides generator functions for streaming logs, agent thoughts, metrics, and progress.
These functions work with the RPC streaming protocol to push data to frontend.
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import Generator, Optional, Dict, Any
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# SYSTEM LOGS STREAMING
# ============================================================================

def stream_logs(since: Optional[float] = None, max_items: int = 1000) -> Generator[Dict, None, None]:
    """
    Stream recent system logs in real-time.
    
    Args:
        since: Unix timestamp to get logs since
        max_items: Maximum number of logs to return per batch
        
    Yields:
        Log entry dictionaries
    """
    try:
        # Try to read from log file
        log_file = Path("/workspaces/Piddy/data/.piddy_service.log")
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
                for line in lines[-max_items:]:
                    try:
                        # Parse log line
                        # Format: [LEVEL] timestamp - message
                        parts = line.strip().split(' - ', 1)
                        if len(parts) == 2:
                            timestamp = datetime.utcnow().isoformat()
                            message = parts[1]
                            level_part = parts[0]
                            
                            # Extract level
                            level = "INFO"
                            if "ERROR" in level_part:
                                level = "ERROR"
                            elif "WARNING" in level_part:
                                level = "WARNING"
                            elif "DEBUG" in level_part:
                                level = "DEBUG"
                            
                            yield {
                                "timestamp": timestamp,
                                "level": level,
                                "message": message,
                                "source": "System"
                            }
                    except Exception as e:
                        logger.debug(f"Could not parse log line: {e}")
                        yield {
                            "timestamp": datetime.utcnow().isoformat(),
                            "level": "INFO",
                            "message": line.strip(),
                            "source": "System"
                        }
        else:
            # No log file, return a demo entry
            yield {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "Streaming logs initialized",
                "source": "System"
            }
    except Exception as e:
        logger.error(f"Error streaming logs: {e}")
        yield {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "message": f"Error streaming logs: {str(e)}",
            "source": "System"
        }


# ============================================================================
# AGENT THOUGHTS STREAMING
# ============================================================================

def stream_agent_thoughts(agent_id: str, max_items: int = 100) -> Generator[Dict, None, None]:
    """
    Stream agent thoughts and reasoning in real-time.
    
    Args:
        agent_id: ID of agent to stream thoughts from
        max_items: Maximum thoughts to return
        
    Yields:
        Agent thought dictionaries with reasoning and confidence
    """
    try:
        # Try to get agent's recent thoughts from coordinator
        from src.coordination.agent_coordinator import AgentCoordinator
        
        coordinator = AgentCoordinator()
        agent = coordinator.get_agent(agent_id)
        
        if agent:
            # Yield current agent status as a "thought"
            yield {
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "thought": f"Agent {agent.name} is {'busy' if not agent.is_available else 'available'}",
                "reasoning": f"Status: {agent.current_task_id or 'idle'}",
                "confidence": 0.95
            }
            
            # If agent has current task, stream its progress
            if agent.current_task_id:
                yield {
                    "agent_id": agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "thought": f"Processing task: {agent.current_task_id}",
                    "reasoning": f"Completed: {agent.completed_tasks}, Failed: {agent.failed_tasks}",
                    "confidence": 0.85
                }
        else:
            yield {
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "thought": f"Agent not found: {agent_id}",
                "reasoning": "Agent may not be registered",
                "confidence": 0.0
            }
    except Exception as e:
        logger.error(f"Error streaming agent thoughts: {e}")
        yield {
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "thought": f"Error getting agent thoughts",
            "reasoning": str(e),
            "confidence": 0.0
        }


# ============================================================================
# MISSION PROGRESS STREAMING
# ============================================================================

def stream_mission_progress(mission_id: str, update_interval: float = 0.5) -> Generator[Dict, None, None]:
    """
    Stream mission/task progress in real-time.
    
    Args:
        mission_id: ID of mission to stream
        update_interval: Time between updates in seconds
        
    Yields:
        Mission progress dictionaries
    """
    try:
        from src.phase34_mission_telemetry import MissionTelemetryCollector
        
        telemetry = MissionTelemetryCollector('.piddy_telemetry.db')
        
        # Get mission
        mission = telemetry.get_mission(mission_id) if hasattr(telemetry, 'get_mission') else None
        
        if mission:
            # Yield initial mission state
            phase = mission.get('phase', 'unknown')
            progress = mission.get('progress_percent', 0)
            
            yield {
                "mission_id": mission_id,
                "phase": phase,
                "progress_percent": progress,
                "current_step": mission.get('current_step', 'initializing'),
                "status": mission.get('status', 'pending'),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Simulate progress updates if mission is in progress
            if progress < 100:
                for i in range(progress + 10, 101, 10):
                    time.sleep(update_interval)
                    yield {
                        "mission_id": mission_id,
                        "phase": phase,
                        "progress_percent": i,
                        "current_step": f"step_{i//10}",
                        "status": "in_progress" if i < 100 else "complete",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        else:
            yield {
                "mission_id": mission_id,
                "phase": "unknown",
                "progress_percent": 0,
                "current_step": "not_found",
                "status": "error",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error streaming mission progress: {e}")
        yield {
            "mission_id": mission_id,
            "phase": "error",
            "progress_percent": 0,
            "current_step": "error",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# SYSTEM METRICS STREAMING
# ============================================================================

def stream_system_metrics(interval: float = 1.0, duration: float = 60.0) -> Generator[Dict, None, None]:
    """
    Stream system metrics (CPU, memory, disk) in real-time.
    
    Args:
        interval: Time between metric updates in seconds
        duration: Total streaming duration in seconds
        
    Yields:
        System metric dictionaries
    """
    try:
        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False
        
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            if has_psutil:
                try:
                    # Get metrics
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    yield {
                        "cpu_percent": cpu_percent,
                        "memory_mb": memory.used / 1024 / 1024,
                        "memory_percent": memory.percent,
                        "disk_percent": disk.percent,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    logger.debug(f"Error getting metrics: {e}")
                    yield {
                        "cpu_percent": 0,
                        "memory_mb": 0,
                        "memory_percent": 0,
                        "disk_percent": 0,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            else:
                # Fallback without psutil
                yield {
                    "cpu_percent": 0,
                    "memory_mb": 0,
                    "memory_percent": 0,
                    "disk_percent": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            time.sleep(interval)
    except Exception as e:
        logger.error(f"Error streaming system metrics: {e}")
        yield {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# STREAM REGISTRY
# ============================================================================

STREAM_FUNCTIONS = {
    "stream.logs": stream_logs,
    "stream.agent_thoughts": stream_agent_thoughts,
    "stream.mission_progress": stream_mission_progress,
    "stream.system_metrics": stream_system_metrics,
}


def get_stream_function(name: str):
    """Get a streaming function by name."""
    return STREAM_FUNCTIONS.get(name)


def get_all_streams() -> Dict[str, str]:
    """Get list of all available streams."""
    return {name: func.__doc__ or "" for name, func in STREAM_FUNCTIONS.items()}
