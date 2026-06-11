from app.core.config import BASE_DIR
from app.services.song_service import SongService


def test_create_song(db):
    song, is_new = SongService.create_song(
        db,
        title="New Song",
        artist="New Artist",
        file_path=str(BASE_DIR / "data" / "music" / "new_song.mp3"),
        duration=200.0,
        album="New Album",
    )
    assert song.title == "New Song"
    assert song.artist == "New Artist"
    assert song.album == "New Album"
    assert song.duration == 200.0
    assert song.media_type == "audio"
    assert is_new is False


def test_create_song_without_album(db):
    song, _ = SongService.create_song(
        db,
        title="No Album",
        artist="Artist",
        file_path=str(BASE_DIR / "data" / "music" / "no_album.mp3"),
        duration=100.0,
    )
    assert song.album is None


def test_create_song_video_type(db):
    song, _ = SongService.create_song(
        db,
        title="Video",
        artist="Artist",
        file_path=str(BASE_DIR / "data" / "music" / "video.mp4"),
        duration=300.0,
        media_type="video",
    )
    assert song.media_type == "video"


def test_get_song_by_id(db, test_song):
    song = SongService.get_song(db, test_song.id)
    assert song is not None
    assert song.title == "Test Song"


def test_get_song_not_found(db):
    song = SongService.get_song(db, "nonexistent-id")
    assert song is None


def test_get_all_songs(db, test_song, test_song2):
    songs = SongService.get_all_songs(db, skip=0, limit=100)
    assert len(songs) >= 2


def test_get_all_songs_with_pagination(db, test_song, test_song2):
    songs = SongService.get_all_songs(db, skip=0, limit=1)
    assert len(songs) == 1


def test_search_songs_by_title(db, test_song, test_song2):
    results = SongService.search_songs(db, "Test")
    assert len(results) >= 1
    assert any(s.title == "Test Song" for s in results)


def test_search_songs_by_artist(db, test_song, test_song2):
    results = SongService.search_songs(db, "Another")
    assert len(results) >= 1
    assert any(s.artist == "Another Artist" for s in results)


def test_search_songs_case_insensitive(db, test_song):
    results = SongService.search_songs(db, "test")
    assert len(results) >= 1


def test_search_songs_no_match(db):
    results = SongService.search_songs(db, "xyznonexistent")
    assert len(results) == 0


def test_delete_song(db, test_song):
    song_id = test_song.id
    SongService.delete_song(db, song_id)
    song = SongService.get_song(db, song_id)
    assert song is None


def test_delete_nonexistent_song(db):
    song = SongService.delete_song(db, "nonexistent-id")
    assert song is None
