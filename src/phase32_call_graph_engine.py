"""
Phase 32a: Call Graph Engine

Extracts, tracks, and analyzes function-level call relationships.
Enables safe refactoring, impact radius calculation, and hotspot analysis.

Integrates with Phase 28 Persistent Repository Graph for cross-request learning.
"""

import sqlite3
import json
import hashlib
import ast
import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Deque
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum

logger = logging.getLogger(__name__)


class CallType(Enum):
    """Types of function calls"""
    DIRECT = "direct"              # f() → g()
    INDIRECT = "indirect"          # f() → g() → h()
    ASYNC = "async"                # await g()
    CALLBACK = "callback"          # register(callback)
    DYNAMIC = "dynamic"            # getattr/eval


@dataclass
class FunctionSignature:
    """Function metadata for call graph"""
    func_id: str
    name: str
    file_path: str
    line_number: int
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    is_async: bool = False
    is_recursive: bool = False
    is_entry_point: bool = False
    lines_of_code: int = 0
    complexity: float = 0.5


@dataclass
class CallEdge:
    """Edge between functions in call graph"""
    call_id: str
    source_func_id: str
    target_func_id: str
    call_type: CallType
    parameter_types: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    call_frequency: int = 1
    execution_time_ms: Optional[float] = None
    line_number: int = 0
    is_deprecated: bool = False
    is_recursive: bool = False


@dataclass
class ImpactRadius:
    """Impact analysis result"""
    function_id: str
    direct_callers: int
    indirect_callers: int
    total_affected: int
    risk_level: str  # low, medium, high
    affected_services: List[str] = field(default_factory=list)
    untested_functions: int = 0
    recommendations: List[str] = field(default_factory=list)


