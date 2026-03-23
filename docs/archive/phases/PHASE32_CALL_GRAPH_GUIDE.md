# Phase 32a: Call Graph Engine - Implementation Guide

**Priority**: HIGH (Enables safe refactoring and impact analysis)
**Complexity**: Medium
**Estimated Lines of Code**: 1,200
**Estimated Time**: 5-7 days

---

## Why Call Graphs First?

### Immediate Value
1. **Impact Radius**: "Will this change break anything?" → Answers in <500ms
2. **Safe Deletion**: "Can I delete this function?" → Traces all callers
3. **Refactoring Validation**: "Is it safe to extract this?" → Checks all downstream impact
4. **Performance Analysis**: "Where are the hot paths?" → Shows call frequency heatmap

### Foundation for Other Features
- Type System needs call graphs for parameter inference
- Service Boundaries need call graphs to separate concerns
- Architecture Analysis needs call graphs for coupling metrics
- Test Coverage Maps need call graphs to associate tests with code

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│        Call Graph Engine (Phase 32a)            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │    AST Analysis Layer                    │  │
│  │  ├─ Function signature extraction        │  │
│  │  ├─ Function call identification         │  │
│  │  ├─ Parameter type inference             │  │
│  │  └─ Return type identification           │  │
│  └──────────────────────────────────────────┘  │
│              ↓                                  │
│  ┌──────────────────────────────────────────┐  │
│  │    Call Graph Build Layer                │  │
│  │  ├─ callgraph table updates              │  │
│  │  ├─ Bidirectional edge creation          │  │
│  │  ├─ Call frequency aggregation           │  │
│  │  └─ Cycle detection                      │  │
│  └──────────────────────────────────────────┘  │
│              ↓                                  │
│  ┌──────────────────────────────────────────┐  │
│  │    Query Layer                           │  │
│  │  ├─ get_callers(function_id)             │  │
│  │  ├─ get_callees(function_id)             │  │
│  │  ├─ find_call_path(source, target)       │  │
│  │  ├─ calculate_impact_radius(function_id) │  │
│  │  ├─ find_dead_code()                     │  │
│  │  └─ detect_circular_calls()              │  │
│  └──────────────────────────────────────────┘  │
│              ↓                                  │
│  ┌──────────────────────────────────────────┐  │
│  │    Reasoning Layer                       │  │
│  │  ├─ Safe refactoring decisions           │  │
│  │  ├─ Impact risk assessment               │  │
│  │  ├─ Call path optimization               │  │
│  │  └─ Hotspot identification               │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│    Backed by: Phase 28 Persistent Graph DB     │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

### New Tables for Call Graphs

