import os
import asyncio
import uuid
from pathlib import Path
from arq.connections import RedisSettings

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.constants import (
    TASK_STATUS_DONE,
    TASK_STATUS_FAILED,
    TASK_STATUS_PROCESSING,
    TASK_PROGRESS_COMPLETE,
    YOUTUBE_WATCH_URL_TEMPLATE,
    YOUTUBE_OUTPUT_TEMPLATE_PATTERN,
    YT_FALLBACK_TITLE,
    YT_FALLBACK_ARTIST,
    YT_FALLBACK_VIDEO_TITLE,
    ERROR_DOWNLOADED_FILE_NOT_FOUND,
)
from app.services.fft_service import FFTService
from app.services.youtube_service import (
    build_ydl_opts, resolve_downloaded_file, compute_expected_path,
    EXT_MAP, create_song_from_info,
)
from app.models.task import Task
from app.models.music import Song


async def compute_fft(ctx, song_id: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == ctx['job_id']).first()
        if task:
            task.status = TASK_STATUS_PROCESSING
            db.commit()

        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            if task:
                task.status = TASK_STATUS_FAILED
                task.error = "Song not found"
                db.commit()
            return

        await FFTService.process_and_store_fft(db, song, task)
    except Exception as e:
        if task:
            task.status = TASK_STATUS_FAILED
            task.error = str(e)
            db.commit()
    finally:
        db.close()


async def download_youtube(ctx, video_id: str, fmt: str, quality: str, title: str = None, artist: str = None):
    import yt_dlp

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == ctx['job_id']).first()
        if task:
            task.status = TASK_STATUS_PROCESSING
            db.commit()

        output_dir = Path(settings.MUSIC_STORAGE_PATH)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid.uuid4())
        output_template = str(output_dir / YOUTUBE_OUTPUT_TEMPLATE_PATTERN.format(file_id=file_id))

        ydl_opts = build_ydl_opts(fmt, quality, output_template)
        video_url = YOUTUBE_WATCH_URL_TEMPLATE.format(video_id=video_id)

        def _do_download():
            """Run the blocking yt-dlp extraction in a worker thread."""
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=True)

        info = await asyncio.to_thread(_do_download)
        actual_title = title or info.get('title', YT_FALLBACK_TITLE)
        actual_artist = artist or info.get('uploader', YT_FALLBACK_ARTIST)

        actual_ext = EXT_MAP[fmt]
        expected_file = compute_expected_path(output_dir, file_id, actual_ext, info.get('title', YT_FALLBACK_VIDEO_TITLE))
        downloaded_file = resolve_downloaded_file(output_dir, file_id, expected_file)

        if not downloaded_file:
            if task:
                task.status = TASK_STATUS_FAILED
                task.error = ERROR_DOWNLOADED_FILE_NOT_FOUND
                db.commit()
            return

        song, _ = create_song_from_info(db, info, actual_title, actual_artist, fmt, str(downloaded_file))

        if task:
            task.status = TASK_STATUS_DONE
            task.result = {"song_id": song.id}
            task.progress = TASK_PROGRESS_COMPLETE
            db.commit()

    except Exception as e:
        if task:
            task.status = TASK_STATUS_FAILED
            task.error = str(e)
            db.commit()
    finally:
        db.close()


class WorkerSettings:
    functions = [compute_fft, download_youtube]
    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        database=int(os.getenv("REDIS_DB", "0")),
    )
