import os
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.song_service import SongService
from app.schemas import YouTubeSearchResult, YouTubeDownloadRequest, SongResponse

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

QUALITY_MAP = {
    "320": "320k",
    "256": "256k",
    "128": "128k",
    "1080p": "1080",
    "720p": "720",
    "480p": "480",
}


@router.get("/search", response_model=list[YouTubeSearchResult])
async def search_youtube(q: str, limit: int = 10):
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


@router.post("/download", response_model=SongResponse)
async def download_youtube(
    request: YouTubeDownloadRequest,
    db: Session = Depends(get_db)
):
    """Download and convert a YouTube video."""
    import yt_dlp

    if request.format not in YTDLP_FORMAT_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Format not supported. Choose: {', '.join(YTDLP_FORMAT_MAP.keys())}"
        )

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

    if request.format in ['m4a', 'mp3', 'wav', 'flac', 'ogg']:
        quality = QUALITY_MAP.get(request.quality, '320k')
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': request.format if request.format != 'mp3' else 'mp3',
            'preferredquality': quality,
        }]

    video_url = f"https://www.youtube.com/watch?v={request.video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)

            title = request.title or info.get('title', 'Unknown')
            artist = request.artist or info.get('uploader', 'Unknown')
            duration = info.get('duration', 0)

            ext_map = {
                'm4a': 'm4a', 'mp3': 'mp3', 'wav': 'wav',
                'flac': 'flac', 'ogg': 'ogg', 'mp4': 'mp4',
                'mkv': 'mkv', 'webm': 'webm'
            }
            actual_ext = ext_map.get(request.format, 'm4a')

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

            db_song = SongService.create_song(
                db=db,
                title=title,
                artist=artist,
                file_path=file_path,
                duration=float(duration),
                album=None,
                media_type=media_type
            )

            return SongResponse(
                id=db_song.id,
                title=db_song.title,
                artist=db_song.artist,
                album=db_song.album,
                duration=db_song.duration,
                media_type=db_song.media_type,
                created_at=db_song.created_at
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"YouTube download error: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading: {str(e)}")