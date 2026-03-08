"""Coordination module for Phase 4 - Multi-agent coordination system."""
from .agent_coordinator import (
import logging
    AgentCoordinator,
    get_coordinator,
    Agent,
    Task,
    CoordinationMessage,
    AgentRole,
    TaskPriority,
    TaskStatus,
logger = logging.getLogger(__name__)
)

__all__ = [
    "AgentCoordinator",
    "get_coordinator",
    "Agent",
    "Task",
    "CoordinationMessage",
    "AgentRole",
    "TaskPriority",
    "TaskStatus",
]
