# Piddy's Next Evolution: Strategic Roadmap

**Date**: March 6, 2026
**Current Phase**: 31 (Production Ready for Deployment)
**Recommended Next Phase**: 32 (Persistent Code Reasoning Engine)

---

## The Core Insight

Piddy today is **graph-aware** but not **semantically intelligent**.

**Current Reality**:
```
Piddy stores:
├── Files
├── Functions  
├── Classes
└── Basic dependencies (imports/calls/defines)

Piddy can answer:
├── "What files are involved?"
├── "What functions exist?"
└── "What depends on what?"

Piddy CANNOT reliably answer:
├── "Is it safe to delete this function?"          ← Needs call graph
├── "What breaks if I change this?"                ← Needs impact analysis
├── "Can I refactor this safely?"                  ← Needs type system + call graph
├── "What's the architecture of this service?"     ← Needs service boundaries
└── "Is our code architecture clean?"              ← Needs all of above
```

**Why This Matters**:
- **Today**: Agents make code changes but need human validation
- **Tomorrow**: Agents can make confident, safe changes independently
- **Difference**: Persistent code reasoning engine

---

## The Five Missing Pieces (Phase 32)

### 1. **Call Graphs** (Week 1) - HIGHEST PRIORITY
**What**: Function-level execution paths

```
Current:  module_a calls module_b
Target:   function_a() → function_b(int, str) → function_c(bool)
                         └─ call_frequency: 42
                         └─ execution_time: 12ms
                         └─ test_coverage: 85%
```

**Unlocks**: Safe deletion, impact radius, refactoring validation

### 2. **Type System** (Week 2)
**What**: Complete type relationships and compatibility

```
Current:  class User
Target:   class User: Serializable, Validatable
            └─ attributes: {name: str (required), tags: List[str] (optional)}
            └─ methods: {validate() → bool, to_dict() → Dict}
            └─ implementations: [AdminUser, GuestUser]
```

**Unlocks**: Type-safe refactoring, data flow analysis, generic parameter tracking

### 3. **Service Boundaries** (Week 3)
**What**: Microservice and domain boundaries

```
Current:  src/services/auth/ has files
Target:   Auth Service (exposed APIs: /login, /logout)
          └─ requires: user_service, notification_service
          └─ publishes: user.login, user.logout events
          └─ data models: [User, Session, Token]
          └─ breaking changes: none (stable)
```

**Unlocks**: Architecture analysis, coupling metrics, safe cross-service changes

### 4. **API Contracts** (Week 3-4)
**What**: Persistent endpoint specifications

```
Current:  POST /users/{id}  exists
Target:   POST /users/{id}
          ├─ request: {name: str, email: str}
          ├─ response: {id: UUID, name: str, ...}
          ├─ status codes: [200, 400, 401, 404, 422]
          ├─ test_coverage: 85%
          ├─ deprecation: none
          └─ examples: [...]
```

**Unlocks**: Breaking change detection, documentation generation, endpoint testing

### 5. **Test Coverage Map** (Week 4)
**What**: Test-to-code mapping

```
Current:  test_coverage = 85%
Target:   function_name: 80% covered
          ├─ covered_lines: [1-12, 15-18]
          ├─ uncovered_lines: [13-14, 19]
          ├─ tests: [test_valid_case, test_edge_case_x, test_edge_case_y]
          └─ gaps: "exception handling on line 14"
```

**Unlocks**: Gap analysis, test priority suggestions, reliability assessment

---

## Reasoning Capabilities Unlocked

When all five pieces are in place, Piddy can:

### 1. Calculate Impact Radius (from call graphs)
**Query**: "What breaks if I change this function?"
```
Impact Analysis for function_authenticate():
├─ Direct impact: 5 functions (user_service.py)
├─ Indirect impact: 23 functions across 3 services
├─ Untested paths: 8 functions (16% of impact chain)
├─ Services affected: auth_service, api_gateway, mobile_app
├─ Recommendation: "Risky - HIGH impact. Suggest tests in user_service.py"
```

**Agent Confidence**: 95%+

### 2. Propose Safe Refactoring (from call graphs + type system)
**Query**: "Can I extract this into a helper function?"
```
Refactoring Safety Check:
├─ Extract: [lines 23-27] from authenticate()
├─ New function: validate_token(token: str, secret: str) → bool
├─ Type compatibility: ✅ All call sites match parameter types
├─ Service violations: ✅ None (stays within auth_service)
├─ Impact radius: ✅ 3 direct callers (all tested at >90%)
├─ Required changes: [Update 3 call sites]
├─ Rollback plan: Generated
├─ Recommendation: "SAFE to refactor. Risk: LOW"
```

**Agent Confidence**: 99%

### 3. Trace Data Flow (from call graphs + types + API contracts)
**Query**: "How does user data flow from API to database?"
```
Data Flow: POST /users → User Model → Database
├─ API endpoint: POST /users/{id}/settings
├─ Request schema: {settings: UserSettings}
├─ Data transformation: UserSettings → SettingsModel
├─ Database operation: INSERT INTO user_settings
├─ Type conversions: [SettingsModel.to_dict() → dict → JSON]
├─ Validation points: [schema_validate(), model_validate(), db_validate()]
├─ Security checks: [OAuth2 scope check, input sanitization]
├─ Potential issues: ["JSON serialization on line 145", "SQL injection risk (mitigated)"]
```

