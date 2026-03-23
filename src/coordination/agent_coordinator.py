"""
Multi-agent coordination system for Phase 4.
Enables communication and task distribution between multiple AI agents.
"""
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent role classification."""
    BACKEND_DEVELOPER = "backend_developer"
    CODE_REVIEWER = "code_reviewer"
    ARCHITECT = "architect"
    SECURITY_SPECIALIST = "security_specialist"
    DEVOPS_ENGINEER = "devops_engineer"
    DATA_ENGINEER = "data_engineer"
    COORDINATOR = "coordinator"
    PERFORMANCE_ANALYST = "performance_analyst"
    TECH_DEBT_HUNTER = "tech_debt_hunter"
    API_COMPATIBILITY = "api_compatibility"
    DATABASE_MIGRATION = "database_migration"
    ARCHITECTURE_REVIEWER = "architecture_reviewer"
    COST_OPTIMIZER = "cost_optimizer"
    FRONTEND_DEVELOPER = "frontend_developer"
    DOCUMENTATION = "documentation"
    SECURITY_TOOLING = "security_tooling"
    SECURITY_MONITORING = "security_monitoring"
    LOAD_TESTING = "load_testing"
    DATA_SECURITY = "data_security"
    KNOWLEDGE_MONITOR = "knowledge_monitor"
    TASK_AUTOMATION = "task_automation"


class TaskPriority(int, Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(str, Enum):
    """Task status values."""
    CREATED = "created"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Agent:
    """Agent definition for multi-agent coordination."""
    id: str
    name: str
    role: AgentRole
    capabilities: List[str]
    is_available: bool = True
    current_task_id: Optional[str] = None
    completed_tasks: int = 0
    failed_tasks: int = 0
    created_at: str = None
    last_activity: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_activity is None:
            self.last_activity = datetime.now().isoformat()


@dataclass
class Task:
    """Task for multi-agent execution."""
    id: str
    type: str
    description: str
    priority: TaskPriority
    assigned_agent_id: Optional[str] = None
    required_role: Optional[AgentRole] = None
    required_capabilities: List[str] = None
    metadata: Dict[str, Any] = None
    result: Optional[Any] = None
    status: TaskStatus = TaskStatus.CREATED
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.required_capabilities is None:
            self.required_capabilities = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CoordinationMessage:
    """Message for inter-agent communication."""
    id: str
    from_agent_id: str
    to_agent_id: str
    message_type: str  # 'request', 'response', 'status', 'alert'
    content: Dict[str, Any]
    created_at: str = None
    read_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AgentCoordinator:
    """
    Coordinates multiple AI agents working on backend development tasks.
    Handles task distribution, communication, and result aggregation.
    """

    def __init__(self):
        """Initialize coordinator."""
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: List[CoordinationMessage] = []
        self.task_queue: List[str] = []  # Task IDs in order
        self.completed_workflows: List[Dict] = []
        logger.info("✅ Agent Coordinator initialized")

    def register_agent(
        self,
        name: str,
        role: AgentRole,
        capabilities: List[str],
    ) -> Agent:
        """
        Register a new agent with the coordinator.

        Args:
            name: Human-readable agent name
            role: Agent's primary role
            capabilities: List of capabilities/skills

        Returns:
            Registered Agent object
        """
        agent_id = str(uuid.uuid4())[:8]
        agent = Agent(
            id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities,
        )
        self.agents[agent_id] = agent
        logger.info(f"✅ Agent registered: {name} ({role.value}) - {agent_id}")
        return agent

    def submit_task(
        self,
        task_type: str,
        description: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        required_role: Optional[AgentRole] = None,
        required_capabilities: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> Task:
        """
        Submit a new task for execution by agents.

        Args:
            task_type: Type of task
            description: Task description
            priority: Task priority
            required_role: Required agent role
            required_capabilities: Required capabilities
            metadata: Additional metadata

        Returns:
            Created Task object
        """
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            type=task_type,
            description=description,
            priority=priority,
            required_role=required_role,
            required_capabilities=required_capabilities or [],
            metadata=metadata or {},
        )

        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        logger.info(f"📋 Task submitted: {task_type} - {task_id}")

        return task

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Assign a task to a specific agent.

        Args:
            task_id: Task ID
            agent_id: Agent ID to assign to

        Returns:
            True if assignment successful
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return False

        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return False

        task = self.tasks[task_id]
        agent = self.agents[agent_id]

        # Check requirements
        if task.required_role and agent.role != task.required_role:
            logger.warning(f"Agent role mismatch for task {task_id}")
            return False

        if task.required_capabilities:
            missing = set(task.required_capabilities) - set(agent.capabilities)
            if missing:
                logger.warning(f"Agent missing capabilities: {missing}")
                return False

        # Assign task
        task.assigned_agent_id = agent_id
        task.status = TaskStatus.ASSIGNED
        agent.current_task_id = task_id
        agent.last_activity = datetime.now().isoformat()

        logger.info(f"✅ Task {task_id} assigned to {agent.name}")
        return True

    def find_suitable_agent(self, task: Task) -> Optional[Agent]:
        """
        Find a suitable available agent for a task.

        Args:
            task: Task to find agent for

        Returns:
            Suitable Agent or None
        """
        suitable_agents = []

        for agent_id, agent in self.agents.items():
            # Must be available
            if not agent.is_available:
                continue

            # Check role requirement
            if task.required_role and agent.role != task.required_role:
                continue

            # Check capabilities
            if task.required_capabilities:
                if not set(task.required_capabilities).issubset(set(agent.capabilities)):
                    continue

            suitable_agents.append(agent)

        # Return agent with lowest current load
        if suitable_agents:
            return min(suitable_agents, key=lambda a: a.completed_tasks - a.failed_tasks)

        return None

    def auto_assign_tasks(self) -> int:
        """
        Automatically assign queued tasks to suitable agents.

        Returns:
            Number of tasks assigned
        """
        assigned = 0

        for task_id in self.task_queue[:]:
            task = self.tasks[task_id]

            if task.status != TaskStatus.QUEUED and task.status != TaskStatus.CREATED:
                continue

            agent = self.find_suitable_agent(task)
            if agent:
                self.assign_task(task_id, agent.id)
                assigned += 1

        return assigned

    def start_task(self, task_id: str) -> bool:
        """Mark task as in progress."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()

        if task.assigned_agent_id:
            agent = self.agents[task.assigned_agent_id]
            agent.is_available = False

        logger.info(f"▶️ Task started: {task_id}")
        return True

    def complete_task(
        self,
        task_id: str,
        result: Any,
        agent_feedback: Optional[str] = None,
    ) -> bool:
        """
        Mark task as completed with result.

        Args:
            task_id: Task ID
            result: Task result
            agent_feedback: Agent's feedback on task

        Returns:
            True if successful
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result

        if task.assigned_agent_id:
            agent = self.agents[task.assigned_agent_id]
            agent.is_available = True
            agent.completed_tasks += 1
            agent.current_task_id = None
            agent.last_activity = datetime.now().isoformat()

        logger.info(f"✅ Task completed: {task_id}")
        return True

    def fail_task(self, task_id: str, error: str) -> bool:
        """
        Mark task as failed.

        Args:
            task_id: Task ID
            error: Error message

        Returns:
            True if successful
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now().isoformat()
        task.error = error

        if task.assigned_agent_id:
            agent = self.agents[task.assigned_agent_id]
            agent.is_available = True
            agent.failed_tasks += 1
            agent.current_task_id = None

        logger.error(f"❌ Task failed: {task_id} - {error}")
        return True

    def send_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message_type: str,
        content: Dict[str, Any],
    ) -> CoordinationMessage:
        """
        Send a message between agents.

        Args:
            from_agent_id: Sender agent ID
            to_agent_id: Receiver agent ID
            message_type: Type of message
            content: Message content

        Returns:
            Created CoordinationMessage
        """
        msg_id = str(uuid.uuid4())[:8]
        message = CoordinationMessage(
            id=msg_id,
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            message_type=message_type,
            content=content,
        )

        self.messages.append(message)
        logger.debug(f"📨 Message sent: {from_agent_id} -> {to_agent_id}")
        return message

    def get_agent_messages(self, agent_id: str, unread_only: bool = False) -> List[CoordinationMessage]:
        """Get messages for an agent."""
        messages = [m for m in self.messages if m.to_agent_id == agent_id]

        if unread_only:
            messages = [m for m in messages if m.read_at is None]

        return messages

    def mark_message_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        for msg in self.messages:
            if msg.id == message_id:
                msg.read_at = datetime.now().isoformat()
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status and statistics."""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        in_progress = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])

        available_agents = len([a for a in self.agents.values() if a.is_available])

        return {
            "agents": {
                "total": len(self.agents),
                "available": available_agents,
                "by_role": self._agents_by_role(),
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "in_progress": in_progress,
                "queued": len(self.task_queue),
            },
            "messages": {
                "total": len(self.messages),
                "unread": len([m for m in self.messages if m.read_at is None]),
            },
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        }

    def _agents_by_role(self) -> Dict[str, int]:
        """Get agents grouped by role."""
        by_role = {}
        for agent in self.agents.values():
            role = agent.role.value
            by_role[role] = by_role.get(role, 0) + 1
        return by_role

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for an agent."""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role.value,
            "is_available": agent.is_available,
            "completed_tasks": agent.completed_tasks,
            "failed_tasks": agent.failed_tasks,
            "success_rate": (
                agent.completed_tasks / (agent.completed_tasks + agent.failed_tasks) * 100
                if (agent.completed_tasks + agent.failed_tasks) > 0
                else 0
            ),
            "created_at": agent.created_at,
            "last_activity": agent.last_activity,
        }

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of completed workflows."""
        if not self.completed_workflows:
            return {"count": 0, "workflows": []}

        return {
            "count": len(self.completed_workflows),
            "workflows": self.completed_workflows[-10:],  # Last 10 workflows
        }

    def get_stats(self) -> Dict[str, Any]:
        """Alias for get_status() - for backward compatibility."""
        return self.get_status()

    def get_all_agents(self) -> List[Agent]:
        """Get all registered agents."""
        return list(self.agents.values())

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID."""
        return self.agents.get(agent_id)

    def get_recent_messages(self, limit: int = 50) -> List[CoordinationMessage]:
        """Get recent messages (most recent first)."""
        sorted_messages = sorted(self.messages, key=lambda m: m.created_at, reverse=True)
        return sorted_messages[:limit]


# Global coordinator instance
_coordinator_instance: Optional[AgentCoordinator] = None


def get_coordinator() -> AgentCoordinator:
    """Get or create global agent coordinator instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance
