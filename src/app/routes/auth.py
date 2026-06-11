from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import RATE_LIMIT_LOGIN, RATE_LIMIT_REGISTER
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token, create_refresh_token, revoke_refresh_token, verify_refresh_token
from app.schemas import RefreshRequest, Token, UserLogin, UserRegister, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
@limiter.limit(RATE_LIMIT_REGISTER)
def register(request: Request, user: UserRegister, db: Annotated[Session, Depends(get_db)]):
    """Create a new user account. Rate limited to 3 requests per minute."""
    existing_user = UserService.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    existing_username = UserService.get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya existe")

    new_user = UserService.create_user(db, user.username, user.email, user.password)
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit(RATE_LIMIT_LOGIN)
def login(request: Request, user: UserLogin, db: Annotated[Session, Depends(get_db)]):
    """Authenticate by email+password and return a JWT + refresh token. Rate limited to 5/minute."""
    db_user = UserService.verify_user_password(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "role": db_user.role.value}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(db, db_user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        username=db_user.username,
        user_id=db_user.id,
        role=db_user.role.value,
    )


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: Annotated[Session, Depends(get_db)]):
    """Issue a new access token + refresh token using a valid refresh token (rotation)."""
    payload = verify_refresh_token(db, body.refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido o expirado")

    user_id = payload["sub"]
    db_user = UserService.get_user_by_id(db, user_id)
    if not db_user or not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")

    # Rotate: revoke old, issue new pair
    revoke_refresh_token(db, body.refresh_token)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id, "role": db_user.role.value}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(db, db_user.id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        username=db_user.username,
        user_id=db_user.id,
        role=db_user.role.value,
    )
