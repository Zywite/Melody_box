from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.constants import ERROR_TOKEN_INVALID, USER_LOOKUP_CACHE_TTL_SECONDS, USER_LOOKUP_CACHE_MAXSIZE
from app.core.security import decode_token
from app.core.ttl_cache import TTLCache
from app.services.user_service import UserService
from app.models import User, UserRole


_user_cache: TTLCache[User] = TTLCache(
    maxsize=USER_LOOKUP_CACHE_MAXSIZE,
    ttl_seconds=USER_LOOKUP_CACHE_TTL_SECONDS,
)


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Resolve the authenticated user from a ``Bearer`` token header.

    The resolved user is cached in-process for a short TTL so that
    repeated requests from the same client don't hit the database on
    every call.

    Raises:
        HTTPException: 401 if the token is missing/invalid or the user no
            longer exists; 503 if the database is unreachable.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail=ERROR_TOKEN_INVALID)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail=ERROR_TOKEN_INVALID)

    cached = _user_cache.get(user_id)
    if cached is not None:
        if not cached.is_active:
            raise HTTPException(status_code=401, detail="Cuenta desactivada")
        return cached

    try:
        user = UserService.get_user_by_id(db, user_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Servicio no disponible")

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Cuenta desactivada")

    _user_cache.set(user_id, user)
    return user


def require_admin(current_user: User = Depends(get_current_user)):
    """Require the authenticated user to have the ``admin`` role.

    Raises:
        HTTPException: 403 if the user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return current_user


def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Resolve the user from a token header, or return None when unauthenticated.

    Database errors are also swallowed to None so this dependency can be
    used on public endpoints that should not 500 on transient DB issues.
    """
    if not authorization:
        return None

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    cached = _user_cache.get(user_id)
    if cached is not None:
        return cached

    try:
        user = UserService.get_user_by_id(db, user_id)
    except SQLAlchemyError:
        return None

    if user is not None:
        _user_cache.set(user_id, user)
    return user


def invalidate_user_cache(user_id: str) -> None:
    """Drop a single user from the cache (e.g. after role change / deletion)."""
    _user_cache.invalidate(user_id)


def clear_user_cache() -> None:
    """Drop the entire user cache (e.g. in tests or admin actions)."""
    _user_cache.clear()
