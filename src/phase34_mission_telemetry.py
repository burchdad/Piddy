"""
Phase 34: Mission Telemetry and Observability

Captures detailed metrics about autonomous missions to enable:
- Confidence threshold tuning
- Performance optimization
- Success rate tracking
- Revision pattern analysis

Metrics collected:
- mission_success_rate: % of missions that completed
- avg_confidence: Average confidence score across all missions
- revision_count: How many times plans were revised
- task_duration: How long each task took
- false_positive_rate: Rate of unsafe changes caught
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskTelemetry:
    """Telemetry for a single task execution"""
    task_name: str
    task_id: str
    mission_id: str
    status: str  # completed, failed, revised
    started_at: str
    completed_at: str
    duration_seconds: float
    confidence: float
    revisions: int = 0
    error_message: Optional[str] = None
    
    @property
    def duration(self) -> timedelta:
        """Get duration as timedelta"""
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.completed_at)
        return end - start


@dataclass
class MissionTelemetry:
    """Telemetry for a complete mission"""
    mission_id: str
    goal: str
    status: str  # completed, failed, partial
    started_at: str
    completed_at: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_confidence: float
    total_revisions: int
    tasks: List[TaskTelemetry] = field(default_factory=list)
    false_positives: int = 0
    safety_violations: int = 0
    
    @property
    def success_rate(self) -> float:
        """Percentage of tasks completed"""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks
    
    @property
    def duration(self) -> timedelta:
        """Get mission duration"""
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.completed_at)
        return end - start
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'mission_id': self.mission_id,
            'goal': self.goal,
            'status': self.status,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'duration_seconds': self.duration.total_seconds(),
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'avg_confidence': self.avg_confidence,
            'total_revisions': self.total_revisions,
            'false_positives': self.false_positives,
            'safety_violations': self.safety_violations,
        }


class MissionTelemetryCollector:
    """Collects and stores mission telemetry"""
    
    def __init__(self, db_path: str = '.piddy_telemetry.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize telemetry database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                goal TEXT,
                status TEXT,
                started_at TEXT,
                completed_at TEXT,
                duration_seconds REAL,
                total_tasks INTEGER,
                completed_tasks INTEGER,
                failed_tasks INTEGER,
                avg_confidence REAL,
                total_revisions INTEGER,
                false_positives INTEGER,
                safety_violations INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                mission_id TEXT,
                task_name TEXT,
                status TEXT,
                started_at TEXT,
                completed_at TEXT,
                duration_seconds REAL,
                confidence REAL,
                revisions INTEGER,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(mission_id) REFERENCES missions(mission_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_mission(self, telemetry: MissionTelemetry):
        """Store mission telemetry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = telemetry.to_dict()
        cursor.execute('''
            INSERT OR REPLACE INTO missions
            (mission_id, goal, status, started_at, completed_at, duration_seconds,
             total_tasks, completed_tasks, failed_tasks, avg_confidence,
             total_revisions, false_positives, safety_violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['mission_id'],
            data['goal'],
            data['status'],
            data['started_at'],
            data['completed_at'],
            data['duration_seconds'],
            data['total_tasks'],
            data['completed_tasks'],
            data['failed_tasks'],
            data['avg_confidence'],
            data['total_revisions'],
            data['false_positives'],
            data['safety_violations'],
        ))
        
        # Store individual tasks
        for task in telemetry.tasks:
            cursor.execute('''
                INSERT OR REPLACE INTO tasks
                (task_id, mission_id, task_name, status, started_at, completed_at,
                 duration_seconds, confidence, revisions, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.task_id,
                task.mission_id,
                task.task_name,
                task.status,
                task.started_at,
                task.completed_at,
                task.duration_seconds,
                task.confidence,
                task.revisions,
                task.error_message,
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Recorded telemetry for mission {telemetry.mission_id}")
    
    def get_mission_metrics(self, mission_id: str) -> Optional[Dict]:
        """Get metrics for a specific mission"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM missions WHERE mission_id = ?', (mission_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return dict(row)
    
    def get_stats_by_goal(self, goal_pattern: str) -> Dict[str, Any]:
        """Get aggregated stats for missions matching a goal"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                goal,
                COUNT(*) as total_missions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_missions,
                AVG(avg_confidence) as avg_confidence,
                SUM(total_revisions) as total_revisions,
                SUM(false_positives) as total_false_positives,
                SUM(safety_violations) as total_violations,
                AVG(duration_seconds) as avg_duration_seconds
            FROM missions
            WHERE goal LIKE ?
            GROUP BY goal
        ''', (f'%{goal_pattern}%',))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {}
        
        result = dict(row)
        if result.get('total_missions', 0) > 0:
            result['success_rate'] = (result.get('successful_missions', 0) or 0) / result['total_missions']
        else:
            result['success_rate'] = 0.0
        
        return result
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_missions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_missions,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_missions,
                AVG(avg_confidence) as avg_confidence,
                AVG(duration_seconds) as avg_duration_seconds,
                SUM(total_revisions) as total_revisions,
                SUM(false_positives) as total_false_positives,
                SUM(safety_violations) as total_violations
            FROM missions
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {}
        
        result = dict(row)
        if result.get('total_missions') and result['total_missions'] > 0:
            result['success_rate'] = (result.get('completed_missions', 0) or 0) / result['total_missions']
        else:
            result['success_rate'] = 0.0
        
        return result
    
    def get_task_performance(self) -> Dict[str, Dict]:
        """Get performance metrics by task type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                task_name,
                COUNT(*) as executions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(duration_seconds) as avg_duration,
                AVG(confidence) as avg_confidence,
                SUM(revisions) as total_revisions
            FROM tasks
            GROUP BY task_name
            ORDER BY executions DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        result = {}
        for row in rows:
            task_data = dict(row)
            if task_data.get('executions', 0) > 0:
                task_data['success_rate'] = (task_data.get('successful', 0) or 0) / task_data['executions']
            result[task_data['task_name']] = task_data
        
        return result
    
    def get_confidence_histogram(self, buckets: int = 10) -> Dict[str, int]:
        """Get histogram of confidence scores"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                ROUND(avg_confidence * ?, 0) / ? as bucket,
                COUNT(*) as count
            FROM missions
            GROUP BY bucket
            ORDER BY bucket
        ''', (buckets, buckets))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = {}
        for bucket, count in rows:
            if bucket is not None:
                result[f'{bucket}-{bucket + 1/buckets}'] = count
        
        return result
    
    def generate_report(self) -> str:
        """Generate human-readable telemetry report"""
        stats = self.get_all_stats()
        task_perf = self.get_task_performance()
        
        report = [
            "=" * 70,
            "PIDDY MISSION TELEMETRY REPORT",
            "=" * 70,
            "",
            f"Total Missions: {stats.get('total_missions', 0)}",
            f"Completed: {stats.get('completed_missions', 0)}",
            f"Failed: {stats.get('failed_missions', 0)}",
            f"Success Rate: {stats.get('success_rate', 0):.1%}",
            "",
            f"Average Confidence: {stats.get('avg_confidence', 0):.2%}",
            f"Average Duration: {stats.get('avg_duration_seconds', 0):.1f}s",
            f"Total Revisions: {stats.get('total_revisions', 0)}",
            f"Safety Violations: {stats.get('total_violations', 0)}",
            "",
            "TASK PERFORMANCE",
            "-" * 70,
        ]
        
        for task_name, metrics in sorted(task_perf.items(), 
                                         key=lambda x: x[1]['executions'], 
                                         reverse=True):
            report.append(f"\n{task_name}:")
            report.append(f"  Executions: {metrics.get('executions', 0)}")
            report.append(f"  Success: {metrics.get('success_rate', 0):.1%}")
            report.append(f"  Avg Duration: {metrics.get('avg_duration', 0):.1f}s")
            report.append(f"  Avg Confidence: {metrics.get('avg_confidence', 0):.2%}")
        
        report.append("\n" + "=" * 70)
        return "\n".join(report)


if __name__ == '__main__':
    # Example usage
    collector = MissionTelemetryCollector()
    
    # Print telemetry report
    print(collector.generate_report())
    
    # Get stats
    stats = collector.get_all_stats()
    print(f"\nOverall Stats: {json.dumps(stats, indent=2)}")
