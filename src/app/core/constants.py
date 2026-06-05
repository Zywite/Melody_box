"""Application-wide constants for task statuses, job types, error messages,
rate limits, cache TTLs, and FFT parameters.

Centralizing these values prevents drift between modules and makes it
trivial to retune the system from a single location.
"""

# ---------------------------------------------------------------------------
# Task lifecycle
# ---------------------------------------------------------------------------
TASK_STATUS_PENDING: str = "pending"
TASK_STATUS_PROCESSING: str = "processing"
TASK_STATUS_DONE: str = "done"
TASK_STATUS_FAILED: str = "failed"

TASK_TYPE_FFT: str = "fft"
TASK_TYPE_YOUTUBE_DOWNLOAD: str = "youtube_download"

JOB_NAME_COMPUTE_FFT: str = "compute_fft"
JOB_NAME_DOWNLOAD_YOUTUBE: str = "download_youtube"

TASK_PROGRESS_COMPLETE: int = 100

# ---------------------------------------------------------------------------
# Error messages (Spanish, used in HTTP responses)
# ---------------------------------------------------------------------------
ERROR_SONG_NOT_FOUND: str = "Canción no encontrada"
ERROR_PLAYLIST_NOT_FOUND: str = "Playlist no encontrada"
ERROR_FILENAME_REQUIRED: str = "Nombre de archivo requerido"
ERROR_FILE_NOT_FOUND: str = "Archivo no encontrado: {file_path}"
ERROR_METADATA_FILES_MISMATCH: str = "Number of files and metadata entries must match"
ERROR_TOKEN_INVALID: str = "Token inválido"
ERROR_TASK_NOT_FOUND: str = "Task not found"
ERROR_PLAYLIST_FORBIDDEN: str = "No tienes permiso para realizar esta accion"
ERROR_INTERNAL_SERVER: str = "Error interno del servidor"
ERROR_FFT_COMPUTATION_FAILED: str = "Failed to compute FFT"
ERROR_FFT_NO_RESULT: str = "FFT returned no result"
ERROR_DOWNLOADED_FILE_NOT_FOUND: str = "Downloaded file not found"
ERROR_FFT_ANALYSIS_FAILED: str = "FFT analysis failed: {error}"
ERROR_UPLOAD_PROCESSING: str = "Error al procesar {filename}: {error}"
ERROR_INVALID_FILE_FORMAT: str = "Formato no permitido: {filename}. Formatos soportados: {extensions}"

# ---------------------------------------------------------------------------
# Success messages
# ---------------------------------------------------------------------------
SUCCESS_UPLOAD_MESSAGE: str = "Archivo subido exitosamente"
MESSAGE_BULK_ANALYZE_RESULT: str = "Analyzed {analyzed} songs, {failed} failed"

# ---------------------------------------------------------------------------
# Rate-limit strings (slowapi format)
# ---------------------------------------------------------------------------
RATE_LIMIT_REGISTER: str = "3/minute"
RATE_LIMIT_LOGIN: str = "5/minute"
RATE_LIMIT_UPLOAD: str = "10/minute"
RATE_LIMIT_UPLOAD_MULTIPLE: str = "5/minute"
RATE_LIMIT_FFT_READ: str = "30/minute"
RATE_LIMIT_ANALYZE_ALL: str = "2/minute"
RATE_LIMIT_YT_SEARCH: str = "10/minute"
RATE_LIMIT_YT_DOWNLOAD: str = "3/minute"

# ---------------------------------------------------------------------------
# Cache TTLs (seconds)
# ---------------------------------------------------------------------------
FFT_CACHE_TTL_SECONDS: int = 86400  # 24h
STREAM_CACHE_MAX_AGE_SECONDS: int = 3600  # 1h
STATIC_CACHE_MAX_AGE_SECONDS: int = 31536000  # 1y

FFT_CACHE_KEY_PREFIX: str = "fft:"

# ---------------------------------------------------------------------------
# Pagination defaults
# ---------------------------------------------------------------------------
DEFAULT_SONGS_PAGE_SIZE: int = 100
DEFAULT_SONGS_PAGE_SKIP: int = 0
DEFAULT_YOUTUBE_SEARCH_RESULTS: int = 10
MAX_BULK_ANALYZE_BATCH: int = 1000
MIN_SEARCH_QUERY_LENGTH: int = 1

# ---------------------------------------------------------------------------
# Pagination: search defaults
# ---------------------------------------------------------------------------
FFPROBE_TIMEOUT_SECONDS: int = 10

# ---------------------------------------------------------------------------
# FFT parameters
# ---------------------------------------------------------------------------
DEFAULT_FFT_SIZE: int = 2048
DEFAULT_FFT_HOP_SIZE: int = 512
MAX_SPECTROGRAM_FRAMES: int = 200
FFT_NORMALIZATION_RANGE: int = 255
FFT_NORMALIZATION_EPSILON: float = 1e-10
POWER_PERCENT_MULTIPLIER: int = 100
BASS_FREQUENCY_CUTOFF_HZ: int = 250
MID_FREQUENCY_CUTOFF_HZ: int = 2000

# ---------------------------------------------------------------------------
# YouTube defaults
# ---------------------------------------------------------------------------
YOUTUBE_WATCH_URL_TEMPLATE: str = "https://www.youtube.com/watch?v={video_id}"
YOUTUBE_OUTPUT_TEMPLATE_PATTERN: str = "%(title)s_{file_id}.%(ext)s"
YT_FALLBACK_TITLE: str = "Unknown"
YT_FALLBACK_ARTIST: str = "Unknown"
YT_FALLBACK_VIDEO_TITLE: str = "video"
DEFAULT_AUDIO_BITRATE: str = "320k"
DEFAULT_AUDIO_QUALITY_KEY: str = "high"

# ---------------------------------------------------------------------------
# Database retry policy
# ---------------------------------------------------------------------------
DB_RETRY_MAX_ATTEMPTS: int = 3
DB_RETRY_BACKOFF_SECONDS: int = 2
GZIP_MINIMUM_SIZE_BYTES: int = 1000