```sql
-- Call graph edges (function-level calls)
CREATE TABLE call_graphs (
    call_graph_id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,         -- Calling function
    target_node_id TEXT NOT NULL,         -- Called function
    
    -- Call details
    call_type TEXT,                       -- direct, indirect, async
    is_recursive BOOLEAN DEFAULT FALSE,
    is_circular BOOLEAN DEFAULT FALSE,    -- Part of circular dependency
    
    -- Type information
    parameter_types TEXT,                 -- JSON: ["int", "str", "bool"]
    return_type TEXT,                     -- Inferred from target function
    type_compatibility_score REAL,        -- 0-1: likelihood types match
    
    -- Frequency and performance
    call_frequency INT DEFAULT 1,         -- How many times observed
    total_calls_lifetime INT DEFAULT 0,   -- Cumulative across all time
    execution_time_ms REAL,               -- Average execution time
    last_call_timestamp TEXT,
    
    -- Context
    call_line_number INT,                 -- Line where call happens
    call_column_number INT,
    calling_context TEXT,                 -- JSON: surrounding scope
    
    -- Lifecycle
    is_deprecated BOOLEAN DEFAULT FALSE,
    deprecation_reason TEXT,
    first_observed TEXT,
    last_observed TEXT,
    
    -- Constraints
    FOREIGN KEY (source_node_id) REFERENCES nodes(node_id),
    FOREIGN KEY (target_node_id) REFERENCES nodes(node_id),
    UNIQUE(source_node_id, target_node_id)
);

-- Call path history (for tracking changes)
CREATE TABLE call_graph_history (
    history_id TEXT PRIMARY KEY,
    call_graph_id TEXT NOT NULL,
    operation TEXT,                       -- add, remove, modify
    change_timestamp TEXT,
    reason TEXT,                          -- why the change
    FOREIGN KEY (call_graph_id) REFERENCES call_graphs(call_graph_id)
);

-- Call cycles (for circular dependency tracking)
CREATE TABLE call_cycles (
    cycle_id TEXT PRIMARY KEY,
    cycle_length INT,                     -- Number of functions in cycle
    node_ids TEXT,                        -- JSON: ["func_1", "func_2", ...]
    severity TEXT,                        -- low, medium, high
    first_detected TEXT,
    last_verified TEXT,
    is_safe BOOLEAN,                      -- Intentional vs. bug
    mitigation_suggestions TEXT           -- JSON recommendations
);

-- Call statistics for hotspot analysis
CREATE TABLE call_statistics (
    stat_id TEXT PRIMARY KEY,
    function_id TEXT NOT NULL,
    
    -- Incoming calls
    in_degree INT DEFAULT 0,              -- Number of callers
    in_degree_direct INT DEFAULT 0,       -- Direct callers only
    
    -- Outgoing calls
    out_degree INT DEFAULT 0,             -- Number of callees
    out_degree_direct INT DEFAULT 0,      -- Direct callees only
    
    -- Centrality metrics
    betweenness_centrality REAL,          -- How often in paths
    closeness_centrality REAL,            -- Distance to other functions
    eigenvector_centrality REAL,          -- Influenced by important functions
    
    -- Call characteristics
    avg_call_depth INT,                   -- Average depth in call chain
    max_call_depth INT,                   -- Maximum depth
    is_hotspot BOOLEAN,                   -- High call frequency
    is_bottleneck BOOLEAN,                -- High latency impact
    is_leaf BOOLEAN,                      -- No outgoing calls
    is_root BOOLEAN,                      -- No incoming calls
    
    last_updated TEXT,
    FOREIGN KEY (function_id) REFERENCES nodes(node_id)
);

-- Indexes for performance
CREATE INDEX idx_source ON call_graphs(source_node_id);
CREATE INDEX idx_target ON call_graphs(target_node_id);
CREATE INDEX idx_recursive ON call_graphs(is_recursive);
CREATE INDEX idx_circular ON call_graphs(is_circular);
CREATE INDEX idx_frequency ON call_graphs(call_frequency DESC);
CREATE INDEX idx_deprecated ON call_graphs(is_deprecated);
CREATE INDEX idx_cycles ON call_cycles(cycle_length);
```

---

## Core Implementation

### File: `src/phase32_call_graph_engine.py`

