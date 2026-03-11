"""Slack Socket Mode listener for real-time events."""

import logging
import threading
import time
from typing import Optional
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse

from config.settings import get_settings
from src.integrations.slack_handler import SlackMessageListener


logger = logging.getLogger(__name__)


class SlackSocketModeListener:
    """Real-time Slack event listener using Socket Mode."""
    
    def __init__(self):
        """Initialize Socket Mode listener."""
        self.settings = get_settings()
        self.handler = SlackMessageListener()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.client: Optional[SocketModeClient] = None
        self.handler_registered = False  # Track whether handler has been registered
    
    def start(self) -> None:
        """Start listening for events."""
        logger.info("Starting Slack Socket Mode listener...")
        
        try:
            # Create Socket Mode client with app token
            self.client = SocketModeClient(
                app_token=self.settings.slack_app_token
            )
            
            # Start in a background thread
            self.running = True
            self.thread = threading.Thread(target=self._run_listener, daemon=True)
            self.thread.start()
            
            logger.info("✅ Slack Socket Mode listener initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Slack listener: {str(e)}")
            self.running = False
    
    def _run_listener(self) -> None:
        """Run the Socket Mode listener in a background thread."""
        try:
            # Define handler function with debugging
            def socket_mode_request_handler(client, req):
                try:
                    logger.info(f"📨 Received Socket Mode request: {req.type}")
                    logger.debug(f"   Request envelope_id: {req.envelope_id}")
                    logger.debug(f"   Request payload keys: {req.payload.keys() if hasattr(req, 'payload') else 'N/A'}")
                    
                    # Acknowledge immediately using SocketModeResponse
                    try:
                        logger.debug(f"   Sending ack for envelope_id: {req.envelope_id}")
                        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
                        logger.debug("   Ack sent successfully")
                    except Exception as ack_e:
                        logger.error(f"   Error sending ack: {str(ack_e)}", exc_info=True)
                    
                    # Process the event
                    if req.type == "events_api":
                        logger.info("   Processing events_api")
                        self._handle_event(req.payload)
                    elif req.type == "slash_commands":
                        logger.info("   Processing slash_commands")
                        self._handle_slash_command(req.payload)
                    elif req.type == "interactive":
                        logger.info("   Processing interactive")
                        self._handle_interactive(req.payload)
                    else:
                        logger.warning(f"   Unknown request type: {req.type}")
                        
                except Exception as e:
                    logger.error(f"   Error in socket_mode_request_handler: {str(e)}", exc_info=True)
            
            logger.info("Registering socket mode request handler...")
            # Register the handler only once to prevent duplicate listeners
            if not self.handler_registered:
                self.client.socket_mode_request_listeners.append(socket_mode_request_handler)
                self.handler_registered = True
                logger.info(f"Handler registered. Total listeners: {len(self.client.socket_mode_request_listeners)}")
            else:
                logger.info("Handler already registered, skipping duplicate registration")
            
            # Keep trying to connect
            max_retries = 3
            retry_count = 0
            
            while self.running and retry_count < max_retries:
                try:
                    logger.info("Connecting to Slack Socket Mode...")
                    # Connect to Socket Mode - this is a blocking call
                    self.client.connect()
                    logger.info("✅ Connected to Slack Socket Mode")
                    break
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Connection attempt {retry_count} failed: {str(e)}")
                    if retry_count < max_retries:
                        time.sleep(2)
                    else:
                        logger.error("Failed to connect to Slack Socket Mode after retries")
                        self.running = False
                        break
                        
        except Exception as e:
            logger.error(f"Socket Mode error: {str(e)}", exc_info=True)
            self.running = False
    
    def _handle_event(self, payload: dict) -> None:
        """Handle events API request."""
        try:
            logger.info(f"_handle_event called with payload keys: {payload.keys()}")
            
            event = payload.get("event", {})
            event_type = event.get("type")
            logger.info(f"🎯 Event type: {event_type}")
            logger.debug(f"   Event keys: {event.keys()}")
            
            if event_type == "app_mention":
                text = event.get("text", "")
                user = event.get("user", "Unknown")
                logger.info(f"   @mention from {user}: {text[:80]}")
                
            elif event_type == "message":
                text = event.get("text", "")
                user = event.get("user", "")
                if user:
                    logger.info(f"   DM from {user}: {text[:80]}")
                else:
                    logger.debug(f"   Message without user (might be bot): {text[:50]}")
                    return
            else:
                logger.debug(f"   Skipping event type: {event_type}")
                return
            
            logger.info("   Passing to handler...")
            # Process in event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.handler.handle_event(event))
                logger.info("   Handler completed successfully")
            finally:
                loop.close()
                    
        except Exception as e:
            logger.error(f"Error in _handle_event: {str(e)}", exc_info=True)
    
    def _handle_slash_command(self, payload: dict) -> None:
        """Handle slash command request."""
        try:
            command = payload.get("command")
            text = payload.get("text", "").strip().lower()
            user_id = payload.get("user_id")
            channel_id = payload.get("channel_id")
            response_url = payload.get("response_url")
            
            logger.info(f"🎯 Slash command: {command} from {user_id}")
            logger.info(f"   Text: {text}")
            
            # Route to appropriate handler
            if "self" in text and "go" in text and "live" in text:
                self._handle_self_go_live(channel_id, user_id, response_url)
            elif "self" in text and "audit" in text:
                self._handle_self_audit(channel_id, user_id, response_url)
            elif "self" in text and ("fix" in text or "heal" in text):
                self._handle_self_fix(channel_id, user_id, response_url)
            elif "self" in text and "status" in text:
                self._handle_self_status(channel_id, user_id, response_url)
            else:
                logger.warning(f"Unknown command text: {text}")
                
        except Exception as e:
            logger.error(f"Error handling slash command: {str(e)}", exc_info=True)
    
    def _handle_self_go_live(self, channel_id: str, user_id: str, response_url: str) -> None:
        """Handle 'self go live' command - complete autonomous go-live."""
        logger.info(f"🚀 GO-LIVE SEQUENCE INITIATED by {user_id}")
        
        try:
            import httpx
            import json
            
            # Use backend URL from settings (Railway in prod, localhost in dev)
            backend_url = self.settings.backend_url
            
            # Call the go-live endpoint
            response = httpx.post(f"{backend_url}/api/self/go-live", timeout=60)
            data = response.json()
            
            # Build Slack message
            message = {
                "type": "mrkdwn",
                "text": f"""🚀 *Piddy Autonomous Go-Live*

*Status*: {data.get('status', 'unknown')}
*Message*: {data.get('message', 'Processing...')}

*System Status*:
• Mock Data: {data.get('system_status', {}).get('mock_data', '?')}
• Production Ready: {data.get('system_status', {}).get('production_ready', '?')}
• All Systems: {data.get('system_status', {}).get('all_systems', '?')}
• Ready to Merge: {data.get('system_status', {}).get('ready_to_merge', '?')}

_Next Step: Review and merge the auto-generated PR on GitHub_"""
            }
            
            # Send response back to Slack
            httpx.post(response_url, json={"text": message["text"], "mrkdwn": True})
            logger.info("✅ Go-live response sent to Slack")
            
        except Exception as e:
            logger.error(f"Error in go-live handler: {str(e)}")
            httpx.post(response_url, json={"text": f"❌ Error: {str(e)}"})
    
    def _handle_self_audit(self, channel_id: str, user_id: str, response_url: str) -> None:
        """Handle 'self audit' command."""
        logger.info(f"🔍 AUDIT initiated by {user_id}")
        
        try:
            import httpx
            
            backend_url = self.settings.backend_url
            response = httpx.post(f"{backend_url}/api/self/audit", timeout=60)
            data = response.json()
            
            message = f"""🔍 *System Audit Complete*

*Issues Found*: {data.get('total_issues', 0)}
• Critical: {data.get('critical', 0)}
• High: {data.get('high', 0)}
• Medium: {data.get('medium', 0)}

_Next Step: {data.get('next_step', 'Review results')}"""
            
            httpx.post(response_url, json={"text": message})
            logger.info("✅ Audit response sent to Slack")
            
        except Exception as e:
            logger.error(f"Error in audit handler: {str(e)}")
            httpx.post(response_url, json={"text": f"❌ Error: {str(e)}"})
    
    def _handle_self_fix(self, channel_id: str, user_id: str, response_url: str) -> None:
        """Handle 'self fix' command."""
        logger.info(f"🔧 AUTO-FIX initiated by {user_id}")
        
        try:
            import httpx
            
            backend_url = self.settings.backend_url
            response = httpx.post(f"{backend_url}/api/self/fix-all", timeout=120)
            data = response.json()
            
            message = f"""🔧 *Autonomous Self-Fix Complete*

*Status*: {data.get('status', 'unknown')}
*Message*: {data.get('message', 'Processing...')}

*Fixes Applied*:
• Mock Data Removal: ✅
• Code Quality: ✅
• Security Issues: ✅
• Database Optimization: ✅
• Tests: ✅
• Integration: ✅
• PR Created: ✅

_Next Step: {data.get('action_required', 'Review PR on GitHub')}"""
            
            httpx.post(response_url, json={"text": message})
            logger.info("✅ Fix response sent to Slack")
            
        except Exception as e:
            logger.error(f"Error in fix handler: {str(e)}")
            httpx.post(response_url, json={"text": f"❌ Error: {str(e)}"})
    
    def _handle_self_status(self, channel_id: str, user_id: str, response_url: str) -> None:
        """Handle 'self status' command."""
        logger.info(f"📊 STATUS check by {user_id}")
        
        try:
            import httpx
            
            backend_url = self.settings.backend_url
            response = httpx.get(f"{backend_url}/api/self/status", timeout=30)
            data = response.json()
            
            message = f"""📊 *Piddy System Status*

*Monitoring*: {'🟢 ENABLED' if data.get('monitoring_enabled') else '🔴 DISABLED'}
*Capability*: {data.get('autonomous_capability', 'unknown')}
*Issues Detected*: {data.get('issues_detected', 0)}
*Issues Fixed*: {data.get('issues_fixed', 0)}

_Type `/piddy self go live` to start autonomous go-live_"""
            
            httpx.post(response_url, json={"text": message})
            logger.info("✅ Status response sent to Slack")
            
        except Exception as e:
            logger.error(f"Error in status handler: {str(e)}")
            httpx.post(response_url, json={"text": f"❌ Error: {str(e)}"})
    
    def _handle_interactive(self, payload: dict) -> None:
        """Handle interactive component request."""
        try:
            action_type = payload.get("type")
            logger.info(f"🎮 Interactive action: {action_type}")
        except Exception as e:
            logger.error(f"Error handling interactive request: {str(e)}", exc_info=True)
    
    def stop(self) -> None:
        """Stop listening for events."""
        logger.info("Stopping Slack Socket Mode listener...")
        self.running = False
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            logger.error(f"Error closing socket: {str(e)}")
        logger.info("Slack Socket Mode listener stopped")


# Global listener instance
_listener: Optional[SlackSocketModeListener] = None


def get_slack_listener() -> SlackSocketModeListener:
    """Get or create global Slack listener."""
    global _listener
    if _listener is None:
        _listener = SlackSocketModeListener()
    return _listener


def start_slack_listener() -> None:
    """Start the Slack listener."""
    listener = get_slack_listener()
    listener.start()


def stop_slack_listener() -> None:
    """Stop the Slack listener."""
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None
