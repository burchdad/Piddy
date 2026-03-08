"""Slack command endpoints."""

from fastapi import APIRouter, Request, HTTPException
import logging
import asyncio

from src.integrations.slack_events import SlackEventHandler
from src.integrations.slack import SlackIntegration
from src.integrations.slack_handler import SlackMessageListener


router = APIRouter(prefix="/slack", tags=["slack"])
event_handler = SlackEventHandler()
slack_client = SlackIntegration()

# Lazy initialize message listener (avoid hanging on import)
_message_listener = None

def get_message_listener():
    """Get or create message listener lazily."""
    global _message_listener
    if _message_listener is None:
        _message_listener = SlackMessageListener()
    return _message_listener

logger = logging.getLogger(__name__)


@router.post("/events")
async def handle_slack_events(request: Request):
    """
    Handle incoming Slack events.
    
    This endpoint receives all Slack events including messages, mentions, etc.
    """
    # Verify the request came from Slack
    if not await event_handler.verify_slack_request(request):
        raise HTTPException(status_code=401, detail="Invalid request signature")
    
    # Get request body
    payload = await request.json()
    
    # Parse event
    event = await event_handler.parse_event(payload)
    
    # Handle challenge for URL verification
    if event.get("type") == "challenge":
        return {"challenge": event.get("challenge")}
    
    # Log event
    logger.info(f"Slack event received: {event.get('type')}")
    
    # Process message event
    if event.get("type") == "message":
        # Process asynchronously to avoid timeout
        asyncio.create_task(get_message_listener().handle_event(event))
    
    return {"ok": True}


@router.post("/commands/{command_name}")
async def handle_slash_command(command_name: str, request: Request):
    """
    Handle Slack slash commands.
    
    Args:
        command_name: Name of the slash command
        request: Request data
    """
    # TODO (2026-03-08): Implement slash command handling
    return {"response_type": "in_channel", "text": f"Command {command_name} received"}
