# Phase 5 Quick Start - Market-Driven Autonomous System

## 🚀 Start Everything in One Command

```bash
# Start the background service (runs 24/7)
python3 src/autonomous_background_service.py
```

That's it. The system will now:
- Collect metrics every 60 seconds
- Feed to growth engine (learns)
- Trigger automation rules (cascades improvements)
- Deploy waves when ready
- **Run market analysis periodically**
- **Autonomously build new agents**
- **Deploy them automatically**

## 📊 What You'll See When It Runs

### Initial Startup (Seconds 1-5)
```
❤️  AUTONOMOUS BACKGROUND SERVICE STARTED
   Polling interval: 60s (configurable)
   Auto-trigger: True
   Auto-execute: True
   Status: RUNNING (will feed metrics continuously)
   🌍 Market-Driven Building: ENABLED
```

### Continuous Metrics Cycles (Every 60 seconds)
```
📊 Cycle 1: Collected 3 metrics
📊 Cycle 2: Collected 3 metrics
📊 Cycle 3: Collected 3 metrics
...
```

### Status Reports (Every 10 cycles)
```
📈 Status Report:
   Cycles completed: 30
   Growth engine patterns: 5
   Automation rules triggered: 2
   Waves deployed: 1
   Market analysis cycles: 0 (waiting...)
```

### Market Analysis Phase (~after 100 cycles)
```
================================================================================
🌍 MARKET-DRIVEN BUILD PHASE
================================================================================

🔍 MARKET ANALYZER: Scanning real-world ecosystem...
✅ Found 20 market patterns across 5 categories

🕵️  GAP DETECTOR: Finding market opportunities...
✅ Detected 19 market gaps

🤖 PROPOSAL ENGINE: Generating build recommendations...
✅ Generated 5 autonomous build proposals

👷 Queueing build: MutationTestingAgent
👷 Queueing build: FlakyTestDetectionAgent
👷 Queueing build: CodeDuplicationAgent

👷 Processing 3 queued builds...

🏗️  BUILDING: MutationTesting
  1/5 📝 Generating code...
      ✅ Generated 1239 bytes of code
  2/5 📁 Creating files...
      ✅ Files created at src/agent/testing/mutationtesting_agent.py
  3/5 🧪 Generating tests...
      ✅ Tests created at tests/agent/mutationtesting/test_agent.py
  4/5 🔗 Creating integration...
      ✅ Integration created at src/integration/mutationtesting_integration.py
  5/5 ✔️  Validating build...
      ✅ Build validated successfully

✅ Build complete: MutationTesting
   Status: built
   Ready to deploy: True

[Same for other agents...]
```

### What Happens Next
```
📊 Cycle 120: Processed 5 metrics
📊 Cycle 121: Processed 5 metrics
   ✅ New agents deployed
   ✅ New metrics flowing
   ✅ Growth engine learning from new agents
   ✅ Automation rules checking new metrics
```

## 🔧 Configuration Options

Edit in `src/autonomous_background_service.py`:

### Polling Interval
```python
# In ServiceConfig class
polling_interval_seconds: int = 60  # Change this
```
- **60 seconds:** Production setting
- **5 seconds:** Demo/testing
- **300 seconds:** Low-frequency monitoring

### Market Analysis Frequency
```python
# In continuous_loop method
market_analysis_interval = 100  # Change this
```
- **100 cycles:** Frequent analysis (demo)
- **500 cycles:** Balance (production)
- **1000+ cycles:** Rare analysis (large systems)

### Auto-Execution
```python
# In ServiceConfig class
auto_trigger_enabled: bool = True        # Trigger waves automatically
auto_execute_enabled: bool = True        # Execute actions automatically
```

## 📈 Monitoring the System

### Watch Cycles Count
```
Look for: "📊 Cycle N: Collected X metrics"
Initial: Cycles 1-9 (single metrics)
Growing: Cycles 10+ (multiple metrics flowing)
Status: System is healthy if cycles keep incrementing
```

### Watch Market Analysis
```
Look for: "🌍 MARKET-DRIVEN BUILD PHASE"
Frequency: Every ~100 cycles (or configured interval)
Success: Counts of gaps detected and proposals generated
```

