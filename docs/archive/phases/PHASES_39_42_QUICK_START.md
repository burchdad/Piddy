# Phases 39-42: Quick Start Guide

**Status**: ✅ Ready to Use  
**Date**: March 6, 2026  

---

## Installation

```bash
# Install dependencies
pip install networkx pyyaml

# Verify installation
python3 -c "from src.infrastructure import *; from src.phase39_*; print('✓ Ready')"
```

---

## 5-Minute Demo

### 1. Create a Graph with Dependencies

```python
from src.infrastructure.graph_store import DependencyGraphStore, GraphNode, GraphEdge

store = DependencyGraphStore("demo.db")

# Define nodes (functions, modules, services)
nodes = [
    GraphNode("auth_handler", "function", {"file": "auth.py"}),
    GraphNode("api_client", "function", {"file": "client.py"}),
    GraphNode("cache_layer", "function", {"file": "cache.py"}),
]

# Define dependencies (who calls whom)
edges = [
    GraphEdge("auth_handler", "cache_layer", "calls", {}),
    GraphEdge("api_client", "auth_handler", "calls", {}),
]

store.create_graph("my_service", "repo1", nodes, edges)
```

### 2. Analyze Impact of Changes

```python
from src.phase39_impact_graph_visualization import ImpactGraphVisualizer

visualizer = ImpactGraphVisualizer(store)

# What happens if we change auth_handler?
analysis = visualizer.analyze_change("my_service", "auth_handler")

print(f"⚠️ Impact Level: {analysis.impact_level.name}")
print(f"  Directly affected: {len(analysis.direct_dependents)}")
print(f"  Total cascading: {len(analysis.transitive_dependents)}")
print(f"  % of codebase: {analysis.impact_percentage:.1f}%")
```

### 3. Simulate a Mission

```python
from src.phase40_mission_simulation import MissionSimulator
from src.infrastructure.mission_config import MissionConfig, MissionType, RiskTolerance

config = MissionConfig(
    name="cleanup_dead_code",
    type=MissionType.CLEANUP,
    description="Remove unused code",
    priority=3,
    risk_tolerance=RiskTolerance.LOW,
    approval_required=False,
    min_confidence=0.7,
)

simulator = MissionSimulator()

# Simulate with repository context
repo_context = {
    'estimated_dead_functions': 5,
    'estimated_unused_imports': 3,
}

report = await simulator.simulate_mission(config, repo_context)

print(f"✓ Safe to execute: {report.can_proceed}")
print(f"  Confidence: {report.confidence:.0%}")
print(f"  Recommendation: {report.recommendation}")
```

### 4. Coordinate Across Repos

```python
from src.phase41_multi_repo_coordination import (
    MultiRepoCoordinator, RepositoryInfo, CrossRepoDependency
)

coordinator = MultiRepoCoordinator(store)

# Register your microservices
coordinator.register_repository(RepositoryInfo(
    repo_id="auth_service",
    repo_name="Auth Service",
    repo_path="/repos/auth",
    graph_id="graph_auth",
))

coordinator.register_repository(RepositoryInfo(
    repo_id="api_service",
    repo_name="API Service",  
    repo_path="/repos/api",
    graph_id="graph_api",
))

# Map dependencies
coordinator.add_cross_repo_dependency(CrossRepoDependency(
    source_repo="api_service",
    target_repo="auth_service",
    dependency_type="imports",
))

# Plan coordinated refactoring
mission = coordinator.plan_coordinated_execution(
    primary_repo="auth_service",
    mission_name="add_types",
    changed_modules=["handlers"],
)

# See execution order
print(f"Execute in order: {mission.execution_order}")

# Generate PR chain
prs = coordinator.create_pr_chain(mission)
for pr in prs:
    print(f"PR in {pr['repo_name']}: {pr['title']}")
```

### 5. Schedule Nightly Refactoring

```python
from src.phase42_continuous_refactoring import (
    create_default_continuous_refactoring
)
import asyncio

scheduler = create_default_continuous_refactoring()

# See scheduled missions
missions = scheduler.get_nightly_missions()
for m in missions:
    print(f"  • {m.name} - {m.frequency.value}")

# Start scheduler (runs in background)
# asyncio.create_task(scheduler.start_scheduler())
```

---

## API Reference

