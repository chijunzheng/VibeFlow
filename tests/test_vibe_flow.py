from unittest.mock import patch, MagicMock
from backend.ai import ai_service

def test_get_vibe_cloud_flow():
    """Verify the Generate -> Curate flow within get_vibe_cloud."""
    
    mock_candidates = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"]
    mock_curated = ["C1", "C3", "C5", "C7", "C9"]
    
    # We patch the *methods* on the instance or class. 
    # Since they are methods of ai_service, we patch them there.
    
    with patch.object(ai_service, "_generate_vibe_candidates", return_value=mock_candidates) as m_gen:
        with patch.object(ai_service, "_curate_vibe_anchors", return_value=mock_curated) as m_cur:
            
            result = ai_service.get_vibe_cloud("Sleep")
            
            # Assertions
            assert result == mock_curated
            m_gen.assert_called_once_with("Sleep")
            m_cur.assert_called_once_with("Sleep", mock_candidates)

def test_curate_handles_empty_candidates():
    """Test curation with empty input."""
    result = ai_service._curate_vibe_anchors("Prompt", [])
    assert result == []

def test_curate_fallback_on_error():
    """Test curation returns subset if AI fails."""
    candidates = ["A", "B", "C", "D", "E", "F"]
    
    # Mock client to raise exception
    with patch.object(ai_service, "client") as mock_client:
        mock_client.models.generate_content.side_effect = Exception("AI Error")
        
        result = ai_service._curate_vibe_anchors("Prompt", candidates)
        
        # Should return top 5 of input
        assert result == ["A", "B", "C", "D", "E"]
