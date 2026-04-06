from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.services.playlist_service import PlaylistService
from app.services.song_service import SongService
from app.services.user_service import UserService
from app.schemas import PlaylistCreate, PlaylistResponse, SongAddRequest

router = APIRouter(prefix="/playlists", tags=["playlists"])

def get_user_from_header(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extraer usuario del header de autorización"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = payload.get("sub") if payload else None
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.get("", response_model=list[PlaylistResponse])
def get_playlists(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Obtener playlists del usuario"""
    current_user = get_user_from_header(authorization, db)
    playlists = PlaylistService.get_user_playlists(db, current_user.id)
    return playlists

@router.post("", response_model=PlaylistResponse)
def create_playlist(
    playlist: PlaylistCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Crear nueva playlist"""
    current_user = get_user_from_header(authorization, db)
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
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Obtener detalles de una playlist"""
    current_user = get_user_from_header(authorization, db)
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
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Agregar canción a una playlist"""
    current_user = get_user_from_header(authorization, db)
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
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Eliminar canción de una playlist"""
    current_user = get_user_from_header(authorization, db)
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
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Eliminar una playlist"""
    current_user = get_user_from_header(authorization, db)
    playlist = PlaylistService.get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist no encontrada")
    
    if playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta playlist")
    
    PlaylistService.delete_playlist(db, playlist_id)
    return {"message": "Playlist eliminada"}
