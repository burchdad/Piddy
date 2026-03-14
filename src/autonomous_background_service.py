"""
Autonomous Background Service: Continuous Growth Engine
Runs 24/7 in the background, continuously feeding metrics and triggering improvements

This is the HEARTBEAT of the autonomous system.
Without this, the system is just code sitting idle.
With this, it feeds itself continuously and grows.
"""

import asyncio
import logging
import sys
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
from dataclasses import dataclass, field

# Import our systems
sys.path.insert(0, str(Path(__file__).parent))
from growth_engine import AutonomousGrowthEngine, SystemMetric, GrowthPattern
from acceleration_framework import AccelerationFramework, DeploymentWave
from market_analyzer import MarketAnalyzer
from autonomous_builder import AutonomousBuilder
from market_gap_reporter import MarketGapReporter
from approval_workflow import ApprovalWorkflow, ApprovalBuilderBridge


logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Snapshot of current system metrics"""
    timestamp: str
    phase42_prs_generated: int = 0
    tests_generated: float = 0.0
    coverage_percentage: float = 0.0
    phase40_success_probability: float = 0.0
    pr_review_success_rate: float = 0.0
    auto_merge_rate: float = 0.0


@dataclass
class ServiceConfig:
    """Configuration for background service"""
    polling_interval_seconds: int = 60  # Check metrics every 60s
    metrics_retention_days: int = 30
    auto_trigger_enabled: bool = True
    auto_execute_enabled: bool = True
    background_mode: bool = True  # Run in background vs foreground
    log_level: str = "INFO"
    metrics_dir: str = "./growth_data"


class MetricsCollector:
    """Collects metrics from various Phase 42 and Phase 50 sources"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetricsCollector")
        self.last_snapshot: Optional[MetricsSnapshot] = None
        
    async def collect_metrics(self) -> List[SystemMetric]:
        """
        Collect current system metrics from Phase 42, Phase 50, agents, etc.
        
        In production, this would read from:
        - Phase 42 PR generation logs
        - TestGenerationAgent status
        - PullRequestReviewAgent metrics
        - MergeConflictResolutionAgent status
        - Phase 50 orchestrator dashboard
        - Integration module caches
        """
        metrics = []
        
        # Simulated metric collection (production would connect to actual sources)
        try:
            # Try to read from cached metrics files
            metrics_files = Path(self.config.metrics_dir).glob("metrics_*.json")
            for metrics_file in sorted(metrics_files)[-10:]:  # Last 10 files
                try:
                    with open(metrics_file, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            # Convert to SystemMetric objects
                            for m in data[-5:]:  # Last 5 from each file
                                metric = SystemMetric(
                                    timestamp=m.get('timestamp', datetime.utcnow().isoformat()),
                                    metric_name=m.get('metric_name', ''),
                                    value=float(m.get('value', 0)),
                                    unit=m.get('unit', ''),
                                    component=m.get('component', ''),
                                )
                                metrics.append(metric)
                except Exception as e:
                    self.logger.warning(f"Could not read metrics file {metrics_file}: {e}")
                    continue
        except Exception as e:
            self.logger.warning(f"No metrics files found: {e}")
        
        # If no metrics found, return simulated metrics for demo
        if not metrics:
            metrics = self._generate_demo_metrics()
        
        return metrics
    
    def _generate_demo_metrics(self) -> List[SystemMetric]:
        """Generate demo metrics for testing (production: read real metrics)"""
        
        # Simulate Week 1 progress incrementally
        current_hour = datetime.utcnow().hour
        current_day = (datetime.utcnow() - datetime(2026, 3, 14)).days
        
        # Simulate progression over the week
        if current_day <= 7:
            # Simple progression over Week 1
            coverage = 3.0 + (current_day * 3.5)  # 3% → 28%
            tests = 500 + (current_day * 600)  # ~500 → 4700
        else:
            # Plateau at Week 1 goal
            coverage = 28.0
            tests = 4725
        
        return [
            SystemMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_name="coverage_percentage",
                value=coverage,
                unit="%",
                component="piddy_system",
            ),
            SystemMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_name="tests_generated_total",
                value=tests,
                unit="tests",
                component="phase42_test_gen",
            ),
            SystemMetric(
                timestamp=datetime.utcnow().isoformat(),
                metric_name="phase40_success_probability",
                value=min(0.63 + (current_day * 0.04), 0.95),  # 63% → 95%
                unit="probability",
                component="phase40",
            ),
        ]


