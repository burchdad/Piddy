# Phase 32: Enhanced Persistent Code Reasoning Engine

**Status**: Planned (Next Generation Component)

**Goal**: Transform Piddy from a graph-based agent into a full code reasoning system with deep semantic understanding, enabling safe, intelligent refactoring and architecture analysis.

---

## Current State (Phase 28-31)

### What Piddy Currently Stores
```
Nodes:
├── Files
├── Functions
├── Classes
└── Modules

Edges:
├── imports
├── calls
├── defines
└── uses

Limited to:
- Basic dependency tracking
- Pattern detection (singleton, factory, etc.)
- Call frequency counts
```

### Gap Analysis
- ❌ No call graphs (function-level execution paths)
- ❌ No type system model (generics, interfaces, hierarchies)
- ❌ No service boundary definition
- ❌ No API contract storage
- ❌ No test coverage mapping
- ❌ No impact radius calculations
- ❌ Limited cross-file reasoning

---

## Phase 32: The Missing Pieces

### 1. Call Graph Enhancement
**What**: Function-level execution path tracking

```
Current:
  module_a.py calls module_b.py (boolean)

Target:
  function_a() → function_b() → function_c()
  ├── parameter types: int, str, dict
  ├── return type: bool
  ├── call frequency: 42 times in tests
  ├── call stack depth: 3
  └── execution time: 12ms avg
```

**Storage**:
```sql
CREATE TABLE call_graphs (
    call_graph_id TEXT PRIMARY KEY,
    caller_id TEXT NOT NULL,           -- function_a
    callee_id TEXT NOT NULL,           -- function_b
    call_stack_depth INT,
    parameter_types TEXT,              -- JSON: ["int", "str"]
    return_type TEXT,
    call_frequency INT,
    execution_time_ms REAL,
    is_async BOOLEAN,
    is_recursive BOOLEAN,
    first_observed TEXT,
    last_observed TEXT,
    FOREIGN KEY (caller_id) REFERENCES nodes(node_id),
    FOREIGN KEY (callee_id) REFERENCES nodes(node_id)
);

CREATE INDEX idx_caller ON call_graphs(caller_id);
CREATE INDEX idx_callee ON call_graphs(callee_id);
CREATE INDEX idx_recursive ON call_graphs(is_recursive);
```

**Implementation Steps**:
1. AST analysis to extract function signatures and calls
2. Runtime instrumentation to track actual call paths
3. Type inference from call sites
4. Recursion detection and cycle identification
5. Performance telemetry collection

---

### 2. Type System Model
**What**: Complete type relationship tracking

```
Current:
  class User { ... }

Target:
  class User:
    ├── interfaces: [Serializable, Validatable]
    ├── inherits_from: BaseModel
    ├── generic_params: [T: str]
    ├── attributes: {
    │   ├── name: TypeRef(str, required=True, default=None)
    │   ├── email: TypeRef(str, required=True, validation=[email_pattern])
    │   └── tags: TypeRef(List[str], required=False)
    │ }
    ├── methods: {
    │   ├── validate(): TypeRef(bool)
    │   └── to_dict(): TypeRef(Dict[str, Any])
    │ }
    ├── union_types: [User | None, User | Admin]
    ├── generic_constraints: ["T must inherit from BaseModel"]
    └── implementations: [5 subclasses]
```

**Storage**:
```sql
CREATE TABLE type_system (
    type_id TEXT PRIMARY KEY,
    type_name TEXT NOT NULL,
    type_kind TEXT,  -- class, interface, union, generic
    language TEXT,
    file_path TEXT,
    line_number INT,
    
    -- Hierarchy
    parent_type_id TEXT,
    is_interface BOOLEAN,
    is_abstract BOOLEAN,
    is_generic BOOLEAN,
    
    -- Generic info
    generic_parameters TEXT,  -- JSON: ["T", "U"]
    generic_constraints TEXT,  -- JSON constraints
    
    -- Union types
    union_members TEXT,  -- JSON: ["User", "None"]
    
    -- Implementations/Subclasses
    implementations TEXT,  -- JSON: ["AdminUser", "GuestUser"]
    FOREIGN KEY (parent_type_id) REFERENCES type_system(type_id)
);

CREATE TABLE type_attributes (
    attr_id TEXT PRIMARY KEY,
    type_id TEXT NOT NULL,
    attribute_name TEXT,
    attribute_type TEXT,
    is_required BOOLEAN,
    default_value TEXT,
    validations TEXT,  -- JSON
    FOREIGN KEY (type_id) REFERENCES type_system(type_id)
);

CREATE TABLE type_methods (
    method_id TEXT PRIMARY KEY,
    type_id TEXT NOT NULL,
    method_name TEXT,
    parameter_types TEXT,  -- JSON
    return_type TEXT,
    is_static BOOLEAN,
    is_async BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES type_system(type_id)
);
```

