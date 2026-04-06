from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from app.core.config import settings
from app.core.database import engine, Base

# Importar modelos ANTES de crear tablas
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

@app.get("/")
async def root():
    # From src/app/main.py -> project root (3 levels up) -> public/
    frontend_path = Path(__file__).parent.parent.parent / "public" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return {
        "name": "MelodyBox",
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

frontend_static_path = Path(__file__).parent.parent.parent / "public" / "static"
if frontend_static_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_static_path)), name="static")

from app.routes import auth, songs, playlists, favorites

app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(favorites.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
