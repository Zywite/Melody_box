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

      <VideoPlayer
        :video-src="videoSrc"
        :is-fullscreen="isFullscreen"
        :volume="volume"
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @durationchange="onDurationChange"
        @canplay="onCanPlay"
        @ended="onEnded"
        @play="onPlay"
        @pause="onPause"
        @mounted="onVideoMounted"
      />

      <VideoControls
        :progress="progress"
        :current-time="currentTime"
        :duration="duration"
        :is-playing="isPlaying"
        :volume="volume"
        :is-muted="isMuted"
        @seek="handleSeek"
        @toggle-play="togglePlay"
        @play-next="playNext"
        @play-prev="playPrev"
        @volume="handleVolume"
        @toggle-mute="toggleMute"
      />

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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { X, Headphones, Maximize2, Minimize2, Heart, ListPlus } from 'lucide-vue-next'
import VideoPlayer from './VideoPlayer.vue'
import VideoControls from './VideoControls.vue'

const playerStore = usePlayerStore()
const isFullscreen = ref(false)
let videoRef = null
let durationCheckInterval = null

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
  if (videoRef) {
    videoRef.pause()
  }
  playerStore.closeVideoFlyout()
}

function onBackdropClick() {
  close()
}

function onVideoMounted(ref) {
  videoRef = ref
  playerStore.setVideoElement(ref)
  durationCheckInterval = setInterval(() => {
    if (ref && ref.readyState >= 2) {
      const dur = ref.duration
      if (dur && isFinite(dur) && !isNaN(dur) && playerStore.duration !== dur) {
        playerStore.setDuration(dur)
      }
    }
  }, 500)
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
  if (videoRef) {
    if (isPlaying.value) {
      videoRef.pause()
    } else {
      videoRef.play()
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

function handleSeek(time) {
  if (videoRef && duration.value) {
    videoRef.currentTime = time
  }
}

function handleVolume(val) {
  playerStore.setVolume(val)
}

function toggleMute() {
  playerStore.toggleMute()
}

function onTimeUpdate(ref) {
  if (ref) {
    playerStore.setCurrentTime(ref.currentTime)
  }
}

function onLoadedMetadata(ref) {
  if (ref) {
    const dur = ref.duration
    if (dur && isFinite(dur) && !isNaN(dur)) {
      playerStore.setDuration(dur)
    }
    playerStore.isPlaying = true
    ref.play().catch(e => console.error('Play error:', e))
  }
}

function onDurationChange(ref) {
  if (ref) {
    const dur = ref.duration
    if (dur && isFinite(dur) && !isNaN(dur) && playerStore.duration !== dur) {
      playerStore.setDuration(dur)
    }
  }
}

function onCanPlay(ref) {
  if (ref) {
    const dur = ref.duration
    if (dur && isFinite(dur) && !isNaN(dur)) {
      playerStore.setDuration(dur)
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

onUnmounted(() => {
  if (durationCheckInterval) {
    clearInterval(durationCheckInterval)
  }
  playerStore.setCurrentTime(0)
  playerStore.setDuration(0)
})
</script>

<style scoped>
.video-flyout {
  position: fixed;
  top:0;
  left:0;
  right:0;
  bottom:0;
  background: rgba(255, 245, 247, 0.9);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index:1000;
  padding:20px;
  animation: fadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.video-container {
  width:100%;
  max-width:1200px;
  background: var(--bg-secondary);
  border-radius: 28px;
  overflow: hidden;
  box-shadow:0 25px 80px rgba(255, 158, 187, 0.2), 0 0 0 2px var(--border);
  animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity:0; }
  to { transform: translateY(0); opacity:1; }
}

.video-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding:20px 24px;
  background: linear-gradient(180deg, rgba(255, 183, 197, 0.2) 0%, transparent 100%);
  border-bottom:2px solid var(--border);
}

.video-info {
  flex:1;
  min-width:0;
  overflow: hidden;
}

.video-title {
  font-size:1.35rem;
  font-weight:700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.video-artist {
  font-size:0.9rem;
  color: var(--accent);
  margin-top:4px;
  font-family: 'Nunito', sans-serif;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap:8px;
  flex-shrink:0;
}

.header-btn,
.close-btn {
  background: var(--bg-tertiary);
  border:2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding:10px;
  border-radius:14px;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-btn:hover,
.close-btn:hover {
  background: var(--accent-gradient);
  color: white;
  border-color: transparent;
  transform: scale(1.05);
}

.video-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap:24px;
  padding:16px;
  border-top:2px solid var(--border);
}

.footer-btn {
  display: flex;
  align-items: center;
  gap:10px;
  padding:12px 24px;
  background: var(--bg-tertiary);
  border:2px solid var(--border);
  color: var(--text-secondary);
  font-size:0.875rem;
  cursor: pointer;
  border-radius:20px;
  transition: all var(--transition);
  font-family: 'Nunito', sans-serif;
  font-weight:600;
}

.footer-btn:hover {
  background: rgba(255, 158, 187, 0.2);
  color: var(--accent);
  border-color: var(--accent-light);
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

  .video-footer {
    display: none;
  }
}
</style>