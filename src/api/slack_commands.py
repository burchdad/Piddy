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
message_listener = SlackMessageListener()

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
        asyncio.create_task(message_listener.handle_event(event))
    
    return {"ok": True}


@router.post("/commands/{command_name}")
async def handle_slash_command(command_name: str, request: Request):
    """
    Handle Slack slash commands.
    
    Args:
        command_name: Name of the slash command
        request: Request data
    """
    # TODO: Implement slash command handling
    return {"response_type": "in_channel", "text": f"Command {command_name} received"}
