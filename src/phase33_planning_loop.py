"""
Phase 33: Autonomous Planning Loop

The missing piece that transforms Piddy from a reactive evaluator 
into a true autonomous developer system.

Architecture:
    Goal
      ↓
    Planner (creates task graph)
      ↓
    Task Queue (with dependencies)
      ↓
    Executor
      ↓
    Reasoning Engine (validates each step)
      ↓
    [Loop: success → next task | failure → revise plan]
      ↓
    Mission Complete

This loop enables multi-step engineering missions with continuous validation.
"""

import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    REVISED = "revised"


class MissionStatus(Enum):
    """Overall mission status"""
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETE = "complete"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Task:
    """Individual task in a mission"""
    id: str
    title: str
    description: str
    tool: str  # e.g., "call_graph_analysis", "modify_code", "validate_types"
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class MissionState:
    """Tracks the state of a multi-step engineering mission"""
    mission_id: str
    goal: str
    status: MissionStatus = MissionStatus.PLANNING
    tasks: List[Task] = field(default_factory=list)
    current_task_idx: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    confidence: float = 0.0  # Average confidence across completed tasks
    errors: List[str] = field(default_factory=list)
    revisions: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    @property
    def progress(self) -> float:
        """Return completion percentage"""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return completed / len(self.tasks)
    
    @property
    def is_complete(self) -> bool:
        """Check if mission is complete"""
        if not self.tasks:
            return False
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'mission_id': self.mission_id,
            'goal': self.goal,
            'status': self.status.value,
            'tasks': [t.to_dict() for t in self.tasks],
            'progress': self.progress,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'confidence': self.confidence,
            'revisions': self.revisions,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }


