# Spec: fft-progress-feedback

Scope: feature

# FFT Progress Feedback - Feature Specification

## Overview
Add comprehensive progress feedback and notifications for FFT analysis to improve user experience during song upload and analysis.

## Requirements

### 1. Backend Logging
**File:** `src/app/services/song_service.py`

- Add success logging when FFT analysis completes:
  ```python
  print(f"FFT analysis completed for song: {title} (ID: {db_song.id})")
  ```
- Log analysis duration:
  ```python
  import time
  start_time = time.time()
  # ... FFT computation ...
  duration = time.time() - start_time
  print(f"FFT analysis took {duration:.2f}s for {title}")
  ```
- Keep existing error logging

### 2. Toast Notifications (Frontend)
**File:** `frontend/src/views/UploadView.vue`

- Import toast composable (already available via `useToast`)
- Show success toast after upload + FFT analysis:
  ```javascript
  toast.success(`"${song.title}" subido y analizado exitosamente`)
  ```
- Show error toast if FFT fails (upload succeeds but analysis fails):
  ```javascript
  toast.warning(`"${song.title}" subido, pero falló el análisis FFT`)
  ```
- Show info toast when redirecting to FFT tab:
  ```javascript
  toast.info('Redirigiendo a Análisis FFT...')
  ```

### 3. Upload Progress with FFT Analysis
**File:** `frontend/src/views/UploadView.vue`

- Modify upload flow to show FFT analysis progress:
  - Upload phase: "Subiendo... X%"
  - FFT phase: "Analizando FFT..."
- Use loading overlay or better progress indication:
  ```vue
  <div v-if="isUploading" class="upload-overlay">
    <div class="upload-spinner"></div>
    <p>{{ uploadStatus }}</p>
  </div>
  ```
- Update `uploadStatus` ref:
  - Set to "Subiendo archivo..." during upload
  - Set to "Analizando FFT..." during FFT computation
  - Clear when complete

### 4. Automatic has_fft Verification
**File:** `frontend/src/views/FFTView.vue`

- After upload redirect (songId in route query), verify has_fft status
- Poll backend if needed (max 5 attempts, 1 second interval):
  ```javascript
  async function waitForFFT(songId, attempts = 0) {
    if (attempts > 5) return false;
    const song = songs.value.find(s => s.id === songId);
    if (song?.has_fft) {
      await loadFFTData(songId);
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
    await libraryStore.fetchSongs(); // Refresh song list
    return waitForFFT(songId, attempts + 1);
  }
  ```

### 5. Display "Analyzing FFT..." Message
**File:** `frontend/src/views/FFTView.vue`

- Add new state for pending analysis:
  ```javascript
  const isAnalyzingFFT = ref(false)
  ```
- Show message when song is selected but has_fft is false:
  ```vue
  <div v-if="selectedSongId && !result && !song.has_fft" class="analyzing-state">
    <div class="analyzing-spinner"></div>
    <p>Analizando FFT para "{{ selectedSongTitle }}"...</p>
    <p class="analyzing-hint">Esto puede tardar unos segundos</p>
  </div>
  ```
- Style with kawaii theme (pink spinner, soft colors)

### 6. Enhanced Song List Status
**File:** `frontend/src/views/FFTView.vue`

- Show "Pendiente - Analizando..." for songs currently being analyzed
- Add animated spinner next to song title during analysis
- Disable "Analizar" button during analysis

### 7. Backend Status Endpoint (Optional Enhancement)
**File:** `src/app/routes/songs.py`

- Add endpoint to check FFT status:
  ```python
  @router.get("/{song_id}/fft-status")
  def get_fft_status(song_id: str, db: Session = Depends(get_db)):
      song = SongService.get_song(db, song_id)
      if not song:
          raise HTTPException(status_code=404, detail="Song not found")
      return {
          "has_fft": bool(song.fft_data),
          "song_id": song_id,
          "title": song.title
      }
  ```

## UI/UX Specifications

### Kawaii Theme Compliance
- All spinners: Use `--accent` color (#ff9ebb)
- Loading text: Use `--text-secondary` color
- Success toasts: Use `--success` color (#98fb98)
- Warning toasts: Use `--warning` color (#ffd700)
- Error toasts: Use `--danger` color (#ff6b8a)

### Animation
- Spinners: Use CSS animation with `cubic-bezier(0.34, 1.56, 0.64, 1)` for bouncy effect
- Toast enter: Use `slide-up` animation
- Status changes: Smooth transition (already in main.css)

## Testing Checklist
- [ ] Upload song → See "Subiendo..." → See "Analizando FFT..." → See success toast
- [ ] Upload song → FFT fails → See warning toast
- [ ] Redirect to FFT tab → Auto-load results when ready
- [ ] Existing song without FFT → Shows "Analizando..." state
- [ ] Backend logs show analysis duration
- [ ] Dark mode: All feedback elements visible
- [ ] Light mode: All feedback elements visible

## Acceptance Criteria
1. User always knows when FFT analysis is in progress
2. User receives clear success/error feedback via toasts
3. Upload progress shows both upload and FFT phases
4. FFT tab shows appropriate messages for pending analysis
5. Backend provides useful logging for debugging
6. All feedback respects kawaii theme (dark/light modes)