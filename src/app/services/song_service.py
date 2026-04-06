from sqlalchemy.orm import Session
from app.models import Song
from app.core.config import settings
import os
import uuid
from pathlib import Path

class SongService:
    @staticmethod
    def create_song(db: Session, title: str, artist: str, file_path: str, duration: float, album: str = None, media_type: str = "audio"):
        db_song = Song(
            id=str(uuid.uuid4()),
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            file_path=file_path,
            media_type=media_type
        )
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        return db_song

    @staticmethod
    def get_song(db: Session, song_id: str):
        return db.query(Song).filter(Song.id == song_id).first()

    @staticmethod
    def get_all_songs(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Song).offset(skip).limit(limit).all()

    @staticmethod
    def search_songs(db: Session, query: str):
        return db.query(Song).filter(
            (Song.title.ilike(f"%{query}%")) |
            (Song.artist.ilike(f"%{query}%")) |
            (Song.album.ilike(f"%{query}%"))
        ).all()

    @staticmethod
    def delete_song(db: Session, song_id: str):
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            # Eliminar archivo
            if os.path.exists(song.file_path):
                os.remove(song.file_path)
            db.delete(song)
            db.commit()
        return song
