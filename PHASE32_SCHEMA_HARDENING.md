# Phase 32: Schema Hardening Guide

**Database migrations to add confidence scoring, node stability, and rich reporting**

---

## Overview

This guide shows the exact schema changes needed to harden Phase 32a for production.

Three sets of migrations:
1. **Node Identity** - Qualified names + signatures (blocks all other improvements)
2. **Confidence Scoring** - Evidence tracking + confidence scores
3. **Test Coverage** - Test mapping (enables risk scoring)

---

## Migration 1: Node Identity Stability

### Problem
Current:
```python
node_id = hash(file_path + line_number + function_name)
# Breaks when file moves
```

Better:
```python
qualified_name = "src.engine.CallGraphDB.get_callers"
signature_hash = "abc12345"
# Survives file moves, reformats, small changes
```

### Schema Changes

**Before:**
```sql
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    node_type TEXT NOT NULL,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    -- No stability guarantee
);

CREATE TABLE call_graphs (
    call_id INTEGER PRIMARY KEY,
    source_node_id INTEGER NOT NULL,
    target_node_id INTEGER NOT NULL,
    -- Only references unstable node IDs
);
```

**After:**
```sql
-- UPDATED nodes table
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    node_type TEXT NOT NULL,           -- 'function' | 'class' | 'method'
    
    -- Stable identification (survives refactors)
    repo_id TEXT NOT NULL,             -- 'piddy'
    qualified_name TEXT NOT NULL,      -- 'src.engine.CallGraphDB.get_callers'
    signature_hash TEXT NOT NULL,      -- 'abc12345' (hash of signature)
    stable_id TEXT UNIQUE NOT NULL,    -- '{repo_id}:{qualified_name}:{signature_hash}'
    
    -- Current location (may change)
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deprecated BOOLEAN DEFAULT FALSE,
    
    UNIQUE(stable_id)
);

-- Add index for qualifed name lookups
CREATE INDEX idx_nodes_qualified_name ON nodes(qualified_name);
CREATE INDEX idx_nodes_stable_id ON nodes(stable_id);

-- UPDATED call_graphs table
CREATE TABLE call_graphs (
    call_id INTEGER PRIMARY KEY,
    source_node_id INTEGER NOT NULL,
    target_node_id INTEGER NOT NULL,
    
    -- Keep both unstable and stable IDs for transition period
    source_stable_id TEXT,             -- NEW: for lookup by qualified name
    target_stable_id TEXT,
    
    call_type TEXT,
    parameter_types TEXT,
    return_type TEXT,
    
    -- NEW: Confidence scoring
    evidence_type TEXT DEFAULT 'static',  -- 'static' | 'runtime' | 'inferred'
    confidence REAL DEFAULT 0.95,         -- 0.0-1.0
    source TEXT DEFAULT 'ast:call_node',  -- where this came from
    observed_count INTEGER DEFAULT 1,     -- how many times observed
    last_verified TIMESTAMP,              -- when we verified it
    
    call_frequency INTEGER DEFAULT 1,
    execution_time_ms REAL,
    is_recursive BOOLEAN DEFAULT FALSE,
    is_circular BOOLEAN DEFAULT FALSE,
    is_deprecated BOOLEAN DEFAULT FALSE,
    line_number INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(source_node_id) REFERENCES nodes(id),
    FOREIGN KEY(target_node_id) REFERENCES nodes(id),
    INDEX idx_call_confidence (source_node_id, confidence DESC)
);
```

### Migration Script

