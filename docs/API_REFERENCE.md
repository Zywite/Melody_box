# Referencia de API — MelodyBox

**Base URL:** `http://localhost:8001`
**Autenticación:** Bearer Token (JWT)

---

## Endpoints públicos

### Health Check

```
GET /health
```

**Respuesta:**
```json
{ "status": "healthy" }
```

### Root

```
GET /
```

Devuelve el `index.html` del frontend.

### Registro

```
POST /auth/register
Content-Type: application/json
```

**Body:**
```json
{
  "username": "miusuario",
  "email": "mi@email.com",
  "password": "mi_contraseña"
}
```

**Respuesta 200:**
```json
{
  "id": "a1b2c3d4-...",
  "username": "miusuario",
  "email": "mi@email.com",
  "is_active": true,
  "created_at": "2026-04-05T00:00:00"
}
```

**Errores:**
| Código | Detalle |
|---|---|
| 400 | El email ya está registrado |
| 400 | El nombre de usuario ya existe |

### Login

```
POST /auth/login
Content-Type: application/json
```

**Body:**
```json
{
  "email": "mi@email.com",
  "password": "mi_contraseña"
}
```

**Respuesta 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "username": "miusuario"
}
```

**Errores:**
| Código | Detalle |
|---|---|
| 401 | Email o contraseña incorrectos |

---

## Endpoints de canciones

### Listar canciones

```
GET /songs?skip=0&limit=100
```

**Respuesta 200:**
```json
[
  {
    "id": "uuid",
    "title": "Nombre de canción",
    "artist": "Artista",
    "album": "Álbum",
    "duration": 245.5,
    "media_type": "audio",
    "created_at": "2026-04-05T00:00:00"
  }
]
```

### Buscar canciones

```
GET /songs/search?q=rock
```

Busca por título, artista o álbum.

**Respuesta 200:** Lista de canciones coincidentes.

### Obtener canción individual

```
GET /songs/{song_id}
```

**Respuesta 200:** Objeto `SongResponse`.

**Errores:**
| Código | Detalle |
|---|---|
| 404 | Canción no encontrada |

### Reproducir (stream)

```
GET /songs/{song_id}/stream
```

Devuelve el archivo de audio/video con soporte de byte-range.

**Headers de respuesta:**
```
Content-Type: audio/mpeg    (para MP3)
Content-Type: video/mp4     (para MP4)
Accept-Ranges: bytes
Cache-Control: public, max-age=3600
```

**MIME types por formato:**

| Extensión | Content-Type |
|---|---|
| `.mp3` | `audio/mpeg` |
| `.wav` | `audio/wav` |
| `.flac` | `audio/flac` |
| `.ogg` | `audio/ogg` |
| `.m4a` | `audio/mp4` |
| `.mp4` | `video/mp4` |
| `.mkv` | `video/x-matroska` |
| `.avi` | `video/x-msvideo` |
| `.webm` | `video/webm` |
| `.mov` | `video/quicktime` |

### Subir archivo

```
POST /songs/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}
```

**Form fields:**
| Campo | Tipo | Requerido |
|---|---|---|
| `file` | File | Sí |
| `title` | String | Sí |
| `artist` | String | Sí |
| `album` | String | No |

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:8001/songs/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@mi_cancion.mp3" \
  -F "title=Mi Canción" \
  -F "artist=Mi Artista" \
  -F "album=Mi Álbum"
```

**Respuesta 200:**
```json
{
  "id": "uuid",
  "title": "Mi Canción",
  "artist": "Mi Artista",
  "album": "Mi Álbum",
  "duration": 245.5,
  "media_type": "audio",
  "message": "Archivo subido exitosamente"
}
```

**Errores:**
| Código | Detalle |
|---|---|
| 401 | Token requerido / inválido |
| 400 | Formato no permitido |
| 400 | Nombre de archivo requerido |
| 409 | Ya existe un archivo con esa ruta |
| 500 | Error al subir el archivo |

### Eliminar canción

```
DELETE /songs/{song_id}
Authorization: Bearer {token}
```

**Respuesta 200:**
```json
{ "message": "Canción eliminada" }
```

**Errores:**
| Código | Detalle |
|---|---|
| 401 | Token requerido |
| 404 | Canción no encontrada |

---

## Endpoints de playlists

### Obtener playlists del usuario

```
GET /playlists
Authorization: Bearer {token}
```

**Respuesta 200:**
```json
[
  {
    "id": "uuid",
    "name": "Mi Playlist",
    "description": "Descripción",
    "created_at": "2026-04-05T00:00:00",
    "updated_at": "2026-04-05T00:00:00",
    "songs": [
      {
        "id": "uuid",
        "song_id": "uuid",
        "position": 0,
        "added_at": "2026-04-05T00:00:00"
      }
    ]
  }
]
```

### Crear playlist

```
POST /playlists
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Mi Playlist",
  "description": "Descripción opcional"
}
```

**Respuesta 200:** Objeto `PlaylistResponse`.

### Obtener playlist detallada

```
GET /playlists/{playlist_id}
Authorization: Bearer {token}
```

**Respuesta 200:** `PlaylistResponse` con lista de canciones.

**Errores:**
| Código | Detalle |
|---|---|
| 404 | Playlist no encontrada |
| 403 | No tienes permiso |

### Agregar canción a playlist

```
POST /playlists/{playlist_id}/songs
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{ "song_id": "uuid-de-la-cancion" }
```

**Respuesta 200:**
```json
{ "message": "Canción agregada a la playlist" }
```

### Eliminar canción de playlist

```
DELETE /playlists/{playlist_id}/songs/{song_id}
Authorization: Bearer {token}
```

### Eliminar playlist

```
DELETE /playlists/{playlist_id}
Authorization: Bearer {token}
```

---

## Endpoints de favoritos

### Obtener favoritos

```
GET /favorites
Authorization: Bearer {token}
```

**Respuesta 200:**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "song_id": "uuid",
    "added_at": "2026-04-05T00:00:00"
  }
]
```

### Agregar a favoritos

```
POST /favorites
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{ "song_id": "uuid-de-la-cancion" }
```

**Respuesta 200:** Objeto `FavoriteResponse`.

**Errores:**
| Código | Detalle |
|---|---|
| 400 | La canción ya está en favoritos |
| 404 | Canción no encontrada |

### Quitar de favoritos

```
DELETE /favorites/{song_id}
Authorization: Bearer {token}
```

**Respuesta 200:**
```json
{ "message": "Canción eliminada de favoritos" }
```

---

## Autenticación

Todos los endpoints protegidos requieren el header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Obtener el token

1. Haz login con `POST /auth/login`
2. Copia el valor de `access_token` de la respuesta
3. Úsalo en el header `Authorization`

### Duración del token

Por defecto: **1440 minutos** (24 horas). Configurable en `.env`.

---

## Códigos de error

| Código | Significado |
|---|---|
| 200 | Éxito |
| 400 | Solicitud incorrecta (validación) |
| 401 | No autenticado o token inválido |
| 403 | Sin permisos |
| 404 | Recurso no encontrado |
| 409 | Conflicto (duplicado) |
| 500 | Error interno del servidor |

---

## Interactiva

La documentación interactiva está disponible en:

```
http://localhost:8001/docs     → Swagger UI
http://localhost:8001/redoc    → ReDoc
```
