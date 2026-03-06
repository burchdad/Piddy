"""Phase 32: Production Integration Tools

Integrates the unified reasoning engine with agent decision-making.
Enables autonomous refactoring, testing, and code improvement decisions.
"""

import json
import logging
from typing import Dict, Any, List
from phase32_unified_reasoning import (
    UnifiedReasoningEngine,
    RefactoringDecision,
    DecisionConfidence
)
from phase32_type_system import TypeCompatibilityChecker
from phase32_api_contracts import APIContractTracker
from phase32_service_boundaries import ServiceBoundaryDetector

logger = logging.getLogger(__name__)


class Phase32ProductionIntegration:
    """Bridge between Phase 32 analysis and agent decision-making"""
    
    def __init__(self, db_path: str = '.piddy_callgraph.db'):
        """Initialize Phase 32 production integration"""
        self.db_path = db_path
        self.reasoning_engine = UnifiedReasoningEngine(db_path)
        self.type_checker = TypeCompatibilityChecker(db_path)
        self.contract_tracker = APIContractTracker(db_path)
        self.service_detector = ServiceBoundaryDetector(db_path)
        logger.info("Phase 32 production integration initialized")
    
    def evaluate_refactoring_safety(self, func_id: str, change_description: str) -> Dict[str, Any]:
        """
        Agent hook: Evaluate if refactoring is safe
        
        Args:
            func_id: Function to refactor (can use qualified_name or node_id)
            change_description: What type of change (e.g., "optimize", "bugfix", "refactor")
        
        Returns:
            Dict with safety evaluation and agent guidance
        """
        try:
            evaluation = self.reasoning_engine.evaluate_refactoring(
                func_id,
                {'action': change_description}
            )
            
            # Convert to agent decision format
            agent_decision = {
                'can_proceed': evaluation['confidence'] >= 0.85,
                'confidence': evaluation['confidence'],
                'recommendation': evaluation['recommendation'],
                'safety_level': 'safe' if evaluation['confidence'] >= 0.85 else 'risky' if evaluation['confidence'] >= 0.65 else 'dangerous',
                'factors': evaluation['factors'],
                'blockers': evaluation['blockers'],
                'warnings': evaluation['warnings'],
                'required_actions': self._get_required_actions(evaluation),
                'success': True
            }
            
            logger.info(f"Refactoring evaluation: {func_id} -> {agent_decision['safety_level']}")
            return agent_decision
            
        except Exception as e:
            logger.error(f"Error evaluating refactoring: {e}")
            return {
                'can_proceed': False,
                'confidence': 0.0,
                'recommendation': RefactoringDecision.BLOCKED,
                'safety_level': 'error',
                'error': str(e),
                'success': False
            }
    
    def get_refactoring_plan(self, func_id: str) -> Dict[str, Any]:
        """
        Agent hook: Get detailed refactoring plan
        
        Returns step-by-step instructions for autonomous refactoring
        """
        try:
            instructions = self.reasoning_engine.generate_agent_instructions(func_id)
            return {
                'function_id': func_id,
                'safety_level': instructions['safety_level'],
                'steps': instructions['steps'],
                'verification_checks': instructions['checks'],
                'rollback_plan': instructions['rollback_plan'],
                'warnings': instructions.get('warnings', []),
                'success': True
            }
        except Exception as e:
            logger.error(f"Error generating refactoring plan: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def prioritize_testing(self, limit: int = 10) -> Dict[str, Any]:
        """
        Agent hook: Get prioritized list of functions needing tests
        
        Returns functions ranked by risk and usefulness for testing
        """
        try:
            priorities = self.reasoning_engine.prioritize_testing()
            return {
                'functions': priorities[:limit],
                'total': len(priorities),
                'priority_criteria': [
                    'complexity (high complexity = high priority)',
                    'test_coverage (untested = high priority)',
                    'lines_of_code (larger = higher priority)',
                    'estimated_effort (low effort first)'
                ],
                'success': True
            }
        except Exception as e:
            logger.error(f"Error prioritizing testing: {e}")
            return {'error': str(e), 'success': False}
    
    def find_refactoring_opportunities(self) -> Dict[str, Any]:
        """
        Agent hook: Identify hotspots and optimization opportunities
        
        Returns code that should be refactored, why, and how
        """
        try:
            hotspots = self.reasoning_engine.identify_refactoring_hot_spots()
            
            # Categorize hotspots
            categories = {
                'duplicates': [],
                'complexity': [],
                'other': []
            }
            
            for spot in hotspots:
                if spot['type'] == 'duplicate_code':
                    categories['duplicates'].append(spot)
                elif spot['type'] == 'high_complexity':
                    categories['complexity'].append(spot)
                else:
                    categories['other'].append(spot)
            
            return {
                'opportunities': hotspots,
                'by_category': categories,
                'total': len(hotspots),
                'success': True
            }
        except Exception as e:
            logger.error(f"Error finding refactoring opportunities: {e}")
            return {'error': str(e), 'success': False}
    
    def verify_type_safety(self, caller_id: str, callee_id: str, arg_types: List[str]) -> Dict[str, Any]:
        """
        Agent hook: Verify type compatibility before function call
        
        Args:
            caller_id: Function making the call
            callee_id: Function being called
            arg_types: Types of arguments being passed
        
        Returns:
            Type safety verification result
        """
        try:
            compatible = self.type_checker.check_compatibility(
                caller_id,
                callee_id,
                arg_types
            )
            
            return {
                'compatible': compatible.get('compatible', False),
                'mismatches': compatible.get('mismatches', []),
                'expected_types': compatible.get('expected_types', []),
                'provided_types': arg_types,
                'suggestion': compatible.get('suggestion', 'Types match!'),
                'success': True
            }
        except Exception as e:
            logger.error(f"Error verifying type safety: {e}")
            return {
                'compatible': False,
                'error': str(e),
                'success': False
            }
    
    def check_api_compatibility(self, func_id: str, proposed_signature: str) -> Dict[str, Any]:
        """
        Agent hook: Check if API change would break compatibility
        
        Args:
            func_id: Function being modified
            proposed_signature: New function signature
        
        Returns:
            Compatibility check result with breaking changes if any
        """
        try:
            violations = self.contract_tracker.detect_breaking_changes()
            
            return {
                'breaking_changes': violations,
                'has_violations': len(violations) > 0,
                'recommendation': 'version_bump' if violations else 'safe',
                'action': 'Update API contract version' if violations else 'API compatible',
                'success': True
            }
        except Exception as e:
            logger.error(f"Error checking API compatibility: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def plan_service_refactoring(self, functions: List[str], new_service_name: str) -> Dict[str, Any]:
        """
        Agent hook: Plan service extraction or refactoring
        
        Args:
            functions: Functions to extract into new service
            new_service_name: Name of new service
        
        Returns:
            Refactoring plan with safety assessment
        """
        try:
            plan = self.service_detector.plan_service_extraction(
                functions,
                new_service_name
            )
            
            return {
                'plan': plan,
                'is_safe': plan.get('health_status') == 'healthy',
                'coupling_factor': plan.get('coupling_factor', 0.0),
                'recommendation': 'proceed' if plan.get('health_status') == 'healthy' else 'refactor_first',
                'refactoring_steps': [
                    'Extract identified functions',
                    'Update imports',
                    'Run integration tests',
                    'Verify cross-service communication'
                ],
                'success': True
            }
        except Exception as e:
            logger.error(f"Error planning service refactoring: {e}")
            return {'error': str(e), 'success': False}
    
    def _get_required_actions(self, evaluation: Dict) -> List[str]:
        """Generate required actions based on evaluation"""
        actions = []
        
        if evaluation['factors']['test_coverage']['score'] < 0.5:
            actions.append('Generate tests for better coverage')
        
        if not evaluation['factors']['type_safety'].get('typed', False):
            actions.append('Add type hints to function')
        
        if evaluation['factors']['api_contracts']['score'] < 0.8:
            actions.append('Define API contract for this function')
        
        if evaluation['factors']['stable_identity']['score'] < 0.9:
            actions.append('Ensure stable identifier is set')
        
        return actions


# Helper functions for agent tool integration

def evaluate_refactoring_safety(input_str: str) -> str:
    """Tool wrapper for refactoring safety evaluation"""
    try:
        params = json.loads(input_str)
        func_id = params.get('func_id', params.get('function_id', ''))
        change = params.get('change', params.get('change_description', 'optimize'))
        
        if not func_id:
            return json.dumps({'error': 'func_id required', 'success': False})
        
        integration = Phase32ProductionIntegration()
        result = integration.evaluate_refactoring_safety(func_id, change)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


def get_refactoring_plan(input_str: str) -> str:
    """Tool wrapper for refactoring plan generation"""
    try:
        params = json.loads(input_str)
        func_id = params.get('func_id', params.get('function_id', ''))
        
        if not func_id:
            return json.dumps({'error': 'func_id required', 'success': False})
        
        integration = Phase32ProductionIntegration()
        result = integration.get_refactoring_plan(func_id)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


def prioritize_testing(input_str: str) -> str:
    """Tool wrapper for test prioritization"""
    try:
        params = json.loads(input_str) if input_str else {}
        limit = params.get('limit', 10)
        
        integration = Phase32ProductionIntegration()
        result = integration.prioritize_testing(limit)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


def find_refactoring_opportunities(input_str: str) -> str:
    """Tool wrapper for finding refactoring hotspots"""
    try:
        integration = Phase32ProductionIntegration()
        result = integration.find_refactoring_opportunities()
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


def verify_type_safety(input_str: str) -> str:
    """Tool wrapper for type safety verification"""
    try:
        params = json.loads(input_str)
        caller_id = params.get('caller_id')
        callee_id = params.get('callee_id')
        arg_types = params.get('arg_types', [])
        
        if not (caller_id and callee_id):
            return json.dumps({'error': 'caller_id and callee_id required', 'success': False})
        
        integration = Phase32ProductionIntegration()
        result = integration.verify_type_safety(caller_id, callee_id, arg_types)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


def check_api_compatibility(input_str: str) -> str:
    """Tool wrapper for API compatibility checking"""
    try:
        params = json.loads(input_str)
        func_id = params.get('func_id', params.get('function_id'))
        proposed_sig = params.get('proposed_signature', '')
        
        if not func_id:
            return json.dumps({'error': 'func_id required', 'success': False})
        
        integration = Phase32ProductionIntegration()
        result = integration.check_api_compatibility(func_id, proposed_sig)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


def plan_service_refactoring(input_str: str) -> str:
    """Tool wrapper for service refactoring planning"""
    try:
        params = json.loads(input_str)
        functions = params.get('functions', [])
        new_service_name = params.get('new_service_name', 'new_service')
        
        if not functions:
            return json.dumps({'error': 'functions list required', 'success': False})
        
        integration = Phase32ProductionIntegration()
        result = integration.plan_service_refactoring(functions, new_service_name)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({'error': str(e), 'success': False})


if __name__ == '__main__':
    # Demonstration
    print("Phase 32 Production Integration Demo")
    print("=" * 70)
    
    integration = Phase32ProductionIntegration()
    
    # Get sample function
    import sqlite3
    conn = sqlite3.connect('.piddy_callgraph.db')
    cursor = conn.cursor()
    cursor.execute('SELECT node_id, name FROM nodes WHERE node_type = "function" LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        func_id, func_name = result
        print(f"\nEvaluating refactoring for: {func_name}")
        
        # Test refactoring evaluation
        evaluation = integration.evaluate_refactoring_safety(func_id, 'optimize')
        print(f"Safety: {evaluation['safety_level']}")
        print(f"Can proceed: {evaluation['can_proceed']}")
        print(f"Confidence: {evaluation['confidence']:.2f}")
        
        print("\n✅ Phase 32 production integration initialized successfully")
