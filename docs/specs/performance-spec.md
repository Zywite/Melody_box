# Spec: performance-spec

Scope: feature

# Performance Optimization Spec

## Backend

### 1. Thread Pool for CPU-Bound Work
**Problem**: `worker.py` (compute_fft, download_youtube) and `routes/songs.py` (get_song_fft fallback) call CPU-bound operations (librosa, yt-dlp) directly in async context, blocking the event loop.

**Solution**:
- Add `concurrent.futures.ThreadPoolExecutor(max_workers=4)` in `worker.py` module level
- Wrap `FFTService.compute_fft_from_file` calls in `loop.run_in_executor(executor, ...)`
- Wrap `yt_dlp.YoutubeDL(...).download(...)` in same pattern
- In `routes/songs.py:get_song_fft`, wrap FFT fallback in `asyncio.to_thread()`
- ProcessPoolExecutor for true CPU-bound work (FFT); ThreadPoolExecutor for I/O-bound (yt-dlp)

### 2. FFT Memory Optimization
**Problem**: `librosa.load(file_path, sr=None, mono=True)` loads entire audio file as float64 (~106MB for 10-min stereo).

**Solution**:
- Change `sr` parameter: `sr=22050` (downsample) — acceptable for visualization
- Limit to first N seconds for preview (`duration=120`)
- Use `librosa.stft(y, center=False)` to reduce boundary frames
- Skip loading if cached FFT exists (already in redis_helper)

### 3. Database Indexes
**Problem**: PostgreSQL doesn't auto-index foreign keys; full-table scans on FFT task lookups.

**Solution**:
```python
# models/task.py
__table_args__ = (
    Index("ix_task_song_id", "song_id"),
    Index("ix_task_type_status", "type", "status"),
)

# models/music.py (PlaylistSong)
__table_args__ = (
    Index("ix_playlist_song_playlist_id", "playlist_id"),
    Index("ix_playlist_song_song_id", "song_id"),
)

# models/music.py (Favorite)
__table_args__ = (
    Index("ix_favorite_user_song", "user_id", "song_id"),
)
```

### 4. Search Pagination
**Problem**: `search_songs` returns all matches with no LIMIT.

**Solution**: Add `skip` and `limit` parameters to `routes/songs.py:search_songs` and `services/song_service.py:search_songs`.

### 5. User Lookup Cache
**Problem**: `get_current_user` runs DB query on every authenticated request.

**Solution**:
- Short-term: Add `cachetools.TTLCache(maxsize=500, ttl=60)` in `routes/dependencies.py`
- Keyed by `user_id` from JWT subject claim
- Skip cache when `is_active` check is critical (only check on protected mutations)

### 6. Engine Connect Timeout
**Problem**: `core/database.py` engine created at import with no timeout, stalls startup.

**Solution**: Add `connect_args={"connect_timeout": 3}` to `create_engine()` call.

### 7. analyze_all_songs_fft Refactor
**Problem**: Sync endpoint that loops 1000 songs, blocks uvicorn thread for minutes.

**Solution**:
- Enqueue individual FFT jobs via arq instead of in-process loop
- Use `asyncio.to_thread` for any in-process fallback
- Commit progress to DB after each song
- Add a progress-tracking task row

### 8. Selective GZip Middleware
**Problem**: GZip re-compresses already-compressed audio streams.

**Solution**:
```python
class SelectiveGZipMiddleware(GZipMiddleware):
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            if path.startswith(("/songs/", "/music/", "/assets/")):
                await self.app(scope, receive, send)
                return
        await super().__call__(scope, receive, send)
```

---

## Frontend

### 9. Virtual Scrolling for Song Lists
**Problem**: `LibraryView.vue` and `FFTView.vue` render all `<SongCard>` in flat `v-for`; DOM explosion beyond 300 songs.

**Solution**:
- Use `vue-virtual-scroller` (RecycleScroller)
- Replace `v-for` over `songsStore.songs` with `<RecycleScroller :items="..." :item-size="80">`
- Configure :key-field="'id'" for stable recycling
- Keep the existing pagination API but increase page size (e.g., 200 per page)

### 10. Spectrogram Canvas ImageData
**Problem**: `fftCanvas.js:168-178` does ~256,000 `fillRect` calls; blocks main thread 100s of ms.

**Solution**:
- Build `Uint8ClampedArray(width * height * 4)` pixel buffer
- Loop once over frames/bins, set RGBA values
- Single `ctx.putImageData(imageData, 0, 0)` call
- ~250x faster than fillRect approach

### 11. Lazy Image Loading
**Problem**: All `<img>` tags load eagerly; 200+ concurrent image requests on Library mount.

**Solution**:
- Add `loading="lazy"` to `SongCard.vue:14`, `PlaylistCard.vue:4`, `YouTubeDownloader.vue:63`
- Add proper `alt` text
- Add `@error` handler that swaps to placeholder

### 12. Store Optimizations
**Problem**: AppSidebar duplicate API call; favorites full re-fetch on toggle.

**Solution**:
- `AppSidebar.vue`: Remove `api.getPlaylists()` from `onMounted`; use `playlistsStore.playlists` and call `playlistsStore.fetchPlaylists()` only if not loaded
- `favorites.js:24,34`: Optimistic update — push to local array on add, splice on remove, revert on error
- `playlists.js:30`: Push new playlist locally instead of full refetch
- `songs.js:22`: Add `lastFetched` timestamp, skip re-fetch if data is <30s old (configurable)

### 13. CSS Performance
**Problem**: Universal `* { transition: ... }` causes style recalc on every DOM change.

**Solution**:
- Remove universal transition from `main.css:6-11`
- Add explicit `.transition-colors` utility class for elements that need it
- Audit and remove duplicate CSS rules in scoped components (QueuePanel, CreatePlaylistModal, SearchInput, ToastContainer)

### 14. Vite Build Optimizations
**Problem**: No brotli compression; too many Google Fonts.

**Solution**:
- Add `vite-plugin-compression` with `algorithm: 'brotliCompress', ext: '.br'`
- Audit Google Fonts URL — keep only Inter (or whatever is actually used), remove unused families
- Verify lucide tree-shaking still effective (it is)

### 15. Canvas Rendering Quality
**Problem**: Hardcoded 800x300 resolution; blurry on retina displays.

**Solution**:
- Use `canvas.getBoundingClientRect()` for display size
- Set canvas internal width/height to `displaySize * devicePixelRatio`
- Scale context: `ctx.scale(dpr, dpr)` after size set
- Wrap draws in `requestAnimationFrame` for smooth rendering

---

## Priority Order (Impact / Effort Ratio)

1. **Lazy image loading** — 1 line per image, high impact
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

- All 133 existing backend tests must continue to pass after each step
- Frontend: `npm run build` must succeed; visual smoke test of FFT visualization
- Optional: add performance tests (e.g., `pytest-benchmark` for FFT path)