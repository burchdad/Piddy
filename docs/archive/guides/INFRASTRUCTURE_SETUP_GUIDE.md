# Infrastructure Setup: Prepare for Phases 39-50+

**Date**: March 6, 2026  
**Purpose**: Establish foundation for next-generation features  
**Timeline**: 2-4 weeks implementation  

## Overview

While Phases 39-42 will be implemented in future quarters, certain infrastructure pieces should be built now to:
1. De-risk future phases
2. Reduce time-to-market for Phase 39+
3. Provide foundation for multi-agent system
4. Enable parallel development

---

## 1. Graph Store Infrastructure

### Purpose
Store and query dependency graphs for:
- Phase 39 (visualization)
- Phase 41 (multi-repo)
- Phase 50+ (multi-agent reasoning)

### Implementation Options

#### Option A: NetworkX + SQLite (Recommended for MVP)
```python
# src/infrastructure/graph_store.py

from typing import Dict, List, Set, Tuple
import networkx as nx
import sqlite3
from dataclasses import dataclass
import json

@dataclass
class GraphNode:
    id: str
    type: str              # "function", "module", "service", "file"
    metadata: Dict        # name, file, line_number, etc.

@dataclass
class GraphEdge:
    source: str
    target: str
    type: str             # "calls", "imports", "depends_on", "uses_api"
    metadata: Dict        # weight, confidence, etc.

class DependencyGraphStore:
    """Store and query dependency graphs"""
    
    def __init__(self, db_path: str = "piddy_graphs.db"):
        self.db_path = db_path
        self.graphs: Dict[str, nx.DiGraph] = {}
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Nodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_nodes (
                graph_id TEXT,
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Edges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS graph_edges (
                graph_id TEXT,
                source_id TEXT,
                target_id TEXT,
                edge_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_graph(self, graph_id: str, nodes: List[GraphNode],
                    edges: List[GraphEdge]):
        """Create new graph"""
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node.id, **node.metadata)
        
        # Add edges
        for edge in edges:
            G.add_edge(edge.source, edge.target, 
                      type=edge.type, **edge.metadata)
        
        self.graphs[graph_id] = G
        self._persist_graph(graph_id, nodes, edges)
    
    def get_dependencies(self, node_id: str) -> Set[str]:
        """Get all dependencies of a node"""
        # Find which nodes this depends on
        pass
    
    def get_dependents(self, node_id: str) -> Set[str]:
        """Get all nodes that depend on this"""
        # Find which nodes depend on this
        pass
    
    def get_impact_radius(self, node_id: str) -> int:
        """Calculate how far changes propagate"""
        # Use NetworkX to find longest path
        pass
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies for Phase 41"""
        pass
```

#### Option B: Neo4j (For high-scale systems)
```
Neo4j provides:
- More efficient for complex queries
- Better for visualization
- APOC procedures for graph algorithms
- Web UI for exploration

Setup:
  docker run -d -p 7474:7474 -p 7687:7687 neo4j
  pip install neo4j
```

### Integration Points
- Phase 32 builds graphs
- Phase 34 stores usage data
- Phase 39 visualizes graphs
- Phase 41 queries for multi-repo
- Phase 50+ uses for reasoning

---

## 2. Mission Configuration Framework

### Purpose
Standardize mission definition and metadata for:
- Phase 40 (simulation config)
- Phase 42 (nightly missions)
- Phase 50+ (agent pipelines)

### Implementation

