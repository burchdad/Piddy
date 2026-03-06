"""
Multi-Agent Framework
Base classes for agent coordination and communication

Supports:
- Phase 50+: Multi-agent orchestration
- Agent-to-agent communication
- Coordinated mission execution
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
from datetime import datetime


class AgentRole(Enum):
    """Types of agents in the system"""
    ANALYST = "analyst"              # Analyzes code changes
    PLANNER = "planner"              # Plans mission execution
    EXECUTOR = "executor"            # Executes missions
    VALIDATOR = "validator"          # Validates results
    COORDINATOR = "coordinator"      # Coordinates between agents
    OPTIMIZER = "optimizer"          # Optimizes solutions


class MessageType(Enum):
    """Types of messages between agents"""
    REQUEST = "request"              # Request to do something
    RESPONSE = "response"            # Response to request
    STATUS = "status"                # Status update
    ERROR = "error"                  # Error notification
    QUERY = "query"                  # Query for information
    BROADCAST = "broadcast"          # Broadcast to all agents


@dataclass
class AgentMessage:
    """Message for agent-to-agent communication"""
    
    sender_id: str                   # ID of sending agent
    recipient_id: str                # ID of recipient (or broadcast)
    message_type: MessageType        # Type of message
    payload: Dict                    # Message content
    
    # Metadata
    message_id: str = ""
    timestamp: str = ""
    correlation_id: Optional[str] = None  # Link to related messages
    priority: int = 5                # 1-10, higher = more urgent
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"{self.sender_id}_{datetime.utcnow().timestamp()}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type.value,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'correlation_id': self.correlation_id,
            'priority': self.priority,
        }


class Agent(ABC):
    """Base class for agents"""
    
    def __init__(self, agent_id: str, role: AgentRole):
        """Initialize agent"""
        self.agent_id = agent_id
        self.role = role
        self.inbox: asyncio.Queue = asyncio.Queue()
        self.outbox: asyncio.Queue = asyncio.Queue()
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.state: Dict = {}
        self.active = False
    
    def register_message_handler(self, message_type: MessageType, 
                                handler: Callable) -> None:
        """Register handler for message type"""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, recipient_id: str, message_type: MessageType,
                          payload: Dict, priority: int = 5) -> str:
        """Send message to another agent"""
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            payload=payload,
            priority=priority,
        )
        
        await self.outbox.put(message)
        return message.message_id
    
    async def broadcast_message(self, message_type: MessageType,
                               payload: Dict, priority: int = 5) -> str:
        """Broadcast message to all agents"""
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="broadcast",
            message_type=message_type,
            payload=payload,
            priority=priority,
        )
        
        await self.outbox.put(message)
        return message.message_id
    
    async def receive_message(self) -> Optional[AgentMessage]:
        """Receive next message from inbox"""
        try:
            return self.inbox.get_nowait()
        except asyncio.QueueEmpty:
            return None
    
    async def wait_for_message(self, timeout: int = 30) -> Optional[AgentMessage]:
        """Wait for message with timeout"""
        try:
            return await asyncio.wait_for(self.inbox.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
    
    @abstractmethod
    async def run(self) -> None:
        """Main agent loop - must be implemented by subclass"""
        pass
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle received message - must be implemented by subclass"""
        pass


class AnalystAgent(Agent):
    """Agent that analyzes code and changes"""
    
    def __init__(self, agent_id: str = "analyst-1"):
        super().__init__(agent_id, AgentRole.ANALYST)
        self.analysis_cache: Dict = {}
    
    async def run(self) -> None:
        """Main analyst loop"""
        self.active = True
        
        while self.active:
            message = await self.wait_for_message(timeout=30)
            if message:
                await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle analysis requests"""
        if message.message_type == MessageType.REQUEST:
            # Perform analysis
            request_type = message.payload.get('type')
            
            if request_type == 'analyze_changes':
                result = await self.analyze_changes(message.payload)
            elif request_type == 'assess_risk':
                result = await self.assess_risk(message.payload)
            else:
                result = {'error': f'Unknown request type: {request_type}'}
            
            # Send response back
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'original_request': message.message_id,
                    'result': result,
                },
                priority=message.priority
            )
    
    async def analyze_changes(self, payload: Dict) -> Dict:
        """Analyze code changes"""
        # This would integrate with Phase 38 LLM planning
        return {
            'files_affected': payload.get('file_count', 0),
            'complexity': 'medium',
            'test_impact': 'high',
        }
    
    async def assess_risk(self, payload: Dict) -> Dict:
        """Assess risk of changes"""
        return {
            'risk_level': 'medium',
            'confidence': 0.75,
            'mitigations': [],
        }


class PlannerAgent(Agent):
    """Agent that plans mission execution"""
    
    def __init__(self, agent_id: str = "planner-1"):
        super().__init__(agent_id, AgentRole.PLANNER)
        self.plans_cache: Dict = {}
    
    async def run(self) -> None:
        """Main planner loop"""
        self.active = True
        
        while self.active:
            message = await self.wait_for_message(timeout=30)
            if message:
                await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle planning requests"""
        if message.message_type == MessageType.REQUEST:
            request_type = message.payload.get('type')
            
            if request_type == 'create_plan':
                plan = await self.create_plan(message.payload)
            elif request_type == 'optimize_plan':
                plan = await self.optimize_plan(message.payload)
            else:
                plan = {'error': f'Unknown request type: {request_type}'}
            
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {'plan': plan},
                priority=message.priority
            )
    
    async def create_plan(self, payload: Dict) -> Dict:
        """Create execution plan for mission"""
        # This would integrate with Phase 38 LLM planning
        return {
            'steps': [
                {'action': 'analyze', 'duration': 60},
                {'action': 'execute', 'duration': 300},
                {'action': 'validate', 'duration': 60},
            ],
            'estimated_duration': 420,
        }
    
    async def optimize_plan(self, payload: Dict) -> Dict:
        """Optimize existing plan"""
        return {
            'optimized': True,
            'efficiency_gain': 0.15,
        }


