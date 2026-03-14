"""
Autonomous System Growth Engine
Self-feeding feedback loop for continuous improvement

Enables the Piddy system to:
1. Collect metrics from Week 1 test generation
2. Learn optimal patterns and configurations
3. Predict improvements needed for Phase 40 success
4. Auto-cascade improvements across phases
5. Feed learnings back to sub-agents for optimization

This creates a self-improving autonomous system.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class GrowthPattern(Enum):
    """Types of system growth patterns"""
    TEST_GENERATION_ACCELERATION = "test_generation_acceleration"
    COVERAGE_THRESHOLD_BREAKTHROUGH = "coverage_threshold_breakthrough"
    AGENT_EFFICIENCY_IMPROVEMENT = "agent_efficiency_improvement"
    PHASE_READINESS_UNLOCK = "phase_readiness_unlock"
    CASCADING_IMPROVEMENT = "cascading_improvement"
    PREDICTIVE_OPTIMIZATION = "predictive_optimization"


@dataclass
class SystemMetric:
    """Single system metric observation"""
    timestamp: str
    metric_name: str
    value: float
    threshold: Optional[float] = None
    unit: str = ""
    component: str = ""  # which phase/agent
    
    def is_milestone(self) -> bool:
        """Check if value crosses threshold"""
        return self.threshold is not None and self.value >= self.threshold


@dataclass
class LearningObservation:
    """Machine learning observation for future optimization"""
    timestamp: str
    pattern: GrowthPattern
    observation: str
    data_points: Dict = field(default_factory=dict)
    confidence: float = 0.0  # 0.0-1.0 how confident in this pattern
    recommended_action: str = ""


@dataclass
class AutomationRule:
    """Rule for automatic improvement cascade"""
    rule_id: str
    trigger_metric: str
    trigger_threshold: float
    action_component: str  # what to trigger
    action_name: str  # what to do
    enabled: bool = True
    priority: int = 5  # 1-10, higher = more critical


class AutonomousGrowthEngine:
    """
    Feeds the system to help it grow autonomously.
    
    Collects data, learns patterns, predicts improvements,
    and automatically cascades enhancements.
    """
    
    def __init__(self):
        """Initialize growth engine"""
        self.metrics_history: List[SystemMetric] = []
        self.learning_observations: List[LearningObservation] = []
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.phase_readiness_scores: Dict[int, float] = {}  # phase -> score
        self._setup_default_rules()
        self.logger = logging.getLogger(f"{__name__}.GrowthEngine")
        
    def _setup_default_rules(self):
        """Setup default automation rules for cascading improvements"""
        rules = [
            # Week 1: Test generation breakthrough
            AutomationRule(
                rule_id="w1_coverage_10pct",
                trigger_metric="coverage_percentage",
                trigger_threshold=10.0,
                action_component="phase42_test_gen",
                action_name="increase_batch_size",  # Scale to 75 files
                priority=8
            ),
            AutomationRule(
                rule_id="w1_coverage_20pct",
                trigger_metric="coverage_percentage",
                trigger_threshold=20.0,
                action_component="phase42_test_gen",
                action_name="enable_parallel_batches",  # 2 batches simultaneously
                priority=9
            ),
            
            # Week 2: PR review optimization
            AutomationRule(
                rule_id="w2_pr_review_ready",
                trigger_metric="tests_generated_total",
                trigger_threshold=2000.0,
                action_component="pr_review_agent",
                action_name="enable_deployment",  # Start PR review Week 2
                priority=10
            ),
            
            # Phase 40 success breakthrough
            AutomationRule(
                rule_id="phase40_success_70pct",
                trigger_metric="phase40_success_probability",
                trigger_threshold=0.70,
                action_component="phase41_coordinator",
                action_name="prepare_deployment",  # Get ready to unlock
                priority=10
            ),
            AutomationRule(
                rule_id="phase40_success_80pct",
                trigger_metric="phase40_success_probability",
                trigger_threshold=0.80,
                action_component="phase41_coordinator",
                action_name="enable_deployment",  # Unlock Phase 41
                priority=10
            ),
            
            # Merge conflict agent early start
            AutomationRule(
                rule_id="week2_enable_merges",
                trigger_metric="pr_review_success_rate",
                trigger_threshold=0.90,
                action_component="merge_conflict_agent",
                action_name="enable_deployment",  # Early Week 3
                priority=8
            ),
        ]
        
        for rule in rules:
            self.automation_rules[rule.rule_id] = rule
    
    async def feed_metric(self, metric: SystemMetric) -> List[Dict]:
        """
        Feed a new metric to the growth engine.
        
        The system learns and automatically cascades improvements.
        
        Args:
            metric: New system metric observation
            
        Returns:
            List of triggered automation actions (if any)
        """
        # 1. Store metric
        self.metrics_history.append(metric)
        self.logger.info(f"Metric recorded: {metric.metric_name}={metric.value} {metric.unit}")
        
        # 2. Check for milestones (threshold crossings)
        if metric.is_milestone():
            self.logger.warning(
                f"🎯 MILESTONE: {metric.metric_name} crossed threshold "
                f"{metric.threshold}! Current: {metric.value}"
            )
        
        # 3. Learn patterns from this metric
        observations = await self._learn_from_metric(metric)
        self.learning_observations.extend(observations)
        
        # 4. Check automation rules
        triggered_actions = await self._check_automation_rules(metric)
        
        # 5. Cascade improvements if needed
        cascades = await self._cascade_improvements(metric)
        triggered_actions.extend(cascades)
        
        # 6. Update phase readiness scores
        await self._update_phase_readiness(metric)
        
        return triggered_actions
    
    async def _learn_from_metric(self, metric: SystemMetric) -> List[LearningObservation]:
        """Learn patterns from new metric"""
        observations = []
        
        # Test generation acceleration pattern
        if metric.metric_name == "tests_generated_per_second":
            if metric.value > 100:  # Very fast
                obs = LearningObservation(
                    timestamp=datetime.utcnow().isoformat(),
                    pattern=GrowthPattern.TEST_GENERATION_ACCELERATION,
                    observation=f"Test generation accelerating: {metric.value} tests/sec",
                    data_points={"rate": metric.value},
                    confidence=0.85,
                    recommended_action="Increase batch size to capture more throughput"
                )
                observations.append(obs)
                self.logger.info(f"✨ LEARNED: {obs.pattern.value} - {obs.observation}")
        
        # Coverage threshold breakthrough
        if metric.metric_name == "coverage_percentage":
            if metric.value >= 25.0 and metric.value < 30.0:  # Approaching Week 1 goal
                obs = LearningObservation(
                    timestamp=datetime.utcnow().isoformat(),
                    pattern=GrowthPattern.COVERAGE_THRESHOLD_BREAKTHROUGH,
                    observation=f"Coverage breakthrough imminent: {metric.value:.1f}%",
                    data_points={"coverage": metric.value},
                    confidence=0.90,
                    recommended_action="Deploy Week 2 PR Review Agent immediately"
                )
                observations.append(obs)
        
        # Phase readiness unlock
        if metric.metric_name == "phase40_success_probability":
            if metric.value >= 0.70 and metric.value < 0.81:
                obs = LearningObservation(
                    timestamp=datetime.utcnow().isoformat(),
                    pattern=GrowthPattern.PHASE_READINESS_UNLOCK,
                    observation=f"Phase 41 approaching unlock: {metric.value:.1%} confidence",
                    data_points={"success_probability": metric.value},
                    confidence=0.95,
                    recommended_action="Prepare Phase 41 deployment infrastructure"
                )
                observations.append(obs)
        
        return observations
    
    async def _check_automation_rules(self, metric: SystemMetric) -> List[Dict]:
        """Check if any automation rules trigger"""
        triggered = []
        
        for rule_id, rule in self.automation_rules.items():
            if not rule.enabled:
                continue
            
            # Check if metric matches trigger
            if rule.trigger_metric == metric.metric_name:
                if metric.value >= rule.trigger_threshold:
                    # Rule triggered!
                    self.logger.warning(
                        f"🚀 AUTOMATION TRIGGERED: {rule_id} "
                        f"({metric.metric_name}={metric.value} >= {rule.trigger_threshold})"
                    )
                    
                    action = {
                        "rule_id": rule_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "trigger_metric": metric.metric_name,
                        "trigger_value": metric.value,
                        "action_component": rule.action_component,
                        "action_name": rule.action_name,
                        "priority": rule.priority,
                        "status": "triggered"
                    }
                    triggered.append(action)
                    
                    # Disable rule to prevent duplicate triggers
                    rule.enabled = False
        
        return triggered
    
    async def _cascade_improvements(self, metric: SystemMetric) -> List[Dict]:
        """Cascade improvements based on metric breakthrough"""
        cascades = []
        
        # When coverage hits 20%, enable parallel test generation
        if metric.metric_name == "coverage_percentage" and metric.value >= 20.0:
            cascade = {
                "type": GrowthPattern.CASCADING_IMPROVEMENT.value,
                "timestamp": datetime.utcnow().isoformat(),
                "source_metric": metric.metric_name,
                "source_value": metric.value,
                "cascade_action": "Enable parallel batch processing",
                "expected_improvement": "2x test generation throughput",
                "target_components": ["phase42_test_gen"],
            }
            cascades.append(cascade)
            self.logger.info(f"⛓️  CASCADE: {cascade['cascade_action']}")
        
        # When Phase 40 success hits 70%, prepare Phase 41 deployment
        if metric.metric_name == "phase40_success_probability" and metric.value >= 0.70:
            cascade = {
                "type": GrowthPattern.CASCADING_IMPROVEMENT.value,
                "timestamp": datetime.utcnow().isoformat(),
                "source_metric": metric.metric_name,
                "source_value": metric.value,
                "cascade_action": "Begin Phase 41 deployment prep",
                "expected_improvement": "Multi-repo coordination ready",
                "target_components": ["phase41_coordinator"],
            }
            cascades.append(cascade)
        
        return cascades
    
    async def _update_phase_readiness(self, metric: SystemMetric):
        """Update readiness scores for each phase based on metrics"""
        
        # Phase 41 readiness depends on Phase 40 success probability
        if metric.metric_name == "phase40_success_probability":
            self.phase_readiness_scores[41] = metric.value
            
            # Related: Phase 42 (refactoring) readiness
            if metric.value >= 0.80:
                self.phase_readiness_scores[42] = 1.0  # Ready to merge PRs
        
        # Phase 51 readiness (sub-agents) depends on test coverage
        if metric.metric_name == "coverage_percentage":
            phase51_readiness = min(metric.value / 50.0, 1.0)  # 50% = fully ready
            self.phase_readiness_scores[51] = phase51_readiness
    
    def get_system_growth_status(self) -> Dict:
        """Get human-readable system growth status"""
        
        # Calculate coverage trend
        coverage_metrics = [
            m for m in self.metrics_history
            if m.metric_name == "coverage_percentage"
        ]
        
        coverage_trend = None
        if len(coverage_metrics) >= 2:
            latest = coverage_metrics[-1].value
            previous = coverage_metrics[-2].value
            coverage_trend = latest - previous
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_metrics_recorded": len(self.metrics_history),
            "total_patterns_learned": len(self.learning_observations),
            "automation_triggers_fired": sum(
                1 for rule in self.automation_rules.values() if not rule.enabled
            ),
            "phase_readiness": self.phase_readiness_scores,
            "coverage_trend": coverage_trend,
            "system_learning_confidence": self._calculate_system_confidence(),
        }
    
    def _calculate_system_confidence(self) -> float:
        """Calculate overall system learning confidence"""
        if not self.learning_observations:
            return 0.0
        
        avg_confidence = sum(
            obs.confidence for obs in self.learning_observations
        ) / len(self.learning_observations)
        
        return avg_confidence
    
    def generate_growth_report(self) -> str:
        """Generate human-readable growth progress report"""
        status = self.get_system_growth_status()
        obs_count = len(self.learning_observations)
        trigger_count = status["automation_triggers_fired"]
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    AUTONOMOUS SYSTEM GROWTH REPORT                        ║
║                      Self-Feeding Feedback Loop                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

📊 SYSTEM METRICS:
  • Observations Recorded: {status['total_metrics_recorded']}
  • Patterns Learned: {obs_count}
  • Automation Rules Triggered: {trigger_count}
  • System Learning Confidence: {status['system_learning_confidence']:.1%}

📈 COVERAGE PROGRESS:
  • Current Trend: {status['coverage_trend'] or 'N/A'}%
  • Target Week 1: 28%
  • Phase 41 Unlock: 50%+

🎯 PHASE READINESS SCORES:
"""
        for phase, score in sorted(status["phase_readiness"].items()):
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            report += f"  Phase {phase}: {bar} {score:.0%}\n"
        
        if self.learning_observations:
            report += "\n🧠 RECENT LEARNINGS:\n"
            for obs in self.learning_observations[-3:]:
                report += f"  • {obs.pattern.value}: {obs.observation}\n"
                report += f"    → {obs.recommended_action}\n"
        
        report += f"\n✨ STATUS: AUTONOMOUS GROWTH ACTIVE AND LEARNING\n"
        return report
    
    async def predict_next_milestone(self) -> Optional[Dict]:
        """Predict next system milestone based on learning"""
        
        # Extract coverage history
        coverage_metrics = [
            m for m in self.metrics_history
            if m.metric_name == "coverage_percentage"
        ]
        
        if len(coverage_metrics) < 2:
            return None
        
        # Simple trend: calculate acceleration
        recent = coverage_metrics[-1].value
        previous = coverage_metrics[-2].value
        trend = recent - previous
        
        if trend <= 0:
            return None  # Not improving
        
        # Predict when we'll hit 28% (Week 1 goal)
        days_to_28_pct = (28.0 - recent) / (trend + 0.0001)  # Avoid division by zero
        
        return {
            "milestone": "Week 1 Success (28% coverage)",
            "current_coverage": recent,
            "trend": trend,
            "predicted_days": max(0, days_to_28_pct),
            "predicted_completion": (
                datetime.utcnow() + timedelta(days=days_to_28_pct)
            ).isoformat(),
            "confidence": 0.6 if len(coverage_metrics) < 5 else 0.8,
        }
    
    def save_growth_data(self, output_dir: str = "./growth_data"):
        """Save learning data for future agent improvement"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save metrics history
        metrics_file = Path(output_dir) / f"metrics_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(
                [
                    {
                        "timestamp": m.timestamp,
                        "metric_name": m.metric_name,
                        "value": m.value,
                        "unit": m.unit,
                    }
                    for m in self.metrics_history
                ],
                f,
                indent=2
            )
        
        # Save learning observations
        learning_file = Path(output_dir) / f"learning_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(learning_file, 'w') as f:
            json.dump(
                [
                    {
                        "timestamp": o.timestamp,
                        "pattern": o.pattern.value,
                        "observation": o.observation,
                        "confidence": o.confidence,
                        "recommended_action": o.recommended_action,
                    }
                    for o in self.learning_observations
                ],
                f,
                indent=2
            )
        
        self.logger.info(f"Growth data saved to {output_dir}")


# Example: Feed the system metrics for autonomous growth
async def example_feed_growth():
    """Example: Feed metrics to grow the system autonomously"""
    
    engine = AutonomousGrowthEngine()
    
    print("🚀 AUTONOMOUS GROWTH ENGINE - EXAMPLE FEEDING\n")
    
    # Simulate Week 1 progress (March 14-20)
    test_metrics = [
        # Day 1 (March 14)
        SystemMetric(
            timestamp=datetime(2026, 3, 14, 20, 0).isoformat(),
            metric_name="tests_generated_total",
            value=675.0,
            unit="tests",
            component="phase42_test_gen",
        ),
        SystemMetric(
            timestamp=datetime(2026, 3, 14, 20, 5).isoformat(),
            metric_name="coverage_percentage",
            value=5.0,
            unit="%",
            component="piddy_system",
        ),
        
        # Day 3 (Mid-week)
        SystemMetric(
            timestamp=datetime(2026, 3, 16, 18, 0).isoformat(),
            metric_name="tests_generated_total",
            value=2000.0,
            unit="tests",
            component="phase42_test_gen",
        ),
        SystemMetric(
            timestamp=datetime(2026, 3, 16, 18, 5).isoformat(),
            metric_name="coverage_percentage",
            value=15.0,
            threshold=10.0,
            unit="%",
            component="piddy_system",
        ),
        
        # Day 4 (approaching Week 1 goal)
        SystemMetric(
            timestamp=datetime(2026, 3, 17, 22, 0).isoformat(),
            metric_name="tests_generated_total",
            value=3500.0,
            threshold=2000.0,
            unit="tests",
            component="phase42_test_gen",
        ),
        SystemMetric(
            timestamp=datetime(2026, 3, 17, 22, 5).isoformat(),
            metric_name="coverage_percentage",
            value=23.0,
            threshold=20.0,
            unit="%",
            component="piddy_system",
        ),
        SystemMetric(
            timestamp=datetime(2026, 3, 17, 22, 10).isoformat(),
            metric_name="phase40_success_probability",
            value=0.72,
            threshold=0.70,
            unit="probability",
            component="phase40",
        ),
    ]
    
    # Feed metrics and watch system grow
    triggered_actions_all = []
    for metric in test_metrics:
        print(f"\n📥 FEEDING: {metric.metric_name} = {metric.value} {metric.unit}")
        actions = await engine.feed_metric(metric)
        triggered_actions_all.extend(actions)
        
        if actions:
            print(f"   ⚡ TRIGGERED {len(actions)} ACTION(S)")
            for action in actions:
                action_desc = action.get('action_name') or action.get('cascade_action', 'unknown')
                component = action.get('action_component') or action.get('target_components', ['unknown'])[0]
                print(f"      → {action_desc} on {component}")
    
    # Show growth report
    print("\n" + engine.generate_growth_report())
    
    # Predict next milestone
    milestone = await engine.predict_next_milestone()
    if milestone:
        print(f"\n🎯 PREDICTED MILESTONE:")
        print(f"   {milestone['milestone']}")
        print(f"   Estimated: {milestone['predicted_days']:.1f} days from now")
        print(f"   Confidence: {milestone['confidence']:.0%}")
    
    # Save learning data
    engine.save_growth_data()
    
    print(f"\n✨ AUTONOMOUS SYSTEM: Learning and growing! 🤖")


if __name__ == "__main__":
    asyncio.run(example_feed_growth())