### Graph Store
```python
# Store and query dependency graphs
store = DependencyGraphStore("graphs.db")
store.create_graph(id, repo, nodes, edges)
store.get_dependencies(graph_id, node_id)
store.get_transitive_dependencies(graph_id, node_id) 
store.find_circular_dependencies(graph_id)
store.analyze_node(graph_id, node_id)
```

### Mission Config
```python
# Define mission types and settings
config = MissionConfig(
    name="cleanup", 
    type=MissionType.CLEANUP,
    risk_tolerance=RiskTolerance.LOW,
    approval_required=False,
    auto_merge=True,
)

manager = MissionConfigManager("config/missions")
manager.create_default_missions()
manager.save_config(config)
manager.validate_config(config)
```

### Approval System
```python
# Request and track approvals
approval_mgr = ApprovalManager()

request = ApprovalRequest(
    mission_id="m1",
    mission_name="Refactor",
    mission_type="refactor",
    description="Simplify functions",
    prediction={},
    confidence=0.8,
    risk_level="medium",
    requires_approval=True,
)

await approval_mgr.request_approval(request)
await approval_mgr.approve("m1", approved_by="alice")
```

### Mission Scheduler
```python
# Schedule recurring missions
scheduler = MissionScheduler()

# Daily cleanup at 2 AM
cleanup = ScheduleBuilder.daily("cleanup_dead_code", at_time="02:00")
scheduler.schedule_mission(cleanup)

# Weekly coverage improvement
coverage = ScheduleBuilder.weekly("improve_coverage", day=6)  # Sunday
scheduler.schedule_mission(coverage)

# One-time execution
once = ScheduleBuilder.once("urgent_fix", datetime(...))
scheduler.schedule_mission(once)

await scheduler.start()
```

### Simulation Engine
```python
# Predict mission outcomes
engine = SimulationEngine()

result = engine.simulate(
    mission_name="cleanup_dead_code",
    mission_state={'id': 'm1', 'type': 'cleanup'},
    repo_context={
        'estimated_dead_functions': 5,
        'estimated_unused_imports': 3,
    }
)

print(result.will_succeed)        # True/False
print(result.confidence)          # 0.0-1.0
print(result.get_risk_score())   # 0.0-1.0
print(result.potential_issues)   # List of concerns
```

### Impact Visualization
```python
# Analyze and visualize change impact
visualizer = ImpactGraphVisualizer(graph_store)

analysis = visualizer.analyze_change(graph_id, node_id)
viz = visualizer.create_visualization(analysis)

# Export in different formats
html = visualizer.export_html_report(analysis, viz)
svg = visualizer.export_svg(viz)
json = visualizer.export_json(viz)
```

### Mission Simulator
```python
# Simulate before execution
simulator = MissionSimulator()

report = await simulator.simulate_mission(config, repo_context)

# Check if safe to run
if report.can_proceed:
    execute_mission()
else:
    print(report.recommendation)

# Get approval status
status = simulator.get_simulation_status(mission_id)
```

### Multi-Repo Coordinator
```python
# Coordinate changes across repos
coordinator = MultiRepoCoordinator(store)

coordinator.register_repository(repo_info)
coordinator.add_cross_repo_dependency(dependency)

mission = coordinator.plan_coordinated_execution(
    primary_repo, mission_name, changed_modules
)

# Validate plan before execution
valid, errors = coordinator.validate_coordinated_plan(mission)

# Generate synced PRs
prs = coordinator.create_pr_chain(mission)
```

### Continuous Refactoring
```python
# Schedule nightly refactoring
scheduler = ContinuousRefactoringScheduler()

mission = RefactoringMission(
    name="nightly_cleanup",
    mission_config=config,
    frequency=ScheduleFrequency.DAILY,
    auto_merge_policy=AutoMergePolicy.ON_SUCCESS,
    blackout_hours=[9, 10, 11, 12, 13, 14, 15, 16, 17],
)

scheduler.add_refactoring_mission(mission)
await scheduler.start_scheduler()

# Monitor execution
prs = scheduler.get_active_prs()
history = scheduler.get_execution_history("nightly_cleanup", limit=10)
```

