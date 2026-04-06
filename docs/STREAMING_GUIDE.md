# Guía de Streaming — MelodyBox

## Cómo funciona

```
Cliente → GET /songs/{id}/stream → Servidor → FileResponse (audio/mpeg, video/mp4, etc.)
```

`FileResponse` de FastAPI soporta automáticamente **byte-range requests**. El navegador:

1. Pide los primeros bytes del archivo
2. Empieza a reproducir inmediatamente
3. Pide más bytes según necesita
4. Permite saltar a cualquier punto sin descargar todo

## Implementación

**Backend** (`app/routes/songs.py`):
```python
MIME_TYPES = {
    "mp3": "audio/mpeg", "wav": "audio/wav", "flac": "audio/flac",
    "ogg": "audio/ogg", "m4a": "audio/mp4", "mp4": "video/mp4",
    "mkv": "video/x-matroska", "avi": "video/x-msvideo",
    "webm": "video/webm", "mov": "video/quicktime",
}

@router.get("/{song_id}/stream")
def stream_song(song_id: str, db: Session = Depends(get_db)):
    song = SongService.get_song(db, song_id)
    ext = Path(song.file_path).suffix.lower().lstrip(".")
    media_type = MIME_TYPES.get(ext, "application/octet-stream")
    return FileResponse(song.file_path, media_type=media_type, headers={
        "Accept-Ranges": "bytes",
        "Cache-Control": "public, max-age=3600"
    })
```

**Frontend** (`player.js`):
```javascript
async play(media) {
    this.isVideo = media.media_type === 'video';
    const streamUrl = api.streamUrl(media.id);
    if (this.isVideo) {
        this.videoEl.src = streamUrl;
        this.videoEl.play();
    } else {
        this.audio.src = streamUrl;
        this.audio.play();
    }
}
```

## Formatos soportados

| Audio | Video |
|---|---|
| MP3, WAV, FLAC, OGG, M4A | MP4, MKV, AVI, WebM, MOV |
