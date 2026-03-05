"""
Memory and context persistence system using SQLite.

Stores conversation history, context, and agent state for retrieval
and learning across sessions.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message in conversation history."""
    id: Optional[int] = None
    user_id: str = ""
    channel_id: str = ""
    content: str = ""
    role: str = "user"  # "user", "assistant", "system"
    timestamp: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        if self.metadata:
            data["metadata"] = json.dumps(self.metadata)
        return data


@dataclass
class ConversationContext:
    """Represents a conversation thread."""
    id: Optional[int] = None
    conversation_id: str = ""
    user_id: str = ""
    channel_id: str = ""
    project_context: str = ""
    title: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict] = None


class Memory:
    """
    SQLite-based memory system for storing:
    - Conversation history
    - Context and state
    - Generated artifacts
    - User preferences
    """

    def __init__(self, db_path: str = "/workspaces/Piddy/.piddy_memory.db"):
        """
        Initialize memory system.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()
        logger.info(f"Memory initialized at {db_path}")

    def _initialize_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # Conversation contexts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                project_context TEXT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                role TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)

        # Artifacts table (generated code, configs, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                content TEXT NOT NULL,
                filename TEXT,
                file_path TEXT,
                language TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)

        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Context cache for quick lookups
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        channel_id: str,
        project_context: str = "",
        title: str = ""
    ) -> bool:
        """
        Create a new conversation context.

        Args:
            conversation_id: Unique conversation identifier
            user_id: User ID
            channel_id: Channel/thread ID
            project_context: Project context info
            title: Conversation title

        Returns:
            True if created successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO conversations 
                (conversation_id, user_id, channel_id, project_context, title)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, user_id, channel_id, project_context, title))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.info(f"Conversation already exists: {conversation_id}")
            return False

    def add_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
        role: str = "assistant",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add a message to conversation history.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            role: "user", "assistant", or "system"
            metadata: Additional metadata

        Returns:
            True if added successfully
        """
        try:
            cursor = self.conn.cursor()
            meta_json = json.dumps(metadata) if metadata else None
            cursor.execute("""
                INSERT INTO messages
                (conversation_id, user_id, content, role, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (conversation_id, user_id, content, role, meta_json))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False

    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """
        Retrieve conversation history.

        Args:
            conversation_id: Conversation ID
            limit: Maximum messages to retrieve

        Returns:
            List of messages
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (conversation_id, limit))

            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                if msg["metadata"]:
                    msg["metadata"] = json.loads(msg["metadata"])
                messages.append(msg)

            return list(reversed(messages))  # Return in chronological order
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []

    def save_artifact(
        self,
        conversation_id: str,
        artifact_type: str,
        content: str,
        filename: str = "",
        file_path: str = "",
        language: str = "python"
    ) -> bool:
        """
        Save a generated artifact (code, config, etc.).

        Args:
            conversation_id: Conversation ID
            artifact_type: Type of artifact (code, schema, config, etc.)
            content: Artifact content
            filename: Original filename
            file_path: Path where saved
            language: Programming language

        Returns:
            True if saved successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO artifacts
                (conversation_id, artifact_type, content, filename, file_path, language)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conversation_id, artifact_type, content, filename, file_path, language))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving artifact: {e}")
            return False

    def get_artifacts(self, conversation_id: str, artifact_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve saved artifacts.

        Args:
            conversation_id: Conversation ID
            artifact_type: Optional filter by type

        Returns:
            List of artifacts
        """
        try:
            cursor = self.conn.cursor()
            if artifact_type:
                cursor.execute("""
                    SELECT * FROM artifacts
                    WHERE conversation_id = ? AND artifact_type = ?
                    ORDER BY created_at DESC
                """, (conversation_id, artifact_type))
            else:
                cursor.execute("""
                    SELECT * FROM artifacts
                    WHERE conversation_id = ?
                    ORDER BY created_at DESC
                """, (conversation_id,))

            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error retrieving artifacts: {e}")
            return []

    def set_preference(self, user_id: str, key: str, value: str) -> bool:
        """Store user preference."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO preferences
                (user_id, preference_key, preference_value)
                VALUES (?, ?, ?)
            """, (user_id, key, value))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting preference: {e}")
            return False

    def get_preference(self, user_id: str, key: str, default: str = "") -> str:
        """Retrieve user preference."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT preference_value FROM preferences
                WHERE user_id = ? AND preference_key = ?
            """, (user_id, key))
            row = cursor.fetchone()
            return row[0] if row else default
        except Exception as e:
            logger.error(f"Error getting preference: {e}")
            return default

    def cache_context(self, key: str, value: Dict, ttl_minutes: int = 60) -> bool:
        """
        Cache context for quick retrieval.

        Args:
            key: Cache key
            value: Value to cache (will be JSON encoded)
            ttl_minutes: Time to live in minutes

        Returns:
            True if cached successfully
        """
        try:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
            value_json = json.dumps(value)

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO context_cache
                (key, value, expires_at)
                VALUES (?, ?, ?)
            """, (key, value_json, expires_at))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error caching context: {e}")
            return False

    def get_cached_context(self, key: str) -> Optional[Dict]:
        """
        Retrieve cached context if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT value FROM context_cache
                WHERE key = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            """, (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached context: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        try:
            cursor = self.conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM artifacts")
            total_artifacts = cursor.fetchone()[0]

            return {
                "conversations": total_conversations,
                "messages": total_messages,
                "artifacts": total_artifacts,
                "database_size": self.db_path.stat().st_size / 1024 / 1024  # MB
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Memory system closed")


# Global instance
_memory: Optional[Memory] = None


def get_memory() -> Memory:
    """Get or create global memory instance."""
    global _memory
    if _memory is None:
        _memory = Memory()
    return _memory
