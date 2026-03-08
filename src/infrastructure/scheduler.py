"""
logger = logging.getLogger(__name__)
Mission Scheduler
Schedules and executes missions on a recurring basis

Supports:
- Phase 42: Nightly missions
- Phase 50+: Autonomous execution pipelines
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, time, timedelta
from abc import ABC, abstractmethod
import logging


class ScheduleFrequency(Enum):
    """Frequency of mission execution"""
    ONCE = "once"                   # One-time execution
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"               # Custom cron expression


@dataclass
class ScheduledMission:
    """Configuration for a scheduled mission"""
    
    mission_name: str                # Name of mission to run
    mission_id: str                  # Unique execution ID
    frequency: ScheduleFrequency    # How often to run
    next_execution: datetime        # Next scheduled time
    
    # Timing
    max_concurrency: int = 1         # Max concurrent executions
    timeout_seconds: int = 3600      # Max execution time
    
    # Execution tracking
    last_execution: Optional[datetime] = None
    last_result: Optional[Dict] = None
    failure_count: int = 0           # Consecutive failures
    max_failures: int = 3            # Disable after N failures
    enabled: bool = True
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    
    def should_run(self) -> bool:
        """Check if mission should run now"""
        if not self.enabled:
            return False
        
        if self.failure_count >= self.max_failures:
            return False
        
        return datetime.utcnow() >= self.next_execution
    
    def mark_executed(self, result: Dict) -> None:
        """Mark mission as executed"""
        self.last_execution = datetime.utcnow()
        self.last_result = result
        self.updated_at = datetime.utcnow()
        
        # Reset failure count on success
        if result.get('success', False):
            self.failure_count = 0
        else:
            self.failure_count += 1
        
        # Schedule next execution
        self._schedule_next()
    
    def _schedule_next(self) -> None:
        """Schedule the next execution"""
        now = datetime.utcnow()
        
        if self.frequency == ScheduleFrequency.ONCE:
            # Don't schedule again
            self.enabled = False
        elif self.frequency == ScheduleFrequency.HOURLY:
            self.next_execution = now + timedelta(hours=1)
        elif self.frequency == ScheduleFrequency.DAILY:
            self.next_execution = now + timedelta(days=1)
        elif self.frequency == ScheduleFrequency.WEEKLY:
            self.next_execution = now + timedelta(weeks=1)
        elif self.frequency == ScheduleFrequency.MONTHLY:
            # Add 30 days for simplicity
            self.next_execution = now + timedelta(days=30)


class MissionScheduler:
    """Schedules and executes missions"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.scheduled_missions: Dict[str, ScheduledMission] = {}
        self.execution_handlers: List[Callable] = []
        self.running = False
        self.current_executions: Dict[str, asyncio.Task] = {}
    
    def register_execution_handler(self, handler: Callable) -> None:
        """Register handler that executes missions"""
        self.execution_handlers.append(handler)
    
    def schedule_mission(self, scheduled_mission: ScheduledMission) -> None:
        """Add mission to schedule"""
        scheduled_mission.created_at = datetime.utcnow()
        scheduled_mission.updated_at = datetime.utcnow()
        self.scheduled_missions[scheduled_mission.mission_id] = scheduled_mission
    
    def unschedule_mission(self, mission_id: str) -> bool:
        """Remove mission from schedule"""
        if mission_id in self.scheduled_missions:
            del self.scheduled_missions[mission_id]
            return True
        return False
    
    def get_scheduled_missions(self) -> List[ScheduledMission]:
        """Get all scheduled missions"""
        return list(self.scheduled_missions.values())
    
    def get_missions_due(self) -> List[ScheduledMission]:
        """Get missions that should run now"""
        return [m for m in self.scheduled_missions.values() if m.should_run()]
    
    async def start(self) -> None:
        """Start the scheduler"""
        self.running = True
        
        while self.running:
            try:
                # Check for missions that should run
                missions_due = self.get_missions_due()
                
                for mission in missions_due:
                    # Don't exceed max concurrency
                    concurrent = sum(1 for m in self.current_executions.values() 
                                   if not m.done())
                    
                    if concurrent < mission.max_concurrency:
                        # Start execution
                        task = asyncio.create_task(
                            self._execute_mission(mission)
                        )
                        self.current_executions[mission.mission_id] = task
                
                # Clean up completed tasks
                self.current_executions = {
                    k: v for k, v in self.current_executions.items()
                    if not v.done()
                }
                
                # Check every 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.info(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        
        # Wait for all executions to complete
        if self.current_executions:
            await asyncio.gather(*self.current_executions.values(),
                                return_exceptions=True)
    
    async def _execute_mission(self, mission: ScheduledMission) -> None:
        """Execute a scheduled mission"""
        result = {
            'mission_id': mission.mission_id,
            'mission_name': mission.mission_name,
            'started_at': datetime.utcnow().isoformat(),
            'success': False,
            'result': None,
            'error': None,
        }
        
        try:
            # Call execution handlers
            for handler in self.execution_handlers:
                if asyncio.iscoroutinefunction(handler):
                    exec_result = await handler(mission)
                else:
                    exec_result = handler(mission)
                
                if exec_result:
                    result['result'] = exec_result
                    result['success'] = True
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        finally:
            result['completed_at'] = datetime.utcnow().isoformat()
            mission.mark_executed(result)
    
    def get_execution_status(self) -> Dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'total_scheduled': len(self.scheduled_missions),
            'currently_executing': len([t for t in self.current_executions.values() 
                                       if not t.done()]),
            'due_soon': len(self.get_missions_due()),
        }


