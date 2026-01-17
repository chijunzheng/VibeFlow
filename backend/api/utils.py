from fastapi import APIRouter, Body
from backend.utils import get_syllable_counts
from typing import List

router = APIRouter(prefix="/utils", tags=["utils"])

@router.post("/syllables", response_model=List[int])
def syllables(text: str = Body(..., embed=True)):
    """
    Calculate syllable counts for each line of the provided text.
    """
    return get_syllable_counts(text)
