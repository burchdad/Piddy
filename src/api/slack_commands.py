"""Slack command endpoints."""

from fastapi import APIRouter, Request, HTTPException
import logging

from src.integrations.slack_events import SlackEventHandler
from src.integrations.slack import SlackIntegration


router = APIRouter(prefix="/slack", tags=["slack"])
event_handler = SlackEventHandler()
slack_client = SlackIntegration()

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
    
    # TODO: Process message event and send to agent
    # This will be handled by the message processing service
    
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
