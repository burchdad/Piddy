"""
Discord bot integration for Piddy.

Connects Piddy's agent engine to a Discord server via the discord.py library.
Mirrors the Slack integration: command routing → agent execution → response.

Requires: pip install discord.py
Token config: DISCORD_BOT_TOKEN in .env or key_manager
"""

import logging
import asyncio
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Lazy-load discord.py (only needed when bot is started)
try:
    import discord  # type: ignore[import-unresolved]
    from discord import Intents  # type: ignore[import-unresolved]
    HAS_DISCORD = True
except ImportError:
    discord = None  # type: ignore[assignment]
    Intents = None  # type: ignore[assignment]
    HAS_DISCORD = False
    logger.info("discord.py not installed — install with: pip install discord.py")


# ---------------------------------------------------------------------------
# Shared command detection (reused from Slack integration pattern)
# ---------------------------------------------------------------------------
COMMAND_KEYWORDS = [
    "generate", "create", "write", "code", "review", "analyze", "check",
    "audit", "design", "schema", "database", "model", "debug", "fix",
    "error", "issue", "secure", "security", "vulnerability", "docker",
    "kubernetes", "infra", "deploy", "document", "docs", "comment",
    "migrate", "migration", "commit", "push", "git", "status",
    "remember", "save context", "memory", "self",
]


def _is_command(text: str) -> bool:
    text_lower = text.lower().strip()
    return any(kw in text_lower for kw in COMMAND_KEYWORDS)


# ---------------------------------------------------------------------------
# Discord Bot Client
# ---------------------------------------------------------------------------
class PiddyDiscordBot:
    """Discord bot that routes messages through Piddy's agent engine."""

    def __init__(self, token: str):
        self.token = token
        self._agent: Any = None
        self._client: Any = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def agent(self):
        if self._agent is None:
            from src.agent.core import BackendDeveloperAgent
            self._agent = BackendDeveloperAgent()
        return self._agent

    # -- lifecycle -----------------------------------------------------------

    def start(self) -> Dict[str, Any]:
        """Start the Discord bot in a background thread."""
        if not HAS_DISCORD:
            return {"success": False, "error": "discord.py not installed. Run: pip install discord.py"}

        if self._running:
            return {"success": False, "error": "Discord bot is already running"}

        intents = Intents.default()  # type: ignore[union-attr]
        intents.message_content = True

        self._client = discord.Client(intents=intents)  # type: ignore[union-attr]
        self._register_events()

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._running = True
        return {"success": True, "message": "Discord bot started"}

    def stop(self) -> Dict[str, Any]:
        """Stop the Discord bot."""
        if not self._running or self._client is None:
            return {"success": False, "error": "Discord bot is not running"}

        asyncio.run_coroutine_threadsafe(self._client.close(), self._client.loop)
        self._running = False
        return {"success": True, "message": "Discord bot stopped"}

    def status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "library_installed": HAS_DISCORD,
            "connected": self._client is not None and self._client.is_ready() if self._running else False,
            "guilds": len(self._client.guilds) if self._running and self._client and self._client.is_ready() else 0,
        }

    # -- internal ------------------------------------------------------------

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._client.start(self.token))
        except Exception as exc:
            logger.error(f"Discord bot error: {exc}")
            self._running = False

    def _register_events(self):
        client = self._client

        @client.event
        async def on_ready():
            logger.info(f"Discord bot connected as {client.user} in {len(client.guilds)} guild(s)")

        @client.event
        async def on_message(message):
            # Skip own messages
            if message.author == client.user:
                return

            # Only respond to DMs or when mentioned
            is_dm = isinstance(message.channel, discord.DMChannel)  # type: ignore[union-attr]
            mentioned = client.user in message.mentions if message.mentions else False
            if not is_dm and not mentioned:
                return

            text = message.content
            # Strip mention prefix if present
            if mentioned and client.user:
                text = text.replace(f"<@{client.user.id}>", "").strip()

            if not text:
                return

            # Show typing indicator while processing
            async with message.channel.typing():
                response_text = await self._process(text)

            # Discord message limit = 2000
            for chunk in _chunk_message(response_text, 2000):
                await message.reply(chunk)

    async def _process(self, text: str) -> str:
        """Route text through agent and return response string."""
        try:
            from src.models.command import Command, CommandType

            if _is_command(text):
                command = Command(
                    description=text,
                    command_type=CommandType.CODE_GENERATION,
                    source="discord",
                    metadata={},
                )
                response = await self.agent.process_command(command)
                return str(response.result) if response.result else "Done."
            else:
                # Conversational fallback
                command = Command(
                    description=text,
                    command_type=CommandType.CONVERSATION,
                    source="discord",
                    metadata={},
                )
                response = await self.agent.process_command(command)
                return str(response.result) if response.result else "I'm here! How can I help?"
        except Exception as exc:
            logger.error(f"Discord process error: {exc}", exc_info=True)
            return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Telegram Bot
# ---------------------------------------------------------------------------
# (kept separate from discord module — see telegram_bot.py)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _chunk_message(text: str, limit: int = 2000):
    """Split a long message into chunks respecting the platform limit."""
    while len(text) > limit:
        # Try to split on newline
        idx = text.rfind("\n", 0, limit)
        if idx == -1:
            idx = limit
        yield text[:idx]
        text = text[idx:].lstrip("\n")
    if text:
        yield text


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------
_instance: Optional[PiddyDiscordBot] = None


def get_discord_bot(token: Optional[str] = None) -> PiddyDiscordBot:
    """Get or create the Discord bot singleton."""
    global _instance
    if _instance is None:
        if token is None:
            from config.settings import get_settings
            token = get_settings().discord_bot_token
        _instance = PiddyDiscordBot(token)
    return _instance
