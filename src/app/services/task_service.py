"""Task service: persistence operations for Task entities."""

import uuid

from sqlalchemy.orm import Session

from app.models.task import Task


class TaskService:
    """Static methods for creating and querying tasks."""

    @staticmethod
    def get_task(db: Session, task_id: str) -> Task | None:
        """Fetch a task by its primary key."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_pending_fft_task(db: Session, song_id: str):
        """Return the first pending or processing FFT task for a song, or None."""
        return (
            db.query(Task)
            .filter(
                Task.song_id == song_id,
                Task.type == "fft",
                Task.status.in_(["pending", "processing"]),
            )
            .first()
        )

    @staticmethod
    def create_task(
        db: Session,
        task_type: str,
        status: str,
        song_id: str | None = None,
    ) -> Task:
        """Create and persist a new task row, returning it."""
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            status=status,
            song_id=song_id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
