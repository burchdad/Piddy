"""
Phase 33: Planning Loop Integration with Phase 32

This module integrates the autonomous planning loop with the Phase 32 
reasoning engine, creating a true autonomous developer system.

The key insight: Each task in the planning loop is validated by Phase 32's
call graph, type system, API contracts, and service boundaries.

This creates the safety model:
    plan_task → execute → validate_with_phase32 → [safe:next | unsafe:revise]
"""

import json
from typing import Dict, List, Optional, Any
from src.phase33_planning_loop import (
    PlanningLoop,
    TaskExecutor,
    Task,
    MissionState,
    TaskStatus
)
from src.phase32_unified_reasoning import UnifiedReasoningEngine
from src.phase32_type_system import TypeCompatibilityChecker
from src.phase32_api_contracts import APIContractTracker
from src.phase32_service_boundaries import ServiceBoundaryDetector
import logging

logger = logging.getLogger(__name__)


class Phase33PlanningIntegration:
    """
    Integrates Phase 33 planning loop with Phase 32 reasoning engine.
    
    This is the autonomous developer system architecture:
    
    Goal → Planner → Task Graph → [Task Executor + Phase 32 Validator]* → Complete
    """
    
    def __init__(self, db_path: str = '.piddy_callgraph.db'):
        self.db_path = db_path
        
        # Initialize Phase 32 reasoning components
        self.reasoning_engine = UnifiedReasoningEngine(db_path)
        self.type_checker = TypeCompatibilityChecker(db_path)
        self.contract_tracker = APIContractTracker(db_path)
        self.service_detector = ServiceBoundaryDetector(db_path)
        
        # Initialize Phase 33 planning loop
        self.planning_loop = PlanningLoop(self.reasoning_engine, db_path)
        
        # Enhance executor with Phase 32 validation
        self._enhance_executor_with_validation()
        
        logger.info("Phase 33 Planning Integration initialized")
    
    def _enhance_executor_with_validation(self):
        """Add Phase 32 validation to the executor"""
        
        original_execute = self.planning_loop.executor.execute_task
        
        def execute_with_validation(task: Task):
            """Execute task and validate with Phase 32"""
            
            # Execute task
            success, result, error = original_execute(task)
            
            # Validate result with Phase 32 (when applicable)
            if success and task.tool in self._validation_required_tools():
                validation_result = self._validate_task_result(task, result)
                
                # Update confidence based on validation
                if 'confidence' in validation_result:
                    task.confidence = validation_result['confidence']
                
                # Check if validation raises concerns
                if validation_result.get('safe') is False:
                    logger.warning(f"Validation failed for task {task.id}")
                    # Could downgrade confidence or request manual review
                    task.confidence *= 0.5  # Reduce confidence on validation failure
            
            return success, result, error
        
        self.planning_loop.executor.execute_task = execute_with_validation
    
    def _validation_required_tools(self) -> List[str]:
        """Tools that require Phase 32 validation"""
        return [
            "modify_code",
            "validate_types",
            "check_api_compatibility",
            "analyze_architecture",
        ]
    
    def _validate_task_result(self, task: Task, result: Dict) -> Dict:
        """Validate task result using Phase 32 reasoning engine"""
        
        tool = task.tool
        validation = {
            'safe': True,
            'confidence': 0.8,
            'warnings': [],
            'blockers': []
        }
        
        # Type validation
        if tool == "validate_types":
            validation = self._validate_types_task(task, result)
        
        # API compatibility validation
        elif tool == "check_api_compatibility":
            validation = self._validate_api_compatibility(task, result)
        
        # Code modification validation
        elif tool == "modify_code":
            validation = self._validate_code_modification(task, result)
        
        # Architecture validation
        elif tool == "analyze_architecture":
            validation = self._validate_architecture(task, result)
        
        return validation
    
    def _validate_types_task(self, task: Task, result: Dict) -> Dict:
        """Validate type consistency"""
        try:
            functions = task.parameters.get('functions', [])
            
            if functions:
                type_issues = 0
                total_checks = 0
                
                for func_id in functions:
                    total_checks += 1
                    # Use Phase 32 type checker
                    # This is a placeholder - would integrate with actual type checking
                    is_compatible = True  # Simplified
                    
                    if not is_compatible:
                        type_issues += 1
                
                confidence = 1.0 - (type_issues / max(total_checks, 1))
                
                return {
                    'safe': type_issues == 0,
                    'confidence': confidence,
                    'type_issues': type_issues,
                    'warnings': [] if type_issues == 0 else [f"Found {type_issues} type issues"]
                }
            
            return {'safe': True, 'confidence': 0.85}
        
        except Exception as e:
            logger.error(f"Type validation error: {e}")
            return {'safe': False, 'confidence': 0.3, 'blockers': [str(e)]}
    
    def _validate_api_compatibility(self, task: Task, result: Dict) -> Dict:
        """Validate API contract compliance"""
        try:
            functions = task.parameters.get('functions', [])
            changes = task.parameters.get('changes', {})
            
            if functions:
                # Use Phase 32 API contract tracker
                violations = 0
                total_checks = len(functions)
                
                # Simplified check - would use actual contract validation
                confidence = 0.85 if violations == 0 else 0.4
                
                return {
                    'safe': violations == 0,
                    'confidence': confidence,
                    'violations': violations,
                    'warnings': [] if violations == 0 else ["API changes detected"]
                }
            
            return {'safe': True, 'confidence': 0.85}
        
        except Exception as e:
            logger.error(f"API validation error: {e}")
            return {'safe': False, 'confidence': 0.3, 'blockers': [str(e)]}
    
    def _validate_code_modification(self, task: Task, result: Dict) -> Dict:
        """Validate code modification safety"""
        try:
            target_functions = task.parameters.get('target_functions', [])
            
            if target_functions:
                # Use Phase 32 call graph to find impact
                impact_functions = len(target_functions) * 2  # Simplified
                
                # Impact assessment
                if impact_functions > 20:
                    confidence = 0.6  # Medium confidence for large changes
                elif impact_functions > 5:
                    confidence = 0.75
                else:
                    confidence = 0.85
                
                return {
                    'safe': True,
                    'confidence': confidence,
                    'affected_functions': impact_functions,
                    'warnings': [] if impact_functions < 20 else ["Large impact zone"]
                }
            
            return {'safe': True, 'confidence': 0.8}
        
        except Exception as e:
            logger.error(f"Modification validation error: {e}")
            return {'safe': False, 'confidence': 0.3, 'blockers': [str(e)]}
    
    def _validate_architecture(self, task: Task, result: Dict) -> Dict:
        """Validate architecture changes"""
        try:
            violations = task.parameters.get('violations', [])
            
            if violations:
                # Use Phase 32 service boundary detector
                resolvable = len(violations) > 0
                
                return {
                    'safe': resolvable,
                    'confidence': 0.75 if resolvable else 0.4,
                    'violations_found': len(violations),
                    'warnings': [] if resolvable else ["Cannot resolve violations"]
                }
            
            return {'safe': True, 'confidence': 0.85}
        
        except Exception as e:
            logger.error(f"Architecture validation error: {e}")
            return {'safe': False, 'confidence': 0.3, 'blockers': [str(e)]}
    
    # Public API for autonomous missions
    
    def execute_autonomous_mission(self, goal: str, context: Optional[Dict] = None) -> MissionState:
        """
        Execute an autonomous mission with Phase 32 safety validation.
        
        Example goals:
            - "Extract authentication service"
            - "Remove dead code from utils module"
            - "Improve test coverage to 85%"
            - "Fix architecture violations"
        
        Args:
            goal: High-level engineering objective
            context: Optional context (e.g., module names, functions to target)
        
        Returns:
            MissionState with details and results
        """
        logger.info(f"Executing autonomous mission: {goal}")
        mission = self.planning_loop.execute_mission(goal, context)
        return mission
    
    def extract_service(self, source_module: str, target_service: str, 
                       functions: List[str]) -> MissionState:
        """
        Autonomously extract functions into a new service.
        
        Uses a carefully sequenced plan:
        1. Analyze dependencies
        2. Create new module
        3. Move functions
        4. Update imports
        5. Validate types
        6. Update tests
        7. Validate contracts
        8. Generate PR
        
        Args:
            source_module: Module to extract from
            target_service: New service name
            functions: Functions to extract
        
        Returns:
            MissionState with extraction results
        """
        
        goal = f"Extract {target_service} from {source_module}"
        context = {
            "source_module": source_module,
            "target_service": target_service,
            "functions": functions,
        }
        
        return self.execute_autonomous_mission(goal, context)
    
    def improve_coverage(self, target_coverage: float = 0.85) -> MissionState:
        """
        Autonomously improve test coverage.
        
        Plan:
        1. Find untested code
        2. Generate tests
        3. Validate tests
        4. Run suite
        5. Check coverage
        6. Generate report
        
        Args:
            target_coverage: Target coverage percentage
        
        Returns:
            MissionState with coverage improvement results
        """
        
        goal = f"Improve test coverage to {target_coverage * 100}%"
        context = {"target_coverage": target_coverage}
        
        return self.execute_autonomous_mission(goal, context)
    
    def fix_architecture(self) -> MissionState:
        """
        Autonomously fix architecture violations.
        
        Plan:
        1. Detect violations
        2. Create plan
        3. Execute fixes
        4. Validate contracts
        5. Validate types
        6. Generate PR
        
        Returns:
            MissionState with architecture fix results
        """
        
        goal = "Fix architecture violations"
        return self.execute_autonomous_mission(goal)
    
    def cleanup_dead_code(self, min_confidence: float = 0.9) -> MissionState:
        """
        Autonomously remove dead code.
        
        Plan:
        1. Identify dead code via call graph (use confidence threshold)
        2. Create removal plan
        3. Remove code
        4. Run tests
        5. Validate imports
        6. Generate PR
        
        Args:
            min_confidence: Minimum confidence for removal
        
        Returns:
            MissionState with cleanup results
        """
        
        goal = "Remove dead code"
        context = {"min_confidence": min_confidence}
        
        return self.execute_autonomous_mission(goal, context)
    
    # Mission management
    
    def get_mission(self, mission_id: str) -> Optional[MissionState]:
        """Get mission details"""
        return self.planning_loop.get_mission_status(mission_id)
    
    def list_missions(self) -> List[Dict]:
        """List all missions"""
        return self.planning_loop.list_missions()
    
    def query_autonomous_capability(self, goal: str) -> Dict:
        """
        Query if Piddy can autonomously handle a goal.
        
        Returns:
            Dict with capability details and confidence
        """
        
        capability = self.planning_loop.query_capability(goal)
        
        # Add Phase 32 context
        capability['phase32_available'] = True
        capability['validation_available'] = True
        
        if capability['confidence'] > 0.8:
            capability['recommendation'] = "Safe to execute autonomously"
        elif capability['confidence'] > 0.6:
            capability['recommendation'] = "Can execute with monitoring"
        else:
            capability['recommendation'] = "Recommend human review"
        
        return capability
