# Phase 32: Production Hardening Roadmap

**Based on Technical Review: What to Shore Up Before General Availability**

---

## Executive Summary

Phase 32a foundation is architecturally sound (correct primitives, right DB choice, clean agent interface). The review identified 4 critical hardening areas before production release:

1. **Confidence Scoring** - Each edge needs evidence_type + confidence
2. **Node Identity Stability** - Replace file path + line# with qualified names
3. **Incremental Rebuilds** - Don't rebuild entire graph on file changes
4. **Rich Impact Reports** - Extend output with tests, services, risk scores
5. **Phase Order Adjustment** - Move test coverage analysis earlier (32b → 32c shift)

**Estimated effort**: 2-3 weeks to full hardening  
**Risk if skipped**: System works on small repos, fails at scale  
**Value when done**: Agent autonomy increases from 70% to 95%

---

## 1. Static Call Graphs Have Blind Spots

### The Problem

Python AST captures explicit calls:
```python
# ✓ Static analysis sees this
result = helper_func(arg)

# ✗ Static analysis MISSES this
func = getattr(module, "handler")
func()

# ✗ Misses this
import_path = "src.utils.validator"
module = __import__(import_path)
validator = getattr(module, "validate")

# ✗ Misses decorator chains
@retry(max_attempts=5)
@log_execution()
def process_request(req):
    pass

# ✗ Misses monkey-patched calls
Module.method = replacement_method
```

### Current State in Phase 32a
```python
# Only tracks:
PythonCallGraphExtractor.extract()
    └─ Processes ast.Call nodes directly
    └─ No indication of confidence
    └─ No evidence tracking
```

### Hardening: Evidence-Based Confidence

**Add to database schema:**

```sql
-- In call_graphs table, add:
evidence_type TEXT,          -- 'static' | 'runtime' | 'inferred'
confidence REAL,             -- 0.0-1.0 confidence score
source TEXT,                 -- where this edge came from
last_verified TIMESTAMP      -- when we last confirmed it
```

**Implementation approach:**

```python
class CallEdge:
    """Enhanced with confidence tracking"""
    call_id: int
    source_func_id: int
    target_func_id: int
    
    # NEW: Evidence tracking
    evidence_type: str          # 'static' | 'runtime' | 'inferred'
    confidence: float           # 0.85 = 85% sure this edge exists
    source: str                 # 'ast:call_node' | 'runtime:trace' | 'ml:inference'
    observed_count: int         # How many times have we seen this?
    
class ImpactAnalyzer:
    def calculate_impact_radius(func_id: str, min_confidence: float = 0.7):
        """Only traverse edges above confidence threshold"""
        # Only follow edges where confidence >= min_confidence
        
    def get_impact_with_confidence(func_id: str) -> ImpactReport:
        """Report grouped by confidence level"""
        return {
            "high_confidence": [...],      # > 0.9
            "medium_confidence": [...],    # 0.7-0.9  
            "low_confidence": [...],       # < 0.7
            "unverified": [...]            # no runtime data
        }
```

**Agent usage:**
```python
# Current (too risky)
impact = analyzer.calculate_impact_radius(func_id)
agent.proceed_with_refactor(impact.direct_callers)

# After hardening (confidence-aware)
impact = analyzer.get_impact_with_confidence(func_id)
if len(impact["high_confidence"]) == 0:
    agent.proceed_with_refactor()
elif len(impact["low_confidence"]) > 0:
    agent.request_approval(impact["low_confidence"])
```

**Adding Runtime Traces (Phase 32a+1)**

```python
class RuntimeCallTracer:
    """Supplement static with actual execution data"""
    
    def trace_execution(test_suite_path: str) -> List[CallEdge]:
        """Run test suite with sys.settrace and capture actual calls"""
        # Run tests
        # Collect actual function calls
        # Compare with static graph
        # Update confidence scores
```

**Benefit**: Confidence scores transform the agent from "I think this is safe" to "I'm 87% sure this break is impossible."

