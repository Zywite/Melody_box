from datetime import timedelta

from app.core.security import create_access_token, decode_token, get_password_hash, verify_password


def test_password_hash_is_different():
    hash1 = get_password_hash("password123")
    hash2 = get_password_hash("password123")
    assert hash1 != hash2


def test_verify_password_correct():
    hashed = get_password_hash("password123")
    assert verify_password("password123", hashed) is True


def test_verify_password_incorrect():
    hashed = get_password_hash("password123")
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token(data={"sub": "user123"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_valid_token():
    token = create_access_token(data={"sub": "user123"}, expires_delta=timedelta(hours=1))
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"


def test_decode_token_with_extra_claims():
    token = create_access_token(data={"sub": "user123", "role": "admin"}, expires_delta=timedelta(hours=1))
    payload = decode_token(token)
    assert payload["role"] == "admin"


def test_decode_invalid_token():
    payload = decode_token("invalid.token.here")
    assert payload is None


def test_decode_expired_token():
    token = create_access_token(data={"sub": "user123"}, expires_delta=timedelta(seconds=-1))
    payload = decode_token(token)
    assert payload is None


def test_token_decodes_successfully():
    token = create_access_token(data={"sub": "user123"})
    payload = decode_token(token)
    assert payload is not None
