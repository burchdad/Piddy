"""
Phase 42: Continuous Refactoring Mode
Automatically runs refactoring missions on a schedule

Integrates with:
- Phase 40: Mission simulation for safety
- Phase 42: Auto-merge policies
- Infrastructure: Mission scheduler, config manager
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from src.infrastructure.mission_config import MissionConfig, MissionConfigManager, MissionType
from src.infrastructure.scheduler import MissionScheduler, ScheduleFrequency, ScheduledMission, ScheduleBuilder


class AutoMergePolicy(Enum):
    """Policy for auto-merging PRs"""
    NEVER = "never"                 # Never auto-merge
    ON_SUCCESS = "on_success"       # Auto-merge if tests pass
    ON_APPROVAL = "on_approval"     # Auto-merge if approved
    ALWAYS = "always"               # Auto-merge without checks


@dataclass
class RefactoringMission:
    """Configuration for a refactoring mission"""
    name: str
    mission_config: MissionConfig
    frequency: ScheduleFrequency = ScheduleFrequency.DAILY
    auto_merge_policy: AutoMergePolicy = AutoMergePolicy.NEVER
    max_prs_per_period: int = 5     # Max concurrent PRs
    blackout_hours: List[int] = field(default_factory=list)  # Hours to skip
    dry_run_first: bool = True      # Simulate before execution
    requires_manual_approval: bool = False  # Override auto-merge for safety


class ContinuousRefactoringScheduler:
    """Schedules and executes continuous refactoring missions"""
    
    def __init__(self, config_manager: MissionConfigManager = None,
                 mission_scheduler: MissionScheduler = None):
        """Initialize continuous refactoring scheduler"""
        self.config_manager = config_manager or MissionConfigManager()
        self.mission_scheduler = mission_scheduler or MissionScheduler()
        self.refactoring_missions: Dict[str, RefactoringMission] = {}
        self.active_prs: Dict[str, Dict] = {}  # Tracks active PRs
        self.execution_history: List[Dict] = []
    
    def add_refactoring_mission(self, refactoring_mission: RefactoringMission) -> None:
        """Add a refactoring mission to the scheduler"""
        
        self.refactoring_missions[refactoring_mission.name] = refactoring_mission
        
        # Create scheduled mission
        if refactoring_mission.frequency == ScheduleFrequency.DAILY:
            scheduled = ScheduleBuilder.daily(
                refactoring_mission.name,
                at_time="02:00",  # 2 AM by default
            )
        elif refactoring_mission.frequency == ScheduleFrequency.WEEKLY:
            scheduled = ScheduleBuilder.weekly(
                refactoring_mission.name,
                day=6,  # Sunday
                at_time="02:00",
            )
        else:
            scheduled = ScheduleBuilder.daily(refactoring_mission.name)
        
        # Register with scheduler
        self.mission_scheduler.schedule_mission(scheduled)
    
    async def start_scheduler(self) -> None:
        """Start the continuous refactoring scheduler"""
        
        # Register execution handler
        self.mission_scheduler.register_execution_handler(self._execute_mission)
        
        # Start scheduler
        await self.mission_scheduler.start()
    
    async def stop_scheduler(self) -> None:
        """Stop the scheduler"""
        await self.mission_scheduler.stop()
    
    async def _execute_mission(self, scheduled_mission: ScheduledMission) -> Dict:
        """Execute a scheduled refactoring mission"""
        
        mission_name = scheduled_mission.mission_name
        refactoring = self.refactoring_missions.get(mission_name)
        
        if not refactoring:
            return {'error': f'Refactoring mission not found: {mission_name}'}
        
        # Check blackout hours
        from datetime import datetime
        now = datetime.utcnow()
        if now.hour in refactoring.blackout_hours:
            return {'skipped': True, 'reason': 'Blackout hour'}
        
        # Check active PR limit
        active_count = len([pr for pr in self.active_prs.values() if pr.get('status') == 'open'])
        if active_count >= refactoring.max_prs_per_period:
            return {'skipped': True, 'reason': 'Max concurrent PRs reached'}
        
        # Execute mission
        result = {
            'mission_name': mission_name,
            'executed_at': now.isoformat(),
            'success': True,
            'pr_id': None,
            'pr_title': None,
        }
        
        try:
            # In production, this would:
            # 1. Run the mission simulation (Phase 40)
            # 2. Create a PR with changes
            # 3. Run tests
            # 4. Auto-merge if policy allows
            
            # For now, create a mock PR
            pr_id = f"PR-{len(self.active_prs)+1}"
            self.active_prs[pr_id] = {
                'mission': mission_name,
                'status': 'open',
                'created_at': now.isoformat(),
                'auto_merge_policy': refactoring.auto_merge_policy.value,
            }
            
            result['pr_id'] = pr_id
            result['pr_title'] = refactoring.mission_config.description
            
            # Track in history
            self.execution_history.append(result)
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def get_nightly_missions(self) -> List[RefactoringMission]:
        """Get missions configured to run nightly"""
        return [m for m in self.refactoring_missions.values()
                if m.frequency in [ScheduleFrequency.DAILY, ScheduleFrequency.WEEKLY]]
    
    def get_active_prs(self) -> Dict:
        """Get all active PRs"""
        return self.active_prs.copy()
    
    def set_auto_merge_policy(self, pr_id: str, policy: AutoMergePolicy) -> None:
        """Set auto-merge policy for a PR"""
        if pr_id in self.active_prs:
            self.active_prs[pr_id]['auto_merge_policy'] = policy.value
    
    def get_execution_history(self, mission_name: str = None,
                             limit: int = 50) -> List[Dict]:
        """Get execution history"""
        if mission_name:
            history = [e for e in self.execution_history if e['mission_name'] == mission_name]
        else:
            history = self.execution_history[:]
        
        return history[-limit:]
    
    def can_execute_mission(self, refactoring: RefactoringMission) -> bool:
        """Check if mission can execute now"""
        
        from datetime import datetime
        now = datetime.utcnow()
        
        # Check blackout hours
        if now.hour in refactoring.blackout_hours:
            return False
        
        # Check active PR count
        active_count = len([pr for pr in self.active_prs.values() if pr.get('status') == 'open'])
        if active_count >= refactoring.max_prs_per_period:
            return False
        
        return True


def create_default_continuous_refactoring() -> ContinuousRefactoringScheduler:
    """Create scheduler with default refactoring missions"""
    
    scheduler = ContinuousRefactoringScheduler()
    
    # Cleanup: Run nightly
    cleanup_config = MissionConfig(
        name="nightly_cleanup",
        type=MissionType.CLEANUP,
        description="Remove dead code and unused imports",
        priority=3,
        risk_tolerance=None,  # Will be set
        approval_required=False,
        auto_merge=True,
        max_changes=50,
        tags=["cleanup", "nightly"],
        owner="system",
    )
    
    cleanup_mission = RefactoringMission(
        name="nightly_cleanup",
        mission_config=cleanup_config,
        frequency=ScheduleFrequency.DAILY,
        auto_merge_policy=AutoMergePolicy.ON_SUCCESS,
        blackout_hours=[9, 10, 11, 12, 13, 14, 15, 16, 17],  # Skip business hours
    )
    scheduler.add_refactoring_mission(cleanup_mission)
    
    # Coverage: Run 2x per week
    coverage_config = MissionConfig(
        name="weekly_coverage",
        type=MissionType.COVERAGE,
        description="Add tests for uncovered code",
        priority=4,
        risk_tolerance=None,
        approval_required=False,
        auto_merge=True,
        max_changes=20,
        tags=["coverage", "weekly"],
        owner="system",
    )
    
    coverage_mission = RefactoringMission(
        name="weekly_coverage",
        mission_config=coverage_config,
        frequency=ScheduleFrequency.WEEKLY,
        auto_merge_policy=AutoMergePolicy.ON_SUCCESS,
        blackout_hours=[],  # Can run anytime
    )
    scheduler.add_refactoring_mission(coverage_mission)
    
    # Type improvements: Run weekly
    type_config = MissionConfig(
        name="weekly_types",
        type=MissionType.TYPE_IMPROVEMENT,
        description="Add type hints to untyped code",
        priority=2,
        risk_tolerance=None,
        approval_required=False,
        auto_merge=True,
        max_changes=30,
        tags=["types", "weekly"],
        owner="system",
    )
    
    type_mission = RefactoringMission(
        name="weekly_types",
        mission_config=type_config,
        frequency=ScheduleFrequency.WEEKLY,
        auto_merge_policy=AutoMergePolicy.ON_SUCCESS,
        blackout_hours=[],
    )
    scheduler.add_refactoring_mission(type_mission)
    
    return scheduler


class NightlyMissionExecutor:
    """Executes nightly missions with safety checks"""
    
    def __init__(self, scheduler: ContinuousRefactoringScheduler):
        """Initialize executor"""
        self.scheduler = scheduler
    
    async def execute_nightly_missions(self, repo_context: Dict) -> Dict:
        """Execute all nightly missions"""
        
        results = {
            'total_missions': 0,
            'executed': 0,
            'skipped': 0,
            'failed': 0,
            'prs_created': [],
        }
        
        missions = self.scheduler.get_nightly_missions()
        results['total_missions'] = len(missions)
        
        for mission in missions:
            if not self.scheduler.can_execute_mission(mission):
                results['skipped'] += 1
                continue
            
            try:
                # Execute with simulation (Phase 40)
                # TODO: Integrate with Phase 40 simulator
                
                results['executed'] += 1
                results['prs_created'].append({
                    'mission': mission.name,
                    'status': 'created',
                })
                
            except Exception as e:
                results['failed'] += 1
                print(f"Failed to execute {mission.name}: {e}")
        
        return results