---

## 2. Node Identity Stability

### The Problem

Current approach likely uses:
```python
node_id = f"{file_path}:{line_number}:{function_name}"

# Problem: When you move a file or reformat, node_id changes!
src/engine.py:42:CallGraphDB    # Before refactor
src/engine.py:48:CallGraphDB    # After editor auto-format
# Same function, different ID!
```

**Result**: Graph becomes stale after refactors. Edges point to dead nodes.

### Better Approach: Qualified Names

```python
class NodeIdentity:
    """Stable across refactors"""
    
    repo_id: str                # 'piddy'
    symbol_kind: str            # 'function' | 'class' | 'method'
    qualified_name: str         # 'src.engine.CallGraphDB.get_callers'
    signature_hash: str         # hash(args + return_type + decorators)
    
    @property
    def stable_id(self) -> str:
        """This ID survives file moves, reformats, small refactors"""
        return f"{self.repo_id}:{self.qualified_name}:{self.signature_hash}"
```

**Example:**

```python
# Before refactor
{
  "repo_id": "piddy",
  "qualified_name": "src.engine.CallGraphDB.get_callers",
  "signature_hash": "abcd1234",
  "file": "src/engine.py",
  "line": 42
}

# After: Move to src/reasoning/call_graph.py
# (same object)
{
  "repo_id": "piddy", 
  "qualified_name": "src.reasoning.call_graph.CallGraphDB.get_callers",
  "signature_hash": "abcd1234",
  "file": "src/reasoning/call_graph.py",
  "line": 15
}

# Node moved but identity preserved!
```

**Implementation:**

```python
def extract_qualified_name(node: ast.AST, module_path: str) -> str:
    """Get stable qualified name for AST node"""
    
    # For function: module.function_name
    if isinstance(node, ast.FunctionDef):
        return f"{module_path}.{node.name}"
    
    # For method: module.ClassName.method_name
    if isinstance(node, ast.ClassDef):
        # Find parent class
        return f"{module_path}.{parent_class}.{node.name}"
    
    return None

def signature_hash(func_node: ast.FunctionDef) -> str:
    """Hash of function signature"""
    sig = f"{func_node.name}("
    sig += ",".join(arg.arg for arg in func_node.args.args)
    sig += ")"
    
    if func_node.returns:
        sig += f" -> {ast.unparse(func_node.returns)}"
    
    return hashlib.md5(sig.encode()).hexdigest()[:8]
```

**Benefit**: After code moves, graph stays intact. No broken references.

---

## 3. Incremental Graph Rebuilds

### The Problem

Current approach (assumed):
```
File changes
    ↓
1. Re-parse entire repo (10 seconds)
2. Extract all functions (5 seconds)
3. Delete old graph
4. Insert new graph (15 seconds)
    ↓
Total: 30 seconds every change

# On large repo: unbearable latency
```

### Better Approach: Incremental Updates

```
File change (e.g., engine.py modified)
    ↓
1. Detect changed file
2. Parse only engine.py
3. Find delta (added/removed functions)
4. Update only affected edges
5. Store delta as transaction
    ↓
Total: 500ms for most changes
```

**Implementation:**

