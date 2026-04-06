from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

# Project root is 2 levels up from src/app/core/config.py
BASE_DIR = Path(__file__).parents[2]

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./spotify_local.db"
    
    # API
    API_TITLE: str = "MelodyBox API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para reproductor de música local en red"
    
    # Security
    SECRET_KEY: str = "tu-clave-secreta-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Media storage (absolute path)
    MUSIC_STORAGE_PATH: str = str(BASE_DIR / "music_storage")
    ALLOWED_AUDIO_EXTENSIONS: str = "mp3,wav,flac,ogg,m4a"
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,mkv,avi,webm,mov"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_allowed_extensions(self) -> tuple:
        """Obtener todas las extensiones permitidas (audio + video)"""
        audio = tuple(ext.strip() for ext in self.ALLOWED_AUDIO_EXTENSIONS.split(","))
        video = tuple(ext.strip() for ext in self.ALLOWED_VIDEO_EXTENSIONS.split(","))
        return audio + video

    def is_video(self, ext: str) -> bool:
        """Verificar si una extensión es de video"""
        return ext.lower() in tuple(e.strip() for e in self.ALLOWED_VIDEO_EXTENSIONS.split(","))
    
    def get_allowed_origins(self) -> list:
        """Obtener orígenes permitidos como lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
