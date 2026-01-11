"""
Configuration management for Spaces API.
Loads and validates environment variables using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    
    # Rate Limiting
    rate_limit: int = 60
    
    # Caching
    cache_size: int = 100
    cache_ttl: int = 3600
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()
