"""Slack event handlers."""

import logging
import json
import hashlib
import hmac
import time
from typing import Dict, Any
from fastapi import Request

from config.settings import get_settings


logger = logging.getLogger(__name__)


class SlackEventHandler:
    """Handle Slack events and requests."""
    
    def __init__(self):
        """Initialize event handler."""
        self.settings = get_settings()
    
    async def verify_slack_request(self, request: Request) -> bool:
        """
        Verify that a request came from Slack.
        
        Args:
            request: FastAPI request object
            
        Returns:
            True if request is valid, False otherwise
        """
        slack_signing_secret = self.settings.slack_signing_secret
        
        # Get request headers
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        
        if not timestamp or not signature:
            logger.warning("Missing Slack verification headers")
            return False
        
        # Check timestamp freshness (within 5 minutes)
        if abs(time.time() - int(timestamp)) > 300:
            logger.warning("Request timestamp too old")
            return False
        
        # Get request body
        body = await request.body()
        
        # Create signature base string
        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        
        # Calculate expected signature
        my_signature = (
            "v0=" +
            hmac.new(
                slack_signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256
            ).hexdigest()
        )
        
        # Verify signature
        return hmac.compare_digest(my_signature, signature)
    
    async def parse_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Slack event payload.
        
        Args:
            payload: Raw event payload from Slack
            
        Returns:
            Parsed event data
        """
        event_type = payload.get("type")
        
        if event_type == "url_verification":
            # Challenge for Slack API verification
            return {"type": "challenge", "challenge": payload.get("challenge")}
        
        elif event_type == "event_callback":
            event = payload.get("event", {})
            return {
                "type": "message",
                "event": event,
                "user_id": event.get("user"),
                "channel_id": event.get("channel"),
                "text": event.get("text"),
                "thread_ts": event.get("thread_ts"),
                "timestamp": event.get("ts"),
            }
        
        return {"type": "unknown"}
