import asyncio
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    DEFAULT_SONGS_PAGE_SIZE,
    DEFAULT_SONGS_PAGE_SKIP,
    ERROR_FFT_ANALYSIS_FAILED,
    ERROR_FFT_COMPUTATION_FAILED,
    ERROR_FFT_NO_RESULT,
    ERROR_FILE_NOT_FOUND,
    ERROR_FILENAME_REQUIRED,
    ERROR_INVALID_FILE_FORMAT,
    ERROR_METADATA_FILES_MISMATCH,
    ERROR_SONG_NOT_FOUND,
    ERROR_UPLOAD_PROCESSING,
    FFPROBE_TIMEOUT_SECONDS,
    JOB_NAME_COMPUTE_FFT,
    MAX_BULK_ANALYZE_BATCH,
    MAX_FILE_SIZE_BYTES,
    MAX_SEARCH_PAGE_SIZE,
    MB,
    MESSAGE_BULK_ANALYZE_RESULT,
    MIN_SEARCH_QUERY_LENGTH,
    RATE_LIMIT_ANALYZE_ALL,
    RATE_LIMIT_FFT_READ,
    RATE_LIMIT_UPLOAD,
    RATE_LIMIT_UPLOAD_MULTIPLE,
    STREAM_CACHE_MAX_AGE_SECONDS,
    SUCCESS_UPLOAD_MESSAGE,
    TASK_PROGRESS_COMPLETE,
    TASK_STATUS_DONE,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_PROCESSING,
    TASK_TYPE_FFT,
)
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.redis_helper import cache_get_fft, cache_set_fft, enqueue_job
from app.models import User
from app.routes.dependencies import get_current_user
from app.schemas import SongResponse
from app.services.fft_service import FFTService
from app.services.song_service import SongService
from app.services.task_service import TaskService

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
    """Return the media duration in seconds, or 0.0 on extraction failure.

    Audio files are decoded with librosa; video files use ffprobe.
    """
    import subprocess

    try:
        if not is_video:
            import librosa

            return librosa.get_duration(filename=file_path) or 0.0
        else:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=FFPROBE_TIMEOUT_SECONDS,
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        logger.warning("Duration extraction failed for %s: %s", file_path, e)
    return 0.0


def _write_upload_to_disk(file_path: str, source_file) -> None:
    with open(file_path, "wb") as f:
        shutil.copyfileobj(source_file, f)