```python
# src/infrastructure/mission_config.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class MissionType(Enum):
    CLEANUP = "cleanup"
    REFACTOR = "refactor"
    COVERAGE = "coverage_improvement"
    OPTIMIZATION = "optimization"
    TYPE_IMPROVEMENT = "type_improvement"
    CUSTOM = "custom"

class RiskTolerance(Enum):
    LOW = "low"              # Conservative
    MEDIUM = "medium"        # Balanced
    HIGH = "high"            # Aggressive

@dataclass
class MissionConfig:
    """Standardized mission configuration"""
    name: str                          # Unique mission name
    type: MissionType                  # Mission type
    description: str                   # What it does
    priority: int                      # Execution priority (1-10)
    risk_tolerance: RiskTolerance     # Risk level
    approval_required: bool            # Needs human approval?
    auto_merge: bool = False           # Auto-merge PR?
    max_changes: Optional[int] = None  # Max files to change
    max_time: int = 300                # Max execution time (sec)
    
    # Phase dependencies
    dependencies: List[str] = field(default_factory=list)  # Other missions
    
    # Targeting
    target_modules: List[str] = field(default_factory=list)
    exclude_modules: List[str] = field(default_factory=list)
    
    # Constraints
    min_confidence: float = 0.7        # Don't execute if below this
    retry_on_failure: bool = True
    max_retries: int = 2
    
    # Metrics
    target_metrics: Dict = field(default_factory=dict)  # Coverage, etc.
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    owner: str = "system"
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'priority': self.priority,
            'risk_tolerance': self.risk_tolerance.value,
            'approval_required': self.approval_required,
            'auto_merge': self.auto_merge,
            'max_changes': self.max_changes,
            'dependencies': self.dependencies,
            'target_metrics': self.target_metrics,
            'tags': self.tags,
        }

class MissionConfigManager:
    """Manages mission configurations"""
    
    def __init__(self, config_dir: str = "config/missions"):
        self.config_dir = config_dir
        self.configs: Dict[str, MissionConfig] = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load configurations from YAML files"""
        # Load from config/missions/*.yaml
        pass
    
    def get_config(self, mission_type: str) -> MissionConfig:
        """Get configuration for mission type"""
        return self.configs.get(mission_type)
    
    def validate_config(self, config: MissionConfig) -> bool:
        """Validate mission configuration"""
        # Check dependencies exist
        # Check metrics are valid
        # Check phases are reachable
        pass
```

### Configuration Files

```yaml
# config/missions/cleanup_dead_code.yaml
name: cleanup_dead_code
type: cleanup
description: "Remove unreachable and unused code"
priority: 3
risk_tolerance: low
approval_required: false
auto_merge: true
max_changes: 50
tags: ["code quality", "cleanup"]
target_metrics:
  files_removed_min: 5
  functions_removed_min: 10

# config/missions/improve_coverage.yaml
name: improve_coverage
type: coverage_improvement
description: "Add tests for uncovered code"
priority: 4
risk_tolerance: low
approval_required: false
auto_merge: true
max_changes: 20
target_metrics:
  coverage_increase_min: 1.0  # percent

# config/missions/refactor_complex_functions.yaml
name: refactor_complex_functions
type: refactor
description: "Simplify functions with high complexity"
priority: 5
risk_tolerance: medium
approval_required: true        # Needs review!
auto_merge: false
max_changes: 15
target_modules:
  - src
```

---

## 3. Approval & Notification System

### Purpose
Request approvals and notify for:
- Phase 40 (high-risk missions)
- Phase 42 (auto-merge decisions)

### Implementation

```python
# src/infrastructure/approval_system.py

from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum
import asyncio

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class ApprovalRequest:
    mission_id: str
    mission_type: str
    prediction: Dict       # What will happen
    confidence: float      # How confident
    risk_level: str        # Risk assessment
    requires_approval: bool
    expires_in: int = 3600 # seconds

class ApprovalManager:
    """Manage approvals for high-risk missions"""
    
    def __init__(self):
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.notification_handlers = []
    
    async def request_approval(self, request: ApprovalRequest) -> bool:
        """Request approval from humans"""
        
        # Store request
        self.pending_approvals[request.mission_id] = request
        
        # Notify humans
        await self._notify_approvers(request)
        
        # Wait for response (with timeout)
        approval = await asyncio.wait_for(
            self._wait_for_approval(request.mission_id),
            timeout=request.expires_in
        )
        
        return approval
    
    async def _notify_approvers(self, request: ApprovalRequest):
        """Notify approvers via all channels"""
        for handler in self.notification_handlers:
            await handler.notify(request)
    
    async def _wait_for_approval(self, mission_id: str) -> bool:
        """Wait for approval from queue"""
        while True:
            await asyncio.sleep(1)
            # Check if approved/rejected
            if self.is_approved(mission_id):
                return True
            if self.is_rejected(mission_id):
                return False

# Notification handlers
class SlackNotificationHandler:
    """Send approval requests to Slack"""
    
    async def notify(self, request: ApprovalRequest):
        # Send to Slack channel
        # Include prediction, risk, confidence
        pass

class EmailNotificationHandler:
    """Send approval requests via email"""
    
    async def notify(self, request: ApprovalRequest):
        # Send to email list
        pass

class WebDashboardHandler:
    """Show pending approvals on web dashboard"""
    
    async def notify(self, request: ApprovalRequest):
        # Add to web queue
        pass
```

