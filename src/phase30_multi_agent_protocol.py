"""
Phase 30: Multi-Agent Protocol

Enable agents to collaborate and coordinate:
- Agent registration and discovery
- Capability-based service model
- Request/response protocol
- Async communication
- Event-driven coordination
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Coroutine
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Types of capabilities agents can provide"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    SECURITY_SCAN = "security_scan"
    CODE_ANALYSIS = "code_analysis"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    COMPLIANCE_CHECK = "compliance_check"
    RESOURCE_OPTIMIZATION = "resource_optimization"


class RequestStatus(Enum):
    """Status of a request"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentCapabilityDef:
    """Definition of an agent's capability"""
    capability: AgentCapability
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    async_handler: Optional[Callable] = None


@dataclass
class AgentRequest:
    """Request sent to an agent"""
    request_id: str
    source_agent: str
    target_agent: str
    capability: AgentCapability
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    deadline_seconds: int = 300
    priority: int = 5  # 1-10


@dataclass
class AgentResponse:
    """Response from an agent"""
    response_id: str
    request_id: str
    source_agent: str
    target_agent: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    duration_ms: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            'response_id': self.response_id,
            'request_id': self.request_id,
            'source_agent': self.source_agent,
            'target_agent': self.target_agent,
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'duration_ms': self.duration_ms
        }


