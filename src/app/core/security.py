"""Security helpers: password hashing and JWT token utilities."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from .config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if ``plain_password`` matches the stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash ``password`` with bcrypt and return the UTF-8 encoded digest."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Build a signed JWT containing ``data`` and an ``exp`` claim.

    Args:
        data: Claims to embed in the token (e.g. ``{"sub": user_id}``).
        expires_delta: Lifetime of the token. Defaults to 15 minutes from
            now.

    Returns:
        The encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """Verify and decode a JWT.

    Returns:
        The decoded claim set on success, or None if the token is invalid
        or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None
