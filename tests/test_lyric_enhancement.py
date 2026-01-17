from unittest.mock import patch, MagicMock
import pytest
from backend.ai import ai_service

def test_sonic_polish_integration():
    """Verify that the Sonic Sculptor agent is integrated into the workflow."""
    
    # Mocks for the chain
    mock_anchors = ["A", "B"]
    mock_outline = "Outline"
    mock_draft = "Draft Lyrics"
    mock_refined = "Refined Lyrics"
    mock_rhythm = "Rhythmic Lyrics"
    mock_final = "Sonic Polished Lyrics"
    
    with patch.object(ai_service, "get_vibe_cloud", return_value=mock_anchors) as m_scout, \
         patch.object(ai_service, "architect_outline", return_value=mock_outline) as m_architect, \
         patch.object(ai_service, "drafter_write", return_value=mock_draft) as m_drafter, \
         patch.object(ai_service, "editor_refine", return_value=mock_refined) as m_editor, \
         patch.object(ai_service, "rhythmist_polish", return_value=mock_rhythm) as m_rhythmist, \
         patch.object(ai_service, "sonic_polish", return_value=mock_final) as m_sonic:
        
        # Act: Consume the generator
        generator = ai_service.lyrics_factory_stream("Title", "Seed", "Style", "Rhyme")
        output = list(generator)
        full_text = "".join(output)
        
        # Assertions
        
        # 1. Verify sequence
        m_scout.assert_called_once()
        m_architect.assert_called_once()
        m_drafter.assert_called_once()
        m_editor.assert_called_once()
        m_rhythmist.assert_called_once_with(mock_refined)
        
        # 2. Verify Sonic Sculptor is called with previous output
        m_sonic.assert_called_once_with(mock_rhythm)
        
        # 3. Verify user feedback in stream
        assert "✨ [Sonic Sculptor] Enhancing phonetics..." in full_text
        
        # 4. Verify final output contains the sonic polished lyrics
        assert mock_final in full_text
