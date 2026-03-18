"""
PostgreSQL Persistence Layer for Piddy

Stores:
- Mission history and results
- Agent execution logs
- System metrics
- Message history
- Audit trail

Falls back to SQLite if PostgreSQL unavailable
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional,Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

# Try to import psycopg2 for PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import Json, execute_values
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    logger.warning("⚠️ psycopg2 not available, falling back to SQLite")


@dataclass
class MissionRecord:
    """Database record for a mission"""
    mission_id: str
    agent: str
    task: str
    status: str
    start_time: str
    end_time: Optional[str]
    duration_ms: Optional[int]
    output: str
    error: str
    files_changed: List[str]
    commits: List[str]
    pr_url: Optional[str]
    result: Dict


@dataclass
class LogEntry:
    """Database record for a log entry"""
    id: str
    agent: str
    level: str
    message: str
    timestamp: str
    context: Dict


class PersistenceLayer:
    """Unified database access layer"""
    
    def __init__(self, db_type: str = "sqlite", **kwargs):
        """
        Initialize persistence layer
        
        Args:
            db_type: 'postgres' or 'sqlite'
            **kwargs: Connection parameters (host, port, user, password, database)
        """
        self.db_type = db_type
        self.conn = None
        
        if db_type == "postgres" and HAS_PSYCOPG2:
            self._connect_postgres(**kwargs)
        else:
            self._connect_sqlite(kwargs.get("database", ".piddy.db"))
        
        self._create_schema()
    
    def _connect_postgres(self, host="localhost", port=5432, user="piddy", password="piddy", database="piddy_db"):
        """Connect to PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            logger.info(f"✅ Connected to PostgreSQL: {user}@{host}:{port}/{database}")
            self.db_type = "postgres"
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}, falling back to SQLite")
            self._connect_sqlite()
    
    def _connect_sqlite(self, db_path: str = ".piddy.db"):
        """Connect to SQLite"""
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"✅ Connected to SQLite: {db_path}")
            self.db_type = "sqlite"
        except Exception as e:
            logger.error(f"❌ SQLite connection failed: {e}")
            raise
    
    def _create_schema(self):
        """Create database tables if they don't exist"""
        if self.db_type == "postgres":
            self._create_postgres_schema()
        else:
            self._create_sqlite_schema()
    
    def _create_postgres_schema(self):
        """Create PostgreSQL tables"""
        cur = self.conn.cursor()
        try:
            # Missions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id VARCHAR(255) PRIMARY KEY,
                    agent VARCHAR(255),
                    task TEXT,
                    status VARCHAR(50),
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_ms INTEGER,
                    output TEXT,
                    error TEXT,
                    files_changed JSONB,
                    commits JSONB,
                    pr_url VARCHAR(255),
                    result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Logs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id VARCHAR(255) PRIMARY KEY,
                    agent VARCHAR(255),
                    level VARCHAR(20),
                    message TEXT,
                    timestamp TIMESTAMP,
                    context JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id VARCHAR(255) PRIMARY KEY,
                    sender_id VARCHAR(255),
                    receiver_id VARCHAR(255),
                    content TEXT,
                    timestamp TIMESTAMP,
                    priority INTEGER,
                    status VARCHAR(50),
                    action VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Metrics table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    metric_name VARCHAR(255),
                    value FLOAT,
                    timestamp TIMESTAMP,
                    context JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mission Approvals table (TRUST LAYER)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mission_approvals (
                    mission_id VARCHAR(255) PRIMARY KEY,
                    task_description TEXT,
                    risk_level VARCHAR(50),
                    requester_id VARCHAR(255),
                    files_changed JSONB,
                    lines_added INTEGER,
                    lines_deleted INTEGER,
                    estimated_execution_time_sec INTEGER,
                    status VARCHAR(50) DEFAULT 'pending',
                    approved_by VARCHAR(255),
                    approval_reason TEXT,
                    requested_at TIMESTAMP,
                    approved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("✅ PostgreSQL schema created")
        except Exception as e:
            logger.error(f"❌ Schema creation failed: {e}")
            self.conn.rollback()
    
    def _create_sqlite_schema(self):
        """Create SQLite tables"""
        cur = self.conn.cursor()
        try:
            # Missions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    agent TEXT,
                    task TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_ms INTEGER,
                    output TEXT,
                    error TEXT,
                    files_changed TEXT,
                    commits TEXT,
                    pr_url TEXT,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Logs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY,
                    agent TEXT,
                    level TEXT,
                    message TEXT,
                    timestamp TEXT,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    sender_id TEXT,
                    receiver_id TEXT,
                    content TEXT,
                    timestamp TEXT,
                    priority INTEGER,
                    status TEXT,
                    action TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Metrics table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    value REAL,
                    timestamp TEXT,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mission Approvals table (TRUST LAYER)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mission_approvals (
                    mission_id TEXT PRIMARY KEY,
                    task_description TEXT,
                    risk_level TEXT,
                    requester_id TEXT,
                    files_changed TEXT,
                    lines_added INTEGER,
                    lines_deleted INTEGER,
                    estimated_execution_time_sec INTEGER,
                    status TEXT DEFAULT 'pending',
                    approved_by TEXT,
                    approval_reason TEXT,
                    requested_at TEXT,
                    approved_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("✅ SQLite schema created")
        except Exception as e:
            logger.error(f"❌ Schema creation failed: {e}")
            self.conn.rollback()
    
    # ========================================================================
    # MISSIONS
    # ========================================================================
    
    def save_mission(self, mission: Dict) -> bool:
        """Save/update mission execution result"""
        try:
            cur = self.conn.cursor()
            
            # Prepare data
            files_changed_json = json.dumps(mission.get("files_changed", []))
            commits_json = json.dumps(mission.get("commits", []))
            result_json = json.dumps(mission.get("result", {}))
            
            if self.db_type == "postgres":
                cur.execute("""
                    INSERT INTO missions
                    (mission_id, agent, task, status, start_time, end_time, duration_ms,
                     output, error, files_changed, commits, pr_url, result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (mission_id) DO UPDATE SET
                    status=EXCLUDED.status, end_time=EXCLUDED.end_time,
                    output=EXCLUDED.output, error=EXCLUDED.error
                """, (
                    mission["mission_id"], mission["agent"], mission["task"],
                    mission["status"], mission["start_time"], mission.get("end_time"),
                    mission.get("duration_ms"), mission.get("output", ""),
                    mission.get("error", ""), files_changed_json, commits_json,
                    mission.get("pr_url"), result_json
                ))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO missions
                    (mission_id, agent, task, status, start_time, end_time, duration_ms,
                     output, error, files_changed, commits, pr_url, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mission["mission_id"], mission["agent"], mission["task"],
                    mission["status"], mission["start_time"], mission.get("end_time"),
                    mission.get("duration_ms"), mission.get("output", ""),
                    mission.get("error", ""), files_changed_json, commits_json,
                    mission.get("pr_url"), result_json
                ))
            
            self.conn.commit()
            logger.info(f"✅ Saved mission: {mission['mission_id']}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save mission: {e}")
            self.conn.rollback()
            return False
    
    def get_mission(self, mission_id: str) -> Optional[Dict]:
        """Get mission by ID"""
        try:
            cur = self.conn.cursor()
            if self.db_type == "postgres":
                cur.execute("SELECT * FROM missions WHERE mission_id = %s", (mission_id,))
            else:
                cur.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
            
            row = cur.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get mission: {e}")
            return None
    
    def get_missions(self, agent: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get missions, optionally filtered by agent"""
        try:
            cur = self.conn.cursor()
            if agent:
                if self.db_type == "postgres":
                    cur.execute(
                        "SELECT * FROM missions WHERE agent = %s ORDER BY start_time DESC LIMIT %s",
                        (agent, limit)
                    )
                else:
                    cur.execute(
                        "SELECT * FROM missions WHERE agent = ? ORDER BY start_time DESC LIMIT ?",
                        (agent, limit)
                    )
            else:
                if self.db_type == "postgres":
                    cur.execute("SELECT * FROM missions ORDER BY start_time DESC LIMIT %s", (limit,))
                else:
                    cur.execute("SELECT * FROM missions ORDER BY start_time DESC LIMIT ?", (limit,))
            
            rows = cur.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get missions: {e}")
            return []
    
    # ========================================================================
    # LOGS
    # ========================================================================
    
    def save_log(self, log_entry: Dict) -> bool:
        """Save log entry"""
        try:
            cur = self.conn.cursor()
            context_json = json.dumps(log_entry.get("context", {}))
            
            if self.db_type == "postgres":
                cur.execute("""
                    INSERT INTO logs (id, agent, level, message, timestamp, context)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    log_entry["id"], log_entry["agent"], log_entry["level"],
                    log_entry["message"], log_entry["timestamp"], context_json
                ))
            else:
                cur.execute("""
                    INSERT OR IGNORE INTO logs (id, agent, level, message, timestamp, context)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    log_entry["id"], log_entry["agent"], log_entry["level"],
                    log_entry["message"], log_entry["timestamp"], context_json
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save log: {e}")
            self.conn.rollback()
            return False
    
    def get_logs(self, agent: Optional[str] = None, level: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get logs, optionally filtered"""
        try:
            cur = self.conn.cursor()
            
            query_parts = ["SELECT * FROM logs WHERE 1=1"]
            params = []
            
            if agent:
                query_parts.append("AND agent = ?")
                params.append(agent)
            if level:
                query_parts.append("AND level = ?")
                params.append(level)
            
            query_parts.append(f"ORDER BY timestamp DESC LIMIT ?")
            params.append(limit)
            
            query = " ".join(query_parts)
            
            if self.db_type == "postgres":
                query = query.replace("?", "%s")
                cur.execute(query, params)
            else:
                cur.execute(query, params)
            
            rows = cur.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get logs: {e}")
            return []
    
    # ========================================================================
    # MESSAGES
    # ========================================================================
    
    def save_message(self, message: Dict) -> bool:
        """Save message"""
        try:
            cur = self.conn.cursor()
            
            if self.db_type == "postgres":
                cur.execute("""
                    INSERT INTO messages
                    (message_id, sender_id, receiver_id, content, timestamp, priority, status, action)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (message_id) DO NOTHING
                """, (
                    message.get("id"), message["sender"], message.get("receiver"),
                    message["content"], message["timestamp"], message.get("priority", 1),
                    message.get("status", "sent"), message.get("action")
                ))
            else:
                cur.execute("""
                    INSERT OR IGNORE INTO messages
                    (message_id, sender_id, receiver_id, content, timestamp, priority, status, action)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.get("id"), message["sender"], message.get("receiver"),
                    message["content"], message["timestamp"], message.get("priority", 1),
                    message.get("status", "sent"), message.get("action")
                ))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save message: {e}")
            self.conn.rollback()
            return False
    
    def get_messages(self, agent: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get messages"""
        try:
            cur = self.conn.cursor()
            if agent:
                if self.db_type == "postgres":
                    cur.execute(
                        "SELECT * FROM messages WHERE sender_id = %s OR receiver_id = %s ORDER BY timestamp DESC LIMIT %s",
                        (agent, agent, limit)
                    )
                else:
                    cur.execute(
                        "SELECT * FROM messages WHERE sender_id = ? OR receiver_id = ? ORDER BY timestamp DESC LIMIT ?",
                        (agent, agent, limit)
                    )
            else:
                if self.db_type == "postgres":
                    cur.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT %s", (limit,))
                else:
                    cur.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?", (limit,))
            
            rows = cur.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get messages: {e}")
            return []
    
    # ========================================================================
    # METRICS
    # ========================================================================
    
    def save_metric(self, metric_name: str, value: float, context: Optional[Dict] = None) -> bool:
        """Save a metric"""
        try:
            cur = self.conn.cursor()
            timestamp = datetime.utcnow().isoformat()
            context_json = json.dumps(context or {})
            
            if self.db_type == "postgres":
                cur.execute("""
                    INSERT INTO metrics (metric_name, value, timestamp, context)
                    VALUES (%s, %s, %s, %s)
                """, (metric_name, value, timestamp, context_json))
            else:
                cur.execute("""
                    INSERT INTO metrics (metric_name, value, timestamp, context)
                    VALUES (?, ?, ?, ?)
                """, (metric_name, value, timestamp, context_json))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save metric: {e}")
            self.conn.rollback()
            return False
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dict"""
        if self.db_type == "postgres":
            return dict(row.__dict__['record'])
        else:
            return dict(row)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            cur = self.conn.cursor()
            if self.db_type == "postgres":
                cur.execute("SELECT 1")
            else:
                cur.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False


# Global persistence layer instance
_persistence = None

def get_persistence() -> PersistenceLayer:
    """Get or create global persistence layer"""
    global _persistence
    if _persistence is None:
        db_type = os.environ.get("DATABASE_TYPE", "sqlite")
        _persistence = PersistenceLayer(db_type=db_type)
    return _persistence