**Implementation Steps**:
1. Parse type annotations (Python, TypeScript, Java, etc.)
2. Extract generic parameters and constraints
3. Build type hierarchy graph
4. Infer types from usage patterns (ML-based)
5. Track type compatibility and coercion

---

### 3. Service Boundary Detection
**What**: Identify microservice boundaries, domain boundaries, and API separation

```
Current:
  module_a.py imports module_b.py

Target:
  Service: auth_service
  ├── boundary: src/services/auth/
  ├── exposed_apis: [
  │   ├── POST /auth/login - requires(user, password)
  │   ├── POST /auth/logout - requires(token)
  │   └── POST /auth/refresh - requires(token)
  │ ]
  ├── internal_modules: [jwt_handler, session_manager, crypto]
  ├── external_dependencies: [user_service, notification_service]
  ├── data_models: [User, Session, Token]
  ├── database_tables: [users, sessions, tokens]
  ├── events_published: [user.login, user.logout]
  ├── events_consumed: [user.created]
  └── service_contracts: [
      ├── requires: user_service.get_user()
      └── provides: token validation
    ]
```

**Storage**:
```sql
CREATE TABLE service_boundaries (
    service_id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    service_type TEXT,  -- microservice, domain, module
    root_path TEXT,
    description TEXT,
    owner_team TEXT,
    
    -- Boundary enforcement
    is_enforced BOOLEAN,
    public_modules TEXT,  -- JSON
    internal_modules TEXT,  -- JSON
    
    created_at TEXT,
    last_analyzed TEXT
);

CREATE TABLE service_contracts (
    contract_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    contract_type TEXT,  -- provides, requires, publishes, consumes
    contract_name TEXT,
    contract_spec TEXT,  -- JSON: full API spec
    version TEXT,
    stability TEXT,  -- stable, beta, deprecated
    breaking_changes TEXT,  -- JSON
    FOREIGN KEY (service_id) REFERENCES service_boundaries(service_id)
);

CREATE TABLE service_dependencies (
    dep_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    depends_on_service_id TEXT NOT NULL,
    dependency_type TEXT,  -- required, optional, transitive
    contract_id TEXT,
    last_checked TEXT,
    is_circular BOOLEAN,
    FOREIGN KEY (service_id) REFERENCES service_boundaries(service_id),
    FOREIGN KEY (depends_on_service_id) REFERENCES service_boundaries(service_id)
);
```

**Implementation Steps**:
1. Detect service root directories (by convention or config)
2. Extract API endpoints (FastAPI, Flask, Express, etc.)
3. Identify data models per service
4. Map event publishing/consumption
5. Calculate service dependency graph
6. Detect circular dependencies and coupling

---

### 4. API Contract Storage
**What**: Persistent API specifications and schemas

```
Endpoint: POST /users/{id}/settings
├── path: /users/{id}/settings
├── method: POST
├── parameters:
│   ├── path: {id: UUID}
│   ├── query: {include_nested: bool, format: Literal["json", "xml"]}
│   └── body: {settings: UserSettings}
├── request_schema: UserSettingsUpdate (JSON Schema)
├── response_schema: UserSettings (JSON Schema)
├── status_codes:
│   ├── 200: Success
│   ├── 400: Invalid input
│   ├── 401: Unauthorized
│   ├── 404: User not found
│   └── 422: Validation error
├── authentication: OAuth2 with scopes [user:write]
├── rate_limit: 100/hour
├── cache_policy: no-cache
├── deprecation_info: None
├── examples: [...]
├── test_coverage: 85%
└── last_updated: 2026-03-06
```