---

## 4. Mission Scheduler

### Purpose
Schedule missions for:
- Phase 42 (nightly automation)
- Future: complex execution plans

### Implementation

```python
# src/infrastructure/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Callable, Dict
from dataclasses import dataclass
import json

@dataclass
class ScheduledMission:
    mission_type: str
    schedule: str              # cron-like: "0 3 * * *"
    timezone: str = "UTC"
    enabled: bool = True
    metadata: Dict = None

class MissionScheduler:
    """Schedule missions for future execution"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.missions: Dict[str, ScheduledMission] = {}
    
    def schedule_mission(self, scheduled_mission: ScheduledMission,
                        callback: Callable):
        """Schedule a mission to run repeatedly"""
        
        job = self.scheduler.add_job(
            callback,
            trigger='cron',
            hour=3, minute=0,  # 3 AM
            timezone=scheduled_mission.timezone,
            args=[scheduled_mission.mission_type]
        )
        
        self.missions[scheduled_mission.mission_type] = scheduled_mission
    
    def load_schedule_config(self, config_file: str):
        """Load schedule from YAML"""
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        for mission_config in config.get('missions', []):
            scheduled = ScheduledMission(**mission_config)
            self.schedule_mission(scheduled, self._execute_mission)
    
    async def _execute_mission(self, mission_type: str):
        """Execute scheduled mission"""
        logger.info(f"Executing scheduled mission: {mission_type}")
        # Call system.execute_intelligent_mission()
        pass
```

### Schedule Configuration

```yaml
# config/schedule.yaml
continuous_refactoring:
  enabled: true
  timezone: UTC
  missions:
    - mission_type: cleanup_dead_code
      schedule: "0 3 * * *"      # 3 AM daily
      enabled: true
      
    - mission_type: improve_coverage
      schedule: "0 3 30 * *"     # 3 AM monthly
      enabled: true
      
    - mission_type: optimize_imports
      schedule: "0 4 * * *"      # 4 AM daily
      enabled: true
      
    - mission_type: refactor_complex_functions
      schedule: "0 5 * * 0"      # 5 AM every Sunday
      enabled: true
      approval_required: true    # Needs review
```

---

## 5. Simulation Engine Core

### Purpose
Foundation for Phase 40 (Mission Simulation)

### Implementation

```python
# src/infrastructure/simulation_engine.py

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SimulationResult:
    predicted_changes: Dict
    predicted_risks: List[str]
    success_probability: float
    estimated_confidence: float

class SimulationEngine:
    """Simulate mission execution without actually running it"""
    
    def __init__(self, analyzer, validator):
        self.analyzer = analyzer
        self.validator = validator
    
    def simulate_changes(self, mission_type: str, 
                        affected_files: List[str]) -> SimulationResult:
        """Predict what changes would happen"""
        
        # Analyze what mission would do
        predictions = self._predict_mission_changes(
            mission_type, affected_files
        )
        
        # Validate predictions
        risks = self._predict_risks(predictions)
        
        # Estimate success
        confidence = self._estimate_confidence(
            mission_type, predictions, risks
        )
        
        return SimulationResult(
            predicted_changes=predictions,
            predicted_risks=risks,
            success_probability=confidence,
            estimated_confidence=confidence
        )
    
    def _predict_mission_changes(self, mission_type: str,
                                 affected_files: List[str]) -> Dict:
        """Predict changes for mission"""
        
        if mission_type == "cleanup":
            return self._predict_cleanup_changes(affected_files)
        elif mission_type == "coverage":
            return self._predict_coverage_changes(affected_files)
        # ... etc
    
    def _predict_risks(self, predictions: Dict) -> List[str]:
        """Identify predicted risks"""
        risks = []
        # Analyze predictions for risks
        return risks
```

---

## 6. Multi-Agent Base Framework

### Purpose
Foundation for Phase 50+ (Multi-Agent System)

### Implementation

