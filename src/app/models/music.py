from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    artist = Column(String, index=True, nullable=False)
    album = Column(String, index=True)
    duration = Column(Float)
    file_path = Column(String, unique=True, nullable=False)
    media_type = Column(String, default="audio")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    playlists = relationship("PlaylistSong", back_populates="song")
    favorites = relationship("Favorite", back_populates="song")

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="playlists")
    songs = relationship("PlaylistSong", back_populates="playlist")

class PlaylistSong(Base):
    __tablename__ = "playlist_songs"
    
    id = Column(String, primary_key=True, index=True)
    playlist_id = Column(String, ForeignKey("playlists.id"), nullable=False)
    song_id = Column(String, ForeignKey("songs.id"), nullable=False)
    position = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    playlist = relationship("Playlist", back_populates="songs")
    song = relationship("Song", back_populates="playlists")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    song_id = Column(String, ForeignKey("songs.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="favorites")
    song = relationship("Song", back_populates="favorites")
