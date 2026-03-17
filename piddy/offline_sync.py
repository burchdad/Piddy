"""
Offline Support Layer - Mission Queue & Sync

Enables Piddy desktop app to work offline:
1. Queues missions while offline
2. Auto-syncs when connection restored
3. Handles conflicts and retries
4. Persists queue to local SQLite
"""

import logging
import asyncio
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import threading

logger = logging.getLogger(__name__)


class QueueStatus(Enum):
    """Status of mission in queue"""
    PENDING = "pending"  # Ready to execute or sync
    EXECUTING = "executing"  # Currently executing
    SYNCING = "syncing"  # Syncing with server
    COMPLETED = "completed"  # Successfully synced
    FAILED = "failed"  # Failed after retries
    CONFLICT = "conflict"  # Conflict with server version
    OFFLINE = "offline"  # Execution queued while offline


class OfflineMissionQueue:
    """
    Local queue for missions when offline/low-connectivity.
    
    Stores missions in local SQLite, syncs when connection available.
    """
    
    def __init__(self, db_path: str = "$HOME/.piddy_offline.db"):
        """Initialize offline queue"""
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.sync_thread = None
        self.sync_running = False
        self.is_online = True  # Track connectivity
        
        # Initialize database
        self._init_db()
        
        logger.info(f"✅ Offline queue initialized: {self.db_path}")
    
    def _init_db(self):
        """Initialize local SQLite database"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        
        # Create queue table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mission_queue (
                id TEXT PRIMARY KEY,
                mission_id TEXT UNIQUE,
                agent TEXT NOT NULL,
                task TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                created_at TEXT NOT NULL,
                queued_at TEXT NOT NULL,
                synced_at TEXT,
                error TEXT,
                result TEXT,
                conflict_resolution TEXT,
                metadata TEXT
            )
        """)
        
        # Create sync log
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event TEXT NOT NULL,
                mission_count INTEGER,
                synced_count INTEGER,
                failed_count INTEGER,
                details TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("✅ Offline database schema initialized")
    
    def queue_mission(self, mission_id: str, agent: str, task: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Queue a mission for execution (typically while offline)
        
        Returns: Queue entry dict
        """
        try:
            queue_id = str(uuid.uuid4())[:8]
            now = datetime.utcnow().isoformat()
            
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO mission_queue
                (id, mission_id, agent, task, status, created_at, queued_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                queue_id, mission_id, agent, task, 
                QueueStatus.OFFLINE.value, now, now,
                json.dumps(metadata or {})
            ))
            self.conn.commit()
            
            logger.info(f"📥 Mission queued: {mission_id} (queue_id: {queue_id})")
            
            return {
                "queue_id": queue_id,
                "mission_id": mission_id,
                "status": QueueStatus.OFFLINE.value,
                "queued_at": now,
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to queue mission: {e}")
            raise
    
    def get_pending_missions(self, limit: int = 100) -> List[Dict]:
        """Get all pending missions from queue"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT * FROM mission_queue
                WHERE status IN (?, ?)
                ORDER BY created_at ASC
                LIMIT ?
            """, (QueueStatus.PENDING.value, QueueStatus.OFFLINE.value, limit))
            
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"❌ Failed to get pending missions: {e}")
            return []
    
    def update_mission_status(
        self,
        mission_id: str,
        status: QueueStatus,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Update mission status in queue"""
        try:
            now = datetime.utcnow().isoformat()
            
            cur = self.conn.cursor()
            
            update_fields = {
                "status": status.value,
                "synced_at": now if status == QueueStatus.COMPLETED else None,
            }
            
            if result:
                update_fields["result"] = json.dumps(result)
            if error:
                update_fields["error"] = error
            
            set_clause = ", ".join(f"{k}=?" for k in update_fields.keys())
            values = list(update_fields.values()) + [mission_id]
            
            cur.execute(f"""
                UPDATE mission_queue
                SET {set_clause}
                WHERE mission_id = ?
            """, values)
            
            self.conn.commit()
            logger.info(f"✅ Mission status updated: {mission_id} → {status.value}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to update mission status: {e}")
            return False
    
    def increment_retry_count(self, mission_id: str) -> int:
        """Increment retry count for failed mission"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE mission_queue
                SET retry_count = retry_count + 1
                WHERE mission_id = ?
            """, (mission_id,))
            self.conn.commit()
            
            # Get updated count
            cur.execute("SELECT retry_count FROM mission_queue WHERE mission_id = ?", (mission_id,))
            row = cur.fetchone()
            return row[0] if row else 0
        
        except Exception as e:
            logger.error(f"❌ Failed to increment retry count: {e}")
            return -1
    
    def mark_conflict(self, mission_id: str, server_result: Dict, resolution: str = "client_wins") -> bool:
        """
        Mark mission as having conflict with server version
        
        resolution: "client_wins" | "server_wins" | "merge"
        """
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE mission_queue
                SET status = ?, conflict_resolution = ?, result = ?
                WHERE mission_id = ?
            """, (
                QueueStatus.CONFLICT.value,
                resolution,
                json.dumps(server_result),
                mission_id,
            ))
            self.conn.commit()
            
            logger.warning(f"⚠️ Mission conflict detected: {mission_id} (resolution: {resolution})")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to mark conflict: {e}")
            return False
    
    def mark_mission_completed(self, mission_id: str, result: Dict) -> bool:
        """Mark mission as successfully completed and synced"""
        return self.update_mission_status(
            mission_id,
            QueueStatus.COMPLETED,
            result=result
        )
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get overview of queue"""
        try:
            cur = self.conn.cursor()
            
            # Total missions in queue
            cur.execute("SELECT COUNT(*) FROM mission_queue")
            total = cur.fetchone()[0]
            
            # By status
            cur.execute("""
                SELECT status, COUNT(*) FROM mission_queue
                GROUP BY status
            """)
            by_status = dict(cur.fetchall())
            
            # Failed (maxed retries)
            cur.execute("""
                SELECT COUNT(*) FROM mission_queue
                WHERE retry_count >= max_retries AND status != ?
            """, (QueueStatus.COMPLETED.value,))
            failed = cur.fetchone()[0]
            
            return {
                "total": total,
                "by_status": by_status,
                "failed": failed,
                "is_online": self.is_online,
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to get queue stats: {e}")
            return {}
    
    def log_sync_event(self, event: str, mission_count: int, synced_count: int, failed_count: int, details: Optional[str] = None) -> None:
        """Log sync event for debugging"""
        try:
            now = datetime.utcnow().isoformat()
            
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO sync_log (timestamp, event, mission_count, synced_count, failed_count, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (now, event, mission_count, synced_count, failed_count, details))
            
            self.conn.commit()
        
        except Exception as e:
            logger.warning(f"Failed to log sync event: {e}")
    
    def clear_completed_missions(self, older_than_hours: int = 24) -> int:
        """Clean up old completed missions from queue"""
        try:
            from datetime import timedelta
            
            cutoff_time = (datetime.utcnow() - timedelta(hours=older_than_hours)).isoformat()
            
            cur = self.conn.cursor()
            cur.execute("""
                DELETE FROM mission_queue
                WHERE status = ? AND synced_at < ?
            """, (QueueStatus.COMPLETED.value, cutoff_time))
            
            deleted = cur.rowcount
            self.conn.commit()
            
            logger.info(f"🧹 Cleaned up {deleted} old completed missions")
            return deleted
        
        except Exception as e:
            logger.error(f"Failed to clear completed missions: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Offline queue closed")


class SyncManager:
    """
    Manages synchronization between local queue and server.
    
    Handles:
    - Detecting connectivity changes
    - Batching queue processfor efficient sync
    - Conflict resolution
    - Retry logic
    """
    
    def __init__(self, queue: OfflineMissionQueue, sync_api_url: Optional[str] = None):
        """Initialize sync manager"""
        self.queue = queue
        self.sync_api_url = sync_api_url or "http://localhost:3000/api/sync"
        self.is_syncing = False
        self.last_sync_time = None
        
        logger.info("✅ Sync manager initialized")
    
    async def auto_sync(self, interval_seconds: int = 5, retry_delay: int = 2) -> None:
        """
        Auto-sync: periodically check for pending missions and sync
        
        Runs in background, checking connectivity and syncing when online
        """
        while True:
            try:
                # If online, try to sync pending missions
                if self.queue.is_online and not self.is_syncing:
                    pending = self.queue.get_pending_missions(limit=50)
                    
                    if pending:
                        logger.info(f"🔄 Syncing {len(pending)} pending missions...")
                        synced_count, failed_count = await self.sync_batch(pending)
                        
                        self.last_sync_time = datetime.utcnow()
                        self.queue.log_sync_event(
                            "auto_sync",
                            len(pending),
                            synced_count,
                            failed_count,
                            f"Synced {synced_count} missions, {failed_count} failed"
                        )
                
                # Wait before next check
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"⚠️ Auto-sync error: {e}")
                await asyncio.sleep(retry_delay)
    
    async def sync_batch(self, missions: List[Dict]) -> tuple:
        """
        Sync a batch of missions to server
        
        Returns: (synced_count, failed_count)
        """
        synced_count = 0
        failed_count = 0
        
        for mission in missions:
            try:
                # Update status
                self.queue.update_mission_status(
                    mission["mission_id"],
                    QueueStatus.SYNCING
                )
                
                # Try to sync mission
                result = await self._sync_mission(mission)
                
                if result["success"]:
                    self.queue.mark_mission_completed(mission["mission_id"], result)
                    synced_count += 1
                    logger.info(f"✅ Mission synced: {mission['mission_id']}")
                else:
                    # Retry logic
                    retry_count = self.queue.increment_retry_count(mission["mission_id"])
                    
                    if retry_count >= mission.get("max_retries", 3):
                        self.queue.update_mission_status(
                            mission["mission_id"],
                            QueueStatus.FAILED,
                            error=result.get("error", "Max retries exceeded")
                        )
                        failed_count += 1
                        logger.error(f"❌ Mission failed (max retries): {mission['mission_id']}")
                    else:
                        logger.warning(f"⚠️ Mission sync failed, will retry: {mission['mission_id']}")
            
            except Exception as e:
                logger.error(f"❌ Error syncing mission {mission['mission_id']}: {e}")
                failed_count += 1
        
        return synced_count, failed_count
    
    async def _sync_mission(self, mission: Dict) -> Dict:
        """
        Sync single mission to server
        
        Returns: {"success": bool, "result": dict, "error": str}
        """
        try:
            # This would call actual server API
            # For now, simulated success
            logger.info(f"📤 Syncing mission: {mission['mission_id']}")
            
            # TODO: Make actual API call to server
            # response = await http_client.post(self.sync_api_url, json=mission)
            
            return {
                "success": True,
                "result": json.loads(mission.get("result", "{}")),
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def set_connectivity_status(self, is_online: bool) -> None:
        """Update connectivity status"""
        prev_status = self.queue.is_online
        self.queue.is_online = is_online
        
        if prev_status != is_online:
            status_str = "🌐 ONLINE" if is_online else "📴 OFFLINE"
            logger.info(f"{status_str}")
            
            if is_online:
                logger.info("🔄 Connection restored - starting sync...")


# Global instances
_offline_queue = None
_sync_manager = None

def get_offline_queue(db_path: Optional[str] = None) -> OfflineMissionQueue:
    """Get or create offline queue"""
    global _offline_queue
    if _offline_queue is None:
        _offline_queue = OfflineMissionQueue(db_path or "$HOME/.piddy_offline.db")
    return _offline_queue

def get_sync_manager(queue: Optional[OfflineMissionQueue] = None) -> SyncManager:
    """Get or create sync manager"""
    global _sync_manager
    if _sync_manager is None:
        if queue is None:
            queue = get_offline_queue()
        _sync_manager = SyncManager(queue)
    return _sync_manager