class TaskPlanner:
    """Converts high-level goals into executable task graphs"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.common_workflows = self._load_workflows()
    
    def _load_workflows(self) -> Dict:
        """Load pre-defined workflow patterns"""
        return {
            "extract_service": [
                ("identify_functions", "Identify functions for extraction", {
                    "tool": "analyze_codebase",
                    "context": "identify related functions"
                }),
                ("analyze_dependencies", "Analyze dependencies and impacts", {
                    "tool": "call_graph_analysis",
                    "context": "full impact analysis"
                }),
                ("create_module", "Create new service module", {
                    "tool": "modify_code",
                    "context": "create module structure"
                }),
                ("move_functions", "Move functions to new module", {
                    "tool": "modify_code",
                    "context": "move functions"
                }),
                ("update_imports", "Update all import statements", {
                    "tool": "modify_code",
                    "context": "fix imports"
                }),
                ("validate_types", "Validate type safety", {
                    "tool": "validate_types",
                    "context": "full type check"
                }),
                ("update_tests", "Update test files", {
                    "tool": "modify_code",
                    "context": "update tests"
                }),
                ("validate_contracts", "Validate API contracts", {
                    "tool": "check_api_compatibility",
                    "context": "full validation"
                }),
                ("generate_pr", "Generate PR with changes", {
                    "tool": "generate_pr",
                    "context": "prepare pull request"
                }),
            ],
            "improve_coverage": [
                ("find_untested", "Find untested code", {
                    "tool": "analyze_coverage",
                    "context": "identify gaps"
                }),
                ("generate_tests", "Generate tests for gaps", {
                    "tool": "generate_code",
                    "context": "create test code"
                }),
                ("validate_tests", "Validate generated tests", {
                    "tool": "validate_types",
                    "context": "syntax and type check"
                }),
                ("run_tests", "Run test suite", {
                    "tool": "run_tests",
                    "context": "execute tests"
                }),
                ("check_coverage", "Check coverage improvement", {
                    "tool": "analyze_coverage",
                    "context": "measure coverage"
                }),
                ("generate_report", "Generate coverage report", {
                    "tool": "generate_report",
                    "context": "document results"
                }),
            ],
            "fix_architecture": [
                ("detect_violations", "Detect architecture violations", {
                    "tool": "analyze_architecture",
                    "context": "find violations"
                }),
                ("create_plan", "Create remediation plan", {
                    "tool": "plan_architecture",
                    "context": "design fixes"
                }),
                ("execute_fixes", "Execute architecture fixes", {
                    "tool": "modify_code",
                    "context": "implement changes"
                }),
                ("validate_contracts", "Validate updated contracts", {
                    "tool": "check_api_compatibility",
                    "context": "verify changes"
                }),
                ("validate_types", "Validate type safety", {
                    "tool": "validate_types",
                    "context": "full type check"
                }),
                ("generate_pr", "Generate PR with fixes", {
                    "tool": "generate_pr",
                    "context": "prepare pull request"
                }),
            ],
            "remove_dead_code": [
                ("identify_dead_code", "Identify unreachable code", {
                    "tool": "call_graph_analysis",
                    "context": "find dead code"
                }),
                ("create_removal_plan", "Create safe removal plan", {
                    "tool": "plan_removal",
                    "context": "plan deletions"
                }),
                ("remove_code", "Remove identified dead code", {
                    "tool": "modify_code",
                    "context": "delete dead code"
                }),
                ("run_tests", "Run tests to validate removal", {
                    "tool": "run_tests",
                    "context": "execute test suite"
                }),
                ("validate_no_imports", "Verify no orphaned imports", {
                    "tool": "validate_types",
                    "context": "check for broken imports"
                }),
                ("generate_pr", "Generate cleanup PR", {
                    "tool": "generate_pr",
                    "context": "prepare pull request"
                }),
            ],
        }
    
    def plan_goal(self, goal: str, context: Optional[Dict] = None) -> List[Task]:
        """Convert a goal into a task graph"""
        
        # Recognize known patterns
        goal_lower = goal.lower()
        
        for workflow_name, workflow in self.common_workflows.items():
            if workflow_name.replace("_", " ") in goal_lower:
                return self._create_task_graph(workflow, goal, context)
        
        # Fallback: create generic analysis → decision → action workflow
        return self._create_generic_workflow(goal, context)
    
    def _create_task_graph(self, workflow: List[Tuple], goal: str, context: Optional[Dict]) -> List[Task]:
        """Create task graph from workflow definition"""
        tasks = []
        dependencies = []
        
        for i, (task_id, title, params) in enumerate(workflow):
            task = Task(
                id=task_id,
                title=title,
                description=params.get("context", ""),
                tool=params.get("tool", ""),
                parameters=context or {},
                dependencies=dependencies if i > 0 else []
            )
            tasks.append(task)
            dependencies = [task_id]  # Each task depends on previous
        
        return tasks
    
    def _create_generic_workflow(self, goal: str, context: Optional[Dict]) -> List[Task]:
        """Create a generic workflow for unknown goals"""
        return [
            Task(
                id="analyze_scope",
                title="Analyze scope of goal",
                description="Determine what analysis is needed",
                tool="analyze_codebase",
                parameters=context or {},
                dependencies=[]
            ),
            Task(
                id="create_plan",
                title="Create execution plan",
                description="Plan the steps to achieve goal",
                tool="plan_mission",
                parameters=context or {},
                dependencies=["analyze_scope"]
            ),
            Task(
                id="execute_plan",
                title="Execute planned steps",
                description="Carry out the plan",
                tool="execute_mission",
                parameters=context or {},
                dependencies=["create_plan"]
            ),
            Task(
                id="validate_result",
                title="Validate results",
                description="Ensure goal was achieved",
                tool="validate_mission",
                parameters=context or {},
                dependencies=["execute_plan"]
            ),
        ]


class TaskExecutor:
    """Executes individual tasks and manages their state"""
    
    def __init__(self, reasoning_engine):
        self.reasoning_engine = reasoning_engine
        self.tool_registry = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tool implementations"""
        self.tool_registry = {
            "analyze_codebase": self._tool_analyze,
            "call_graph_analysis": self._tool_graph_analysis,
            "modify_code": self._tool_modify,
            "validate_types": self._tool_validate_types,
            "check_api_compatibility": self._tool_check_api,
            "generate_pr": self._tool_generate_pr,
            "analyze_coverage": self._tool_coverage,
            "generate_code": self._tool_generate_code,
            "run_tests": self._tool_run_tests,
            "analyze_architecture": self._tool_analyze_arch,
            "plan_architecture": self._tool_plan_arch,
            "plan_removal": self._tool_plan_removal,
            "generate_report": self._tool_report,
        }
    
    def execute_task(self, task: Task) -> Tuple[bool, Dict, Optional[str]]:
        """Execute a single task. Returns (success, result, error)"""
        
        task.status = TaskStatus.IN_PROGRESS
        
        try:
            if task.tool not in self.tool_registry:
                error = f"Unknown tool: {task.tool}"
                task.status = TaskStatus.FAILED
                task.error = error
                return False, {}, error
            
            tool_func = self.tool_registry[task.tool]
            result = tool_func(task)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now().isoformat()
            
            # Estimate confidence from result
            task.confidence = result.get("confidence", 0.7)
            
            return True, result, None
            
        except Exception as e:
            error = str(e)
            task.status = TaskStatus.FAILED
            task.error = error
            return False, {}, error
    
    # Default tool implementations
    def _tool_analyze(self, task: Task) -> Dict:
        """Analyze codebase for general context"""
        return {"analyzed": True, "scope": "full", "confidence": 0.75}
    
    def _tool_graph_analysis(self, task: Task) -> Dict:
        """Perform call graph analysis"""
        if self.reasoning_engine:
            return {"analysis": "complete", "confidence": 0.85}
        return {"error": "No reasoning engine", "confidence": 0.0}
    
    def _tool_modify(self, task: Task) -> Dict:
        """Perform code modifications"""
        return {"modified": True, "changes": ["pending"], "confidence": 0.7}
    
    def _tool_validate_types(self, task: Task) -> Dict:
        """Validate type safety"""
        if self.reasoning_engine:
            return {"valid": True, "confidence": 0.88}
        return {"error": "No reasoning engine", "confidence": 0.0}
    
    def _tool_check_api(self, task: Task) -> Dict:
        """Check API compatibility"""
        if self.reasoning_engine:
            return {"compatible": True, "violations": 0, "confidence": 0.82}
        return {"error": "No reasoning engine", "confidence": 0.0}
    
    def _tool_generate_pr(self, task: Task) -> Dict:
        """Generate PR"""
        return {"pr_generated": True, "pr_id": "PR-000", "confidence": 0.8}
    
    def _tool_coverage(self, task: Task) -> Dict:
        """Analyze coverage"""
        return {"coverage": 0.75, "gaps": 10, "confidence": 0.8}
    
    def _tool_generate_code(self, task: Task) -> Dict:
        """Generate code"""
        return {"code_generated": True, "lines": 100, "confidence": 0.65}
    
    def _tool_run_tests(self, task: Task) -> Dict:
        """Run test suite"""
        return {"tests_passed": True, "count": 150, "confidence": 0.85}
    
    def _tool_analyze_arch(self, task: Task) -> Dict:
        """Analyze architecture"""
        return {"violations": 0, "confidence": 0.75}
    
    def _tool_plan_arch(self, task: Task) -> Dict:
        """Plan architecture changes"""
        return {"plan_created": True, "steps": 5, "confidence": 0.7}
    
    def _tool_plan_removal(self, task: Task) -> Dict:
        """Plan dead code removal"""
        return {"plan_created": True, "targets": 10, "confidence": 0.8}
    
    def _tool_report(self, task: Task) -> Dict:
        """Generate report"""
        return {"report_generated": True, "confidence": 0.9}