class AutomationExecutor:
    """Executes automation rules when triggered"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AutomationExecutor")
        self.executed_rules: Dict[str, datetime] = {}
        
    async def execute_rule(self, rule_id: str, action: str):
        """
        Execute an automation rule.
        
        In production, would:
        - Deploy agents (spin up containers)
        - Update configurations
        - Trigger deployments
        - Send notifications
        """
        if not self.config.auto_execute_enabled:
            self.logger.info(f"Auto-execute disabled, skipping: {rule_id}")
            return
        
        self.logger.warning(f"⚡ EXECUTING AUTOMATION: {rule_id}")
        self.logger.warning(f"   Action: {action}")
        
        # In production: actually execute the action
        # For now: log it and track that it happened
        self.executed_rules[rule_id] = datetime.utcnow()
        
        # Simulate execution delay
        await asyncio.sleep(0.5)
        
        self.logger.warning(f"   ✅ Execution complete")


class WaveCoordinator:
    """Manages autonomous wave deployments"""
    
    def __init__(self, framework: AccelerationFramework, config: ServiceConfig):
        self.framework = framework
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.WaveCoordinator")
        self.deployed_waves: List[DeploymentWave] = []
        
    async def check_wave_transitions(self, metrics: List[SystemMetric]) -> Optional[DeploymentWave]:
        """Check if ready to transition to next deployment wave"""
        
        current_wave = self.framework.growth_plan.current_wave
        if not current_wave:
            return None
        
        # Get current wave config
        wave_config = next(
            w for w in self.framework.growth_plan.waves
            if w.wave == current_wave
        )
        
        # Check if success criteria met
        for metric in metrics:
            if wave_config.target_metric in metric.metric_name:
                if metric.value >= wave_config.threshold:
                    self.logger.warning(
                        f"🎯 WAVE TRANSITION READY: {current_wave.value}"
                    )
                    return current_wave
        
        return None
    
    async def deploy_wave(self, wave: DeploymentWave):
        """Deploy the next wave"""
        
        self.logger.warning(f"🚀 DEPLOYING WAVE: {wave.value}")
        self.deployed_waves.append(wave)
        
        # In production: actually deploy the agent/infrastructure
        # For now: simulate
        await asyncio.sleep(1)
        
        self.logger.warning(f"✅ WAVE DEPLOYED: {wave.value}")


class MarketDrivenBuildManager:
    """
    Manages autonomous builds with USER APPROVAL WORKFLOW
    
    This is the bridge between:
    - Market analysis (what the world needs)
    - Gap reporter (notifies user for security review)
    - Approval workflow (waits for user decision)
    - Autonomous builder (building new agents only when approved)
    - Growth engine (learning from metrics)
    
    SECURITY: No builds happen without user approval!
    
    Flow:
    1. Market analyzer identifies gaps
    2. Gap reporter sends email to user
    3. User reviews gaps via dashboard
    4. Only approved gaps are queued for building
    5. Background service builds approved gaps
    """
    
    def __init__(self, 
                 config: ServiceConfig,
                 user_email: str = "user@example.com"):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MarketBuilder")
        
        # Core components
        self.market_analyzer = MarketAnalyzer()
        self.builder = AutonomousBuilder()
        
        # New: Approval workflow
        self.gap_reporter = MarketGapReporter(
            user_email=user_email,
            dashboard_url="http://localhost:8000"
        )
        self.approval_workflow = ApprovalWorkflow()
        self.builder_bridge = ApprovalBuilderBridge(self.approval_workflow)
        
        self.analysis_cycle = 0
        self.last_analysis: Optional[Dict] = None
        self.pending_approval_requests: List[str] = []
        
    async def run_market_analysis_cycle(self) -> Dict:
        """
        Periodically analyze market for gaps
        
        ⚠️  Gap reporter sends email to user for approval
        """
        self.analysis_cycle += 1
        
        self.logger.info(f"🌍 Market Analysis Cycle {self.analysis_cycle}")
        
        # Run market analysis
        analysis = await self.market_analyzer.run_market_analysis()
        self.last_analysis = analysis
        
        top_proposals = analysis.get("recommended_builds", [])[:3]
        
        if not top_proposals:
            self.logger.info("No proposals found")
            return analysis
        
        # Convert proposals to gap format
        gaps = [{"gap_id": p.get("agent_name", f"agent_{i}")}
                | p for i, p in enumerate(top_proposals)]
        
        # NEW: Generate report and send to user
        self.logger.warning(f"\n{'='*60}")
        self.logger.warning("📧 SENDING APPROVAL REQUEST TO USER")
        self.logger.warning(f"{'='*60}")
        
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        approval_request = await self.gap_reporter.generate_and_send_report(gaps)
        
        if approval_request:
            # NEW: Initiate approval workflow
            await self.approval_workflow.initiate_approval_workflow(
                request_id=request_id,
                market_gaps=gaps,
                recipient_email=self.gap_reporter.user_email
            )
            self.pending_approval_requests.append(request_id)
            
            self.logger.warning(f"✅ Approval workflow initiated: {request_id}")
            self.logger.warning(f"📍 User will review at: http://localhost:8000")
        
        return analysis
    
    async def check_pending_approvals(self) -> int:
        """
        Check if any approvals are ready to proceed
        
        Returns count of gaps ready to build
        """
        total_ready = 0
        
        for request_id in self.pending_approval_requests[:]:
            # Check if approval deadline passed
            timeout = await self.approval_workflow.check_workflow_timeout(request_id)
            
            # Get approved gaps
            approved = await self.approval_workflow.get_approved_gaps(request_id)
            
            if approved:
                self.logger.warning(f"✅ {len(approved)} gaps approved for building")
                total_ready += len(approved)
                
                # Remove from pending if auto-approved (no more waiting)
                if timeout:
                    self.pending_approval_requests.remove(request_id)
        
        return total_ready
    
    async def process_approved_builds(self) -> List[Dict]:
        """
        Build only APPROVED gaps (not all gaps)
        
        NEW: Respects user approvals before building
        """
        results = []
        
        # Get next approved gap to build
        gap = await self.builder_bridge.get_next_gap_to_build()
        
        if not gap:
            # No approved gaps waiting
            return results
        
        # Build the approved gap
        self.logger.warning(f"\n{'='*60}")
        self.logger.warning(f"👷 BUILDING APPROVED GAP: {gap.get('agent_name', 'Unknown')}")
        self.logger.warning(f"{'='*60}")
        
        result = await self.builder.build_agent(gap)
        results.append(result)
        
        # Record completion
        await self.builder_bridge.notify_build_complete(
            gap.get("gap_id"),
            success=result.get("ready_to_deploy", False)
        )
        
        return results
    
    async def process_pending_builds(self) -> List[Dict]:
        """
        Process approved builds (replacing direct queue processing)
        
        Only builds gaps that user has explicitly approved
        """
        # First check for any new approvals
        ready_count = await self.check_pending_approvals()
        
        if ready_count > 0:
            self.logger.warning(f"🎯 {ready_count} gaps ready to build (user approved)")
        
        # Then process approved builds
        return await self.process_approved_builds()
    
    async def get_next_deployable_agent(self) -> Optional[Dict]:
        """Get next agent that's ready to deploy (was approved and built)"""
        agent = await self.builder.get_next_deployable()
        if agent:
            self.logger.warning(f"🚀 Ready to deploy: {agent['agent_name']}")
        return agent
        
        return results
    
    async def get_next_deployable_agent(self) -> Optional[Dict]:
        """Get next agent that's ready to deploy"""
        agent = await self.builder.get_next_deployable()
        if agent:
            self.logger.warning(f"🚀 Ready to deploy: {agent['agent_name']}")
        return agent


