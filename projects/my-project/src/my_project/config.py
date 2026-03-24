from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "MyProject"
    API_KEY: str = None
    LOG_LEVEL: str = "INFO"

settings = Settings()
