# Phase 38: LLM-Assisted Planning - Quick Start Guide

## Installation

```bash
# Make sure Anthropic package is installed
pip install anthropic
```

## Quick Usage

### Basic: Enable LLM Planning (Recommended)

```python
from src.phase34_38_integration import EnhancedAutonomousSystem

# Create system (LLM planning enabled by default)
system = EnhancedAutonomousSystem()

# Execute mission - LLM will enhance the plan automatically
result = await system.execute_intelligent_mission(
    mission_type="cleanup",
    from_ref="main",
    create_pr=True
)

# Access LLM insights
print(result['llm_analysis']['semantic_summary'])
print(result['llm_analysis']['strategy'])
print(f"Confidence: {result['llm_analysis']['confidence']:.1%}")
```

### Option: Disable LLM Planning

```python
# Fall back to Phase 36 diff-aware planning only
result = await system.execute_intelligent_mission(
    mission_type="cleanup",
    use_llm_planning=False
)
```

## Direct LLM Planner Usage

```python
from src.phase38_llm_assisted_planning import LLMPlanningAssistant

# Create planner
assistant = LLMPlanningAssistant()

# 1. Analyze diff semantically
analysis = assistant.analyze_diff_semantically(
    diff_text="<git diff output>",
    file_paths=["src/module.py", "src/utils.py"],
    module_names=["src", "tests"]
)

print(f"Semantic Summary: {analysis.semantic_summary}")
print(f"Strategy: {analysis.suggested_strategy}")
print(f"Risks: {analysis.risk_factors}")
print(f"Confidence: {analysis.confidence_score:.1%}")

# 2. Get optimized tasks
tasks = assistant.generate_optimized_tasks(
    mission_type="cleanup",
    base_plan={"tasks": ["analyze", "execute", "validate"]},
    llm_analysis=analysis
)

# 3. Get test selection
tests = assistant.suggest_test_selection(
    mission_type="cleanup",
    affected_modules=["src"],
    llm_analysis=analysis
)

print(f"Must Run: {tests['must_run']}")
print(f"Can Skip: {tests['can_skip']}")

# 4. Get enhanced plan
if analysis.confidence_score > 0.7:
    enhanced = assistant.enhance_plan(
        base_plan={"tasks": [...]},
        diff_analysis={"diff_text": "...", "files_changed": [...]},
        mission_type="cleanup"
    )
    print(assistant.generate_execution_summary(enhanced))
```

## Key Concepts

### Strategies

```python
from src.phase38_llm_assisted_planning import PlanStrategy

# CONSERVATIVE: Safe, thorough, slower
# - Extra validation runs first
# - All tests run
# - Highest safety margin

# BALANCED: Standard, proven
# - Mix of analysis and execution
# - Optimized test selection
# - Good balance

# AGGRESSIVE: Fast, calculated risk
# - Skip non-critical validation
# - Minimize test runs
# - Focus on speed

# EXPLORATORY: Learn-focused
# - Try new approaches
# - Gather data
# - Innovation-oriented
```

### Confidence Score

```
0.0-0.3: Very Low  → Use CONSERVATIVE
0.3-0.6: Low       → Use BALANCED or CONSERVATIVE
0.6-0.8: Good      → Use BALANCED
0.8-0.9: High      → Can use AGGRESSIVE
0.9-1.0: Very High → Can be very AGGRESSIVE
```

## Common Patterns

### Pattern 1: Risky Changes - Conservative Approach

```python
assistant = LLMPlanningAssistant()

# Analyze changes
analysis = assistant.analyze_diff_semantically(
    diff_text=get_major_refactor_diff(),
    file_paths=get_all_changed_files(),
    module_names=["database", "api", "models"]
)

# High-risk changes get conservative strategy
# → All validation runs first
# → All tests run
# → Extra safety checks included

# Confidence is automatically considered
print(f"Strategy: {analysis.suggested_strategy}")
print(f"Tasks ordered for safety first")
```

### Pattern 2: Small Changes - Aggressive Approach

```python
# Small, focused changes
analysis = assistant.analyze_diff_semantically(
    diff_text=get_docs_fix_diff(),
    file_paths=["README.md", "docs/api.md"],
    module_names=["docs"]
)

# Low-risk changes get aggressive strategy
# → Skip unnecessary validation
# → Run only relevant tests
# → Fast execution

# Example result:
# Strategy: AGGRESSIVE
# Confidence: 95%
# Duration: 30 seconds
```

### Pattern 3: Learning from Results

```python
from src.phase38_llm_assisted_planning import LLMPlanOptimizer

# Create optimizer
optimizer = LLMPlanOptimizer(assistant)

# Learn from completed mission
insights = optimizer.learn_from_execution(
    plan=enhanced_plan,
    execution_result={
        'status': 'success',
        'tasks_completed': 8,
        'duration_actual': 120
    }
)

# Use insights for next mission
print("What worked:")
for item in insights['what_worked']:
    print(f"  ✓ {item}")

print("\nImprovements:")  
for item in insights['improvements_for_next_time']:
    print(f"  → {item}")
```

## Viewing Results

```python
# After mission execution

# LLM Analysis
result['llm_analysis'] = {
    'semantic_summary': '...',      # What it means
    'strategy': 'balanced',          # Execution strategy
    'risk_factors': [...],           # Identified risks
    'mitigation_strategies': [...],  # How to address them
    'confidence': 0.89               # (0-1) confidence level
}

# Enhanced Plan
result['enhanced_plan'] = {
    'final_tasks': [...],            # Optimized task list
    'execution_order': [...],        # Recommended order
    'estimated_duration': '3m 45s'   # Time estimate
}

# Use this data to:
# 1. Understand what will happen
# 2. Adjust strategy if needed
# 3. Set expectations
# 4. Learn for next mission
```

## Troubleshooting

### "LLM plan enhancement failed"

**Cause:** Anthropic API error or invalid diff  
**Solution:** Check ANTHROPIC_API_KEY environment variable

```bash
export ANTHROPIC_API_KEY="sk-..."
```

**Fallback:** System uses base plan from Phase 36 automatically

### "Confidence score too low"

**Cause:** Complex changes with high uncertainty  
**Solution:** Use CONSERVATIVE strategy or wait for more analysis

```python
if analysis.confidence_score < 0.6:
    # Use conservative approach
    print("Using extra validation due to low confidence")
```

### Large diffs cause timeout

**Cause:** API rate limiting or very large diff  
**Solution:** Limit diff size to first 5000 characters (auto-trimmed)

## Environment

### Required
- Python 3.8+
- `anthropic` package
- Anthropic API key

### Optional
- Different Claude model (configure in LLMPlanningAssistant)
- Custom system prompts (modify prompts in methods)

## Examples Location

```
/workspaces/Piddy/
├─ src/phase38_llm_assisted_planning.py     (Implementation)
├─ PHASE38_LLM_PLANNING.md                  (Full documentation)
├─ PHASES_34_38_COMPLETE.md                 (Integration overview)
└─ This file                                 (Quick start)
```

## Next Steps

1. **Enable LLM Planning**: Set `use_llm_planning=True` in your missions
2. **Monitor Confidence**: Track confidence vs actual results
3. **Calibrate Strategies**: Adjust strategy selection based on data
4. **Expand Usage**: Try on different mission types
5. **Measure Impact**: Compare execution time and safety metrics

---

**Ready?** Start using LLM-assisted planning in your next autonomous mission! 🚀
