"""
Simulation Engine
Predicts mission outcomes before execution

Supports:
- Phase 40: Mission simulation mode
- Phase 50+: Autonomous decision making
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class PredictionConfidence(Enum):
    """Confidence level of prediction"""
    VERY_LOW = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    VERY_HIGH = 1.0


@dataclass
class SimulationResult:
    """Result of mission simulation"""
    
    mission_id: str                  # Mission being simulated
    mission_name: str                # Mission name
    will_succeed: bool               # Predicted success
    confidence: float                # 0.0-1.0
    predicted_changes: Dict          # Expected code changes
    potential_issues: List[str] = field(default_factory=list)
    risks: Dict = field(default_factory=dict)
    opportunities: List[str] = field(default_factory=list)
    
    # Predictions
    estimated_time: int = 300        # Seconds
    files_affected: int = 0
    lines_changed: int = 0
    
    # Context
    reasoning: str = ""
    reasoning_steps: List[str] = field(default_factory=list)
    
    def is_safe(self, min_confidence: float = 0.7) -> bool:
        """Check if simulation result is safe to execute"""
        return self.will_succeed and self.confidence >= min_confidence
    
    def get_risk_score(self) -> float:
        """Calculate overall risk score (0-1)"""
        risk = 0.0
        
        # Higher risk if low confidence
        risk += (1.0 - self.confidence) * 0.3
        
        # Risk based on number of issues
        risk += min(len(self.potential_issues) * 0.1, 0.4)
        
        # Risk based on files affected
        risk += min(self.files_affected * 0.01, 0.3)
        
        return min(risk, 1.0)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'mission_id': self.mission_id,
            'mission_name': self.mission_name,
            'will_succeed': self.will_succeed,
            'confidence': self.confidence,
            'risk_score': self.get_risk_score(),
            'estimated_time': self.estimated_time,
            'files_affected': self.files_affected,
            'lines_changed': self.lines_changed,
            'potential_issues': self.potential_issues,
            'risks': self.risks,
            'opportunities': self.opportunities,
            'reasoning': self.reasoning,
        }


class SimulationEngine:
    """Engine for simulating mission outcomes"""
    
    def __init__(self):
        """Initialize simulation engine"""
        self.history: List[Tuple[str, SimulationResult]] = []
        self.accuracy_metrics: Dict = {}
    
    def simulate(self, mission_name: str, mission_state: Dict, 
                repo_context: Dict) -> SimulationResult:
        """
        Simulate a mission execution
        
        Args:
            mission_name: Name of the mission
            mission_state: Current state of mission
            repo_context: Repository context (dependencies, structure, etc.)
        
        Returns:
            SimulationResult with predictions
        """
        
        mission_id = mission_state.get('id', 'unknown')
        
        result = SimulationResult(
            mission_id=mission_id,
            mission_name=mission_name,
            will_succeed=False,
            confidence=0.5,
        )
        
        # Run appropriate simulation based on mission type
        mission_type = mission_state.get('type', 'custom')
        
        if mission_type == 'cleanup':
            result = self._simulate_cleanup(result, mission_state, repo_context)
        elif mission_type == 'refactor':
            result = self._simulate_refactor(result, mission_state, repo_context)
        elif mission_type == 'coverage_improvement':
            result = self._simulate_coverage(result, mission_state, repo_context)
        elif mission_type == 'type_improvement':
            result = self._simulate_types(result, mission_state, repo_context)
        elif mission_type == 'optimization':
            result = self._simulate_optimization(result, mission_state, repo_context)
        elif mission_type == 'security':
            result = self._simulate_security(result, mission_state, repo_context)
        else:
            result = self._simulate_custom(result, mission_state, repo_context)
        
        # Store in history
        self.history.append((mission_name, result))
        
        return result
    
    def _simulate_cleanup(self, result: SimulationResult, mission_state: Dict,
                         repo_context: Dict) -> SimulationResult:
        """Simulate dead code cleanup mission"""
        result.reasoning_steps.append("Analyzing code for dead code patterns")
        
        # Estimate changes
        dead_count = repo_context.get('estimated_dead_functions', 0)
        unused_count = repo_context.get('estimated_unused_imports', 0)
        
        result.files_affected = max(0, dead_count + unused_count) // 5
        result.lines_changed = result.files_affected * 20
        result.estimated_time = 300 + result.files_affected * 10
        
        # Assess success
        if dead_count > 0 or unused_count > 0:
            result.will_succeed = True
            result.confidence = 0.85  # High confidence in cleanup
            result.predicted_changes = {
                'functions_removed': dead_count,
                'imports_removed': unused_count,
            }
        else:
            result.will_succeed = False
            result.confidence = 0.5
            result.potential_issues.append("No dead code found")
        
        result.reasoning = f"Can remove ~{dead_count} dead functions and {unused_count} unused imports"
        
        return result
    
    def _simulate_refactor(self, result: SimulationResult, mission_state: Dict,
                          repo_context: Dict) -> SimulationResult:
        """Simulate refactoring mission"""
        result.reasoning_steps.append("Analyzing complex functions for refactoring")
        
        complex_functions = repo_context.get('high_complexity_functions', 0)
        
        result.files_affected = max(0, complex_functions) // 3
        result.lines_changed = result.files_affected * 50
        result.estimated_time = 600 + result.files_affected * 20
        
        if complex_functions > 0:
            result.will_succeed = True
            result.confidence = 0.75  # Medium-high (refactors are more risky)
            result.predicted_changes = {
                'functions_refactored': complex_functions,
                'complexity_reduced': 'yes',
            }
            result.risks['test_coverage'] = "Need to verify tests after refactoring"
        else:
            result.will_succeed = False
            result.confidence = 0.5
            result.potential_issues.append("No high-complexity functions found")
        
        result.reasoning = f"Can refactor ~{complex_functions} complex functions"
        
        return result
    
    def _simulate_coverage(self, result: SimulationResult, mission_state: Dict,
                          repo_context: Dict) -> SimulationResult:
        """Simulate test coverage improvement"""
        result.reasoning_steps.append("Analyzing uncovered code")
        
        uncovered_lines = repo_context.get('uncovered_lines', 0)
        coverage_gap = repo_context.get('coverage_gap', 0.0)
        
        # Estimate test additions
        tests_to_add = max(0, uncovered_lines // 20)
        
        result.files_affected = max(0, tests_to_add) // 10
        result.lines_changed = tests_to_add * 15
        result.estimated_time = 900 + tests_to_add * 5
        
        if coverage_gap > 0.0:
            result.will_succeed = True
            result.confidence = 0.8  # Good confidence in test addition
            result.predicted_changes = {
                'tests_added': tests_to_add,
                'coverage_increase': min(coverage_gap, 5.0),  # Estimate 5% increase
            }
            result.opportunities.append("Increase coverage from new tests")
        else:
            result.will_succeed = False
            result.confidence = 0.5
            result.potential_issues.append("Already has good coverage")
        
        result.reasoning = f"Can add ~{tests_to_add} tests to improve coverage"
        
        return result
    
    def _simulate_types(self, result: SimulationResult, mission_state: Dict,
                       repo_context: Dict) -> SimulationResult:
        """Simulate type hint addition"""
        result.reasoning_steps.append("Analyzing untyped functions")
        
        untyped_functions = repo_context.get('untyped_functions', 0)
        
        result.files_affected = max(0, untyped_functions) // 20
        result.lines_changed = untyped_functions * 2
        result.estimated_time = 400 + untyped_functions * 2
        
        if untyped_functions > 0:
            result.will_succeed = True
            result.confidence = 0.9  # Very high confidence - type hints aren't risky
            result.predicted_changes = {
                'functions_typed': untyped_functions,
            }
            result.opportunities.append("Improve code clarity with type hints")
            result.opportunities.append("Enable better IDE support")
        else:
            result.will_succeed = False
            result.confidence = 0.5
            result.potential_issues.append("All functions already typed")
        
        result.reasoning = f"Can add type hints to ~{untyped_functions} functions"
        
        return result
    
    def _simulate_optimization(self, result: SimulationResult, mission_state: Dict,
                              repo_context: Dict) -> SimulationResult:
        """Simulate performance optimization"""
        result.reasoning_steps.append("Analyzing performance bottlenecks")
        
        bottlenecks = repo_context.get('performance_bottlenecks', 0)
        
        result.files_affected = max(0, bottlenecks) // 2
        result.lines_changed = result.files_affected * 30
        result.estimated_time = 1200 + result.files_affected * 50
        
        if bottlenecks > 0:
            result.will_succeed = True
            result.confidence = 0.7  # Medium confidence - optimizations need testing
            result.predicted_changes = {
                'bottlenecks_optimized': bottlenecks,
                'expected_speedup': '10-30%',
            }
            result.risks['performance'] = "Changes may affect performance in unexpected ways"
            result.risks['maintainability'] = "Optimized code may be harder to understand"
        else:
            result.will_succeed = False
            result.confidence = 0.5
            result.potential_issues.append("No identified performance bottlenecks")
        
        result.reasoning = f"Can optimize ~{bottlenecks} performance bottlenecks"
        
        return result
    
    def _simulate_security(self, result: SimulationResult, mission_state: Dict,
                          repo_context: Dict) -> SimulationResult:
        """Simulate security improvements"""
        result.reasoning_steps.append("Analyzing security issues")
        
        vulnerabilities = repo_context.get('vulnerabilities', 0)
        
        result.files_affected = max(0, vulnerabilities)
        result.lines_changed = result.files_affected * 15
        result.estimated_time = 500 + result.files_affected * 50
        
        if vulnerabilities > 0:
            result.will_succeed = True
            result.confidence = 0.95  # Very high confidence - security fixes are clear
            result.predicted_changes = {
                'vulnerabilities_fixed': vulnerabilities,
            }
            result.opportunities.append("Reduce security risk")
        else:
            result.will_succeed = False
            result.confidence = 0.5
            result.potential_issues.append("No identified vulnerabilities")
        
        result.reasoning = f"Can fix ~{vulnerabilities} security vulnerabilities"
        
        return result
    
    def _simulate_custom(self, result: SimulationResult, mission_state: Dict,
                        repo_context: Dict) -> SimulationResult:
        """Simulate custom mission"""
        result.reasoning_steps.append("Analyzing custom mission")
        result.will_succeed = True
        result.confidence = 0.5  # Conservative for unknown missions
        result.files_affected = 5
        result.lines_changed = 50
        result.estimated_time = 600
        
        result.reasoning = "Custom mission - using conservative estimates"
        
        return result
    
    def get_accuracy(self, mission_name: str) -> Optional[Tuple[float, int]]:
        """Get accuracy metrics for a mission type"""
        key = mission_name
        if key in self.accuracy_metrics:
            return self.accuracy_metrics[key]
        return None
    
    def record_execution(self, mission_name: str, simulation: SimulationResult,
                        actual_result: Dict) -> None:
        """Record actual execution result to improve accuracy"""
        
        predicted = simulation.will_succeed
        actual = actual_result.get('success', False)
        
        key = mission_name
        if key not in self.accuracy_metrics:
            self.accuracy_metrics[key] = (0.0, 0)
        
        accuracy, count = self.accuracy_metrics[key]
        
        # Update running average
        correct = 1 if predicted == actual else 0
        new_accuracy = (accuracy * count + correct) / (count + 1)
        
        self.accuracy_metrics[key] = (new_accuracy, count + 1)
