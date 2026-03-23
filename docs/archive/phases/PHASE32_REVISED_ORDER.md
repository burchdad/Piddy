# Phase 32: Revised Execution Order

**Based on technical review: Test coverage enables risk scoring immediately, types can wait**

---

## Strategic Reason for Reordering

### Original Order
```
32a: Call Graph
32b: Type System
32c: Service Boundaries
32d: API Contracts
32e: Test Coverage
32f: Reasoning Engine
```

**Problem**: Reason for original order was "build complete picture then reason." But that's backward.

**Better approach**: Complete risk scoring loop ASAP, then add dimensions.

### Revised Order
```
32a: Call Graph           ✅ DONE
32b: Test Coverage        ← Enables immediate risk scoring
32c: Type System          ← Requires infrastructure built by 32b
32d: API Contracts        ← Can proceed independently
32e: Service Boundaries   ← Uses outputs from 32b + 32c
32f: Reasoning Engine     ← Unified layer consuming all above
```

---

## Why This Works Better

### Phase 32a: Call Graph (Done ✅)

**Output:** 
- Which functions call which
- Transitive closure (impact radius)
- Circular dependencies

**Missing:** Confidence in those edges, test coverage, type safety

### Phase 32b: Test Coverage (Move Here ← NEW)

**Input:** Call graph from 32a

**Output:**
- For each function: which tests cover it?
- For each code path: tested or untested?
- Coverage percentage per function

**Why now:**
1. **Enables risk scoring immediately**
   ```
   Change detected
   └─ Callers: 12
   └─ Callers with tests: 11 (92%)
   └─ Risk: LOW
   └─ Agent: Autonomously refactor
   ```

2. **Dead code detection working immediately**
   ```
   Function: never called, never tested
   └─ Status: Dead code
   └─ Action: Safe to delete
   ```

3. **Simpler to implement than types**
   - Execution tracing (easier)
   - vs. Type inference (complex)
   - Builds confidence fast

4. **Foundation for 32c (types)**
   - Path tracking needed for types anyway
   - "which code path was executed?" = essential for type checking
   - Reuse infrastructure built by 32b

### Phase 32c: Type System

**Input:** Call graph + test coverage paths

**Output:**
- Type annotations extracted
- Type compatibility matrix
- Inferred types at call points

**Why after 32b:**
- You understand which paths are tested (from 32b)
- Type checking can focus on high-coverage paths first
- Lower-risk type changes because they're test-backed

### Phase 32d: API Contracts

**Input:** Call graph (can work independently)

**Output:**
- HTTP endpoint mapping
- gRPC contract definitions
- Event schema tracking

**Why parallel with 32c:**
- Independent concern (not about internal functions)
- Can be implemented simultaneously
- Both feed into 32f

### Phase 32e: Service Boundaries

**Input:** Call graph + API contracts + types

**Output:**
- Service dependency graph
- Cross-service coupling metrics
- Microservice split opportunities

**Why after 32c + 32d:**
- Needs type safety to suggest splits
- Needs API contracts to validate boundaries
- Needs to know which services own which APIs

### Phase 32f: Reasoning Engine

**Input:** All of above

**Output:**
- "Is this safe?" → Yes/No/Review Needed
- "Suggest refactorings" → List of safe improvements
- "Detect architectural debt" → Specific fix recommendations

---

## Detailed 32b: Test Coverage Engine

### What It Does

```
Input:  Call graph + test suite
        ↓
        Run tests with coverage tracking
        ↓
        Map which tests touch which functions
        ↓
Output: test_coverage table
        ├─ function → [tests that cover it]
        ├─ coverage percent per function
        └─ coverage percent per path
```

### Example Output

```json
{
  "function": "src.engine.CallGraphDB.get_callers",
  "coverage_percent": 92,
  "tests": [
    {
      "test_name": "test_impact_calculation",
      "test_file": "tests/test_call_graph.py",
      "execution_count": 15,
      "is_failing": false
    },
    {
      "test_name": "test_circular_dependency",
      "test_file": "tests/test_call_graph.py",
      "execution_count": 3,
      "is_failing": false
    }
  ],
  "untested_paths": [
    "error handling when db connection fails"
  ]
}
```

### Implementation Structure

```python
# phase32_test_coverage.py

class TestCoverageExtractor:
    """Extract test → function mapping"""
    
    def extract_from_pytest(test_dir: str) -> TestCoverageMap:
        """Run pytest with coverage.py, extract mapping"""
        
    def extract_from_unittest(test_dir: str) -> TestCoverageMap:
        """Support unittest as well"""

class TestCoverageDB:
    """Persist coverage data in SQLite"""
    
    def store_coverage(coverage_map: TestCoverageMap) -> None:
        """Store in test_coverage table"""
    
    def get_function_coverage(func_stable_id: str) -> FunctionCoverage:
        """Query coverage for a function"""
    
    def get_uncovered_functions() -> List[str]:
        """Find dead code"""
    
    def get_path_coverage(func_id: str, path_description: str) -> float:
        """Coverage for specific path"""

class RiskCalculator:
    """Risk scoring using coverage"""
    
    def calculate_risk(func_id: str, impact_radius: int) -> float:
        """
        Risk = (1 - coverage_percent) × log(impact_radius)
        
        Example:
          - 5 callers, 100% tested → 0.0 risk
          - 5 callers, 50% tested → 0.35 risk
          - 50 callers, 50% tested → 0.7 risk
        """
```