**Storage**:
```sql
CREATE TABLE api_contracts (
    api_id TEXT PRIMARY KEY,
    service_id TEXT NOT NULL,
    endpoint_path TEXT,
    http_method TEXT,
    description TEXT,
    
    -- Specifications
    path_params_schema TEXT,  -- JSON Schema
    query_params_schema TEXT,
    request_body_schema TEXT,
    response_schema TEXT,
    status_codes TEXT,  -- JSON
    
    -- Metadata
    authentication_required BOOLEAN,
    authentication_type TEXT,
    required_scopes TEXT,
    rate_limit TEXT,
    cache_policy TEXT,
    
    -- Quality metrics
    test_coverage_percent REAL,
    deprecation_status TEXT,
    stability TEXT,
    
    created_at TEXT,
    last_modified TEXT,
    sunset_date TEXT,
    
    FOREIGN KEY (service_id) REFERENCES service_boundaries(service_id)
);

CREATE TABLE api_examples (
    example_id TEXT PRIMARY KEY,
    api_id TEXT NOT NULL,
    example_type TEXT,  -- request, response, error
    example_data TEXT,  -- JSON
    description TEXT,
    FOREIGN KEY (api_id) REFERENCES api_contracts(api_id)
);

CREATE TABLE api_status_codes (
    status_code_id TEXT PRIMARY KEY,
    api_id TEXT NOT NULL,
    status_code INT,
    description TEXT,
    error_schema TEXT,  -- JSON Schema
    FOREIGN KEY (api_id) REFERENCES api_contracts(api_id)
);
```

**Implementation Steps**:
1. Parse OpenAPI/GraphQL schemas
2. Extract endpoint metadata from decorators
3. Generate JSON Schemas from type definitions
4. Track endpoint changes and deprecations
5. Link test files to API contracts

---

### 5. Test Coverage Map
**What**: Persistent mapping of test coverage to code

```
Function: user_service.authenticate()
├── total_lines: 15
├── covered_lines: 12
├── coverage_percent: 80%
├── branch_coverage: 75%
├── tests:
│   ├── test_authenticate_valid_credentials
│   ├── test_authenticate_invalid_password
│   ├── test_authenticate_expired_token
│   ├── test_authenticate_user_not_found
│   └── test_authenticate_rate_limited
├── gaps:
│   ├── line_8: token expiration edge case
│   └── line_14: exception handling
├── test_performance:
│   ├── avg_execution_time_ms: 12
│   └── slowest_test_ms: 45
└── quality_score: 80/100
```

**Storage**:
```sql
CREATE TABLE test_coverage (
    coverage_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,  -- function, class, or file
    node_type TEXT,
    total_lines INT,
    covered_lines INT,
    coverage_percent REAL,
    branch_coverage_percent REAL,
    
    -- Gap analysis
    uncovered_lines TEXT,  -- JSON: line numbers
    uncovered_branches TEXT,  -- JSON
    
    last_measured TEXT,
    measurement_tool TEXT,  -- pytest, coverage.py, etc.
    
    FOREIGN KEY (node_id) REFERENCES nodes(node_id)
);

CREATE TABLE test_cases (
    test_id TEXT PRIMARY KEY,
    coverage_id TEXT NOT NULL,
    test_file_path TEXT,
    test_name TEXT,
    execution_time_ms REAL,
    status TEXT,  -- pass, fail, skip
    
    -- Coverage detail
    lines_covered TEXT,  -- JSON
    branches_covered TEXT,  -- JSON
    
    last_run TEXT,
    FOREIGN KEY (coverage_id) REFERENCES test_coverage(coverage_id)
);
```

**Implementation Steps**:
1. Parse coverage reports (coverage.py, pytest-cov, etc.)
2. Map coverage to specific code locations
3. Track test execution times
4. Identify covered vs. uncovered branches
5. Analyze test quality metrics (mutation testing)

---

## Reasoning Capabilities Unlocked

### 1. Impact Radius Calculation
**Query**: "What breaks if I change this function?"

```python
def calculate_impact_radius(function_id: str) -> ImpactAnalysis:
    """
    Follow the call graph outward from function_id:
    1. Find all direct callers (via call_graphs table)
    2. For each caller, find their callers (BFS traversal)
    3. Check type compatibility (via type_system)
    4. Filter by test coverage (via test_coverage)
    5. Identify service boundaries (via service_boundaries)
    
    Returns:
    - Direct impact: 5 functions, 2 services
    - Indirect impact: 23 functions, 5 services
    - Untested impact: 8 functions (16% untested in call chain)
    - Service contracts affected: 3
    - Recommended test additions: [...]
    """
```

### 2. Safe Refactoring
**Query**: "Can I extract this into a helper function?"

```python
def propose_safe_refactoring(lines: List[int], file_id: str) -> RefactoringPlan:
    """
    1. Extract selected lines into new function
    2. Infer parameter types from usage (type_system)
    3. Check for captured variables and state
    4. Verify no service boundary violations
    5. Calculate impact radius of new function
    6. Suggest test cases to add
    7. Verify type compatibility with all call sites
    8. Generate rollback plan
    """
```

