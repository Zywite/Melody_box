from datetime import timedelta
from app.core.security import create_access_token
from app.models import UserRole


def _admin_token(admin_user):
    return {"Authorization": f"Bearer {create_access_token(data={'sub': admin_user.id, 'role': 'admin'}, expires_delta=timedelta(hours=1))}"}


def test_admin_list_users(client, admin_user):
    headers = _admin_token(admin_user)
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_admin_list_users_requires_admin(client, test_user):
    headers = {"Authorization": f"Bearer {create_access_token(data={'sub': test_user.id}, expires_delta=timedelta(hours=1))}"}
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 403


def test_admin_list_users_unauthorized(client):
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_admin_count_users(client, admin_user):
    headers = _admin_token(admin_user)
    response = client.get("/admin/users/count", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] >= 1


def test_admin_toggle_user_active(client, admin_user, test_user):
    headers = _admin_token(admin_user)
    response = client.patch(f"/admin/users/{test_user.id}/toggle-active", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    # Toggle back
    response = client.patch(f"/admin/users/{test_user.id}/toggle-active", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_admin_toggle_self_not_allowed(client, admin_user):
    headers = _admin_token(admin_user)
    response = client.patch(f"/admin/users/{admin_user.id}/toggle-active", headers=headers)
    assert response.status_code == 400


def test_admin_delete_user(client, admin_user, test_user):
    headers = _admin_token(admin_user)
    response = client.delete(f"/admin/users/{test_user.id}", headers=headers)
    assert response.status_code == 200


def test_admin_delete_admin_not_allowed(client, admin_user, other_admin_user):
    headers = _admin_token(admin_user)
    response = client.delete(f"/admin/users/{other_admin_user.id}", headers=headers)
    assert response.status_code == 400


def test_admin_user_stats(client, admin_user, test_user, test_playlist, test_favorite):
    headers = _admin_token(admin_user)
    response = client.get(f"/admin/users/{test_user.id}/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "stats" in data
    assert data["stats"]["playlists"] >= 1
    assert data["stats"]["favorites"] >= 1


def test_admin_list_songs(client, admin_user, test_song):
    headers = _admin_token(admin_user)
    response = client.get("/admin/songs", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_admin_list_playlists(client, admin_user, test_playlist):
    headers = _admin_token(admin_user)
    response = client.get("/admin/playlists", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_admin_delete_playlist(client, admin_user, test_playlist):
    headers = _admin_token(admin_user)
    response = client.delete(f"/admin/playlists/{test_playlist.id}", headers=headers)
    assert response.status_code == 200


def test_admin_update_user(client, admin_user, test_user):
    headers = _admin_token(admin_user)
    response = client.patch(f"/admin/users/{test_user.id}", headers=headers, json={
        "username": "updateduser"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


def test_admin_update_user_role(client, admin_user, test_user):
    headers = _admin_token(admin_user)
    response = client.patch(f"/admin/users/{test_user.id}", headers=headers, json={
        "role": "admin"
    })
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
