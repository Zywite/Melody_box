<template>
  <div class="player-bar">
    <div class="player-bar-content">
      <!-- Info de canción -->
      <div class="player-info">
        <template v-if="playerStore.currentSong">
          <div class="track-artwork">
            <img 
              v-if="playerStore.currentSong.cover_url" 
              :src="playerStore.currentSong.cover_url" 
              :alt="playerStore.currentSong.title"
            />
            <div v-else class="artwork-placeholder">
              <Music2 :size="20" />
            </div>
            <div class="artwork-glow"></div>
          </div>
          <div class="track-meta">
            <p class="track-title">{{ playerStore.currentSong.title }}</p>
            <p class="track-artist">{{ playerStore.currentSong.artist }}</p>
          </div>
          <button @click="toggleFavorite" class="track-favorite" :class="{ active: isFavorite }">
            <Heart :size="18" :fill="isFavorite ? 'currentColor' : 'none'" />
          </button>
        </template>
        <template v-else>
          <div class="no-track">
            <p class="text-sm">Sin reproducir</p>
          </div>
        </template>
      </div>

      <!-- Controles centrales -->
      <div class="player-controls">
        <div class="control-buttons">
          <button 
            @click="playerStore.toggleShuffle" 
            class="control-btn small" 
            :class="{ active: playerStore.shuffle }"
            title="Aleatorio"
          >
            <Shuffle :size="16" stroke-width="2.5" />
          </button>
          <button @click="playerStore.playPrev" class="control-btn" title="Anterior">
            <SkipBack :size="18" stroke-width="2.5" />
          </button>
          <button 
            @click="playerStore.togglePlay" 
            class="play-btn" 
            :title="playerStore.isPlaying ? 'Pausar' : 'Reproducir'"
          >
            <Pause v-if="playerStore.isPlaying" :size="20" fill="currentColor" />
            <Play v-else :size="20" fill="currentColor" class="play-icon" />
          </button>
          <button @click="playerStore.playNext" class="control-btn" title="Siguiente">
            <SkipForward :size="18" stroke-width="2.5" />
          </button>
          <button 
            @click="playerStore.toggleRepeat" 
            class="control-btn small" 
            :class="{ active: playerStore.repeat !== 'none' }"
            :title="repeatTitle"
          >
            <Repeat v-if="playerStore.repeat === 'none' || playerStore.repeat === 'all'" :size="16" stroke-width="2.5" />
            <Repeat1 v-else :size="16" stroke-width="2.5" />
          </button>
        </div>

        <div class="progress-wrapper">
          <span class="time-label">{{ formatTime(playerStore.currentTime) }}</span>
          <div class="progress-bar" @click="handleSeek">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: playerStore.progress + '%' }"></div>
              <div class="progress-thumb" :style="{ left: playerStore.progress + '%' }"></div>
            </div>
          </div>
          <span class="time-label">{{ formatTime(playerStore.duration) }}</span>
        </div>
      </div>

      <!-- Controles extra -->
      <div class="player-extra">
        <button class="extra-btn" title="Cola">
          <ListMusic :size="18" />
        </button>
        <div class="volume-wrapper">
          <button @click="playerStore.toggleMute" class="extra-btn">
            <VolumeX v-if="playerStore.isMuted" :size="18" />
            <Volume2 v-else-if="playerStore.volume > 0.5" :size="18" />
            <Volume1 v-else-if="playerStore.volume > 0" :size="18" />
            <VolumeX v-else :size="18" />
          </button>
          <div class="volume-bar">
            <input
              type="range"
              min="0"
              max="100"
              :value="playerStore.volume * 100"
              @input="handleVolume"
              class="volume-slider"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import { SkipBack, Play, Pause, SkipForward, Heart, ListMusic, VolumeX, Volume2, Volume1, Music2, Shuffle, Repeat, Repeat1 } from 'lucide-vue-next'

