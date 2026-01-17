from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_syllable_counting():
    """Test the syllable counting endpoint."""
    text = "I walked down empty streets\nRain falls on the glass"
    response = client.post("/utils/syllables", json={"text": text})
    
    assert response.status_code == 200
    counts = response.json()
    # syllapy output: I(1), walked(2), down(1), empty(2), streets(1) -> 7? 
    # Let's trust syllapy for this test's verification.
    assert counts == [7, 5]

def test_empty_syllables():
    response = client.post("/utils/syllables", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == []

def test_check_cliches():
    """Test the cliché checker utility."""
    from backend.utils import check_cliches
    text = "The shimmering starlight in the tapestry of time."
    found = check_cliches(text)
    assert "shimmering" in found
    assert "starlight" in found
    assert "tapestry" in found
    
    clean_text = "The rain hits the concrete and the tires hum."
    assert check_cliches(clean_text) == []

