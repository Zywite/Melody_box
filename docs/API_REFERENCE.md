# Referencia de API — MelodyBox

API REST para el reproductor de música local.

**Base URL:** `http://localhost:8001`
**Versión:** 1.0.0
**Autenticación:** Bearer Token (JWT)

---

## Tabla de contenido

1. [Autenticación](#1-autenticación)
   - [Registro](#registro)
   - [Login](#login)
   - [Obtener token](#obtener-el-token)
2. [Canciones](#2-canciones)
   - [Listar](#listar-canciones)
   - [Buscar](#buscar-canciones)
   - [Obtener una](#obtener-una-canción)
   - [Reproducir (stream)](#reproducir-stream)
   - [Subir](#subir-archivo)
   - [Eliminar](#eliminar-canción)
3. [Playlists](#3-playlists)
   - [Listar](#listar-playlists)
   - [Crear](#crear-playlist)
   - [Obtener detalles](#obtener-detalles)
   - [Agregar canción](#agregar-canción)
   - [Quitar canción](#quitar-canción)
   - [Eliminar playlist](#eliminar-playlist)
4. [Favoritos](#4-favoritos)
   - [Listar](#listar-favoritos)
   - [Agregar](#agregar-a-favoritos)
   - [Quitar](#quitar-de-favoritos)
5. [YouTube](#5-youtube)
   - [Buscar en YouTube](#buscar-en-youtube)
   - [Descargar desde YouTube](#descargar-desde-youtube)
6. [Códigos de respuesta](#6-códigos-de-respuesta)
6. [Documentación interactiva](#6-documentación-interactiva)

---

## 1. Autenticación

### Registro

Crea un nuevo usuario en el sistema.

```
POST /auth/register
Content-Type: application/json
```

**Parámetros (body):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `username` | string | Sí | Nombre de usuario (único) |
| `email` | string | Sí | Correo electrónico (único) |
| `password` | string | Sí | Contraseña |

**Ejemplo de request:**
```json
{
  "username": "miusuario",
  "email": "mi@email.com",
  "password": "mi_contraseña"
}
```

**Respuesta (201):**
```json
{
  "id": "a1b2c3d4-e5f6-...",
  "username": "miusuario",
  "email": "mi@email.com",
  "is_active": true,
  "created_at": "2026-04-21T10:30:00"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 400 | El email ya está registrado |
| 400 | El nombre de usuario ya existe |

---

### Login

Inicia sesión y obtiene un token JWT.

```
POST /auth/login
Content-Type: application/json
```

**Parámetros (body):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `email` | string | Sí | Correo electrónico registrado |
| `password` | string | Sí | Contraseña del usuario |

**Ejemplo de request:**
```json
{
  "email": "mi@email.com",
  "password": "mi_contraseña"
}
```

**Respuesta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "miusuario"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | Email o contraseña incorrectos |

---

### Obtener el token

El flujo para autenticarse:

1. Llama a `POST /auth/login` con credenciales
2. Copia el valor de `access_token` de la respuesta
3. Incluye el token en el header `Authorization` de las demás peticiones:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Duración del token:** 1440 minutos (24 horas). Configurable en `.env`.

---

## 2. Canciones

### Listar canciones

Obtiene una lista paginada de todas las canciones.

```
GET /songs?skip=0&limit=50
Authorization: Bearer {token}
```

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Cantidad de registros a saltar (para paginación) |
| `limit` | integer | 50 | Cantidad máxima de registros a devolver |

**Respuesta (200):**
```json
[
  {
    "id": "song-uuid-1234",
    "title": "Never Give Up",
    "artist": "Sia",
    "album": "The Lion Movie",
    "duration": 245.5,
    "media_type": "audio",
    "created_at": "2026-04-21T10:30:00"
  },
  {
    "id": "song-uuid-5678",
    "title": "Crab Rave",
    "artist": "Noisestorm",
    "album": "Monstercat",
    "duration": 180.0,
    "media_type": "audio",
    "created_at": "2026-04-20T15:00:00"
  }
]
```

---

### Buscar canciones

Busca canciones por título, artista o álbum.

```
GET /songs/search?q=rock
Authorization: Bearer {token}
```

**Query parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|----------|-------------|
| `q` | string | Sí | Término de búsqueda |

**Respuesta (200):** Array de canciones coincidentes (mismo formato que listar).

---

### Obtener una canción

Obtiene los detalles de una canción específica.

```
GET /songs/{song_id}
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `song_id` | string | UUID de la canción |

**Respuesta (200):**
```json
{
  "id": "song-uuid-1234",
  "title": "Never Give Up",
  "artist": "Sia",
  "album": "The Lion Movie",
  "duration": 245.5,
  "media_type": "audio",
  "created_at": "2026-04-21T10:30:00"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 404 | Canción no encontrada |

---

### Reproducir (stream)

Devuelve el archivo de audio/video para reproducir. Soporta byte-range para seek.

```
GET /songs/{song_id}/stream
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `song_id` | string | UUID de la canción |

**Headers de respuesta:**

| Header | Valor | Descripción |
|--------|-------|-------------|
| `Content-Type` | audio/mpeg, video/mp4, etc. | Tipo MIME según extensión |
| `Accept-Ranges` | bytes | Soporta reproducción por partes |
| `Content-Length` | bytes | Tamaño del archivo |

**MIME types por extensión:**

| Extensión | Content-Type |
|-----------|---------------|
| `.mp3` | audio/mpeg |
| `.wav` | audio/wav |
| `.flac` | audio/flac |
| `.ogg` | audio/ogg |
| `.m4a` | audio/mp4 |
| `.mp4` | video/mp4 |
| `.mkv` | video/x-matroska |
| `.avi` | video/x-msvideo |
| `.webm` | video/webm |
| `.mov` | video/quicktime |

**Ejemplo de uso con fetch:**

```javascript
// Reproducir música
const audio = new Audio('/songs/song-uuid-1234/stream')
audio.play()

// Reproducir video
const video = document.createElement('video')
video.src = '/songs/song-uuid-5678/stream'
video.controls = true
document.body.appendChild(video)
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 404 | Canción no encontrada |

---

### Subir archivo

Sube un nuevo archivo de audio o video.

```
POST /songs/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Form fields:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `file` | binary | Sí | Archivo de audio/video |
| `title` | string | Sí | Título de la canción |
| `artist` | string | Sí | Nombre del artista |
| `album` | string | No | Nombre del álbum |

**Extensiones permitidas:**

- Audio: mp3, wav, flac, ogg, m4a
- Video: mp4, mkv, avi, webm, mov

**Ejemplo con curl:**

```bash
curl -X POST http://localhost:8001/songs/upload \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -F "file=@mi_cancion.mp3" \
  -F "title=Mi Canción" \
  -F "artist=Mi Artista" \
  -F "album=Mi Álbum"
```

**Ejemplo con fetch (JavaScript):**

```javascript
const formData = new FormData()
formData.append('file', fileInput.files[0])
formData.append('title', 'Mi Canción')
formData.append('artist', 'Mi Artista')
formData.append('album', 'Mi Álbum')

fetch('/songs/upload', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
})
```

**Respuesta (201):**
```json
{
  "id": "song-uuid-nuevo",
  "title": "Mi Canción",
  "artist": "Mi Artista",
  "album": "Mi Álbum",
  "duration": 245.5,
  "media_type": "audio",
  "message": "Archivo subido exitosamente"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | Token requerido o inválido |
| 400 | Formato de archivo no permitido |
| 400 | Nombre de archivo requerido |
| 409 | Ya existe un archivo con esa ruta |
| 500 | Error al procesar el archivo |

---

### Eliminar canción

Elimina una canción y su archivo del servidor.

```
DELETE /songs/{song_id}
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `song_id` | string | UUID de la canción a eliminar |

**Respuesta (200):**
```json
{
  "message": "Canción eliminada"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 401 | Token requerido |
| 404 | Canción no encontrada |

---

## 3. Playlists

### Listar playlists

Obtiene todas las playlists del usuario.

```
GET /playlists
Authorization: Bearer {token}
```

**Respuesta (200):**
```json
[
  {
    "id": "playlist-uuid-1234",
    "name": "Mis Favoritas",
    "description": "Las mejores canciones",
    "created_at": "2026-04-21T10:30:00",
    "updated_at": "2026-04-21T12:00:00",
    "songs": [
      {
        "id": "playlist-song-uuid-1",
        "song_id": "song-uuid-1234",
        "position": 0,
        "added_at": "2026-04-21T10:30:00"
      }
    ]
  }
]
```

---

### Crear playlist

Crea una nueva playlist.

```
POST /playlists
Content-Type: application/json
Authorization: Bearer {token}
```

**Parámetros (body):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `name` | string | Sí | Nombre de la playlist |
| `description` | string | No | Descripción opcional |

**Ejemplo de request:**
```json
{
  "name": "Mi Playlist",
  "description": "Canciones para estudiar"
}
```

**Respuesta (201):**
```json
{
  "id": "playlist-uuid-nuevo",
  "name": "Mi Playlist",
  "description": "Canciones para estudiar",
  "created_at": "2026-04-21T10:30:00",
  "updated_at": "2026-04-21T10:30:00",
  "songs": []
}
```

---

### Obtener detalles

Obtiene una playlist específica con todas sus canciones.

```
GET /playlists/{playlist_id}
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `playlist_id` | string | UUID de la playlist |

**Respuesta (200):** Mismo formato que listar, con el array `songs` completo.

**Errores:**

| Código | Descripción |
|--------|-------------|
| 404 | Playlist no encontrada |
| 403 | No tienes permiso para ver esta playlist |

---

### Agregar canción

Agrega una canción a una playlist.

```
POST /playlists/{playlist_id}/songs
Content-Type: application/json
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `playlist_id` | string | UUID de la playlist |

**Parámetros (body):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `song_id` | string | Sí | UUID de la canción a agregar |

**Ejemplo de request:**
```json
{
  "song_id": "song-uuid-1234"
}
```

**Respuesta (201):**
```json
{
  "message": "Canción agregada a la playlist"
}
```

---

### Quitar canción

Quita una canción de una playlist.

```
DELETE /playlists/{playlist_id}/songs/{song_id}
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `playlist_id` | string | UUID de la playlist |
| `song_id` | string | UUID de la canción a quitar |

**Respuesta (200):**
```json
{
  "message": "Canción eliminada de la playlist"
}
```

---

### Eliminar playlist

Elimina una playlist completamente.

```
DELETE /playlists/{playlist_id}
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `playlist_id` | string | UUID de la playlist |

**Respuesta (200):**
```json
{
  "message": "Playlist eliminada"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 404 | Playlist no encontrada |
| 403 | No tienes permiso para eliminar esta playlist |

---

## 4. Favoritos

### Listar favoritos

Obtiene todas las canciones favoritas del usuario.

```
GET /favorites
Authorization: Bearer {token}
```

**Respuesta (200):**
```json
[
  {
    "id": "favorite-uuid-1234",
    "user_id": "user-uuid-1234",
    "song_id": "song-uuid-5678",
    "added_at": "2026-04-21T10:30:00"
  }
]
```

---

### Agregar a favoritos

Marca una canción como favorita.

```
POST /favorites
Content-Type: application/json
Authorization: Bearer {token}
```

**Parámetros (body):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `song_id` | string | Sí | UUID de la canción |

**Ejemplo de request:**
```json
{
  "song_id": "song-uuid-1234"
}
```

**Respuesta (201):**
```json
{
  "id": "favorite-uuid-nuevo",
  "user_id": "user-uuid-1234",
  "song_id": "song-uuid-1234",
  "added_at": "2026-04-21T10:30:00"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 400 | La canción ya está en favoritos |
| 404 | Canción no encontrada |

---

### Quitar de favoritos

Quita una canción de favoritos.

```
DELETE /favorites/{song_id}
Authorization: Bearer {token}
```

**Parámetros de path:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `song_id` | string | UUID de la canción |

**Respuesta (200):**
```json
{
  "message": "Canción eliminada de favoritos"
}
```

---

## 5. YouTube

Descarga videos y audio desde YouTube.

### Buscar en YouTube

Busca videos en YouTube por término de búsqueda.

```
GET /youtube/search?q=rock&limit=10
```

**Query parameters:**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `q` | string | Sí | Término de búsqueda |
| `limit` | integer | 10 | Cantidad de resultados |

**Respuesta (200):**
```json
[
  {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "channel": "RickAstleyVEVO",
    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "duration": 213,
    "views": 1500000000
  }
]
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 500 | Error al conectar con YouTube |

---

### Descargar desde YouTube

Descarga y convierte un video de YouTube como audio o video.

```
POST /youtube/download
Content-Type: application/json
Authorization: Bearer {token}
```

**Parámetros (body):**

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `video_id` | string | Sí | ID del video de YouTube |
| `format` | string | Sí | Formato de salida: m4a, mp3, wav, flac, ogg, mp4, mkv, webm |
| `quality` | string | No | Calidad de audio: 320, 256, 128 (kbps) o video: 1080p, 720p, 480p |
| `title` | string | No | Título personalizado (usa el del video si no se indica) |
| `artist` | string | No | Artista personalizado (usa el canal del video si no se indica) |

**Formatos disponibles:**

| Formato | Tipo | Descripción |
|---------|------|-------------|
| `mp3` | audio | MP3 (más popular) |
| `m4a` | audio | M4A AAC |
| `wav` | audio | WAV sin pérdida |
| `flac` | audio | FLAC sin pérdida |
| `ogg` | audio | OGG Vorbis |
| `mp4` | video | MP4 H.264 |
| `mkv` | video | MKV |
| `webm` | video | WebM |

**Ejemplo de request:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "format": "mp3",
  "quality": "320",
  "title": "Never Gonna Give You Up",
  "artist": "Rick Astley"
}
```

**Ejemplo con curl:**

```bash
curl -X POST http://localhost:8001/youtube/download \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"video_id": "dQw4w9WgXcQ", "format": "mp3", "quality": "320"}'
```

**Respuesta (201):**
```json
{
  "id": "song-uuid-nuevo",
  "title": "Never Gonna Give You Up",
  "artist": "Rick Astley",
  "album": null,
  "duration": 213.0,
  "media_type": "audio",
  "created_at": "2026-04-21T10:30:00"
}
```

**Errores:**

| Código | Descripción |
|--------|-------------|
| 400 | Formato no soportado |
| 401 | Token requerido o inválido |
| 500 | Error al descargar desde YouTube |

**Nota:** Este endpoint requiere que `yt-dlp` esté instalado:

```bash
pip install yt-dlp
```

---

## 6. Códigos de respuesta

| Código | Significado | Descripción |
|--------|------------|-------------|
| 200 | OK | Request exitosa |
| 201 | Created | Recurso creado |
| 400 | Bad Request | Solicitud inválida |
| 401 | Unauthorized | Token requerido o inválido |
| 403 | Forbidden | Sin permisos |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto (duplicado) |
| 500 | Internal Server Error | Error en el servidor |

---

## 7. Documentación interactiva

Prueba la API directamente desde el navegador:

| Herramienta | URL |
|------------|-----|
| Swagger UI | http://localhost:8001/docs |
| ReDoc | http://localhost:8001/redoc |

Ambas interfaces permiten:
- Ver todos los endpoints disponibles
- Probar llamadas directamente
- Observar esquemas de respuesta
- Autenticarse con JWT

---

## Resumen de endpoints

| Endpoint | Método | Autenticado | Descripción |
|----------|--------|------------|-------------|
| `/health` | GET | No | Health check |
| `/` | GET | No | Frontend SPA |
| `/auth/register` | POST | No | Crear usuario |
| `/auth/login` | POST | No | Iniciar sesión |
| `/songs` | GET | Sí | Listar canciones |
| `/songs/search` | GET | Sí | Buscar canciones |
| `/songs/{id}` | GET | Sí | Obtener canción |
| `/songs/{id}/stream` | GET | No | Reproducir archivo |
| `/songs/upload` | POST | Sí | Subir archivo |
| `/songs/{id}` | DELETE | Sí | Eliminar canción |
| `/playlists` | GET | Sí | Listar playlists |
| `/playlists` | POST | Sí | Crear playlist |
| `/playlists/{id}` | GET | Sí | Obtener playlist |
| `/playlists/{id}/songs` | POST | Sí | Agregar canción |
| `/playlists/{id}/songs/{song_id}` | DELETE | Sí | Quitar canción |
| `/playlists/{id}` | DELETE | Sí | Eliminar playlist |
| `/favorites` | GET | Sí | Listar favoritos |
| `/favorites` | POST | Sí | Agregar favorito |
| `/favorites/{song_id}` | DELETE | Sí | Quitar favorito |
| `/youtube/search` | GET | No | Buscar en YouTube |
| `/youtube/download` | POST | Sí | Descargar desde YouTube |