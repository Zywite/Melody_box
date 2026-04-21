# Guía de Streaming — MelodyBox

Esta guía explica cómo funciona el sistema de streaming de audio y video en MelodyBox.

---

## Tabla de contenido

1. [Cómo funciona](#1-cómo-funciona)
2. [Byte-range requests](#2-byte-range-requests)
3. [Implementación](#3-implementación)
4. [Formatos soportados](#4-formatos-soportados)
5. [Casos de error](#5-casos-de-error)
6. [Optimización](#6-optimización)
7. [Ejemplos de uso](#7-ejemplos-de-uso)

---

## 1. Cómo funciona

El streaming permite reproducir audio/video sin descargar el archivo completo.

```
Cliente (navegador)                    Servidor (FastAPI)
      │                                      │
      │──── GET /songs/{id}/stream ──────────►│
      │◄──── Primeros bytes (Range: 0-)───────│
      │──── Reproduciendo...────────────────►│
      │──── GET /songs/{id}/stream ──────────►│
      │    Range: 5000000-10000000            │
      │◄──── Bytes 5MB a 10MB ────────────────│
      │──── (reproduce el segmento) ────────►│
      │──── ...siguiente rango ─────────────►│
```

### Diferencia entre descarga y streaming

| Aspecto | Descarga completa | Streaming |
|---------|------------------|-----------|
| Tiempo inicial | Esperar descarga total | Reproducción inmediata |
| Memoria | Todo el archivo en RAM | Solo segmentos pequeños |
| Seek | Descargar de nuevo | Salto directo |
| Uso de red | 1 conexión | Múltiples conexiones parciales |

---

## 2. Byte-range requests

El header `Range` permite pedir solo partes del archivo.

### Solicitud del cliente

```
GET /songs/{id}/stream HTTP/1.1
Host: localhost:8001
Range: bytes=0-
```

### Respuesta del servidor

```
HTTP/1.1 206 Partial Content
Content-Type: audio/mpeg
Content-Length: 5000000
Accept-Ranges: bytes
Content-Range: bytes 0-4999999/10000000

[.Bytes 0 a 5,000,000 del archivo...]
```

### Cómo lo usa el navegador

1. Pide los primeros bytes (típicamente ~1MB)
2. Empieza a reproducir mientras descarga
3. Según avanza, pide más segmentos
4. Al hacer seek, pide el rango específico

### Ventajas

- **Inicio rápido**: No espera descargar todo
- **Seek instantáneo**: Salta a cualquier punto
- **Menor uso de memoria**: Solo lo necesario
- **Ahorro de ancho de banda**: No descarga lo que no escucha

---

## 3. Implementación

### Backend — FastAPI (`src/app/routes/songs.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

router = APIRouter(prefix="/songs", tags=["songs"])

# Mapa de tipos MIME por extensión
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
    # 1. Buscar la canción en la base de datos
    song = SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    # 2. Verificar que el archivo existe
    file_path = str(Path(song.file_path).resolve())
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    # 3. Determinar el tipo MIME por extensión
    ext = Path(file_path).suffix.lower().lstrip(".")
    media_type = MIME_TYPES.get(ext, "application/octet-stream")

    # 4. Devolver FileResponse con byte-range
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={
            "Accept-Ranges": "bytes",          # Indica soporte
            "Cache-Control": "public, max-age=3600"  # Cache 1 hora
        }
    )
```

**Clave:** `FileResponse` de FastAPI soporta automáticamente:
- `Range` header del cliente
- `206 Partial Content` con el segmento pedido
- `Content-Range` indicando posición/total

---

### Frontend — Vue/Pinia (`frontend/src/stores/player.js`)

```javascript
function play(song) {
  currentSong.value = song
  isPlaying.value = true

  if (song.media_type === 'video') {
    // Video: usar elemento video
    videoElement.value.src = `/songs/${song.id}/stream`
    videoElement.value.play()
  } else {
    // Audio: usar elemento audio
    audio.value.src = `/songs/${song.id}/stream`
    audio.value.play()
  }
}

// Controles del reproductor
function seek(percent) {
  if (audio.value && duration.value) {
    // Calcular posición en segundos
    audio.value.currentTime = (percent / 100) * duration.value
    // El navegador automáticamente pide el nuevo rango
  }
}
```

---

## 4. Formatos soportados

### Audio

| Extensión | MIME Type | Notas |
|----------|----------|-------|
| `.mp3` | audio/mpeg | Más compatible |
| `.wav` | audio/wav | Sin compresión, grande |
| `.flac` | audio/flac | Sin pérdida |
| `.ogg` | audio/ogg | Libre |
| `.m4a` | audio/mp4 | AAC |

### Video

| Extensión | MIME Type | Notas |
|----------|----------|-------|
| `.mp4` | video/mp4 | H.264, más compatible |
| `.mkv` | video/x-matroska | Containers flexibles |
| `.avi` | video/x-msvideo |legacy |
| `.webm` | video/webm | VP8/VP9 |
| `.mov` | video/quicktime | QuickTime |

---

## 5. Casos de error

| Error | Causa | Solución |
|-------|------|---------|
| `404 Canción no encontrada` | ID incorrecto | Verificar el ID de la canción |
| `404 Archivo no encontrado` | Archivo eliminado del disco | Volver a subir |
| `404 Invalid Range` | Rango fuera del archivo | Buscar a posición válida |
| `500 Error de servidor` | Archivo corrupto | Eliminar y volver a subir |
| `Media src not loaded` | CORS | Verificar headers CORS |

### Verificar problemas

```bash
# 1. Ver si el archivo existe
ls -la src/music_storage/

# 2. Probar streaming con curl
curl -I http://localhost:8001/songs/{id}/stream

# 3. Ver rango específico
curl -H "Range: bytes=0-1023" http://localhost:8001/songs/{id}/stream
```

---

## 6. Optimización

### Cache del navegador

```python
# TTL de 1 hora (3600 segundos)
headers={
    "Cache-Control": "public, max-age=3600"
}
```

### Recomendaciones de tamaño

| Tipo | Tamaño óptimo |
|------|----------------|
| Audio MP3 | 3-10 MB por canción |
| Audio FLAC | 20-50 MB por canción |
| Video | 50-500 MB por archivo |

### Red local

- El streaming funciona mejor en red local (baja latencia)
- En internet, considerar una CDN para archivos grandes

---

## 7. Ejemplos de uso

### Desde el navegador

```javascript
// Reproducir audio
const audio = new Audio('/songs/{song_id}/stream')
audio.play()

// Con controles
const audio = new Audio('/songs/{song_id}/stream')
audio.controls = true
document.body.appendChild(audio)

// Seek al 50%
audio.addEventListener('loadedmetadata', () => {
  audio.currentTime = audio.duration * 0.5
})
```

### Con curl

```bash
# Ver headers de streaming
curl -I http://localhost:8001/songs/{song_id}/stream

# Solicitar rango específico (primeros 1MB)
curl -H "Range: bytes=0-1048575" \
     http://localhost:8001/songs/{song_id}/stream \
     -o primero.bin
```

### Desde la API

```javascript
// Fetch API
const response = await fetch(`/songs/${songId}/stream`)
const blob = await response.blob()
const url = URL.createObjectURL(blob)
```

---

## Flujo completo

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE STREAMING                      │
├─────────────────────────────────────────────────────────────┤
│                                                      │
│  Usuario hace click en canción                          │
│         │                                             │
│         ▼                                             │
│  player.js → fetch(/songs/{id}/stream)                   │
│         │                                             │
│         ▼                                             │
│  FastAPI → SongService.get_song() → BD                  │
│         │                                             │
│         ▼                                             │
│  FileResponse con archivo + headers Range               │
│         │                                             │
│         ▼                                             │
│  Navegador recibe bytes,almacena en buffer              │
│         │                                             │
│         ▼                                             │
│  Reproduce mientras recibe más segmentos                 │
│         │                                             │
│         ▼                                             │
│  Usuario hace seek → nuevo Range request                │
│         │                                             │
│         ▼                                             │
│  FastAPI → retorna segmento específico                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```