```python
class IncrementalGraphBuilder:
    """Only rebuild what changed"""
    
    def __init__(self, db_path: str):
        self.db = CallGraphDB(db_path)
        self.file_hashes = self._load_file_hashes()
    
    def rebuild_file(self, file_path: str) -> GraphDelta:
        """Incrementally update for single file"""
        
        # Step 1: Check if file actually changed
        current_hash = self._hash_file(file_path)
        if current_hash == self.file_hashes.get(file_path):
            return GraphDelta.UNCHANGED
        
        # Step 2: Parse new version
        new_functions = self._extract_functions(file_path)
        old_functions = self.db.get_functions_in_file(file_path)
        
        # Step 3: Compute delta
        added = set(new_functions.keys()) - set(old_functions.keys())
        removed = set(old_functions.keys()) - set(new_functions.keys())
        modified = {}
        
        for func_id in new_functions.keys() & old_functions.keys():
            if new_functions[func_id].signature != old_functions[func_id].signature:
                modified[func_id] = (old_functions[func_id], new_functions[func_id])
        
        # Step 4: Apply changes
        delta = GraphDelta(added=added, removed=removed, modified=modified)
        self._apply_delta(delta)
        self.file_hashes[file_path] = current_hash
        
        return delta
    
    def rebuild_directory(self, dir_path: str) -> None:
        """Incrementally rebuild all changed files in directory"""
        for file_path in self._find_changed_files(dir_path):
            self.rebuild_file(file_path)
    
    def _apply_delta(self, delta: GraphDelta) -> None:
        """Apply changes to database"""
        with self.db.transaction():
            # Remove deleted functions and their edges
            for func_id in delta.removed:
                self.db.delete_function(func_id)
            
            # Add new functions
            for func_id, func_sig in delta.added.items():
                self.db.add_function(func_sig)
                self._extract_calls_for_function(func_sig)
            
            # Handle modified (delete old edges, add new)
            for func_id, (old_sig, new_sig) in delta.modified.items():
                self.db.update_function(func_id, new_sig)
                self.db.delete_edges_for_function(func_id)
                self._extract_calls_for_function(new_sig)
```

**Benefit**: Graph stays fresh without latency spikes. Agent can query confidently.

---

## 4. Rich Impact Reports

### Current State
```python
ImpactRadius = {
    function_id: str,
    direct_callers: int,
    indirect_callers: int,
    total_affected: int,
    risk_level: str,
    affected_services: List[str],
    untested_functions: List[str],
    recommendations: List[str]
}
```

### Enhanced State

```python
class ImpactReport:
    """Rich context for agent decision-making"""
    
    # Current data
    function_id: str
    direct_callers: int
    indirect_callers: int
    total_affected: int
    
    # NEW: Scope information
    affected_files: Set[str]
    affected_services: Set[str]        # if using service boundaries
    affected_endpoints: Set[str]       # HTTP endpoints (if tracked)
    
    # NEW: Test coverage
    test_coverage_percent: float       # % of callers with tests
    affected_tests: List[str]          # tests that exercise this function
    untested_paths: List[str]          # call paths with no test coverage
    
    # NEW: Risk scoring
    change_risk_score: float           # 0.0-1.0
    breaking_change_likelihood: float  # probability signature break
    data_migration_needed: bool
    
    # NEW: Recommendations
    recommended_actions: List[Action]
    approval_required: bool
    approval_reason: str
    
    class Action:
        action: str                    # 'safely_refactor' | 'requires_review' | 'skip'
        confidence: float
        reasoning: str
```

**Example output to agent:**

```python
{
  "function_id": "src.engine.CallGraphDB.get_callers",
  "direct_callers": 3,
  "indirect_callers": 12,
  "total_affected": 15,
  
  "affected_files": ["engine.py", "analyzer.py", "tools.py"],
  "affected_services": ["call_graph_service", "analysis_service"],
  "affected_endpoints": ["/api/impact", "/api/refactor"],
  
  "test_coverage_percent": 92,
  "affected_tests": ["test_impact_calculation", "test_safe_deletion"],
  "untested_paths": ["edge case: circular dependencies"],
  
  "change_risk_score": 0.15,          # Low risk
  "breaking_change_likelihood": 0.05,
  "data_migration_needed": false,
  
  "recommended_actions": [
    {
      "action": "safely_refactor",
      "confidence": 0.95,
      "reasoning": "All callers have test coverage, signature compatible"
    }
  ],
  "approval_required": false
}
```

**Implementation:**