class PythonCallGraphExtractor:
    """Extract call graph from Python AST"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.source = self.file_path.read_text()
        try:
            self.tree = ast.parse(self.source)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            self.tree = None
            return

        self.functions: Dict[str, FunctionSignature] = {}
        self.calls: List[CallEdge] = []
        self.current_function: Optional[str] = None
        self.current_class: Optional[str] = None

    def extract(self) -> Tuple[Dict[str, FunctionSignature], List[CallEdge]]:
        """Extract functions and calls from file"""
        if self.tree is None:
            return {}, []
        
        self._visit_tree()
        return self.functions, self.calls

    def _visit_tree(self):
        """Visit AST and extract functions and calls"""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node)

    def _process_function(self, node: ast.FunctionDef):
        """Process a function definition"""
        func_id = self._generate_func_id(node.name, node.lineno)
        
        # Calculate LOC
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        lines_of_code = end_line - node.lineno + 1

        # Extract function signature
        sig = FunctionSignature(
            func_id=func_id,
            name=node.name,
            file_path=str(self.file_path),
            line_number=node.lineno,
            parameters=self._extract_parameters(node),
            return_type=self._extract_return_type(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_recursive=self._check_recursion(node, node.name),
            is_entry_point=self._is_entry_point(node),
            lines_of_code=lines_of_code,
            complexity=self._calculate_complexity(node)
        )
        
        self.functions[func_id] = sig

        # Extract calls within this function
        old_func = self.current_function
        self.current_function = func_id
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._process_call(child, func_id)
            elif isinstance(child, ast.Await):
                if hasattr(child, 'value') and isinstance(child.value, ast.Call):
                    self._process_call(child.value, func_id, is_async=True)
        
        self.current_function = old_func

    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict]:
        """Extract parameter names and inferred types"""
        params = []
        
        for arg in node.args.args:
            param_type = "Any"
            if arg.annotation:
                param_type = self._annotation_to_string(arg.annotation)
            
            params.append({
                "name": arg.arg,
                "type": param_type,
                "required": True
            })
        
        # Handle defaults (parameters with defaults are optional)
        num_defaults = len(node.args.defaults)
        if num_defaults > 0:
            default_start = len(params) - num_defaults
            for i in range(default_start, len(params)):
                params[i]["required"] = False
        
        return params

    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type from annotation"""
        if node.returns:
            return self._annotation_to_string(node.returns)
        return "Any"

    def _annotation_to_string(self, annotation: ast.expr) -> str:
        """Convert AST annotation to readable string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            value = self._annotation_to_string(annotation.value)
            slice_str = self._annotation_to_string(annotation.slice)
            return f"{value}[{slice_str}]"
        elif isinstance(annotation, ast.Attribute):
            value = self._annotation_to_string(annotation.value)
            return f"{value}.{annotation.attr}"
        elif hasattr(ast, 'Union') and isinstance(annotation, ast.Union):
            # Python 3.10+ only
            types = [self._annotation_to_string(t) for t in annotation.args]
            return " | ".join(types)
        elif isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
            # Handle X | Y syntax (Python 3.10+, but parsed as BinOp in some versions)
            try:
                left = self._annotation_to_string(annotation.left)
                right = self._annotation_to_string(annotation.right)
                return f"{left} | {right}"
            except Exception as e:  # TODO (2026-03-08): specify exception type
                return "Any"
        return "Any"

    def _process_call(self, node: ast.Call, source_func_id: str, is_async: bool = False):
        """Process a function call"""
        target_name = self._get_call_target(node.func)
        if not target_name:
            return
        
        # Determine call type
        call_type = CallType.ASYNC if is_async else CallType.DIRECT
        
        # Extract argument types
        arg_types = []
        for arg in node.args:
            arg_types.append(self._infer_arg_type(arg))
        
        # Create call edge
        call_id = self._generate_call_id(source_func_id, target_name, node.lineno)
        edge = CallEdge(
            call_id=call_id,
            source_func_id=source_func_id,
            target_func_id=target_name,
            call_type=call_type,
            parameter_types=arg_types,
            return_type="Any",
            line_number=node.lineno
        )
        
        self.calls.append(edge)

    def _get_call_target(self, node: ast.expr) -> Optional[str]:
        """Get the name of the function being called"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _infer_arg_type(self, arg: ast.expr) -> str:
        """Infer argument type from AST"""
        if isinstance(arg, ast.Constant):
            value = arg.value
            if isinstance(value, int):
                return "int"
            elif isinstance(value, str):
                return "str"
            elif isinstance(value, bool):
                return "bool"
            elif isinstance(value, float):
                return "float"
            elif value is None:
                return "None"
            return "Any"
        elif isinstance(arg, ast.Name):
            return arg.id  # Use variable name as type hint
        elif isinstance(arg, ast.List):
            return "list"
        elif isinstance(arg, ast.Dict):
            return "dict"
        elif isinstance(arg, ast.Tuple):
            return "tuple"
        return "Any"

    def _check_recursion(self, node: ast.FunctionDef, func_name: str) -> bool:
        """Check if function calls itself (direct recursion)"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                target = self._get_call_target(child.func)
                if target == func_name:
                    return True
        return False

    def _is_entry_point(self, node: ast.FunctionDef) -> bool:
        """Check if function is an entry point"""
        entry_names = {
            'main', '__main__', 'handler', 'lambda_handler', 
            'run', 'execute', 'start', 'init', '__init__'
        }
        return node.name.lower() in entry_names

    def _calculate_complexity(self, node: ast.FunctionDef) -> float:
        """Calculate cyclomatic complexity (0-1 scale)"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        # Normalize to 0-1 scale (max 10)
        return min(complexity / 10.0, 1.0)

    def _generate_func_id(self, name: str, line: int) -> str:
        """Generate unique function ID"""
        key = f"{self.file_path}:{name}:{line}"
        return hashlib.md5(key.encode()).hexdigest()[:16]

    def _generate_call_id(self, source: str, target: str, line: int) -> str:
        """Generate unique call ID"""
        key = f"{source}->{target}:{line}"
        return hashlib.md5(key.encode()).hexdigest()[:16]