**Agent Confidence**: 92%

### 4. Architecture Analysis (from service boundaries + call graphs)
**Query**: "Is our architecture clean?"
```
Architecture Health Report:
├─ Services: 8 (auth, user, product, order, payment, notification, analytics, admin)
├─ Coupling Analysis:
│  ├─ auth_service ← user_service (required)
│  ├─ user_service ← order_service (required)
│  ├─ order_service ← product_service (required)
│  └─ payment_service ← order_service (required)
│
├─ Issues Detected:
│  ├─ Circular dependency: order_service ↔ product_service
│  ├─ High coupling: user_service called by 5 services
│  └─ Single point of failure: auth_service no redundancy
│
├─ Metrics:
│  ├─ Average coupling: 2.3 (target: <2.0)
│  ├─ Cyclomatic complexity: 4.2 (target: <4.0)
│  ├─ Cohesion score: 78% (target: >85%)
│
├─ Recommendations:
│  ├─ "Break circular dep: extract product_catalog_service"
│  ├─ "Replicate auth_service for redundancy"
│  └─ "Move user validation to user_service"
│
└─ Overall Grade: B+ (Good architecture, needs minor improvements)
```

**Agent Confidence**: 88%

### 5. Detect Breaking Changes (from API contracts + test coverage)
**Query**: "Will this change break anything?"
```
Breaking Change Analysis: Changing POST /users response
├─ Current schema response: {id, name, email, created_at}
├─ Proposed schema response: {id, name, email, created_at, role}  ← ADDED
├─ Impact: NON-BREAKING (only added field)
├─ Affected clients: 3 external services using this endpoint
├─ Test coverage: 92% (good)
├─ Deprecation path: "No need - backward compatible"
├─ Recommendation: "SAFE - non-breaking. Deploy immediately"
```

**Agent Confidence**: 99%

---

## Why This Is The Right Next Step

### Current Limitations
1. **Refactoring Paralysis**: Agent can generate changes but can't assess safety
2. **Manual Validation Bottleneck**: Every change needs human review
3. **Limited Cross-Service Reasoning**: Can't reliably refactor across services
4. **Architecture Blindness**: Can't assess or improve system design
5. **Test Gap Analysis**: Can't tell what's adequately tested

### What Phase 32 Solves
1. ✅ **Safe Refactoring**: Calculate impact before making changes
2. ✅ **Autonomous Confidence**: Agent makes ~95% of decisions independently
3. ✅ **Cross-Service Intelligence**: Knows service boundaries and contracts
4. ✅ **Architecture Awareness**: Can suggest and validate design improvements
5. ✅ **Test-Driven**: Identifies untested code paths and suggests tests

### Business Impact
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Changes req. human review | 100% | 5-10% | 10-20x faster |
| Safe refactoring success | 80% | 99%+ | 20% fewer bugs |
| Architecture debt → fixed | Manual | Autonomous | -$500K/yr |
| Mean time to detect breaking changes | 2-4 hrs | <1 sec | 7,200x faster |
| Developer confidence in agent | 60% | 95%+ | 160% increase |

---

## Implementation Roadmap

### Phase 32a: Call Graph Engine (Weeks 1-2)
**Effort**: 5-7 days | **Complexity**: Medium
```
┌─ AST Analysis → Extract function definitions and calls
├─ Call Graph DB → Store in Phase 28 persistent graph
├─ Query Layer → Get callers, callees, call chains
├─ Impact Radius → Calculate what's affected
└─ Integration → Hook into agent decision-making
```
**ROI**: HIGHEST - unlocks all safe refactoring

### Phase 32b: Type System Model (Weeks 2-3)
**Effort**: 5-7 days | **Complexity**: Medium
```
┌─ Type Extraction → Parse annotations
├─ Hierarchy Model → Track inheritance and interfaces
├─ Type Inference → Deduce types from usage
├─ Compatibility → Check type safety
└─ Generics → Handle type parameters
```
**ROI**: HIGH - enables safe type-level refactoring

### Phase 32c: Service Boundaries (Week 3)
**Effort**: 4-5 days | **Complexity**: Medium
```
┌─ Boundary Detection → Find microservice folders
├─ Contract Extraction → Get API endpoints
├─ Dependency Mapping → Track inter-service calls
├─ Cycle Detection → Find circular dependencies
└─ Validation → Enforce boundaries
```
**ROI**: HIGH - enables multi-service refactoring

### Phase 32d: API Contracts (Week 3-4)
**Effort**: 3-4 days | **Complexity**: Low-Medium
```
┌─ OpenAPI Parsing → Extract specs
├─ Endpoint Analysis → Get request/response schemas
├─ Status Code Docs → Document responses
├─ Example Storage → Keep request/response examples
└─ Deprecation → Track API versions
```
**ROI**: MEDIUM - enables safe API changes

