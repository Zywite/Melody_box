from sqlalchemy.orm import Session
from app.models import Playlist, PlaylistSong, Song
import uuid

class PlaylistService:
    @staticmethod
    def create_playlist(db: Session, user_id: str, name: str, description: str = None):
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
    def get_playlist(db: Session, playlist_id: str):
        return db.query(Playlist).filter(Playlist.id == playlist_id).first()

    @staticmethod
    def get_user_playlists(db: Session, user_id: str):
        return db.query(Playlist).filter(Playlist.user_id == user_id).all()

    @staticmethod
    def add_song_to_playlist(db: Session, playlist_id: str, song_id: str):
        # Verificar que la canción no esté ya en la playlist
        existing = db.query(PlaylistSong).filter(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        ).first()
        
        if existing:
            return existing

        # Obtener la posición
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
    def remove_song_from_playlist(db: Session, playlist_id: str, song_id: str):
        db_playlist_song = db.query(PlaylistSong).filter(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        ).first()
        
        if db_playlist_song:
            db.delete(db_playlist_song)
            db.commit()
        
        return db_playlist_song

    @staticmethod
    def delete_playlist(db: Session, playlist_id: str):
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if playlist:
            db.delete(playlist)
            db.commit()
        return playlist
