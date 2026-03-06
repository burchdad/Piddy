# Phase 32: Technical Review → Action Plan

**Translating the technical review into concrete next steps**

---

## What The Review Validated ✅

Your Phase 32a is **correct architecture fundamentally**:

1. **Call graphs as foundation** - Right primitive
2. **SQLite for persistence** - Right choice for now
3. **AST extraction** - Deterministic, explainable
4. **Tools layer** - Clean agent interface
5. **Comprehensive tests** - Good foundation

This is rare. Most autonomous dev agents skip this entirely.

---

## What Needs Hardening ⚠️

Four production blockers identified:

| Issue | Impact | Solution |
|-------|--------|----------|
| **1. Static graphs miss edge cases** | Agent makes wrong decisions | Confidence scores (0.0-1.0) on edges |
| **2. Node IDs break on refactor** | Graph becomes stale | Qualified names + signatures |
| **3. Full rebuilds are slow** | Can't run in real-time | Incremental updates per file |
| **4. Impact reports too simple** | Agent lacks context | Add tests, services, risk scores |

---

## Immediate Action Path

### Phase 1: Hardening (1 week)

Do these three things in parallel:

**Sprint 1a: Node Identity** (2 days)
```
Goal: Node IDs survive refactors
Action: Add qualified_name + signature_hash to schema
Result: repo:src.engine.CallGraphDB.get_callers:abc12345 stable forever
File: PHASE32_SCHEMA_HARDENING.md (Migration 1)
```

**Sprint 1b: Confidence Scoring** (2 days)
```
Goal: Each edge has confidence 0.0-1.0
Action: Add evidence_type, confidence, source to call_graphs
Result: Can filter edges by confidence threshold
File: PHASE32_SCHEMA_HARDENING.md (Migration 2)
```

**Sprint 1c: Incremental Rebuilds** (3 days)
```
Goal: <500ms updates on file changes
Action: Build IncrementalGraphBuilder class
Result: Real-time graph updates in CI/CD
File: PHASE32_HARDENING_ROADMAP.md (Section 3)
```

**Outcome after Sprint 1:**
- ✅ Node IDs stable across refactors
- ✅ Edge confidence scores working
- ✅ Graph updates <500ms
- ✅ Ready for test coverage mapping

### Phase 2: Test Coverage (1 week) - NEW PRIORITY

Move **Phase 32b: Test Coverage** here immediately after hardening.

**Why:**
- Enables risk scoring without waiting for types
- Simpler than type system (execution-based, not inference)
- Foundation for types anyway
- Agent autonomy: 60% → 75%

**What it does:**
```python
For each function:
  - Which tests cover it?
  - Coverage percent?
  - Risk score = (1 - coverage) × log(impact_radius)

Result: Agent can autonomously refactor if risk < 0.3
```

**Files to reference:**
- PHASE32_REVISED_ORDER.md (why this order)
- PHASE32_HARDENING_ROADMAP.md (Section 4: Rich Reports)

### Phase 3: Documentation (1 day)

Update docs to reflect:
- New execution order (32a → hardening → 32b → 32c...)
- Node identity approach
- Confidence scoring semantics

---

## Technical Decisions Made

### 1. Node Identity Pattern

```python
# OLD (breaks on refactor)
node_id = hash(file_path + line_number)

# NEW (stable forever)
stable_id = "repo:qualified_name:signature_hash"
# Example: "piddy:src.engine.CallGraphDB.get_callers:abc12345"
```

**Benefits:**
- Survives file moves
- Survives reformatting
- Survives small refactors
- Graph stays valid forever

### 2. Confidence Model

```python
# Each edge now has:
evidence_type    # 'static' | 'runtime' | 'inferred'
confidence       # 0.0-1.0 (0.95 for static AST)
source          # 'ast:call_node' | 'runtime:trace' | etc
observed_count  # How many times verified

# Query pattern:
impact = get_impact_radius(func, min_confidence=0.85)
# Only traverse edges above confidence threshold
```

**Benefits:**
- Agent never makes decisions on 40% confidence edges
- Can upgrade edges to 99% via runtime tracing
- Foundation for probabilistic reasoning later

### 3. Phase Order: 32b Before 32c

```
OLD: 32a → 32b(type) → 32c(services) → ...
NEW: 32a → hardening → 32b(test_coverage) → 32c(type) → ...
```

**Why:**
- Test coverage enables risk scoring immediately
- Types are more complex, can wait 1 week
- Path tracking (needed for types) built during 32b anyway
- Agent gets to 75% autonomy faster

---

## Implementation Checklist

### Before Starting Code

- [ ] Read PHASE32_SCHEMA_HARDENING.md (understand migrations)
- [ ] Read PHASE32_HARDENING_ROADMAP.md (understand each item)
- [ ] Read PHASE32_REVISED_ORDER.md (understand priority shift)
- [ ] Decide: Solo effort or team of 2-3?

### Starting Hardening

**Week 1: Migrations**

- [ ] Backup existing database(s)
- [ ] Execute Migration 1: Node identity
  - [ ] Add columns to nodes table
  - [ ] Add columns to call_graphs table
  - [ ] Run compute_qualified_names()
  - [ ] Verify all nodes have stable_id
  - [ ] Add indexes
  
