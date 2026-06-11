from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, UserRole
from app.routes.dependencies import invalidate_user_cache, require_admin
from app.schemas import SongResponse, UserResponse, UserUpdate
from app.services.favorite_service import FavoriteService
from app.services.playlist_service import PlaylistService
from app.services.song_service import SongService
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["admin"])

USER_NOT_FOUND = "Usuario no encontrado"


# ── Users ──────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserResponse])
def list_users(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    search: Annotated[str | None, Query()] = None,
):
    """List all users with optional search and pagination."""
    users = UserService.get_all_users(db, skip=skip, limit=limit, search=search)
    return users


@router.get("/users/count")
def count_users(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Return total number of registered users."""
    return {"count": UserService.count_users(db)}


@router.patch("/users/{user_id}", response_model=UserResponse, responses={400: {"description": "Bad request"}, 404: {"description": "Not found"}})
def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Update user fields (username, email, role)."""
    if user_id == current_user.id and data.role is not None and data.role != UserRole.admin.value:
        raise HTTPException(status_code=400, detail="No puedes cambiarte el rol a ti mismo")

    updated = UserService.update_user(
        db,
        user_id,
        username=data.username,
        email=data.email,
        role=UserRole(data.role) if data.role else None,
    )
    if not updated:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    invalidate_user_cache(user_id)
    return updated


@router.delete("/users/{user_id}", responses={400: {"description": "Bad request"}, 404: {"description": "Not found"}})
def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete a user and all their associated data."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    if user.role == UserRole.admin:
        raise HTTPException(status_code=400, detail="No puedes eliminar a otro administrador")

    UserService.delete_user(db, user_id)
    invalidate_user_cache(user_id)
    return {"message": "Usuario eliminado"}


@router.patch("/users/{user_id}/toggle-active", responses={400: {"description": "Bad request"}, 404: {"description": "Not found"}})
def toggle_user_active(
    user_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Activate or deactivate a user account."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo")

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    invalidate_user_cache(user_id)

    return {
        "id": user.id,
        "is_active": user.is_active,
        "message": "Usuario activado" if user.is_active else "Usuario desactivado",
    }


@router.get("/users/{user_id}/stats", responses={404: {"description": "Not found"}})
def user_stats(
    user_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get statistics for a specific user."""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)

    from app.models import Playlist

    playlists_count = db.query(Playlist).filter(Playlist.user_id == user_id).count()
    favorites_count = FavoriteService.get_user_favorite_count(db, user_id)

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "stats": {
            "playlists": playlists_count,
            "favorites": favorites_count,
        },
    }


# ── Content ────────────────────────────────────────────────────────────────


@router.get("/songs", response_model=list[SongResponse])
def list_all_songs(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
):
    """List all songs from all users."""
    songs = SongService.get_all_songs(db, skip=skip, limit=limit)
    return [SongResponse.from_orm(s) for s in songs]


@router.delete("/songs/{song_id}", responses={404: {"description": "Not found"}})
def admin_delete_song(
    song_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete any song by any user."""
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    SongService.delete_song(db, song_id)
    return {"message": "Canción eliminada"}


@router.get("/playlists")
def list_all_playlists(
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
):
    """List all playlists from all users."""
    from app.models import Playlist

    playlists = db.query(Playlist).offset(skip).limit(limit).all()
    result = []
    for p in playlists:
        owner = UserService.get_user_by_id(db, p.user_id)
        result.append(
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "user_id": p.user_id,
                "username": owner.username if owner else "Unknown",
                "song_count": len(p.songs) if hasattr(p, "songs") else 0,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
        )
    return result


@router.delete("/playlists/{playlist_id}", responses={404: {"description": "Not found"}})
def admin_delete_playlist(
    playlist_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """Delete any playlist by any user."""
    playlist = PlaylistService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    PlaylistService.delete_playlist(db, playlist_id)
    return {"message": "Playlist eliminada"}
