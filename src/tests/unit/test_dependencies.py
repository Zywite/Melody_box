from datetime import timedelta

from app.core.security import create_access_token
from app.routes.dependencies import clear_user_cache, invalidate_user_cache


def test_get_optional_user_no_header(client):
    response = client.get("/songs")
    assert response.status_code == 200


def test_get_optional_user_invalid_token(client):
    response = client.get("/songs", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 200


def test_get_optional_user_valid_token(client, test_user):
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(hours=1))
    response = client.get("/songs", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_invalidate_user_cache(client, test_user):
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(hours=1))
    headers = {"Authorization": f"Bearer {token}"}
    client.get("/playlists", headers=headers)
    invalidate_user_cache(test_user.id)
    response = client.get("/playlists", headers=headers)
    assert response.status_code == 200


def test_clear_user_cache(client, test_user):
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(hours=1))
    headers = {"Authorization": f"Bearer {token}"}
    client.get("/playlists", headers=headers)
    clear_user_cache()
    response = client.get("/playlists", headers=headers)
    assert response.status_code == 200


def test_get_optional_user_expired_token(client, test_user):
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(days=-1))
    response = client.get("/songs", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_get_optional_user_nonexistent_user(client, db):
    token = create_access_token(data={"sub": "nonexistent-id"}, expires_delta=timedelta(hours=1))
    response = client.get("/songs", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_current_user_inactive_returns_401(client, db, test_user):
    test_user.is_active = False
    db.commit()
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(hours=1))
    response = client.get("/playlists", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_get_optional_user_inactive_returns_none(client, db, test_user):
    test_user.is_active = False
    db.commit()
    token = create_access_token(data={"sub": test_user.id}, expires_delta=timedelta(hours=1))
    response = client.get("/songs", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
