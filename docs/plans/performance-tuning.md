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
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->