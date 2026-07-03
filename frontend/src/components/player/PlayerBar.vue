<template>
  <div class="player-bar">
    <div class="player-bar-content">
      <PlayerTrackInfo
        :song="playerStore.currentSong"
        :is-favorite="isFavorite"
        @toggle-favorite="toggleFavorite"
      />

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

      <div class="player-extra">
        <button
          v-if="playerStore.currentSong"
          @click="addToPlaylist"
          class="extra-btn"
          title="Agregar a playlist"
        >
          <ListPlus :size="18" />
        </button>
        <button
          @click="playerStore.toggleQueue"
          class="extra-btn"
          :class="{ active: playerStore.showQueue }"
          title="Cola"
        >
          <ListMusic :size="18" />
        </button>
        <VolumeControl
          :volume="playerStore.volume"
          :is-muted="playerStore.isMuted"
          @toggle-mute="playerStore.toggleMute"
          @update:volume="handleVolume"
        />
      </div>
    </div>
  </div>

    <AddToPlaylistModal
      v-if="addToPlaylistSong"
      :song="addToPlaylistSong"
      @close="addToPlaylistSong = null"
    />
</template>

<script setup>
import { computed, ref } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import { formatTime } from '@/utils/format'
import api from '@/composables/useApi'
import AddToPlaylistModal from '@/components/common/AddToPlaylistModal.vue'
import PlayerTrackInfo from '@/components/player/PlayerTrackInfo.vue'
import VolumeControl from '@/components/player/VolumeControl.vue'
import { SkipBack, Play, Pause, SkipForward, ListMusic, ListPlus, Shuffle, Repeat, Repeat1 } from 'lucide-vue-next'

const playerStore = usePlayerStore()
const libraryStore = useLibraryStore()
const toast = useToast()
const addToPlaylistSong = ref(null)

const favoriteMap = computed(() => {
  const map = new Map()
  for (const f of libraryStore.favorites) {
    map.set(f.song_id, true)
  }
  return map
})

const isFavorite = computed(() => {
  if (!playerStore.currentSong) return false
  return favoriteMap.value.has(playerStore.currentSong.id)
})

const repeatTitle = computed(() => {
  const modes = {
    'none': 'Repetir: Desactivado',
    'all': 'Repetir: Todo',
    'one': 'Repetir: Una'
  }
  return modes[playerStore.repeat] || 'Repetir'
})

function handleSeek(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const percent = ((event.clientX - rect.left) / rect.width) * 100
  playerStore.seek(Math.max(0, Math.min(100, percent)))
}

function handleVolume(value) {
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
  addToPlaylistSong.value = playerStore.currentSong
}
</script>

<style scoped>
.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--player-height);
  background: var(--bg-glass-strong);
  backdrop-filter: blur(20px);
  border-top: 2px solid var(--border);
  z-index: 100;
  box-shadow: 0 -4px 20px var(--accent-glow);
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
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
  box-shadow: 0 4px 20px var(--accent-glow);
}

.play-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 30px var(--accent-glow);
}

.play-btn:active {
  transform: scale(0.95);
}

.play-icon {
  margin-left: 2px;
}

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
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: visible;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  background-size: 200% 200%;
  border-radius: var(--radius-full);
  transition: width 0.1s linear;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 16px;
  height: 16px;
  background: var(--accent);
  border-radius: 50%;
  opacity: 0;
  transition: opacity var(--transition-fast);
  box-shadow: 0 2px 8px var(--accent-glow);
  border: 2px solid #fff;
}

.progress-bar:hover .progress-thumb {
  opacity: 1;
}

.progress-bar:hover .progress-track {
  height: 6px;
}

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

.extra-btn.active {
  color: var(--accent-primary);
}

@media (max-width: 768px) {
  .player-bar-content {
    grid-template-columns: 1fr auto;
    padding: 0 16px;
  }

  .player-extra,
  .progress-wrapper {
    display: none;
  }
}
</style>