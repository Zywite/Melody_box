from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, EmailStr


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
    role: str = "user"
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    role: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    user_id: str
    role: str = "user"


class SongResponse(BaseModel):
    id: str
    title: str
    artist: str
    album: str | None
    duration: float
    media_type: str | None = "audio"
    file: str | None = None
    file_path: str | None = None
    has_fft: bool | None = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        """Build a SongResponse from a Song ORM row, exposing a public ``file`` URL."""
        filename = Path(obj.file_path).name if obj.file_path else None
        file_url = f"/music/{filename}" if filename else None
        return cls(
            id=obj.id,
            title=obj.title,
            artist=obj.artist,
            album=obj.album,
            duration=obj.duration,
            media_type=obj.media_type,
            file=file_url,
            file_path=filename,
            has_fft=bool(obj.fft_data),
            created_at=obj.created_at,
        )


class PlaylistCreate(BaseModel):
    name: str
    description: str | None = None


class PlaylistSongResponse(BaseModel):
    id: str
    song_id: str
    position: int | None
    added_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None
    songs: list[PlaylistSongResponse] | None = []

    model_config = ConfigDict(from_attributes=True)


class FavoriteCreate(BaseModel):
    song_id: str


class FavoriteResponse(BaseModel):
    id: str
    user_id: str
    song_id: str
    added_at: datetime | None
    song: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class SongAddRequest(BaseModel):
    song_id: str


class YouTubeSearchResult(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str
    duration: int
    views: int | None = None


class YouTubeDownloadRequest(BaseModel):
    video_id: str
    format: str = "m4a"
    quality: str = "320"
    title: str | None = None
    artist: str | None = None
