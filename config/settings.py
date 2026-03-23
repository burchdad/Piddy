from pydantic_settings import BaseSettings
from functools import lru_cache
import logging


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Slack Configuration
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_app_token: str = ""

    # Discord Configuration
    discord_bot_token: str = ""

    # Telegram Configuration
    telegram_bot_token: str = ""

    # Google Calendar
    google_calendar_api_key: str = ""
    google_calendar_id: str = "primary"

    # Jira
    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""

    # Notion
    notion_api_token: str = ""
    
    # Anthropic API
    anthropic_api_key: str = ""
    
    # OpenAI API (Fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    agent_model: str = "claude-opus-4-1-20250805"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 4096
    
    # Local LLM (Ollama) - works completely offline
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_enabled: bool = True  # Auto-detected: tries Ollama if cloud LLMs fail
    local_only: bool = False  # When True, never call cloud APIs (Anthropic/OpenAI) — Ollama only
    
    # Database
    database_url: str = "sqlite:///./piddy.db"
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8001
    debug: bool = False
    
    # Backend URL for self-healing API calls (used when running on different servers)
    # Production: https://piddy-backend.railway.app
    # Development: http://localhost:8000
    backend_url: str = "http://localhost:8000"
    
    # Logging
    log_level: str = "INFO"
    
    # GitHub Configuration
    github_token: str = ""
    
    # Knowledge Base Configuration
    piddy_kb_repo_url: str = ""
    piddy_kb_repo_branch: str = "main"
    
    # Piddy Growth Configuration
    piddy_growth_repo_url: str = ""
    piddy_growth_secret: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Get cached settings instance, enriched with encrypted key store."""
    settings = Settings()
    # Bridge: if .env keys are empty, pull from encrypted key_manager
    try:
        from src.config.key_manager import get_all_keys
        stored = get_all_keys()
        if stored:
            if not settings.anthropic_api_key and stored.get("ANTHROPIC_API_KEY"):
                settings.anthropic_api_key = stored["ANTHROPIC_API_KEY"]
            if not settings.openai_api_key and stored.get("OPENAI_API_KEY"):
                settings.openai_api_key = stored["OPENAI_API_KEY"]
            if not settings.slack_bot_token and stored.get("SLACK_BOT_TOKEN"):
                settings.slack_bot_token = stored["SLACK_BOT_TOKEN"]
            if not settings.slack_signing_secret and stored.get("SLACK_SIGNING_SECRET"):
                settings.slack_signing_secret = stored["SLACK_SIGNING_SECRET"]
            if not settings.slack_app_token and stored.get("SLACK_APP_TOKEN"):
                settings.slack_app_token = stored["SLACK_APP_TOKEN"]
            if not settings.github_token and stored.get("GITHUB_TOKEN"):
                settings.github_token = stored["GITHUB_TOKEN"]
            if not settings.discord_bot_token and stored.get("DISCORD_BOT_TOKEN"):
                settings.discord_bot_token = stored["DISCORD_BOT_TOKEN"]
            if not settings.telegram_bot_token and stored.get("TELEGRAM_BOT_TOKEN"):
                settings.telegram_bot_token = stored["TELEGRAM_BOT_TOKEN"]
            if not settings.google_calendar_api_key and stored.get("GOOGLE_CALENDAR_API_KEY"):
                settings.google_calendar_api_key = stored["GOOGLE_CALENDAR_API_KEY"]
            if not settings.jira_base_url and stored.get("JIRA_BASE_URL"):
                settings.jira_base_url = stored["JIRA_BASE_URL"]
            if not settings.jira_email and stored.get("JIRA_EMAIL"):
                settings.jira_email = stored["JIRA_EMAIL"]
            if not settings.jira_api_token and stored.get("JIRA_API_TOKEN"):
                settings.jira_api_token = stored["JIRA_API_TOKEN"]
            if not settings.notion_api_token and stored.get("NOTION_API_TOKEN"):
                settings.notion_api_token = stored["NOTION_API_TOKEN"]
    except Exception:
        pass  # key_manager not available — use .env only
    return settings


# Setup logging
def setup_logging():
    """Configure application logging."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
