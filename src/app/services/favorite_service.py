"""Favorite service: persistence operations for Favorite entities."""

import uuid

from sqlalchemy.orm import Session, joinedload

from app.models import Favorite, Song


class FavoriteService:
    """Static methods for creating, querying, and removing favorites."""

    @staticmethod
    def get_user_favorites(db: Session, user_id: str) -> list[Favorite]:
        """Return all favorites for a user, eagerly loading the related song."""
        return db.query(Favorite).options(joinedload(Favorite.song)).filter(Favorite.user_id == user_id).all()

    @staticmethod
    def get_favorite(db: Session, user_id: str, song_id: str) -> Favorite | None:
        """Return a single favorite row for a user + song pair, or None."""
        return db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.song_id == song_id).first()

    @staticmethod
    def add_favorite(db: Session, user_id: str, song_id: str) -> Favorite:
        """Create and persist a new favorite."""
        db_favorite = Favorite(
            id=str(uuid.uuid4()),
            user_id=user_id,
            song_id=song_id,
        )
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        return db_favorite

    @staticmethod
    def remove_favorite(db: Session, user_id: str, song_id: str) -> Favorite | None:
        """Delete a favorite (idempotent). Returns the deleted row or None."""
        favorite = FavoriteService.get_favorite(db, user_id, song_id)
        if favorite:
            db.delete(favorite)
            db.commit()
        return favorite

    @staticmethod
    def get_song(db: Session, song_id: str) -> Song | None:
        """Look up a song by primary key (convenience wrapper)."""
        return db.query(Song).filter(Song.id == song_id).first()

    @staticmethod
    def get_user_favorite_count(db: Session, user_id: str) -> int:
        """Return the number of favorites for a user."""
        return db.query(Favorite).filter(Favorite.user_id == user_id).count()
