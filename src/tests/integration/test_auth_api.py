from app.core.security import create_access_token
from tests.conftest import TEST_PASSWORD


def test_register_success(client):
    response = client.post(
        "/auth/register", json={"username": "newuser", "email": "new@example.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert data["is_active"] is True
    assert "id" in data


def test_register_password_too_short(client):
    response = client.post("/auth/register", json={"username": "user1", "email": "u1@example.com", "password": "Ab1"})
    assert response.status_code == 422


def test_register_password_no_uppercase(client):
    response = client.post(
        "/auth/register", json={"username": "user2", "email": "u2@example.com", "password": "abcdef123"}
    )
    assert response.status_code == 422


def test_register_password_no_digit(client):
    response = client.post(
        "/auth/register", json={"username": "user3", "email": "u3@example.com", "password": "Abcdefgh"}
    )
    assert response.status_code == 422


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/auth/register", json={"username": "another", "email": "test@example.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower() or "registrado" in response.json()["detail"].lower()


def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/auth/register", json={"username": "testuser", "email": "other@example.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 400
    assert "usuario" in response.json()["detail"].lower() or "exists" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    response = client.post("/auth/login", json={"email": "test@example.com", "password": TEST_PASSWORD})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "testuser"
    assert "user_id" in data
    assert data["role"] == "user"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong_credential",  # NOSONAR
        },
    )
    assert response.status_code == 401
    assert "incorrectos" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


def test_login_nonexistent_email(client):
    response = client.post("/auth/login", json={"email": "noone@example.com", "password": TEST_PASSWORD})
    assert response.status_code == 401


def test_access_protected_endpoint_with_token(client, auth_headers):
    response = client.get("/playlists", headers=auth_headers)
    assert response.status_code == 200


def test_access_protected_endpoint_without_token(client):
    response = client.get("/playlists")
    assert response.status_code == 401
    assert "token" in response.json()["detail"].lower()


def test_access_protected_endpoint_with_invalid_token(client):
    response = client.get("/playlists", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401


def test_access_protected_endpoint_with_expired_token(client):
    from datetime import timedelta

    token = create_access_token(data={"sub": "anyuser"}, expires_delta=timedelta(days=-1))
    response = client.get("/playlists", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_refresh_token_success(client, test_user):
    login_resp = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": TEST_PASSWORD,
        },
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token  # rotated
    assert data["username"] == "testuser"


def test_refresh_token_invalid(client):
    resp = client.post("/auth/refresh", json={"refresh_token": "garbage-token"})
    assert resp.status_code == 401


def test_refresh_token_revoked_after_use(client, test_user):
    login_resp = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": TEST_PASSWORD,
        },
    )
    refresh_token = login_resp.json()["refresh_token"]

    # First use — succeeds
    resp1 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp1.status_code == 200

    # Second use with same token — revoked, should fail
    resp2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401
