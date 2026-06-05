from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings, BASE_DIR

def _create_engine_with_fallback():
    """Create engine, testing connection. Falls back to SQLite on failure."""
    pool_kwargs = {"pool_size": 20, "max_overflow": 10, "pool_pre_ping": True}

    if "sqlite" in settings.DATABASE_URL:
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            **pool_kwargs
        )

    engine = create_engine(settings.DATABASE_URL, **pool_kwargs)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"Warning: Could not connect to PostgreSQL ({e}), falling back to SQLite")
        db_path = BASE_DIR / "data" / "spotify_local.db"
        return create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )

engine = _create_engine_with_fallback()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