class CallGraphDB:
    """Persistent storage for call graphs in SQLite"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Create call graph tables if they don't exist"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # call_graphs table - function-level calls
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_graphs (
                call_graph_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'direct',
                is_recursive BOOLEAN DEFAULT 0,
                is_circular BOOLEAN DEFAULT 0,
                parameter_types TEXT,
                return_type TEXT,
                type_compatibility_score REAL DEFAULT 1.0,
                call_frequency INT DEFAULT 1,
                execution_time_ms REAL,
                call_line_number INT,
                is_deprecated BOOLEAN DEFAULT 0,
                first_observed TEXT,
                last_observed TEXT,
                FOREIGN KEY (source_node_id) REFERENCES nodes(node_id),
                FOREIGN KEY (target_node_id) REFERENCES nodes(node_id),
                UNIQUE(source_node_id, target_node_id)
            )
        ''')

        # call_cycles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_cycles (
                cycle_id TEXT PRIMARY KEY,
                cycle_length INT,
                node_ids TEXT,
                severity TEXT DEFAULT 'medium',
                first_detected TEXT,
                is_safe BOOLEAN DEFAULT 0,
                mitigation_suggestions TEXT
            )
        ''')

        # call_statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_statistics (
                stat_id TEXT PRIMARY KEY,
                function_id TEXT NOT NULL UNIQUE,
                in_degree INT DEFAULT 0,
                out_degree INT DEFAULT 0,
                betweenness_centrality REAL,
                closeness_centrality REAL,
                eigenvector_centrality REAL,
                is_hotspot BOOLEAN DEFAULT 0,
                is_bottleneck BOOLEAN DEFAULT 0,
                is_leaf BOOLEAN DEFAULT 0,
                is_root BOOLEAN DEFAULT 0,
                last_updated TEXT,
                FOREIGN KEY (function_id) REFERENCES nodes(node_id)
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_source ON call_graphs(source_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_target ON call_graphs(target_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_recursive ON call_graphs(is_recursive)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_circular ON call_graphs(is_circular)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_frequency ON call_graphs(call_frequency DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_deprecated ON call_graphs(is_deprecated)')

        conn.commit()
        conn.close()
        logger.info(f"Call graph schema initialized at {self.db_path}")

    def add_call_edges(self, edges: List[CallEdge]) -> int:
        """Add multiple call edges to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        added = 0
        now = datetime.now().isoformat()

        for edge in edges:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO call_graphs
                    (call_graph_id, source_node_id, target_node_id, call_type,
                     parameter_types, return_type, call_frequency, call_line_number,
                     is_recursive, first_observed, last_observed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    edge.call_id,
                    edge.source_func_id,
                    edge.target_func_id,
                    edge.call_type.value,
                    json.dumps(edge.parameter_types),
                    edge.return_type,
                    edge.call_frequency,
                    edge.line_number,
                    1 if edge.is_recursive else 0,
                    now,
                    now
                ))
                added += 1
            except Exception as e:
                logger.error(f"Error adding call edge {edge.call_id}: {e}")

        conn.commit()
        conn.close()
        return added

    def get_callers(self, func_id: str, depth: int = 1) -> List[Dict]:
        """Get all functions that call this function"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cg.*, n.name AS caller_name, n.path AS caller_path
            FROM call_graphs cg
            LEFT JOIN nodes n ON cg.source_node_id = n.node_id
            WHERE cg.target_node_id = ?
            ORDER BY cg.call_frequency DESC
        ''', (func_id,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_callees(self, func_id: str) -> List[Dict]:
        """Get all functions called by this function"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cg.*, n.name AS callee_name, n.path AS callee_path
            FROM call_graphs cg
            LEFT JOIN nodes n ON cg.target_node_id = n.node_id
            WHERE cg.source_node_id = ?
            ORDER BY cg.call_frequency DESC
        ''', (func_id,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    # ==================== CONFIDENCE-AWARE QUERIES (Phase 32 Migration 2) ====================

    def get_callers_confident(self, func_id: str, min_confidence: float = 0.85) -> List[Dict]:
        """Get callers with confidence >= min_confidence"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cg.*, n.name AS caller_name, n.path AS caller_path,
                   n.stable_id AS caller_stable_id
            FROM call_graphs cg
            LEFT JOIN nodes n ON cg.source_node_id = n.node_id
            WHERE cg.target_node_id = ? 
              AND cg.confidence >= ?
            ORDER BY cg.confidence DESC, cg.call_frequency DESC
        ''', (func_id, min_confidence))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_callees_confident(self, func_id: str, min_confidence: float = 0.85) -> List[Dict]:
        """Get callees with confidence >= min_confidence"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cg.*, n.name AS callee_name, n.path AS callee_path,
                   n.stable_id AS callee_stable_id
            FROM call_graphs cg
            LEFT JOIN nodes n ON cg.target_node_id = n.node_id
            WHERE cg.source_node_id = ? 
              AND cg.confidence >= ?
            ORDER BY cg.confidence DESC, cg.call_frequency DESC
        ''', (func_id, min_confidence))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_impact_radius_confident(self, func_id: str, min_confidence: float = 0.85, max_depth: int = 3) -> Dict:
        """Calculate impact radius considering confidence threshold
        
        Returns all functions affected by changes to func_id, 
        only following confident call paths (confidence >= min_confidence)
        """
        affected = set()
        queue: Deque = deque([(func_id, 0)])
        visited = set([func_id])
        confidence_scores = {}

        while queue:
            current_id, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            callers = self.get_callers_confident(current_id, min_confidence)
            
            for caller in callers:
                caller_id = caller['source_node_id']
                conf = caller.get('confidence', 0)
                
                affected.add(caller_id)
                confidence_scores[caller_id] = conf
                
                if caller_id not in visited:
                    visited.add(caller_id)
                    queue.append((caller_id, depth + 1))
        
        # Get details about affected functions
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        affected_details = []
        for node_id in affected:
            cursor.execute('''
                SELECT node_id, name, qualified_name, stable_id, complexity, lines_of_code
                FROM nodes WHERE node_id = ?
            ''', (node_id,))
            row = cursor.fetchone()
            if row:
                affected_details.append({
                    'node_id': row['node_id'],
                    'name': row['name'],
                    'qualified_name': row['qualified_name'],
                    'stable_id': row['stable_id'],
                    'complexity': row['complexity'],
                    'lines_of_code': row['lines_of_code'],
                    'confidence': confidence_scores.get(node_id, 0)
                })
        
        conn.close()
        
        # Calculate risk level
        if len(affected) == 0:
            risk_level = "low"
        elif len(affected) <= 3:
            risk_level = "low"
        elif len(affected) <= 10:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            'function_id': func_id,
            'min_confidence': min_confidence,
            'total_affected': len(affected),
            'affected_functions': affected_details,
            'risk_level': risk_level,
            'avg_confidence': sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
        }

    def get_confident_call_paths(self, source_id: str, target_id: str, min_confidence: float = 0.85) -> List[List[Dict]]:
        """Find all confident paths from source to target function
        
        Returns paths where every edge has confidence >= min_confidence
        """
        paths = []
        
        def dfs(current_id: str, target_id: str, path: List[str], visited: set) -> bool:
            if current_id == target_id:
                paths.append(path)
                return True
            
            if len(path) > 10:  # Prevent excessive recursion
                return False
            
            callees = self.get_callees_confident(current_id, min_confidence)
            found_any = False
            
            for callee in callees:
                callee_id = callee['target_node_id']
                if callee_id not in visited:
                    visited.add(callee_id)
                    if dfs(callee_id, target_id, path + [callee_id], visited):
                        found_any = True
                    visited.remove(callee_id)
            
            return found_any
        
        dfs(source_id, target_id, [source_id], set([source_id]))
        
        # Convert node IDs to detailed call information
        detailed_paths = []
        for path_ids in paths:
            detailed_path = []
            for i in range(len(path_ids) - 1):
                source = path_ids[i]
                target = path_ids[i + 1]
                
                # Find the edge between these nodes
                conn = sqlite3.connect(str(self.db_path))
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT cg.*, 
                           src.name AS source_name, src.stable_id AS source_stable_id,
                           tgt.name AS target_name, tgt.stable_id AS target_stable_id
                    FROM call_graphs cg
                    LEFT JOIN nodes src ON cg.source_node_id = src.node_id
                    LEFT JOIN nodes tgt ON cg.target_node_id = tgt.node_id
                    WHERE cg.source_node_id = ? AND cg.target_node_id = ?
                ''', (source, target))
                
                edge = cursor.fetchone()
                conn.close()
                
                if edge:
                    detailed_path.append(dict(edge))
            
            if detailed_path:
                detailed_paths.append(detailed_path)
        
        return detailed_paths

    def find_call_chains(self, start_func_id: str, max_depth: int = 5) -> List[List[str]]:
        """Find all call chains from a function using BFS"""
        chains = []
        queue: Deque = deque([(start_func_id, [start_func_id], 0)])
        visited = set()

        while queue:
            current, path, depth = queue.popleft()
            
            if depth >= max_depth or len(path) > 100:  # Prevent infinite loops
                chains.append(path)
                continue

            callees = self.get_callees(current)
            if not callees:
                chains.append(path)
            else:
                for callee_row in callees:
                    callee_id = callee_row['target_node_id']
                    if callee_id not in visited:
                        visited.add(callee_id)
                        new_path = path + [callee_id]
                        queue.append((callee_id, new_path, depth + 1))

        return chains

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular call dependencies using DFS"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get all nodes that participate in calls
        cursor.execute('''
            SELECT DISTINCT source_node_id FROM call_graphs
            UNION
            SELECT DISTINCT target_node_id FROM call_graphs
        ''')
        all_nodes = [row[0] for row in cursor.fetchall()]
        
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            cursor.execute(
                'SELECT target_node_id FROM call_graphs WHERE source_node_id = ?',
                (node,)
            )
            neighbors = [row[0] for row in cursor.fetchall()]

            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start_idx = path.index(neighbor)
                    cycle = path[cycle_start_idx:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            rec_stack.discard(node)

        for node in all_nodes:
            if node not in visited:
                dfs(node, [])

        conn.close()
        return cycles

    def update_statistics(self) -> int:
        """Update call statistics for all functions"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        updated = 0
        now = datetime.now().isoformat()

        # Get all functions
        cursor.execute('SELECT node_id FROM nodes WHERE node_type = "function"')
        functions = [row[0] for row in cursor.fetchall()]

        for func_id in functions:
            # Calculate in-degree
            cursor.execute(
                'SELECT COUNT(*) FROM call_graphs WHERE target_node_id = ?',
                (func_id,)
            )
            in_degree = cursor.fetchone()[0]

            # Calculate out-degree
            cursor.execute(
                'SELECT COUNT(*) FROM call_graphs WHERE source_node_id = ?',
                (func_id,)
            )
            out_degree = cursor.fetchone()[0]

            # Determine characteristics
            is_leaf = out_degree == 0
            is_root = in_degree == 0
            is_hotspot = in_degree > 5  # Arbitrary threshold
            is_bottleneck = out_degree > 3 and in_degree > 3

            stat_id = hashlib.md5(f"{func_id}_stat".encode()).hexdigest()[:16]

            cursor.execute('''
                INSERT OR REPLACE INTO call_statistics
                (stat_id, function_id, in_degree, out_degree, is_leaf, is_root,
                 is_hotspot, is_bottleneck, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stat_id, func_id, in_degree, out_degree,
                1 if is_leaf else 0, 1 if is_root else 0,
                1 if is_hotspot else 0, 1 if is_bottleneck else 0,
                now
            ))
            updated += 1

        conn.commit()
        conn.close()
        return updated


class ImpactAnalyzer:
    """Analyze impact of code changes using call graph"""

    def __init__(self, db: CallGraphDB):
        self.db = db

    def calculate_impact_radius(self, func_id: str) -> ImpactRadius:
        """
        Calculate all functions affected by changes to this function.
        
        Uses BFS to traverse call graph and identify all transitive callers.
        """
        direct_callers = self.db.get_callers(func_id)
        indirect_callers = set()
        visited = {func_id}

        # BFS to find all transitive callers
        queue: Deque = deque([c['source_node_id'] for c in direct_callers])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            indirect_callers.add(current)

            callers_of_current = self.db.get_callers(current)
            for caller in callers_of_current:
                caller_id = caller['source_node_id']
                if caller_id not in visited:
                    queue.append(caller_id)

        # Determine risk level
        total_affected = len(direct_callers) + len(indirect_callers)
        if total_affected > 20:
            risk_level = "high"
        elif total_affected > 5:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Build recommendations
        recommendations = []
        if len(direct_callers) > 0:
            recommendations.append(
                f"Changes will affect {len(direct_callers)} direct callers"
            )
        if len(indirect_callers) > 0:
            recommendations.append(
                f"Transitive impact: {len(indirect_callers)} indirect callers"
            )
        if risk_level == "high":
            recommendations.append("RISK: HIGH - Consider impact on multiple services")
            recommendations.append("Recommendation: Comprehensive test coverage required")
        elif risk_level == "medium":
            recommendations.append("Recommendation: Run affected test suites before deploying")

        return ImpactRadius(
            function_id=func_id,
            direct_callers=len(direct_callers),
            indirect_callers=len(indirect_callers),
            total_affected=total_affected,
            risk_level=risk_level,
            affected_services=[],  # Would populate from service_boundaries table
            recommendations=recommendations
        )

    def is_safe_to_delete(self, func_id: str) -> Tuple[bool, str]:
        """Check if function can be safely deleted"""
        callers = self.db.get_callers(func_id)
        
        if not callers:
            return True, "Safe: No callers found. Function can be deleted."
        else:
            caller_names = [c['caller_name'] or c['source_node_id'] for c in callers]
            return False, f"Unsafe: {len(callers)} function(s) still call this: {', '.join(caller_names)}"

    def find_cycles(self) -> List[List[str]]:
        """Find all circular call dependencies"""
        return self.db.detect_circular_dependencies()


class CallGraphBuilder:
    """Build call graph from repository"""

    def __init__(self, call_db: CallGraphDB):
        self.call_db = call_db
        # Connect to the nodes database using the same path
        self.node_db_path = str(call_db.db_path)
        self.node_conn = sqlite3.connect(self.node_db_path)
        self.node_conn.row_factory = sqlite3.Row

    def build_from_directory(self, repo_path: str) -> Dict[str, Any]:
        """Build call graph from all Python files in directory"""
        repo_path = Path(repo_path)
        stats = {
            "files_processed": 0,
            "functions_found": 0,
            "calls_found": 0,
            "errors": [],
            "total_functions": 0,
            "total_calls": 0,
            "circular_deps": 0,
            "nodes_added": 0
        }

        for py_file in repo_path.glob('**/*.py'):
            # Skip virtual environments and cache
            if any(part in str(py_file) for part in ['venv', '__pycache__', '.venv', 'node_modules']):
                continue

            try:
                extractor = PythonCallGraphExtractor(str(py_file))
                functions, calls = extractor.extract()

                # Add functions to call graph
                for func_id, sig in functions.items():
                    self._add_function_node(func_id, sig)
                    stats["functions_found"] += 1

                # Add calls to call graph
                added = self.call_db.add_call_edges(calls)
                stats["calls_found"] += added
                stats["files_processed"] += 1

            except Exception as e:
                logger.warning(f"Error processing {py_file}: {e}")
                stats["errors"].append(str(e))

        # Set total counts
        stats["total_functions"] = stats["functions_found"]
        stats["total_calls"] = stats["calls_found"]
        stats["nodes_added"] = stats["functions_found"]

        self.node_conn.close()
        return stats

    def _add_function_node(self, func_id: str, sig: FunctionSignature):
        """Add function to node database (Phase 28 integration)"""
        cursor = self.node_conn.cursor()
        now = datetime.now().isoformat()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO nodes
                (node_id, node_type, name, path, language, lines_of_code, 
                 complexity, last_modified, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                func_id,
                'function',
                sig.name,
                sig.file_path,
                'python',
                sig.lines_of_code,
                sig.complexity,
                now,
                json.dumps({
                    'is_async': sig.is_async,
                    'is_recursive': sig.is_recursive,
                    'parameters': sig.parameters,
                    'return_type': sig.return_type
                })
            ))
            self.node_conn.commit()
        except Exception as e:
            logger.error(f"Error adding function node {func_id}: {e}")