```python
def migrate_1_node_identity(db: sqlite3.Connection):
    """Add stable node IDs and confidence to schema"""
    
    cursor = db.cursor()
    
    # Step 1: Add new columns to nodes table
    cursor.execute("""
        ALTER TABLE nodes ADD COLUMN repo_id TEXT DEFAULT 'piddy';
        ALTER TABLE nodes ADD COLUMN qualified_name TEXT;
        ALTER TABLE nodes ADD COLUMN signature_hash TEXT;
        ALTER TABLE nodes ADD COLUMN stable_id TEXT UNIQUE;
        ALTER TABLE nodes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE nodes ADD COLUMN last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE nodes ADD COLUMN is_deprecated BOOLEAN DEFAULT FALSE;
    """)
    
    # Step 2: Add new columns to call_graphs table
    cursor.execute("""
        ALTER TABLE call_graphs ADD COLUMN source_stable_id TEXT;
        ALTER TABLE call_graphs ADD COLUMN target_stable_id TEXT;
        ALTER TABLE call_graphs ADD COLUMN evidence_type TEXT DEFAULT 'static';
        ALTER TABLE call_graphs ADD COLUMN confidence REAL DEFAULT 0.95;
        ALTER TABLE call_graphs ADD COLUMN source TEXT DEFAULT 'ast:call_node';
        ALTER TABLE call_graphs ADD COLUMN observed_count INTEGER DEFAULT 1;
        ALTER TABLE call_graphs ADD COLUMN last_verified TIMESTAMP;
        ALTER TABLE call_graphs ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE call_graphs ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)
    
    # Step 3: Populate stable_id for existing nodes
    # This requires the extraction logic to compute qualified names
    # See: compute_qualified_names() below
    
    # Step 4: Create indexes
    cursor.execute("CREATE INDEX idx_nodes_qualified_name ON nodes(qualified_name);")
    cursor.execute("CREATE INDEX idx_nodes_stable_id ON nodes(stable_id);")
    cursor.execute("CREATE INDEX idx_call_stable_source ON call_graphs(source_stable_id);")
    cursor.execute("CREATE INDEX idx_call_stable_target ON call_graphs(target_stable_id);")
    cursor.execute("CREATE INDEX idx_call_confidence ON call_graphs(source_node_id, confidence DESC);")
    
    db.commit()
    print("✓ Migration 1: Node identity stability applied")

def compute_qualified_names(db: sqlite3.Connection, repo_path: str):
    """Populate qualified_name and signature_hash for all nodes"""
    
    import ast
    import hashlib
    from pathlib import Path
    
    cursor = db.cursor()
    
    # Get all Python files
    for py_file in Path(repo_path).rglob("*.py"):
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
            
            relative_path = str(py_file.relative_to(repo_path))
            module_name = relative_path.replace("/", ".").replace(".py", "")
            
            # Process each function/class
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    qualified = f"{module_name}.{node.name}"
                    sig_hash = _signature_hash(node)
                    
                    cursor.execute("""
                        UPDATE nodes 
                        SET qualified_name = ?, signature_hash = ?, 
                            stable_id = 'piddy:' || ? || ':' || ?
                        WHERE name = ? AND file_path = ?
                    """, (qualified, sig_hash, qualified, sig_hash, 
                          node.name, str(py_file)))
                
                elif isinstance(node, ast.ClassDef):
                    qualified = f"{module_name}.{node.name}"
                    sig_hash = "class"  # Classes don't have signatures like functions
                    
                    cursor.execute("""
                        UPDATE nodes
                        SET qualified_name = ?, signature_hash = ?,
                            stable_id = 'piddy:' || ? || ':' || ?
                        WHERE name = ? AND file_path = ?
                    """, (qualified, sig_hash, qualified, sig_hash,
                          node.name, str(py_file)))
        
        except Exception as e:
            print(f"⚠ Skipped {py_file}: {e}")
    
    # Populate call_graphs stable IDs from nodes
    cursor.execute("""
        UPDATE call_graphs
        SET source_stable_id = (
            SELECT stable_id FROM nodes WHERE nodes.id = call_graphs.source_node_id
        ),
        target_stable_id = (
            SELECT stable_id FROM nodes WHERE nodes.id = call_graphs.target_node_id
        )
    """)
    
    db.commit()
    print("✓ Computed qualified names and stable IDs for all nodes")

def _signature_hash(func_node: ast.FunctionDef) -> str:
    """Hash of function signature"""
    sig = f"{func_node.name}("
    sig += ",".join(arg.arg for arg in func_node.args.args)
    sig += ")"
    if func_node.returns:
        sig += f" -> {ast.unparse(func_node.returns)}"
    return hashlib.md5(sig.encode()).hexdigest()[:8]
```

### Usage Update

```python
# Before
caller_id = get_node_id_by_name("CallGraphDB.get_callers")

# After (stable)
caller_id = get_node_by_stable_id("piddy:src.engine.CallGraphDB.get_callers:abc12345")
```

---

## Migration 2: Confidence Scoring

### Problem
Current edges have no confidence information:
```sql
INSERT INTO call_graphs(source, target)
-- No way to know: "Am I 95% sure or 60% sure this edge exists?"
```

### Schema Already Added Above

The call_graphs table already has:
- `evidence_type` - 'static' | 'runtime' | 'inferred'
- `confidence` - 0.0-1.0 score
- `source` - where the edge came from
- `observed_count` - how many times we've seen it

