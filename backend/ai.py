from google import genai
from google.genai import types
from backend.config import settings
from backend.constants import BANNED_AI_WORDS
import json
import logging
from typing import List, Dict, Generator

logger = logging.getLogger("vibeflow.ai")

# Using Gemini 3 models as per spec
MODEL_FLASH = "gemini-3-flash-preview"
MODEL_PRO = "gemini-3-pro-preview"

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.client = None
            logger.warning("AIService initialized without API Key. AI features will fail.")

    def get_vibe_cloud(self, prompt: str) -> List[str]:
        """Agent 0: The Sensory Scout - Expands seed into sensory anchors using a Generate-Curate loop."""
        if not self.client: raise Exception("Gemini API Key not configured")

        # Step 1: Brainstorm diverse candidates (Generate 10)
        candidates = self.generate_vibe_candidates(prompt)
        
        # Step 2: Curate the best ones (Select 5)
        anchors = self.curate_vibe_anchors(prompt, candidates)
        
        return anchors

    def generate_vibe_candidates(self, prompt: str) -> List[str]:
        """Internal: Generates a broad list of sensory candidates."""
        system_instruction = (
            "You are a Cinematographer and Sound Designer finding the 'Vibe' for a song."
            "\nTask: Brainstorm 10 distinct, evocative sensory details (visuals, sounds, textures) based on the user's input."
            "\n\nGUIDELINES:"
            "\n1. **Synthesize the Input:** If multiple keywords are provided, do not treat them in isolation. Find the *intersection* where they coexist. Create images that embody the combination of all inputs simultaneously."
            "\n2. **Logical Correlation:** Ensure each vibe is a direct, tangible manifestation of the *combined* theme."
            "\n3. **Conciseness:** Keep each anchor short and punchy (Max 8 words). Avoid long, flowery sentences."
            "\n4. **Sensory Focus:** Mix visuals, sounds, and textures. Show the physical evidence of the feeling."
            "\n5. **No Purple Prose:** Keep it raw, real, and grounded."
            "\n\nOUTPUT:"
            "\nReturn ONLY a JSON array of 10 strings."
        )
        try:
            response = self.client.models.generate_content(
                model=MODEL_FLASH,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.8
                )
            )
            return json.loads(response.text)[:10] if response.text else []
        except Exception as e:
            logger.error(f"Vibe Candidate Generation error: {e}")
            return []

    def curate_vibe_anchors(self, original_prompt: str, candidates: List[str]) -> List[str]:
        """Internal: Selects the most evocative anchors from the candidates."""
        if not candidates: return []
        
        candidates_str = "\n".join([f"- {c}" for c in candidates])
        prompt = f"Original Prompt: {original_prompt}\nCandidates:\n{candidates_str}"
        
        system_instruction = (
            "You are the 'Vibe Curator'. Select the top 5 most evocative, atmospheric, and inspiring anchors from the list."
            "\nCRITERIA:"
            "\n- **Reject** clichés (e.g., 'broken heart', 'tears')."
            "\n- **Select** images that tell a story or set a scene immediately."
            "\n- **Ensure** they fit the original prompt's mood."
            "\n\nOUTPUT:"
            "\nReturn ONLY a JSON array of the 5 selected strings."
        )
        try:
            response = self.client.models.generate_content(
                model=MODEL_FLASH,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.5
                )
            )
            return json.loads(response.text)[:5] if response.text else candidates[:5]
        except Exception as e:
            logger.error(f"Vibe Curation error: {e}")
            return candidates[:5]

    def architect_outline(self, title: str, anchors: List[str]) -> str:
        """Agent A: The Architect - Outlines the song structure."""
        prompt = f"Title: {title}\nAnchors: {', '.join(anchors)}\n\nOutline a song structure (Verse 1, Chorus, Verse 2, Bridge, Outro) with a brief narrative goal for each."
        system_instruction = "You are 'The Architect'. Create a structural outline for a song. Be brief. Return only the outline."
        
        response = self.client.models.generate_content(
            model=MODEL_PRO,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        return response.text

    def drafter_write(self, title: str, anchors: List[str], outline: str, style: str, rhyme_scheme: str) -> str:
        """Agent B: The Drafter - Writes the raw content with tags."""
        prompt = f"Title: {title}\nAnchors: {', '.join(anchors)}\nOutline: {outline}\nStyle: {style}\nRhyme Scheme: {rhyme_scheme}\n\nWrite the full lyrics."
        system_instruction = (
            "You are 'The Drafter'. Write raw, evocative lyrics based on the outline and anchors. "
            "MANDATORY: Tag every section clearly using brackets, e.g., [Verse 1], [Chorus], [Bridge], [Outro]. "
            "Use 'Show, Don't Tell'. Do not force rhymes. Rhyme when it feels natural, but prioritize imagery and meaning."
        )
        
        response = self.client.models.generate_content(
            model=MODEL_PRO,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.8)
        )
        return response.text

    def editor_refine(self, lyrics: str) -> str:
        """Agent C: The Editor - Removes clichés and polishes tone."""
        banned = ", ".join(BANNED_AI_WORDS)
        prompt = f"Lyrics to refine:\n{lyrics}\n\nStrictly remove these clichés: {banned}. Rewrite to be more conversational and raw."
        system_instruction = (
            "You are 'The Editor'. Clean up the lyrics. Make them feel authentic and human. "
            "MANDATORY: Preserve all section tags like [Verse 1], [Chorus], etc. "
            "Return ONLY the refined lyrics."
        )
        
        response = self.client.models.generate_content(
            model=MODEL_PRO,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
        )
        return response.text

    def rhythmist_polish(self, lyrics: str) -> str:
        """Agent D: The Rhythmist - Final meter and stress check."""
        prompt = f"Lyrics to polish:\n{lyrics}\n\nEnsure rhythmic consistency and natural flow."
        system_instruction = (
            "You are 'The Rhythmist'. Perform a final rhythmic polish. Ensure the flow is perfect for singing. "
            "MANDATORY: Preserve all section tags like [Verse 1], [Chorus], etc. "
            "Return ONLY the polished lyrics."
        )
        
        response = self.client.models.generate_content(
            model=MODEL_PRO,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.5)
        )
        return response.text

    def sonic_polish(self, lyrics: str) -> str:
        """Agent E: The Sonic Sculptor - Improves phonetics and removes forced rhymes."""
        prompt = f"Lyrics to improve:\n{lyrics}\n\nOptimize for phonetic beauty (assonance, consonance) and naturalness."
        system_instruction = (
            "You are 'The Sonic Sculptor'. Your job is to make the lyrics sound beautiful when sung or spoken. "
            "1. Enhance phonetic patterns (alliteration, assonance) without being overwhelming. "
            "2. LOOSEN strict rhyming. If a rhyme feels forced or cheesy, break it. Prioritize flow and 'mouthfeel'. "
            "MANDATORY: Preserve all section tags like [Verse 1], [Chorus], etc. "
            "Return ONLY the sculpted lyrics."
        )
        
        response = self.client.models.generate_content(
            model=MODEL_PRO,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
        )
        return response.text

    def lyrics_factory_stream(self, title: str, seed: str, style: str, rhyme_scheme: str, anchors: List[str] = None) -> Generator[str, None, None]:
        """Coordinated Agentic Workflow (The Lyrics Factory)."""
        if not self.client: yield "Error: No API Key"; return

        if not anchors:
            yield "🔍 [Sensory Scout] Expanding vibes...\n"
            anchors = self.get_vibe_cloud(seed)
            yield f"✨ Anchors: {', '.join(anchors)}\n\n"
        else:
            yield "Using selected vibes...\n"
            yield f"✨ Anchors: {', '.join(anchors)}\n\n"

        yield "🏗️ [Architect] Designing structure...\n"
        outline = self.architect_outline(title, anchors)
        
        yield "✍️ [Drafter] Drafting lyrics...\n"
        raw_draft = self.drafter_write(title, anchors, outline, style, rhyme_scheme)
        
        yield "✂️ [Editor] Removing clichés...\n"
        refined = self.editor_refine(raw_draft)
        
        yield "🎵 [Rhythmist] Polishing flow...\n"
        polished_rhythm = self.rhythmist_polish(refined)

        yield "✨ [Sonic Sculptor] Enhancing phonetics...\n"
        final_lyrics = self.sonic_polish(polished_rhythm)
        
        yield "\n--- FINAL LYRICS ---\n\n"
        
        # Stream the final lyrics word by word to maintain the 'feeling' of generation
        import time
        for word in final_lyrics.split(" "):
            yield word + " "
            time.sleep(0.01)
        
        # Total tokens tracking placeholder
        yield f"\n\n__USAGE__:1500"

    def get_stress_patterns(self, text: str) -> str:
        if not self.client: return text
        system_instruction = "Mark stressed syllables with **bold**."
        response = self.client.models.generate_content(
            model=MODEL_PRO, contents=text,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        return response.text

    def rewrite_text(self, original_text: str, selection: str, instructions: str = "Rewrite this") -> str:
        if not self.client: return selection
        system_instruction = f"Context: {original_text}\nRewrite the selection: {selection}\nBased on: {instructions}"
        response = self.client.models.generate_content(
            model=MODEL_PRO, contents=selection,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        return response.text

ai_service = AIService()
