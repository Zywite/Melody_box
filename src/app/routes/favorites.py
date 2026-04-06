from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models import Favorite, Song
from app.schemas import FavoriteCreate, FavoriteResponse
from app.services.user_service import UserService
import uuid

router = APIRouter(prefix="/favorites", tags=["favorites"])

def get_user_from_header(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extraer usuario del header de autorización"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")

        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error de autenticación: {str(e)}")

@router.get("", response_model=list[FavoriteResponse])
def get_favorites(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Obtener canciones favoritas del usuario"""
    current_user = get_user_from_header(authorization, db)
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favorites

@router.post("", response_model=FavoriteResponse)
def add_favorite(
    favorite: FavoriteCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Agregar canción a favoritos"""
    current_user = get_user_from_header(authorization, db)

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

    return db_favorite

@router.delete("/{song_id}")
def remove_favorite(
    song_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Eliminar canción de favoritos"""
    current_user = get_user_from_header(authorization, db)

    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.song_id == song_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Canción no encontrada en favoritos")

    db.delete(favorite)
    db.commit()

    return {"message": "Canción eliminada de favoritos"}
