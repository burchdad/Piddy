# Quick Start Guide: End-to-End Demo

Run the complete Phases 39→40→41→42→50 workflow in under 30 seconds.

## 📋 Prerequisites

```bash
# Python 3.11+
python3 --version

# Piddy installed
cd /workspaces/Piddy
```

## 🚀 Running the Demo

### Option 1: Full Demo (Recommended)

```bash
# Run complete workflow
python3 demo_end_to_end_phases_39_to_50.py

# Output: Detailed phase-by-phase breakdown
# Results saved to: /tmp/piddy_demo_results.json
```

### Option 2: Individual Phase Testing

```python
# Test Phase 39: Impact Analysis
from demo_end_to_end_phases_39_to_50 import Phase39ImpactAnalyzer, MICROSERVICES

impact = Phase39ImpactAnalyzer.analyze_change("auth", MICROSERVICES)
print(f"Impact Level: {impact['impact_level']}")
print(f"Affected Services: {len(impact['transitive_dependents'])}")

# Test Phase 40: Simulation
from demo_end_to_end_phases_39_to_50 import Phase40MissionSimulator

simulator = Phase40MissionSimulator(impact)
result = simulator.simulate_update()
print(f"Success Probability: {result['success_probability']}")

# Test Phase 41: Coordination
from demo_end_to_end_phases_39_to_50 import Phase41MultiRepoCoordinator

coordinator = Phase41MultiRepoCoordinator()
plan = coordinator.plan_coordinated_execution(
    impact['transitive_dependents'], 
    MICROSERVICES
)
print(f"PR Chain: {plan['total_prs']} PRs in {plan['estimated_deployment_time_hours']} hours")

# Test Phase 42: Refactoring
from demo_end_to_end_phases_39_to_50 import Phase42RefactoringScheduler

scheduler = Phase42RefactoringScheduler()
schedule = scheduler.create_nightly_schedule()
print(f"Nightly PRs: {schedule['total_estimated_prs_per_night']}")

# Test Phase 50: Consensus
from demo_end_to_end_phases_39_to_50 import Phase50MultiAgentConsensus

consensus = Phase50MultiAgentConsensus.evaluate_auth_upgrade()
print(f"Agent Consensus: {consensus['consensus_type']}")
print(f"Average Confidence: {consensus['average_confidence']}")
```

## 📊 Output Interpretation

### Phase 39: Impact Analysis
```
Impact Level: CRITICAL (92.59%)
├─ What it means: Changes affect >90% of system
├─ Action: Plan for coordinated rollout
└─ Confidence: 95% (very high)
```

### Phase 40: Simulation
```
Success Probability: 90.0%
├─ What it means: Predicted success if deployed
├─ Action: Safe to proceed (>90% threshold)
└─ Risk Level: MEDIUM (acceptable for critical service)
```

### Phase 41: Coordination
```
PR Chain: 25 PRs in 2 hours
├─ What it means: Coordinated deployment plan
├─ Optimization: 3 parallel waves (65 min actual)
└─ Parallel Speedup: 27% faster than sequential
```

### Phase 42: Refactoring
```
Nightly PRs: 36 PRs/night
├─ What it means: Automated improvements
├─ Tech Debt Reduction: 5% per night
└─ No Human Cost: Fully automated
```

### Phase 50: Consensus
```
Consensus: UNANIMOUS (8/8 agents)
├─ What it means: All agents agree on strategy
├─ Average Confidence: 94.6% (very high)
└─ Recommendation: PROCEED WITH EXECUTION
```

## 🔄 Integration Examples

### Example 1: Use in CI/CD Pipeline

```yaml
# .github/workflows/deploy-auth-service.yml
name: Deploy Auth Service

on:
  push:
    branches: [main]
    paths: ['services/auth/**']

jobs:
  analyze-impact:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run Impact Analysis
        run: python3 demo_end_to_end_phases_39_to_50.py
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: piddy-analysis
          path: /tmp/piddy_demo_results.json
```

