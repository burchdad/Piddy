from pydantic_settings import BaseSettings
from functools import lru_cache
import logging


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Slack Configuration
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_app_token: str = ""
    
    # Anthropic API
    anthropic_api_key: str = ""
    
    # OpenAI API (Fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    agent_model: str = "claude-opus-4-1-20250805"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 4096
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Get cached settings instance."""
    return Settings()


# Setup logging
def setup_logging():
    """Configure application logging."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
