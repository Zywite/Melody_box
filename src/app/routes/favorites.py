from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Favorite, Song
from app.schemas import FavoriteCreate, FavoriteResponse
from app.routes.dependencies import get_current_user
from app.models import User
import uuid

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener canciones favoritas del usuario"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    result = []
    for f in favorites:
        song = db.query(Song).filter(Song.id == f.song_id).first()
        fav_dict = {
            "id": f.id,
            "user_id": f.user_id,
            "song_id": f.song_id,
            "added_at": f.added_at,
            "song": {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "album": song.album,
                "duration": song.duration,
                "media_type": song.media_type,
                "file_path": song.file_path
            } if song else None
        }
        result.append(fav_dict)
    return result


@router.post("", response_model=FavoriteResponse)
def add_favorite(
    favorite: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar canción a favoritos"""
    song = db.query(Song).filter(Song.id == favorite.song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.song_id == favorite.song_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="La canción ya está en favoritos")

    db_favorite = Favorite(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        song_id=favorite.song_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)

    return {
        "id": db_favorite.id,
        "user_id": db_favorite.user_id,
        "song_id": db_favorite.song_id,
        "added_at": db_favorite.added_at,
        "song": {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "duration": song.duration,
            "media_type": song.media_type,
            "file_path": song.file_path
        }
    }


@router.delete("/{song_id}")
def remove_favorite(
    song_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar canción de favoritos"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.song_id == song_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Canción no encontrada en favoritos")

    db.delete(favorite)
    db.commit()

    return {"message": "Canción eliminada de favoritos"}