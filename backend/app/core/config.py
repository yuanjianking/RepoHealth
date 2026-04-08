"""
Configuration management for RepoHealth backend.

Uses pydantic-settings to load configuration from environment variables and .env file.
"""

import sys
from pathlib import Path
from typing import List, Optional

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    Environment variables take precedence over .env file.
    All field names are case-insensitive for environment variables.
    """

    # Application settings
    app_env: str = Field("development", env="APP_ENV", description="Application environment")
    app_debug: bool = Field(True, env="APP_DEBUG", description="Debug mode")
    app_host: str = Field("0.0.0.0", env="APP_HOST", description="Host to bind to")
    app_port: int = Field(8000, env="APP_PORT", description="Port to listen on")
    app_cors_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:5173"],
        env="APP_CORS_ORIGINS",
        description="Allowed CORS origins",
    )

    # Data storage settings
    data_path: Path = Field(Path("./data"), env="DATA_PATH", description="Root data directory")

    # AI integration settings (DeepSeek)
    deepseek_api_key: Optional[str] = Field(None, env="DEEPSEEK_API_KEY", description="DeepSeek API key")
    deepseek_api_base: str = Field("https://api.deepseek.com", env="DEEPSEEK_API_BASE", description="DeepSeek API base URL")
    deepseek_model: str = Field("deepseek-chat", env="DEEPSEEK_MODEL", description="DeepSeek model name")

    # Derived paths
    @property
    def dashboard_data_root(self) -> Path:
        """Get the dashboard data directory path."""
        return self.data_path / "dashboard"

    @field_validator("data_path", mode="before")
    @classmethod
    def validate_data_path(cls, v: str | Path) -> Path:
        """Convert string to Path and ensure it's absolute relative to project root."""
        if isinstance(v, str):
            v = Path(v)

        # If path is relative, make it absolute relative to project root
        if not v.is_absolute():
            # Assuming config is in backend/app/core/
            project_root = Path(__file__).resolve().parents[2]  # backend directory
            v = (project_root / v).resolve()

        return v

    @field_validator("app_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.

    This function follows the singleton pattern to avoid loading settings
    multiple times.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        # Ensure data directory exists
        _settings.dashboard_data_root.mkdir(parents=True, exist_ok=True)
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (mainly for testing)."""
    global _settings
    _settings = None