from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Index
from datetime import datetime
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # "fft", "youtube_download"
    status = Column(String, default="pending")  # "pending", "processing", "done", "failed"
    progress = Column(Integer, default=0)
    song_id = Column(String, nullable=True, index=True)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_task_type_status", "type", "status"),
    )