### 3. Cross-File Reasoning
**Query**: "How does data flow from API endpoint to database?"

```python
def trace_data_flow(api_id: str) -> DataFlowMap:
    """
    1. Start at API endpoint (via api_contracts)
    2. Follow function calls (call_graphs)
    3. Track data transformations (type_system)
    4. Identify type conversions/coercions
    5. Find database operations
    6. Map to ORM models
    7. Identify validation points
    8. Check for security concerns (SQL injection, etc.)
    
    Returns:
    - Complete data flow from request to DB
    - Type changes at each step
    - Potential issues/improvements
    """
```

### 4. Architecture Analysis
**Query**: "Is our architecture clean? Any coupling issues?"

```python
def analyze_architecture() -> ArchitectureReport:
    """
    1. Map all service boundaries (service_boundaries)
    2. Calculate coupling metrics (inter-service calls)
    3. Detect circular dependencies (service_dependencies)
    4. Measure module cohesion within services
    5. Check API versioning consistency
    6. Analyze test distribution (test_coverage)
    7. Identify single points of failure
    8. Calculate maintainability index
    """
```

---

## Implementation Roadmap

### Phase 32a: Call Graph Engine (Week 1)
**Deliverables**:
- [ ] `CallGraph` class with AST analysis
- [ ] Call graph extraction for all supported languages
- [ ] Runtime call tracing infrastructure
- [ ] Call frequency and performance tracking
- [ ] Recursion detection and cycle identification
- [ ] Integration with persistent graph

**Files to Create**:
- `src/phase32_call_graph_engine.py` (500 lines)
- `src/reasoning/call_graph.py` (400 lines)
- `src/tools/call_graph_analyzer.py` (300 lines)

### Phase 32b: Type System Model (Week 2)
**Deliverables**:
- [ ] Type extraction from annotations
- [ ] Generic parameter tracking
- [ ] Type hierarchy building
- [ ] Type compatibility checking
- [ ] Union and intersection type support
- [ ] Type inference engine

**Files to Create**:
- `src/phase32_type_system.py` (600 lines)
- `src/reasoning/type_relationships.py` (500 lines)
- `src/inference/type_inference.py` (400 lines)

### Phase 32c: Service Boundary Detection (Week 3)
**Deliverables**:
- [ ] Service root detection
- [ ] Boundary enforcement rules
- [ ] Contract extraction
- [ ] Dependency graph building
- [ ] Circular dependency detection
- [ ] API surface mapping

**Files to Create**:
- `src/phase32_service_boundaries.py` (550 lines)
- `src/reasoning/service_contracts.py` (450 lines)
- `src/tools/boundary_analyzer.py` (350 lines)

### Phase 32d: API Contract Storage (Week 3)
**Deliverables**:
- [ ] OpenAPI/GraphQL parsing
- [ ] Endpoint metadata extraction
- [ ] Schema generation
- [ ] Status code documentation
- [ ] Example storage and retrieval
- [ ] Deprecation tracking

**Files to Create**:
- `src/phase32_api_contracts.py` (500 lines)
- `src/reasoning/api_specifications.py` (400 lines)

### Phase 32e: Test Coverage Map (Week 4)
**Deliverables**:
- [ ] Coverage report parsing
- [ ] Coverage-to-code mapping
- [ ] Gap analysis
- [ ] Test execution tracking
- [ ] Quality metrics calculation
- [ ] Uncovered branch identification

**Files to Create**:
- `src/phase32_test_coverage.py` (450 lines)
- `src/reasoning/coverage_analysis.py` (350 lines)

### Phase 32f: Reasoning Engines (Week 4)
**Deliverables**:
- [ ] Impact radius calculator
- [ ] Safe refactoring proposer
- [ ] Data flow tracer
- [ ] Architecture analyzer
- [ ] Integration with agent decision-making

**Files to Create**:
- `src/phase32_reasoning_engines.py` (700 lines)
- `src/reasoning/impact_analysis.py` (300 lines)
- `src/reasoning/refactoring_planner.py` (350 lines)
- `src/reasoning/architecture_analyzer.py` (300 lines)

---

## Database Schema Summary

```
EXISTING (Phase 28):
├── nodes (file, function, class, module)
├── edges (imports, calls, defines, uses)
├── patterns (learned patterns)
└── query_cache

NEW (Phase 32):
├── call_graphs (function-level call paths)
├── type_system (type definitions)
├── type_attributes (attribute types)
├── type_methods (method signatures)
├── service_boundaries (service definitions)
├── service_contracts (API contracts)
├── service_dependencies (service relationships)
├── api_contracts (endpoint specifications)
├── api_examples (endpoint examples)
├── api_status_codes (status code specs)
├── test_coverage (coverage metrics)
└── test_cases (individual test tracking)

Total Tables: 23
Total Indexes: 40+
Estimated Size: 50MB - 500MB depending on codebase
```

