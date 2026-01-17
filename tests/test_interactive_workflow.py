from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import pytest
from backend.main import app
from backend.database import get_session

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

def test_brainstorm_vibes(client: TestClient):
    """Test the brainstorming endpoint."""
    mock_candidates = ["Vibe 1", "Vibe 2"]
    
    with patch("backend.ai.ai_service.generate_vibe_candidates", return_value=mock_candidates) as mock_gen:
        response = client.post("/ai/brainstorm_vibes", json={"prompt": "Test Prompt"})
        
        assert response.status_code == 200
        assert response.json() == mock_candidates
        mock_gen.assert_called_once_with("Test Prompt")

def test_refine_lyrics(client: TestClient):
    """Test the lyric refinement endpoint."""
    # Create a song first
    response = client.post("/songs/", json={"title": "Test Song"})
    song_id = response.json()["id"]
    
    mock_rewritten = "Better lyrics"
    
    with patch("backend.ai.ai_service.rewrite_text", return_value=mock_rewritten) as mock_rewrite:
        response = client.post(
            f"/songs/{song_id}/refine_lyrics",
            json={
                "current_lyrics": "Bad lyrics",
                "selection": "Bad",
                "instruction": "Make it better"
            }
        )
        
        assert response.status_code == 200
        assert response.json() == mock_rewritten
        
        mock_rewrite.assert_called_once_with(
            original_text="Bad lyrics",
            selection="Bad",
            instructions="Make it better"
        )

def test_refine_lyrics_song_not_found(client: TestClient):
    """Test refinement for non-existent song."""
    response = client.post(
        "/songs/999/refine_lyrics",
        json={
            "current_lyrics": "Text",
            "selection": "Text",
            "instruction": "Fix"
        }
    )
    assert response.status_code == 404