class ExecutorAgent(Agent):
    """Agent that executes missions"""
    
    def __init__(self, agent_id: str = "executor-1"):
        super().__init__(agent_id, AgentRole.EXECUTOR)
        self.executing: Dict = {}
    
    async def run(self) -> None:
        """Main executor loop"""
        self.active = True
        
        while self.active:
            message = await self.wait_for_message(timeout=30)
            if message:
                await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle execution requests"""
        if message.message_type == MessageType.REQUEST:
            request_type = message.payload.get('type')
            
            if request_type == 'execute_mission':
                result = await self.execute_mission(message.payload)
            else:
                result = {'error': f'Unknown request type: {request_type}'}
            
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {'result': result},
                priority=message.priority
            )
    
    async def execute_mission(self, payload: Dict) -> Dict:
        """Execute a mission"""
        mission_id = payload.get('mission_id')
        
        return {
            'mission_id': mission_id,
            'status': 'completed',
            'success': True,
            'result': {},
        }


class ValidatorAgent(Agent):
    """Agent that validates execution results"""
    
    def __init__(self, agent_id: str = "validator-1"):
        super().__init__(agent_id, AgentRole.VALIDATOR)
    
    async def run(self) -> None:
        """Main validator loop"""
        self.active = True
        
        while self.active:
            message = await self.wait_for_message(timeout=30)
            if message:
                await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle validation requests"""
        if message.message_type == MessageType.REQUEST:
            result = await self.validate(message.payload)
            
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {'validation': result},
                priority=message.priority
            )
    
    async def validate(self, payload: Dict) -> Dict:
        """Validate mission results"""
        return {
            'valid': True,
            'checks_passed': 5,
            'checks_failed': 0,
        }


class AgentOrchestrator:
    """Orchestrates communication between agents"""
    
    def __init__(self):
        """Initialize orchestrator"""
        self.agents: Dict[str, Agent] = {}
        self.message_bus: asyncio.Queue = asyncio.Queue()
        self.running = False
    
    def register_agent(self, agent: Agent) -> None:
        """Register an agent"""
        self.agents[agent.agent_id] = agent
    
    async def route_message(self, message: AgentMessage) -> None:
        """Route message to recipient"""
        if message.recipient_id == "broadcast":
            # Broadcast to all agents
            for agent in self.agents.values():
                await agent.inbox.put(message)
        else:
            # Send to specific agent
            recipient = self.agents.get(message.recipient_id)
            if recipient:
                await recipient.inbox.put(message)
    
    async def start(self) -> None:
        """Start the orchestrator"""
        self.running = True
        
        # Start all agents
        agent_tasks = [agent.run() for agent in self.agents.values()]
        
        # Message routing loop
        try:
            await asyncio.gather(
                self._route_messages(),
                *agent_tasks,
                return_exceptions=True
            )
        finally:
            self.running = False
    
    async def _route_messages(self) -> None:
        """Main message routing loop"""
        while self.running:
            # Collect outgoing messages from all agents
            for agent in self.agents.values():
                try:
                    message = agent.outbox.get_nowait()
                    await self.route_message(message)
                except asyncio.QueueEmpty:
                    pass
            
            await asyncio.sleep(0.1)
    
    async def stop(self) -> None:
        """Stop the orchestrator"""
        self.running = False
        
        for agent in self.agents.values():
            agent.active = False
    
    async def send_request(self, sender_id: str, recipient_id: str,
                          request_type: str, payload: Dict) -> AgentMessage:
        """Send request to an agent"""
        message = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.REQUEST,
            payload={**payload, 'type': request_type},
        )
        
        await self.route_message(message)
        return message
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return [
            {
                'agent_id': agent.agent_id,
                'role': agent.role.value,
                'active': agent.active,
            }
            for agent in self.agents.values()
        ]
