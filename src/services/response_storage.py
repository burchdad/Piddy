"""Response storage service for long outputs."""

import uuid
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


class ResponseStorage:
    """Store and retrieve long response outputs."""
    
    def __init__(self, storage_dir: str = "/tmp/piddy_responses"):
        """Initialize response storage."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._load_index()
    
    def _load_index(self) -> None:
        """Load the response index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    self.index = json.load(f)
                logger.info(f"Loaded {len(self.index)} responses from index")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self.index = {}
        else:
            self.index = {}
    
    def _save_index(self) -> None:
        """Save the response index to disk."""
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _cleanup_old_responses(self) -> None:
        """Remove responses older than 7 days."""
        now = datetime.now().timestamp()
        expired_ids = []
        
        for response_id, metadata in self.index.items():
            created_at = metadata.get("created_at", 0)
            age_days = (now - created_at) / (24 * 3600)
            
            if age_days > 7:
                expired_ids.append(response_id)
        
        for response_id in expired_ids:
            try:
                response_file = self.storage_dir / f"{response_id}.json"
                if response_file.exists():
                    response_file.unlink()
                del self.index[response_id]
                logger.info(f"Deleted expired response: {response_id}")
            except Exception as e:
                logger.error(f"Error deleting response {response_id}: {e}")
        
        if expired_ids:
            self._save_index()
    
    def store_response(self, response_text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a response and return its ID.
        
        Args:
            response_text: The full response text
            metadata: Optional metadata (command_type, user_id, channel_id, etc.)
            
        Returns:
            Response ID for later retrieval
        """
        response_id = str(uuid.uuid4())[:8]
        
        response_file = self.storage_dir / f"{response_id}.json"
        
        data = {
            "content": response_text,
            "metadata": metadata or {},
            "created_at": datetime.now().timestamp(),
            "length": len(response_text)
        }
        
        try:
            with open(response_file, "w") as f:
                json.dump(data, f)
            
            # Update index
            self.index[response_id] = {
                "created_at": data["created_at"],
                "length": data["length"],
                "metadata": metadata or {}
            }
            self._save_index()
            
            logger.info(f"Stored response {response_id} ({len(response_text)} chars)")
            return response_id
            
        except Exception as e:
            logger.error(f"Error storing response: {e}")
            raise
    
    def get_response(self, response_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a stored response.
        
        Args:
            response_id: The response ID
            
        Returns:
            Response data dict with 'content' and 'metadata' keys, or None if not found
        """
        response_file = self.storage_dir / f"{response_id}.json"
        
        if not response_file.exists():
            logger.warning(f"Response not found: {response_id}")
            return None
        
        try:
            with open(response_file, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error retrieving response {response_id}: {e}")
            return None
    
    def cleanup(self) -> None:
        """Clean up old responses."""
        self._cleanup_old_responses()
    
    def get_summary(self, response_id: str, max_length: int = 500) -> Optional[str]:
        """
        Get a summary of a response (first N characters).
        
        Args:
            response_id: The response ID
            max_length: Maximum characters to return
            
        Returns:
            Summary text or None if not found
        """
        response_data = self.get_response(response_id)
        if not response_data:
            return None
        
        content = response_data.get("content", "")
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content


# Singleton instance
_storage_instance = None


def get_response_storage() -> ResponseStorage:
    """Get or create the response storage singleton."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ResponseStorage()
    return _storage_instance
