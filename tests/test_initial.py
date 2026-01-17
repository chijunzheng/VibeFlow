import pytest
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_api_key_env_loading():
    """F001: API Key Configuration Security"""
    # This will fail because backend.main doesn't exist yet
    from backend.config import settings
    assert settings.GEMINI_API_KEY is not None

def test_db_file_permissions():
    """F002: Local Database File Protection"""
    import os
    import stat
    db_path = "storage/vibeflow.db"
    if os.path.exists(db_path):
        mode = os.stat(db_path).st_mode
        assert mode & stat.S_IRUSR
        assert not (mode & stat.S_IRGRP)
        assert not (mode & stat.S_IROTH)
    else:
        pytest.fail("DB file does not exist")
