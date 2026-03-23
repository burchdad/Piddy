"""
Piddy Session & Context Manager

Manages conversation sessions with persistence:
- Session creation/retrieval with SQLite storage
- Message history per session
- Context window management (summarization for long conversations)
- User isolation (sessions belong to users)
- TTL-based session expiration

Storage: SQLite (piddy.db) — portable, no external dependencies.
"""

import logging
import sqlite3
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "piddy.db"

# Max messages to keep in active context before summarizing
MAX_CONTEXT_MESSAGES = 50
# Session TTL in hours
SESSION_TTL_HOURS = 72


@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class Session:
    """A conversation session."""
    session_id: str
    user_id: str = "default"
    title: str = ""
    created_at: str = ""
    updated_at: str = ""
    messages: List[Message] = field(default_factory=list)
    context_summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now


def _get_db() -> sqlite3.Connection:
    """Get SQLite connection with sessions table."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT DEFAULT 'default',
            title TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            context_summary TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_session 
        ON messages(session_id, timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_user 
        ON sessions(user_id, updated_at)
    """)
    conn.commit()
    return conn


class SessionManager:
    """Manages conversation sessions with SQLite persistence."""

    def create_session(self, user_id: str = "default", title: str = "") -> Session:
        """Create a new conversation session."""
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%b %d %H:%M')}",
        )
        conn = _get_db()
        try:
            conn.execute(
                "INSERT INTO sessions (session_id, user_id, title, created_at, updated_at, context_summary, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session.session_id, session.user_id, session.title,
                 session.created_at, session.updated_at, "", "{}"),
            )
            conn.commit()
        finally:
            conn.close()
        logger.info(f"Created session {session.session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session with its messages."""
        conn = _get_db()
        try:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None

            messages = []
            for msg_row in conn.execute(
                "SELECT role, content, timestamp, metadata FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,),
            ):
                messages.append(Message(
                    role=msg_row["role"],
                    content=msg_row["content"],
                    timestamp=msg_row["timestamp"],
                    metadata=json.loads(msg_row["metadata"] or "{}"),
                ))

            return Session(
                session_id=row["session_id"],
                user_id=row["user_id"],
                title=row["title"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                messages=messages,
                context_summary=row["context_summary"] or "",
                metadata=json.loads(row["metadata"] or "{}"),
            )
        finally:
            conn.close()

    def add_message(self, session_id: str, role: str, content: str,
                    metadata: Optional[Dict] = None) -> Message:
        """Add a message to a session."""
        msg = Message(role=role, content=content, metadata=metadata or {})
        conn = _get_db()
        try:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, msg.role, msg.content, msg.timestamp,
                 json.dumps(msg.metadata)),
            )
            conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (msg.timestamp, session_id),
            )
            conn.commit()
        finally:
            conn.close()
        return msg

    def get_context_window(self, session_id: str, max_messages: int = MAX_CONTEXT_MESSAGES) -> List[Dict]:
        """Get the context window for LLM calls.
        
        Returns recent messages plus any summary of older messages.
        Format suitable for passing to LLM as conversation history.
        """
        session = self.get_session(session_id)
        if not session:
            return []

        context = []

        # Include summary of older messages if we have one
        if session.context_summary:
            context.append({
                "role": "system",
                "content": f"Summary of earlier conversation:\n{session.context_summary}",
            })

        # Add recent messages (last N)
        recent = session.messages[-max_messages:]
        for msg in recent:
            context.append({"role": msg.role, "content": msg.content})

        return context

    def summarize_if_needed(self, session_id: str, summarizer=None) -> bool:
        """Check if context window is too large and summarize older messages.
        
        Args:
            session_id: Session to check
            summarizer: Optional callable(messages) -> summary_text
                        If None, uses a simple concatenation summary.
        """
        session = self.get_session(session_id)
        if not session or len(session.messages) <= MAX_CONTEXT_MESSAGES:
            return False

        # Messages to summarize (everything except recent)
        cutoff = len(session.messages) - MAX_CONTEXT_MESSAGES
        old_messages = session.messages[:cutoff]

        if summarizer:
            summary = summarizer(old_messages)
        else:
            # Simple summary: keep first/last messages and key points
            parts = []
            if session.context_summary:
                parts.append(session.context_summary)
            for msg in old_messages:
                # Keep assistant responses short, user messages in full
                if msg.role == "user":
                    parts.append(f"User: {msg.content[:200]}")
                elif msg.role == "assistant":
                    parts.append(f"Assistant: {msg.content[:100]}...")
            summary = "\n".join(parts[-20:])  # Keep last 20 summary lines

        # Update session summary
        conn = _get_db()
        try:
            conn.execute(
                "UPDATE sessions SET context_summary = ? WHERE session_id = ?",
                (summary, session_id),
            )
            conn.commit()
        finally:
            conn.close()

        logger.info(f"Summarized {len(old_messages)} messages for session {session_id}")
        return True

    def list_sessions(self, user_id: str = "default", limit: int = 50) -> List[Dict]:
        """List recent sessions for a user."""
        conn = _get_db()
        try:
            rows = conn.execute(
                """SELECT s.session_id, s.title, s.created_at, s.updated_at,
                          (SELECT COUNT(*) FROM messages m WHERE m.session_id = s.session_id) AS message_count
                   FROM sessions s WHERE s.user_id = ? ORDER BY s.updated_at DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
            return [
                {
                    "session_id": r["session_id"],
                    "title": r["title"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "message_count": r["message_count"],
                }
                for r in rows
            ]
        finally:
            conn.close()

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its messages."""
        conn = _get_db()
        try:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            result = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def cleanup_expired(self, ttl_hours: int = SESSION_TTL_HOURS) -> int:
        """Remove sessions older than TTL."""
        cutoff = (datetime.utcnow() - timedelta(hours=ttl_hours)).isoformat()
        conn = _get_db()
        try:
            # Get expired session IDs
            expired = conn.execute(
                "SELECT session_id FROM sessions WHERE updated_at < ?", (cutoff,)
            ).fetchall()
            ids = [r["session_id"] for r in expired]
            if ids:
                placeholders = ",".join("?" * len(ids))
                conn.execute(f"DELETE FROM messages WHERE session_id IN ({placeholders})", ids)
                conn.execute(f"DELETE FROM sessions WHERE session_id IN ({placeholders})", ids)
                conn.commit()
            return len(ids)
        finally:
            conn.close()


# Singleton
_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager."""
    global _manager
    if _manager is None:
        _manager = SessionManager()
    return _manager