class Agent:
    """Base autonomous agent with collaboration support"""

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities: Dict[AgentCapability, AgentCapabilityDef] = {}
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.responses: Dict[str, AgentResponse] = {}
        self.registry: Optional['AgentRegistry'] = None

    def register_capability(
        self,
        capability: AgentCapability,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        handler: Callable
    ):
        """Register a capability this agent can perform"""
        self.capabilities[capability] = AgentCapabilityDef(
            capability=capability,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            async_handler=handler
        )
        logger.info(f"Agent {self.agent_name} registered capability: {capability.value}")

    async def request_capability(
        self,
        target_agent_id: str,
        capability: AgentCapability,
        data: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Request another agent to perform a capability"""

        if not self.registry:
            return None

        # Create request
        request = AgentRequest(
            request_id=str(uuid.uuid4())[:8],
            source_agent=self.agent_id,
            target_agent=target_agent_id,
            capability=capability,
            data=data
        )

        # Route through registry
        response = await self.registry.route_request(request)
        return response

    async def handle_request(self, request: AgentRequest) -> AgentResponse:
        """Handle incoming request"""
        start_time = datetime.now()

        if request.capability not in self.capabilities:
            return AgentResponse(
                response_id=str(uuid.uuid4())[:8],
                request_id=request.request_id,
                source_agent=request.source_agent,
                target_agent=self.agent_id,
                success=False,
                data={},
                error=f"Capability {request.capability.value} not supported",
                duration_ms=0
            )

        try:
            # Execute handler
            capability_def = self.capabilities[request.capability]
            if callable(capability_def.async_handler):
                result = await capability_def.async_handler(request.data)
            else:
                result = {"error": "No handler"}

            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            return AgentResponse(
                response_id=str(uuid.uuid4())[:8],
                request_id=request.request_id,
                source_agent=request.source_agent,
                target_agent=self.agent_id,
                success=True,
                data=result,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentResponse(
                response_id=str(uuid.uuid4())[:8],
                request_id=request.request_id,
                source_agent=request.source_agent,
                target_agent=self.agent_id,
                success=False,
                data={},
                error=str(e),
                duration_ms=duration_ms
            )

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get list of this agent's capabilities"""
        return [
            {
                'capability': cap.value,
                'description': cap_def.description,
                'input_schema': cap_def.input_schema,
                'output_schema': cap_def.output_schema
            }
            for cap, cap_def in self.capabilities.items()
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'capabilities_count': len(self.capabilities),
            'capabilities': [c.value for c in self.capabilities.keys()],
            'responses_cached': len(self.responses),
            'connected': self.registry is not None
        }


class AgentRegistry:
    """Central registry for agent coordination"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.request_history: List[AgentRequest] = []
        self.response_history: List[AgentResponse] = []

    def register_agent(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        agent.registry = self
        logger.info(f"Registered agent: {agent.agent_name}")

    def deregister_agent(self, agent_id: str):
        """Deregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Deregistered agent: {agent_id}")

    async def route_request(self, request: AgentRequest) -> Optional[AgentResponse]:
        """Route request to target agent"""
        if request.target_agent not in self.agents:
            logger.warning(f"Target agent not found: {request.target_agent}")
            return None

        target_agent = self.agents[request.target_agent]
        response = await target_agent.handle_request(request)

        # Record in history
        self.request_history.append(request)
        self.response_history.append(response)

        return response

    def get_agent_by_capability(self, capability: AgentCapability) -> Optional[Agent]:
        """Find an agent that supports a capability"""
        for agent in self.agents.values():
            if capability in agent.capabilities:
                return agent
        return None

    def get_agents_by_capability(self, capability: AgentCapability) -> List[Agent]:
        """Find all agents that support a capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]

    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status"""
        return {
            'total_agents': len(self.agents),
            'agents': [
                {
                    'agent_id': agent.agent_id,
                    'agent_name': agent.agent_name,
                    'capabilities': len(agent.capabilities)
                }
                for agent in self.agents.values()
            ],
            'total_requests': len(self.request_history),
            'total_responses': len(self.response_history)
        }

    def get_agent_directory(self) -> List[Dict[str, Any]]:
        """Get directory of all agents and capabilities"""
        return [
            {
                'agent_id': agent.agent_id,
                'agent_name': agent.agent_name,
                'capabilities': agent.get_capabilities()
            }
            for agent in self.agents.values()
        ]


class MultiAgentOrchestrator:
    """Orchestrate complex tasks across multiple agents"""

    def __init__(self, registry: AgentRegistry, coordinator_agent: Agent):
        self.registry = registry
        self.coordinator = coordinator_agent

    async def execute_cooperative_task(
        self,
        task_description: str,
        initial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a task requiring multiple agents:
        1. Coordinator receives task
        2. Breaks into sub-tasks
        3. Routes to specialized agents
        4. Aggregates results
        """

        logger.info(f"Executing cooperative task: {task_description}")

        workflow = {
            'task': task_description,
            'steps': [],
            'results': {},
            'success': True
        }

        # Step 1: Code generation
        code_gen_agent = self.registry.get_agent_by_capability(AgentCapability.CODE_GENERATION)
        if code_gen_agent:
            response = await self.coordinator.request_capability(
                code_gen_agent.agent_id,
                AgentCapability.CODE_GENERATION,
                initial_data
            )
            if response:
                workflow['results']['generated_code'] = response.data
                workflow['steps'].append({
                    'step': 'code_generation',
                    'success': response.success,
                    'duration_ms': response.duration_ms
                })

        # Step 2: Security scan
        security_agent = self.registry.get_agent_by_capability(AgentCapability.SECURITY_SCAN)
        if security_agent:
            scan_data = workflow['results'].get('generated_code', {})
            response = await self.coordinator.request_capability(
                security_agent.agent_id,
                AgentCapability.SECURITY_SCAN,
                scan_data
            )
            if response:
                workflow['results']['security_scan'] = response.data
                workflow['steps'].append({
                    'step': 'security_scan',
                    'success': response.success,
                    'duration_ms': response.duration_ms
                })

        # Step 3: Code review
        review_agent = self.registry.get_agent_by_capability(AgentCapability.CODE_REVIEW)
        if review_agent:
            review_data = workflow['results'].get('generated_code', {})
            response = await self.coordinator.request_capability(
                review_agent.agent_id,
                AgentCapability.CODE_REVIEW,
                review_data
            )
            if response:
                workflow['results']['code_review'] = response.data
                workflow['steps'].append({
                    'step': 'code_review',
                    'success': response.success,
                    'duration_ms': response.duration_ms
                })

        workflow['success'] = all(step['success'] for step in workflow['steps'])
        return workflow


# Demo agents

async def demo_code_generation(data: Dict) -> Dict:
    """Demo code generation handler"""
    return {'code': '# Generated code', 'lines': 10}


async def demo_security_scan(data: Dict) -> Dict:
    """Demo security scan handler"""
    return {'vulnerabilities': 0, 'score': 100}


async def demo_code_review(data: Dict) -> Dict:
    """Demo code review handler"""
    return {'approved': True, 'issues': []}


async def demo_multi_agent():
    """Demo multi-agent collaboration"""
    # Create registry
    registry = AgentRegistry()

    # Create agents
    piddy = Agent("piddy-1", "Piddy")
    quality_ai = Agent("quality-1", "QualityAssuranceAI")
    security_ai = Agent("security-1", "SecurityAuditAI")

    # Register capabilities
    piddy.register_capability(
        AgentCapability.CODE_GENERATION,
        "Generate code from specifications",
        {"spec": "string"},
        {"code": "string", "lines": "number"},
        demo_code_generation
    )

    security_ai.register_capability(
        AgentCapability.SECURITY_SCAN,
        "Scan code for security issues",
        {"code": "string"},
        {"vulnerabilities": "number", "score": "number"},
        demo_security_scan
    )

    quality_ai.register_capability(
        AgentCapability.CODE_REVIEW,
        "Review code quality",
        {"code": "string"},
        {"approved": "boolean", "issues": "array"},
        demo_code_review
    )

    # Register with registry
    registry.register_agent(piddy)
    registry.register_agent(security_ai)
    registry.register_agent(quality_ai)

    # Create orchestrator
    orchestrator = MultiAgentOrchestrator(registry, piddy)

    # Execute cooperative task
    result = await orchestrator.execute_cooperative_task(
        "Generate and validate JWT auth endpoint",
        {"spec": "JWT authentication endpoint"}
    )

    logger.info("\nPhase 30: Multi-Agent Protocol - Demo")
    logger.info("=" * 60)
    logger.info(f"Task: {result['task']}")
    logger.info(f"Steps completed: {len(result['steps'])}")
    logger.info(f"Overall success: {result['success']}")
    logger.info("\nRegistry status:")
    logger.info(json.dumps(registry.get_registry_status(), indent=2))


if __name__ == "__main__":
    asyncio.run(demo_multi_agent())
