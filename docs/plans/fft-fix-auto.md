---
plan name: fft-fix-auto
plan description: Fix FFT theme and auto-analyze
plan status: done
---

## Idea
Fix FFTView dark mode compatibility by replacing hardcoded colors with CSS variables, and auto-trigger FFT analysis after file upload with automatic redirect to results

## Implementation
- Replace all hardcoded colors in FFTView.vue with CSS variables (--bg-primary, --text-primary, etc.)
- Update FFTView canvas drawing to use theme-aware colors instead of #1DB954, #000, #fff
- Fix FFTVisualizer.vue canvas gradient to use accent colors from CSS variables
- Modify upload flow in UploadView.vue to store uploaded song ID after successful upload
- Auto-redirect to FFTView with the uploaded song selected and analysis triggered automatically
- Add loading state during automatic FFT analysis after upload
- Test dark/light mode switching in FFTView
- Test automatic FFT analysis trigger after file upload

## Required Specs
<!-- SPECS_START -->
<!-- SPECS_END -->