---
plan name: fft-progress-feedback
plan description: FFT progress feedback
plan status: active
---

## Idea
Add proper progress feedback and notifications for FFT analysis: toast notifications, backend logging, upload progress indication, and automatic has_fft verification after upload

## Implementation
- Add success logging in backend song_service.py when FFT analysis completes
- Add toast notification in frontend when FFT analysis completes after upload
- Show upload progress spinner during FFT analysis (not just upload)
- Auto-refresh has_fft status in FFTView after upload completes
- Add backend endpoint to check FFT status for a song
- Display 'Analyzing FFT...' message in FFT tab when song is pending
- Test complete flow: upload → FFT analysis → notification → FFT tab update
- Ensure toast notifications show both success and error cases

## Required Specs
<!-- SPECS_START -->
- fft-progress-feedback
<!-- SPECS_END -->