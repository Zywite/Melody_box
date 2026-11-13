import logging
import secrets
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Project root is 3 levels up: src/app/core/config.py -> core -> app -> src -> project root
BASE_DIR = Path(__file__).parents[3]

# Placeholder values that ship in compose/docs and must never sign real tokens.
INSECURE_SECRET_KEYS = frozenset({"change-me-in-production", "changeme", "secret", "secret-key"})
MIN_SECRET_KEY_LENGTH = 32
PRODUCTION_ENVIRONMENTS = frozenset({"production", "prod"})


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/spotify_local.db"

    # Environment
    APP_ENV: str = "development"

    # API
    API_TITLE: str = "MelodyBox API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para reproductor de música local en red"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # NOSONAR - safe default, override via .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_PASSWORD: str = ""

    # Media storage (absolute path) - files are in data/music after reorganization
    MUSIC_STORAGE_PATH: str = str(BASE_DIR / "data" / "music")
    ALLOWED_AUDIO_EXTENSIONS: str = "mp3,wav,flac,ogg,m4a"
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,mkv,avi,webm,mov"

    # Redis / Worker
    REDIS_URL: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8001"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8")

    @model_validator(mode="after")
    def _validate_secret_key(self) -> "Settings":
        """Fail fast on a missing or placeholder SECRET_KEY in production.

        Without this, a deployment can silently sign JWTs with the
        ``change-me-in-production`` placeholder on the compose file -- or, when
        the variable is absent, with the per-process random default, which
        differs across gunicorn/uvicorn workers and invalidates every token
        issued by a sibling worker.
        """
        explicit = "SECRET_KEY" in self.model_fields_set
        is_production = self.APP_ENV.strip().lower() in PRODUCTION_ENVIRONMENTS
        insecure = (
            not explicit
            or self.SECRET_KEY.strip() in INSECURE_SECRET_KEYS
            or len(self.SECRET_KEY) < MIN_SECRET_KEY_LENGTH
        )
        if is_production and insecure:
            raise ValueError(
                "SECRET_KEY must be set to a unique value of at least "
                f"{MIN_SECRET_KEY_LENGTH} characters when APP_ENV=production"
            )
        if not explicit:
            logger.warning(
                "SECRET_KEY not set: using a random per-process key. Set SECRET_KEY before running multiple workers."
            )
        return self

    @staticmethod
    def _split_and_strip(value: str) -> list[str]:
        """Split a comma-separated string and strip whitespace from each item."""
        return [item.strip() for item in value.split(",")]

    def get_allowed_extensions(self) -> tuple:
        """Return the full tuple of accepted audio + video file extensions."""
        audio = tuple(self._split_and_strip(self.ALLOWED_AUDIO_EXTENSIONS))
        video = tuple(self._split_and_strip(self.ALLOWED_VIDEO_EXTENSIONS))
        return audio + video

    def is_video(self, ext: str) -> bool:
        """Return True if ``ext`` is in the configured video-extension list."""
        return ext.lower() in self._split_and_strip(self.ALLOWED_VIDEO_EXTENSIONS)

    def get_allowed_origins(self) -> list:
        """Return the list of CORS-allowed origins parsed from settings."""
        return self._split_and_strip(self.ALLOWED_ORIGINS)


settings = Settings()
