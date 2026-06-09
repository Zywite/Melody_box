from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is 3 levels up: src/app/core/config.py -> core -> app -> src -> project root
BASE_DIR = Path(__file__).parents[3]


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/spotify_local.db"

    # API
    API_TITLE: str = "MelodyBox API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para reproductor de música local en red"

    # Security
    SECRET_KEY: str = "tu-clave-secreta-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Media storage (absolute path) - files are in data/music after reorganization
    MUSIC_STORAGE_PATH: str = str(BASE_DIR / "data" / "music")
    ALLOWED_AUDIO_EXTENSIONS: str = "mp3,wav,flac,ogg,m4a"
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,mkv,avi,webm,mov"

    # Redis / Worker
    REDIS_URL: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8001"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8")

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