### Population Strategy

```python
class ConfidencePopulator:
    def populate_initial_confidence(db: sqlite3.Connection):
        """Set confidence for existing edges based on evidence type"""
        
        cursor = db.cursor()
        
        # Static AST edges: 95% confidence (high, but not 100%)
        cursor.execute("""
            UPDATE call_graphs
            SET evidence_type = 'static',
                confidence = 0.95,
                source = 'ast:call_node'
            WHERE evidence_type IS NULL OR evidence_type = '';
        """)
        
        # Edges from decorators: lower confidence (harder to track)
        cursor.execute("""
            UPDATE call_graphs
            SET confidence = 0.75
            WHERE source = 'ast:decorator';
        """)
        
        # Edges from reflection: lowest confidence
        cursor.execute("""
            UPDATE call_graphs
            SET confidence = 0.40
            WHERE source = 'inference:reflection';
        """)
        
        db.commit()
        print("✓ Populated initial confidence scores")

def enhance_confidence_from_runtime(db: sqlite3.Connection, test_output: str):
    """Update confidence based on actual execution traces"""
    
    # Parse test output to find actual calls
    # Compare with static graph
    # Boost confidence for confirmed edges
    # Flag missing edges
    
    cursor = db.cursor()
    
    # For each edge found in runtime:
    cursor.execute("""
        UPDATE call_graphs
        SET evidence_type = 'static+runtime',
            confidence = 0.99,
            observed_count = observed_count + 1,
            last_verified = CURRENT_TIMESTAMP
        WHERE source_stable_id = ? AND target_stable_id = ?
    """, (caller_stable_id, callee_stable_id))
```

### Query Pattern: Confidence-Aware Impact

```python
def get_impact_radius_confident(db: sqlite3.Connection, func_id: str, 
                                min_confidence: float = 0.85) -> ImpactRadius:
    """Only traverse edges with sufficient confidence"""
    
    cursor = db.cursor()
    
    # BFS traversal, only following high-confidence edges
    cursor.execute("""
        WITH RECURSIVE impact_graph AS (
            -- Base case: the function itself
            SELECT target_node_id, 1 as depth, confidence
            FROM call_graphs
            WHERE source_node_id = ? AND confidence >= ?
            
            UNION ALL
            
            -- Recursive case: callers of callers
            SELECT cg.target_node_id, ig.depth + 1, cg.confidence
            FROM call_graphs cg
            JOIN impact_graph ig ON cg.source_node_id = ig.target_node_id
            WHERE ig.depth < 5 AND cg.confidence >= ?
        )
        SELECT COUNT(DISTINCT target_node_id) as total_affected
        FROM impact_graph
    """, (func_id, min_confidence, min_confidence))
    
    return cursor.fetchone()[0]
```

---

## Migration 3: Test Coverage Mapping

### New Table

```sql
CREATE TABLE test_coverage (
    coverage_id INTEGER PRIMARY KEY,
    
    -- What's covered
    function_stable_id TEXT NOT NULL,      -- Which function
    test_path TEXT NOT NULL,               -- Path to test that covers it
    test_name TEXT NOT NULL,               -- Specific test function
    
    -- Coverage details
    coverage_type TEXT,                    -- 'unit' | 'integration' | 'e2e'
    execution_count INTEGER DEFAULT 1,     -- How many times does test run this?
    assertion_count INTEGER DEFAULT 0,     -- How many assertions cover it?
    
    -- Metadata
    last_executed TIMESTAMP,
    is_failing BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(function_stable_id) REFERENCES nodes(stable_id),
    UNIQUE(function_stable_id, test_path)
);

CREATE INDEX idx_coverage_function ON test_coverage(function_stable_id);
CREATE INDEX idx_coverage_test ON test_coverage(test_path);
```

### Building Test Coverage Map