### Watch Agent Generation
```
Look for: "🏗️  BUILDING: AgentName"
Success: All 5 steps complete (code → files → tests → integration → validation)
Ready to Deploy: True/False
```

## 🔍 Verify it's Working

### Check 1: Cycles Incrementing
```bash
# Watch logs for cycle counter going up
# Should see: Cycle 1, 2, 3, 4, 5... continuously
```

### Check 2: Market Analysis Running
```bash
# After ~100 cycles (or configured interval), should see:
# 🌍 MARKET-DRIVEN BUILD PHASE
# 🔍 MARKET ANALYZER: Scanning real-world ecosystem...
```

### Check 3: New Files Generated
```bash
# Check if new agent files exist
ls -la src/agent/
ls -la src/integration/
ls -la tests/agent/

# Should see new files appearing as agents are built
```

## ⏰ Timeline Expectations

### First 100 cycles (~1.7 hours in demo mode)
- Background service running ✓
- Metrics collecting ✓
- Growth engine learning ✓
- Automation rules triggering ✓
- Waves deploying (when ready) ✓

### Cycle 100+ (Market Analysis Triggers)
- Market analysis runs ✓
- Gaps detected (19 found) ✓
- Build proposals generated ✓
- Autonomous builder queues builds ✓

### Cycle 100-110 (Builds Executing)
- Agent code generated ✓
- Tests created ✓
- Integration created ✓
- Builds validated ✓
- Ready to deploy ✓

### Cycle 110+ (New Agents Active)
- New agents deployed ✓
- New metrics flowing ✓
- Growth engine learns from them ✓
- System increasingly capable ✓

## 🎯 Success Checklist

- [ ] Background service starts without errors
- [ ] Cycles incrementing every 60 seconds
- [ ] Growth engine receiving metrics
- [ ] Automation rules triggering (watch logs)
- [ ] Waves deploying when ready
- [ ] Market analysis runs (after ~100 cycles)
- [ ] New agents being autonomously built
- [ ] Agent files appearing in src/agent/
- [ ] System runs continuously without stopping
- [ ] No manual intervention needed

## 🚨 Troubleshooting

### Service won't start
```bash
# Check Python version (needs 3.9+)
python3 --version

# Check imports
python3 -c "from src.growth_engine import AutonomousGrowthEngine; print('OK')"
python3 -c "from src.market_analyzer import MarketAnalyzer; print('OK')"
python3 -c "from src.autonomous_builder import AutonomousBuilder; print('OK')"
```

### No cycles incrementing
```bash
# Check if service is actually running
# Should see "RUNNING" status
# Check for exceptions in logs
```

### Market analysis not running
```bash
# Check cycle count (should be multiples of 100)
# Verify market_analysis_interval setting
# Check for exceptions in market analysis logs
```

### New agents not generating
```bash
# Check if market analysis is running first
# Verify autonomous_builder imports
# Check for exceptions in builder logs
# Check disk space for generated files
```

## 💾 Data Generated

### Metrics Auto-saved
```
data/market_analysis_latest.json
└─ Latest market analysis results
└─ Gaps detected, proposals, build recommendations

growth_data/metrics_*.json
└─ Historical metrics for learning

growth_data/learning_*.json
└─ Growth engine learning patterns
```

## 🛑 Stopping the Service

```bash
# Ctrl+C in terminal
Ctrl+C

# Service will shutdown gracefully
# Current metrics are automatically saved
```

## 🚀 Next Level: Multiple Instances

For production, run multiple instances:

```bash
# Terminal 1 - Main service
python3 src/autonomous_background_service.py

# Terminal 2 - Monitor metrics
watch -n 10 'cat data/market_analysis_latest.json | python3 -m json.tool | head -20'

# Terminal 3 - Watch for new agents
watch -n 5 'find src/agent -type f -newer src/market_analyzer.py'
```

---

**Status: Ready to Run** 🎉

Start the service and watch the autonomous system discover, build, and deploy new agents continuously.

No manual work needed. Just let it run.

