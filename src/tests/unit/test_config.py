"""Tests for the startup SECRET_KEY validation (fail fast in production)."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

STRONG_KEY = "k" * 32


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_production_rejects_missing_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(APP_ENV="production")


def test_production_rejects_placeholder_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(APP_ENV="production", SECRET_KEY="change-me-in-production")


def test_production_rejects_short_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(APP_ENV="production", SECRET_KEY="short-key")


def test_production_accepts_strong_secret_key():
    settings = _settings(APP_ENV="production", SECRET_KEY=STRONG_KEY)
    assert settings.SECRET_KEY == STRONG_KEY


def test_development_keeps_random_default(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    settings = _settings(APP_ENV="development")
    assert len(settings.SECRET_KEY) >= 32