```python
"""
Phase 32a: Call Graph Engine

Extracts, tracks, and analyzes function-level call relationships.
Enables impact radius calculation, safe refactoring, and hotspot analysis.
"""

import sqlite3
import json
import hashlib
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
import ast
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CallType(Enum):
    """Types of function calls"""
    DIRECT = "direct"              # f() → g()
    INDIRECT = "indirect"          # f() → g() → h()
    ASYNC = "async"                # await g()
    CALLBACK = "callback"          # register(callback)
    LAMBDA = "lambda"              # map(lambda x: ...)


@dataclass
class FunctionSignature:
    """Function metadata for call graph"""
    func_id: str
    name: str
    file_path: str
    line_number: int
    parameters: List[Dict[str, Any]]      # [{"name": "x", "type": "int"}]
    return_type: Optional[str]
    is_async: bool
    is_recursive: bool
    is_entry_point: bool                  # Main, handler, endpoint


@dataclass
class CallEdge:
    """Edge between functions in call graph"""
    call_id: str
    source_func_id: str
    target_func_id: str
    call_type: CallType
    parameter_types: List[str]            # Types passed to target
    return_type: Optional[str]
    call_frequency: int = 1
    execution_time_ms: Optional[float] = None
    line_number: int = 0
    is_deprecated: bool = False


class CallGraphExtractor:
    """Extract call graph from Python AST"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.source = self.file_path.read_text()
        self.tree = ast.parse(self.source)
        self.functions: Dict[str, FunctionSignature] = {}
        self.calls: List[CallEdge] = []
        self.current_function: Optional[str] = None

    def extract(self) -> Tuple[Dict[str, FunctionSignature], List[CallEdge]]:
        """Extract functions and calls from file"""
        self._visit_tree()
        return self.functions, self.calls

    def _visit_tree(self):
        """Visit AST and extract functions and calls"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self._process_function(node)

    def _process_function(self, node: ast.FunctionDef):
        """Process a function definition"""
        func_id = self._generate_func_id(node.name, node.lineno)
        
        # Extract function signature
        sig = FunctionSignature(
            func_id=func_id,
            name=node.name,
            file_path=str(self.file_path),
            line_number=node.lineno,
            parameters=self._extract_parameters(node),
            return_type=self._extract_return_type(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_recursive=self._check_recursion(node),
            is_entry_point=self._is_entry_point(node)
        )
        
        self.functions[func_id] = sig

        # Extract calls within this function
        old_func = self.current_function
        self.current_function = func_id
        
        for child in ast.walk(node):
            if isinstance(child, (ast.Call, ast.Await)):
                self._process_call(child, func_id)
        
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
        return "Any"

    def _process_call(self, node: ast.expr, source_func_id: str):
        """Process a function call"""
        call_node = node.func if isinstance(node, ast.Call) else node.value
        
        target_name = self._get_call_target(call_node)
        if not target_name:
            return
        
        # Determine call type
        call_type = CallType.ASYNC if isinstance(node, ast.Await) else CallType.DIRECT
        
        # Extract argument types
        arg_types = []
        if isinstance(node, ast.Call):
            for arg in node.args:
                arg_types.append(self._infer_arg_type(arg))
        
        # Create call edge
        call_id = self._generate_call_id(source_func_id, target_name, node.lineno)
        edge = CallEdge(
            call_id=call_id,
            source_func_id=source_func_id,
            target_func_id=target_name,  # May need resolution
            call_type=call_type,
            parameter_types=arg_types,
            return_type="Any",            # Will be inferred later
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
            if isinstance(arg.value, int):
                return "int"
            elif isinstance(arg.value, str):
                return "str"
            elif isinstance(arg.value, bool):
                return "bool"
            return "Any"
        elif isinstance(arg, ast.Name):
            return "Any"  # Would need type inference
        return "Any"

    def _check_recursion(self, node: ast.FunctionDef) -> bool:
        """Check if function calls itself"""
        func_name = node.name
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._get_call_target(child.func) == func_name:
                    return True
        return False

    def _is_entry_point(self, node: ast.FunctionDef) -> bool:
        """Check if function is an entry point (main, handler, etc.)"""
        entry_names = {'main', '__main__', 'handler', 'lambda_handler', 'run', 'execute'}
        return node.name.lower() in entry_names

    def _generate_func_id(self, name: str, line: int) -> str:
        """Generate unique function ID"""
        return hashlib.md5(f"{self.file_path}:{name}:{line}".encode()).hexdigest()

    def _generate_call_id(self, source: str, target: str, line: int) -> str:
        """Generate unique call ID"""
        return hashlib.md5(f"{source}->{target}:{line}".encode()).hexdigest()


class CallGraphDB:
    """Persistent storage for call graphs"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        # Use Phase 28 database
        if not self.db_path.exists():
            raise FileNotFoundError(f"Phase 28 database not found at {db_path}")
        self._init_call_graph_schema()

    def _init_call_graph_schema(self):
        """Create call graph tables if they don't exist"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # call_graphs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_graphs (
                call_graph_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                call_type TEXT,
                is_recursive BOOLEAN DEFAULT FALSE,
                is_circular BOOLEAN DEFAULT FALSE,
                parameter_types TEXT,
                return_type TEXT,
                type_compatibility_score REAL,
                call_frequency INT DEFAULT 1,
                execution_time_ms REAL,
                call_line_number INT,
                is_deprecated BOOLEAN DEFAULT FALSE,
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
                severity TEXT,
                first_detected TEXT,
                is_safe BOOLEAN DEFAULT FALSE
            )
        ''')

        # call_statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_statistics (
                stat_id TEXT PRIMARY KEY,
                function_id TEXT NOT NULL,
                in_degree INT DEFAULT 0,
                out_degree INT DEFAULT 0,
                betweenness_centrality REAL,
                is_hotspot BOOLEAN DEFAULT FALSE,
                is_bottleneck BOOLEAN DEFAULT FALSE,
                is_leaf BOOLEAN DEFAULT FALSE,
                is_root BOOLEAN DEFAULT FALSE,
                last_updated TEXT,
                FOREIGN KEY (function_id) REFERENCES nodes(node_id)
            )
        ''')

        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_source ON call_graphs(source_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_target ON call_graphs(target_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_recursive ON call_graphs(is_recursive)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_call_frequency ON call_graphs(call_frequency DESC)')

        conn.commit()
        conn.close()

    def add_call_edges(self, edges: List[CallEdge]) -> int:
        """Add multiple call edges"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        added = 0

        for edge in edges:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO call_graphs
                    (call_graph_id, source_node_id, target_node_id, call_type,
                     parameter_types, return_type, call_frequency, call_line_number,
                     first_observed, last_observed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    edge.call_id,
                    edge.source_func_id,
                    edge.target_func_id,
                    edge.call_type.value,
                    json.dumps(edge.parameter_types),
                    edge.return_type,
                    edge.call_frequency,
                    edge.line_number,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                added += 1
            except Exception as e:
                logger.error(f"Error adding call edge {edge.call_id}: {e}")

        conn.commit()
        conn.close()
        return added

    def get_callers(self, func_id: str) -> List[Dict]:
        """Get all functions that call this function"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cg.*, n.name AS caller_name
            FROM call_graphs cg
            JOIN nodes n ON cg.source_node_id = n.node_id
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
            SELECT cg.*, n.name AS callee_name
            FROM call_graphs cg
            JOIN nodes n ON cg.target_node_id = n.node_id
            WHERE cg.source_node_id = ?
            ORDER BY cg.call_frequency DESC
        ''', (func_id,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def find_call_chains(self, start_func_id: str, max_depth: int = 5) -> List[List[str]]:
        """Find all call chains starting from a function (BFS)"""
        chains = []
        queue = deque([(start_func_id, [start_func_id], 0)])

        while queue:
            current, path, depth = queue.popleft()
            
            if depth >= max_depth:
                chains.append(path)
                continue

            callees = self.get_callees(current)
            if not callees:
                chains.append(path)
            else:
                for callee in callees:
                    new_path = path + [callee['target_node_id']]
                    queue.append((callee['target_node_id'], new_path, depth + 1))

        return chains

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular call dependencies"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cycles = []
        # DFS-based cycle detection
        visited = set()
        rec_stack = set()

        cursor.execute('SELECT DISTINCT source_node_id FROM call_graphs')
        start_nodes = [row[0] for row in cursor.fetchall()]

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            cursor.execute('SELECT target_node_id FROM call_graphs WHERE source_node_id = ?', (node,))
            neighbors = [row[0] for row in cursor.fetchall()]

            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for start in start_nodes:
            if start not in visited:
                dfs(start, [])

        conn.close()
        return cycles


class ImpactAnalyzer:
    """Analyze impact of changes using call graph"""

    def __init__(self, db: CallGraphDB):
        self.db = db

    def calculate_impact_radius(self, func_id: str) -> Dict[str, Any]:
        """
        Calculate all functions affected by changes to this function.
        
        Returns:
        {
            'direct_impact': [list of immediate callers],
            'indirect_impact': [list of transitive callers],
            'total_functions_affected': int,
            'affected_services': [list of service boundaries],
            'risk_level': 'low|medium|high',
            'untested_functions': int,
            'recommendations': [list of strings]
        }
        """
        direct_callers = self.db.get_callers(func_id)
        indirect_callers = set()
        visited = set([func_id])

        # BFS to find all transitive callers
        queue = deque([c['source_node_id'] for c in direct_callers])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            indirect_callers.add(current)

            callers_of_current = self.db.get_callers(current)
            for caller in callers_of_current:
                if caller['source_node_id'] not in visited:
                    queue.append(caller['source_node_id'])

        return {
            'direct_impact': len(direct_callers),
            'indirect_impact': len(indirect_callers),
            'total_functions_affected': len(direct_callers) + len(indirect_callers),
            'risk_level': 'high' if len(indirect_callers) > 10 else 'medium' if len(direct_callers) > 3 else 'low',
            'recommendation': f"Changes to {len(direct_callers)} direct callers, {len(indirect_callers)} indirect callers"
        }
```

