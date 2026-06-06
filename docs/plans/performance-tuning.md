---
plan name: performance-tuning
plan description: Full-stack performance optimization
plan status: done
---

## Idea
Optimize MelodyBox for real-world performance. The clean-code refactor improved maintainability; now address the actual runtime bottlenecks. 

Key areas:
- **Backend**: CPU-bound FFT/yt-dlp blocking event loops (worker.py + routes), full audio file loaded in memory by librosa, missing DB indexes on FK columns, leading-wildcard search scanning full tables, `get_current_user` hitting DB per request, GZip re-compressing already-compressed audio streams, eager engine creation stalling startup, and `analyze_all_songs_fft` blocking a uvicorn thread for minutes.
- **Frontend**: No virtual scrolling in song lists (DOM explosion >300 songs), per-pixel `fillRect` spectrogram canvas blocking main thread for 100s of ms, no `loading="lazy"` on any images causing 200+ concurrent image requests, universal CSS `* { transition: ... }` causing style recalc overhead on every DOM change, redundant API calls (AppSidebar fetching playlists directly, full favorite refetch on each toggle), no brotli compression, too many Google Fonts, stale data on view re-entry due to no cache in songs store, KeepAlive caching large views indefinitely.
- DevOps: Add `connect_timeout=3` to engine creation to prevent startup stalls when DB is unreachable.

All changes must pass 133 existing backend tests.

## Implementation
- [x] **Backend core** — `app.core.ttl_cache` (LRU+TTL genérico) y `app.core.selective_gzip` (ASGI middleware que solo gzipea content-types comprimibles) + nuevas constantes en `app.core.constants` (`MAX_FFT_INPUT_DURATION_SECONDS`, `FFT_TARGET_SAMPLE_RATE`, `USER_LOOKUP_CACHE_TTL_SECONDS`, `USER_LOOKUP_CACHE_MAXSIZE`).
- [x] **Engine connect timeout** — `app.core.database` añade `connect_timeout=3` a la URL del engine (libpq) y configura `SessionLocal(expire_on_commit=False)` para que los ORM cacheados sobrevivan al cierre de la sesión.
- [x] **Selective GZip en main** — `app.main` reemplaza `GZipMiddleware` por `SelectiveGZipMiddleware(minimum_size=1000)`.
- [x] **Database indexes** — `app.models.music` añade `index=True` en `Playlist.user_id`, `PlaylistSong.playlist_id`, `PlaylistSong.song_id`, `Favorite.user_id`, `Favorite.song_id`. `app.models.task` añade `Index` en `song_id` y un composite `(type, status)`.
- [x] **User lookup cache** — `app.routes.dependencies` memoiza `get_current_user` y `get_optional_user` con el `TTLCache` (maxsize=1024, ttl=30s) + helpers `invalidate_user_cache` / `clear_user_cache`.
- [x] **Search pagination** — `routes/songs.search_songs` y `services/song_service.search_songs` aceptan `skip` (default 0) y `limit` (default 100, máx 200).
- [x] **Async FFT + analyze-all** — `services/fft_service` baja `librosa.load(sr=22050, duration=600)` para acotar memoria; `compute_and_store` y el fallback de `routes/songs.get_song_fft` corren en `asyncio.to_thread`; `routes/songs.analyze_all_songs_fft` ahora enqueuea un `Task` + arq job por canción y retorna inmediato con `{message, enqueued, failed}`.
- [x] **Async yt-dlp en worker** — `src.worker.download_youtube` envuelve `yt_dlp.YoutubeDL.extract_info` en `asyncio.to_thread` para no bloquear el event loop.
- [x] **Frontend polish** — `assets/main.css` pierde la transición universal; `<img>` en `PlaylistCard`/`SongCard`/`YouTubeDownloader` ganan `loading="lazy"`; nuevo `components/common/VirtualList.vue` usado por `FFTView`; stores `favorites.js` y `songs.js` adoptan cache SWR en `sessionStorage` (TTL 30s) + updates optimistas con rollback; `utils/fftCanvas` usa canvas HiDPI y `ImageData` para el espectrograma; `index.html` recorta las Google Fonts; `vite.config.js` añade el plugin de brotli.
- [x] **Scaffolding TypeScript** — `tsconfig.json` con `strict: true` y alias `@/*`; `package.json` añade `typescript` y `vue-tsc` como devDeps (migración gradual, los .js existentes siguen como están).
- [x] **Build artifacts** — `frontend/dist` regenerado con los nuevos hashes, `.gz` actualizados y `.br` (brotli) emitidos por primera vez.

## Required Specs
<!-- SPECS_START -->
- performance-spec
<!-- SPECS_END -->