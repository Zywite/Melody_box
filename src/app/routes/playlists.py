from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.playlist_service import PlaylistService
from app.services.song_service import SongService
from app.routes.dependencies import get_current_user
from app.schemas import PlaylistCreate, PlaylistResponse, SongAddRequest
from app.models import User

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("", response_model=list[PlaylistResponse])
def get_playlists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener playlists del usuario"""
    playlists = PlaylistService.get_user_playlists(db, current_user.id)
    return playlists


@router.post("", response_model=PlaylistResponse)
def create_playlist(
    playlist: PlaylistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva playlist"""
    new_playlist = PlaylistService.create_playlist(
        db,
        current_user.id,
        playlist.name,
        playlist.description
    )
    return new_playlist


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def get_playlist(
    playlist_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de una playlist"""
    playlist = PlaylistService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")
    
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta playlist")
    
    return playlist


@router.post("/{playlist_id}/songs")
def add_song_to_playlist(
    playlist_id: str,
    song_data: SongAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar canción a una playlist"""
    playlist = PlaylistService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")

    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta playlist")

    song = SongService.get_song(db, song_data.song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    PlaylistService.add_song_to_playlist(db, playlist_id, song.id)
    return {"message": "Canción agregada a la playlist"}


@router.delete("/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist(
    playlist_id: str,
    song_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar canción de una playlist"""
    playlist = PlaylistService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")
    
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta playlist")
    
    PlaylistService.remove_song_from_playlist(db, playlist_id, song_id)
    return {"message": "Canción eliminada de la playlist"}


@router.delete("/{playlist_id}")
def delete_playlist(
    playlist_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una playlist"""
    playlist = PlaylistService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")
    
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta playlist")
    
    PlaylistService.delete_playlist(db, playlist_id)
    return {"message": "Playlist eliminada"}