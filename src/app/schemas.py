from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from pathlib import Path

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
    file: Optional[str] = None
    file_path: Optional[str] = None
    has_fft: Optional[bool] = False
    created_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, song):
        filename = Path(song.file_path).name if song.file_path else None
        file_url = f"/music/{filename}" if filename else None
        return cls(
            id=song.id,
            title=song.title,
            artist=song.artist,
            album=song.album,
            duration=song.duration,
            media_type=song.media_type,
            file=file_url,
            file_path=filename,
            has_fft=bool(song.fft_data),
            created_at=song.created_at
        )

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


class YouTubeSearchResult(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str
    duration: int
    views: Optional[int] = None


class YouTubeDownloadRequest(BaseModel):
    video_id: str
    format: str = "m4a"
    quality: str = "320"
    title: Optional[str] = None
    artist: Optional[str] = None
