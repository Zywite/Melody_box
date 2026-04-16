from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.core.config import settings
from app.core.database import engine, Base

from app.models import User, Song, Playlist, PlaylistSong, Favorite


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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


BASE_DIR = Path(__file__).parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
PUBLIC_DIR = BASE_DIR / "public"
MUSIC_DIR = BASE_DIR / "src" / "music_storage"


@app.get("/")
async def root():
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
    return {"status": "healthy"}


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets"), html=True), name="frontend-assets")

if MUSIC_DIR.exists():
    app.mount("/music", StaticFiles(directory=str(MUSIC_DIR)), name="music-storage")

if PUBLIC_DIR.exists():
    static_path = PUBLIC_DIR / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="public-static")

from app.routes import auth, songs, playlists, favorites

app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(favorites.router)

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