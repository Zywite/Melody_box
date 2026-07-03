from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.constants import DB_MAX_OVERFLOW, DB_POOL_SIZE
from .config import BASE_DIR, settings

DB_CONNECT_TIMEOUT_SECONDS = 3


def _create_engine_with_fallback() -> Engine:
    """Create engine, testing connection. Falls back to SQLite on failure."""
    if "sqlite" in settings.DATABASE_URL:
        return create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

    pool_kwargs = {"pool_size": DB_POOL_SIZE, "max_overflow": DB_MAX_OVERFLOW, "pool_pre_ping": True}

    # 3s connect timeout prevents startup from hanging when the DB host
    # is unreachable. libpq accepts ``connect_timeout`` in the URL.
    db_url = settings.DATABASE_URL
    if "connect_timeout" not in db_url:
        sep = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{sep}connect_timeout={DB_CONNECT_TIMEOUT_SECONDS}"

    engine = create_engine(db_url, **pool_kwargs)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"Warning: Could not connect to PostgreSQL ({e}), falling back to SQLite")
        db_path = BASE_DIR / "data" / "spotify_local.db"
        return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})


engine = _create_engine_with_fallback()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    # Keep loaded attributes available after commit so that ORM objects
    # stored in the in-process user cache (see ``routes/dependencies.py``)
    # don't trigger ``DetachedInstanceError`` when the session is closed.
    expire_on_commit=False,
)
Base = declarative_base()


def get_db() -> Generator:
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