---

## Queries That Will Be Possible

### Basic Queries
```sql
-- Find all tests for a function
SELECT t.test_name FROM test_cases t
JOIN test_coverage tc ON t.coverage_id = tc.coverage_id
WHERE tc.node_id = 'func_12345';

-- Get all callers of a function
SELECT DISTINCT cg.caller_id, n.name
FROM call_graphs cg
JOIN nodes n ON cg.caller_id = n.node_id
WHERE cg.callee_id = 'func_12345'
ORDER BY cg.call_frequency DESC;

-- Find all type violations
SELECT DISTINCT cg.caller_id, cg.callee_id
FROM call_graphs cg
JOIN type_methods tm_caller ON cg.caller_id = tm_caller.method_id
WHERE NOT is_type_compatible(
    tm_caller.return_type,
    cg.parameter_types->0
);
```

### Advanced Reasoning Queries
```python
# Impact radius
SELECT * FROM calculate_impact_radius('func_12345')
-- Returns: direct impact graph, indirect impact, untested paths, affected services

# Refactoring safety check
SELECT * FROM check_refactoring_safety('func_12345', ['func_67890', 'func_11111'])
-- Returns: type compatibility, service violations, required tests

# Architecture metrics
SELECT * FROM calculate_architecture_metrics()
-- Returns: coupling, cohesion, complexity, maintainability scores
```

---

## Success Metrics

### Accuracy
- Impact radius calculation: 95%+ accuracy in predicting breaking changes
- Safe refactoring: 0 critical bugs from refactorings done with system guidance
- Type checking: 99%+ type compatibility matches static analysis tools

### Performance
- Impact radius calculation: <500ms for 100K-node graphs
- Service boundary analysis: <1s for multi-service analysis
- API contract changes: Detected within 1s of code change

### Reliability
- Graph consistency: No orphaned edges or nodes
- Type inference: <5% false positives
- Coverage accuracy: Match with pytest/coverage.py within ±2%

### Adoption
- Agent uses reasoning in 80%+ of decisions
- Safe refactoring success rate: >99%
- Developer confidence increase: >40%

---

## Technology Stack

### Core Components
- **Database**: SQLite (single machine) → PostgreSQL (distributed)
- **Graph Traversal**: Custom BFS/DFS with caching
- **Type Inference**: Hindley-Milner with constraint propagation
- **Static Analysis**: AST parsing + bytecode inspection
- **Runtime Instrumentation**: sys.settrace() for Python, similar for other languages

### Integration Points
- Phase 28 Persistent Graph API
- Phase 23 RKG reasoning
- Phase 30 Multi-Agent Protocol
- Existing tool framework

### Optional Enhancements
- GraphQL API for reasoning queries
- Machine learning for pattern discovery
- Distributed querying for multi-repo analysis

---

## Risk Mitigation

### Data Corruption Risk
- ✅ Transaction-based writes
- ✅ Automatic backups before major updates
- ✅ Integrity constraints in schema
- ✅ Repair utilities for graph reconstruction

### Performance Risk
- ✅ Incremental graph updates (not full recomputation)
- ✅ Query result caching
- ✅ Index optimization for common queries
- ✅ Horizontal scaling via PostgreSQL

### Accuracy Risk
- ✅ Cross-validation with static analysis tools
- ✅ Test suite for inference engine
- ✅ Human review of critical decisions
- ✅ Continuous accuracy metrics

---

## Next Steps (Immediate)

1. **Architecture Review**: Get feedback on schema design
2. **Performance Model**: Estimate query times on real codebases
3. **Prototype Sprint**: Build call graph engine as MVP
4. **Integration Plan**: Map to Phase 28-31 APIs
5. **Testing Strategy**: Design test coverage for reasoning engines

---

## Questions for Validation

1. **Priority**: Call graphs vs. type system first? (Recommend: call graphs for immediate impact)
2. **Scope**: Start with Python-only or multi-language? (Recommend: Python first, scale)
3. **Distribution**: SQLite embedded vs. PostgreSQL? (Recommend: SQLite for Phase 32, PostgreSQL for Phase 33)
4. **Reasoning**: Start with deterministic or ML-based? (Recommend: deterministic, add ML in Phase 33)

