"""Slack conversation context and memory management."""

import logging
from collections import defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


logger = logging.getLogger(__name__)


class ConversationContext:
    """Store context for a single conversation."""
    
    def __init__(self, channel_id: str, user_id: str, thread_ts: Optional[str] = None):
        """
        Initialize conversation context.
        
        Args:
            channel_id: Slack channel ID
            user_id: Slack user ID
            thread_ts: Thread timestamp if in a thread
        """
        self.channel_id = channel_id
        self.user_id = user_id
        self.thread_ts = thread_ts
        self.messages: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.metadata = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(msg)
        self.last_activity = datetime.now()
        logger.debug(f"Added {role} message to conversation")
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation messages."""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_context_string(self, limit: int = 10) -> str:
        """Get formatted conversation history for context."""
        recent_messages = self.get_messages(limit)
        if not recent_messages:
            return ""
        
        context = "Recent conversation history:\n"
        for msg in recent_messages:
            role = msg["role"].upper()
            content = msg["content"]
            context += f"{role}: {content}\n"
        
        return context
    
    def is_stale(self, timeout_minutes: int = 60) -> bool:
        """Check if conversation is stale."""
        return (datetime.now() - self.last_activity) > timedelta(minutes=timeout_minutes)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "channel_id": self.channel_id,
            "user_id": self.user_id,
            "thread_ts": self.thread_ts,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata
        }


class SlackConversationManager:
    """Manage Slack conversation contexts."""
    
    def __init__(self, max_contexts: int = 100, timeout_minutes: int = 60):
        """
        Initialize conversation manager.
        
        Args:
            max_contexts: Maximum number of active conversations
            timeout_minutes: Minutes before conversation expires
        """
        self.max_contexts = max_contexts
        self.timeout_minutes = timeout_minutes
        # Key: f"{channel_id}#{thread_ts}" or f"{channel_id}#{user_id}"
        self.contexts: Dict[str, ConversationContext] = {}
    
    def _get_context_key(
        self,
        channel_id: str,
        user_id: str,
        thread_ts: Optional[str] = None
    ) -> str:
        """Generate context key for conversation."""
        if thread_ts:
            return f"{channel_id}#{thread_ts}"
        return f"{channel_id}#{user_id}"
    
    def get_or_create_context(
        self,
        channel_id: str,
        user_id: str,
        thread_ts: Optional[str] = None
    ) -> ConversationContext:
        """Get existing or create new conversation context."""
        key = self._get_context_key(channel_id, user_id, thread_ts)
        
        if key not in self.contexts:
            # Clean up stale contexts if needed
            self._cleanup_stale()
            
            # Ensure we don't exceed max contexts
            if len(self.contexts) >= self.max_contexts:
                # Remove oldest context
                oldest_key = min(
                    self.contexts.keys(),
                    key=lambda k: self.contexts[k].last_activity
                )
                del self.contexts[oldest_key]
                logger.info(f"Removed oldest conversation context: {oldest_key}")
            
            # Create new context
            context = ConversationContext(channel_id, user_id, thread_ts)
            self.contexts[key] = context
            logger.info(f"Created new conversation context: {key}")
        
        return self.contexts[key]
    
    def _cleanup_stale(self):
        """Remove stale conversation contexts."""
        stale_keys = [
            key for key, context in self.contexts.items()
            if context.is_stale(self.timeout_minutes)
        ]
        
        for key in stale_keys:
            del self.contexts[key]
            logger.info(f"Removed stale conversation context: {key}")
    
    def get_context_history(
        self,
        channel_id: str,
        user_id: str,
        thread_ts: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Get conversation history as formatted string."""
        key = self._get_context_key(channel_id, user_id, thread_ts)
        
        if key in self.contexts:
            return self.contexts[key].get_context_string(limit)
        
        return ""
    
    def add_user_message(
        self,
        channel_id: str,
        user_id: str,
        content: str,
        thread_ts: Optional[str] = None
    ):
        """Add user message to conversation."""
        context = self.get_or_create_context(channel_id, user_id, thread_ts)
        context.add_message("user", content)
    
    def add_bot_message(
        self,
        channel_id: str,
        user_id: str,
        content: str,
        thread_ts: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Add bot response to conversation."""
        context = self.get_or_create_context(channel_id, user_id, thread_ts)
        context.add_message("bot", content, metadata)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation manager statistics."""
        return {
            "total_contexts": len(self.contexts),
            "max_contexts": self.max_contexts,
            "contexts": {
                key: {
                    "channel": context.channel_id,
                    "user": context.user_id,
                    "message_count": len(context.messages),
                    "created_at": context.created_at.isoformat(),
                    "last_activity": context.last_activity.isoformat(),
                    "is_stale": context.is_stale(self.timeout_minutes)
                }
                for key, context in self.contexts.items()
            }
        }


# Global conversation manager instance
_conversation_manager: Optional[SlackConversationManager] = None


def get_conversation_manager() -> SlackConversationManager:
    """Get or create global conversation manager."""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = SlackConversationManager()
    return _conversation_manager
