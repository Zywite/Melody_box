import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.redis_helper import enqueue_job
from app.services.song_service import SongService
from app.schemas import YouTubeSearchResult, YouTubeDownloadRequest, SongResponse
from app.models.task import Task

router = APIRouter(prefix="/youtube", tags=["youtube"])

YTDLP_FORMAT_MAP = {
    "m4a": "bestaudio[ext=m4a]/bestaudio/best",
    "mp3": "bestaudio[ext=mp3]/bestaudio/best",
    "wav": "bestaudio[ext=wav]/bestaudio/best",
    "flac": "bestaudio[ext=flac]/bestaudio/best",
    "ogg": "bestaudio[ext=ogg]/bestaudio/best",
    "mp4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "mkv": "bestvideo[ext=mkv]+bestaudio[ext=m4a]/best[ext=mkv]/best",
    "webm": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
}

QUALITY_MAP = {"320": "320k", "256": "256k", "128": "128k", "1080p": "1080", "720p": "720", "480p": "480"}
AUDIO_FORMATS = {"m4a", "mp3", "wav", "flac", "ogg"}
VIDEO_FORMATS = {"mp4", "mkv", "webm"}
EXTENSION_MAP = {fmt: fmt for fmt in list(AUDIO_FORMATS) + list(VIDEO_FORMATS)}


@router.get("/search", response_model=list[YouTubeSearchResult])
@limiter.limit("10/minute")
async def search_youtube(request: Request, q: str, limit: int = 10):
    """Search for videos on YouTube."""
    import yt_dlp

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'discard_infinite',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{limit}:{q}"
            results = ydl.extract_info(search_query, download=False)

            if not results or 'entries' not in results:
                return []

            videos = []
            for entry in results['entries']:
                if entry:
                    duration = entry.get('duration', 0)
                    videos.append(YouTubeSearchResult(
                        video_id=entry.get('id', ''),
                        title=entry.get('title', 'Unknown'),
                        channel=entry.get('uploader', 'Unknown'),
                        thumbnail=entry.get('thumbnail', ''),
                        duration=duration,
                        views=entry.get('view_count')
                    ))

            return videos

    except Exception as e:
        print(f"YouTube search error: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {str(e)}")


@router.post("/download")
@limiter.limit("3/minute")
async def download_youtube(
    fastapi_request: Request,
    request: YouTubeDownloadRequest,
    db: Session = Depends(get_db)
):
    """Download and convert a YouTube video (async via worker)."""
    if request.format not in YTDLP_FORMAT_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Format not supported. Choose: {', '.join(YTDLP_FORMAT_MAP.keys())}"
        )

    # Create task record
    task = Task(
        id=str(uuid.uuid4()),
        type="youtube_download",
        status="pending",
    )
    db.add(task)
    db.commit()

    job_id = await enqueue_job(
        "download_youtube",
        request.video_id,
        request.format,
        request.quality,
        request.title,
        request.artist,
        _job_id=task.id,
    )

    if job_id:
        return {"task_id": task.id, "status": "pending"}
    else:
        # Fallback: synchronous execution
        task.status = "processing"
        db.commit()
        try:
            result = await _sync_download_youtube(request, db, task)
            return result
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")


async def _sync_download_youtube(request: YouTubeDownloadRequest, db: Session, task: Task):
    """Fallback synchronous YouTube download when no worker is available."""
    import asyncio
    import yt_dlp

    output_dir = Path(settings.MUSIC_STORAGE_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    ext = request.format if request.format in ['mp4', 'mkv', 'webm'] else f"({request.format})"
    output_template = str(output_dir / f"%(title)s_{file_id}.%(ext)s")

    ydl_opts = {
        'format': YTDLP_FORMAT_MAP[request.format],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [],
    }

    if request.format in AUDIO_FORMATS:
        quality = QUALITY_MAP.get(request.quality, '320k')
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': request.format if request.format != 'mp3' else 'mp3',
            'preferredquality': quality,
        }]

    video_url = f"https://www.youtube.com/watch?v={request.video_id}"

    def _run_ytdlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(video_url, download=True)

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _run_ytdlp)

    title = request.title or info.get('title', 'Unknown')
    artist = request.artist or info.get('uploader', 'Unknown')
    duration = info.get('duration', 0)

    actual_ext = {'m4a': 'm4a', 'mp3': 'mp3', 'wav': 'wav',
                  'flac': 'flac', 'ogg': 'ogg', 'mp4': 'mp4',
                  'mkv': 'mkv', 'webm': 'webm'}.get(request.format, 'm4a')

    original_title = info.get('title', 'video')
    safe_title = "".join(c for c in original_title if c.isalnum() or c in ' _-').strip()[:50]
    expected_file = output_dir / f"{safe_title}_{file_id}.{actual_ext}"

    downloaded_file = None
    if expected_file.exists():
        downloaded_file = expected_file
    else:
        for f in output_dir.glob(f"*{file_id}*"):
            if f.is_file():
                downloaded_file = f
                break

    if not downloaded_file:
        raise HTTPException(status_code=500, detail="Downloaded file not found")

    file_path = str(downloaded_file)
    is_video = request.format in ['mp4', 'mkv', 'webm']
    media_type = "video" if is_video else "audio"

    db_song, _ = SongService.create_song(
        db=db,
        title=title,
        artist=artist,
        file_path=file_path,
        duration=float(duration),
        album=None,
        media_type=media_type
    )

    task.status = "done"
    task.result = {"song_id": db_song.id}
    task.progress = 100
    db.commit()

    return SongResponse(
        id=db_song.id,
        title=db_song.title,
        artist=db_song.artist,
        album=db_song.album,
        duration=db_song.duration,
        media_type=db_song.media_type,
        created_at=db_song.created_at
    )
