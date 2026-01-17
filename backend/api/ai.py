from fastapi import APIRouter, HTTPException, Body
from typing import List
from backend.ai import ai_service
from pydantic import BaseModel
import logging

logger = logging.getLogger("vibeflow.api.ai")

router = APIRouter(prefix="/ai", tags=["ai"])

class BrainstormRequest(BaseModel):
    prompt: str

@router.post("/brainstorm_vibes", response_model=List[str])
def brainstorm_vibes(request: BrainstormRequest):
    """
    Generates a list of vibe candidates based on a prompt.
    Does not save to the database.
    """
    try:
        candidates = ai_service.generate_vibe_candidates(request.prompt)
        return candidates
    except Exception as e:
        logger.error(f"Brainstorm vibes failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