---

## Integration Points

### With Phase 28 Persistent Graph
```python
# In phase28_persistent_graph.py
def build_call_graph(repo_path: str):
    """Build call graph from repository"""
    from phase32_call_graph_engine import CallGraphExtractor, CallGraphDB
    
    db = CallGraphDB(db_path=self.graph_db_path)
    
    for py_file in Path(repo_path).glob('**/*.py'):
        extractor = CallGraphExtractor(str(py_file))
        functions, calls = extractor.extract()
        
        # Add functions as nodes
        for func_id, sig in functions.items():
            self.add_node(func_id, 'function', sig.name, str(py_file))
        
        # Add calls as edges
        db.add_call_edges(calls)
```

### With Agent Decision-Making
```python
# In agent/core.py
def should_refactor(self, change_description: str, target_code: str):
    """Check if refactoring is safe"""
    from phase32_call_graph_engine import ImpactAnalyzer
    
    # Find function to refactor
    func_id = self.identify_function(target_code)
    
    # Analyze impact
    analyzer = ImpactAnalyzer(self.call_graph_db)
    impact = analyzer.calculate_impact_radius(func_id)
    
    # Make decision
    if impact['risk_level'] == 'low':
        return True, f"Safe to refactor: only {impact['direct_impact']} direct callers"
    else:
        return False, f"Risky: {impact['total_functions_affected']} functions affected"
```