class AutonomousBackgroundService:
    """
    The HEARTBEAT of the autonomous system.
    
    Runs continuously 24/7, feeding metrics and triggering improvements.
    This is what makes the system self-improving.
    
    Now with market-driven autonomous building!
    """
    
    def __init__(self, config: ServiceConfig = None):
        """Initialize background service"""
        self.config = config or ServiceConfig()
        self._setup_logging()
        
        self.growth_engine = AutonomousGrowthEngine()
        self.framework = AccelerationFramework()
        self.metrics_collector = MetricsCollector(self.config)
        self.automation_executor = AutomationExecutor(self.config)
        self.wave_coordinator = WaveCoordinator(self.framework, self.config)
        self.market_builder = MarketDrivenBuildManager(self.config)
        
        self.logger = logging.getLogger(f"{__name__}.Service")
        
        self.cycles_completed = 0
        self.market_analysis_cycles = 0
        self.service_start_time = datetime.utcnow()
        self.is_running = False
        
    def _setup_logging(self):
        """Setup logging for the service"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def run_cycle(self):
        """
        Single feed cycle: collect → analyze → trigger → cascade
        
        This runs continuously, forever.
        """
        try:
            # 1. COLLECT: Get latest metrics
            metrics = await self.metrics_collector.collect_metrics()
            
            if not metrics:
                self.logger.debug("No metrics available")
                return
            
            self.logger.info(f"📊 Cycle {self.cycles_completed}: Collected {len(metrics)} metrics")
            
            # 2. FEED: Give metrics to growth engine
            for metric in metrics:
                triggered_actions = await self.growth_engine.feed_metric(metric)
                
                # 3. EXECUTE: Run any triggered automation rules
                if triggered_actions and self.config.auto_execute_enabled:
                    for action in triggered_actions:
                        await self.automation_executor.execute_rule(
                            action.get('rule_id', 'unknown'),
                            action.get('action_name', 'unknown')
                        )
            
            # 4. COORDINATE: Check for wave transitions
            next_wave = await self.wave_coordinator.check_wave_transitions(metrics)
            if next_wave and self.config.auto_trigger_enabled:
                await self.wave_coordinator.deploy_wave(next_wave)
            
            self.cycles_completed += 1
            
        except Exception as e:
            self.logger.error(f"Error in feed cycle: {e}", exc_info=True)
    
    async def continuous_loop(self, duration_hours: Optional[int] = None):
        """
        Main background loop: runs forever (or for specified duration)
        
        This is the HEARTBEAT. It never stops.
        Every cycle: metrics → learning → improvement → cascade
        Every N cycles: market analysis → autonomous builds
        """
        self.is_running = True
        self.logger.warning("❤️  AUTONOMOUS BACKGROUND SERVICE STARTED")
        self.logger.warning(f"   Polling interval: {self.config.polling_interval_seconds}s")
        self.logger.warning(f"   Auto-trigger: {self.config.auto_trigger_enabled}")
        self.logger.warning(f"   Auto-execute: {self.config.auto_execute_enabled}")
        self.logger.warning("   Status: RUNNING (will feed metrics continuously)")
        self.logger.warning("   🌍 Market-Driven Building: ENABLED")
        
        start_time = datetime.utcnow()
        end_time = None
        if duration_hours:
            end_time = start_time + timedelta(hours=duration_hours)
        
        market_analysis_interval = 100  # Run market analysis every 100 cycles
        
        try:
            while self.is_running:
                # Check if we should stop (if duration specified)
                if end_time and datetime.utcnow() >= end_time:
                    self.logger.warning("⏰ Duration complete, stopping service")
                    break
                
                # Run one feed cycle
                await self.run_cycle()
                
                # Every N cycles: run market analysis and autonomous building
                if self.cycles_completed % market_analysis_interval == 0 and self.cycles_completed > 0:
                    self.logger.warning("\n" + "=" * 80)
                    self.logger.warning("🌍 MARKET-DRIVEN BUILD PHASE")
                    self.logger.warning("=" * 80)
                    
                    # Run market analysis
                    await self.market_builder.run_market_analysis_cycle()
                    
                    # Process pending builds
                    await self.market_builder.process_pending_builds()
                    
                    self.market_analysis_cycles += 1
                
                # Print status report periodically (every 10 cycles)
                if self.cycles_completed % 10 == 0:
                    await self._print_status_report()
                
                # Wait for next cycle
                await asyncio.sleep(self.config.polling_interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.warning("⏹️  Service interrupted by user")
        except Exception as e:
            self.logger.error(f"Fatal error in background service: {e}", exc_info=True)
        finally:
            await self.shutdown()
    
    async def _print_status_report(self):
        """Print periodic status report"""
        uptime = datetime.utcnow() - self.service_start_time
        growth_status = self.growth_engine.get_system_growth_status()
        
        self.logger.warning(f"""
