"""Configuration management for MCP server."""

import os
from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Server configuration
    host: str = Field(default="127.0.0.1", env="MCP_SERVER_HOST")
    port: int = Field(default=8000, env="MCP_SERVER_PORT")
    
    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Development configuration
    dev_mode: bool = Field(default=False, env="DEV_MODE")
    auto_reload: bool = Field(default=True, env="AUTO_RELOAD")
    
    # Security (optional)
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    secret_key: Optional[str] = Field(default=None, env="SECRET_KEY")
    
    # External services (optional)
    external_api_url: Optional[str] = Field(default=None, env="EXTERNAL_API_URL")
    external_api_key: Optional[str] = Field(default=None, env="EXTERNAL_API_KEY")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()