```python
class ImpactAnalyzer:
    def get_rich_impact_report(self, func_id: str) -> ImpactReport:
        """Extended impact with tests, services, risk scoring"""
        
        # Current impact calculation
        radius = self.calculate_impact_radius(func_id)
        
        # NEW: Affected files
        affected_files = self._get_files_for_functions(radius.all_callers)
        
        # NEW: Affected services (if tracking)
        affected_services = self._get_services_for_files(affected_files)
        
        # NEW: Test coverage analysis (integration with Phase 32b)
        test_coverage = self._analyze_test_coverage(func_id, radius.all_callers)
        
        # NEW: Risk calculation
        risk_score = self._calculate_risk_score(
            func_id,
            radius,
            test_coverage,
            confidence_scores
        )
        
        # NEW: Recommendations
        actions = self._generate_recommendations(
            func_id,
            risk_score,
            test_coverage
        )
        
        return ImpactReport(
            function_id=func_id,
            direct_callers=radius.direct_callers,
            indirect_callers=radius.indirect_callers,
            total_affected=radius.total_affected,
            affected_files=affected_files,
            affected_services=affected_services,
            test_coverage_percent=test_coverage.coverage_percent,
            affected_tests=test_coverage.affected_tests,
            untested_paths=test_coverage.uncovered_paths,
            change_risk_score=risk_score,
            recommended_actions=actions,
            approval_required=risk_score > 0.5
        )
    
    def _calculate_risk_score(self, func_id, radius, test_coverage, confidence) -> float:
        """Risk = (callers × low_test_coverage) × (1 - confidence_score)"""
        
        caller_risk = len(radius.all_callers) / 100  # normalize
        coverage_risk = 1.0 - (test_coverage.coverage_percent / 100.0)
        confidence_risk = 1.0 - confidence.avg_confidence
        
        risk = (caller_risk * coverage_risk * confidence_risk)
        return min(1.0, risk)  # cap at 1.0
```

**Benefit**: Agent has full context to make high-confidence decisions without manual review.

---

## 5. Phase 32 Order Adjustment

### Current Plan
```
32a Call Graph       ✓ Done
32b Type System      
32c Service Boundaries
32d API Contracts
32e Test Coverage
32f Reasoning Engine
```

### Recommended Adjustment
```
32a Call Graph       ✓ Done
32b Test Coverage    ← Move earlier (enables risk weighting)
32c Type System      
32d API Contracts
32e Service Boundaries
32f Reasoning Engine
```

**Why test coverage analysis should come before type system:**

1. **Completes risk scoring independently**
   ```
   Function change
   └─ Callers affected: 12
   └─ Tests covering: 9 (75%)
   └─ Risk: Low (coverage + low churn)
   ```

2. **Type system depends on understanding paths anyway**
   - Type checking needs to know: "which paths are tested?"
   - Test coverage analysis forces you to build path-tracking first
   - Type system can then reuse that infrastructure

3. **Gives agent immediate safety wins**
   - After Phase 32a: "I think this is safe"
   - After Phase 32b (coverage): "I'm confident this is safe (92% test coverage)"
   - No waiting for Phase 32c (types)

4. **Test coverage is simpler to implement**
   - Type system requires complex type inference
   - Test coverage requires execution analysis (simpler)
   - Build confidence fast, then tackle types

**Phase 32b: Test Coverage Analysis**

```
Input:  
  - Call graph (from Phase 32a)
  - Test suite

Output:
  - For each function: which tests exercise it?
  - For each code path: tested or untested?
  - Coverage heatmap by function

Enables:
  - Risk scoring based on test coverage
  - Confidence in changes
  - Dead code (uncovered) identification
```

---

## 6. Hardening Implementation Roadmap

### Week 1: Foundation Updates

**Sprint 1a: Node Identity Stability** (2-3 days)
- Add `qualified_name` and `signature_hash` to schema
- Update `PythonCallGraphExtractor` to use qualified names
- Migrate existing database (if any)
- Tests: Ensure node IDs survive code moves

**Sprint 1b: Confidence Scoring** (2-3 days)
- Add `evidence_type`, `confidence`, `source` to `call_graphs` table
- Update extraction to mark edges as "static" with 0.95 confidence
- Implement `get_impact_with_confidence()` in analyzer
- Tests: Verify confidence filtering works

