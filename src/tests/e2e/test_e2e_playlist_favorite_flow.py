from unittest.mock import patch


def test_e2e_full_user_journey(client, auth_headers, tone_wav_bytes, tone_wav_bytes2, tmp_path):
    """
    Full user journey:
    Upload 2 songs → create playlist → add songs → favorite → remove → delete playlist.
    """
    storage = tmp_path / "music"
    storage.mkdir()

    with (
        patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(storage)),
        patch("app.routes.songs._extract_duration", return_value=0.3),
    ):
        # Upload song 1
        r1 = client.post(
            "/songs/upload",
            headers=auth_headers,
            files={"file": ("song1.wav", tone_wav_bytes, "audio/wav")},
            data={"title": "Song One", "artist": "Artist A", "album": "Album X"},
        )
        assert r1.status_code == 200
        song1_id = r1.json()["id"]

        # Upload song 2
        r2 = client.post(
            "/songs/upload",
            headers=auth_headers,
            files={"file": ("song2.wav", tone_wav_bytes2, "audio/wav")},
            data={"title": "Song Two", "artist": "Artist A", "album": "Album X"},
        )
        assert r2.status_code == 200
        song2_id = r2.json()["id"]

    # Create playlist
    resp = client.post(
        "/playlists",
        headers=auth_headers,
        json={
            "name": "E2E Playlist",
            "description": "Created by e2e test",
        },
    )
    assert resp.status_code == 200
    playlist = resp.json()
    playlist_id = playlist["id"]
    assert playlist["name"] == "E2E Playlist"
    assert len(playlist["songs"]) == 0

    # Add song 1
    resp = client.post(
        f"/playlists/{playlist_id}/songs",
        headers=auth_headers,
        json={"song_id": song1_id},
    )
    assert resp.status_code == 200
    assert "agregada" in resp.json()["message"].lower()

    # Get playlist → 1 song
    resp = client.get(f"/playlists/{playlist_id}", headers=auth_headers)
    assert resp.status_code == 200
    songs = resp.json()["songs"]
    assert len(songs) == 1
    assert songs[0]["song_id"] == song1_id

    # Add song 2
    resp = client.post(
        f"/playlists/{playlist_id}/songs",
        headers=auth_headers,
        json={"song_id": song2_id},
    )
    assert resp.status_code == 200

    # Favorite song 1
    resp = client.post("/favorites", headers=auth_headers, json={"song_id": song1_id})
    assert resp.status_code == 200
    assert resp.json()["song_id"] == song1_id

    # Get favorites → has song details
    resp = client.get("/favorites", headers=auth_headers)
    assert resp.status_code == 200
    favs = resp.json()
    assert len(favs) == 1
    assert favs[0]["song"]["title"] == "Song One"

    # Duplicate favorite → 400
    resp = client.post("/favorites", headers=auth_headers, json={"song_id": song1_id})
    assert resp.status_code == 400

    # Remove favorite
    resp = client.delete(f"/favorites/{song1_id}", headers=auth_headers)
    assert resp.status_code == 200

    # Remove song from playlist
    resp = client.delete(
        f"/playlists/{playlist_id}/songs/{song1_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # Get playlist → 1 song remaining
    resp = client.get(f"/playlists/{playlist_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["songs"]) == 1

    # Delete playlist
    resp = client.delete(f"/playlists/{playlist_id}", headers=auth_headers)
    assert resp.status_code == 200

    # Verify playlist gone
    resp = client.get(f"/playlists/{playlist_id}", headers=auth_headers)
    assert resp.status_code == 404

    # Verify songs still exist
    resp = client.get(f"/songs/{song2_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Song Two"


def test_e2e_other_user_cannot_access_playlist(client, auth_headers, other_auth_headers, tone_wav_bytes, tmp_path):
    """Non-owner gets 403 on playlist operations."""
    storage = tmp_path / "music"
    storage.mkdir()

    with (
        patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(storage)),
        patch("app.routes.songs._extract_duration", return_value=0.3),
    ):
        resp = client.post(
            "/songs/upload",
            headers=auth_headers,
            files={"file": ("song.wav", tone_wav_bytes, "audio/wav")},
            data={"title": "My Song", "artist": "Me", "album": "Mine"},
        )
        song_id = resp.json()["id"]

    # Owner creates playlist
    resp = client.post(
        "/playlists",
        headers=auth_headers,
        json={
            "name": "My Playlist",
        },
    )
    playlist_id = resp.json()["id"]

    # Other user tries to get playlist
    resp = client.get(f"/playlists/{playlist_id}", headers=other_auth_headers)
    assert resp.status_code == 403

    # Other user tries to add song
    resp = client.post(
        f"/playlists/{playlist_id}/songs",
        headers=other_auth_headers,
        json={"song_id": song_id},
    )
    assert resp.status_code == 403

    # Other user tries to delete playlist
    resp = client.delete(f"/playlists/{playlist_id}", headers=other_auth_headers)
    assert resp.status_code == 403
