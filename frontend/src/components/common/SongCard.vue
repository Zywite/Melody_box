<template>
  <div
    :class="['song-card', { active: isPlaying, playing: isCurrentlyPlaying }]"
    @dblclick="emit('play', song)"
  >
    <div v-if="showPosition" class="song-position">
      <span v-if="!isCurrentlyPlaying">{{ position }}</span>
      <div v-else class="playing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>

    <div class="song-artwork">
      <img v-if="song.cover_url" :src="song.cover_url" :alt="song.title" />
      <div v-else class="artwork-placeholder">
        <Video v-if="song.media_type === 'video'" :size="24" />
        <Music2 v-else :size="24" />
      </div>
      <div class="artwork-overlay" @click.stop="emit('play', song)">
        <Play :size="24" fill="currentColor" />
      </div>
    </div>

    <div class="song-content">
      <div class="song-main">
        <p class="song-title">{{ song.title }}</p>
        <p v-if="showArtist" class="song-artist">{{ song.artist }}</p>
      </div>
      <p v-if="song.album" class="song-album">{{ song.album }}</p>
    </div>

    <div class="song-meta">
      <span v-if="song.duration" class="song-duration">{{ formatDuration(song.duration) }}</span>
    </div>

    <div class="song-actions">
      <button
        @click.stop="toggleFavorite"
        class="action-btn"
        :class="{ active: isFavorite }"
        title="Favorito"
      >
        <Heart :size="18" :fill="isFavorite ? 'currentColor' : 'none'" />
      </button>
      <button @click.stop="showMenu = !showMenu" class="action-btn" :class="{ active: showMenu }">
        <MoreHorizontal :size="18" />
      </button>

      <Transition name="dropdown">
        <div v-if="showMenu" class="dropdown-menu">
          <button @click="addToPlaylist" class="menu-item">
            <ListPlus :size="16" />
            Agregar a playlist
          </button>
          <button @click="deleteSong" class="menu-item danger">
            <Trash2 :size="16" />
            Eliminar
          </button>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import { Music2, Video, Play, Heart, ListPlus, MoreHorizontal, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  song: { type: Object, required: true },
  showPosition: { type: Boolean, default: false },
  position: { type: Number, default: 0 },
  showArtist: { type: Boolean, default: false },
  isFavorite: { type: Boolean, default: false }
})

const emit = defineEmits(['play', 'add-to-playlist', 'toggle-favorite'])

const playerStore = usePlayerStore()
const libraryStore = useLibraryStore()
const toast = useToast()

const showMenu = ref(false)

const isCurrentlyPlaying = computed(() => playerStore.currentSong?.id === props.song.id)
const isPlaying = computed(() => isCurrentlyPlaying.value && playerStore.isPlaying)

function formatDuration(seconds) {
  if (!seconds) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function toggleFavorite() {
  emit('toggle-favorite', props.song)
  showMenu.value = false
}

function addToPlaylist() {
  emit('add-to-playlist', props.song)
  showMenu.value = false
}

async function deleteSong() {
  if (!confirm('¿Eliminar canción?')) return
  try {
    await api.deleteSong(props.song.id)
    toast.success('Canción eliminada')
    await libraryStore.fetchSongs()
  } catch (e) {
    toast.error('Error', e.message)
  }
  showMenu.value = false
}
</script>

<style scoped>
.song-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.song-card:hover {
  background: var(--bg-tertiary);
}

.song-card.active {
  background: rgba(225, 29, 72, 0.1);
}

.song-card.playing .song-title {
  color: var(--accent);
}

.song-position {
  width: 32px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.playing-indicator {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 2px;
  height: 16px;
}

.playing-indicator span {
  width: 3px;
  background: var(--accent);
  animation: bounce 0.8s ease-in-out infinite;
}

.playing-indicator span:nth-child(1) { height: 60%; animation-delay: 0s; }
.playing-indicator span:nth-child(2) { height: 100%; animation-delay: 0.2s; }
.playing-indicator span:nth-child(3) { height: 40%; animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}

.song-artwork {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.song-artwork img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.artwork-placeholder {
  width: 100%;
  height: 100%;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.artwork-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.song-card:hover .artwork-overlay {
  opacity: 1;
}

.song-card.playing .artwork-overlay {
  opacity: 1;
  background: rgba(225, 29, 72, 0.6);
}

.song-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.song-main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.song-title {
  font-weight: 500;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
}

.song-artist {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-album {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.song-duration {
  font-size: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted);
  min-width: 45px;
  text-align: right;
}

.song-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
}

.action-btn {
  padding: 8px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.action-btn.active {
  color: var(--accent);
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 6px;
  min-width: 180px;
  z-index: 50;
  box-shadow: var(--shadow-lg);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
  border-radius: 8px;
  transition: background var(--transition-fast);
}

.menu-item:hover {
  background: var(--bg-tertiary);
}

.menu-item.danger {
  color: var(--danger);
}

.menu-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>