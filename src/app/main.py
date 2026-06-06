from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import time
import logging
from sqlalchemy import text
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import limiter
from app.core.selective_gzip import SelectiveGZipMiddleware
from app.models import Favorite, Playlist, PlaylistSong, Song, User  # noqa: F401 - needed for Base.metadata
from app.routes import auth, favorites, playlists, songs, youtube, tasks

logger = logging.getLogger(__name__)


class CachedStaticFiles(StaticFiles):
    """StaticFiles variant that emits a 1-year immutable Cache-Control header."""
    def file_response(self, *args, **kwargs):
        """Wrap the parent file response and inject the cache header."""
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: create schema, run lightweight migrations, log start/stop."""
    # Retry create_all with a brief delay for PostgreSQL readiness
    for attempt in range(3):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            print(f"Database connection attempt {attempt+1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                print("All database connection attempts failed. Continuing without DB.")
    
    # Migrations: Add new columns if they don't exist
    try:
        with engine.connect() as conn:
            # Check if fft_data column exists in songs table (PostgreSQL)
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'songs' AND column_name = 'fft_data'"
            ))
            columns = [row[0] for row in result]
            
            if 'fft_data' not in columns:
                conn.execute(text("ALTER TABLE songs ADD COLUMN fft_data TEXT"))
                print("Added fft_data column to songs table")
            
            conn.commit()
    except Exception as e:
        print(f"Migration error: {e}")
    
    print("MelodyBox iniciando...")
    yield
    print("MelodyBox detenido")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SelectiveGZipMiddleware, minimum_size=1000)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Log unhandled exceptions and return a generic 500 to the client."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


BASE_DIR = Path(__file__).parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
PUBLIC_DIR = BASE_DIR / "public"
MUSIC_DIR = BASE_DIR / "data" / "music"


@app.get("/")
async def root():
    """Serve the built SPA index.html, or a JSON banner if no build exists."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "name": "MelodyBox",
        "version": settings.API_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Liveness probe used by docker / orchestrators."""
    return {"status": "healthy"}


if FRONTEND_DIR.exists():
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", CachedStaticFiles(directory=str(assets_dir), html=True), name="frontend-assets")

if MUSIC_DIR.exists():
    app.mount("/music", StaticFiles(directory=str(MUSIC_DIR)), name="music-storage")

if PUBLIC_DIR.exists():
    static_path = PUBLIC_DIR / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="public-static")

app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(favorites.router)
app.include_router(youtube.router)
app.include_router(tasks.router)

@app.get("/{path:path}")
async def serve_spa(path: str):
    """Serve index.html for any non-API route (SPA fallback)"""
    # Exclude static assets, media files, and API routes
    if path.startswith(('assets/', 'static/', 'music/', 'favicon')):
        return {"error": "Not found"}
    
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"error": "Not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
