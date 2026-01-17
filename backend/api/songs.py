from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import List
import json
from backend.database import get_session
from backend.models import Song, SongCreate, SongRead, SongUpdate
from backend.ai import ai_service

router = APIRouter(prefix="/songs", tags=["songs"])

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
    """
    Generate a Vibe Cloud for the song using Gemini Flash.
    Updates the song's vibe_cloud field.
    """
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    try:
        anchors = ai_service.get_vibe_cloud(prompt)
        song.vibe_cloud = anchors
        session.add(song)
        session.commit()
        session.refresh(song)
        return song
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

@router.post("/{song_id}/write_lyrics", response_model=SongRead)
def write_lyrics(
    song_id: int,
    style: str = Body(default="Modern", embed=True),
    rhyme_scheme: str = Body(default="Free Verse", embed=True),
    session: Session = Depends(get_session)
):
    """
    Generate lyrics using Gemini Pro based on the song's title and vibe cloud.
    Updates the song's content.
    """
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.vibe_cloud:
        raise HTTPException(status_code=400, detail="Vibe Cloud is empty. Generate vibes first.")
    
    # Simple placeholder as we prefer streaming
    return song

@router.get("/{song_id}/write_lyrics/stream")
def stream_lyrics(
    song_id: int,
    style: str = "Modern",
    rhyme_scheme: str = "Free Verse",
    session: Session = Depends(get_session)
):
    """
    Stream lyrics generation.
    """
    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.vibe_cloud:
        raise HTTPException(status_code=400, detail="Vibe Cloud is empty")

    # Construct the current prompt
    anchors_str = ", ".join(song.vibe_cloud)
    prompt_text = (
        f"Title: {song.title}\n"
        f"Vibe Cloud Anchors: {anchors_str}\n"
        f"Style: {style}\n"
        f"Rhyme Scheme: {rhyme_scheme}\n\n"
        "Write a verse and a chorus for this song."
    )
    
    # Load history
    history = []
    if song.thought_sig:
        try:
            history = json.loads(song.thought_sig)
        except:
            history = []
            
    # Add current prompt
    current_message = {"role": "user", "parts": [prompt_text]}
    history.append(current_message)

    def generator():
        full_lyrics = ""
        # Pass full history to AI
        for chunk in ai_service.stream_lyrics(history, style, rhyme_scheme):
            full_lyrics += chunk
            yield chunk
        
        # Append model response to history
        history.append({"role": "model", "parts": [full_lyrics]})
        
        # Update DB
        song.content = song.content or {}
        song.content["lyrics"] = full_lyrics
        song.content = dict(song.content)
        song.thought_sig = json.dumps(history) # Save updated history
        session.add(song)
        session.commit()

    return StreamingResponse(generator(), media_type="text/plain")