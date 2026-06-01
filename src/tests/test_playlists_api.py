def test_create_playlist(client, auth_headers):
    response = client.post("/playlists", headers=auth_headers, json={
        "name": "New Playlist",
        "description": "A brand new playlist"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Playlist"
    assert data["description"] == "A brand new playlist"
    assert "id" in data
    assert "songs" in data


def test_create_playlist_without_auth(client):
    response = client.post("/playlists", json={
        "name": "No Auth Playlist"
    })
    assert response.status_code == 401


def test_get_user_playlists(client, auth_headers, test_playlist):
    response = client.get("/playlists", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "Test Playlist" for p in data)


def test_get_playlist_by_id(client, auth_headers, test_playlist):
    response = client.get(f"/playlists/{test_playlist.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Playlist"
    assert data["description"] == "A test playlist"


def test_get_playlist_not_found(client, auth_headers):
    response = client.get("/playlists/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404


def test_get_playlist_not_owner(client, other_auth_headers, test_playlist):
    response = client.get(f"/playlists/{test_playlist.id}", headers=other_auth_headers)
    assert response.status_code == 403


def test_get_playlist_without_auth(client, test_playlist):
    response = client.get(f"/playlists/{test_playlist.id}")
    assert response.status_code == 401


def test_add_song_to_playlist(client, auth_headers, test_playlist, test_song2):
    response = client.post(
        f"/playlists/{test_playlist.id}/songs",
        headers=auth_headers,
        json={"song_id": test_song2.id}
    )
    assert response.status_code == 200
    assert "agregada" in response.json()["message"].lower()


def test_add_song_to_playlist_not_owner(client, other_auth_headers, test_playlist, test_song2):
    response = client.post(
        f"/playlists/{test_playlist.id}/songs",
        headers=other_auth_headers,
        json={"song_id": test_song2.id}
    )
    assert response.status_code == 403


def test_add_song_to_nonexistent_playlist(client, auth_headers, test_song):
    response = client.post(
        "/playlists/nonexistent-id/songs",
        headers=auth_headers,
        json={"song_id": test_song.id}
    )
    assert response.status_code == 404


def test_add_nonexistent_song_to_playlist(client, auth_headers, test_playlist):
    response = client.post(
        f"/playlists/{test_playlist.id}/songs",
        headers=auth_headers,
        json={"song_id": "nonexistent-song"}
    )
    assert response.status_code == 404


def test_remove_song_from_playlist(client, auth_headers, test_playlist, test_song):
    response = client.delete(
        f"/playlists/{test_playlist.id}/songs/{test_song.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "eliminada" in response.json()["message"].lower()


def test_remove_song_from_playlist_not_owner(client, other_auth_headers, test_playlist, test_song):
    response = client.delete(
        f"/playlists/{test_playlist.id}/songs/{test_song.id}",
        headers=other_auth_headers
    )
    assert response.status_code == 403


def test_delete_playlist(client, auth_headers, test_user, db):
    response = client.post("/playlists", headers=auth_headers, json={"name": "To Delete"})
    playlist_id = response.json()["id"]
    response = client.delete(f"/playlists/{playlist_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "eliminada" in response.json()["message"].lower()


def test_delete_playlist_not_owner(client, other_auth_headers, test_playlist):
    response = client.delete(f"/playlists/{test_playlist.id}", headers=other_auth_headers)
    assert response.status_code == 403


def test_delete_nonexistent_playlist(client, auth_headers):
    response = client.delete("/playlists/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404
