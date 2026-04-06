# Arquitectura — MelodyBox

## Visión general

MelodyBox es una aplicación web cliente-servidor para reproducir audio y video en una red local. El backend expone una API REST y sirve el frontend estático. La comunicación es HTTP sobre la red local, permitiendo que cualquier dispositivo conectado acceda al contenido.

```
┌─────────────────────────────────────────────────────┐
│                   Red Local (WiFi)                   │
│                                                      │
│  ┌──────────────┐    HTTP/REST    ┌───────────────┐ │
│  │  Navegador   │ ──────────────► │   FastAPI     │ │
│  │  (Cliente)   │ ◄────────────── │   Server      │ │
│  │  HTML/JS/CSS │                 │   :8001       │ │
│  └──────────────┘                 └───────┬───────┘ │
│                                           │         │
│                                    ┌──────▼───────┐ │
│                                    │  PostgreSQL  │ │
│                                    │  /  SQLite   │ │
│                                    └──────┬───────┘ │
│                                           │         │
│                                    ┌──────▼───────┐ │
│                                    │ music_storage│ │
│                                    │  (archivos)  │ │
│                                    └──────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## Estructura del proyecto

```
MelodyBox/
├── src/                     # Backend
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        # Configuración con pydantic-settings
│   │   │   ├── database.py      # Motor SQL + sesión
│   │   │   └── security.py      # JWT + bcrypt
│   │   ├── models/
│   │   │   ├── __init__.py      # Exporta todos los modelos
│   │   │   ├── user.py          # Modelo User
│   │   │   └── music.py         # Song, Playlist, PlaylistSong, Favorite
│   │   ├── routes/
│   │   │   ├── auth.py          # /auth/register, /auth/login
│   │   │   ├── songs.py         # /songs (CRUD + upload + stream)
│   │   │   ├── playlists.py     # /playlists (CRUD + songs)
│   │   │   └── favorites.py     # /favorites (CRUD)
│   │   ├── services/
│   │   │   ├── user_service.py      # Lógica de usuarios
│   │   │   ├── song_service.py      # Lógica de canciones
│   │   │   └── playlist_service.py  # Lógica de playlists
│   │   ├── schemas.py           # Schemas Pydantic (DTOs)
│   │   └── main.py              # FastAPI app, middleware, routers
│   ├── .env                     # Configuración (no incluir en git)
│   └── music_storage/          # Archivos subidos
├── public/                     # Frontend
│   ├── index.html              # SPA con 5 páginas
│   └── static/
│       ├── css/style.css       # Diseño dark theme con glassmorphism
│       └── js/
│           ├── api.js          # Cliente HTTP
│           ├── player.js       # Reproductor (MusicPlayer)
│           └── app.js          # Lógica UI
├── docs/                       # Documentación
├── scripts/                    # Scripts de utilidad
│   ├── start_server.py         # Script de inicio
│   ├── run_server.bat          # Script Windows
│   └── run_server.sh           # Script Linux/Mac
├── .gitignore                  # Archivos a ignorar
├── .env.example                # Ejemplo de configuración
├── requirements.txt            # Dependencias Python
└── README.md                   # Documentación principal
```

---

## Base de datos

### Diagrama de tablas

```
┌──────────────────┐     ┌──────────────────┐
│      users       │     │      songs       │
├──────────────────┤     ├──────────────────┤
│ id (PK, UUID)    │     │ id (PK, UUID)    │
│ username (UNQ)   │     │ title            │
│ email (UNQ)      │     │ artist           │
│ hashed_password  │     │ album (NULL)     │
│ is_active        │     │ duration         │
│ created_at       │     │ file_path (UNQ)  │
└───────┬──────────┘     │ media_type       │
        │                │ created_at       │
        │                └───────┬──────────┘
        │                        │
        │          ┌─────────────┼──────────────┐
        │          │             │              │
        ▼          ▼             ▼              ▼
┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  playlists   │ │  playlist_songs  │ │    favorites     │
├──────────────┤ ├──────────────────┤ ├──────────────────┤
│ id (PK)      │ │ id (PK)          │ │ id (PK)          │
│ name         │ │ playlist_id (FK) │ │ user_id (FK)     │
│ description  │ │ song_id (FK)     │ │ song_id (FK)     │
│ user_id (FK) │ │ position         │ │ added_at         │
│ created_at   │ │ added_at         │ └──────────────────┘
│ updated_at   │ └──────────────────┘
└──────────────┘
```

### Relaciones

| Relación | Tipo | Tabla intermedia |
|---|---|---|
| User → Playlists | 1:N | — |
| User → Favorites | 1:N | — |
| Song → Favorites | 1:N | — |
| Playlist → Songs | N:M | `playlist_songs` |

### Notas de diseño

- **UUID como claves primarias** — Evita colisiones y no expone IDs secuenciales
- **`file_path` UNIQUE** — Previene subir el mismo archivo dos veces
- **`media_type`** — Diferencia audio de video para el streaming correcto

---

## Flujo de datos

### Upload

```
Cliente → POST /songs/upload (multipart/form-data)
    │
    ├─ 1. Validar token JWT
    ├─ 2. Validar extensión del archivo
    ├─ 3. Determinar media_type (audio/video)
    ├─ 4. Guardar archivo en music_storage/
    ├─ 5. Detectar duración (librosa para audio, ffprobe para video)
    ├─ 6. Crear registro en BD (ruta absoluta)
    └─ 7. Retornar SongResponse
