"""Song service: persistence operations for Song entities."""

from sqlalchemy.orm import Session
from app.models import Song
from app.core.config import settings
import os
import uuid
import time
from pathlib import Path


class SongService:
    """Static methods for creating, reading, searching, and deleting songs."""

    @staticmethod
    def create_song(
        db: Session,
        title: str,
        artist: str,
        file_path: str,
        duration: float,
        album: str = None,
        media_type: str = "audio",
    ) -> tuple[Song, bool]:
        """Create and persist a new song row.

        FFT analysis is NOT triggered here; callers (upload routes) enqueue
        an arq job when Redis is available.

        Returns:
            A tuple of (newly created Song, fft_enqueued_flag). The boolean
            is always False; it remains part of the signature for backward
            compatibility with older callers.
        """
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
        return db_song, False

    @staticmethod
    def get_song(db: Session, song_id: str) -> Song | None:
        """Look up a song by primary key.

        Returns:
            The matching Song row, or None if no song has that id.
        """
        return db.query(Song).filter(Song.id == song_id).first()

    @staticmethod
    def get_all_songs(db: Session, skip: int = 0, limit: int = 100) -> list[Song]:
        """Return a slice of songs ordered by their insertion order.

        Args:
            skip: Number of rows to skip (offset).
            limit: Maximum number of rows to return.

        Returns:
            A list of Song rows; empty if there are no songs.
        """
        return db.query(Song).offset(skip).limit(limit).all()

    @staticmethod
    def search_songs(db: Session, query: str) -> list[Song]:
        """Case-insensitive substring search over title, artist, and album.

        Returns:
            A list of matching Song rows; empty if nothing matches.
        """
        return db.query(Song).filter(
            (Song.title.ilike(f"%{query}%")) |
            (Song.artist.ilike(f"%{query}%")) |
            (Song.album.ilike(f"%{query}%"))
        ).all()

    @staticmethod
    def delete_song(db: Session, song_id: str) -> Song | None:
        """Delete a song row and the underlying file on disk.

        Missing files are ignored so the row can still be removed from the
        database.

        Returns:
            The deleted Song row if it existed, otherwise None.
        """
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            if os.path.exists(song.file_path):
                os.remove(song.file_path)
            db.delete(song)
            db.commit()
        return song
