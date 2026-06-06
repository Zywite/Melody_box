# Spec: performance-spec

Scope: feature

# Performance Optimization Spec

This spec describes the design that was actually shipped for the
`performance-tuning` plan. Sections that originally proposed a different
approach (process-pool executor, `vue-virtual-scroller`, `cachetools`,
etc.) have been rewritten to match the implementation: `asyncio.to_thread`
per call, a custom `TTLCache`, an `Index()`-on-FK strategy, a
content-type-based selective GZip middleware, and a custom
`VirtualList.vue` component.

## Backend

### 1. Async CPU-Bound Work via `asyncio.to_thread`
**Problem**: `worker.py` (compute_fft, download_youtube) and
`routes/songs.py` (get_song_fft fallback) call CPU-bound operations
(librosa, yt-dlp) directly in the async context, blocking the event
loop until the work finishes.

**Solution**:
- Use `asyncio.to_thread(...)` per call site (no module-level
  `ThreadPoolExecutor`). The default executor in the loop is reused.
- Call sites:
  - `services/fft_service.compute_and_store` wraps
    `compute_fft_from_file(song.file_path)`.
  - `routes/songs.get_song_fft` wraps the synchronous fallback used when
    the arq worker is unavailable.
  - `worker.download_youtube` wraps `yt_dlp.YoutubeDL.extract_info`.

### 2. FFT Memory Bounding
**Problem**: `librosa.load(file_path, sr=None, mono=True)` loads the
entire audio file as float32 in memory (~176 KB/s mono at 44.1 kHz;
~106 MB for a 10-minute track).

**Solution**:
- Pass `sr=FFT_TARGET_SAMPLE_RATE` (22050) so librosa downsamples on
  load — acceptable for FFT visualization.
- Pass `duration=MAX_FFT_INPUT_DURATION_SECONDS` (600s = 10 min) so
  very long tracks are truncated before the STFT is taken. ~13 MB cap
  per call.
- The cached `fft_data` is still consulted before re-computing (see
  `redis_helper`).

### 3. Database Indexes on Foreign Keys
**Problem**: PostgreSQL does not auto-index foreign keys; playlist
joins, favorite lookups, and task-by-song queries were full-scanning.

**Solution**:
- `app.models.music`: add `index=True` to the FK `Column(...)`
  declarations (idiomatic SQLAlchemy 2.x; no `__table_args__` block
  needed for single-column indexes):
  - `Playlist.user_id`
  - `PlaylistSong.playlist_id`
  - `PlaylistSong.song_id`
  - `Favorite.user_id`
  - `Favorite.song_id`
- `app.models.task`: keep `index=True` on `song_id` and add a
  composite `Index("ix_task_type_status", "type", "status")` via
  `__table_args__` (the only place we use it).

### 4. Search Pagination
**Problem**: `search_songs` returns all matches with no LIMIT.

**Solution**: `routes/songs.search_songs` and
`services/song_service.search_songs` accept `skip` (default
`DEFAULT_SONGS_PAGE_SKIP` = 0, `>= 0`) and `limit` (default
`DEFAULT_SONGS_PAGE_SIZE` = 100, `1 <= limit <= 200`). The leading-`%`
`ILIKE` is unchanged.

### 5. User Lookup Cache (custom `TTLCache`)
**Problem**: `get_current_user` runs a DB query on every authenticated
request, even though the user row rarely changes during a session.

**Solution**:
- New module `app.core.ttl_cache.TTLCache`: thread-safe LRU + per-entry
  TTL (`OrderedDict` + `threading.Lock`, `move_to_end` on access).
- Constants in `app.core.constants`:
  - `USER_LOOKUP_CACHE_TTL_SECONDS = 30`
  - `USER_LOOKUP_CACHE_MAXSIZE = 1024`
- `routes/dependencies.py` instantiates a module-level
  `_user_cache: TTLCache[User] = TTLCache(maxsize=..., ttl_seconds=...)`
  and consults it before/after the DB lookup.
- Helpers `invalidate_user_cache(user_id)` and `clear_user_cache()` are
  exposed for tests and admin flows.
- Why not `cachetools`? The custom class is dependency-free, matches
  the project's "no new third-party deps" rule for backend core, and
  makes the test surface obvious.

### 6. Engine Connect Timeout
**Problem**: `core/database.py` builds the engine at import with no
connection timeout, so a bad `DATABASE_URL` stalls the whole process at
startup.

**Solution**: Append `connect_timeout=3` to the engine URL
(libpq style) before calling `create_engine`, e.g.
`postgresql+psycopg2://user:pw@host/db?connect_timeout=3`. The
3-second budget matches the 3s probe we run via `engine.connect() +
SELECT 1` for the SQLite fallback path. No `connect_args` dict is
needed because the URL is the canonical place for libpq options.

