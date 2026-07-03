"""Lightweight schema migrations for MelodyBox.

These are one-shot migration helpers invoked during application startup
to bring the database schema up to date without requiring Alembic.
"""

from sqlalchemy import text

from app.core.database import engine


def _run_migrations_sqlite() -> None:
    """Fallback migrations for SQLite."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            if "role" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))
                print("Added role column to users table (SQLite)")
            conn.commit()
    except Exception as e:
        print(f"Migration error (non-fatal): {e}")


def run_migrations() -> None:
    """Run lightweight schema migrations."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'songs' AND column_name = 'fft_data'"
                )
            )
            if "fft_data" not in [row[0] for row in result]:
                conn.execute(text("ALTER TABLE songs ADD COLUMN fft_data TEXT"))
                print("Added fft_data column to songs table")

            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'users' AND column_name = 'role'"
                )
            )
            if "role" not in [row[0] for row in result]:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL"))
                print("Added role column to users table")
            conn.commit()
    except Exception:
        _run_migrations_sqlite()
