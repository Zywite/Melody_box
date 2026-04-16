from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.services.user_service import UserService
from app.models import User


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extraer usuario del header de autorización"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")


def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extraer usuario del header si existe token, sino返回 None"""
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return UserService.get_user_by_id(db, user_id)
    except Exception:
        return None