```

### Streaming

```
Cliente → GET /songs/{id}/stream
    │
    ├─ 1. Buscar canción en BD
    ├─ 2. Verificar que el archivo existe
    ├─ 3. Determinar MIME type por extensión
    └─ 4. FileResponse con Accept-Ranges: bytes
              │
              └─► El navegador pide por partes (byte-range)
                  Permitiendo seek sin descargar todo
```

### Autenticación

```
Cliente → POST /auth/login
    │
    ├─ 1. Buscar usuario por email
    ├─ 2. Verificar password con bcrypt
    ├─ 3. Crear JWT con python-jose
    │      payload: { sub: user_id, exp: now + 1440min }
    └─ 4. Retornar { access_token, token_type, username }
```

---

## Patrones de diseño

### 1. Singleton — `config.py`

Una única instancia de configuración compartida en toda la aplicación.

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./spotify_local.db"
    SECRET_KEY: str = "tu-clave-secreta"
    # ... más configuraciones

settings = Settings()  # Instancia única, importada donde se necesite
```

Se importa como `from app.core.config import settings` en cualquier módulo — siempre es el mismo objeto.

---

### 2. Service Layer — `services/`

La lógica de negocio está separada de los endpoints HTTP. Los routes delegan a servicios.

```python
# backend/app/services/song_service.py
class SongService:
    @staticmethod
    def create_song(db, title, artist, file_path, duration, album, media_type):
        db_song = Song(id=str(uuid.uuid4()), title=title, ...)
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        return db_song

    @staticmethod
    def get_song(db, song_id):
        return db.query(Song).filter(Song.id == song_id).first()
```

```python
# backend/app/routes/songs.py
@router.post("/upload")
async def upload_song(...):
    # El endpoint solo valida y delega
    song = SongService.create_song(db, title, artist, file_path, duration, album, media_type)
    return {"id": song.id, "title": song.title, ...}
```

**Ventaja:** La lógica de negocio es reutilizable y testeable independientemente de FastAPI.

---

### 3. Repository — `services/`

Los servicios encapsulan el acceso a datos. Los routes no hacen queries directas.

```python
# backend/app/services/user_service.py
class UserService:
    @staticmethod
    def get_user_by_email(db, email):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db, user_id):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def verify_user_password(db, email, password):
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
```

```python
# backend/app/routes/auth.py
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = UserService.verify_user_password(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    # ...
```

---

### 4. Dependency Injection — `Depends()`

FastAPI inyecta dependencias automáticamente en cada endpoint.

```python
# backend/app/core/database.py
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Se ejecuta al terminar la request
```

```python
# backend/app/routes/songs.py
@router.get("", response_model=list[SongResponse])
def get_all_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    songs = SongService.get_all_songs(db, skip, limit)
    return songs
```

**Ventaja:** Cada request recibe su propia sesión de BD que se cierra automáticamente.

---

### 5. DTO (Data Transfer Object) — `schemas.py`

Los schemas Pydantic separan la capa API de los modelos de base de datos.

```python
# backend/app/schemas.py
class SongResponse(BaseModel):
    id: str
    title: str
    artist: str
    album: Optional[str]
    duration: float
    media_type: Optional[str] = "audio"
    created_at: datetime

    class Config:
        from_attributes = True  # Convierte ORM objects a dict
```

```python
# backend/app/routes/songs.py
@router.get("", response_model=list[SongResponse])  # FastAPI serializa automáticamente
def get_all_songs(..., db: Session = Depends(get_db)):
    return SongService.get_all_songs(db, skip, limit)  # Retorna objetos ORM
```

**Ventaja:** Control total sobre qué campos se exponen y validación automática de tipos.

---

### 6. Facade — `api.js`

Una clase que envuelve todas las operaciones HTTP del frontend.

```javascript
// frontend/static/js/api.js
class SpotifyAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('token');
    }

    async request(endpoint, options = {}) {
        // Maneja headers, token, errores en un solo lugar
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
        // ...
    }

    async getSongs() { return this.request('/songs'); }
    async login(email, password) { /* ... */ }
    async uploadSong(file, title, artist, album) { /* ... */ }
}

const api = new SpotifyAPI();  // Instancia global
```

