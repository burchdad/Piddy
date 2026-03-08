"""Task models for tracking work."""

from pydantic import BaseModel
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime
import logging


logger = logging.getLogger(__name__)
class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Task(BaseModel):
    """Task representation for Piddy."""
    task_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