- [ ] Execute Migration 2: Confidence
  - [ ] Mark existing edges as 'static' with 0.95 confidence
  - [ ] Verify query: get_impact_radius_confident()
  - [ ] Test: Queries with min_confidence filter work
  
- [ ] Build IncrementalGraphBuilder
  - [ ] File change detection
  - [ ] Delta computation
  - [ ] Edge updates
  - [ ] Verify: <500ms rebuilds on large files

**Week 2: Test Coverage (32b)**

- [ ] Extract test coverage
  - [ ] pytest integration with coverage.py
  - [ ] Mapping of tests → functions
  
- [ ] Build test_coverage table
  - [ ] Store coverage data
  - [ ] Query: which tests cover function
  
- [ ] Risk scoring
  - [ ] Implement formula: (1 - coverage) × log(impact)
  - [ ] Integration with agent
  
- [ ] Validate
  - [ ] Dead code detection working
  - [ ] Risk scores match manual review

---

## What Success Looks Like

### After Hardening (Week 1)
```
✅ Nodes have stable IDs (survived file move test)
✅ Edges have confidence scores (0.85-0.99)
✅ File change rebuilds <500ms
✅ All tests passing
```

### After Test Coverage (Week 2)
```
✅ Test coverage mapping complete
✅ Risk scores calculated
✅ Dead code flagged automatically
✅ Agent autonomy: 60% → 75%
✅ Ready for type system (32c)
```

---

## Tools/Resources Needed

- **Python**: ast module, sqlite3 (std lib)
- **Testing**: pytest, coverage.py
- **Optional**: sqlalchemy for schema migrations
- **Time**: 2 weeks, 1-2 experienced backend engineers

---

## When to Stop Iterating

When these are true, you're done:

1. ✅ Phase 32a tests still passing (all 6/6)
2. ✅ Node IDs prove stable (move file, graph doesn't break)
3. ✅ Confidence filtering works (query excludes low-confidence edges)
4. ✅ Incremental rebuild <500ms
5. ✅ Test coverage table populated
6. ✅ Risk scores guide agent decisions
7. ✅ Dead code detected automatically
8. ✅ New tests pass 100%

That's production-ready for Phase 32a+b.

---

## Risk If You Skip This

**Shipping without hardening:**

- Node IDs break after first refactor → graph becomes unreliable
- No confidence scores → agent trusts wrong edges → breaks callers
- Full rebuilds every time → can't use in CI/CD loops
- Poor impact reports → agent lacks context for decisions

**Result**: Works in demo (small isolated code), fails in production (large codebase, frequent changes).

---

## Risk If You Try Everything At Once

**Attempting all phases simultaneously:**

- Confusion about what breaks where
- Hard to test each component
- Shipping with untested interactions
- Slower overall

**Better**: Do in phases, verify each before next.

---

## Recommended Next Steps (In Order)

### This Week
1. ✅ Read the three hardening documents (this page + 2 others)
2. ✅ Review database schema changes
3. ✅ Decide on team size (solo vs. 2-3 people)
4. ⏭️ **Start Migration 1: Node identity** (2 days)

### Next Week  
5. ⏭️ **Complete Migration 1, 2** (2 days each)
6. ⏭️ **Build IncrementalGraphBuilder** (3 days)
7. ⏭️ **Verify hardening** (1 day)
8. ⏭️ **Start Phase 32b: Test Coverage** (5 days)

### Week After
9. ⏭️ **Complete 32b, test coverage working**
10. ⏭️ **Validate agent with new risk scores**
11. ⏭️ **Plan 32c (Type System)**

---

## Key Files Reference

| Document | Purpose | Status |
|----------|---------|--------|
| PHASE32_REASONING_ENGINE.md | Overall vision | Reference |
| PHASE32_CALL_GRAPH_GUIDE.md | 32a details | Reference |
| PHASE32_HARDENING_ROADMAP.md | **Production hardening** | **Read this** |
| PHASE32_SCHEMA_HARDENING.md | **Database migrations** | **Read this** |
| PHASE32_REVISED_ORDER.md | **Phase priority shift** | **Read this** |
| PHASE32_IMPLEMENTATION_COMPLETE.md | Status of Phase 32a | Reference |

---

## Summary

**What you have:** A correct foundation (Phase 32a)

**What you need:** 2 weeks of hardening to make it production-ready

**What you'll gain:** Agent autonomy 60% → 75% right after 32b

**Recommended:** Do hardening + 32b (test coverage) immediately, then decide on 32c (types) timing

**Timeline:** 2 weeks, can be done in parallel where noted

**Risk if you skip:** Works in demos, fails in production

---

## Final Recommendation

The technical review nailed it. Your Phase 32a architecture is sound. The additions aren't "nice to haves" — they're the difference between a prototype and production infrastructure.

**My recommendation:**
1. ✅ Keep everything you've built in Phase 32a
2. ✅ Do the hardening migrations (2 weeks)
3. ✅ Move test coverage (32b) to phase 2
4. ✅ Ship after 32b is complete (agent gets 75% autonomy)
5. ⏹️ Types (32c) can follow at normal pace

This gets you to "production-grade code reasoning" in 3 weeks instead of 5-6 weeks.

