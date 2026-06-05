import os
import uuid
from pathlib import Path
from arq.connections import RedisSettings

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.redis_helper import cache_set_fft
from app.services.fft_service import FFTService
from app.models.task import Task
from app.models.music import Song


async def compute_fft(ctx, song_id: str):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == ctx['job_id']).first()
        if task:
            task.status = "processing"
            db.commit()

        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            if task:
                task.status = "failed"
                task.error = "Song not found"
                db.commit()
            return

        result = FFTService.compute_fft_from_file(song.file_path)
        if result:
            fft_json = FFTService.to_json(result)
            song.fft_data = fft_json
            if task:
                task.status = "done"
                task.result = result
                task.progress = 100
            db.commit()
            await cache_set_fft(song_id, fft_json)
        else:
            if task:
                task.status = "failed"
                task.error = "FFT returned no result"
                db.commit()
    except Exception as e:
        if task:
            task.status = "failed"
            task.error = str(e)
            db.commit()
    finally:
        db.close()


async def download_youtube(ctx, video_id: str, fmt: str, quality: str, title: str = None, artist: str = None):
    import yt_dlp
    from app.services.song_service import SongService

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == ctx['job_id']).first()
        if task:
            task.status = "processing"
            db.commit()

        output_dir = Path(settings.MUSIC_STORAGE_PATH)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid.uuid4())
        ext = fmt if fmt in ['mp4', 'mkv', 'webm'] else fmt
        output_template = str(output_dir / f"%(title)s_{file_id}.%(ext)s")

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

        QUALITY_MAP = {
            "320": "320k", "256": "256k", "128": "128k",
            "1080p": "1080", "720p": "720", "480p": "480",
        }

        ydl_opts = {
            'format': YTDLP_FORMAT_MAP[fmt],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [],
        }

        if fmt in ['m4a', 'mp3', 'wav', 'flac', 'ogg']:
            q = QUALITY_MAP.get(quality, '320k')
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': fmt if fmt != 'mp3' else 'mp3',
                'preferredquality': q,
            }]

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            actual_title = title or info.get('title', 'Unknown')
            actual_artist = artist or info.get('uploader', 'Unknown')
            duration = info.get('duration', 0)

            EXT_MAP = {
                'm4a': 'm4a', 'mp3': 'mp3', 'wav': 'wav',
                'flac': 'flac', 'ogg': 'ogg', 'mp4': 'mp4',
                'mkv': 'mkv', 'webm': 'webm'
            }
            actual_ext = EXT_MAP[fmt]

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
                if task:
                    task.status = "failed"
                    task.error = "Downloaded file not found"
                    db.commit()
                return

            is_video = fmt in ['mp4', 'mkv', 'webm']
            media_type = "video" if is_video else "audio"

            song, _ = SongService.create_song(
                db=db,
                title=actual_title,
                artist=actual_artist,
                file_path=str(downloaded_file),
                duration=float(duration),
                album=None,
                media_type=media_type
            )

            if task:
                task.status = "done"
                task.result = {"song_id": song.id}
                task.progress = 100
                db.commit()

    except Exception as e:
        if task:
            task.status = "failed"
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
