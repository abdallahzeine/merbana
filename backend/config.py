"""
backend/config.py
=================
Configuration management using Pydantic Settings.

Provides centralized configuration for the Merbana backend including
app metadata, server settings, database configuration, and CORS origins.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

from .paths import is_packaged


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are automatically loaded with the APP_ prefix.
    Example: APP_PORT=8080 will set port=8080
    """

    # App metadata
    app_name: str = Field(default="Merbana", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")

    # Server configuration
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8741, description="Server port")

    # Database configuration
    database_filename: str = Field(
        default="merbana.db", description="SQLite database filename"
    )

    # CORS origins
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:5173",
            "http://localhost:8741",
            "http://127.0.0.1:8741",
        ],
        description="Allowed CORS origins",
    )

    # Environment
    @property
    def is_packaged(self) -> bool:
        """Check if running in packaged (PyInstaller) mode."""
        return is_packaged()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return not self.is_packaged

    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Settings are cached to avoid repeated environment variable lookups.
    """
    return Settings()