### Example 2: Use in Pre-Deployment Script

```bash
#!/bin/bash
# scripts/pre-deploy.sh

echo "🔍 Running Piddy Phase 39-50 Analysis..."

# Run demo
python3 demo_end_to_end_phases_39_to_50.py

# Extract results
RESULTS=$(cat /tmp/piddy_demo_results.json)

# Check if safe to proceed
SUCCESS_PROB=$(echo $RESULTS | jq '.phases["40_simulation"].success_probability')

if (( $(echo "$SUCCESS_PROB > 0.90" | bc -l) )); then
    echo "✅ Success probability $SUCCESS_PROB > 90%"
    echo "✅ Safe to proceed with deployment"
    exit 0
else
    echo "❌ Success probability $SUCCESS_PROB < 90%"
    echo "❌ Cannot proceed - requires approval"
    exit 1
fi
```

### Example 3: Use in Decision Dashboard

```python
# dashboard/phase50_consensus_display.py

from demo_end_to_end_phases_39_to_50 import Phase50MultiAgentConsensus

def render_consensus_panel():
    """Display multi-agent consensus on dashboard"""
    
    consensus = Phase50MultiAgentConsensus.evaluate_auth_upgrade()
    
    # Color code based on consensus
    if consensus['consensus_type'] == 'UNANIMOUS':
        color = 'green'
        icon = '✅'
    elif consensus['consensus_type'] == 'SUPERMAJORITY':
        color = 'yellow'
        icon = '⚠️'
    else:
        color = 'red'
        icon = '❌'
    
    # Display votes
    for agent_name, agent_data in consensus['agent_votes'].items():
        vote_color = 'green' if agent_data['vote'] == 'APPROVE' else 'red'
        print(f"[{vote_color}] {agent_data['role']}: {agent_data['vote']} ({agent_data['confidence']*100}%)")
    
    # Display recommendation
    print(f"\n[{color}] {icon} {consensus['recommendation']}")
    
    return consensus
```

## 📈 Metrics You Can Track

After running the demo multiple times:

```python
# Track how metrics change with different scenarios

scenarios = [
    {"name": "Small change", "service": "email"},
    {"name": "Medium change", "service": "payment"},
    {"name": "Critical change", "service": "auth"},
]

for scenario in scenarios:
    impact = Phase39ImpactAnalyzer.analyze_change(scenario['service'], MICROSERVICES)
    print(f"{scenario['name']}: {impact['total_affected']} services affected")
```

## 🎓 Learning Outcomes

After running this demo, you'll understand:

1. **How Phase 39 works**: Impact analysis across real services
2. **How Phase 40 works**: Mission simulation for safety
3. **How Phase 41 works**: Coordinating changes across repos
4. **How Phase 42 works**: Autonomous refactoring scheduling
5. **How Phase 50 works**: Multi-agent consensus decision making
6. **How they integrate**: Complete autonomous workflow

## 🚀 Next Steps

1. **Run the demo** - See it in action
2. **Modify the scenario** - Change different services
3. **Check the results** - Understand the output
4. **Integrate into CI/CD** - Use in your pipeline
5. **Deploy to production** - Launch with confidence

---

**Time to run full demo: ~5 seconds**  
**Time to understand output: ~10 minutes**  
**Value delivered: Production-grade autonomous deployment system**

---

## 📞 Support

For issues or questions:
1. Check [DEMO_RESULTS_PHASES_39_50.md](DEMO_RESULTS_PHASES_39_50.md) for detailed results
2. Review [PHASE39_PLUS_ROADMAP.md](PHASE39_PLUS_ROADMAP.md) for phase details
3. See [PHASES_19_20_50_51_SPECIFICATIONS.md](PHASES_19_20_50_51_SPECIFICATIONS.md) for Phase 50 details