**Ventaja:** El resto del frontend no necesita conocer detalles de HTTP.

---

### 7. Strategy — MIME types por extensión

El tipo de contenido se determina dinámicamente según la extensión del archivo.

```python
# backend/app/routes/songs.py
MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "flac": "audio/flac",
    "ogg": "audio/ogg",
    "m4a": "audio/mp4",
    "mp4": "video/mp4",
    "mkv": "video/x-matroska",
    "avi": "video/x-msvideo",
    "webm": "video/webm",
    "mov": "video/quicktime",
}

@router.get("/{song_id}/stream")
def stream_song(song_id: str, db: Session = Depends(get_db)):
    song = SongService.get_song(db, song_id)
    ext = Path(song.file_path).suffix.lower().lstrip(".")
    media_type = MIME_TYPES.get(ext, "application/octet-stream")
    return FileResponse(song.file_path, media_type=media_type)
```

---

### 8. Observer — Event listeners del reproductor

El reproductor reacciona a eventos del elemento audio/video.

```javascript
// frontend/static/js/player.js
class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.audio.addEventListener('ended', () => this.nextSong());
        this.audio.addEventListener('timeupdate', () => this.updateProgress());
        this.audio.addEventListener('loadedmetadata', () => this.updateDuration());
    }

    updateProgress() {
        const pct = (this.audio.currentTime / this.audio.duration) * 100;
        document.getElementById('progress-fill').style.width = pct + '%';
    }
}
```

---

### 9. MVC (Model-View-Controller)

| Capa | Implementación |
|---|---|
| **Model** | Modelos SQLAlchemy (`User`, `Song`, `Playlist`) |
| **View** | `index.html` + `style.css` (renderizado en el navegador) |
| **Controller** | Routes FastAPI (`auth.py`, `songs.py`) + `app.js` (lógica UI) |

---

## Dependencias

### Backend

| Paquete | Versión | Propósito |
|---|---|---|
| `fastapi` | 0.104.1 | Framework web |
| `uvicorn` | 0.24.0 | Servidor ASGI |
| `sqlalchemy` | 2.0.48 | ORM |
| `psycopg2-binary` | 2.9.9 | Driver PostgreSQL |
| `pydantic` | 2.5.0 | Validación de datos |
| `pydantic-settings` | 2.1.0 | Configuración desde .env |
| `python-jose[cryptography]` | 3.3.0 | JWT |
| `bcrypt` | 5.0.0 | Hash de contraseñas |
| `email-validator` | 2.3.0 | Validación de emails |
| `python-multipart` | 0.0.6 | Parseo de formularios |

### Externas

| Herramienta | Propósito |
|---|---|
| `librosa` | Detección de duración de audio (opcional) |
| `ffprobe` (ffmpeg) | Detección de duración de video (opcional) |
| `PostgreSQL` | Base de datos principal |

---

## Decisiones técnicas

### ¿Por qué PostgreSQL y no solo SQLite?

- **Concurrencia** — PostgreSQL soporta múltiples conexiones simultáneas sin bloqueos
- **Escalabilidad** — Mejor rendimiento con muchos archivos y usuarios
- **Integridad** — Foreign keys reales con cascada
- **Fallback** — Si PostgreSQL no está disponible, usa SQLite automáticamente

### ¿Por qué UUID y no auto-increment?

- **Seguridad** — No expone la cantidad de registros
- **Distribución** — Funciona si se replica la BD en el futuro
- **Sin colisiones** — Seguro para IDs generados en diferentes nodos

### ¿Por qué `bcrypt` directo y no `passlib`?

`passlib` es incompatible con `bcrypt` 5.0+. Usar `bcrypt` directamente elimina una dependencia problemática y simplifica el código.

### ¿Por qué rutas absolutas para los archivos?

Las rutas relativas (`./music_storage/...`) fallan si el servidor se inicia desde un directorio diferente. Las rutas absolutas garantizan que siempre se encuentren los archivos.

### ¿Por qué byte-range en el streaming?

`FileResponse` de FastAPI soporta automáticamente el header `Range`. El navegador pide el archivo por partes, permitiendo:
- Empezar a reproducir sin descargar todo
- Saltar a cualquier punto del audio/video
- Menor uso de memoria

---

## Limitaciones conocidas

1. **Las canciones no tienen dueño** — Cualquier usuario autenticado puede eliminar cualquier canción
2. **Sin paginación en favoritos/playlists** — Se retornan todos los registros
3. **Sin interfaz para favoritos** — Solo accesible vía API
4. **Sin rate limiting** — Los endpoints de auth son vulnerables a fuerza bruta
5. **SECRET_KEY por defecto** — Debe cambiarse en producción
6. **Sin migraciones de BD** — Se usa `create_all()` que no maneja cambios de schema