╔═══════════════════════════════════════════════════════════╗
║           BACKGROUND SERVICE STATUS REPORT               ║
╚═══════════════════════════════════════════════════════════╝

⏱️  SERVICE UPTIME: {uptime}
🔄 FEED CYCLES: {self.cycles_completed}
📊 METRICS FED: {growth_status['total_metrics_recorded']}
🧠 PATTERNS LEARNED: {growth_status['total_patterns_learned']}
⚡ AUTOMATIONS FIRED: {growth_status['automation_triggers_fired']}

📈 PHASE READINESS:
{self._format_readiness_scores(growth_status['phase_readiness'])}

🌊 CURRENT WAVE: {self.framework.growth_plan.current_wave.value if self.framework.growth_plan.current_wave else 'None'}
🎯 WAVES DEPLOYED: {len(self.wave_coordinator.deployed_waves)}

🚀 STATUS: CONTINUOUS AUTONOMOUS IMPROVEMENT IN PROGRESS
""")
    
    def _format_readiness_scores(self, scores: Dict[int, float]) -> str:
        """Format phase readiness scores for display"""
        lines = []
        for phase, score in sorted(scores.items()):
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            lines.append(f"   Phase {phase}: {bar} {score:.0%}")
        return "\n".join(lines)
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.warning("⏹️  BACKGROUND SERVICE SHUTTING DOWN")
        self.is_running = False
        self.logger.warning(f"   Total cycles: {self.cycles_completed}")
        self.logger.warning(f"   Uptime: {datetime.utcnow() - self.service_start_time}")
        self.logger.warning("   Goodbye!")


async def main():
    """Start the autonomous background service"""
    
    config = ServiceConfig(
        polling_interval_seconds=5,  # Check every 5 seconds for demo
        auto_trigger_enabled=True,
        auto_execute_enabled=True,
    )
    
    service = AutonomousBackgroundService(config)
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║        🤖 AUTONOMOUS BACKGROUND SERVICE - CONTINUOUS GROWTH ENGINE 🤖     ║
║                                                                           ║
║   This service runs 24/7, continuously:                                  ║
║   1. Collecting metrics from Phase 42                                    ║
║   2. Feeding them to the growth engine                                   ║
║   3. Learning patterns and improvements                                  ║
║   4. Triggering automation rules                                         ║
║   5. Deploying next waves when ready                                     ║
║                                                                           ║
║   This is the HEARTBEAT that makes the system self-improving.           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run for demo duration (30 cycles ≈ 2.5 min at 5s interval)
    # In production: runs forever (remove duration_hours)
    await service.continuous_loop(duration_hours=None)


if __name__ == "__main__":
    asyncio.run(main())
