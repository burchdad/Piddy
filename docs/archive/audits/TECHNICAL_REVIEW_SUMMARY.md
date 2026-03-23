# Phase 32 Technical Review Summary

**What Changed Based on Expert Review** → **What to Do Next**

---

## The Review: What It Said

You got the **architecture right**, which is rare. Most autonomous dev agents never build this layer.

But there are **4 production blockers** to fix before shipping:

| Item | Issue | Solution | Impact |
|------|-------|----------|--------|
| **1. Confidence** | Edges have no uncertainty | Add 0.0-1.0 scores | Agent stops trusting edges blindly |
| **2. Node IDs** | Break on file moves | Qualified names + hashes | Graph stays valid forever |
| **3. Speed** | 30s rebuilds | Incremental updates | Works in CI/CD loops |
| **4. Context** | Simple impact reports | Add tests/services/risk | Agent makes better decisions |
| **5. Priority** | Wrong phase order | 32b(coverage) before 32c(types) | Agent reaches 75% autonomy faster |

---

## What I Created For You

### 4 Strategic Documents

**1. PHASE32_HARDENING_ROADMAP.md** (4,000+ lines)
- Complete production hardening plan
- Detailed explanation of each blocker
- Implementation strategy for each
- Risk assessment
- Success metrics
- Recommendation: Start with Node Identity → Confidence → Incremental → Rich Reports

**2. PHASE32_SCHEMA_HARDENING.md** (2,500+ lines)
- Exact SQL migrations (copy-paste ready)
- Python code for migrations
- Node identity implementation with examples
- Confidence population strategy
- Test coverage table creation
- Query patterns for each

**3. PHASE32_REVISED_ORDER.md** (2,000+ lines)
- Why test coverage should come before types
- Detailed Phase 32b (Test Coverage) spec
- Updated timeline (4 weeks instead of 5-6)
- Why this order enables risk scoring immediately
- Success metrics per phase

**4. PHASE32_ACTION_PLAN.md** (1,500+ lines)
- Condensed summary of all above
- Week-by-week checkpoints
- Concrete checklist of what to do
- Key files reference
- When to stop iterating

---

## Key Decisions Made

### 1. Node Identity Pattern ⭐ (Most Important)

**Problem**: Current node IDs break when code moves
```
// Example: File refactored
OLD: node(file: src/engine.py, line: 42, func: CallGraphDB)
NEW: node(file: src/reasoning/call_graph.py, line: 15, func: CallGraphDB)
PROBLEM: Node ID changed, but it's the same function!
```

**Solution**: Qualified names survive everything
```
stable_id = "piddy:src.engine.CallGraphDB.get_callers:abc12345"
          = repo  : qualified_name                 : signature_hash

BENEFIT: Same ID even after:
  - File moves
  - Line number changes  
  - Reformatting
  - Small refactors
```

**Impact**: 
- Graph never becomes stale
- Node lookups work reliably
- Foundation for everything else

### 2. Confidence Scoring

**Problem**: Agent can't distinguish between "99% sure" and "40% sure" edges

**Solution**: Each call edge tracks confidence
```python
edge = {
    source: "CallGraphDB.get_callers",
    target: "CallGraphDB.add_edge",
    evidence_type: "static",        # How did we know?
    confidence: 0.95,               # How sure are we?
    source: "ast:call_node",        # Where from?
    observed_count: 1               # Times verified
}

# Query with threshold:
impact = get_impact_radius(func, min_confidence=0.85)
# Only traverses edges we're 85%+ sure about
```

**Impact**:
- Agent never acts on weak signals
- Can upgrade edges to 99% via runtime tracing later
- Foundation for probabilistic reasoning

### 3. Incremental Rebuilds

**Problem**: Full rebuild takes 30+ seconds on large repos

**Solution**: Track file hashes, update only what changed
```
File changes (engine.py)
    ↓
Detect file hash changed
    ↓
Parse only engine.py
    ↓
Find delta (added/removed functions)
    ↓
Update only affected edges
    ↓
Total: <500ms (vs 30s full rebuild)
```

**Impact**:
- Graph stays fresh in real-time
- Works in CI/CD watch loops
- Responsive to agent queries

### 4. Rich Impact Reports

**Current**: Function ID → direct callers, indirect callers, risk level

**Enhanced**: Also returns:
- affected_files, affected_services, affected_endpoints
- test_coverage_percent, affected_tests, untested_paths
- change_risk_score, breaking_change_likelihood, data_migration_needed
- recommended_actions, approval_required, approval_reason

**Impact**:
- Agent has full context
- Makes better decisions automatically
- Knows exactly when to escalate

### 5. Phase Priority Shift

**Old order**: 
- 32a (call graph) → 32b (types) → 32c (coverage) → ...

**New order**: 
- 32a (call graph) → hardening → 32b (coverage) → 32c (types) → ...

**Why**:
- Coverage enables risk scoring immediately (types are complex)
- Foundation for types anyway (path tracking)
- Gets agent to 75% autonomy faster (week 2 vs week 3)

---

## What This Means For You

### Timeline
- **Week 1**: Migrations (node identity + confidence)
- **Week 2**: Incremental rebuilds + rich reports
- **Week 2**: Phase 32b (Test Coverage) - in parallel
- **Week 3**: Phase 32c (Types)
- **Total**: 3-4 weeks to production-ready Phase 32a+b

