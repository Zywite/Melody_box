---
plan name: background-fft-storage
plan description: Background FFT with storage
plan status: done
---

## Idea
Implement server-side FFT analysis with database storage, auto-analyze on upload and for existing songs, display stored results in FFT tab

## Implementation
- Add fft_data JSON column to Song model or create FFTAnalysis model with song_id FK
- Install numpy and scipy for server-side FFT computation
- Create fft_service.py with function to compute FFT from audio file path
- Add FFT analysis endpoint GET /songs/{id}/fft to get or compute FFT data
- Modify upload endpoint to trigger FFT analysis after song creation (store results)
- Create endpoint POST /songs/analyze-all to analyze all songs missing FFT data
- Update SongResponse schema to include has_fft flag
- Modify FFTView.vue to load FFT data from backend API instead of computing client-side
- Add loading state in FFTView when analysis is pending
- Add 'Analyze all missing' button in FFTView for existing songs
- Test complete flow: upload → auto-analyze → view results
- Test analyzing existing songs without FFT data

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->