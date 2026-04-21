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
│   │   │   ├── favorites.py     # /favorites (CRUD)
│   │   │   └── dependencies.py  # Dependencias compartidas de auth
│   │   ├── services/
│   │   │   ├── user_service.py      # Lógica de usuarios
│   │   │   ├── song_service.py      # Lógica de canciones
│   │   │   └── playlist_service.py  # Lógica de playlists
│   │   ├── schemas.py           # Schemas Pydantic (DTOs)
│   │   └── main.py              # FastAPI app, middleware, routers, SPA fallback
│   ├── .env                     # Configuración (no incluir en git)
│   └── music_storage/          # Archivos subidos
├── frontend/                   # Frontend Vue 3 + Vite + Tailwind
│   ├── src/
│   │   ├── assets/
│   │   │   └── main.css         # Estilos globales, variables CSS, glassmorphism
│   │   ├── components/
│   │   │   ├── common/          # SongCard, PlaylistCard, SearchInput, etc.
│   │   │   ├── layout/          # AppSidebar, MobileNav, ToastContainer
│   │   │   └── player/          # PlayerBar, VideoFlyout, ModeSelector
│   │   ├── composables/        # useApi.js, useToast.js
│   │   ├── stores/              # Pinia stores (auth, library, player)
│   │   ├── views/               # Vue components (HomeView, SearchView, etc.)
│   │   ├── router/              # Vue Router config
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
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

En esta sección se documentan los patrones de diseño utilizados en el proyecto, con ejemplos prácticos del código real.

---

### 1. Singleton

**Propósito:** Garantizar una única instancia de configuración compartida en toda la aplicación.

**Implementación:** La clase `Settings` se instancia una sola vez y se importa como módulo singleton.

```python
# src/app/core/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
import os

BASE_DIR = Path(__file__).parents[2]

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./spotify_local.db"
    SECRET_KEY: str = "tu-clave-secreta-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    MUSIC_STORAGE_PATH: str = str(BASE_DIR / "music_storage")
    ALLOWED_AUDIO_EXTENSIONS: str = "mp3,wav,flac,ogg,m4a"
    ALLOWED_VIDEO_EXTENSIONS: str = "mp4,mkv,avi,webm,mov"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia única global
settings = Settings()
```

**Uso:** Se importa en cualquier módulo y siempre devuelve la misma instancia.

```python
# En cualquier archivo del proyecto
from app.core.config import settings

print(settings.DATABASE_URL)  # sqlite:///./spotify_local.db
print(settings.MUSIC_STORAGE_PATH)  # Ruta absoluta a music_storage
```

**Ventaja:** Configuración centralizada, carga desde `.env`, valor consistente en toda la aplicación.

---

### 2. Service Layer (Capa de Servicio)

**Propósito:** Separar la lógica de negocio de los endpoints HTTP.

**Implementación:** Clases con métodos estáticos que contienen toda la lógica de negocio.

```python
# src/app/services/song_service.py
from sqlalchemy.orm import Session
from app.models import Song
import os
import uuid
from pathlib import Path

class SongService:
    @staticmethod
    def create_song(db: Session, title: str, artist: str, file_path: str, 
                    duration: float, album: str = None, media_type: str = "audio"):
        """Crear una nueva canción en la base de datos."""
        db_song = Song(
            id=str(uuid.uuid4()),
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            file_path=file_path,
            media_type=media_type
        )
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        return db_song

    @staticmethod
    def get_song(db: Session, song_id: str):
        """Obtener una canción por su ID."""
        return db.query(Song).filter(Song.id == song_id).first()

    @staticmethod
    def get_all_songs(db: Session, skip: int = 0, limit: int = 100):
        """Obtener todas las canciones con paginación."""
        return db.query(Song).offset(skip).limit(limit).all()

    @staticmethod
    def search_songs(db: Session, query: str):
        """Buscar canciones por título, artista o álbum."""
        return db.query(Song).filter(
            (Song.title.ilike(f"%{query}%")) |
            (Song.artist.ilike(f"%{query}%")) |
            (Song.album.ilike(f"%{query}%"))
        ).all()

    @staticmethod
    def delete_song(db: Session, song_id: str):
        """Eliminar una canción y su archivo físico."""
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            if os.path.exists(song.file_path):
                os.remove(song.file_path)
            db.delete(song)
            db.commit()
        return song
```

**Uso en el endpoint:** El route solo delega al servicio.

