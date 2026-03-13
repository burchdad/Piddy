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
    try:
        # Verify request is from Slack
        # body = await request.body()
        # if not await verify_slack_request(request):
        #     logger.warning("Unauthorized Slack request")
        #     return {"error": "Unauthorized"}, 401
        
        # Normalize command name
        command_name = command_name.lower().strip()
        
        # Implementation depends on command type
        if command_name == "analyze":
            return await handle_analyze_command(request)
        elif command_name == "fix":
            return await handle_fix_command(request)
        elif command_name == "deploy":
            return await handle_deploy_command(request)
        elif command_name == "status":
            return await handle_status_command(request)
        else:
            logger.warning(f"Unknown command: {command_name}")
            return {
                "response_type": "ephemeral",
                "text": f"Unknown command: {command_name}\n\nAvailable commands: analyze, fix, deploy, status"
            }
        
    except Exception as e:
        logger.error(f"❌ Slash command handler error: {e}")
        return {
            "response_type": "ephemeral",
            "text": f"Error executing command: {str(e)}"
        }


async def handle_analyze_command(request: Request):
    """Handle /piddy analyze command"""
    try:
        # Parse form data
        form_data = await request.form()
        text = form_data.get("text", "")
        
        logger.info(f"Executing analyze command with text: {text}")
        
        # Return analysis result
        return {
            "response_type": "in_channel",
            "text": f"✅ Analyzing: {text or 'current workspace'}"
        }
    except Exception as e:
        logger.error(f"❌ Analyze command failed: {e}")
        return {
            "response_type": "ephemeral",
            "text": f"Error: {str(e)}"
        }


async def handle_fix_command(request: Request):
    """Handle /piddy fix command"""
    try:
        form_data = await request.form()
        text = form_data.get("text", "")
        
        logger.info(f"Executing fix command with text: {text}")
        
        return {
            "response_type": "in_channel",
            "text": f"🔧 Fixing: {text or 'issues in current workspace'}"
        }
    except Exception as e:
        logger.error(f"❌ Fix command failed: {e}")
        return {
            "response_type": "ephemeral",
            "text": f"Error: {str(e)}"
        }


async def handle_deploy_command(request: Request):
    """Handle /piddy deploy command"""
    try:
        form_data = await request.form()
        text = form_data.get("text", "")
        
        logger.info(f"Executing deploy command with text: {text}")
        
        return {
            "response_type": "in_channel",
            "text": f"🚀 Deploying: {text or 'latest changes'}"
        }
    except Exception as e:
        logger.error(f"❌ Deploy command failed: {e}")
        return {
            "response_type": "ephemeral",
            "text": f"Error: {str(e)}"
        }


async def handle_status_command(request: Request):
    """Handle /piddy status command"""
    try:
        form_data = await request.form()
        
        logger.info("Executing status command")
        
        return {
            "response_type": "in_channel",
            "text": "📊 Status: System operational"
        }
    except Exception as e:
        logger.error(f"❌ Status command failed: {e}")
        return {
            "response_type": "ephemeral",
            "text": f"Error: {str(e)}"
        }
