from fastapi import Depends, Header, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.constants import ERROR_TOKEN_INVALID
from app.core.security import decode_token
from app.services.user_service import UserService
from app.models import User


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Resolve the authenticated user from a ``Bearer`` token header.

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

    try:
        user = UserService.get_user_by_id(db, user_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Servicio no disponible")

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user


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

    try:
        return UserService.get_user_by_id(db, user_id)
    except SQLAlchemyError:
        return None