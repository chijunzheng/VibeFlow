from fastapi.testclient import TestClient
from unittest.mock import patch
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

def test_stream_lyrics(client: TestClient):
    """Test streaming lyrics for a song."""
    # Create song
    response = client.post("/songs/", json={"title": "Neon City"})
    song_id = response.json()["id"]
    
    # Mock vibe cloud
    mock_anchors = ["Neon", "Light"]
    with patch("backend.ai.ai_service.get_vibe_cloud", return_value=mock_anchors):
        client.post(f"/songs/{song_id}/generate_vibe", json={"prompt": "Neon"})

    mock_chunks = ["Verse 1", "\nWalking", " down"]
    
    with patch("backend.ai.ai_service.stream_lyrics_factory", return_value=iter(mock_chunks)) as mock_stream:
        response = client.get(f"/songs/{song_id}/write_lyrics/stream")
        
        assert response.status_code == 200
        # Consuming the stream
        content = b"".join(response.iter_bytes())
        assert content.decode("utf-8") == "Verse 1\nWalking down"
        
        mock_stream.assert_called_once()
        call_args = mock_stream.call_args[0]
        assert call_args[0] == "Neon City"
        assert call_args[1] == "Neon"
        assert call_args[2] == mock_anchors

def test_stream_lyrics_uses_seed(client: TestClient):
    """Test that streaming lyrics uses the seed to expand the vibe cloud."""
    response = client.post("/songs/", json={"title": "Fresh Start Song"})
    song_id = response.json()["id"]

    mock_chunks = ["Verse 1"]
    with patch("backend.ai.ai_service.get_vibe_cloud", return_value=["Fire", "Ice"]) as mock_vibe:
        with patch("backend.ai.ai_service.stream_lyrics_factory", return_value=iter(mock_chunks)) as mock_stream:
            response = client.get(f"/songs/{song_id}/write_lyrics/stream?seed=Dual")

            assert response.status_code == 200
            content = b"".join(response.iter_bytes())
            assert content.decode("utf-8") == "Verse 1"

            mock_vibe.assert_called_once_with("Dual")
            mock_stream.assert_called_once()
            call_args = mock_stream.call_args[0]
            assert call_args[0] == "Fresh Start Song"
            assert call_args[1] == "Dual"
            assert call_args[2] == ["Fire", "Ice"]

    song = client.get(f"/songs/{song_id}").json()
    assert song["vibe_cloud"] == ["Fire", "Ice"]

def test_get_stress_patterns(client: TestClient):
    """Test stress pattern analysis."""
    mock_response = "I **walked** down **emp**ty **streets**"
    
    with patch("backend.ai.ai_service.get_stress_patterns", return_value=mock_response) as mock_stress:
        response = client.post(
            "/utils/stress",
            json={"text": "I walked down empty streets"}
        )
        
        assert response.status_code == 200
        assert response.json() == mock_response
        mock_stress.assert_called_once_with("I walked down empty streets")