```python
# src/app/routes/songs.py
@router.post("/upload")
async def upload_song(...):
    # El endpoint solo valida entrada y delega al servicio
    song = SongService.create_song(db, title, artist, file_path, duration, album, media_type)
    return {"id": song.id, "title": song.title, ...}
```

**Ventajas:**
- Lógica de negocio reutilizable desde cualquier endpoint
- Testeable independientemente de FastAPI
- Código más limpio y mantenible

---

### 3. Repository

**Propósito:** Encapsular el acceso a datos, los routes no hacen queries SQL directas.

**Implementación:** Servicios que contienen todas las operaciones de base de datos.

```python
# src/app/services/user_service.py
from sqlalchemy.orm import Session
from app.models import User
from app.core.security import get_password_hash, verify_password
import uuid

class UserService:
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str):
        """Crear un nuevo usuario."""
        db_user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=get_password_hash(password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        """Buscar usuario por email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str):
        """Buscar usuario por ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def verify_user_password(db: Session, email: str, password: str):
        """Verificar credenciales del usuario."""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
```

**Uso en autenticación:**

```python
# src/app/routes/auth.py
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = UserService.verify_user_password(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    # ... crear token JWT
```

---

### 4. Dependency Injection (Inyección de Dependencias)

**Propósito:** FastAPI maneja automáticamente el ciclo de vida de las dependencias.

**Implementación:** Función generadora con `yield` que se ejecuta antes y después de cada request.

```python
# src/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Inyección de sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db  # Se pasa la sesión al endpoint
    finally:
        db.close()  # Siempre se cierra, incluso si hay error
```

**Uso en endpoints:**

```python
# src/app/routes/songs.py
@router.get("", response_model=list[SongResponse])
def get_all_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Cada request recibe su propia sesión de BD."""
    songs = SongService.get_all_songs(db, skip, limit)
    return songs
```

**Ventajas:**
- Cada request tiene su propia sesión
- Se cierra automáticamente (no memory leaks)
- Código limpio sin gestión manual de conexiones

---

### 5. DTO (Data Transfer Object)

**Propósito:** Separar la capa API de los modelos de base de datos.

**Implementación:** Schemas Pydantic que definen qué campos se exponen.

```python
# src/app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SongResponse(BaseModel):
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[float] = None
    media_type: str = "audio"
    created_at: datetime

    class Config:
        from_attributes = True  # Convierte ORM → dict automáticamente
```

**Uso:**

```python
# src/app/routes/songs.py
@router.get("", response_model=list[SongResponse])
def get_all_songs(db: Session = Depends(get_db)):
    songs = SongService.get_all_songs(db, skip, limit)
    # FastAPI serializa automáticamente los objetos ORM a SongResponse
    return songs
```

**Ventajas:**
- Control total sobre qué campos se exponen al cliente
- Validación automática de tipos
- Separación clara entre DB y API

---

### 6. Facade (Fachada)

**Propósito:** Encapsular lógica compleja tras una interfaz simple.

**Implementación:** Composables de Vue que abstraen llamadas HTTP.

```javascript
// frontend/src/composables/useApi.js
import { useAuthStore } from '@/stores/auth'

export function useApi() {
  const authStore = useAuthStore()

  async function fetchApi(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json' }
    if (authStore.token) {
      headers['Authorization'] = `Bearer ${authStore.token}`
    }

    const response = await fetch(endpoint, {
      ...options,
      headers: { ...headers, ...options.headers }
    })

    if (response.status === 401) {
      authStore.logout()
      throw new Error('Sesión expirada')
    }

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error de servidor')
    }

    return response.json()
  }

  return { fetchApi }
}
```

**Uso en stores:**

```javascript
// frontend/src/stores/library.js
import { defineStore } from 'pinia'
import api from '@/composables/useApi'

export const useLibraryStore = defineStore('library', () => {
  async function fetchSongs() {
    return await api.fetchApi('/songs')
  }

  async function uploadSong(file, title, artist, album) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('artist', artist)
    if (album) formData.append('album', album)
    return await api.fetchApi('/songs/upload', {
      method: 'POST',
      body: formData
    })
  }
})
```

**Ventaja:** Lógica HTTP reutilizable, manejo centralizado de errores y autenticación.

---

### 7. Observer (Observador)

**Propósito:** El estado reactivo actualiza la UI automáticamente cuando cambia.

**Implementación:** Pinia stores con refs y computed properties.

