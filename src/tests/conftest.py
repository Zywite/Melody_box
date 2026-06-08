import os
import sys
import uuid
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import redis_helper
redis_helper.enqueue_job = AsyncMock(return_value=None)
redis_helper.cache_get_fft = AsyncMock(return_value=None)
redis_helper.cache_set_fft = AsyncMock(return_value=None)
redis_helper.get_redis = AsyncMock(return_value=None)

from app.core import database
from app.core.database import Base, get_db
from app.core.config import BASE_DIR
from app.core.security import create_access_token
from app.models import User, UserRole, Song, Playlist, PlaylistSong, Favorite, Task
from app.services.user_service import UserService
from app.services.song_service import SongService
from app.services.playlist_service import PlaylistService

TEST_PASSWORD = "TestPass123!"  # nosec
ADMIN_PASSWORD = "AdminPass123!"  # nosec

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

database.engine = _test_engine
database.SessionLocal.configure(bind=_test_engine)


def override_get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def db():
    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.close()


from app.core.rate_limit import limiter as _limiter


def _restore_limiter():
    """Restore real slowapi limiter method by removing instance attribute."""
    try:
        del _limiter.__dict__["limit"]
    except KeyError:
        pass


@pytest.fixture
def client():
    _limiter.limit = lambda *args, **kwargs: lambda func: func
    for mod in list(sys.modules):
        if mod == "app.routes" or mod.startswith("app.routes.") or mod in ("app.main",):
            del sys.modules[mod]
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    _restore_limiter()


@pytest.fixture
def test_user(db):
    return UserService.create_user(db, username="testuser", email="test@example.com", password=TEST_PASSWORD)


@pytest.fixture
def other_user(db):
    return UserService.create_user(db, username="otheruser", email="other@example.com", password=TEST_PASSWORD)

@pytest.fixture
def admin_user(db):
    return UserService.create_user(db, username="adminuser", email="admin@test.com", password=ADMIN_PASSWORD, role=UserRole.admin)

@pytest.fixture
def other_admin_user(db):
    return UserService.create_user(db, username="otheradmin", email="otheradmin@test.com", password=ADMIN_PASSWORD, role=UserRole.admin)


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(hours=1))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_user):
    token = create_access_token(data={"sub": other_user.id}, expires_delta=timedelta(hours=1))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_song(db):
    song, _ = SongService.create_song(
        db, title="Test Song", artist="Test Artist",
        file_path=str(BASE_DIR / "data" / "music" / "test_song.mp3"),
        duration=180.0, album="Test Album"
    )
    return song


@pytest.fixture
def test_song2(db):
    song, _ = SongService.create_song(
        db, title="Another Song", artist="Another Artist",
        file_path=str(BASE_DIR / "data" / "music" / "test_song2.mp3"),
        duration=240.0, album="Another Album"
    )
    return song


@pytest.fixture
def test_playlist(db, test_user, test_song):
    playlist = PlaylistService.create_playlist(db, test_user.id, "Test Playlist", "A test playlist")
    PlaylistService.add_song_to_playlist(db, playlist.id, test_song.id)
    return playlist


@pytest.fixture
def test_favorite(db, test_user, test_song):
    fav = Favorite(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        song_id=test_song.id,
        added_at=datetime.now(timezone.utc)
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


@pytest.fixture
def test_task(db, test_song):
    task = Task(
        id=str(uuid.uuid4()),
        type="fft",
        status="done",
        song_id=test_song.id,
        progress=100,
        result={"bass": 30.0, "mid": 40.0, "treble": 30.0}
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
