import io
import json
from unittest.mock import patch
from app.core.config import BASE_DIR


def test_get_all_songs(client, test_song, test_song2):
    response = client.get("/songs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    titles = [s["title"] for s in data]
    assert "Test Song" in titles
    assert "Another Song" in titles


def test_get_song_by_id(client, test_song):
    response = client.get(f"/songs/{test_song.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Song"
    assert data["artist"] == "Test Artist"
    assert data["album"] == "Test Album"
    assert data["duration"] == 180.0


def test_get_song_not_found(client):
    response = client.get("/songs/nonexistent-id")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


def test_search_songs(client, test_song, test_song2):
    response = client.get("/songs/search", params={"q": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["title"] == "Test Song" for s in data)


def test_search_songs_no_results(client):
    response = client.get("/songs/search", params={"q": "xyznonexistent"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_songs_empty_query(client):
    response = client.get("/songs/search", params={"q": ""})
    assert response.status_code == 422


def test_stream_song(client, test_song):
    response = client.get(f"/songs/{test_song.id}/stream")
    assert response.status_code == 404


def test_stream_song_not_found(client):
    response = client.get("/songs/nonexistent-id/stream")
    assert response.status_code == 404


def test_upload_song_success(client, auth_headers, tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    fake_file = io.BytesIO(b"fake audio content")
    fake_file.name = "test_audio.mp3"

    with patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(music_dir)), \
         patch("app.routes.songs._extract_duration", return_value=180.0):
        response = client.post(
            "/songs/upload",
            headers=auth_headers,
            files={"file": ("test_audio.mp3", fake_file, "audio/mpeg")},
            data={"title": "Uploaded Song", "artist": "Uploaded Artist", "album": "Uploaded Album"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Uploaded Song"
    assert data["artist"] == "Uploaded Artist"
    assert data["media_type"] == "audio"


def test_upload_song_invalid_extension(client, auth_headers):
    fake_file = io.BytesIO(b"fake content")
    fake_file.name = "test.exe"
    response = client.post(
        "/songs/upload",
        headers=auth_headers,
        files={"file": ("test.exe", fake_file, "application/octet-stream")},
        data={"title": "Bad", "artist": "Bad"}
    )
    assert response.status_code == 400
    assert "formato" in response.json()["detail"].lower() or "not allowed" in response.json()["detail"].lower()


def test_upload_song_without_auth(client, tmp_path):
    fake_file = io.BytesIO(b"fake content")
    fake_file.name = "test.mp3"
    with patch("app.routes.songs._extract_duration", return_value=180.0):
        response = client.post(
            "/songs/upload",
            files={"file": ("test.mp3", fake_file, "audio/mpeg")},
            data={"title": "No Auth", "artist": "No Auth"}
        )
    assert response.status_code == 401


def test_delete_song(client, auth_headers, test_song):
    response = client.delete(f"/songs/{test_song.id}", headers=auth_headers)
    assert response.status_code == 200
    assert "eliminada" in response.json()["message"].lower()


def test_delete_song_not_found(client, auth_headers):
    response = client.delete("/songs/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404


def test_delete_song_without_auth(client, test_song):
    response = client.delete(f"/songs/{test_song.id}")
    assert response.status_code == 401


def test_upload_multiple_success(client, auth_headers, tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    files = [
        ("files", ("song1.mp3", io.BytesIO(b"content1"), "audio/mpeg")),
        ("files", ("song2.mp3", io.BytesIO(b"content2"), "audio/mpeg")),
    ]
    metadata = json.dumps([
        {"title": "Multi 1", "artist": "Artist 1", "album": "Album 1"},
        {"title": "Multi 2", "artist": "Artist 2", "album": "Album 2"},
    ])
    with patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(music_dir)), \
         patch("app.routes.songs._extract_duration", return_value=180.0):
        response = client.post(
            "/songs/upload-multiple",
            headers=auth_headers,
            files=files,
            data={"metadata": metadata}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success_count"] == 2
    assert data["error_count"] == 0
    assert data["total"] == 2


def test_upload_multiple_mismatch(client, auth_headers):
    files = [("files", ("song.mp3", io.BytesIO(b"content"), "audio/mpeg"))]
    metadata = json.dumps([
        {"title": "A", "artist": "B", "album": "C"},
        {"title": "D", "artist": "E", "album": "F"},
    ])
    response = client.post(
        "/songs/upload-multiple",
        headers=auth_headers,
        files=files,
        data={"metadata": metadata}
    )
    assert response.status_code == 400


def test_get_song_fft_not_found(client, auth_headers):
    response = client.get("/songs/nonexistent-id/fft", headers=auth_headers)
    assert response.status_code == 404


def test_get_song_fft_no_data(client, auth_headers, test_song):
    with patch("app.routes.songs.FFTService.compute_fft_from_file") as mock_fft:
        mock_fft.return_value = {
            "duration": 10.0, "sample_rate": 22050, "channels": 1,
            "bins": [0, 128], "spectrogram": [[0]], "bass_power": 33.0,
            "mid_power": 33.0, "treble_power": 34.0,
            "fft_size": 2048, "hop_size": 512, "nyquist": 11025, "bin_count": 2
        }
        response = client.get(f"/songs/{test_song.id}/fft", headers=auth_headers)
    assert response.status_code == 200


def test_analyze_all_songs(client, auth_headers, test_song):
    with patch("app.routes.songs.FFTService.compute_fft_from_file") as mock_fft:
        mock_fft.return_value = {
            "duration": 10.0, "sample_rate": 22050, "channels": 1,
            "bins": [0, 128], "spectrogram": [[0]], "bass_power": 33.0,
            "mid_power": 33.0, "treble_power": 34.0,
            "fft_size": 2048, "hop_size": 512, "nyquist": 11025, "bin_count": 2
        }
        response = client.post("/songs/analyze-all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_get_songs_response_format(client, test_song):
    response = client.get("/songs")
    song = response.json()[0]
    assert "id" in song
    assert "title" in song
    assert "artist" in song
    assert "album" in song
    assert "duration" in song
    assert "media_type" in song
    assert "has_fft" in song


def test_stream_song_success(client, db, tmp_path):
    music_file = tmp_path / "real_song.mp3"
    music_file.write_bytes(b"fake audio content")
    import app.models as models
    import uuid
    from app.core.config import BASE_DIR
    song = models.Song(
        id=str(uuid.uuid4()), title="Stream Real", artist="Artist",
        file_path=str(music_file), duration=30.0
    )
    db.add(song)
    db.commit()
    response = client.get(f"/songs/{song.id}/stream")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "audio/mpeg"


def test_delete_song_file_removed_from_disk(client, db, auth_headers, tmp_path):
    music_file = tmp_path / "delete_test.mp3"
    music_file.write_bytes(b"content")
    import app.models as models
    import uuid
    song = models.Song(
        id=str(uuid.uuid4()), title="Delete Real", artist="Artist",
        file_path=str(music_file), duration=10.0
    )
    db.add(song)
    db.commit()
    client.delete(f"/songs/{song.id}", headers=auth_headers)
    assert not music_file.exists()


def test_upload_multiple_partial_error(client, auth_headers, tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    import json
    import app.routes.songs as songs_route
    files = [
        ("files", ("ok.mp3", io.BytesIO(b"valid content"), "audio/mpeg")),
        ("files", ("bad.exe", io.BytesIO(b"bad"), "application/octet-stream")),
    ]
    metadata = json.dumps([
        {"title": "Valid", "artist": "V", "album": ""},
        {"title": "Invalid", "artist": "I", "album": ""},
    ])
    with patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(music_dir)):
        with patch("app.routes.songs._extract_duration", return_value=30.0):
            response = client.post(
                "/songs/upload-multiple",
                headers=auth_headers,
                files=files,
                data={"metadata": metadata},
            )
    assert response.status_code == 200
    data = response.json()
    assert data["success_count"] == 1
    assert data["error_count"] == 1
    assert data["total"] == 2
    assert len(data["errors"]) == 1
    assert data["errors"][0]["filename"] == "bad.exe"
    assert "formato" in data["errors"][0]["error"].lower() or "not allowed" in data["errors"][0]["error"].lower()
