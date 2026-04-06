from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query, Header, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.song_service import SongService
from app.schemas import SongResponse
import os
from pathlib import Path

router = APIRouter(prefix="/songs", tags=["songs"])

MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "flac": "audio/flac",
    "ogg": "audio/ogg",
    "m4a": "audio/mp4",
    "mp4": "video/mp4",
    "mkv": "video/x-matroska",
    "avi": "video/x-msvideo",
    "webm": "video/webm",
    "mov": "video/quicktime",
}

@router.get("", response_model=list[SongResponse])
def get_all_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    songs = SongService.get_all_songs(db, skip, limit)
    return songs

@router.get("/search", response_model=list[SongResponse])
def search_songs(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    songs = SongService.search_songs(db, q)
    return songs

@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: str, db: Session = Depends(get_db)):
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return song

@router.get("/{song_id}/stream")
def stream_song(song_id: str, db: Session = Depends(get_db)):
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    file_path = str(Path(song.file_path).resolve())
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {file_path}")

    ext = Path(file_path).suffix.lower().lstrip(".")
    media_type = MIME_TYPES.get(ext, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type, headers={
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=3600"
    })

@router.post("/upload")
async def upload_song(
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(""),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    try:
        token = authorization.replace("Bearer ", "")
        from app.core.security import decode_token
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")

    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    allowed_exts = settings.get_allowed_extensions()
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Formatos soportados: {', '.join(allowed_exts)}"
        )

    is_video = settings.is_video(file_ext)
    media_type = "video" if is_video else "audio"

    os.makedirs(settings.MUSIC_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.MUSIC_STORAGE_PATH, file.filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        duration = 0.0
        try:
            if not is_video:
                try:
                    import librosa
                    duration = librosa.get_duration(filename=file_path) or 0.0
                except Exception:
                    duration = 0.0
            else:
                try:
                    import subprocess
                    result = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", file_path],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        duration = float(result.stdout.strip())
                except Exception:
                    duration = 0.0
        except Exception:
            duration = 0.0

        song = SongService.create_song(db, title, artist, file_path, duration, album, media_type)

        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "duration": song.duration,
            "media_type": song.media_type,
            "message": "Archivo subido exitosamente"
        }

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error al subir el archivo: {str(e)}")

@router.delete("/{song_id}")
def delete_song(song_id: str, authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    SongService.delete_song(db, song_id)
    return {"message": "Canción eliminada"}
