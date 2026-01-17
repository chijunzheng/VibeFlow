from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
import json
from backend.database import get_session
from backend.models import Song, SongCreate, SongRead, SongUpdate
from backend.ai import ai_service

router = APIRouter(prefix="/songs", tags=["songs"])

class RefineLyricsRequest(BaseModel):
    current_lyrics: str
    selection: str
    instruction: str

@router.post("/", response_model=SongRead)
def create_song(song: SongCreate, session: Session = Depends(get_session)):
    db_song = Song.model_validate(song)
    session.add(db_song)
    session.commit()
    session.refresh(db_song)
    return db_song

@router.get("/", response_model=List[SongRead])
def read_songs(offset: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    songs = session.exec(select(Song).offset(offset).limit(limit)).all()
    return songs

@router.get("/{song_id}", response_model=SongRead)
def read_song(song_id: int, session: Session = Depends(get_session)):
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.put("/{song_id}", response_model=SongRead)
def update_song(song_id: int, song_update: SongUpdate, session: Session = Depends(get_session)):
    db_song = session.get(Song, song_id)
    if not db_song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song_data = song_update.model_dump(exclude_unset=True)
    for key, value in song_data.items():
        setattr(db_song, key, value)
    
    session.add(db_song)
    session.commit()
    session.refresh(db_song)
    return db_song

@router.delete("/{song_id}")
def delete_song(song_id: int, session: Session = Depends(get_session)):
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    session.delete(song)
    session.commit()
    return {"ok": True}

@router.post("/{song_id}/generate_vibe", response_model=SongRead)
def generate_vibe(
    song_id: int, 
    prompt: str = Body(..., embed=True), 
    session: Session = Depends(get_session)
):
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        anchors = ai_service.get_vibe_cloud(prompt)
        song.vibe_cloud = anchors
        song.content = song.content or {}
        song.content["seed_prompt"] = prompt
        song.content = dict(song.content)
        session.add(song)
        session.commit()
        session.refresh(song)
        return song
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

@router.get("/{song_id}/write_lyrics/stream")
def stream_lyrics(
    song_id: int,
    style: str = "Modern",
    rhyme_scheme: str = "Free Verse",
    seed: str | None = None,
    session: Session = Depends(get_session)
):
    """
    The Lyrics Factory: Coordinated Agentic Workflow.
    """
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    seed_text = (seed or "").strip()
    if not seed_text:
        seed_text = (song.content or {}).get("seed_prompt") or song.title

    def generator():
        full_output = ""
        final_tokens = 0
        
        # Trigger the Lyrics Factory
        # If vibe_cloud exists, we pass it directly to skip regeneration
        anchors = song.vibe_cloud if song.vibe_cloud else None
        if not anchors:
            anchors = ai_service.get_vibe_cloud(seed_text)
            song.vibe_cloud = anchors
        
        for chunk in ai_service.lyrics_factory_stream(song.title, seed_text, style, rhyme_scheme, anchors=anchors):
            if chunk.startswith("__USAGE__:"):
                try:
                    final_tokens = int(chunk.split(":")[1])
                except: pass
                continue
                
            full_output += chunk
            yield chunk
        
        # Extract actual lyrics from the factory output (anything after '--- FINAL LYRICS ---')
        final_lyrics = full_output
        if "--- FINAL LYRICS ---" in full_output:
            final_lyrics = full_output.split("--- FINAL LYRICS ---")[-1].strip()
        
        # Update DB
        song.content = song.content or {}
        song.content["seed_prompt"] = seed_text
        song.content["lyrics"] = final_lyrics
        song.content = dict(song.content)
        if final_tokens > 0:
            song.total_tokens = (song.total_tokens or 0) + final_tokens
        
        session.add(song)
        session.commit()

    return StreamingResponse(generator(), media_type="text/plain")

@router.post("/{song_id}/refine_lyrics", response_model=str)
def refine_lyrics(
    song_id: int,
    request: RefineLyricsRequest,
    session: Session = Depends(get_session)
):
    """
    Refines a specific section of lyrics using AI.
    Returns only the rewritten section.
    """
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        rewritten = ai_service.rewrite_text(
            original_text=request.current_lyrics,
            selection=request.selection,
            instructions=request.instruction
        )
        return rewritten
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")
