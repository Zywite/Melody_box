import logging
import uuid
from pathlib import Path
from typing import Annotated

import yt_dlp
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    DEFAULT_YOUTUBE_SEARCH_RESULTS,
    ERROR_DOWNLOADED_FILE_NOT_FOUND,
    JOB_NAME_DOWNLOAD_YOUTUBE,
    RATE_LIMIT_YT_DOWNLOAD,
    RATE_LIMIT_YT_SEARCH,
    TASK_PROGRESS_COMPLETE,
    TASK_STATUS_DONE,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_PROCESSING,
    TASK_TYPE_YOUTUBE_DOWNLOAD,
    YOUTUBE_OUTPUT_TEMPLATE_PATTERN,
    YOUTUBE_WATCH_URL_TEMPLATE,
    YT_FALLBACK_ARTIST,
    YT_FALLBACK_TITLE,
    YT_FALLBACK_VIDEO_TITLE,
)
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.redis_helper import enqueue_job
from app.models.task import Task
from app.schemas import SongResponse, YouTubeDownloadRequest, YouTubeSearchResult
from app.services.task_service import TaskService
from app.services.youtube_service import (
    EXT_MAP,
    YTDLP_FORMAT_MAP,
    build_ydl_opts,
    compute_expected_path,
    create_song_from_info,
    resolve_downloaded_file,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])


@router.get("/search", response_model=list[YouTubeSearchResult])
@limiter.limit(RATE_LIMIT_YT_SEARCH)
async def search_youtube(request: Request, q: str, limit: int = DEFAULT_YOUTUBE_SEARCH_RESULTS):
    """Search for videos on YouTube."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "discard_infinite",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{limit}:{q}"
            results = ydl.extract_info(search_query, download=False)

            if not results or "entries" not in results:
                return []

            videos = []
            for entry in results["entries"]:
                if entry:
                    duration = entry.get("duration", 0)
                    videos.append(
                        YouTubeSearchResult(
                            video_id=entry.get("id", ""),
                            title=entry.get("title", YT_FALLBACK_TITLE),
                            channel=entry.get("uploader", YT_FALLBACK_ARTIST),
                            thumbnail=entry.get("thumbnail", ""),
                            duration=duration,
                            views=entry.get("view_count"),
                        )
                    )

            return videos

    except (yt_dlp.utils.YoutubeDLError, OSError) as e:
        logger.error("YouTube search error: %s", e)
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {str(e)}") from e


@router.post("/download")
@limiter.limit(RATE_LIMIT_YT_DOWNLOAD)
async def download_youtube(
    fastapi_request: Request, request: YouTubeDownloadRequest, db: Annotated[Session, Depends(get_db)]
):
    """Download and convert a YouTube video (async via worker)."""
    if request.format not in YTDLP_FORMAT_MAP:
        raise HTTPException(
            status_code=400, detail=f"Format not supported. Choose: {', '.join(YTDLP_FORMAT_MAP.keys())}"
        )

    # Create task record
    task = TaskService.create_task(db, TASK_TYPE_YOUTUBE_DOWNLOAD, TASK_STATUS_PENDING)

    job_id = await enqueue_job(
        JOB_NAME_DOWNLOAD_YOUTUBE,
        request.video_id,
        request.format,
        request.quality,
        request.title,
        request.artist,
        _job_id=task.id,
    )

    if job_id:
        return {"task_id": task.id, "status": TASK_STATUS_PENDING}

    task.status = TASK_STATUS_PROCESSING
    db.commit()
    try:
        return await _sync_download_youtube(request, db, task)
    except (OSError, ValueError, SQLAlchemyError, yt_dlp.utils.YoutubeDLError) as e:
        task.status = TASK_STATUS_FAILED
        task.error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}") from e


async def _sync_download_youtube(request: YouTubeDownloadRequest, db: Session, task: Task):
    """Fallback synchronous YouTube download when no worker is available."""
    import asyncio

    output_dir = Path(settings.MUSIC_STORAGE_PATH)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    output_template = str(output_dir / YOUTUBE_OUTPUT_TEMPLATE_PATTERN.format(file_id=file_id))

    ydl_opts = build_ydl_opts(request.format, request.quality, output_template)
    video_url = YOUTUBE_WATCH_URL_TEMPLATE.format(video_id=request.video_id)

    def _run_ytdlp():
        """Blocking yt_dlp call run in the default executor."""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(video_url, download=True)

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _run_ytdlp)

    title = request.title or info.get("title", YT_FALLBACK_TITLE)
    artist = request.artist or info.get("uploader", YT_FALLBACK_ARTIST)

    actual_ext = EXT_MAP[request.format]
    expected_file = compute_expected_path(output_dir, file_id, actual_ext, info.get("title", YT_FALLBACK_VIDEO_TITLE))
    downloaded_file = resolve_downloaded_file(output_dir, file_id, expected_file)

    if not downloaded_file:
        raise HTTPException(status_code=500, detail=ERROR_DOWNLOADED_FILE_NOT_FOUND)

    db_song, _ = create_song_from_info(db, info, title, artist, request.format, str(downloaded_file))

    task.status = TASK_STATUS_DONE
    task.result = {"song_id": db_song.id}
    task.progress = TASK_PROGRESS_COMPLETE
    db.commit()

    return SongResponse(
        id=db_song.id,
        title=db_song.title,
        artist=db_song.artist,
        album=db_song.album,
        duration=db_song.duration,
        media_type=db_song.media_type,
        created_at=db_song.created_at,
    )