async def _process_upload_file(
    db: Session,
    file: UploadFile,
    title: str,
    artist: str,
    album: str,
) -> dict:
    """Persist a single uploaded file and enqueue its FFT job.

    Raises:
        HTTPException: 400 on invalid filename/extension; 500 on IO errors
            after the partial file has been cleaned up.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail=ERROR_FILENAME_REQUIRED)

    safe_filename = Path(file.filename).name
    if safe_filename.startswith("-"):
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_ext = Path(safe_filename).suffix.lower().lstrip(".")
    allowed_exts = settings.get_allowed_extensions()
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=ERROR_INVALID_FILE_FORMAT.format(filename=file.filename, extensions=", ".join(allowed_exts)),
        )

    is_video = settings.is_video(file_ext)
    media_type = "video" if is_video else "audio"

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande. Máximo permitido: {MAX_FILE_SIZE_BYTES // MB}MB",
        )

    os.makedirs(settings.MUSIC_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.MUSIC_STORAGE_PATH, safe_filename)

    try:
        await asyncio.to_thread(_write_upload_to_disk, file_path, file.file)

        duration = _extract_duration(file_path, is_video)

        song, _ = SongService.create_song(db, title, artist, file_path, duration, album, media_type)

        task_id = None
        try:
            task = TaskService.create_task(db, TASK_TYPE_FFT, TASK_STATUS_PENDING, song_id=song.id)
            job_id = await enqueue_job(JOB_NAME_COMPUTE_FFT, song.id, _job_id=task.id)
            if job_id:
                task_id = task.id
            else:
                task.status = TASK_STATUS_FAILED
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
        raise HTTPException(
            status_code=500, detail=ERROR_UPLOAD_PROCESSING.format(filename=file.filename, error=str(e))
        ) from e


@router.get("", response_model=list[SongResponse])
def get_all_songs(
    db: Annotated[Session, Depends(get_db)],
    skip: int = DEFAULT_SONGS_PAGE_SKIP,
    limit: int = DEFAULT_SONGS_PAGE_SIZE,
):
    """List songs with pagination."""
    songs = SongService.get_all_songs(db, skip, limit)
    return [SongResponse.from_orm(song) for song in songs]


@router.get("/search", response_model=list[SongResponse])
def search_songs(
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=MIN_SEARCH_QUERY_LENGTH)],
    skip: Annotated[int, Query(ge=0)] = DEFAULT_SONGS_PAGE_SKIP,
    limit: Annotated[int, Query(ge=1, le=MAX_SEARCH_PAGE_SIZE)] = DEFAULT_SONGS_PAGE_SIZE,
):
    """Case-insensitive search over title, artist, and album."""
    songs = SongService.search_songs(db, q, skip=skip, limit=limit)
    return [SongResponse.from_orm(song) for song in songs]


@router.get("/{song_id}", response_model=SongResponse, responses={404: {"description": "Song not found"}})
def get_song(song_id: str, db: Annotated[Session, Depends(get_db)]):
    """Fetch a single song by id."""
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=ERROR_SONG_NOT_FOUND)
    return SongResponse.from_orm(song)


@router.get("/{song_id}/stream", responses={404: {"description": "Song or file not found"}})
def stream_song(song_id: str, db: Annotated[Session, Depends(get_db)]):
    """Stream the audio/video bytes of a song with range support and 1h cache."""
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=ERROR_SONG_NOT_FOUND)

    file_path = str(Path(song.file_path).resolve())
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=ERROR_FILE_NOT_FOUND.format(file_path=file_path))

    ext = Path(file_path).suffix.lower().lstrip(".")
    media_type = MIME_TYPES.get(ext, "application/octet-stream")

    return FileResponse(
        file_path,
        media_type=media_type,
        headers={"Accept-Ranges": "bytes", "Cache-Control": f"public, max-age={STREAM_CACHE_MAX_AGE_SECONDS}"},
    )


@router.post(
    "/upload", responses={400: {"description": "Invalid file"}, 500: {"description": "Upload processing error"}}
)
@limiter.limit(RATE_LIMIT_UPLOAD)
async def upload_song(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
    title: Annotated[str, Form(...)],
    artist: Annotated[str, Form(...)],
    album: Annotated[str, Form()] = "",
):
    """Upload a single song. Rate limited to 10/minute."""
    result = await _process_upload_file(db, file, title, artist, album)
    result["message"] = SUCCESS_UPLOAD_MESSAGE + (
        f" (FFT en cola, tarea: {result['fft_task_id']})" if result["fft_task_id"] else ""
    )
    return result


@router.post(
    "/upload-multiple",
    responses={
        400: {"description": "Invalid file or metadata mismatch"},
        500: {"description": "Upload processing error"},
    },
)
@limiter.limit(RATE_LIMIT_UPLOAD_MULTIPLE)
async def upload_multiple(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    files: Annotated[list[UploadFile], File(...)],
    metadata: Annotated[str, Form(...)],
):
    """Upload many songs in one request. Rate limited to 5/minute.

    Each file is processed in its own savepoint so a single failure does
    not abort the whole batch.
    """
    metadata_list = json.loads(metadata)
    if len(files) != len(metadata_list):
        raise HTTPException(status_code=400, detail=ERROR_METADATA_FILES_MISMATCH)

    results = []
    errors = []

    for i, (file, meta) in enumerate(zip(files, metadata_list, strict=False)):
        try:
            result = await _process_upload_file(db, file, meta["title"], meta["artist"], meta.get("album", ""))
            results.append(result)
        except HTTPException as e:
            db.rollback()
            errors.append({"index": i, "filename": file.filename or f"file_{i}", "error": e.detail})
        except Exception as e:
            db.rollback()
            errors.append({"index": i, "filename": file.filename or f"file_{i}", "error": str(e)})

    return {
        "results": results,
        "total": len(files),
        "success_count": len(results),
        "error_count": len(errors),
        "errors": errors,
    }


@router.delete("/{song_id}", responses={404: {"description": "Song not found"}})
def delete_song(
    song_id: str, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
):
    """Delete a song row and its underlying file on disk."""
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=ERROR_SONG_NOT_FOUND)

    SongService.delete_song(db, song_id)
    return {"message": "Canción eliminada"}


@router.get(
    "/{song_id}/fft", responses={404: {"description": "Song not found"}, 500: {"description": "FFT computation error"}}
)
@limiter.limit(RATE_LIMIT_FFT_READ)
async def get_song_fft(request: Request, song_id: str, db: Annotated[Session, Depends(get_db)]):
    """Get FFT analysis for a song. Enqueues computation if not available."""
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail=ERROR_SONG_NOT_FOUND)

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
    existing_task = TaskService.get_pending_fft_task(db, song_id)
    if existing_task:
        return {"task_id": existing_task.id, "status": existing_task.status}

    # Create task and enqueue
    task = TaskService.create_task(db, TASK_TYPE_FFT, TASK_STATUS_PENDING, song_id=song_id)

    job_id = await enqueue_job(JOB_NAME_COMPUTE_FFT, song_id, _job_id=task.id)
    if job_id:
        return {"task_id": task.id, "status": TASK_STATUS_PENDING}
    else:
        # Fallback: compute synchronously
        task.status = TASK_STATUS_PROCESSING
        db.commit()
        try:
            fft_result = await asyncio.to_thread(FFTService.compute_fft_from_file, song.file_path)
            if fft_result:
                fft_json = FFTService.to_json(fft_result)
                song.fft_data = fft_json
                task.status = TASK_STATUS_DONE
                task.result = fft_result
                task.progress = TASK_PROGRESS_COMPLETE
                db.commit()
                await cache_set_fft(song_id, fft_json)
                return JSONResponse(content=fft_result)
            else:
                task.status = TASK_STATUS_FAILED
                task.error = ERROR_FFT_NO_RESULT
                db.commit()
                raise HTTPException(status_code=500, detail=ERROR_FFT_COMPUTATION_FAILED)
        except Exception as e:
            task.status = TASK_STATUS_FAILED
            task.error = str(e)
            db.commit()
            raise HTTPException(status_code=500, detail=ERROR_FFT_ANALYSIS_FAILED.format(error=str(e))) from e


@router.post("/analyze-all")
@limiter.limit(RATE_LIMIT_ANALYZE_ALL)
async def analyze_all_songs_fft(
    request: Request, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
):
    """Enqueue an FFT job for every song that still lacks analysis.

    This no longer blocks the request thread. Each song gets its own
    ``Task`` row (used as the arq ``_job_id``) and is dispatched to the
    arq worker, so the route returns immediately. Progress is polled via
    the existing ``/tasks/{id}`` endpoint.
    """
    songs = SongService.get_all_songs(db, limit=MAX_BULK_ANALYZE_BATCH)
    enqueued = 0
    failed = 0

    for song in songs:
        if song.fft_data:
            continue
        try:
            task = TaskService.create_task(db, TASK_TYPE_FFT, TASK_STATUS_PENDING, song_id=song.id)
            job_id = await enqueue_job(JOB_NAME_COMPUTE_FFT, song.id, _job_id=task.id)
            if job_id:
                enqueued += 1
            else:
                task.status = TASK_STATUS_FAILED
                task.error = "Worker not available"
                db.commit()
                failed += 1
        except Exception as e:
            logger.error("Failed to enqueue FFT for song %s: %s", song.id, e)
            failed += 1

    return {
        "message": MESSAGE_BULK_ANALYZE_RESULT.format(analyzed=enqueued, failed=failed),
        "enqueued": enqueued,
        "failed": failed,
    }
