import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import verify_password
from app.services.user_service import UserService
from tests.conftest import TEST_PASSWORD


def test_create_user(db):
    user = UserService.create_user(db, username="newuser", email="new@example.com", password=TEST_PASSWORD)
    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert verify_password(TEST_PASSWORD, user.hashed_password)
    assert user.is_active is True


def test_get_user_by_email_found(db, test_user):
    user = UserService.get_user_by_email(db, "test@example.com")
    assert user is not None
    assert user.id == test_user.id


def test_get_user_by_email_not_found(db):
    user = UserService.get_user_by_email(db, "nonexistent@example.com")
    assert user is None


def test_get_user_by_username_found(db, test_user):
    user = UserService.get_user_by_username(db, "testuser")
    assert user is not None
    assert user.id == test_user.id


def test_get_user_by_username_not_found(db):
    user = UserService.get_user_by_username(db, "nonexistent")
    assert user is None


def test_get_user_by_id_found(db, test_user):
    user = UserService.get_user_by_id(db, test_user.id)
    assert user is not None
    assert user.username == "testuser"


def test_get_user_by_id_not_found(db):
    user = UserService.get_user_by_id(db, "nonexistent-id")
    assert user is None


def test_verify_user_password_correct(db, test_user):
    user = UserService.verify_user_password(db, "test@example.com", TEST_PASSWORD)
    assert user is not None
    assert user.id == test_user.id


def test_verify_user_password_wrong(db, test_user):
    user = UserService.verify_user_password(db, "test@example.com", "wrong_credential")
    assert user is None


def test_verify_user_password_email_not_found(db):
    user = UserService.verify_user_password(db, "no@example.com", TEST_PASSWORD)
    assert user is None


def test_create_user_unique_email(db):
    UserService.create_user(db, username="user1", email="same@example.com", password=TEST_PASSWORD)
    with pytest.raises(IntegrityError):
        UserService.create_user(db, username="user2", email="same@example.com", password=TEST_PASSWORD)


def test_create_user_unique_username(db):
    UserService.create_user(db, username="sameuser", email="user1@example.com", password=TEST_PASSWORD)
    with pytest.raises(IntegrityError):
        UserService.create_user(db, username="sameuser", email="user2@example.com", password=TEST_PASSWORD)


def test_create_user_password_too_short(db):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(db, username="user1", email="u1@example.com", password="Ab1")
    assert "8 caracteres" in exc_info.value.detail


def test_create_user_password_no_uppercase(db):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(db, username="user2", email="u2@example.com", password="abcdef123")
    assert "mayúscula" in exc_info.value.detail


def test_create_user_password_no_digit(db):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(db, username="user3", email="u3@example.com", password="Abcdefgh")
    assert "número" in exc_info.value.detail
