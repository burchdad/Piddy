"""
Task Engine - Long-running Async Job Execution

Enables Piddy to execute long-running operations without blocking the UI.
Tasks can be:
- Launched (started in background)
- Monitored (progress tracked)
- Controlled (paused, resumed, cancelled)
- Orchestrated (multi-agent coordination)
"""

import logging
import uuid
import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import threading

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a long-running task"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = ""  # 'analysis', 'deployment', 'mission', 'repair', etc.
    status: str = field(default=TaskStatus.PENDING.value)
    progress_percent: int = 0
    total_steps: int = 0
    current_step: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_remaining_seconds: int = 0
    
    # Execution context
    agent_id: Optional[str] = None
    mission_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    
    # Results
    result: Any = None
    error: Optional[str] = None
    
    # Metadata
    priority: int = 1  # 1=low, 5=high
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "estimated_remaining_seconds": self.estimated_remaining_seconds,
            "agent_id": self.agent_id,
            "mission_id": self.mission_id,
            "parent_task_id": self.parent_task_id,
            "result": self.result,
            "error": self.error,
            "priority": self.priority,
            "tags": self.tags,
            "metadata": self.metadata
        }


class TaskExecutor:
    """Manages task execution"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: List[str] = []
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.lock = threading.Lock()
        
        logger.info("Task executor initialized")
    
    def create_task(self, name: str, task_type: str, **kwargs) -> Task:
        """Create a new task"""
        task = Task(
            name=name,
            type=task_type,
            **kwargs
        )
        
        with self.lock:
            self.tasks[task.id] = task
        
        logger.info(f"Task created: {task.id} ({name})")
        return task
    
    def start_task(self, task_id: str) -> bool:
        """Start a task"""
        with self.lock:
            if task_id not in self.tasks:
                logger.error(f"Task not found: {task_id}")
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.PENDING.value:
                logger.warning(f"Task {task_id} cannot be started (status: {task.status})")
                return False
            
            task.status = TaskStatus.RUNNING.value
            task.started_at = datetime.utcnow().isoformat()
            self.running_tasks.append(task_id)
        
        logger.info(f"Task started: {task_id}")
        return True
    
    def update_progress(self, task_id: str, current_step: int, total_steps: int, 
                       estimated_remaining: int = 0) -> bool:
        """Update task progress"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.current_step = current_step
            task.total_steps = total_steps
            task.progress_percent = int((current_step / max(total_steps, 1)) * 100)
            task.estimated_remaining_seconds = estimated_remaining
        
        return True
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark task as completed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED.value
            task.progress_percent = 100
            task.completed_at = datetime.utcnow().isoformat()
            task.result = result
            
            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)
            self.completed_tasks.append(task_id)
        
        logger.info(f"Task completed: {task_id}")
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED.value
            task.completed_at = datetime.utcnow().isoformat()
            task.error = error
            
            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)
            self.failed_tasks.append(task_id)
        
        logger.error(f"Task failed: {task_id} - {error}")
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a running task"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.RUNNING.value:
                return False
            
            task.status = TaskStatus.PAUSED.value
            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)
        
        logger.info(f"Task paused: {task_id}")
        return True
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.PAUSED.value:
                return False
            
            task.status = TaskStatus.RUNNING.value
            self.running_tasks.append(task_id)
        
        logger.info(f"Task resumed: {task_id}")
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
                return False
            
            task.status = TaskStatus.CANCELLED.value
            task.completed_at = datetime.utcnow().isoformat()
            
            if task_id in self.running_tasks:
                self.running_tasks.remove(task_id)
        
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_running_tasks(self) -> List[Task]:
        """Get all running tasks"""
        with self.lock:
            return [self.tasks[tid] for tid in self.running_tasks if tid in self.tasks]
    
    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """Get tasks by type"""
        with self.lock:
            return [task for task in self.tasks.values() if task.type == task_type]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        with self.lock:
            return {
                "total_tasks": len(self.tasks),
                "running": len(self.running_tasks),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
                "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING.value])
            }


# Singleton instance
_task_executor: Optional[TaskExecutor] = None


def get_task_executor() -> TaskExecutor:
    """Get or create task executor instance"""
    global _task_executor
    if _task_executor is None:
        _task_executor = TaskExecutor()
    return _task_executor


# ============================================================================
# BUILT-IN TASK TYPES
# ============================================================================

def create_analysis_task(name: str, **kwargs) -> Task:
    """Create a code analysis task"""
    executor = get_task_executor()
    return executor.create_task(name, "analysis", **kwargs)


def create_deployment_task(name: str, **kwargs) -> Task:
    """Create a deployment task"""
    executor = get_task_executor()
    return executor.create_task(name, "deployment", **kwargs)


def create_repair_task(name: str, **kwargs) -> Task:
    """Create a code repair/fix task"""
    executor = get_task_executor()
    return executor.create_task(name, "repair", **kwargs)


def create_mission_task(name: str, mission_id: str, **kwargs) -> Task:
    """Create a mission execution task"""
    executor = get_task_executor()
    return executor.create_task(name, "mission", mission_id=mission_id, **kwargs)


def create_orchestration_task(name: str, agent_ids: List[str], **kwargs) -> Task:
    """Create a multi-agent orchestration task"""
    executor = get_task_executor()
    task = executor.create_task(name, "orchestration", **kwargs)
    task.metadata["agents"] = agent_ids
    return task
