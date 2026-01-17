from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from typing import List
from backend.database import get_session
from backend.models import Song, SongCreate, SongRead
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
    
    try:
        lyrics = ai_service.write_lyrics(song.title, song.vibe_cloud, style)
        
        # Initialize content dict if None
        if not song.content:
            song.content = {}
        
        # Update content with new lyrics (appending or replacing - let's replace for now or add to a 'drafts' list)
        # For simplicity, we just store it in a 'lyrics' key
        song.content["lyrics"] = lyrics
        # We need to re-assign to trigger SQLModel/SQLAlchemy change detection for JSON fields if it was mutable
        # But here we are assigning a new dict key or re-assigning the whole dict
        song.content = dict(song.content) 
        
        session.add(song)
        session.commit()
        session.refresh(song)
        return song
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Writing failed: {str(e)}")
