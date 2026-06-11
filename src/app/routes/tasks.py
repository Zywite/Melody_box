from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import ERROR_TASK_NOT_FOUND
from app.core.database import get_db
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
def get_task(task_id: str, db: Annotated[Session, Depends(get_db)]):
    """Return the current status and result of an arq task by id."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=ERROR_TASK_NOT_FOUND)

    return {
        "id": task.id,
        "type": task.type,
        "status": task.status,
        "progress": task.progress,
        "error": task.error,
        "result": task.result,
        "song_id": task.song_id,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }
