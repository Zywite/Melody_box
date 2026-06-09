import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(enum.StrEnum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole, create_constraint=False), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    playlists = relationship("Playlist", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
