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

def test_stream_lyrics_persistence(client: TestClient):
    """
    Verify that stream_lyrics saves to the DB correctly.
    """
    # Create song
    response = client.post("/songs/", json={"title": "Persistence Test"})
    song_id = response.json()["id"]
    
    # Mock Vibe Cloud
    with patch("backend.ai.ai_service.get_vibe_cloud", return_value=["Vibe1"]):
        client.post(f"/songs/{song_id}/generate_vibe", json={"prompt": "Test"})

    # Mock Stream
    mock_chunks = ["Chunk1", "Chunk2"]
    
    with patch("backend.ai.ai_service.lyrics_factory_stream", return_value=iter(mock_chunks)):
        response = client.get(f"/songs/{song_id}/write_lyrics/stream")
        
        # Consume stream
        content = b"".join(response.iter_bytes())
        assert content.decode("utf-8") == "Chunk1Chunk2"
        
        # Verify persistence
        response = client.get(f"/songs/{song_id}")
        data = response.json()
        assert data["content"]["lyrics"] == "Chunk1Chunk2"
