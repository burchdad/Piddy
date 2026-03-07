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
    
    # Agent Configuration
    agent_model: str = "claude-opus-4-1-20250805"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 4096
    
    # Database
    database_url: str = "sqlite:///./piddy.db"
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8001
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    
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
