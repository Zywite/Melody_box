"""Security helpers: password hashing and JWT token utilities."""

import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from sqlalchemy.orm import Session

from .config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if ``plain_password`` matches the stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Hash ``password`` with bcrypt and return the UTF-8 encoded digest."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
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
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
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


def create_refresh_token(db: Session, user_id: str) -> str:
    """Create a refresh token JWT, persist it, and return the token string."""
    from app.models import RefreshToken

    jti = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = jwt.encode(
        {"sub": user_id, "type": "refresh", "jti": jti, "exp": expires_at},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    db_refresh = RefreshToken(
        id=str(uuid.uuid4()),
        token=token,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(db_refresh)
    db.commit()
    return token


def verify_refresh_token(db: Session, token: str) -> dict | None:
    """Validate a refresh token JWT, check revocation, return its payload.

    Returns None if the token is invalid, expired, or revoked.
    """
    from app.models import RefreshToken

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        return None

    stored = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not stored or stored.revoked_at is not None:
        return None

    return payload


def revoke_refresh_token(db: Session, token: str) -> None:
    """Mark a refresh token as revoked (rotation on use)."""
    from app.models import RefreshToken

    stored = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if stored:
        stored.revoked_at = datetime.now(UTC)
        db.commit()
