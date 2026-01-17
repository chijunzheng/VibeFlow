from fastapi.testclient import TestClient
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

def test_create_song(client: TestClient):
    """Test creating a new song."""
    response = client.post(
        "/songs/",
        json={"title": "Midnight Rain"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["title"] == "Midnight Rain"
    assert data["id"] is not None
    assert data["created_at"] is not None

def test_read_songs(client: TestClient):
    """Test reading songs."""
    client.post("/songs/", json={"title": "Song 1"})
    client.post("/songs/", json={"title": "Song 2"})
    
    response = client.get("/songs/")
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] == "Song 1"
    assert data[1]["title"] == "Song 2"
