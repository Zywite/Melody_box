from app.core.selective_gzip import _header_value, _is_compressible


def test_is_compressible_json():
    assert _is_compressible("application/json") is True


def test_is_compressible_text():
    assert _is_compressible("text/html; charset=utf-8") is True


def test_is_compressible_none():
    assert _is_compressible(None) is True


def test_is_compressible_audio():
    assert _is_compressible("audio/mpeg") is False


def test_is_compressible_video():
    assert _is_compressible("video/mp4") is False


def test_header_value_found():
    headers = [(b"content-type", b"application/json"), (b"content-length", b"100")]
    assert _header_value(headers, b"content-type") == "application/json"


def test_header_value_not_found():
    headers = [(b"content-type", b"application/json")]
    assert _header_value(headers, b"x-custom") == ""
