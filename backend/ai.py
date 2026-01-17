from google import genai
from google.genai import types
from backend.config import settings
import json
import logging
from typing import List

logger = logging.getLogger("vibeflow.ai")

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.client = None
            logger.warning("AIService initialized without API Key. AI features will fail.")

    def get_vibe_cloud(self, prompt: str) -> List[str]:
        """
        Generates 5 sensory anchors based on the input prompt using Gemini Flash.
        """
        if not self.client:
            raise Exception("Gemini API Key not configured")

        system_instruction = (
            "You are 'The Sensory Scout', a creative songwriting assistant. "
            "Your goal is to expand a single word or concept into a 'Vibe Cloud' of 5 concrete, sensory details. "
            "Focus on sights, sounds, smells, and textures. "
            "Avoid clichés. Be specific. "
            "Return ONLY a JSON array of 5 strings. Example: ['Petrichor', 'Cold glass', 'Blurred brake lights', 'Static on radio', 'Heavy wool']"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp", # Using latest flash model
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            # Parse the JSON response
            if response.text:
                anchors = json.loads(response.text)
                if isinstance(anchors, list):
                    return anchors[:5] # Ensure max 5
                
            logger.error(f"Unexpected AI response format: {response.text}")
            return []

        except Exception as e:
            logger.error(f"Error generating vibe cloud: {str(e)}")
            raise e

    def write_lyrics(self, title: str, vibe_cloud: List[str], style: str = "Modern") -> str:
        """
        Writes lyrics using Gemini Pro based on the vibe cloud.
        """
        if not self.client:
            raise Exception("Gemini API Key not configured")
        
        anchors_str = ", ".join(vibe_cloud)
        prompt = f"Title: {title}\nVibe Cloud Anchors: {anchors_str}\nStyle: {style}\n\nWrite a verse and a chorus for this song."

        system_instruction = (
            "You are 'The Ghostwriter', a top-tier lyricist. "
            "Write lyrics that strictly incorporate the provided 'Vibe Cloud' anchors to ensure concrete imagery. "
            "Avoid 'AI-isms' (shimmering, tapestry, embrace, whisper). "
            "Use a conversational, raw, and modern tone. "
            "Structure: [Verse] then [Chorus]. "
            "Return ONLY the lyrics."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp-1219", # Using a thinking model for high reasoning
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.8
                )
            )
            
            return response.text if response.text else ""

        except Exception as e:
            logger.error(f"Error writing lyrics: {str(e)}")
            raise e

ai_service = AIService()