### Phase 32e: Test Coverage Map (Week 4)
**Effort**: 3-4 days | **Complexity**: Low
```
┌─ Coverage Parsing → Read coverage reports
├─ Code Mapping → Map coverage to lines
├─ Gap Analysis → Find uncovered paths
├─ Test Tracking → Store per-test coverage
└─ Quality Metrics → Calculate coverage scores
```
**ROI**: MEDIUM - enables test-driven refactoring

### Phase 32f: Reasoning Engines (Week 4-5)
**Effort**: 5-7 days | **Complexity**: High
```
┌─ Impact Calculator → Assesses change impact
├─ Refactoring Planner → Generates safe refactorings
├─ Data Flow Tracer → Tracks data through system
├─ Architecture Analyzer → Reports on design quality
└─ Agent Integration → Feeds into decision-making
```
**ROI**: HIGHEST - all the above depends on this

---

## Decision Points

### Q1: Start with Call Graphs or Type System First?
**Recommendation**: **Call Graphs** (Phase 32a)
- **Why**: Most immediate value (enables safe deletion, impact analysis)
- **Benefit**: Can start making agent decisions independently within days
- **Type System**: Build after, uses call graph data

### Q2: SQLite or PostgreSQL?
**Recommendation**: **SQLite for Phase 32**, plan PostgreSQL for Phase 33
- **Why**: Single-machine deployment, no infrastructure needed
- **When to upgrade**: When analyzing 1M+ functions or multiple repos in parallel
- **Path**: Schema stays same, just swap database backend

### Q3: Python-only or Multi-language?
**Recommendation**: **Start Python**, add JavaScript/TypeScript in Phase 32b
- **Why**: 80% of codebase likely Python, other languages follow same patterns
- **Scalability**: Each language needs ~300 lines for call graph extractor

### Q4: Deterministic or ML-based Reasoning?
**Recommendation**: **Deterministic first** (Phase 32), ML-based in Phase 33
- **Why**: Deterministic reasoning more explainable and predictable
- **When to add ML**: When you want pattern-based suggestions or anomaly detection

### Q5: Backward Compatibility with Phase 28?
**Recommendation**: **100% compatible**
- **How**: Call graph tables added to existing Phase 28 database
- **Migration**: Fully automatic, no data loss
- **Rollback**: Safe - new tables are independent

---

## Prerequisites Checklist

Before starting Phase 32, verify:

- [ ] Phase 28 (Persistent Graph) is deployed and working
- [ ] Phase 28 unit tests pass 100%
- [ ] Database backups are automated
- [ ] Development environment has SQLite tools
- [ ] Team understands graph theory basics
- [ ] Python AST parsing examples reviewed
- [ ] Call graph visualization tool identified (optional: Graphviz)

---

## Success Metrics

### Phase 32 Complete When:

**Functional**
- ✅ Extracts 99%+ of function calls from Python code
- ✅ Detects all circular dependencies correctly
- ✅ Impact radius calculations match manual analysis
- ✅ Handles 100K+ functions with <500ms query time
- ✅ Type inference agrees with type checkers >95%

**Reliability**
- ✅ Zero graph corruption over 1M database updates
- ✅ Query results consistent across tool restarts
- ✅ Handles malformed code gracefully
- ✅ Automatic repair on database corruption

**Adoption**
- ✅ Agent uses call graph for 80%+ of refactoring decisions
- ✅ Agent confidence in safe refactoring > 95%
- ✅ Team validates agent refactorings with >95% acceptance rate
- ✅ Zero critical bugs from refactorings guided by system

---

## Long-Term Vision (Post-Phase 32)

### Phase 33: Distributed Reasoning
- Multi-repo analysis
- PostgreSQL distributed backend
- Real-time collaboration on architecture changes
- ML-based pattern discovery

### Phase 34: Automated Architecture Evolution
- Suggest refactorings that improve architecture metrics
- Autonomous service extraction when coupling threshold exceeded
- ML models for optimal service boundaries
- Automatic test generation based on coverage gaps

### Phase 35: Semantic Code Understanding
- Full semantic analysis (beyond syntax)
- Business logic extraction
- Domain model inference
- Automated documentation generation

---

## Questions to Answer Before Starting

1. **Team Readiness**: Is the team ready for agent autonomy increasing to 95%?
2. **Scope**: Start with current codebase only, or design for multi-repo from start?
3. **Performance**: Do we need sub-100ms queries or is <1s acceptable?
4. **Explainability**: How important is it to explain agent reasoning?
5. **Validation**: What's the validation process for agent-proposed changes?

---

## Next Action

**Recommendation**: Schedule 2-hour architecture review meeting

**Agenda**:
1. Review Phase 32 roadmap (30 min)
2. Make decisions on Q1-Q5 above (40 min)
3. Create Phase 32a sprint backlog (40 min)
4. Identify dependencies/blockers (10 min)

**Outcome**: Ready to start Phase 32a within 1 week

