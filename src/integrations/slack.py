"""Slack integration for Piddy."""

import logging
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, Optional

from config.settings import get_settings


logger = logging.getLogger(__name__)


class SlackIntegration:
    """Handle Slack communication for Piddy."""
    
    def __init__(self):
        """Initialize Slack integration."""
        self.settings = get_settings()
        self.client = WebClient(token=self.settings.slack_bot_token)
        self.signing_secret = self.settings.slack_signing_secret
        logger.info("Slack Integration initialized")
    
    async def send_message(
        self, 
        channel: str, 
        text: str,
        thread_ts: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a message to a Slack channel.
        
        Args:
            channel: Target channel ID or name
            text: Message text
            thread_ts: Optional thread timestamp for threaded messages
            metadata: Optional metadata to include
            
        Returns:
            Success status
        """
        try:
            self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
                metadata=metadata,
            )
            logger.info(f"Message sent to {channel}")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")
            return False
    
    async def send_rich_message(
        self,
        channel: str,
        blocks: list,
        thread_ts: Optional[str] = None
    ) -> bool:
        """
        Send a rich formatted message using blocks.
        
        Args:
            channel: Target channel ID or name
            blocks: List of block kit blocks
            thread_ts: Optional thread timestamp
            
        Returns:
            Success status
        """
        try:
            self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                thread_ts=thread_ts,
            )
            logger.info(f"Rich message sent to {channel}")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending rich message: {e.response['error']}")
            return False
    
    async def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
        blocks: Optional[list] = None
    ) -> bool:
        """
        Update an existing message.
        
        Args:
            channel: Channel containing the message
            ts: Message timestamp
            text: Updated text
            blocks: Optional updated blocks
            
        Returns:
            Success status
        """
        try:
            self.client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
                blocks=blocks,
            )
            logger.info(f"Message updated in {channel}")
            return True
        except SlackApiError as e:
            logger.error(f"Error updating message: {e.response['error']}")
            return False
    
    async def add_reaction(self, channel: str, ts: str, emoji: str) -> bool:
        """
        Add an emoji reaction to a message.
        
        Args:
            channel: Channel containing the message
            ts: Message timestamp
            emoji: Emoji name (without colons)
            
        Returns:
            Success status
        """
        try:
            self.client.reactions_add(
                channel=channel,
                timestamp=ts,
                name=emoji,
            )
            return True
        except SlackApiError as e:
            logger.error(f"Error adding reaction: {e.response['error']}")
            return False
