"""User service: persistence operations for User entities."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, UserRole
from app.core.security import get_password_hash, verify_password
import uuid


class UserService:
    """Static methods for creating and querying user accounts."""

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, role: UserRole = UserRole.user) -> User:
        """Create and persist a new user with a hashed password."""
        db_user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Look up a user by their email address."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        """Look up a user by their display name."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User | None:
        """Look up a user by primary key (UUID string)."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def verify_user_password(db: Session, email: str, password: str) -> User | None:
        """Authenticate a user by email + plaintext password."""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        """Return paginated list of users, optionally filtered by search."""
        query = db.query(User)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                User.username.ilike(pattern) | User.email.ilike(pattern)
            )
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_users(db: Session) -> int:
        """Return total number of users."""
        return db.query(User).count()

    @staticmethod
    def update_user(db: Session, user_id: str, **kwargs) -> User | None:
        """Update user fields. Returns None if user not found."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Delete a user by id. Returns True if deleted, False if not found."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