### 7. `analyze_all_songs_fft` Refactor
**Problem**: The endpoint was a synchronous `def` that ran librosa in
a loop on the uvicorn thread, blocking the worker for minutes for
large libraries.

**Solution**:
- Make the route `async def`; for each song without `fft_data`:
  1. Create a `Task` row (`type=TASK_TYPE_FFT`, `status=PENDING`,
     `song_id=...`).
  2. `db.commit()` so the task is visible to the worker.
  3. `await enqueue_job(JOB_NAME_COMPUTE_FFT, song.id, _job_id=task.id)`.
  4. If enqueue returned `None` (Redis down), mark the task as FAILED
     and bump `failed`.
- Return immediately with
  `{ "message": "Analyzed N songs, M failed", "enqueued": N, "failed": M }`.
- The `get_song_fft` route keeps a synchronous fallback (now also
  running in `asyncio.to_thread`) for the case where the worker is
  unavailable but a single song still needs analysis.

### 8. Selective GZip Middleware (Content-Type Based)
**Problem**: Stock `GZipMiddleware` re-compresses already-compressed
audio streams served by `FileResponse` (mp3, mp4, webm, jpg, png, ...),
wasting CPU and growing the body for those payloads.

**Solution**: New ASGI middleware `app.core.selective_gzip.SelectiveGZipMiddleware`
that:
- Skips compression entirely when the client does not advertise
  `Accept-Encoding: gzip`.
- On the first `http.response.start` message, reads the `Content-Type`
  header and decides whether the payload is compressible
  (`text/*`, `application/json`, `application/javascript`,
  `application/xml`, `application/x-yaml`, `image/svg+xml`).
- Buffers the body only when the content type is compressible and the
  compressed size is smaller than the raw size; otherwise forwards
  every message verbatim, preserving FastAPI's `FileResponse` /
  `StreamingResponse` zero-copy streaming for audio/video.
- Strategy is content-type-based, not path-based, so non-audio endpoints
  with unusual paths still get gzipped correctly.

---

## Frontend

### 9. Virtual Scrolling via Custom `VirtualList.vue`
**Problem**: `LibraryView.vue` and `FFTView.vue` render all `<SongCard>`
in a flat `v-for`; DOM explodes beyond 300 songs and the FFT view
becomes unresponsive during the FFT refresh.

