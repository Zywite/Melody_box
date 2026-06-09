from pathlib import Path

from sqlalchemy.orm import Session

from app.services.song_service import SongService

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

AUDIO_FORMATS = {"m4a", "mp3", "wav", "flac", "ogg"}
VIDEO_FORMATS = {"mp4", "mkv", "webm"}

EXT_MAP = {
    "m4a": "m4a",
    "mp3": "mp3",
    "wav": "wav",
    "flac": "flac",
    "ogg": "ogg",
    "mp4": "mp4",
    "mkv": "mkv",
    "webm": "webm",
}

TITLE_MAX_LENGTH = 50


def build_ydl_opts(fmt: str, quality: str, output_template: str) -> dict:
    """Build the yt_dlp options dict for a given format and quality preset."""
    opts = {
        "format": YTDLP_FORMAT_MAP[fmt],
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [],
    }
    if fmt in AUDIO_FORMATS:
        quality_kbps = QUALITY_MAP.get(quality, "320k")
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt if fmt != "mp3" else "mp3",
                "preferredquality": quality_kbps,
            }
        ]
    return opts


def resolve_downloaded_file(output_dir: Path, file_id: str, expected_file: Path) -> Path | None:
    """Return the expected file if it exists, otherwise glob for a fallback."""
    if expected_file.exists():
        return expected_file
    for f in output_dir.glob(f"*{file_id}*"):
        if f.is_file():
            return f
    return None


def compute_expected_path(output_dir: Path, file_id: str, actual_ext: str, original_title: str) -> Path:
    """Compute the canonical output path for a downloaded YouTube file."""
    safe_title = sanitize_title(original_title)
    return output_dir / f"{safe_title}_{file_id}.{actual_ext}"


def sanitize_title(title: str) -> str:
    """Sanitize a YouTube title for use as a filesystem-safe prefix."""
    safe = "".join(c for c in title if c.isalnum() or c in " _-").strip()
    return safe[:TITLE_MAX_LENGTH]


def create_song_from_info(db: Session, info: dict, title: str, artist: str, fmt: str, file_path: str) -> tuple:
    """Persist a Song row from a yt_dlp ``info`` dict and the saved file path."""
    duration = info.get("duration", 0)
    is_video = fmt in VIDEO_FORMATS
    media_type = "video" if is_video else "audio"
    return SongService.create_song(
        db=db,
        title=title,
        artist=artist,
        file_path=file_path,
        duration=float(duration),
        album=None,
        media_type=media_type,
    )
