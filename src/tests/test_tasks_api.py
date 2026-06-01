def test_get_task_by_id(client, test_task):
    response = client.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_task.id
    assert data["type"] == "fft"
    assert data["status"] == "done"
    assert data["progress"] == 100
    assert data["result"] is not None
    assert data["song_id"] == test_task.song_id


def test_get_task_not_found(client):
    response = client.get("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_task_with_pending_status(client, db, test_song):
    from app.models.task import Task
    import uuid
    task = Task(
        id=str(uuid.uuid4()),
        type="youtube_download",
        status="pending",
        song_id=test_song.id,
        progress=0
    )
    db.add(task)
    db.commit()

    response = client.get(f"/tasks/{task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["progress"] == 0


def test_get_task_with_error(client, db, test_song):
    from app.models.task import Task
    import uuid
    task = Task(
        id=str(uuid.uuid4()),
        type="fft",
        status="failed",
        song_id=test_song.id,
        progress=50,
        error="Something went wrong"
    )
    db.add(task)
    db.commit()

    response = client.get(f"/tasks/{task.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "Something went wrong"


def test_get_task_returns_timestamps(client, test_task):
    response = client.get(f"/tasks/{test_task.id}")
    data = response.json()
    assert "created_at" in data
    assert "updated_at" in data
    assert data["created_at"] is not None