---

## Testing Strategy

### Unit Tests (test_call_graph_engine.py)

```python
def test_extract_function_definitions():
    """Extract function signatures"""
    code = """
    def add(a: int, b: int) -> int:
        return a + b
    """
    extractor = CallGraphExtractor.from_code(code)
    functions, _ = extractor.extract()
    
    assert len(functions) == 1
    assert list(functions.values())[0].parameters == 2

def test_extract_function_calls():
    """Extract function call edges"""
    code = """
    def add(a, b):
        return a + b
    
    def compute():
        result = add(1, 2)
        return result
    """
    extractor = CallGraphExtractor.from_code(code)
    _, calls = extractor.extract()
    
    assert len(calls) == 1
    assert calls[0].source_func_id == 'compute'
    assert calls[0].target_func_id == 'add'

def test_detect_recursion():
    """Detect recursive functions"""
    code = """
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)
    """
    extractor = CallGraphExtractor.from_code(code)
    functions, _ = extractor.extract()
    
    assert functions['factorial'].is_recursive

def test_detect_cycles():
    """Detect circular call dependencies"""
    # Add three functions: a calls b, b calls c, c calls a
    db = CallGraphDB(':memory:')
    # ... setup calls ...
    cycles = db.detect_circular_dependencies()
    
    assert len(cycles) > 0

def test_impact_radius():
    """Calculate impact of changes"""
    db = CallGraphDB(':memory:')
    # ... setup call graph ...
    
    analyzer = ImpactAnalyzer(db)
    impact = analyzer.calculate_impact_radius('func_a')
    
    assert impact['direct_impact'] > 0
    assert impact['risk_level'] in ['low', 'medium', 'high']
```

---

## Deliverables Checklist

- [ ] `src/phase32_call_graph_engine.py` (500 lines)
- [ ] `src/phase32_call_graph_extractor.py` (300 lines)
- [ ] `src/reasoning/impact_analyzer.py` (200 lines)
- [ ] Database schema integration with Phase 28
- [ ] Unit tests (100+ test cases)
- [ ] Integration tests with Phase 28 DB
- [ ] Documentation and examples
- [ ] Performance benchmarks

---

## Success Criteria

1. **Accuracy**: Extract 99%+ of direct function calls
2. **Performance**: Process 100K functions in <10s
3. **Completeness**: Handle Python, JavaScript, TypeScript
4. **Reliability**: Zero graph corruption over 1M updates
5. **Usability**: Reasoning queries return results in <500ms

---

## Next Steps

1. Start with `CallGraphExtractor` for Python
2. Build SQLite persistence layer
3. Implement BFS/DFS traversal queries
4. Add impact radius calculation
5. Integrate with agent decision-making
6. Add support for other languages
7. Build performance monitoring

