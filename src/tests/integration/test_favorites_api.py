def test_add_favorite(client, auth_headers, test_song):
    response = client.post("/favorites", headers=auth_headers, json={"song_id": test_song.id})
    assert response.status_code == 200
    data = response.json()
    assert data["song_id"] == test_song.id
    assert data["song"] is not None
    assert data["song"]["title"] == "Test Song"


def test_add_favorite_without_auth(client, test_song):
    response = client.post("/favorites", json={"song_id": test_song.id})
    assert response.status_code == 401


def test_add_favorite_nonexistent_song(client, auth_headers):
    response = client.post("/favorites", headers=auth_headers, json={"song_id": "nonexistent-id"})
    assert response.status_code == 404


def test_add_duplicate_favorite(client, auth_headers, test_song):
    client.post("/favorites", headers=auth_headers, json={"song_id": test_song.id})
    response = client.post("/favorites", headers=auth_headers, json={"song_id": test_song.id})
    assert response.status_code == 400
    assert "favoritos" in response.json()["detail"].lower() or "already" in response.json()["detail"].lower()


def test_get_favorites(client, auth_headers, test_favorite):
    response = client.get("/favorites", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(f["song_id"] == test_favorite.song_id for f in data)


def test_get_favorites_includes_song_details(client, auth_headers, test_favorite, test_song):
    response = client.get("/favorites", headers=auth_headers)
    data = response.json()
    fav = next(f for f in data if f["song_id"] == test_song.id)
    assert fav["song"]["title"] == "Test Song"
    assert fav["song"]["artist"] == "Test Artist"


def test_get_favorites_without_auth(client):
    response = client.get("/favorites")
    assert response.status_code == 401


def test_remove_favorite(client, auth_headers, test_favorite):
    response = client.delete(f"/favorites/{test_favorite.song_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "eliminada" in response.json()["message"].lower()


def test_remove_nonexistent_favorite(client, auth_headers):
    response = client.delete("/favorites/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404


def test_remove_favorite_without_auth(client, test_favorite):
    response = client.delete(f"/favorites/{test_favorite.song_id}")
    assert response.status_code == 401