### Agent Framework
```python
# Multi-agent coordination (Phase 50+)
orchestrator = AgentOrchestrator()

analyst = AnalystAgent("analyst-1")
planner = PlannerAgent("planner-1")
executor = ExecutorAgent("executor-1")

orchestrator.register_agent(analyst)
orchestrator.register_agent(planner)
orchestrator.register_agent(executor)

# Agents communicate via messages
await orchestrator.send_request(
    sender_id="orchestrator",
    recipient_id="analyst",
    request_type="analyze_changes",
    payload={'files': ['auth.py', 'client.py']}
)

await orchestrator.start()
```

---

## Common Workflows

### Workflow 1: Safe Autonomous Refactoring

```python
async def safe_refactor():
    # 1. Define mission
    config = get_mission_config("cleanup_dead_code")
    
    # 2. Analyze impact
    analysis = visualizer.analyze_change(graph_id, "main_function")
    if analysis.impact_level == ImpactLevel.CRITICAL:
        print("Too risky - requires manual review")
        return
    
    # 3. Simulate
    report = await simulator.simulate_mission(config, repo_context)
    if not report.can_proceed:
        print(f"Blocked: {report.recommendation}")
        return
    
    # 4. Execute (safe because simulation passed)
    result = execute_mission(config)
    print(f"✓ Executed: {result}")
    
    # 5. Record for learning
    engine.record_execution("cleanup", result.simulation, actual_result)

await safe_refactor()
```

### Workflow 2: Coordinated Multi-Repo Change

```python
async def coordinated_refactor():
    # 1. Register repos
    for repo_info in my_microservices:
        coordinator.register_repository(repo_info)
    
    # 2. Map dependencies  
    for dep in my_dependencies:
        coordinator.add_cross_repo_dependency(dep)
    
    # 3. Plan coordinated execution
    mission = coordinator.plan_coordinated_execution(
        "auth_service", "add_types", ["handlers"]
    )
    
    # 4. Validate
    valid, errors = coordinator.validate_coordinated_plan(mission)
    if not valid:
        print(f"Invalid plan: {errors}")
        return
    
    # 5. Create PR chain
    prs = coordinator.create_pr_chain(mission)
    for pr in prs:
        create_and_open_pr(pr)
    
    # 6. Merge in order
    for pr in prs:
        await wait_for_approval(pr)
        merge_pr(pr)

await coordinated_refactor()
```

### Workflow 3: Nightly Autonomous Missions

```python
async def setup_nightly():
    scheduler = create_default_continuous_refactoring()
    
    # Missions already configured:
    # - cleanup (daily 2 AM)
    # - coverage (weekly Sunday 2 AM)
    # - types (weekly Saturday 2 AM)
    
    # Start scheduler
    await scheduler.start_scheduler()
    
    # Monitor in loop
    while True:
        for pr in scheduler.get_active_prs().values():
            print(f"PR {pr['mission']}: {pr['status']}")
        await asyncio.sleep(60)

asyncio.run(setup_nightly())
```

---

## Troubleshooting

### "Graph not found"
```python
# Make sure graph is created first
store.create_graph("my_graph", "repo1", nodes, edges)

# Or load from database
store.load_graph("my_graph")
```

### "Confidence too low"
```python
# Increase when safe, or improve simulation
config.min_confidence = 0.6  # Default is 0.7

# Or improve repo context for better predictions
repo_context = {
    'estimated_dead_functions': 5,   # Provide this
    'estimated_unused_imports': 3,
    'high_complexity_functions': 2,
}
```

### "Permission denied" on auto-merge
```python
# Set policy to require approval first
mission.auto_merge_policy = AutoMergePolicy.ON_APPROVAL

# Then approve
await approval_manager.approve(mission_id, approved_by="alice")
```

### "Circular dependency"
```python
# Detect
cycles = store.find_circular_dependencies(graph_id)

# Break manually or
# Use safe execution order from coordinator
mission = coordinator.plan_coordinated_execution(...)
# execution_order respects cycles via topological sort
```

---

## Next: Read Full Documentation

- [PHASES_39_42_DELIVERY.md](PHASES_39_42_DELIVERY.md) - Complete specs
- [INFRASTRUCTURE_SETUP_GUIDE.md](INFRASTRUCTURE_SETUP_GUIDE.md) - Architecture
- [PHASE39_PLUS_ROADMAP.md](PHASE39_PLUS_ROADMAP.md) - Detailed designs

---

**Ready to build on this foundation!** 🚀
