<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title">Agregar a playlist</h2>
        <button @click="emit('close')" class="close-btn">
          <X :size="20" />
        </button>
      </div>

      <div class="modal-body">
        <div v-if="playlistsStore.playlists.length" class="playlist-list">
          <button
            v-for="playlist in playlistsStore.playlists"
            :key="playlist.id"
            class="playlist-item"
            :disabled="isAdding"
            @click="addTo(playlist.id)"
          >
            <div class="playlist-cover-mini">
              <ListMusic :size="18" />
            </div>
            <span class="playlist-name">{{ playlist.name }}</span>
            <span class="playlist-count">{{ playlist.songs?.length || 0 }} canciones</span>
          </button>
        </div>

        <div v-else class="empty-playlists">
          <p class="text-[var(--text-secondary)] mb-4">No tienes playlists aún</p>
          <button @click="showCreate = true" class="btn-primary">
            <Plus :size="16" />
            Crear playlist
          </button>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="emit('close')" class="btn-secondary">Cancelar</button>
        <button @click="showCreate = true" class="btn-primary" v-if="playlistsStore.playlists.length">
          <Plus :size="16" />
          Nueva playlist
        </button>
      </div>
    </div>

    <CreatePlaylistModal
      v-if="showCreate"
      @close="showCreate = false"
      @created="onPlaylistCreated"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { usePlaylistsStore } from '@/stores/playlists'
import { useToast } from '@/composables/useToast'
import CreatePlaylistModal from './CreatePlaylistModal.vue'
import { X, ListMusic, Plus } from 'lucide-vue-next'

const props = defineProps({
  song: { type: Object, required: true }
})

const emit = defineEmits(['close', 'added'])

const playlistsStore = usePlaylistsStore()
const toast = useToast()
const isAdding = ref(false)
const showCreate = ref(false)

async function addTo(playlistId) {
  isAdding.value = true
  try {
    await playlistsStore.addSongToPlaylist(playlistId, props.song.id)
    toast.success('Agregada a playlist')
    emit('added', playlistId)
  } catch (e) {
    toast.error('Error', e.message)
  } finally {
    isAdding.value = false
  }
}

function onPlaylistCreated() {
  showCreate.value = false
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset:0;
  background: rgba(255, 245, 247, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 28px;
  width: 100%;
  max-width: 460px;
  overflow: hidden;
  border:2px solid var(--border);
  box-shadow:0 20px 60px rgba(255, 158, 187, 0.2);
  animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-bottom:2px solid var(--border);
}

.modal-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.close-btn {
  background: var(--bg-tertiary);
  border:2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 12px;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 158, 187, 0.2);
  color: var(--accent);
  border-color: var(--accent-light);
  transform: scale(1.05);
}

.modal-body {
  padding: 12px 8px;
  max-height: 360px;
  overflow-y: auto;
}

.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 14px;
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
  width: 100%;
  text-align: left;
}

.playlist-item:hover {
  background: var(--bg-tertiary);
}

.playlist-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.playlist-cover-mini {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.playlist-name {
  flex: 1;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.playlist-count {
  font-size: 0.8rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.empty-playlists {
  text-align: center;
  padding: 40px 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top:2px solid var(--border);
}
</style>
