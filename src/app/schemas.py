from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class SongCreate(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    duration: float

class SongResponse(BaseModel):
    id: str
    title: str
    artist: str
    album: Optional[str]
    duration: float
    media_type: Optional[str] = "audio"
    created_at: datetime

    class Config:
        from_attributes = True

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PlaylistSongResponse(BaseModel):
    id: str
    song_id: str
    position: Optional[int]
    added_at: Optional[datetime]

    class Config:
        from_attributes = True

class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    songs: Optional[List[PlaylistSongResponse]] = []

    class Config:
        from_attributes = True

class FavoriteCreate(BaseModel):
    song_id: str

class FavoriteResponse(BaseModel):
    id: str
    user_id: str
    song_id: str
    added_at: Optional[datetime]
    song: Optional[dict] = None

    class Config:
        from_attributes = True

class SongAddRequest(BaseModel):
    song_id: str
