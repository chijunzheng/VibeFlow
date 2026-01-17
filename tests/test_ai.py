from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest
from backend.main import app
from backend.database import get_session
from backend.models import Song

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_generate_vibe(client: TestClient):
    """Test generating vibe cloud for a song."""
    # Create a song first
    response = client.post("/songs/", json={"title": "Stormy Night"})
    song_id = response.json()["id"]

    # Mock the AIService
    mock_anchors = ["Thunder", "Dark clouds", "Wind", "Raindrops", "Cold"]
    
    with patch("backend.ai.ai_service.get_vibe_cloud", return_value=mock_anchors) as mock_get_vibe:
        # Call the generate endpoint
        response = client.post(
            f"/songs/{song_id}/generate_vibe",
            json={"prompt": "Storm"}
        )
        
        data = response.json()
        
        assert response.status_code == 200
        assert data["id"] == song_id
        assert data["vibe_cloud"] == mock_anchors
        
        # Verify mock was called
        mock_get_vibe.assert_called_once_with("Storm")

def test_generate_vibe_song_not_found(client: TestClient):
    """Test generating vibe for non-existent song."""
    with patch("backend.ai.ai_service.get_vibe_cloud", return_value=[]) as mock_get_vibe:
        response = client.post(
            "/songs/999/generate_vibe",
            json={"prompt": "Storm"}
        )
        assert response.status_code == 404
