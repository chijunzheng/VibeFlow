import os
import pytest
from backend.config import Settings

def test_settings_load_from_env():
    """Verify settings load from environment variables."""
    os.environ["GEMINI_API_KEY"] = "test_env_key"
    settings = Settings()
    assert settings.GEMINI_API_KEY == "test_env_key"
    assert settings.is_gemini_configured is True
    del os.environ["GEMINI_API_KEY"]

def test_settings_default_empty():
    """Verify default setting is empty string if not provided."""
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    
    settings = Settings()
    # If no .env file exists or key not in it
    if not os.path.exists(".env"):
        assert settings.GEMINI_API_KEY == ""
        assert settings.is_gemini_configured is False

def test_database_url_default():
    """Verify default database URL."""
    settings = Settings()
    assert settings.DATABASE_URL == "sqlite:///storage/vibeflow.db"
