"""
Phase 32 Agent Tools: Call Graph Integration

Tools for agents to use call graphs in their decision-making.
Enables safe refactoring, impact analysis, and architecture-aware code changes.
"""

from typing import Dict, List, Any, Tuple, Optional
import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


def get_function_impact(func_id: str, db_path: str) -> Dict[str, Any]:
    """
    Tool: Get impact of changes to a function.
    
    Usage by agent:
        impact = get_function_impact("func_123", db_path)
        if impact['risk_level'] == 'low':
            agent.proceed_with_refactoring()
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get direct callers
        cursor.execute('''
            SELECT COUNT(*) as count FROM call_graphs WHERE target_node_id = ?
        ''', (func_id,))
        direct_callers = cursor.fetchone()['count']

        # Get functions called by this function
        cursor.execute('''
            SELECT COUNT(*) as count FROM call_graphs WHERE source_node_id = ?
        ''', (func_id,))
        Functions_called = cursor.fetchone()['count']

        # Check if function is recursive
        cursor.execute('''
            SELECT is_recursive FROM call_graphs 
            WHERE source_node_id = ? AND target_node_id = ?
            LIMIT 1
        ''', (func_id, func_id))
        recursive_row = cursor.fetchone()
        is_recursive = recursive_row['is_recursive'] if recursive_row else 0

        # Get test coverage (would come from test_coverage table in Phase 32e)
        # For now, return 0
        test_coverage = 0

        conn.close()

        risk_level = "high" if direct_callers > 10 else "medium" if direct_callers > 3 else "low"

        return {
            "function_id": func_id,
            "direct_callers": direct_callers,
            "functions_called": Functions_called,
            "is_recursive": bool(is_recursive),
            "test_coverage_percent": test_coverage,
            "risk_level": risk_level,
            "safe_to_refactor": risk_level == "low",
            "safe_to_delete": direct_callers == 0,
            "recommendation": f"Risk: {risk_level.upper()} - {direct_callers} direct callers"
        }
    except Exception as e:
        logger.error(f"Error getting function impact: {e}")
        return {"error": str(e), "safe_to_refactor": False}


def check_breaking_change(
    source_func_id: str,
    parameter_changes: Dict[str, Any],
    db_path: str
) -> Dict[str, Any]:
    """
    Tool: Check if parameter changes would break callers.
    
    Usage by agent:
        breaking = check_breaking_change(
            source_func_id="func_123",
            parameter_changes={"added": ["logger"], "removed": [], "changed": []},
            db_path="/path/to/graph.db"
        )
        if breaking['is_breaking']:
            agent.suggest_alternative()
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT source_node_id FROM call_graphs WHERE target_node_id = ?
        ''', (source_func_id,))
        
        callers = [row[0] for row in cursor.fetchall()]
        conn.close()

        is_breaking = len(parameter_changes.get("removed", [])) > 0 or \
                     len(parameter_changes.get("changed", [])) > 0

        return {
            "is_breaking": is_breaking,
            "affected_callers": len(callers),
            "caller_list": callers if len(callers) < 20 else callers[:20],
            "recommendation": (
                "Breaking change - requires updates to all callers" 
                if is_breaking 
                else "Non-breaking - callers unaffected"
            )
        }
    except Exception as e:
        logger.error(f"Error checking breaking change: {e}")
        return {"error": str(e), "is_breaking": True}


def find_safe_extraction_points(
    source_func_id: str,
    lines_to_extract: List[int],
    db_path: str
) -> Dict[str, Any]:
    """
    Tool: Find if code extraction is safe.
    
    Usage by agent:
        safe_points = find_safe_extraction_points(
            source_func_id="func_123",
            lines_to_extract=[10, 11, 12, 13, 14],
            db_path="/path/to/graph.db"
        )
        if safe_points['can_extract']:
            new_func = agent.create_function(lines, name="extracted_helper")
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get function metadata
        cursor.execute('''
            SELECT source_node_id, target_node_id FROM call_graphs 
            WHERE source_node_id = ?
        ''', (source_func_id,))
        
        functions_called = [row[1] for row in cursor.fetchall()]

        # In a full implementation, would analyze captured variables
        # For now, base decision on call complexity
        can_extract = len(functions_called) < 5

        conn.close()

        return {
            "can_extract": can_extract,
            "lines_count": len(lines_to_extract),
            "functions_called_in_extracted_code": len(functions_called),
            "recommendation": (
                "Extraction is safe" if can_extract 
                else "Extraction may cause issues - complex interdependencies"
            )
        }
    except Exception as e:
        logger.error(f"Error finding extraction points: {e}")
        return {"error": str(e), "can_extract": False}


def get_call_chain(
    start_func_id: str,
    end_func_id: Optional[str] = None,
    max_depth: int = 5,
    db_path: str = None
) -> Dict[str, Any]:
    """
    Tool: Get call chain from start function to end function.
    
    Usage by agent:
        chain = get_call_chain(
            start_func_id="authenticate",
            end_func_id="database.query",
            db_path="/path/to/graph.db"
        )
        # Check each function in chain for vulnerabilities
        for func in chain['path']:
            agent.check_security(func)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        chain_paths = []
        queue = [(start_func_id, [start_func_id], 0)]

        while queue:
            current, path, depth = queue.pop(0)
            
            if depth >= max_depth:
                if not end_func_id or current == end_func_id:
                    chain_paths.append(path)
                continue

            cursor.execute('''
                SELECT DISTINCT target_node_id FROM call_graphs 
                WHERE source_node_id = ?
            ''', (current,))
            
            callees = [row[0] for row in cursor.fetchall()]

            for callee in callees:
                new_path = path + [callee]
                if end_func_id and callee == end_func_id:
                    chain_paths.append(new_path)
                else:
                    queue.append((callee, new_path, depth + 1))

        conn.close()

        return {
            "start_function": start_func_id,
            "end_function": end_func_id,
            "paths_found": len(chain_paths),
            "paths": chain_paths[:5],  # Limit to first 5
            "max_depth": max([len(p) for p in chain_paths]) if chain_paths else 0
        }
    except Exception as e:
        logger.error(f"Error getting call chain: {e}")
        return {"error": str(e), "paths_found": 0}


def detect_circular_dependencies(db_path: str) -> Dict[str, Any]:
    """
    Tool: Detect and report circular dependencies in code.
    
    Usage by agent:
        cycles = detect_circular_dependencies(db_path="/path/to/graph.db")
        if cycles['cycles_found']:
            agent.suggest_refactoring_to_break_cycles()
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all nodes in call graph
        cursor.execute('''
            SELECT DISTINCT source_node_id FROM call_graphs
            UNION
            SELECT DISTINCT target_node_id FROM call_graphs
        ''')
        all_nodes = [row[0] for row in cursor.fetchall()]

        cycles = []
        visited = set()

        def dfs(node, path, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            cursor.execute('''
                SELECT target_node_id FROM call_graphs WHERE source_node_id = ?
            ''', (node,))
            neighbors = [row[0] for row in cursor.fetchall()]

            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, path[:], rec_stack)
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.discard(node)

        for node in all_nodes:
            if node not in visited:
                dfs(node, [], set())

        conn.close()

        severity = "high" if len(cycles) > 5 else "medium" if len(cycles) > 1 else "low"

        return {
            "cycles_found": len(cycles),
            "severity": severity,
            "cycles": cycles[:10],  # Limit to first 10
            "recommendation": (
                "Several circular dependencies detected - consider refactoring"
                if len(cycles) > 1
                else "No circular dependencies found"
            )
        }
    except Exception as e:
        logger.error(f"Error detecting cycles: {e}")
        return {"error": str(e), "cycles_found": 0}


def estimate_refactoring_risk(
    changes: List[Dict[str, str]],
    db_path: str
) -> Dict[str, Any]:
    """
    Tool: Estimate overall risk of a set of changes.
    
    Usage by agent:
        risk = estimate_refactoring_risk(
            changes=[
                {"type": "parameter_add", "function": "func_1", "param": "logger"},
                {"type": "function_extract", "function": "func_2", "lines": [10, 20]}
            ],
            db_path="/path/to/graph.db"
        )
        if risk['risk_score'] < 0.5:
            agent.auto_approve_changes()
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_risk = 0.0
        affected_functions = set()

        for change in changes:
            change_type = change.get("type")
            func_id = change.get("function")

            if change_type == "parameter_add":
                # Low risk - usually backward compatible
                total_risk += 0.1
            elif change_type == "parameter_remove":
                # High risk - breaks callers
                total_risk += 0.5
            elif change_type == "parameter_change":
                # Very high risk
                total_risk += 0.7
            elif change_type == "function_delete":
                # Risk depends on callers
                cursor.execute('''
                    SELECT COUNT(*) FROM call_graphs WHERE target_node_id = ?
                ''', (func_id,))
                caller_count = cursor.fetchone()[0]
                total_risk += 0.3 + (0.1 * min(caller_count, 5))
            elif change_type == "function_extract":
                # Low risk usually
                total_risk += 0.2

            affected_functions.add(func_id)

        # Normalize risk to 0-1 scale
        risk_score = min(1.0, total_risk / len(changes)) if changes else 0.0

        conn.close()

        return {
            "risk_score": round(risk_score, 2),
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
            "affected_functions": len(affected_functions),
            "recommendation": (
                "Proceed carefully - high risk changes" if risk_score > 0.7
                else "Moderate risk - comprehensive testing recommended" if risk_score > 0.4
                else "Low risk - safe to proceed"
            )
        }
    except Exception as e:
        logger.error(f"Error estimating refactoring risk: {e}")
        return {"error": str(e), "risk_score": 1.0}


def suggest_safe_refactorings(func_id: str, db_path: str) -> List[Dict[str, Any]]:
    """
    Tool: Suggest safe refactorings for a function.
    
    Usage by agent:
        suggestions = suggest_safe_refactorings(func_id="func_123", db_path="/path/graph.db")
        for sug in suggestions:
            if sug['confidence'] > 0.9:
                agent.apply_refactoring(sug)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        suggestions = []

        # Check if function is dead code
        cursor.execute('''
            SELECT COUNT(*) FROM call_graphs WHERE target_node_id = ?
        ''', (func_id,))
        callers = cursor.fetchone()[0]

        if callers == 0:
            suggestions.append({
                "type": "delete",
                "description": "Function is never called - can be deleted",
                "confidence": 0.99,
                "effort_hours": 0.1
            })

        # Check if function has redundant code
        cursor.execute('''
            SELECT COUNT(*) FROM call_graphs WHERE source_node_id = ?
        ''', (func_id,))
        callees = cursor.fetchone()[0]

        if callees > 3:
            suggestions.append({
                "type": "extract_helper",
                "description": "Function has high complexity - consider extracting helpers",
                "confidence": 0.7,
                "effort_hours": 1.0
            })

        # Check if function is hotspot
        cursor.execute('''
            SELECT COUNT(*) FROM call_graphs WHERE source_node_id = ?
        ''', (func_id,))
        calls = cursor.fetchone()[0]

        if calls > 5:
            suggestions.append({
                "type": "optimize",
                "description": "Function calls many other functions - consider caching",
                "confidence": 0.6,
                "effort_hours": 2.0
            })

        conn.close()

        return suggestions
    except Exception as e:
        logger.error(f"Error suggesting refactorings: {e}")
        return []