const playerStore = usePlayerStore()
const libraryStore = useLibraryStore()
const toast = useToast()

const isFavorite = computed(() => {
  if (!playerStore.currentSong) return false
  return libraryStore.favorites.some(f => f.song_id === playerStore.currentSong.id)
})

const repeatTitle = computed(() => {
  const modes = {
    'none': 'Repetir: Desactivado',
    'all': 'Repetir: Todo',
    'one': 'Repetir: Una'
  }
  return modes[playerStore.repeat] || 'Repetir'
})

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleSeek(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const percent = ((event.clientX - rect.left) / rect.width) * 100
  playerStore.seek(Math.max(0, Math.min(100, percent)))
}

function handleVolume(event) {
  const value = parseInt(event.target.value) / 100
  playerStore.setVolume(value)
}

async function toggleFavorite() {
  if (!playerStore.currentSong) return
  try {
    if (isFavorite.value) {
      await api.removeFavorite(playerStore.currentSong.id)
      toast.success('Eliminado de favoritos')
    } else {
      await api.addFavorite(playerStore.currentSong.id)
      toast.success('Agregado a favoritos')
    }
  } catch (e) {
    toast.error('Error', e.message)
  }
}

function addToPlaylist() {
  // TODO: Implement playlist modal
}
</script>

<style scoped>
.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--player-height);
  background: linear-gradient(180deg, rgba(20, 20, 20, 0.95) 0%, rgba(10, 10, 10, 0.98) 100%);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
  z-index: 100;
}

.player-bar-content {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  align-items: center;
  height: 100%;
  padding: 0 24px;
  max-width: 1800px;
  margin: 0 auto;
}

/* Player Info */
.player-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.track-artwork {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 8px;
  overflow: visible;
  flex-shrink: 0;
}

.track-artwork img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.artwork-placeholder {
  width: 100%;
  height: 100%;
  background: var(--bg-tertiary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.artwork-glow {
  position: absolute;
  inset: -4px;
  border-radius: 12px;
  background: var(--accent-glow);
  filter: blur(12px);
  opacity: 0;
  transition: opacity var(--transition);
}

.track-meta {
  min-width: 0;
  flex: 1;
}

.track-title {
  font-weight: 500;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
}

.track-artist {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-favorite {
  padding: 8px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.track-favorite:hover {
  color: var(--text-primary);
}

.track-favorite.active {
  color: var(--accent);
}

/* Player Controls */
.player-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  max-width: 600px;
  margin: 0 auto;
}

.control-buttons {
  display: flex;
  align-items: center;
  gap: 16px;
}

.control-btn {
  padding: 8px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  color: var(--text-primary);
  transform: scale(1.1);
}

.control-btn.small {
  padding: 6px;
}

.control-btn.small.active {
  color: var(--accent-primary);
}

.play-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--text-primary);
  color: var(--text-inverse);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.play-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2);
}

.play-icon {
  margin-left: 2px;
}

/* Progress */
.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.time-label {
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted);
  min-width: 40px;
  text-align: center;
}

.progress-bar {
  flex: 1;
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.progress-track {
  position: relative;
  width: 100%;
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: visible;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.1s linear;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: var(--text-primary);
  border-radius: 50%;
  opacity: 0;
  transition: opacity var(--transition-fast);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.progress-bar:hover .progress-thumb {
  opacity: 1;
}

.progress-bar:hover .progress-track {
  height: 6px;
}

/* Player Extra */
.player-extra {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.extra-btn {
  padding: 8px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.extra-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.volume-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.volume-bar {
  width: 80px;
}

.volume-slider {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-tertiary);
  border-radius: 2px;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: var(--text-primary);
  border-radius: 50%;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.volume-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.no-track {
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .player-bar-content {
    grid-template-columns: 1fr auto;
    padding: 0 16px;
  }

  .player-extra,
  .progress-wrapper {
    display: none;
  }

  .track-artwork {
    width: 48px;
    height: 48px;
  }
}
</style>