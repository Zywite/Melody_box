"""User service: persistence operations for User entities."""

from sqlalchemy.orm import Session
from app.models import User
from app.core.security import get_password_hash, verify_password
import uuid


class UserService:
    """Static methods for creating and querying user accounts."""

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        """Create and persist a new user with a hashed password.

        Args:
            db: Active SQLAlchemy session.
            username: Display name (must be unique).
            email: User email (must be unique).
            password: Plaintext password; will be hashed before storage.

        Returns:
            The newly created User row, refreshed from the database.
        """
        db_user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=get_password_hash(password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Look up a user by their email address.

        Returns:
            The matching User row, or None if no user has that email.
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        """Look up a user by their display name.

        Returns:
            The matching User row, or None if no user has that username.
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User | None:
        """Look up a user by primary key (UUID string).

        Returns:
            The matching User row, or None if no user has that id.
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def verify_user_password(db: Session, email: str, password: str) -> User | None:
        """Authenticate a user by email + plaintext password.

        Returns:
            The User row on successful authentication, or None if the user
            does not exist or the password does not match.
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
