from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import ERROR_SONG_NOT_FOUND
from app.core.database import get_db
from app.models import User
from app.routes.dependencies import get_current_user
from app.schemas import FavoriteCreate, FavoriteResponse
from app.services.favorite_service import FavoriteService

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
    favorites = FavoriteService.get_user_favorites(db, current_user.id)
    return [_format_favorite(f) for f in favorites]


@router.post("", response_model=FavoriteResponse)
def add_favorite(
    favorite: FavoriteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Agregar canción a favoritos"""
    song = FavoriteService.get_song(db, favorite.song_id)
    if not song:
        raise HTTPException(status_code=404, detail=ERROR_SONG_NOT_FOUND)

    existing = FavoriteService.get_favorite(db, current_user.id, favorite.song_id)
    if existing:
        raise HTTPException(status_code=400, detail="La canción ya está en favoritos")

    db_favorite = FavoriteService.add_favorite(db, current_user.id, favorite.song_id)
    return _format_favorite(db_favorite, song)


@router.delete("/{song_id}")
def remove_favorite(song_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Eliminar canción de favoritos"""
    favorite = FavoriteService.remove_favorite(db, current_user.id, song_id)
    if not favorite:
        raise HTTPException(status_code=404, detail="Canción no encontrada en favoritos")
    return {"message": "Canción eliminada de favoritos"}
