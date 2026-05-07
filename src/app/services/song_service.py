from sqlalchemy.orm import Session
from app.models import Song
from app.core.config import settings
import os
import uuid
import time
from pathlib import Path
from app.services.fft_service import FFTService

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
        
        # Trigger FFT analysis in background (will be done async in real app)
        # For now, compute synchronously
        try:
            start_time = time.time()
            print(f"Starting FFT analysis for: {title}")
            fft_result = FFTService.compute_fft_from_file(file_path)
            if fft_result:
                db_song.fft_data = FFTService.to_json(fft_result)
                db.commit()
                elapsed = time.time() - start_time
                print(f"FFT analysis completed for song: {title} (ID: {db_song.id})")
                print(f"FFT analysis took {elapsed:.2f}s for {title}")
                return db_song, True  # Return success flag
            else:
                print(f"FFT analysis failed: No result for {title}")
                return db_song, False
        except Exception as e:
            print(f"FFT analysis failed for {title}: {e}")
            return db_song, False

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
