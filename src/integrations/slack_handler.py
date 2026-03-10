"""Slack message processing and handling."""

import logging
import asyncio
import json
from typing import Dict, Any, Optional
from src.agent.core import BackendDeveloperAgent
from src.integrations.slack import SlackIntegration
from src.integrations.slack_conversation import get_conversation_manager
from src.models.command import Command, CommandType
from src.utils.memory import get_memory
from src.tools.git_manager import get_git_manager
from src.utils.error_handler import ErrorHandler, ErrorInfo
from src.services.response_storage import get_response_storage


logger = logging.getLogger(__name__)


class SlackMessageProcessor:
    """Process messages from Slack and interact with agent."""
    
    def __init__(self):
        """Initialize message processor."""
        self._agent = None  # Lazy initialization
        self.slack = SlackIntegration()
        self.conversation_manager = get_conversation_manager()
    
    @property
    def agent(self):
        """Get or initialize agent lazily."""
        if self._agent is None:
            self._agent = BackendDeveloperAgent()
        return self._agent
    
    async def process_message(self, event: Dict[str, Any]) -> None:
        """
        Process a message event from Slack.
        
        Args:
            event: Slack event data
        """
        try:
            user_id = event.get("user")
            channel_id = event.get("channel")
            text = event.get("text", "")
            thread_ts = event.get("thread_ts")
            ts = event.get("ts")
            
            if not text or not channel_id:
                logger.warning("Missing required message fields")
                return
            
            # Add thinking reaction to show we're processing
            await self.slack.add_reaction(channel_id, ts, "thinking_face")
            
            # Add message to conversation history
            self.conversation_manager.add_user_message(
                channel_id=channel_id,
                user_id=user_id,
                content=text,
                thread_ts=thread_ts
            )
            
            # Determine if this is a command or conversational message
            is_command = self._is_command(text)
            
            if is_command:
                # Handle as a command
                await self._handle_as_command(event, text, user_id, channel_id, thread_ts, ts)
            else:
                # Handle as conversational message
                await self._handle_as_conversation(event, text, user_id, channel_id, thread_ts, ts)
            
        except Exception as e:
            logger.error(f"Error processing Slack message: {str(e)}", exc_info=True)
            
            # Send error message
            await self.slack.send_message(
                channel=event.get("channel"),
                text=f"❌ Error processing your request: {str(e)}",
                thread_ts=event.get("thread_ts") or event.get("ts"),
            )
            
            # Add X reaction
            await self.slack.add_reaction(
                event.get("channel"),
                event.get("ts"),
                "x"
            )
    
    def _is_command(self, text: str) -> bool:
        """
        Determine if a message is a command or conversational.
        
        Commands typically start with action verbs or specific keywords.
        
        Args:
            text: Message text
            
        Returns:
            True if command, False if conversational
        """
        text_lower = text.lower().strip()
        
        # Command keywords
        command_keywords = [
            "generate", "create", "write", "code", "review", "analyze", "check",
            "audit", "design", "schema", "database", "model", "debug", "fix",
            "error", "issue", "secure", "security", "vulnerability", "docker",
            "kubernetes", "infra", "deploy", "document", "docs", "comment",
            "migrate", "migration", "commit", "push", "commit changes", "git status",
            "git", "status", "what's changed", "remember", "save context", "memory",
            "advanced review"
        ]
        
        return any(keyword in text_lower for keyword in command_keywords)
    
    async def _handle_as_command(
        self,
        event: Dict[str, Any],
        text: str,
        user_id: str,
        channel_id: str,
        thread_ts: Optional[str],
        ts: str
    ) -> None:
        """Handle message as a command."""
        # Send acknowledgment
        ack_text = "🔄 Processing your request..."
        await self.slack.send_message(
            channel=channel_id,
            text=ack_text,
            thread_ts=thread_ts or ts,
        )
        
        # Parse command from message
        command = self._parse_message_to_command(text, user_id, channel_id)
        
        # Handle Phase 2 commands
        phase2_command = command.metadata.get("phase2_command")
        if phase2_command == "git_commit":
            await self._handle_git_commit(channel_id, thread_ts or ts, user_id)
            return
        elif phase2_command == "git_status":
            await self._handle_git_status(channel_id, thread_ts or ts)
            return
        elif phase2_command == "save_memory":
            await self._handle_save_memory(channel_id, thread_ts or ts, text, user_id)
            return
        
        # Process with agent
        logger.info(f"Processing Slack command: {text[:50]}...")
        response = await self.agent.process_command(command)
        
        # Generate formatted response
        formatted_response = self._format_response(response)
        
        # Send response
        await self.slack.send_rich_message(
            channel=channel_id,
            blocks=formatted_response,
            thread_ts=thread_ts or ts,
        )
        
        # Add bot response to conversation history
        self.conversation_manager.add_bot_message(
            channel_id=channel_id,
            user_id=user_id,
            content=str(response.result),
            thread_ts=thread_ts,
            metadata={"command_type": response.command_type.value}
        )
        
        # Add checkmark reaction
        await self.slack.add_reaction(channel_id, ts, "white_check_mark")
        
        logger.info("Command processed successfully")
    
    async def _handle_as_conversation(
        self,
        event: Dict[str, Any],
        text: str,
        user_id: str,
        channel_id: str,
        thread_ts: Optional[str],
        ts: str
    ) -> None:
        """Handle message as conversational text."""
        try:
            # Get conversation history for context
            context_history = self.conversation_manager.get_context_history(
                channel_id=channel_id,
                user_id=user_id,
                thread_ts=thread_ts,
                limit=5  # Last 5 exchanges
            )
            
            # Create a conversational command
            prompt = f"{context_history}\n\nCurrent message: {text}"
            
            command = Command(
                command_type=CommandType.CUSTOM,
                description=prompt,
                context={
                    "source": "slack",
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "conversation_mode": True,
                    "conversation_history": context_history,
                },
                source="slack",
                priority=5,
                metadata={
                    "slack_user": user_id,
                    "slack_channel": channel_id,
                    "is_conversation": True,
                }
            )
            
            # Add thinking emoji
            await self.slack.add_reaction(channel_id, ts, "thought_balloon")
            
            logger.info(f"Processing Slack conversation: {text[:50]}...")
            response = await self.agent.process_command(command)
            
            # Format conversational response (more natural, less structured)
            formatted_response = self._format_conversational_response(response, text)
            
            # Send response
            await self.slack.send_rich_message(
                channel=channel_id,
                blocks=formatted_response,
                thread_ts=thread_ts or ts,
            )
            
            # Add bot response to conversation history
            self.conversation_manager.add_bot_message(
                channel_id=channel_id,
                user_id=user_id,
                content=str(response.result),
                thread_ts=thread_ts,
                metadata={"is_conversation": True}
            )
            
            # Clear thinking emoji and add smile
            await self.slack.add_reaction(channel_id, ts, "smile")
            
            logger.info("Conversation processed successfully")
            
        except Exception as e:
            logger.error(f"Error handling conversation: {str(e)}")
            await self.slack.send_message(
                channel=channel_id,
                text=f"Sorry, I had trouble understanding that. Could you clarify? (Error: {str(e)[:50]})",
                thread_ts=thread_ts or ts,
            )
            await self.slack.add_reaction(channel_id, ts, "confused")
    
    def _parse_message_to_command(
        self,
        text: str,
        user_id: str,
        channel_id: str
    ) -> Command:
        """
        Parse a Slack message into a command.
        
        Args:
            text: Message text
            user_id: Slack user ID
            channel_id: Slack channel ID
            
        Returns:
            Command object
        """
        # Remove bot mention if present
        text = text.replace("<@U", "@").strip()
        
        # Analyze message to determine command type
        text_lower = text.lower()
        
        # Phase 2: Detect advanced commands
        metadata = {
            "slack_user": user_id,
            "slack_channel": channel_id,
        }
        
        # Check for Phase 2 commands first
        if any(word in text_lower for word in ["commit", "push", "commit changes"]):
            metadata["phase2_command"] = "git_commit"
            command_type = CommandType.CUSTOM
        elif any(word in text_lower for word in ["git status", "what's changed", "status"]) and len(text_lower) < 20:
            metadata["phase2_command"] = "git_status"
            command_type = CommandType.CUSTOM
        elif any(word in text_lower for word in ["review this", "code review", "advanced review"]):
            metadata["phase2_command"] = "advanced_review"
            metadata["use_advanced_analyzer"] = True
            command_type = CommandType.CODE_REVIEW
        elif any(word in text_lower for word in ["remember", "save context", "memory"]):
            metadata["phase2_command"] = "save_memory"
            command_type = CommandType.CUSTOM
        # Standard command detection
        elif any(word in text_lower for word in ["generate", "create", "write", "code"]):
            command_type = CommandType.CODE_GENERATION
        elif any(word in text_lower for word in ["review", "analyze", "check", "audit"]):
            command_type = CommandType.CODE_REVIEW
        elif any(word in text_lower for word in ["design", "schema", "database", "model"]):
            command_type = CommandType.DATABASE_SCHEMA
        elif any(word in text_lower for word in ["debug", "fix", "error", "issue"]):
            command_type = CommandType.DEBUGGING
        elif any(word in text_lower for word in ["secure", "security", "vulnerability"]):
            command_type = CommandType.CODE_REVIEW
            metadata["use_advanced_analyzer"] = True
        elif any(word in text_lower for word in ["docker", "kubernetes", "infra", "deploy"]):
            command_type = CommandType.INFRASTRUCTURE
        elif any(word in text_lower for word in ["document", "docs", "comment"]):
            command_type = CommandType.DOCUMENTATION
        elif any(word in text_lower for word in ["migrate", "migration"]):
            command_type = CommandType.MIGRATION
        else:
            command_type = CommandType.CUSTOM
        
        return Command(
            command_type=command_type,
            description=text,
            context={
                "source": "slack",
                "user_id": user_id,
                "channel_id": channel_id,
            },
            source="slack",
            priority=5,
            metadata=metadata
        )
    
    def _format_conversational_response(self, response, user_message: str) -> list:
        """
        Format agent response for conversational mode (more natural).
        
        Args:
            response: Command response from agent
            user_message: Original user message
            
        Returns:
            List of Slack blocks for conversational format
        """
        blocks = []
        
        if response.success:
            result_text = str(response.result).strip()
            
            # For conversations, keep it simple and natural
            # Just show the content without command type header
            if len(result_text) > 3000:
                # Split long responses
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": result_text[:2800]
                    }
                })
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "_(Response truncated - use full API for complete output)_"
                        }
                    ]
                })
            else:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": result_text
                    }
                })
        else:
            # Error response - still conversational
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Sorry, I ran into an issue: {response.error}"
                }
            })
        
        return blocks
    
    def _format_response(self, response) -> list:
        """
        Format agent response into Slack block kit format.
        
        Args:
            response: Command response from agent
            
        Returns:
            List of Slack blocks
        """
        blocks = []
        
        # Header block
        status_emoji = "✅" if response.success else "❌"
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{status_emoji} {response.command_type.value.replace('_', ' ').title()}",
                "emoji": True
            }
        })
        
        # Divider
        blocks.append({
            "type": "divider"
        })
        
        # Main content
        if response.success:
            result_text = str(response.result)
            
            # If response is too long, store it and provide a link
            if len(result_text) > 2000:
                storage = get_response_storage()
                metadata = {
                    "command_type": response.command_type.value,
                    "switched_to_fallback": response.metadata.get("switched_to_fallback", False)
                }
                response_id = storage.store_response(result_text, metadata)
                
                # Show preview and link
                preview = result_text[:800]
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```\n{preview}\n```"
                    }
                })
                
                # Add link button to full response
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📄 *Output truncated ({len(result_text)} characters)* - <get_config().localhost:8000{response_id}|View Full Response>"
                    }
                })
            else:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```\n{result_text}\n```"
                    }
                })
        else:
            # Error message
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:* {response.error}"
                }
            })
        
        # Footer with metadata
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📊 Execution time: {response.execution_time:.2f}s | 🔧 Command type: {response.command_type.value}"
                }
            ]
        })
        
        return blocks
    
    # Phase 2: Git Integration Handlers
    async def _handle_git_status(self, channel_id: str, ts: str) -> None:
        """Handle git status command."""
        try:
            git = get_git_manager()
            if git is None:
                await self.slack.send_message(
                    channel=channel_id,
                    text="❌ Git not available in this repository",
                    thread_ts=ts
                )
                return
            
            status = git.get_status()
            
            if not status["success"]:
                await self.slack.send_message(
                    channel=channel_id,
                    text=f"❌ Error: {status.get('error')}",
                    thread_ts=ts
                )
                return
            
            # Format status for Slack
            message = f"📊 Git Status - Branch: `{status['branch']}`\n\n"
            
            if status.get("staged"):
                message += f"✅ Staged: `{len(status['staged'])}` file(s)\n"
            if status.get("unstaged"):
                message += f"📝 Unstaged: `{len(status['unstaged'])}` file(s)\n"
            if status.get("untracked"):
                message += f"❓ Untracked: `{len(status['untracked'])}` file(s)\n"
            
            if not status.get("has_changes"):
                message += "\n✨ No changes to commit"
            
            await self.slack.send_message(
                channel=channel_id,
                text=message,
                thread_ts=ts
            )
        except Exception as e:
            logger.error(f"Error handling git status: {e}")
            await self.slack.send_message(
                channel=channel_id,
                text=f"❌ Error: {str(e)}",
                thread_ts=ts
            )
    
    async def _handle_git_commit(self, channel_id: str, ts: str, user_id: str) -> None:
        """Handle git commit command."""
        try:
            git = get_git_manager()
            if git is None:
                await self.slack.send_message(
                    channel=channel_id,
                    text="❌ Git not available in this repository",
                    thread_ts=ts
                )
                return
            
            # Get current status
            status = git.get_status()
            if not status.get("has_changes"):
                await self.slack.send_message(
                    channel=channel_id,
                    text="✨ No changes to commit",
                    thread_ts=ts
                )
                return
            
            # Create commit
            message = f"Generated by Piddy from Slack user {user_id}"
            result = git.commit(message=message, auto_stage=True)
            
            if result["success"]:
                await self.slack.send_message(
                    channel=channel_id,
                    text=f"✅ {result['message']}\n🔗 Commit: `{result['short_hash']}`",
                    thread_ts=ts
                )
            else:
                await self.slack.send_message(
                    channel=channel_id,
                    text=f"❌ Commit failed: {result.get('error')}",
                    thread_ts=ts
                )
        except Exception as e:
            logger.error(f"Error handling git commit: {e}")
            await self.slack.send_message(
                channel=channel_id,
                text=f"❌ Error: {str(e)}",
                thread_ts=ts
            )
    
    async def _handle_save_memory(self, channel_id: str, ts: str, text: str, user_id: str) -> None:
        """Handle save memory command."""
        try:
            memory = get_memory()
            
            # Create conversation context
            success = memory.create_conversation(
                conversation_id=f"slack_{channel_id}_{ts}",
                user_id=user_id,
                channel_id=channel_id,
                project_context="Slack Integration",
                title=text[:50]
            )
            
            if success:
                await self.slack.send_message(
                    channel=channel_id,
                    text="✅ Conversation context saved for future reference",
                    thread_ts=ts
                )
            else:
                await self.slack.send_message(
                    channel=channel_id,
                    text="⚠️ Context already exists",
                    thread_ts=ts
                )
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            await self.slack.send_message(
                channel=channel_id,
                text=f"❌ Error: {str(e)}",
                thread_ts=ts
            )
    
    async def process_app_mention(self, event: Dict[str, Any]) -> None:
        """
        Process app mention event.
        
        Args:
            event: Slack event data
        """
        # Extract the actual message text (without the mention)
        text = event.get("text", "")
        
        # Remove the bot mention from the beginning
        if text.startswith("<@"):
            # Find the end of the mention
            mention_end = text.find(">")
            if mention_end != -1:
                text = text[mention_end + 1:].strip()
        
        # Process as normal message
        await self.process_message({
            **event,
            "text": text
        })
    
    async def process_direct_message(self, event: Dict[str, Any]) -> None:
        """
        Process direct message event.
        
        Args:
            event: Slack event data
        """
        # Direct messages are processed the same way as channel messages
        await self.process_message(event)


class SlackMessageListener:
    """Listen for Slack events and process messages."""
    
    def __init__(self):
        """Initialize listener."""
        self.processor = SlackMessageProcessor()
        logger.info("SlackMessageListener initialized")
    
    async def handle_event(self, event: Dict[str, Any]) -> None:
        """
        Handle an incoming Slack event.
        
        Args:
            event: Slack event payload
        """
        event_type = event.get("type")
        
        if event_type == "message":
            # Check if it's a bot message or thread reply we should skip
            if event.get("bot_id") or event.get("subtype"):
                return
            
            # Handle message events
            await self.processor.process_message(event)
        
        elif event_type == "app_mention":
            # Handle mentions
            await self.processor.process_app_mention(event)
        
        else:
            logger.debug(f"Unhandled event type: {event_type}")
