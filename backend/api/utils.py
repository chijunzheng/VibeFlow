from fastapi import APIRouter, Body, HTTPException
from backend.utils import get_syllable_counts
from backend.ai import ai_service
from typing import List

router = APIRouter(prefix="/utils", tags=["utils"])

@router.post("/syllables", response_model=List[int])
def syllables(text: str = Body(..., embed=True)):
    """
    Calculate syllable counts for each line of the provided text.
    """
    return get_syllable_counts(text)

@router.post("/stress", response_model=str)
def analyze_stress(text: str = Body(..., embed=True)):
    """
    Analyze text and return it with stressed syllables marked in **bold**.
    """
    try:
        return ai_service.get_stress_patterns(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
