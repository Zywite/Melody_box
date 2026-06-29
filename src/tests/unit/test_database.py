from unittest.mock import patch

from app.core.database import _create_engine_with_fallback, get_db


def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    try:
        next(gen)
    except StopIteration:
        pass


def test_get_db_closes_on_exit():
    gen = get_db()
    next(gen)
    gen.close()


def test_create_engine_with_sqlite_url_returns_engine():
    with patch("app.core.database.settings.DATABASE_URL", "sqlite:///:memory:"):
        engine = _create_engine_with_fallback()
        assert engine is not None


def test_create_engine_postgresql_fallback():
    with patch("app.core.database.settings.DATABASE_URL", "postgresql://invalid:5432/test"):
        engine = _create_engine_with_fallback()
        assert engine is not None
