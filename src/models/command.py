"""Command models for agent communication."""

from pydantic import BaseModel
from typing import Any, Dict, Optional
from enum import Enum


class CommandType(str, Enum):
    """Types of commands Piddy can handle."""
    CODE_GENERATION = "code_generation"
    API_DESIGN = "api_design"
    DATABASE_SCHEMA = "database_schema"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    MIGRATION = "migration"
    CUSTOM = "custom"


class Command(BaseModel):
    """Command structure for agent communication."""
    command_type: CommandType
    description: str
    context: Dict[str, Any] = {}
    source: str = "api"  # "slack" or "api" or other agent
    priority: int = 5  # 1-10 scale
    metadata: Dict[str, Any] = {}


class CommandResponse(BaseModel):
    """Response structure for executed commands."""
    success: bool
    command_type: CommandType
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = {}
