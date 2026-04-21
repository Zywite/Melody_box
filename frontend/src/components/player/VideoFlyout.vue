<template>
  <div class="video-flyout" @click.self="onBackdropClick">
    <div class="video-container">
      <div class="video-header">
        <div class="video-info">
          <p class="video-title">{{ playerStore.currentSong?.title }}</p>
          <p class="video-artist">{{ playerStore.currentSong?.artist }}</p>
        </div>
        <div class="header-buttons">
          <button @click="switchToAudio" class="header-btn" title="Reproducir solo audio">
            <Headphones :size="20" />
          </button>
          <button @click="toggleFullscreen" class="header-btn" title="Pantalla completa">
            <Maximize2 v-if="!isFullscreen" :size="20" />
            <Minimize2 v-else :size="20" />
          </button>
          <button @click="close" class="close-btn">
            <X :size="24" />
          </button>
        </div>
      </div>

      <div class="video-player-wrapper" :class="{ fullscreen: isFullscreen }">
        <video
          ref="videoRef"
          class="video-player"
          :src="videoSrc"
          @timeupdate="onTimeUpdate"
          @loadedmetadata="onLoadedMetadata"
          @durationchange="onDurationChange"
          @canplay="onCanPlay"
          @ended="onEnded"
          @play="onPlay"
          @pause="onPause"
          @click.stop
        ></video>
      </div>

      <div class="video-controls">
        <div class="progress-container" @click="handleSeek">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
        </div>

        <div class="controls-row">
          <div class="time-display">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</div>

          <div class="control-buttons">
            <button @click="playPrev" class="control-btn" title="Anterior">
              <SkipBack :size="20" />
            </button>
            <button @click="togglePlay" class="control-btn play-btn" :title="isPlaying ? 'Pausar' : 'Reproducir'">
              <Pause v-if="isPlaying" :size="24" fill="currentColor" />
              <Play v-else :size="24" fill="currentColor" />
            </button>
            <button @click="playNext" class="control-btn" title="Siguiente">
              <SkipForward :size="20" />
            </button>
          </div>

          <div class="volume-control">
            <button @click="toggleMute" class="control-btn">
              <VolumeX v-if="isMuted" :size="18" />
              <Volume2 v-else :size="18" />
            </button>
            <input
              type="range"
              min="0"
              max="100"
              :value="volume * 100"
              @input="handleVolume"
              class="volume-slider"
            />
          </div>
        </div>
      </div>

      <div class="video-footer">
        <button class="footer-btn">
          <Heart :size="18" />
          <span>Favorito</span>
        </button>
        <button class="footer-btn">
          <ListPlus :size="18" />
          <span>Agregar a playlist</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { X, Headphones, Maximize2, Minimize2, SkipBack, Play, Pause, SkipForward, VolumeX, Volume2, Heart, ListPlus } from 'lucide-vue-next'

const playerStore = usePlayerStore()
const videoRef = ref(null)
const isFullscreen = ref(false)

const videoSrc = computed(() => {
  if (!playerStore.currentSong) return ''
  return `/songs/${playerStore.currentSong.id}/stream`
})

const isPlaying = computed(() => playerStore.isPlaying)
const currentTime = computed(() => playerStore.currentTime)
const duration = computed(() => playerStore.duration)
const volume = computed(() => playerStore.volume)
const isMuted = computed(() => playerStore.isMuted)

const progress = computed(() => {
  if (!duration.value || duration.value <= 0 || !isFinite(duration.value) || isNaN(duration.value)) {
    return 0
  }
  return (currentTime.value / duration.value) * 100
})

function close() {
  if (videoRef.value) {
    videoRef.value.pause()
  }
  playerStore.closeVideoFlyout()
}

function onBackdropClick() {
  close()
}

