from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    # App settings
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    APP_NAME: str = "Learnora Core Service"
    VERSION: str = "0.1.0"
    
    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite:///./learnora.db"
    DB_ECHO: bool = False
    
    # LangSmith
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = ""
    LANGSMITH_ENDPOINT: str = "https://eu.api.smith.langchain.com"
    
    # Google AI
    GOOGLE_API_KEY: str = ""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()