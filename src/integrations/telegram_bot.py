"""
Telegram bot integration for Piddy.

Connects Piddy's agent engine to a Telegram chat via python-telegram-bot.
Mirrors the Slack integration: command routing → agent execution → response.

Requires: pip install python-telegram-bot
Token config: TELEGRAM_BOT_TOKEN in .env or key_manager
"""

import logging
import asyncio
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from telegram import Update  # type: ignore[import-unresolved]
    from telegram.ext import (  # type: ignore[import-unresolved]
        ApplicationBuilder,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )
    HAS_TELEGRAM = True
except ImportError:
    Update = None  # type: ignore[assignment,misc]
    ApplicationBuilder = None  # type: ignore[assignment,misc]
    CommandHandler = None  # type: ignore[assignment,misc]
    MessageHandler = None  # type: ignore[assignment,misc]
    ContextTypes = None  # type: ignore[assignment,misc]
    filters = None  # type: ignore[assignment,misc]
    HAS_TELEGRAM = False
    logger.info("python-telegram-bot not installed — install with: pip install python-telegram-bot")


# Reuse command keyword detection
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


class PiddyTelegramBot:
    """Telegram bot that routes messages through Piddy's agent engine."""

    def __init__(self, token: str):
        self.token = token
        self._agent: Any = None
        self._app: Any = None
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
        if not HAS_TELEGRAM:
            return {"success": False, "error": "python-telegram-bot not installed. Run: pip install python-telegram-bot"}

        if self._running:
            return {"success": False, "error": "Telegram bot is already running"}

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._running = True
        return {"success": True, "message": "Telegram bot started"}

    def stop(self) -> Dict[str, Any]:
        if not self._running or self._app is None:
            return {"success": False, "error": "Telegram bot is not running"}

        # Signal the polling loop to stop
        self._app.stop_running()
        self._running = False
        return {"success": True, "message": "Telegram bot stopped"}

    def status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "library_installed": HAS_TELEGRAM,
        }

    # -- internal ------------------------------------------------------------

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self._app = ApplicationBuilder().token(self.token).build()  # type: ignore[misc]
            self._app.add_handler(CommandHandler("start", self._cmd_start))  # type: ignore[misc]
            self._app.add_handler(CommandHandler("help", self._cmd_help))  # type: ignore[misc]
            self._app.add_handler(CommandHandler("scan", self._cmd_scan))  # type: ignore[misc]
            self._app.add_handler(CommandHandler("doctor", self._cmd_doctor))  # type: ignore[misc]
            self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message))  # type: ignore[misc]
            self._app.run_polling(close_loop=False)
        except Exception as exc:
            logger.error(f"Telegram bot error: {exc}")
            self._running = False

    # -- handlers ------------------------------------------------------------

    async def _cmd_start(self, update: Any, context: Any):
        await update.message.reply_text(
            "👋 Hi! I'm Piddy — your portable AI dev assistant.\n\n"
            "Just type a message or use:\n"
            "/scan — host diagnostics\n"
            "/doctor — health check\n"
            "/help — this menu"
        )

    async def _cmd_help(self, update: Any, context: Any):
        await update.message.reply_text(
            "🎯 Piddy Commands:\n"
            "/scan — Run host diagnostics\n"
            "/doctor — Health check\n\n"
            "Or type any coding request:\n"
            "• generate a REST API for users\n"
            "• review my code for security issues\n"
            "• debug this error: <paste>\n"
        )

    async def _cmd_scan(self, update: Any, context: Any):
        await update.message.reply_text("🔍 Running host scan…")
        try:
            from src.api.host_scanner import scan_host
            host = scan_host()
            os_info = host.get("os", {})
            hw = host.get("hardware", {})
            lines = [
                f"🖥 {os_info.get('platform')} {os_info.get('release', '')} ({os_info.get('arch')})",
                f"CPU: {hw.get('cpu_cores', '?')} cores",
                f"RAM: {hw.get('ram_gb', '?')} GB",
                f"Runtimes: {len(host.get('runtimes', {}))} detected",
                f"Tools: {len(host.get('installed_tools', []))} found",
            ]
            await update.message.reply_text("\n".join(lines))
        except Exception as exc:
            await update.message.reply_text(f"❌ Scan failed: {exc}")

    async def _cmd_doctor(self, update: Any, context: Any):
        await update.message.reply_text("🩺 Running diagnostics…")
        try:
            from src.api.doctor import run_diagnosis
            report = run_diagnosis()
            status = report.get("status", "unknown").upper()
            s = report.get("summary", {})
            await update.message.reply_text(
                f"Health: {status}\n"
                f"✅ {s.get('ok', 0)} OK · ⚠️ {s.get('warnings', 0)} Warn · ❌ {s.get('errors', 0)} Err"
            )
        except Exception as exc:
            await update.message.reply_text(f"❌ Doctor check failed: {exc}")

    async def _on_message(self, update: Any, context: Any):
        text = update.message.text
        if not text:
            return

        await update.message.reply_text("⏳ Processing…")

        try:
            response_text = await self._process(text)
        except Exception as exc:
            response_text = f"Error: {exc}"

        # Telegram message limit = 4096
        for chunk in _chunk_message(response_text, 4096):
            await update.message.reply_text(chunk)

    async def _process(self, text: str) -> str:
        try:
            from src.models.command import Command, CommandType

            cmd_type = CommandType.CODE_GENERATION if _is_command(text) else CommandType.CONVERSATION
            command = Command(
                description=text,
                command_type=cmd_type,
                source="telegram",
                metadata={},
            )
            response = await self.agent.process_command(command)
            return str(response.result) if response.result else "Done."
        except Exception as exc:
            logger.error(f"Telegram process error: {exc}", exc_info=True)
            return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _chunk_message(text: str, limit: int = 4096):
    while len(text) > limit:
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
_instance: Optional[PiddyTelegramBot] = None


def get_telegram_bot(token: Optional[str] = None) -> PiddyTelegramBot:
    global _instance
    if _instance is None:
        if token is None:
            from config.settings import get_settings
            token = get_settings().telegram_bot_token
        _instance = PiddyTelegramBot(token)
    return _instance
