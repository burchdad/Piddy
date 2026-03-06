"""
Phase 40: Mission Simulation Mode
Predicts mission outcomes before execution to ensure safety

Integrates with:
- Phase 38: LLM planning context
- Infrastructure: Simulation engine, approval system
- Phase 39: Impact visualization
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

from src.infrastructure.simulation_engine import SimulationEngine, SimulationResult
from src.infrastructure.approval_system import ApprovalManager, ApprovalRequest
from src.infrastructure.mission_config import MissionConfig, MissionConfigManager


class ApprovalStrategy(Enum):
    """Strategy for requiring approval"""
    NEVER = "never"                  #  No approval needed
    ON_HIGH_RISK = "on_high_risk"   # Approval if risk > threshold
    ON_MEDIUM_RISK = "on_medium_risk"  # Approval if medium+ risk
    ALWAYS = "always"                # Always require approval


@dataclass
class SimulationReport:
    """Report from mission simulation"""
    mission_id: str
    mission_name: str
    simulation_result: SimulationResult
    approval_needed: bool
    approval_reason: str
    can_proceed: bool
    confidence: float
    recommendation: str


class MissionSimulator:
    """Simulates missions before execution"""
    
    def __init__(self, approval_manager: ApprovalManager = None,
                 config_manager: MissionConfigManager = None):
        """Initialize mission simulator"""
        self.simulation_engine = SimulationEngine()
        self.approval_manager = approval_manager or ApprovalManager()
        self.config_manager = config_manager or MissionConfigManager()
        self.simulation_history: Dict = {}
    
    async def simulate_mission(self, mission_config: MissionConfig,
                              repo_context: Dict) -> SimulationReport:
        """
        Simulate a mission and determine if it should be approved
        
        Args:
            mission_config: Configuration for the mission
            repo_context: Repository state for simulation
        
        Returns:
            SimulationReport with prediction and recommendation
        """
        
        mission_id = f"{mission_config.name}_{id(mission_config)}"
        
        # Run simulation
        sim_result = self.simulation_engine.simulate(
            mission_config.name,
            {'id': mission_id, 'type': mission_config.type.value},
            repo_context
        )
        
        # Determine if approval is needed
        approval_needed, approval_reason = self._determine_approval_need(
            mission_config, sim_result
        )
        
        # Determine if we can proceed
        can_proceed = self._can_proceed(mission_config, sim_result, approval_needed)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            mission_config, sim_result, approval_needed, can_proceed
        )
        
        report = SimulationReport(
            mission_id=mission_id,
            mission_name=mission_config.name,
            simulation_result=sim_result,
            approval_needed=approval_needed,
            approval_reason=approval_reason,
            can_proceed=can_proceed,
            confidence=sim_result.confidence,
            recommendation=recommendation,
        )
        
        # Store in history
        self.simulation_history[mission_id] = report
        
        # If approval needed and we have an approval manager, request it
        if approval_needed and self.approval_manager:
            await self._request_approval(mission_config, sim_result, report)
        
        return report
    
    def _determine_approval_need(self, config: MissionConfig,
                                sim_result: SimulationResult) -> tuple[bool, str]:
        """Determine if approval is required"""
        
        # If config explicitly requires approval
        if config.approval_required:
            return True, "Mission configuration requires approval"
        
        # Check confidence threshold
        if sim_result.confidence < config.min_confidence:
            return True, f"Confidence too low: {sim_result.confidence:.2f} " \
                        f"(required: {config.min_confidence})"
        
        # Check risk level
        risk_score = sim_result.get_risk_score()
        if risk_score > 0.7:
            return True, f"High risk score: {risk_score:.2f}"
        
        # Check for potential issues
        if sim_result.potential_issues:
            return True, f"Potential issues detected: {', '.join(sim_result.potential_issues[:2])}"
        
        return False, ""
    
    def _can_proceed(self, config: MissionConfig, sim_result: SimulationResult,
                    approval_needed: bool) -> bool:
        """Determine if mission can proceed"""
        
        # Must pass basic safety checks
        if not sim_result.will_succeed:
            return False
        
        # Must meet confidence threshold
        if sim_result.confidence < config.min_confidence:
            return False
        
        # Must not have critical issues
        risk_score = sim_result.get_risk_score()
        if risk_score > 0.8:  # > 80% risk = always stop
            return False
        
        # If we needed approval, can't proceed (unless we got it)
        # This will be updated by approval system
        if approval_needed:
            return False
        
        return True
    
    def _generate_recommendation(self, config: MissionConfig,
                               sim_result: SimulationResult,
                               approval_needed: bool,
                               can_proceed: bool) -> str:
        """Generate human-readable recommendation"""
        
        if can_proceed:
            confidence_pct = int(sim_result.confidence * 100)
            return f"✅ APPROVED: Safe to execute ({confidence_pct}% confidence)"
        
        if approval_needed:
            if sim_result.potential_issues:
                issues = ", ".join(sim_result.potential_issues[:2])
                return f"⚠️ PENDING APPROVAL: Issues found - {issues}"
            else:
                return "⚠️ PENDING APPROVAL: Requires human review"
        
        # Something is wrong
        risk_pct = int(sim_result.get_risk_score() * 100)
        return f"❌ DO NOT EXECUTE: Too risky ({risk_pct}% risk), " \
               "confidence too low, or other safety concerns"
    
    async def _request_approval(self, config: MissionConfig,
                               sim_result: SimulationResult,
                               report: SimulationReport) -> None:
        """Request approval from humans"""
        
        # Create approval request
        approval_request = ApprovalRequest(
            mission_id=report.mission_id,
            mission_name=config.name,
            mission_type=config.type.value,
            description=config.description,
            prediction=sim_result.to_dict(),
            confidence=sim_result.confidence,
            risk_level=self._risk_level_string(sim_result.get_risk_score()),
            requires_approval=True,
            impact_summary=f"Will affect {sim_result.files_affected} files, "
                          f"changing ~{sim_result.lines_changed} lines",
            files_affected=list(sim_result.predicted_changes.keys())[:10],
            estimated_duration=sim_result.estimated_time,
        )
        
        # Request approval
        approved = await self.approval_manager.request_approval(approval_request)
        
        # Update report if approved
        if approved:
            report.can_proceed = True
            report.approval_needed = False
            report.recommendation = "✅ APPROVED: Human approval received - safe to execute"
    
    def _risk_level_string(self, risk_score: float) -> str:
        """Convert risk score to level string"""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        elif risk_score < 0.8:
            return "high"
        else:
            return "critical"
    
    def get_simulation_status(self, mission_id: str) -> Optional[Dict]:
        """Get status of a simulation"""
        if mission_id not in self.simulation_history:
            return None
        
        report = self.simulation_history[mission_id]
        return {
            'mission_id': mission_id,
            'mission_name': report.mission_name,
            'status': 'approved' if report.can_proceed else 'pending' if report.approval_needed else 'rejected',
            'confidence': report.confidence,
            'recommendation': report.recommendation,
            'expected_changes': report.simulation_result.lines_changed,
            'expected_files': report.simulation_result.files_affected,
        }
    
    def compare_simulations(self, mission_id1: str, mission_id2: str) -> Optional[Dict]:
        """Compare two simulations"""
        report1 = self.simulation_history.get(mission_id1)
        report2 = self.simulation_history.get(mission_id2)
        
        if not report1 or not report2:
            return None
        
        sim1 = report1.simulation_result
        sim2 = report2.simulation_result
        
        return {
            'mission1': report1.mission_name,
            'mission2': report2.mission_name,
            'confidence_diff': sim2.confidence - sim1.confidence,
            'risk_diff': sim2.get_risk_score() - sim1.get_risk_score(),
            'impact_diff': sim2.files_affected - sim1.files_affected,
            'less_risky': report2.mission_name if sim2.get_risk_score() < sim1.get_risk_score() else report1.mission_name,
        }


class MissionSimulationMode:
    """Manages simulation mode for autonomous missions"""
    
    def __init__(self, simulator: MissionSimulator = None):
        """Initialize simulation mode"""
        self.simulator = simulator or MissionSimulator()
        self.enabled = True  # Simulation is on by default
    
    async def simulate_and_execute(self, mission_config: MissionConfig,
                                  repo_context: Dict,
                                  executor_callback: callable = None) -> Dict:
        """
        Simulate mission and execute if safe
        
        Args:
            mission_config: Mission configuration
            repo_context: Repository context for simulation
            executor_callback: Function to execute if approved
        
        Returns:
            Execution result
        """
        
        if not self.enabled:
            # Skip simulation, execute directly (unsafe mode)
            if executor_callback:
                return await executor_callback()
            return {'error': 'No executor provided'}
        
        # Run simulation
        report = await self.simulator.simulate_mission(mission_config, repo_context)
        
        # Check if we can proceed
        if not report.can_proceed:
            return {
                'success': False,
                'reason': 'Simulation failed or approval denied',
                'recommendation': report.recommendation,
                'confidence': report.confidence,
            }
        
        # Execute mission
        if executor_callback:
            try:
                result = await executor_callback()
                result['simulated'] = True
                result['simulation_confidence'] = report.confidence
                return result
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'simulated': True,
                }
        
        return {
            'success': False,
            'error': 'No executor provided',
        }
    
    def enable(self):
        """Enable simulation mode"""
        self.enabled = True
    
    def disable(self):
        """Disable simulation mode (execute without simulation)"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if simulation mode is enabled"""
        return self.enabled
