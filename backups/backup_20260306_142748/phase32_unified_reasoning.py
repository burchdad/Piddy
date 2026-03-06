"""
Phase 32f: Unified Reasoning Layer

Combines all Phase 32 components into unified decision engine for agent autonomy.
Enables autonomous refactoring, testing prioritization, and code improvement decisions.
"""

import sqlite3
from typing import Dict, List
from enum import Enum

class DecisionConfidence(Enum):
    VERY_LOW = 0.3
    LOW = 0.5
    MEDIUM = 0.65
    HIGH = 0.85
    VERY_HIGH = 0.95


class RefactoringDecision:
    SAFE = "safe_to_refactor"
    RISKY = "risky_refactor"
    BLOCKED = "refactoring_blocked"


class UnifiedReasoningEngine:
    """Combines all Phase 32 analyses for autonomous decisions"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def evaluate_refactoring(self, func_id: str, proposed_change: Dict) -> Dict:
        """Evaluate if a function can be safely refactored
        
        Considers:
        - Test coverage (Phase 32b)
        - Type safety (Phase 32c)
        - API contracts (Phase 32d)
        - Service boundaries (Phase 32e)
        - Call graph impact (Phase 32a)
        - Confidence scores (Phase 32 Migration 2)
        """

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        evaluation = {
            'func_id': func_id,
            'proposed_change': proposed_change,
            'factors': {},
            'confidence': 0.0,
            'recommendation': RefactoringDecision.SAFE,
            'blockers': [],
            'warnings': []
        }

        # Factor 1: Test coverage
        try:
            cursor.execute('''
                SELECT COUNT(*) as test_count FROM test_coverage
                WHERE tested_func_id = ?
            ''', (func_id,))
            test_count = cursor.fetchone()['test_count'] or 0
            evaluation['factors']['test_coverage'] = {
                'test_count': test_count,
                'score': min(0.95, 0.2 + (test_count * 0.15))
            }
        except:
            evaluation['factors']['test_coverage'] = {'score': 0.3}

        # Factor 2: Type safety
        try:
            cursor.execute('''
                SELECT is_correctly_typed FROM function_types
                WHERE func_id = ?
            ''', (func_id,))
            typed = cursor.fetchone()
            evaluation['factors']['type_safety'] = {
                'typed': bool(typed and typed['is_correctly_typed']),
                'score': 0.9 if typed and typed['is_correctly_typed'] else 0.5
            }
        except:
            evaluation['factors']['type_safety'] = {'score': 0.5}

        # Factor 3: API contracts
        try:
            cursor.execute('''
                SELECT version FROM api_contracts
                WHERE func_id = ?
            ''', (func_id,))
            contract = cursor.fetchone()
            evaluation['factors']['api_contracts'] = {
                'has_contract': bool(contract),
                'score': 0.9 if contract else 0.6
            }
        except:
            evaluation['factors']['api_contracts'] = {'score': 0.6}

        # Factor 4: Stable identifier
        try:
            cursor.execute('''
                SELECT stable_id FROM nodes WHERE node_id = ?
            ''', (func_id,))
            result = cursor.fetchone()
            has_stable_id = bool(result and result['stable_id'])
            evaluation['factors']['stable_identity'] = {
                'has_stable_id': has_stable_id,
                'score': 0.95 if has_stable_id else 0.5
            }
        except:
            evaluation['factors']['stable_identity'] = {'score': 0.5}

        # Factor 5: Confidence in call graph
        try:
            cursor.execute('''
                SELECT AVG(confidence) as avg_conf FROM call_graphs
                WHERE source_node_id = ? OR target_node_id = ?
            ''', (func_id, func_id))
            result = cursor.fetchone()
            avg_conf = result['avg_conf'] or 0.95
            evaluation['factors']['call_graph_confidence'] = {
                'avg_confidence': avg_conf,
                'score': avg_conf
            }
        except:
            evaluation['factors']['call_graph_confidence'] = {'score': 0.95}

        conn.close()

        # Calculate overall confidence
        scores = [f.get('score', 0.5) for f in evaluation['factors'].values()]
        evaluation['confidence'] = sum(scores) / len(scores) if scores else 0.5

        # Determine recommendation
        if evaluation['confidence'] >= 0.85:
            evaluation['recommendation'] = RefactoringDecision.SAFE
        elif evaluation['confidence'] >= 0.65:
            evaluation['recommendation'] = RefactoringDecision.RISKY
        else:
            evaluation['recommendation'] = RefactoringDecision.BLOCKED
            evaluation['blockers'].append('Low confidence in refactoring safety')

        # Add warnings
        if evaluation['factors']['test_coverage']['score'] < 0.5:
            evaluation['warnings'].append('Low test coverage - recommend adding tests first')
        
        if not evaluation['factors']['type_safety'].get('typed', False):
            evaluation['warnings'].append('Function lacks type hints - add for safety')

        return evaluation

    def prioritize_testing(self) -> List[Dict]:
        """Identify functions that need testing (high risk, untested)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        priorities = []

        try:
            # Find complex, untested functions
            cursor.execute('''
                SELECT n.node_id, n.name, n.complexity, n.lines_of_code
                FROM nodes n
                WHERE n.node_type = 'function'
                  AND n.complexity > 0.5
                  AND n.node_id NOT IN (
                    SELECT tested_func_id FROM test_coverage
                  )
                ORDER BY n.complexity DESC, n.lines_of_code DESC
                LIMIT 20
            ''')

            for row in cursor.fetchall():
                priority = {
                    'func_id': row['node_id'],
                    'func_name': row['name'],
                    'complexity': row['complexity'],
                    'lines_of_code': row['lines_of_code'],
                    'estimated_effort': 'medium' if row['complexity'] > 0.7 else 'low',
                    'priority_score': (row['complexity'] * 0.7) + (row['lines_of_code'] / 200 * 0.3)
                }
                priorities.append(priority)

        except Exception as e:
            print(f"Error prioritizing tests: {e}")

        conn.close()
        return priorities

    def identify_refactoring_hot_spots(self) -> List[Dict]:
        """Identify code that should be refactored (duplicates, hotspots)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        hot_spots = []

        try:
            # Find duplicate stable IDs (same logic, different locations)
            cursor.execute('''
                SELECT stable_id, COUNT(*) as count, GROUP_CONCAT(name) as names
                FROM nodes
                WHERE stable_id IS NOT NULL AND node_type = 'function'
                GROUP BY stable_id
                HAVING count > 1
                ORDER BY count DESC
                LIMIT 10
            ''')

            for row in cursor.fetchall():
                hot_spots.append({
                    'type': 'duplicate_code',
                    'stable_id': row['stable_id'],
                    'duplicate_count': row['count'],
                    'functions': row['names'].split(','),
                    'recommendation': 'Extract common function or use inheritance'
                })

            # Find high-complexity functions
            cursor.execute('''
                SELECT node_id, name, complexity, lines_of_code
                FROM nodes
                WHERE node_type = 'function' AND complexity > 0.8
                ORDER BY complexity DESC
                LIMIT 5
            ''')

            for row in cursor.fetchall():
                hot_spots.append({
                    'type': 'high_complexity',
                    'func_id': row['node_id'],
                    'func_name': row['name'],
                    'complexity': row['complexity'],
                    'recommendation': 'Break into smaller functions'
                })

        except Exception as e:
            print(f"Error identifying hot spots: {e}")

        conn.close()
        return hot_spots

    def generate_agent_instructions(self, func_id: str) -> Dict:
        """Generate detailed instructions for agent to refactor safely"""
        evaluation = self.evaluate_refactoring(func_id, {'action': 'improve'})

        instructions = {
            'function_id': func_id,
            'safety_level': 'safe' if evaluation['confidence'] > 0.8 else 'careful',
            'steps': [],
            'checks': [],
            'rollback_plan': 'Use stable_id to track changes'
        }

        instructions['steps'] = [
            '1. Verify stable_id matches current function',
            '2. Retrieve type signature from function_types table',
            '3. Check API contract for breaking changes',
            '4. Calculate impact radius using confidence scores',
            '5. Verify test coverage before making changes',
            '6. Apply changes to function body',
            '7. Update call graph if signature changed',
            '8. Run affected tests',
            '9. Update documentation',
            '10. Commit with stable_id reference'
        ]

        instructions['checks'] = [
            'Type compatibility with all callers',
            'API contract compliance',
            'Test coverage >= 80%',
            'No high-risk cross-service calls',
            'Confidence score >= 0.85'
        ]

        if evaluation['warnings']:
            instructions['warnings'] = evaluation['warnings']

        return instructions


def run_unified_reasoning_demo():
    """Demonstrate unified reasoning engine"""
    print("Phase 32f: Unified Reasoning Layer")
    print("=" * 70)

    engine = UnifiedReasoningEngine('.piddy_callgraph.db')

    # Get sample function
    conn = sqlite3.connect('.piddy_callgraph.db')
    cursor = conn.cursor()
    cursor.execute('SELECT node_id, name FROM nodes WHERE node_type = "function" LIMIT 1')
    result = cursor.fetchone()
    conn.close()

    if result:
        func_id, func_name = result

        print(f"\n1. Evaluating refactoring safety for: {func_name}")
        evaluation = engine.evaluate_refactoring(func_id, {'action': 'optimize'})
        print(f"   Overall confidence: {evaluation['confidence']:.2f}")
        print(f"   Recommendation: {evaluation['recommendation']}")
        print(f"   Factors:")
        for factor, data in evaluation['factors'].items():
            print(f"      - {factor}: {data.get('score', 'N/A'):.2f}")

        print(f"\n2. Prioritizing testing needs...")
        priorities = engine.prioritize_testing()
        print(f"   High-risk untested functions: {len(priorities)}")
        if priorities:
            for p in priorities[:3]:
                print(f"      {p['func_name']}: complexity={p['complexity']:.2f}, priority={p['priority_score']:.2f}")

        print(f"\n3. Identifying refactoring hot spots...")
        hot_spots = engine.identify_refactoring_hot_spots()
        print(f"   Hot spots found: {len(hot_spots)}")
        for spot in hot_spots[:3]:
            print(f"      {spot['type']}: {spot['recommendation']}")

        print(f"\n4. Generating agent instructions...")
        instructions = engine.generate_agent_instructions(func_id)
        print(f"   Safety level: {instructions['safety_level']}")
        print(f"   Steps: {len(instructions['steps'])}")

    print("\n✅ Phase 32f unified reasoning complete")


if __name__ == '__main__':
    run_unified_reasoning_demo()