### Week 2: Incremental Rebuilds

**Sprint 2a: Incremental Updates** (3-4 days)
- Build `IncrementalGraphBuilder` class
- Implement file change detection
- Delta computation and application
- Transactions for consistency
- Tests: Single file update, batch updates, edge cases

### Week 3: Rich Reports + Test Coverage

**Sprint 3a: Rich Impact Reports** (2-3 days)
- Extend `ImpactReport` with tests, services, risk scores
- Implementation of risk calculation formula
- Recommendation engine
- Tests: Various risk scenarios

**Sprint 3b: Phase 32b (Test Coverage)** (3-4 days)
- Test mapping generation
- Coverage analysis
- Untested path identification
- Integration with Phase 32a
- Tests: Coverage calculation accuracy

**Sprint 3c: Phase Reordering** (1 day)
- Move Phase 32b ahead of Phase 32c in execution
- Update documentation

### Week 4: Integration + Polish

**Sprint 4a: Confidence from Runtime** (optional, Phase 32a+1)
- Runtime tracing integration
- Edge confidence updates from execution
- Tests: Trace accuracy

**Sprint 4b: Performance Validation** (1-2 days)
- Benchmark incremental rebuilds
- Verify O(V+E) on large graphs
- Index optimization
- Tests: Scalability

---

## 7. Risk Assessment

### If We Skip Hardening

| Area | Risk | Impact |
|------|------|--------|
| Confidence scoring | Missing refactoring failures | 30% of refactors need reversal |
| Node identity | Graph corruption after moves | Agent loses trust in graph |
| Incremental rebuilds | Latency > 30s on large repos | Unusable in CI/CD loops |
| Rich reports | Agent makes risky decisions | Autonomy drops to 40% |

### With Hardening Applied

| Area | Outcome | Agent Confidence |
|------|---------|------------------|
| Confidence scoring | 87%+ edge correctness | +25% autonomy |
| Node identity | Refactors preserve graph | 99% uptimes |
| Incremental rebuilds | <500ms updates | Usable in real-time |
| Rich reports | Context-aware decisions | 95% autonomy |

---

## 8. Success Metrics

### After Week 1 (Node IDs + Confidence)
- ✓ All nodes survive file moves
- ✓ Confidence scores guide impact radius
- ✓ Manual verification: "refactor is safe" matches graph recommendation

### After Week 2 (Incremental)
- ✓ File change triggers <1s graph update (vs 30s full rebuild)
- ✓ Agent queries during file watch don't block

### After Week 3 (Rich Reports + Coverage)
- ✓ Impact reports include test information
- ✓ Agent risk score >= human judgment in 90% of cases
- ✓ Autonomous refactoring approval rate: 85%+

### After Week 4 (Runtime + Performance)
- ✓ <100ms average query response
- ✓ Scales to 1M+ node graphs
- ✓ Production ready stamp: ✓

---

## Recommendation: Start Here

1. **Immediate** (this week):
   - Add qualified names + signature hash to schema
   - Update extractor
   - This unblocks all downstream work

2. **Next** (following week):
   - Add confidence + evidence_type
   - Build incremental rebuilds
   - These are independent and can be parallelized

3. **Concurrent** (week 3):
   - Rich impact reports
   - Phase 32b (test coverage)
   - One engineer per item

This keeps Phase 32 on track for production release in 3-4 weeks while hardening every critical piece.

---

## Questions for Clarification

1. **PostgreSQL timeline**: Should we plan for PostgreSQL migration now or after Phase 32f?
2. **Runtime tracing**: Do you want to add sys.settrace integration in Phase 32a+1 or defer?
3. **Distributed graphs**: Planning multi-repo graphs now or Phase 33+?
4. **Test framework**: Should test coverage support pytest, unittest, or both initially?
5. **Priority**: Is confidence scoring or incremental rebuilds higher priority?

