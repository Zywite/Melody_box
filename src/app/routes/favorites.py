import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.constants import ERROR_SONG_NOT_FOUND
from app.core.database import get_db
from app.models import Favorite, Song, User
from app.routes.dependencies import get_current_user
from app.schemas import FavoriteCreate, FavoriteResponse

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _format_favorite(fav, song=None):
    """Build the API representation of a favorite with embedded song data."""
    song_data = song or (fav.song if hasattr(fav, "song") else None)
    return {
        "id": fav.id,
        "user_id": fav.user_id,
        "song_id": fav.song_id,
        "added_at": fav.added_at,
        "song": {
            "id": song_data.id,
            "title": song_data.title,
            "artist": song_data.artist,
            "album": song_data.album,
            "duration": song_data.duration,
            "media_type": song_data.media_type,
            "file_path": song_data.file_path,
        }
        if song_data
        else None,
    }


@router.get("", response_model=list[FavoriteResponse])
def get_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtener canciones favoritas del usuario"""
    favorites = db.query(Favorite).options(joinedload(Favorite.song)).filter(Favorite.user_id == current_user.id).all()
    return [_format_favorite(f) for f in favorites]


@router.post("", response_model=FavoriteResponse)
def add_favorite(
    favorite: FavoriteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Agregar canción a favoritos"""
    song = db.query(Song).filter(Song.id == favorite.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail=ERROR_SONG_NOT_FOUND)

    existing = (
        db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.song_id == favorite.song_id).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="La canción ya está en favoritos")

    db_favorite = Favorite(id=str(uuid.uuid4()), user_id=current_user.id, song_id=favorite.song_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)

    return _format_favorite(db_favorite, song)


@router.delete("/{song_id}")
def remove_favorite(song_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Eliminar canción de favoritos"""
    favorite = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.song_id == song_id).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Canción no encontrada en favoritos")

    db.delete(favorite)
    db.commit()

    return {"message": "Canción eliminada de favoritos"}