```javascript
// frontend/src/stores/player.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlayerStore = defineStore('player', () => {
  // Estado reactivo
  const currentSong = ref(null)
  const isPlaying = ref(false)
  const volume = ref(0.7)

  // Computed: se actualiza automáticamente cuando cambia currentSong
  const isVideo = computed(() => {
    if (!currentSong.value) return false
    return currentSong.value.media_type === 'video'
  })

  // Acciones que modifican el estado
  function play(song) {
    currentSong.value = song
    isPlaying.value = true
  }

  function pause() {
    isPlaying.value = false
  }

  return {
    currentSong,
    isPlaying,
    isVideo,
    volume,
    play,
    pause
  }
})
```

**Uso en componentes Vue:**

```vue
<!-- En cualquier componente -->
<script setup>
import { usePlayerStore } from '@/stores/player'
const playerStore = usePlayerStore()
</script>

<template>
  <!-- Se actualiza automáticamente cuando cambia isPlaying -->
  <button @click="playerStore.pause()" v-if="playerStore.isPlaying">
    ⏸ Pausar
  </button>
  <button @click="playerStore.play(song)" v-else>
    ▶ Reproducir
  </button>
</template>
```

---

### 8. Strategy (Estrategia)

**Propósito:** Cambiar comportamiento dinámicamente según el contexto.

**Implementación:** Diccionario de MIME types por extensión.

```python
# src/app/routes/songs.py
from pathlib import Path

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
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    # Strategy: elegir MIME type según extensión del archivo
    ext = Path(song.file_path).suffix.lower().lstrip(".")
    media_type = MIME_TYPES.get(ext, "application/octet-stream")

    return FileResponse(
        song.file_path,
        media_type=media_type,
        headers={"Accept-Ranges": "bytes"}
    )
```

**Ventaja:** Agregar nuevos formatos sin modificar la lógica existente.

---

### 9. Observer — Event Listeners

**Propósito:** El reproductor reacciona a eventos del navegador.

**Implementación:** Listeners en elementos audio/video.

```javascript
// frontend/src/stores/player.js
function initAudio(element) {
  audio.value = element
  audio.value.volume = volume.value

  // Cuando termina la canción, reproducir siguiente
  audio.value.addEventListener('ended', playNext)

  // Actualizar progreso
  audio.value.addEventListener('timeupdate', updateTime)

  // Cuando carga metadata, obtener duración
  audio.value.addEventListener('loadedmetadata', updateDuration)
}

function updateTime() {
  if (audio.value && audio.value.currentTime) {
    currentTime.value = audio.value.currentTime
  }
}

function updateDuration() {
  if (audio.value && audio.value.duration && isFinite(audio.value.duration)) {
    duration.value = audio.value.duration
  }
}
```

---

### 10. MVC (Model-View-Controller)

**Propósito:** Separación clara de responsabilidades.

| Capa | Implementación | Ejemplo |
|------|----------------|--------|
| **Model** | Modelos SQLAlchemy + Pinia Stores | `Song`, `Playlist`, `usePlayerStore` |
| **View** | Componentes Vue (.vue) | `HomeView.vue`, `PlayerBar.vue` |
| **Controller** | Routes FastAPI + Composables | `songs.py`, `useApi.js` |

**Flujo típico:**
```
Usuario → Vue Component → Composables → API Fetch → FastAPI Route → Service → Model → DB
     ↑                                                            ↓
     └──────────────────── UI actualizada ← Store reactivo ←─────────────┘
```

---

### Resumen de patrones

| Patrón | Propósito | Ubicación |
|--------|----------|-----------|
| Singleton | Configuración única | `app/core/config.py` |
| Service Layer | Lógica de negocio | `app/services/*.py` |
| Repository | Acceso a datos | `app/services/*.py` |
| Dependency Injection | Ciclo de vida de dependencias | `app/core/database.py` |
| DTO | Transferencia de datos API ↔ DB | `app/schemas.py` |
| Facade | Interfaz simple para API | `frontend/src/composables/useApi.js` |
| Observer | UI reactiva | `frontend/src/stores/*.js` |
| Strategy | Comportamiento dinámico | `app/routes/songs.py` |
| Observer Events | Respuesta a eventos | `frontend/src/stores/player.js` |
| MVC | Separación de responsabilidades | Proyecto completo |

---

## Referencia de API

La documentación completa de todos los endpoints de la APIREST está disponible en:

- **Archivo:** `docs/API_REFERENCE.md`
- **Swagger UI:** `http://localhost:8001/docs`
- **ReDoc:** `http://localhost:8001/redoc`

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