### Agent Integration

```python
# Before Phase 32b
impact = analyzer.get_impact(func_id)
if impact.total_affected < 5:
    agent.proceed()  # Hope not many callers
else:
    agent.request_approval()

# After Phase 32b  
impact = analyzer.get_impact(func_id)
coverage = coverage_db.get_function_coverage(func_id)
risk = risk_calculator.calculate_risk(func_id, impact.total_affected)

if risk < 0.3:
    agent.proceed()  # High confidence: low risk
elif risk < 0.7:
    agent.request_approval(reason=f"Risk: {risk:.0%}")
else:
    agent.escalate()  # Unacceptable risk
```

---

## Timeline: New Phase 32 Schedule

### Week 1: Hardening Foundation
- **Mon-Tue**: Node identity + confidence (Migration 1-2)
- **Wed-Thu**: Incremental rebuilds
- **Fri**: Testing + validation

**Output:** Phase 32a hardened, ready for 32b

### Week 2: Test Coverage (32b)
- **Mon-Wed**: Extract pytest/unittest coverage data
- **Thu-Fri**: Risk scoring integration

**Output:** Phase 32b complete, risk scoring operational

### Week 3: Type System (32c)
- **Mon-Wed**: Type annotation extraction
- **Thu-Fri**: Type compatibility matrix

**Output:** Phase 32c complete, type-safe refactoring possible

### Week 3 (Parallel): API Contracts (32d)
- **Mon-Fri**: Endpoint → function mapping

**Output:** Phase 32d complete, API structure visible

### Week 4: Service Boundaries (32e)
- **Mon-Wed**: Service coupling analysis
- **Thu-Fri**: Split opportunity detection

**Output:** Phase 32e complete, architecture optimization ready

### Week 4 (Parallel): Reasoning Engine (32f)
- **Mon-Fri**: Unified decision making layer

**Output:** Phase 32f complete, production-grade reasoning engine

**Total**: 4 weeks end-to-end (concurrent where possible)

---

## Risk Scoring Formula: From 32b

### Simple Version
```
Risk = (1 - test_coverage_percent) × (log(total_callers) / 5)

Example calculations:
- 2 callers, 100% tested → 0.0
- 2 callers, 50% tested → 0.15 (low)
- 10 callers, 50% tested → 0.35 (medium)
- 50 callers, 20% tested → 0.95 (high)
```

### Advanced Version (After Full Hardening)
```
Risk = (
    (1 - test_coverage_percent) × 0.4 +
    (1 - type_coverage_percent) × 0.3 +
    (1 - edge_confidence) × 0.2 +
    (scope_multiplier) × 0.1
)

where scope_multiplier =
    services_affected / 10 (max 1.0)
```

---

## Success Metrics by Phase

### After Phase 32a ✅
- ✓ Call graphs extracting correctly
- ✓ Impact radius calculating
- ✓ Cycle detection working

### After Phase 32b (New Checkpoint)
- ✓ Test coverage mapping functional
- ✓ Risk scores guiding decisions
- ✓ Dead code identifiable automatically
- ✓ Agent autonomy: 60% → 75%

### After Phase 32c
- ✓ Type compatibility verified
- ✓ Breaking changes detected pre-commit
- ✓ Safe type refactoring possible
- ✓ Agent autonomy: 75% → 85%

### After Phase 32d
- ✓ API contracts tracked
- ✓ Endpoint changes monitored
- ✓ Breaking API detected
- ✓ Agent autonomy: 85% → 90%

### After Phase 32e
- ✓ Service coupling visible
- ✓ Microservice split suggestions
- ✓ Architecture quality scored
- ✓ Agent autonomy: 90% → 93%

### After Phase 32f  
- ✓ Unified reasoning working
- ✓ Multi-dimensional safety analysis
- ✓ Autonomous refactoring at scale
- ✓ Agent autonomy: 93% → 95%+

---

## Recommendation: Start Here

Based on technical review, **Phase 32b (Test Coverage) should be the next focus**.

Reasons:
1. **Immediate ROI**: Enables risk scoring without waiting for types
2. **Simpler than types**: Execution-based (no inference needed)
3. **Foundation for 32c**: Path tracking needed regardless
4. **Agent gains confidence**: 60% → 75% autonomy after this phase
5. **Production-ready risks addressed**: By doing 32a hardening first, then 32b

**Estimated duration**: 5-7 days for complete 32b implementation

**What you'll have after 32b**:
- Phase 32a: Call graphs working reliably ✓
- Phase 32b: Risk scoring functional ✓
- Agent can autonomously refactor with confidence ✓
- Foundation ready for 32c (types) ✓

---

## Open Questions

1. **Should we do 32c and 32d in parallel?** (Yes, recommended - different teams)
2. **PostgreSQL for 32e or stay SQLite through 32f?** (SQLite fine through 32f)
3. **Multi-repo support when?** (Phase 33, after 32f)
4. **Speed priority for 32b?** (Coverage accuracy > speed initially)

---

## Conclusion

Reordering Phase 32 to prioritize test coverage (32b) before types (32c):

✓ Completes immediate risk-scoring loop  
✓ Enables agent autonomy jump (60%→75%)  
✓ Provides foundation for 32c anyway  
✓ Gets to production-grade faster  
✓ Aligns with how senior platforms actually build reasoning

**Recommendation: Proceed with Phase 32 hardening (migration) + Phase 32b (coverage).**