class ScheduleBuilder:
    """Helper to build scheduled missions"""
    
    @staticmethod
    def hourly(mission_name: str, max_concurrency: int = 1) -> ScheduledMission:
        """Create hourly mission"""
        return ScheduledMission(
            mission_name=mission_name,
            mission_id=f"{mission_name}_hourly_{datetime.utcnow().timestamp()}",
            frequency=ScheduleFrequency.HOURLY,
            next_execution=datetime.utcnow() + timedelta(hours=1),
            max_concurrency=max_concurrency,
        )
    
    @staticmethod
    def daily(mission_name: str, at_time: str = "02:00", max_concurrency: int = 1) -> ScheduledMission:
        """Create daily mission at specific time"""
        # Parse time (e.g., "02:00")
        parts = at_time.split(':')
        hour = int(parts[0]) if len(parts) > 0 else 2
        minute = int(parts[1]) if len(parts) > 1 else 0
        
        # Calculate next execution
        now = datetime.utcnow()
        next_exec = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_exec <= now:
            next_exec += timedelta(days=1)
        
        return ScheduledMission(
            mission_name=mission_name,
            mission_id=f"{mission_name}_daily_{datetime.utcnow().timestamp()}",
            frequency=ScheduleFrequency.DAILY,
            next_execution=next_exec,
            max_concurrency=max_concurrency,
        )
    
    @staticmethod
    def weekly(mission_name: str, day: int = 0, at_time: str = "02:00", 
               max_concurrency: int = 1) -> ScheduledMission:
        """Create weekly mission (day 0=Monday)"""
        parts = at_time.split(':')
        hour = int(parts[0]) if len(parts) > 0 else 2
        minute = int(parts[1]) if len(parts) > 1 else 0
        
        now = datetime.utcnow()
        next_exec = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Calculate days until target day
        days_ahead = day - next_exec.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        
        next_exec += timedelta(days=days_ahead)
        
        return ScheduledMission(
            mission_name=mission_name,
            mission_id=f"{mission_name}_weekly_{datetime.utcnow().timestamp()}",
            frequency=ScheduleFrequency.WEEKLY,
            next_execution=next_exec,
            max_concurrency=max_concurrency,
        )
    
    @staticmethod
    def once(mission_name: str, at_time: datetime) -> ScheduledMission:
        """Create one-time mission"""
        return ScheduledMission(
            mission_name=mission_name,
            mission_id=f"{mission_name}_once_{datetime.utcnow().timestamp()}",
            frequency=ScheduleFrequency.ONCE,
            next_execution=at_time,
            max_concurrency=1,
        )
