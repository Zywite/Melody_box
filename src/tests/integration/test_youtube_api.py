from unittest.mock import MagicMock, patch


def test_search_youtube(client):
    with patch("yt_dlp.YoutubeDL") as mock_ytdl:
        instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = instance
        instance.extract_info.return_value = {
            "entries": [
                {
                    "id": "abc123",
                    "title": "Test Video",
                    "uploader": "Test Channel",
                    "thumbnail": "https://example.com/thumb.jpg",
                    "duration": 120,
                    "view_count": 1000,
                }
            ]
        }
        response = client.get("/youtube/search", params={"q": "test", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["video_id"] == "abc123"
    assert data[0]["title"] == "Test Video"
    assert data[0]["channel"] == "Test Channel"
    assert data[0]["duration"] == 120
    assert data[0]["views"] == 1000


def test_search_youtube_no_results(client):
    with patch("yt_dlp.YoutubeDL") as mock_ytdl:
        instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = instance
        instance.extract_info.return_value = {"entries": []}
        response = client.get("/youtube/search", params={"q": "nonexistent"})
    assert response.status_code == 200
    assert response.json() == []


def test_download_youtube_unsupported_format(client):
    response = client.post("/youtube/download", json={"video_id": "abc123", "format": "avi", "quality": "320"})
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower() or "choose" in response.json()["detail"].lower()