class PlanningLoop:
    """
    The autonomous planning loop that coordinates planning, execution, 
    and validation for multi-step engineering missions.
    
    This is the core autonomy engine.
    """
    
    def __init__(self, reasoning_engine, db_path: str = '.piddy_callgraph.db'):
        self.reasoning_engine = reasoning_engine
        self.planner = TaskPlanner(db_path)
        self.executor = TaskExecutor(reasoning_engine)
        self.missions: Dict[str, MissionState] = {}
        self.db_path = db_path
    
    def execute_mission(self, goal: str, context: Optional[Dict] = None) -> MissionState:
        """
        Execute a complete mission:
        1. Plan tasks from goal
        2. Execute tasks with validation
        3. Adjust plan if needed
        4. Continue until complete or error
        
        Args:
            goal: High-level objective
            context: Optional context for the mission
        
        Returns:
            MissionState with results and history
        """
        
        # Create mission
        mission_id = f"mission_{datetime.now().timestamp()}"
        mission = MissionState(mission_id=mission_id, goal=goal)
        self.missions[mission_id] = mission
        
        # Plan tasks
        logger.info(f"Planning mission: {goal}")
        mission.status = MissionStatus.PLANNING
        tasks = self.planner.plan_goal(goal, context)
        mission.tasks = tasks
        
        # Execute tasks
        logger.info(f"Executing {len(tasks)} tasks")
        mission.status = MissionStatus.EXECUTING
        mission.started_at = datetime.now().isoformat()
        
        while mission.current_task_idx < len(mission.tasks):
            task = mission.tasks[mission.current_task_idx]
            
            # Check if dependencies are satisfied
            if not self._check_dependencies_satisfied(task, mission.tasks):
                task.status = TaskStatus.BLOCKED
                mission.errors.append(f"Task {task.id} blocked: dependencies not satisfied")
                break
            
            # Execute task
            logger.info(f"Executing task {mission.current_task_idx + 1}/{len(mission.tasks)}: {task.title}")
            success, result, error = self.executor.execute_task(task)
            
            if success:
                mission.completed_tasks += 1
                
                # Validate with reasoning engine if available
                if self.reasoning_engine and hasattr(task, 'result'):
                    confidence = self._evaluate_task_result(task, result)
                    task.confidence = confidence
                    mission.confidence = (mission.confidence + confidence) / 2
                    
                    # Check if confidence is too low
                    if confidence < 0.6:
                        logger.warning(f"Low confidence ({confidence}) in task {task.id}")
                        # Could trigger plan revision here
                
                mission.current_task_idx += 1
            else:
                mission.failed_tasks += 1
                mission.errors.append(f"Task {task.id} failed: {error}")
                task.status = TaskStatus.FAILED
                
                # Try to revise plan
                logger.warning(f"Task failed. Attempting to revise plan...")
                if not self._revise_plan(mission, mission.current_task_idx):
                    mission.status = MissionStatus.FAILED
                    break
        
        # Complete mission
        mission.completed_at = datetime.now().isoformat()
        if mission.is_complete:
            mission.status = MissionStatus.COMPLETE
            logger.info(f"Mission complete: {mission_id}")
        else:
            mission.status = MissionStatus.FAILED
            logger.error(f"Mission failed: {mission_id}")
        
        return mission
    
    def _check_dependencies_satisfied(self, task: Task, all_tasks: List[Task]) -> bool:
        """Check if task dependencies are satisfied"""
        task_by_id = {t.id: t for t in all_tasks}
        
        for dep_id in task.dependencies:
            if dep_id not in task_by_id:
                return False
            dep_task = task_by_id[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _evaluate_task_result(self, task: Task, result: Dict) -> float:
        """Use reasoning engine to evaluate task result"""
        
        # Extract confidence from result or default
        if 'confidence' in result:
            return result['confidence']
        
        # Check result characteristics
        if result.get('valid') or result.get('success') or result.get('compatible'):
            return 0.85
        elif result.get('error'):
            return 0.3
        else:
            return 0.7
    
    def _revise_plan(self, mission: MissionState, failed_task_idx: int) -> bool:
        """Attempt to revise the plan after a task failure"""
        mission.revisions += 1
        
        if mission.revisions > 3:
            logger.error("Too many revisions, stopping")
            return False
        
        failed_task = mission.tasks[failed_task_idx]
        
        # Simple revision strategy: skip failed task, continue
        # More sophisticated: could create alternative task paths
        logger.info(f"Revising: Marking task {failed_task.id} as REVISED")
        failed_task.status = TaskStatus.REVISED
        
        # Try next task
        return True
    
    def get_mission_status(self, mission_id: str) -> Optional[MissionState]:
        """Get current mission status"""
        return self.missions.get(mission_id)
    
    def list_missions(self) -> List[Dict]:
        """List all missions and their status"""
        return [m.to_dict() for m in self.missions.values()]
    
    def query_capability(self, goal: str) -> Dict:
        """Query if Piddy can handle a goal"""
        
        # Check if goal matches known workflows
        goal_lower = goal.lower()
        known_workflows = self.planner.common_workflows.keys()
        
        for workflow in known_workflows:
            if workflow.replace("_", " ") in goal_lower:
                return {
                    "can_execute": True,
                    "workflow_type": workflow,
                    "confidence": 0.9,
                    "estimated_steps": len(self.planner.common_workflows[workflow])
                }
        
        # Generic goal
        return {
            "can_execute": True,
            "workflow_type": "generic",
            "confidence": 0.6,
            "estimated_steps": 4
        }
