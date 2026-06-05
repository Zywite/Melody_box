"""Playlist service: persistence operations for Playlist and PlaylistSong."""

from sqlalchemy.orm import Session, joinedload
from app.models import Playlist, PlaylistSong, Song
import uuid


class PlaylistService:
    """Static methods for creating, querying, and mutating playlists."""

    @staticmethod
    def create_playlist(
        db: Session, user_id: str, name: str, description: str = None
    ) -> Playlist:
        """Create and persist a new empty playlist owned by ``user_id``."""
        db_playlist = Playlist(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            description=description
        )
        db.add(db_playlist)
        db.commit()
        db.refresh(db_playlist)
        return db_playlist

    @staticmethod
    def get_playlist(db: Session, playlist_id: str) -> Playlist | None:
        """Fetch a playlist eagerly loading its ordered songs.

        Returns:
            The Playlist row with its ``songs`` relationship populated, or
            None if no playlist has that id.
        """
        return db.query(Playlist).options(
            joinedload(Playlist.songs).joinedload(PlaylistSong.song)
        ).filter(Playlist.id == playlist_id).first()

    @staticmethod
    def get_user_playlists(db: Session, user_id: str) -> list[Playlist]:
        """List every playlist owned by ``user_id`` with their songs loaded."""
        return db.query(Playlist).options(
            joinedload(Playlist.songs).joinedload(PlaylistSong.song)
        ).filter(Playlist.user_id == user_id).all()

    @staticmethod
    def add_song_to_playlist(
        db: Session, playlist_id: str, song_id: str
    ) -> PlaylistSong:
        """Append a song to the end of a playlist.

        If the song is already in the playlist, the existing association row
        is returned unchanged (no duplicates, no position change).

        Returns:
            The PlaylistSong association row representing membership.
        """
        existing = db.query(PlaylistSong).filter(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        ).first()

        if existing:
            return existing

        max_position = db.query(PlaylistSong).filter(
            PlaylistSong.playlist_id == playlist_id
        ).count()

        db_playlist_song = PlaylistSong(
            id=str(uuid.uuid4()),
            playlist_id=playlist_id,
            song_id=song_id,
            position=max_position + 1
        )
        db.add(db_playlist_song)
        db.commit()
        db.refresh(db_playlist_song)
        return db_playlist_song

    @staticmethod
    def remove_song_from_playlist(
        db: Session, playlist_id: str, song_id: str
    ) -> PlaylistSong | None:
        """Remove a song from a playlist (idempotent).

        Returns:
            The deleted association row, or None if the song was not in
            the playlist.
        """
        db_playlist_song = db.query(PlaylistSong).filter(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        ).first()

        if db_playlist_song:
            db.delete(db_playlist_song)
            db.commit()

        return db_playlist_song

    @staticmethod
    def delete_playlist(db: Session, playlist_id: str) -> Playlist | None:
        """Delete a playlist (cascades to its PlaylistSong rows).

        Returns:
            The deleted Playlist row, or None if no playlist had that id.
        """
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if playlist:
            db.delete(playlist)
            db.commit()
        return playlist
