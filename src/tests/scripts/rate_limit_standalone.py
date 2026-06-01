"""Standalone rate limit test - runs in a fresh Python process."""
import sys
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import redis_helper
redis_helper.enqueue_job = AsyncMock(return_value=None)
redis_helper.cache_get_fft = AsyncMock(return_value=None)
redis_helper.cache_set_fft = AsyncMock(return_value=None)
redis_helper.get_redis = AsyncMock(return_value=None)

from app.core import database
from app.core.database import Base, get_db
from app.models import User
from app.services.user_service import UserService

_test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
database.engine = _test_engine
database.SessionLocal.configure(bind=_test_engine)
Base.metadata.create_all(bind=_test_engine)


def override_get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.main import app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

failed = 0

# Test A4: Register rate-limited to 3/min
for i in range(3):
    resp = client.post("/auth/register", json={
        "username": f"rluser{i}", "email": f"rluser{i}@test.com", "password": "pass123"
    })
    assert resp.status_code == 200, f"Register {i}: {resp.status_code}"

resp = client.post("/auth/register", json={
    "username": "rlextra", "email": "rlextra@test.com", "password": "pass123"
})
if resp.status_code != 429:
    print(f"FAIL: Register rate limit (expected 429, got {resp.status_code})")
    failed += 1
else:
    print("PASS: Register rate limit")

# Test A7: Login rate-limited to 5/min
db_session = database.SessionLocal()
UserService.create_user(db_session, "loginuser", "login@test.com", "pass123")
db_session.close()

for i in range(5):
    resp = client.post("/auth/login", json={
        "email": "login@test.com", "password": "pass123"
    })
    assert resp.status_code == 200, f"Login {i}: {resp.status_code}"

resp = client.post("/auth/login", json={
    "email": "login@test.com", "password": "pass123"
})
if resp.status_code != 429:
    print(f"FAIL: Login rate limit (expected 429, got {resp.status_code})")
    failed += 1
else:
    print("PASS: Login rate limit")

# Test S4: Upload rate-limited to 10/min
db_session = database.SessionLocal()
user = UserService.create_user(db_session, "uploaduser", "upload@test.com", "pass123")
db_session.close()

from app.core.security import create_access_token
from datetime import timedelta
token = create_access_token(data={"sub": user.id}, expires_delta=timedelta(hours=1))
headers = {"Authorization": f"Bearer {token}"}

for i in range(10):
    resp = client.post(
        "/songs/upload",
        headers=headers,
        files={"file": (f"rate{i}.mp3", b"x", "audio/mpeg")},
        data={"title": f"Rate{i}", "artist": "A"}
    )

resp = client.post(
    "/songs/upload",
    headers=headers,
    files={"file": ("overflow.mp3", b"x", "audio/mpeg")},
    data={"title": "Overflow", "artist": "A"}
)
if resp.status_code != 429:
    print(f"FAIL: Upload rate limit (expected 429, got {resp.status_code})")
    failed += 1
else:
    print("PASS: Upload rate limit")

sys.exit(failed)
