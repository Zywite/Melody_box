import os
import json
import logging
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.redis_helper import enqueue_job, cache_get_fft, cache_set_fft
from app.services.song_service import SongService
from app.services.fft_service import FFTService
from app.schemas import SongResponse
from app.routes.dependencies import get_current_user
from app.models import User
from app.models.task import Task

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


logger = logging.getLogger(__name__)

def _extract_duration(file_path: str, is_video: bool) -> float:
    try:
        if not is_video:
            import librosa
            return librosa.get_duration(filename=file_path) or 0.0
        else:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", file_path],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
    except Exception as e:
        logger.warning("Duration extraction failed for %s: %s", file_path, e)
    return 0.0


async def _process_upload_file(
    db: Session,
    file: UploadFile,
    title: str,
    artist: str,
    album: str,
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")

    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    allowed_exts = settings.get_allowed_extensions()
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido: {file.filename}. Formatos soportados: {', '.join(allowed_exts)}"
        )

    is_video = settings.is_video(file_ext)
    media_type = "video" if is_video else "audio"

    os.makedirs(settings.MUSIC_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.MUSIC_STORAGE_PATH, file.filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        duration = _extract_duration(file_path, is_video)

        song, _ = SongService.create_song(db, title, artist, file_path, duration, album, media_type)

        task_id = None
        try:
            task = Task(id=str(uuid.uuid4()), type="fft", status="pending", song_id=song.id)
            db.add(task)
            db.commit()
            job_id = await enqueue_job("compute_fft", song.id, _job_id=task.id)
            if job_id:
                task_id = task.id
            else:
                task.status = "failed"
                task.error = "Worker not available"
                db.commit()
        except Exception as e:
            logger.error("FFT enqueue failed for song %s: %s", song.id, e)

        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "album": song.album,
            "duration": song.duration,
            "media_type": song.media_type,
            "fft_ready": False,
            "fft_task_id": task_id,
        }
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error al procesar {file.filename}: {str(e)}")


@router.get("", response_model=list[SongResponse])
def get_all_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    songs = SongService.get_all_songs(db, skip, limit)
    return [SongResponse.from_orm(song) for song in songs]


@router.get("/search", response_model=list[SongResponse])
def search_songs(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    songs = SongService.search_songs(db, q)
    return [SongResponse.from_orm(song) for song in songs]


@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: str, db: Session = Depends(get_db)):
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return SongResponse.from_orm(song)


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
@limiter.limit("10/minute")
async def upload_song(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await _process_upload_file(db, file, title, artist, album)
    result["message"] = "Archivo subido exitosamente" + (f" (FFT en cola, tarea: {result['fft_task_id']})" if result['fft_task_id'] else "")
    return result


@router.post("/upload-multiple")
@limiter.limit("5/minute")
async def upload_multiple(
    request: Request,
    files: list[UploadFile] = File(...),
    metadata: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metadata_list = json.loads(metadata)
    if len(files) != len(metadata_list):
        raise HTTPException(status_code=400, detail="Number of files and metadata entries must match")

    results = []
    errors = []

    for i, (file, meta) in enumerate(zip(files, metadata_list)):
        savepoint = db.begin_nested()
        try:
            result = await _process_upload_file(
                db, file, meta["title"], meta["artist"], meta.get("album", "")
            )
            results.append(result)
        except HTTPException as e:
            db.rollback()
            errors.append({
                "index": i,
                "filename": file.filename or f"file_{i}",
                "error": e.detail
            })
        except Exception as e:
            db.rollback()
            errors.append({
                "index": i,
                "filename": file.filename or f"file_{i}",
                "error": str(e)
            })

    return {
        "results": results,
        "total": len(files),
        "success_count": len(results),
        "error_count": len(errors),
        "errors": errors
    }


@router.delete("/{song_id}")
def delete_song(
    song_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    
    SongService.delete_song(db, song_id)
    return {"message": "Canción eliminada"}


@router.get("/{song_id}/fft")
@limiter.limit("30/minute")
async def get_song_fft(request: Request, song_id: str, db: Session = Depends(get_db)):
    """Get FFT analysis for a song. Enqueues computation if not available."""
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    
    # Try Redis cache first (fastest)
    cached = await cache_get_fft(song_id)
    if cached:
        return JSONResponse(content=json.loads(cached))

    # Return existing FFT data from DB
    if song.fft_data:
        fft_json = FFTService.get_fft_data_json(song.fft_data)
        if fft_json:
            await cache_set_fft(song_id, song.fft_data)
            return JSONResponse(content=fft_json)
    
    # Check for existing pending/processing task
    existing_task = db.query(Task).filter(
        Task.song_id == song_id,
        Task.type == "fft",
        Task.status.in_(["pending", "processing"])
    ).first()
    if existing_task:
        return {"task_id": existing_task.id, "status": existing_task.status}
    
    # Create task and enqueue
    task = Task(id=str(uuid.uuid4()), type="fft", status="pending", song_id=song_id)
    db.add(task)
    db.commit()
    
    job_id = await enqueue_job("compute_fft", song_id, _job_id=task.id)
    if job_id:
        return {"task_id": task.id, "status": "pending"}
    else:
        # Fallback: compute synchronously
        task.status = "processing"
        db.commit()
        try:
            fft_result = FFTService.compute_fft_from_file(song.file_path)
            if fft_result:
                fft_json = FFTService.to_json(fft_result)
                song.fft_data = fft_json
                task.status = "done"
                task.result = fft_result
                task.progress = 100
                db.commit()
                await cache_set_fft(song_id, fft_json)
                return JSONResponse(content=fft_result)
            else:
                task.status = "failed"
                task.error = "FFT returned no result"
                db.commit()
                raise HTTPException(status_code=500, detail="Failed to compute FFT")
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            db.commit()
            raise HTTPException(status_code=500, detail=f"FFT analysis failed: {str(e)}")


@router.post("/analyze-all")
@limiter.limit("2/minute")
def analyze_all_songs_fft(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analyze all songs that don't have FFT data yet."""
    songs = SongService.get_all_songs(db, limit=1000)
    analyzed = 0
    failed = 0
    
    for song in songs:
        if not song.fft_data:
            try:
                fft_result = FFTService.compute_fft_from_file(song.file_path)
                if fft_result:
                    song.fft_data = FFTService.to_json(fft_result)
                    analyzed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    
    db.commit()
    return {"message": f"Analyzed {analyzed} songs, {failed} failed"}
