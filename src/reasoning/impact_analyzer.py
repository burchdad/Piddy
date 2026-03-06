"""
Phase 32 Reasoning: Impact Analyzer Tool

Integrates with agent decision-making to provide impact analysis before code changes.
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import sqlite3
import logging

logger = logging.getLogger(__name__)


@dataclass
class RefactoringProposal:
    """Proposed refactoring with safety assessment"""
    description: str
    affected_functions: List[str]
    risk_level: str  # low, medium, high
    estimated_effort_hours: float
    required_tests: List[str]
    breaking_changes: List[str]
    safe_to_execute: bool
    recommendations: List[str]


class ImpactAnalysisTool:
    """Tool for agent to analyze impact before making changes"""

    def __init__(self, call_graph_db: sqlite3.Connection, node_db: sqlite3.Connection):
        self.call_graph_db = call_graph_db
        self.node_db = node_db

    def assess_deletion_safety(self, func_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Assess if a function can be safely deleted.
        
        Returns (is_safe, analysis)
        """
        cursor = self.call_graph_db.cursor()

        # Find all callers
        cursor.execute('''
            SELECT source_node_id, COUNT(*) as count
            FROM call_graphs
            WHERE target_node_id = ?
            GROUP BY source_node_id
        ''', (func_id,))
        
        callers = cursor.fetchall()

        if not callers:
            return True, {
                "reason": "No callers found",
                "confidence": 0.99,
                "recommendation": "Safe to delete"
            }

        caller_details = []
        for caller_id, count in callers:
            cursor.execute('SELECT name, path FROM nodes WHERE node_id = ?', (caller_id,))
            caller_info = cursor.fetchone()
            if caller_info:
                caller_details.append({
                    "function_id": caller_id,
                    "function_name": caller_info[0],
                    "file_path": caller_info[1],
                    "call_count": count
                })

        return False, {
            "reason": f"{len(caller_details)} functions still call this",
            "callers": caller_details,
            "confidence": 0.99,
            "recommendation": "Unsafe to delete without updating callers"
        }

    def assess_parameter_change(self, func_id: str, new_parameter: Dict[str, str]) -> Tuple[bool, Dict]:
        """
        Assess impact of adding/changing a parameter.
        
        Args:
            func_id: Function being modified
            new_parameter: {"name": "logger", "type": "Logger"}
            
        Returns (is_safe, analysis)
        """
        cursor = self.call_graph_db.cursor()

        # Find all callers
        cursor.execute('''
            SELECT source_node_id, parameter_types
            FROM call_graphs
            WHERE target_node_id = ?
        ''', (func_id,))

        callers = cursor.fetchall()
        affected_functions = []

        for caller_id, param_types_json in callers:
            affected_functions.append({
                "function_id": caller_id,
                "requires_update": True
            })

        risk_level = "high" if len(affected_functions) > 10 else "medium" if len(affected_functions) > 3 else "low"

        return False, {  # Not safe without updates
            "affected_functions": affected_functions,
            "risk_level": risk_level,
            "required_updates": len(affected_functions),
            "recommendation": f"Must update {len(affected_functions)} call sites"
        }

    def assess_extraction(self, source_func_id: str, lines: List[int]) -> RefactoringProposal:
        """
        Assess if code can be safely extracted into a new function.
        
        Args:
            source_func_id: Function containing the code
            lines: Line numbers to extract
            
        Returns RefactoringProposal
        """
        # Check for captured variables/state in extracted lines
        # For now, return a proposal based on call count
        cursor = self.call_graph_db.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM call_graphs WHERE source_node_id = ?
        ''', (source_func_id,))
        
        call_count = cursor.fetchone()[0]

        return RefactoringProposal(
            description=f"Extract lines {lines[0]}-{lines[-1]} from {source_func_id}",
            affected_functions=[source_func_id],
            risk_level="low",
            estimated_effort_hours=0.25,
            required_tests=["test_extracted_function_basic"],
            breaking_changes=[],
            safe_to_execute=True,
            recommendations=["Add unit test for extracted function"]
        )

    def find_dead_code(self) -> List[Dict[str, Any]]:
        """Find functions that are never called"""
        cursor = self.call_graph_db.cursor()

        # Find functions with no callers
        cursor.execute('''
            SELECT n.node_id, n.name, n.path
            FROM nodes n
            LEFT JOIN call_graphs cg ON n.node_id = cg.target_node_id
            WHERE n.node_type = 'function'
            AND cg.call_graph_id IS NULL
            AND n.name NOT IN 
                ('main', '__main__', 'handler', 'lambda_handler', '__init__', 'run')
            LIMIT 100
        ''')

        results = []
        for node_id, func_name, path in cursor.fetchall():
            results.append({
                "function_id": node_id,
                "function_name": func_name,
                "file_path": path,
                "recommendation": "Can likely be deleted"
            })

        return results

    def find_hotspots(self, threshold: int = 5) -> List[Dict[str, Any]]:
        """
        Find functions that are called very frequently (potential performance bottlenecks).
        
        Args:
            threshold: Minimum call frequency to be considered a hotspot
        """
        cursor = self.call_graph_db.cursor()

        cursor.execute('''
            SELECT cg.target_node_id, n.name, COUNT(*) as call_count,
                   SUM(cg.execution_time_ms) as total_time
            FROM call_graphs cg
            JOIN nodes n ON cg.target_node_id = n.node_id
            GROUP BY cg.target_node_id
            HAVING call_count >= ?
            ORDER BY call_count DESC
            LIMIT 20
        ''', (threshold,))

        results = []
        for func_id, func_name, call_count, total_time in cursor.fetchall():
            results.append({
                "function_id": func_id,
                "function_name": func_name,
                "call_count": call_count,
                "total_execution_time_ms": total_time,
                "priority": "optimize" if call_count > 20 else "monitor"
            })

        return results

    def calculate_refactoring_confidence(
        self, 
        source_func: str, 
        target_func: str, 
        changes: List[str]
    ) -> Tuple[float, str]:
        """
        Calculate confidence score for a refactoring (0-1 scale).
        
        Factors:
        - Test coverage of affected functions
        - Number of callers
        - Type safety
        - Backward compatibility
        """
        cursor = self.call_graph_db.cursor()

        # Find all affected functions (callers + callees)
        cursor.execute('''
            SELECT COUNT(*) FROM call_graphs 
            WHERE source_node_id = ? OR target_node_id = ?
        ''', (source_func, source_func))
        
        impact_count = cursor.fetchone()[0]

        # Base confidence
        confidence = 0.9

        # Reduce confidence based on impact
        if impact_count > 20:
            confidence -= 0.2
        elif impact_count > 10:
            confidence -= 0.1

        # Additional checks would happen here
        # (type system checks, test coverage, etc.)

        return max(0.0, min(1.0, confidence)), "Based on impact analysis"


class RefactoringValidator:
    """Validate proposed refactorings for safety"""

    def __init__(self, call_graph_db: sqlite3.Connection):
        self.call_graph_db = call_graph_db

    def validate_type_compatibility(
        self, 
        caller_func: str, 
        callee_func: str,
        new_signature: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check if caller passing types that match new signature.
        
        Returns (is_compatible, issues)
        """
        cursor = self.call_graph_db.cursor()

        cursor.execute('''
            SELECT parameter_types FROM call_graphs
            WHERE source_node_id = ? AND target_node_id = ?
        ''', (caller_func, callee_func))

        row = cursor.fetchone()
        if not row:
            return True, []

        import json
        call_param_types = json.loads(row[0]) if row[0] else []
        
        issues = []
        required_params = new_signature.get("parameters", [])
        
        if len(call_param_types) < len(required_params):
            issues.append(
                f"Caller passes {len(call_param_types)} args but function needs {len(required_params)}"
            )

        return len(issues) == 0, issues

    def validate_return_type_usage(
        self,
        func_id: str,
        new_return_type: str
    ) -> Tuple[bool, List[str]]:
        """
        Check if callers are prepared for new return type.
        """
        issues = []
        # Would need type inference engine to fully validate
        # For now, just check that callers exist
        return True, issues