```python
class TestCoverageMapper:
    """Extract test coverage from pytest/unittest"""
    
    def build_from_test_run(db: sqlite3.Connection, test_dir: str):
        """Run tests with coverage, map to functions"""
        
        import subprocess
        import coverage
        
        # Run pytest with coverage
        result = subprocess.run(
            ["pytest", test_dir, "--cov=src", "--cov-report=json"],
            capture_output=True
        )
        
        # Load coverage data
        cov = coverage.Coverage()
        cov.load()
        
        # For each file with coverage data:
        for filename, data in cov.get_data().items():
            lines_executed = data.lines
            
            # Map lines to functions in our call graph
            # For each function in that file:
            #   - Which lines are in that function?
            #   - Are any of those lines in coverage data?
            #   - If yes: function is covered
            
            cursor = db.cursor()
            for func_stable_id, func_lines in self._parse_file(filename):
                covered = any(line in lines_executed for line in func_lines)
                
                if covered:
                    # Find which test covers this
                    test_name = self._trace_test_for_function(
                        func_stable_id, filename, func_lines
                    )
                    
                    cursor.execute("""
                        INSERT INTO test_coverage 
                        (function_stable_id, test_path, test_name, coverage_type, is_failing)
                        VALUES (?, ?, ?, 'unit', FALSE)
                        ON CONFLICT DO UPDATE SET execution_count = execution_count + 1
                    """, (func_stable_id, test_name, test_name))
        
        db.commit()
```

### Query Pattern: Test Coverage Report

```python
def get_test_coverage_for_function(db: sqlite3.Connection, func_stable_id: str) -> Dict:
    """What tests cover this function?"""
    
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_tests,
            COUNT(DISTINCT test_path) as unique_tests,
            AVG(execution_count) as avg_executions
        FROM test_coverage
        WHERE function_stable_id = ?
    """, (func_stable_id,))
    
    coverage_stats = cursor.fetchone()
    
    cursor.execute("""
        SELECT test_path, test_name, execution_count
        FROM test_coverage
        WHERE function_stable_id = ?
        ORDER BY execution_count DESC
    """, (func_stable_id,))
    
    tests = [{"test_path": row[0], "test_name": row[1], "runs": row[2]} 
             for row in cursor.fetchall()]
    
    return {
        "total_tests": coverage_stats[0],
        "unique_tests": coverage_stats[1],
        "avg_executions": coverage_stats[2],
        "tests": tests
    }
```

---

## 4. Integration: Using Hardened Schema

### Complete Impact Analysis Flow

```python
from src.phase32_call_graph_engine import CallGraphDB
from src.reasoning.impact_analyzer import ImpactAnalyzer

# Open database
db = CallGraphDB('.piddy_callgraph.db')

# Get function by stable ID (survives refactors)
func_stable_id = "piddy:src.engine.CallGraphDB.get_callers:abc12345"

# Calculate impact with confidence filtering
impact = db.get_impact_radius_confident(
    func_stable_id, 
    min_confidence=0.85  # Only follow high-confidence edges
)

# Get test coverage for that function
coverage = db.get_test_coverage_for_function(func_stable_id)

# Combine for rich decision context
risk_score = calculate_risk_score(
    callers=impact.total_affected,
    confidence=impact.avg_confidence,
    test_coverage=coverage['total_tests'] / impact.total_affected
)

# Agent decides:
if risk_score < 0.3:
    print("Safe to autonomously refactor")
elif risk_score < 0.7:
    print("Request approval for refactor")
else:
    print("Manual review required")
```

---

## 5. Migration Checklist

- [ ] Backup database before migration
- [ ] Apply Migration 1: Node identity
  - [ ] Run `migrate_1_node_identity()`
  - [ ] Run `compute_qualified_names()`
  - [ ] Verify all nodes have stable_id
- [ ] Apply Migration 2: Confidence
  - [ ] Run `populate_initial_confidence()`
  - [ ] Test: Query with min_confidence filter
- [ ] Apply Migration 3: Test coverage (Phase 32b)
  - [ ] Run `build_from_test_run()`
  - [ ] Test: Query coverage for functions
- [ ] Validation
  - [ ] All foreign keys valid
  - [ ] Indexes created successfully
  - [ ] Query performance meets benchmarks
- [ ] Update application code
  - [ ] Use stable_id for node lookups
  - [ ] Filter by confidence in impact queries
  - [ ] Include coverage in reports

---

## 6. Backward Compatibility

These migrations are designed to be **non-breaking**:

- Old node_id column stays but unused
- New stable_id is UNIQUE so old code can't interfere
- Confidence defaults to 0.95 (conservative, safe)
- Queries work with both old and new columns during transition

Recommended migration window: 1 week at these two column sets existing, then drop old columns.

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| **Node stability** | Breaks on refactor | ✓ Survives moves |
| **Confidence in edges** | Unknown | 85-99% tracked |
| **Test correlation** | Manual tracking | ✓ Automated map |
| **Impact query speed** | Variable | ✓ <500ms |
| **Agent autonomy confidence** | "Maybe safe" | "87% sure safe" |

