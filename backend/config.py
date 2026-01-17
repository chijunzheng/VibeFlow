from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application configuration settings.
    Loads from environment variables and/or .env file.
    """
    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///storage/vibeflow.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def is_gemini_configured(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.GEMINI_API_KEY)

settings = Settings()
