import pytest

from app.services.playlist_service import PlaylistService
from app.services.song_service import SongService


def test_create_playlist(db, test_user):
    playlist = PlaylistService.create_playlist(db, test_user.id, "My Playlist", "Description")
    assert playlist.name == "My Playlist"
    assert playlist.description == "Description"
    assert playlist.user_id == test_user.id


def test_create_playlist_without_description(db, test_user):
    playlist = PlaylistService.create_playlist(db, test_user.id, "No Desc")
    assert playlist.name == "No Desc"
    assert playlist.description is None


def test_get_playlist(db, test_playlist):
    playlist = PlaylistService.get_playlist(db, test_playlist.id)
    assert playlist is not None
    assert playlist.id == test_playlist.id


def test_get_playlist_not_found(db):
    playlist = PlaylistService.get_playlist(db, "nonexistent-id")
    assert playlist is None


def test_get_user_playlists(db, test_user, test_playlist):
    playlists = PlaylistService.get_user_playlists(db, test_user.id)
    assert len(playlists) >= 1
    assert any(p.id == test_playlist.id for p in playlists)


def test_get_user_playlists_empty(db, other_user):
    playlists = PlaylistService.get_user_playlists(db, other_user.id)
    assert len(playlists) == 0


def test_add_song_to_playlist(db, test_playlist, test_song2):
    result = PlaylistService.add_song_to_playlist(db, test_playlist.id, test_song2.id)
    assert result is not None
    assert result.playlist_id == test_playlist.id
    assert result.song_id == test_song2.id
    assert result.position == 2


def test_add_duplicate_song_returns_existing(db, test_playlist, test_song):
    PlaylistService.add_song_to_playlist(db, test_playlist.id, test_song.id)
    result = PlaylistService.add_song_to_playlist(db, test_playlist.id, test_song.id)
    assert result is not None
    assert result.song_id == test_song.id


def test_add_song_auto_increments_position(db, test_playlist, test_song2):
    result = PlaylistService.add_song_to_playlist(db, test_playlist.id, test_song2.id)
    assert result.position == 2


def test_add_song_position_with_new_song(db, test_playlist, test_song2):
    _ = PlaylistService.add_song_to_playlist(db, test_playlist.id, test_song2.id)
    song3, _ = SongService.create_song(
        db, title="Third Song", artist="Third Artist", file_path="/tmp/third.mp3", duration=100.0
    )
    third = PlaylistService.add_song_to_playlist(db, test_playlist.id, song3.id)
    assert third.position == 3


def test_remove_song_from_playlist(db, test_playlist, test_song):
    result = PlaylistService.remove_song_from_playlist(db, test_playlist.id, test_song.id)
    assert result is not None


def test_remove_song_not_in_playlist(db, test_playlist):
    result = PlaylistService.remove_song_from_playlist(db, test_playlist.id, "nonexistent-song-id")
    assert result is None


def test_delete_playlist_without_songs(db, test_user):
    playlist = PlaylistService.create_playlist(db, test_user.id, "To Delete")
    playlist_id = playlist.id
    PlaylistService.delete_playlist(db, playlist_id)
    result = PlaylistService.get_playlist(db, playlist_id)
    assert result is None


def test_delete_nonexistent_playlist(db):
    playlist = PlaylistService.delete_playlist(db, "nonexistent-id")
    assert playlist is None


def test_playlist_has_songs_relationship(db, test_playlist, test_song):
    playlist = PlaylistService.get_playlist(db, test_playlist.id)
    assert len(playlist.songs) >= 1


def test_create_playlist_duplicate_name_raises(db, test_user):
    PlaylistService.create_playlist(db, test_user.id, "Unique Name")
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        PlaylistService.create_playlist(db, test_user.id, "Unique Name")
    assert "existe" in exc_info.value.detail


def test_create_playlist_same_name_different_user_allowed(db, test_user, other_user):
    PlaylistService.create_playlist(db, test_user.id, "Same Name")
    playlist = PlaylistService.create_playlist(db, other_user.id, "Same Name")
    assert playlist.name == "Same Name"


def test_create_playlist_max_limit_reached(db, test_user):
    from fastapi import HTTPException

    from app.core.constants import MAX_PLAYLISTS_PER_USER

    for i in range(MAX_PLAYLISTS_PER_USER):
        PlaylistService.create_playlist(db, test_user.id, f"Playlist {i}")
    with pytest.raises(HTTPException) as exc_info:
        PlaylistService.create_playlist(db, test_user.id, "Overflow")
    assert "Límite" in exc_info.value.detail


def test_add_song_max_limit_reached(db, test_user):
    from fastapi import HTTPException

    from app.core.constants import MAX_SONGS_PER_PLAYLIST

    playlist = PlaylistService.create_playlist(db, test_user.id, "Big Playlist")
    for i in range(MAX_SONGS_PER_PLAYLIST):
        song, _ = SongService.create_song(
            db, title=f"Song {i}", artist="Artist", file_path=f"/tmp/song{i}.mp3", duration=100.0
        )
        PlaylistService.add_song_to_playlist(db, playlist.id, song.id)
    extra_song, _ = SongService.create_song(
        db, title="Extra Song", artist="Artist", file_path="/tmp/extra.mp3", duration=100.0
    )
    with pytest.raises(HTTPException) as exc_info:
        PlaylistService.add_song_to_playlist(db, playlist.id, extra_song.id)
    assert "Límite" in exc_info.value.detail
