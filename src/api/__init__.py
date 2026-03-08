"""API routes module."""

from .agent_commands import router as agent_router
from .slack_commands import router as slack_router
import logging

logger = logging.getLogger(__name__)
__all__ = ["agent_router", "slack_router"]
