from typing import Optional, List, Dict
from sqlmodel import Field, SQLModel, JSON
from datetime import datetime

class SongBase(SQLModel):
    title: str
    vibe_cloud: Optional[List[str]] = Field(default=None, sa_type=JSON)
    content: Optional[Dict] = Field(default=None, sa_type=JSON)
    thought_sig: Optional[str] = None
    total_tokens: int = 0

class Song(SongBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SongCreate(SongBase):
    pass

class SongUpdate(SQLModel):
    title: Optional[str] = None
    vibe_cloud: Optional[List[str]] = Field(default=None, sa_type=JSON)
    content: Optional[Dict] = Field(default=None, sa_type=JSON)
    thought_sig: Optional[str] = None
    total_tokens: Optional[int] = None

class SongRead(SongBase):
    id: int
    created_at: datetime
    updated_at: datetime
