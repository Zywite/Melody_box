import jwt
from app.core.config import settings


def test_e2e_auth_full_flow(client):
    """Register → Login → Access protected endpoint → Verify JWT claims."""
    # 1. Register
    resp = client.post("/auth/register", json={
        "username": "e2euser",
        "email": "e2e@test.com",
        "password": "StrongPass1!",
    })
    assert resp.status_code == 200
    user = resp.json()
    assert user["username"] == "e2euser"
    assert user["email"] == "e2e@test.com"

    # 2. Login
    resp = client.post("/auth/login", json={
        "email": "e2e@test.com",
        "password": "StrongPass1!",
    })
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["username"] == "e2euser"
    token = token_data["access_token"]

    # 3. Access protected endpoint
    resp = client.get("/playlists", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # 4. Verify JWT claims
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == user["id"]
    assert "exp" in payload

    # 5. Wrong password → 401
    resp = client.post("/auth/login", json={
        "email": "e2e@test.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401

    # 6. No token → 401
    resp = client.get("/playlists")
    assert resp.status_code == 401

    # 7. Invalid token → 401
    resp = client.get("/playlists", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401

    # 8. Duplicate email → 400
    resp = client.post("/auth/register", json={
        "username": "e2euser2",
        "email": "e2e@test.com",
        "password": "AnotherPass1!",
    })
    assert resp.status_code == 400

    # 9. Duplicate username → 400
    resp = client.post("/auth/register", json={
        "username": "e2euser",
        "email": "e2e2@test.com",
        "password": "AnotherPass1!",
    })
    assert resp.status_code == 400


def test_e2e_auth_login_then_register_same_credentials(client):
    """Register, logout (no-op), re-register with same email fails."""
    client.post("/auth/register", json={
        "username": "uniqueuser",
        "email": "unique@test.com",
        "password": "Pass1234!",
    })
    resp = client.post("/auth/register", json={
        "username": "uniqueuser",
        "email": "unique@test.com",
        "password": "Pass1234!",
    })
    assert resp.status_code == 400