function switchToAudio() {
  if (playerStore.currentSong) {
    playerStore.switchToAudio()
  }
  close()
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

function togglePlay() {
  if (videoRef.value) {
    if (isPlaying.value) {
      videoRef.value.pause()
    } else {
      videoRef.value.play()
    }
    playerStore.isPlaying = !isPlaying.value
  }
}

function playNext() {
  playerStore.playNext()
}

function playPrev() {
  playerStore.playPrev()
}

function handleSeek(event) {
  if (videoRef.value && duration.value) {
    const rect = event.currentTarget.getBoundingClientRect()
    const percent = ((event.clientX - rect.left) / rect.width) * 100
    videoRef.value.currentTime = (percent / 100) * duration.value
  }
}

function handleVolume(event) {
  const val = parseInt(event.target.value) / 100
  playerStore.setVolume(val)
}

function toggleMute() {
  playerStore.toggleMute()
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds) || !isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function onTimeUpdate() {
  if (videoRef.value) {
    playerStore.currentTime = videoRef.value.currentTime
  }
}

function onLoadedMetadata() {
  if (videoRef.value) {
    const dur = videoRef.value.duration
    if (dur && isFinite(dur) && !isNaN(dur)) {
      playerStore.duration = dur
    }
    playerStore.isPlaying = true
    videoRef.value.play().catch(e => console.error('Play error:', e))
  }
}

function onDurationChange() {
  if (videoRef.value) {
    const dur = videoRef.value.duration
    if (dur && isFinite(dur) && !isNaN(dur) && playerStore.duration !== dur) {
      playerStore.duration = dur
    }
  }
}

function onCanPlay() {
  if (videoRef.value) {
    const dur = videoRef.value.duration
    if (dur && isFinite(dur) && !isNaN(dur)) {
      playerStore.duration = dur
    }
  }
}

function onPlay() {
  playerStore.isPlaying = true
}

function onPause() {
  playerStore.isPlaying = false
}

function onEnded() {
  playerStore.playNext()
}

let durationCheckInterval = null

onMounted(() => {
  if (videoRef.value) {
    playerStore.setVideoElement(videoRef.value)
    videoRef.value.volume = playerStore.volume
    
    // Verificar duración periódicamente
    durationCheckInterval = setInterval(() => {
      if (videoRef.value && videoRef.value.readyState >= 2) {
        const dur = videoRef.value.duration
        if (dur && isFinite(dur) && !isNaN(dur) && playerStore.duration !== dur) {
          playerStore.duration = dur
          // Una vez que tenemos la duración, podemos dejar de verificar
          // clearInterval(durationCheckInterval)
        }
      }
    }, 500)
  }
})

onUnmounted(() => {
  if (durationCheckInterval) {
    clearInterval(durationCheckInterval)
  }
  playerStore.currentTime = 0
  playerStore.duration = 0
})
</script>

<style scoped>
.video-flyout {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.video-container {
  width: 100%;
  max-width: 1100px;
  background: var(--bg-secondary);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 80px rgba(225, 29, 72, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.1);
  animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.video-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(180deg, rgba(225, 29, 72, 0.15) 0%, transparent 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.video-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.video-title {
  font-size: 1.25rem;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

.video-artist {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: 4px;
  font-family: 'DM Sans', sans-serif;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.header-btn,
.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 10px;
  border-radius: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-btn:hover,
.close-btn:hover {
  background: var(--accent-primary);
  color: white;
  transform: scale(1.05);
}

.video-player-wrapper {
  background: #0a0a0a;
  position: relative;
}

.video-player-wrapper.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  max-width: none;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.video-player {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: block;
  background: #0a0a0a;
}

.fullscreen .video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
  aspect-ratio: auto;
}

.video-controls {
  padding: 16px 24px 20px;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.6) 0%, transparent 100%);
}

.progress-container {
  margin-bottom: 16px;
}

.progress-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
  cursor: pointer;
  overflow: hidden;
  transition: height 0.2s ease;
}

.progress-bar:hover {
  height: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #e11d48 0%, #7c3aed 100%);
  border-radius: 3px;
  transition: width 0.1s linear;
}

.controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.time-display {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
  min-width: 90px;
  font-family: 'DM Sans', sans-serif;
}

.control-buttons {
  display: flex;
  align-items: center;
  gap: 20px;
}

.control-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 10px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  color: var(--text-primary);
  transform: scale(1.1);
}

.play-btn {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #e11d48 0%, #7c3aed 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(225, 29, 72, 0.4);
}

.play-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 12px 32px rgba(225, 29, 72, 0.5);
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 140px;
}

.volume-slider {
  width: 100px;
  height: 6px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: linear-gradient(135deg, #e11d48 0%, #7c3aed 100%);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(225, 29, 72, 0.4);
}

.video-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  border-radius: 24px;
  transition: all 0.3s ease;
  font-family: 'DM Sans', sans-serif;
}

.footer-btn:hover {
  background: rgba(225, 29, 72, 0.2);
  color: var(--accent-primary);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .video-flyout {
    padding: 0;
  }

  .video-container {
    border-radius: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .volume-control {
    display: none;
  }

  .video-footer {
    display: none;
  }
}
</style>