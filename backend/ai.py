from google import genai
from google.genai import types
from backend.config import settings
from backend.constants import BANNED_AI_WORDS
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

    def stream_lyrics(self, title: str, vibe_cloud: List[str], style: str = "Modern", rhyme_scheme: str = "Free Verse"):
        """
        Yields lyrics chunks from Gemini Pro.
        """
        if not self.client:
            raise Exception("Gemini API Key not configured")
        
        anchors_str = ", ".join(vibe_cloud)
        banned_str = ", ".join(BANNED_AI_WORDS)
        
        prompt = (
            f"Title: {title}\n"
            f"Vibe Cloud Anchors: {anchors_str}\n"
            f"Style: {style}\n"
            f"Rhyme Scheme: {rhyme_scheme}\n\n"
            "Write a verse and a chorus for this song."
        )

        system_instruction = (
            "You are 'The Ghostwriter', a top-tier lyricist. "
            "Write lyrics that strictly incorporate the provided 'Vibe Cloud' anchors to ensure concrete imagery. "
            "Follow the requested Rhyme Scheme if specified (e.g., AABB, ABAB). "
            f"CRITICAL: Avoid these AI-isms and clichés: {banned_str}. "
            "Use a conversational, raw, and modern tone. Favor concrete nouns over abstract adjectives. "
            "Structure: [Verse] then [Chorus]. "
            "Return ONLY the lyrics."
        )

        try:
            for chunk in self.client.models.generate_content_stream(
                model="gemini-2.0-flash-thinking-exp-1219",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.8
                )
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Error streaming lyrics: {str(e)}")
            raise e

    def get_stress_patterns(self, text: str) -> str:
        """
        Marks stressed syllables in bold (markdown style) using Gemini Flash.
        Example: "I **walked** down **emp**ty **streets**"
        """
        if not self.client:
            raise Exception("Gemini API Key not configured")

        if not text.strip():
            return ""

        system_instruction = (
            "You are a prosody expert. Analyze the provided lyrics and mark the stressed syllables by wrapping them in double asterisks (**bold**). "
            "Do not change any words or punctuation. Only add asterisks around the stressed syllables. "
            "Example Input: 'I walked down empty streets' "
            "Example Output: 'I **walked** down **emp**ty **streets**' "
            "Maintain the original line breaks."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0
                )
            )
            return response.text if response.text else text
        except Exception as e:
            logger.error(f"Error analyzing stress: {str(e)}")
            raise e

ai_service = AIService()
