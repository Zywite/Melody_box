import os
from pathlib import Path
from unittest.mock import patch

from app.routes.songs import _extract_duration


def test_e2e_upload_stream_delete_wav(client, auth_headers, tone_wav_bytes, tmp_path):
    """Upload real .wav → stream → delete, all with real file I/O."""
    storage = tmp_path / "music"
    storage.mkdir()

    with patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(storage)):
        with patch("app.routes.songs._extract_duration", return_value=0.3):
            resp = client.post(
                "/songs/upload",
                headers=auth_headers,
                files={"file": ("sine440.wav", tone_wav_bytes, "audio/wav")},
                data={"title": "Sine 440Hz", "artist": "E2E Tester", "album": "E2E Album"},
            )
    assert resp.status_code == 200
    song = resp.json()
    assert song["title"] == "Sine 440Hz"
    assert song["artist"] == "E2E Tester"
    assert song["media_type"] == "audio"
    song_id = song["id"]

    # File exists on disk
    saved_path = storage / "sine440.wav"
    assert saved_path.exists(), "File was not saved to storage directory"
    assert saved_path.stat().st_size > 0

    # Stream → 200 with correct Content-Type
    resp = client.get(f"/songs/{song_id}/stream")
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("audio/wav")
    assert int(resp.headers.get("content-length", 0)) > 0

    # Delete → file removed from disk
    resp = client.delete(f"/songs/{song_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert not saved_path.exists(), "File should be deleted from disk"


def test_e2e_upload_multiple_wav_files(client, auth_headers, tone_wav_bytes, tone_wav_bytes2, tmp_path):
    """Upload multiple real .wav files and verify both stored on disk."""
    storage = tmp_path / "music"
    storage.mkdir()
    import json

    files = [
        ("files", ("tone1.wav", tone_wav_bytes, "audio/wav")),
        ("files", ("tone2.wav", tone_wav_bytes2, "audio/wav")),
    ]
    metadata = json.dumps([
        {"title": "Tone 1", "artist": "E2E", "album": "Multi"},
        {"title": "Tone 2", "artist": "E2E", "album": "Multi"},
    ])

    with patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(storage)):
        with patch("app.routes.songs._extract_duration", return_value=0.3):
            resp = client.post(
                "/songs/upload-multiple",
                headers=auth_headers,
                files=files,
                data={"metadata": metadata},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success_count"] == 2
    assert data["error_count"] == 0
    assert (storage / "tone1.wav").exists()
    assert (storage / "tone2.wav").exists()


def test_e2e_upload_nonexistent_extension(client, auth_headers, tmp_path):
    """Upload with disallowed extension → 400, no file saved."""
    storage = tmp_path / "music"
    storage.mkdir()
    fake = __import__("io").BytesIO(b"not a real audio")

    with patch("app.routes.songs.settings.MUSIC_STORAGE_PATH", str(storage)):
        resp = client.post(
            "/songs/upload",
            headers=auth_headers,
            files={"file": ("virus.exe", fake, "application/octet-stream")},
            data={"title": "Bad", "artist": "Bad"},
        )
    assert resp.status_code == 400
    assert not any(storage.iterdir()), "No files should be saved"