```python
# src/infrastructure/agent_framework.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class AgentInput:
    data: Dict
    context: Dict = None

@dataclass
class AgentOutput:
    data: Dict
    context: Dict = None
    next_agent: str = None

class AutonomousAgent(ABC):
    """Base class for autonomous agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.input_schema = None
        self.output_schema = None
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process input and return output"""
        pass
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate input against schema"""
        pass

class AgentPipeline:
    """Execute agents in sequence or parallel"""
    
    def __init__(self):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.pipeline_config = None
    
    def register_agent(self, agent: AutonomousAgent):
        """Register agent in pipeline"""
        self.agents[agent.name] = agent
    
    async def execute_pipeline(self, 
                              initial_input: AgentInput,
                              start_agent: str) -> AgentOutput:
        """Execute pipeline starting from agent"""
        
        current = initial_input
        current_agent_name = start_agent
        
        while current_agent_name:
            agent = self.agents[current_agent_name]
            current = await agent.process(current)
            current_agent_name = current.next_agent
        
        return current

class AgentOrchestrator:
    """High-level orchestrator for agent systems"""
    
    def __init__(self):
        self.pipelines: Dict[str, AgentPipeline] = {}
    
    def register_pipeline(self, name: str, pipeline: AgentPipeline):
        """Register a pipeline configuration"""
        self.pipelines[name] = pipeline
    
    async def run_pipeline(self, pipeline_name: str,
                          input_data: Dict) -> Dict:
        """Run registered pipeline"""
        pipeline = self.pipelines[pipeline_name]
        result = await pipeline.execute_pipeline(
            AgentInput(data=input_data),
            start_agent="analysis"
        )
        return result.data
```

---

## 7. Integration Checklist

The infrastructure pieces above should integrate with:

- **Phase 32** (Continuous Validation): Uses graph store
- **Phase 34** (Telemetry): Logs metrics to mission configs
- **Phase 36** (Planning): Provides data to simulation engine
- **Phase 38** (LLM Planning): Enhanced with graph and approval data
- **Future phases**: Use all infrastructure

---

## 8. Implementation Order

### Week 1
- [ ] Graph store infrastructure (1-2 days)
- [ ] Mission config framework (1-2 days)
- [ ] Basic testing (1-2 days)

### Week 2
- [ ] Approval system (2 days)
- [ ] Notification handlers (2 days)
- [ ] Integration testing (2 days)

### Week 3
- [ ] Mission scheduler (2 days)
- [ ] Simulation engine core (2 days)
- [ ] Agent framework (2 days)

### Week 4
- [ ] Integration with Phases 34-38
- [ ] End-to-end testing
- [ ] Documentation
- [ ] Ready for Phase 39

---

## 9. Testing Strategy

### Unit Tests
```
test_graph_store.py
├─ Node/edge creation
├─ Dependency queries
└─ Cycle detection

test_mission_config.py
├─ Configuration loading
├─ Validation
└─ Serialization

test_approval_system.py
├─ Request creation
├─ Timeout handling
└─ Status management

test_scheduler.py
├─ Job scheduling
├─ Cron patterns
└─ Execution

test_simulation_engine.py
├─ Prediction accuracy
├─ Risk detection
└─ Confidence scoring

test_agent_framework.py
├─ Agent registration
├─ Pipeline execution
└─ Context passing
```

### Integration Tests
- Graph store + Telemetry
- Mission config + Scheduler
- Approval + Notifications
- All components together

---

## 10. Success Criteria

- [ ] All infrastructure pieces deployable
- [ ] Phase 34-38 remains stable
- [ ] No performance regressions
- [ ] Team comfortable with new infrastructure
- [ ] Ready to launch Phase 39

---

## Deployment

```bash
# Add infrastructure to existing system
src/
├─ infrastructure/
│  ├─ graph_store.py              (NEW)
│  ├─ mission_config.py            (NEW)
│  ├─ approval_system.py          (NEW)
│  ├─ scheduler.py                (NEW)
│  ├─ simulation_engine.py        (NEW)
│  └─ agent_framework.py          (NEW)
├─ phase34_mission_telemetry.py   (existing)
├─ phase35_parallel_executor.py   (existing)
├─ ... (other phases)

config/
├─ missions/                        (NEW)
│  ├─ cleanup_dead_code.yaml
│  ├─ improve_coverage.yaml
│  ├─ optimize_imports.yaml
│  └─ ... (other mission configs)
└─ schedule.yaml                   (NEW)

# Deploy normally
```

---

## Next Steps

1. **This Week**: Review and approve infrastructure design
2. **Next Week**: Begin implementation
3. **Week 3-4**: Integration and testing
4. **Week 5**: Documentation and team training
5. **Week 6**: Ready for Phase 39

This infrastructure investment now will save weeks of time when launching Phases 39-50+.

The foundation is ready. Let's build the future of autonomous development! 🚀