**Solution**:
- New component `frontend/src/components/common/VirtualList.vue`
  implementing a fixed-height-row virtualizer (no third-party
  dependency, since we don't want to add `vue-virtual-scroller`):
  - Props: `items`, `itemHeight` (required), `overscan` (default 6),
    `keyField` (default `'id'`).
  - Renders only the rows that fall inside the viewport
    (`Math.floor(scrollTop / itemHeight) - overscan` to
    `+ overscan`).
  - Uses a `ResizeObserver` to track the viewport height.
- `views/FFTView.vue` swaps the `v-for` over `songs` for
  `<VirtualList :items="songs" :item-height="60" :key-field="'id'">`.
- LibraryView migration is tracked separately in the
  `frontend-polish` plan (item 3).
- Pagination stays unchanged (50 per page, "load more" appends).

### 10. Spectrogram Canvas via `ImageData`
**Problem**: `fftCanvas.js:drawSpectrogramCanvas` issues
~`graphWidth * numFreqBins` `fillRect` calls per frame; for a 730×160
graph that is ~256,000 calls and blocks the main thread for hundreds
of milliseconds.

**Solution**:
- Build a `Uint8ClampedArray` via `ctx.createImageData(graphWidth, graphHeight)`.
- Loop once over `x` and `y` pixels; for each pixel, sample the
  matching `spectrogram` bin and write RGBA bytes into the typed array.
- Call `ctx.putImageData(imageData, graphLeft, graphTop)` once.
- `getColor` was renamed to `getColorRGB` and now returns a 4-tuple
  `[r, g, b, a]` instead of a CSS string, to avoid the per-pixel
  string formatting that `fillRect` would otherwise incur.
- Result: ~250× fewer draw calls and no per-pixel string allocation.

### 11. Lazy Image Loading
**Problem**: All `<img>` tags load eagerly; mounting `LibraryView`
kicks off 200+ concurrent image requests, saturating the network on
the LAN.

**Solution**:
- Add `loading="lazy"` to:
  - `components/common/PlaylistCard.vue` (cover image)
  - `components/common/SongCard.vue` (artwork)
  - `components/common/YouTubeDownloader.vue` (search-result thumbnails)
- `alt` text and `@error` handling were already present, so no
  further changes.

### 12. Store Optimizations (SWR + Optimistic)
**Problem**: The favorites and songs stores refetched everything on
every mutation/view re-entry, hammering the API and making toggles
feel slow.

**Solution**:
- `stores/favorites.js`:
  - 30-second `sessionStorage` SWR cache (`FAVORITES_CACHE_KEY =
    'melodybox:cache:favorites:v1'`, `FAVORITES_STALE_AFTER_MS =
    30_000`).
  - `fetchFavorites({ force })` reuses the cache when fresh and
    restores from `sessionStorage` on re-entry.
  - `addFavorite(songId, song?)` and `removeFavorite(songId)` perform
    optimistic local updates with snapshot+rollback on error.
  - `pendingSongIds: Set<string>` guards against double-fire.
  - New helpers: `isFavorite(id)`, `toggleFavorite(id, song?)`,
    `invalidate()`.
- `stores/songs.js`:
  - Same 30s SWR pattern (`SONGS_CACHE_KEY`,
    `SONGS_STALE_AFTER_MS`, `SONGS_STALE_AFTER_MS`).
  - `_isStale(page, limit)` also returns `true` when the requested
    `page`/`limit` differs from the cached one.
  - New helpers: `upsertSong(song)`, `removeSongLocal(id)`,
    `invalidate()` for the bulk-analyze flow and admin actions.
- The proposed `AppSidebar.vue` change was **not** shipped in this
  round; it remains a candidate for a follow-up.

### 13. CSS Performance
**Problem**: The universal `* { transition: ... }` rule in
`main.css` forced style recalc on every DOM change.

**Solution**:
- Removed the universal rule (the kawaii theme's per-component
  transitions are still in effect because each component defines its
  own scoped transition).
- The `.transition-colors` utility class proposed in the original
  draft was **not** added: no component was found that needed a
  generic class and was missing the transition it needed.

### 14. Vite Build Optimizations
**Problem**: No brotli compression; the Google Fonts URL loaded 7
families when only 5 were used in the kawaii theme.

**Solution**:
- `vite.config.js` adds a second `vite-plugin-compression` instance
  for brotli:
  `compression({ algorithm: 'brotliCompress', threshold: 1024, filename: '[path][base].br' })`.
- `index.html` keeps `Nunito`, `Mochiy Pop P One`, `JetBrains Mono`,
  `DM Sans`, `Space Grotesk`; **removes** `Inter` and the
  `Nunito 300` and `Space Grotesk 400` weights that no component
  references.
- Lucide tree-shaking was confirmed to still be effective (no
  per-icon imports changed).

### 15. Canvas Rendering Quality (HiDPI)
**Problem**: Hardcoded 800×300 / 800×200 canvas resolution; the
spectrogram looked blurry on retina displays.

**Solution**:
- New helper `_setupHiDPICanvas(canvas, cssWidth, cssHeight)`:
  - `dpr = Math.min(2, window.devicePixelRatio || 1)` (capped to avoid
    blowing memory on 3× screens).
  - `canvas.width = Math.round(cssWidth * dpr)`,
    `canvas.height = Math.round(cssHeight * dpr)`.
  - `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)` so the rest of the draw
    code can keep using CSS-space coordinates.
- `drawSpectrumCanvas` and `drawSpectrogramCanvas` use the helper
  with fixed `CSS_WIDTH`/`CSS_HEIGHT` constants (800×300 and 800×200
  respectively). `getBoundingClientRect` is **not** used: the canvas
  is sized via CSS by its parent container, and the backing store is
  derived from the same CSS dimensions times DPR, which keeps the
  bitmap crisp on retina and behaves identically on non-retina.

---

## Priority Order (Impact / Effort Ratio)

The order in which the items were tackled in commits `8fdcebf`
(backend) and `8dbf6cb` (frontend).

1. **Lazy image loading** — 1 attribute per image, high impact
2. **Remove universal CSS transition** — 1 selector removal, medium-high impact
3. **Database indexes** — small migration, high impact
4. **FFT asynchrony** — moderate refactor, high impact
5. **Spectrogram ImageData** — moderate refactor, high impact
6. **Virtual scrolling** — moderate refactor, high impact on scaling
7. **Selective GZip** — small refactor, medium impact
8. **Store caching** — small refactor, medium impact
9. **FFT memory** — small change, medium impact
10. **Engine timeout** — 1 arg addition, low-medium impact
11. **Search pagination** — small change, medium impact
12. **User lookup cache** — moderate refactor, medium impact
13. **Brotli + fonts** — small config change, medium impact
14. **analyze_all_songs_fft async** — moderate refactor, medium impact
15. **Canvas retina** — moderate refactor, medium impact

## Verification

- All 133 existing backend tests must continue to pass after each step.
  This is enforced by the pre-push hook (`pytest`).
- Frontend: `npm run build` must succeed; visual smoke test of FFT
  visualization in `FFTView.vue`.
- Optional: add performance tests (e.g., `pytest-benchmark` for the
  FFT path) — not shipped yet.