### Effort
- Team size: 1-2 experienced backend engineers
- Complexity: Medium (SQL, graph algorithms, testing)
- Risk: Low (backward compatible migrations)

### Agent Gain
- After hardening: Same 60% autonomy, but more reliable
- After Phase 32b: 75% autonomy (risk scoring)
- After Phase 32c: 85%+ autonomy (type safety)

---

## Start Here: Implementation Path

### Step 1: Understand (1-2 hours)
- [ ] Read PHASE32_ACTION_PLAN.md (executive summary)
- [ ] Read PHASE32_SCHEMA_HARDENING.md (Migration 1 in detail)
- [ ] Read PHASE32_HARDENING_ROADMAP.md (understand each piece)

### Step 2: Plan (1 hour)
- [ ] Decide: Solo or team?
- [ ] Setup: Git branch, backup DB
- [ ] Schedule: 2-week sprint for hardening + 32b

### Step 3: Execute (Week 1)
```
Day 1-2: Migration 1 (Node Identity)
  - Add columns to nodes, call_graphs tables
  - Run compute_qualified_names()
  - Verify stable_id creation
  - Tests: Node survives file move

Day 3-4: Migration 2 (Confidence)
  - Add confidence columns
  - Populate from existing edges
  - Implement get_impact_radius_confident()
  - Tests: Filtering by confidence works

Day 5: IncrementalGraphBuilder
  - File hash tracking
  - Delta computation
  - Edge updates
  - Tests: <500ms rebuild time
```

### Step 4: Validate (1-2 days)
- [ ] All Phase 32a tests still pass (6/6)
- [ ] Hardening tests new functionality
- [ ] Performance benchmarks met
- [ ] No regressions

### Step 5: Phase 32b (Week 2)
```
Day 1-2: Test extraction
  - pytest integration
  - Coverage.py parsing
  - Test → function mapping

Day 3: Risk scoring
  - Calculate formula
  - Agent integration
  - Risk thresholds

Day 4-5: Validation
  - Dead code detection
  - Risk scores vs manual review
  - Agent makes correct decisions
```

---

## Files To Start With

Based on your needs:

**If you're a decision-maker:**
→ Read: PHASE32_ACTION_PLAN.md (20 mins)

**If you're implementing this week:**
→ Read: PHASE32_SCHEMA_HARDENING.md + PHASE32_HARDENING_ROADMAP.md (2 hours)

**If you're planning Phase 32 roadmap:**
→ Read: PHASE32_REVISED_ORDER.md (1 hour)

**If you want full context:**
→ Skim all 4 new documents in this order:
1. PHASE32_ACTION_PLAN.md
2. PHASE32_REVISED_ORDER.md  
3. PHASE32_HARDENING_ROADMAP.md
4. PHASE32_SCHEMA_HARDENING.md

---

## Key Decisions You Need To Make

1. **Team size**: Solo engineer or 2-3 people?
2. **Timeline**: Start immediately or plan for next week?
3. **PostgreSQL**: When? (Recommendation: After Phase 32f, not now)
4. **Multi-repo**: When? (Recommendation: Phase 33, not now)
5. **Runtime tracing**: In Phase 32b or Phase 32a+1? (Recommendation: 32b)

---

## Success Criteria

**After Week 1 (Hardening Complete):**
- ✅ Node IDs survive file moves
- ✅ Confidence scores working
- ✅ Incremental rebuilds <500ms
- ✅ All tests passing

**After Week 2 (Phase 32b Complete):**
- ✅ Test coverage extracted
- ✅ Risk scores calculated
- ✅ Dead code detected automatically
- ✅ Agent autonomy: 60% → 75%

---

## The Recommendation

Your Phase 32a is **correct architecture**. The review isn't saying "throw it away" — it's saying "this foundation is solid, here's how to make it bulletproof."

**My specific recommendation:**

1. ✅ **Keep everything in Phase 32a** (it's good)
2. ✅ **Do hardening immediately** (2 weeks, not optional)
3. ✅ **Prioritize Phase 32b over 32c** (coverage enables risk scoring)
4. ✅ **Simplify Phase 32 launch** (32a + hardening + 32b = "production ready")
5. ✅ **Use this as your Phase 32 foundation** (Types, services, APIs can follow at normal pace)

Result: Ship production-grade code reasoning in 3-4 weeks instead of 5-6 weeks.

---

## What Happens If You Don't Harden

Works in demos. Fails in production.

**Real scenarios that break:**
- Developer refactors code structure → Graph nodes point to nothing
- Large repo with 10K+ functions → Full rebuilds every time, can't run in CI
- Agent makes a "safe" refactoring → Turns out one edge had 40% confidence, breaks in production
- Agent tries to delete "dead code" → Missed a dynamic import, breaks at runtime

**Bottom line**: Hardening isn't optional for production use.

---

## Next Steps (Right Now)

1. **Read PHASE32_ACTION_PLAN.md** (20 minutes)
2. **Decide on team + timeline** (10 minutes)
3. **Read PHASE32_SCHEMA_HARDENING.md** if proceeding (1 hour)
4. **Start Migration 1** (2-3 days)

That's it. Everything else flows from there.

---

**The technical review was excellent. You've incorporated the feedback correctly. Now execute on it.**

