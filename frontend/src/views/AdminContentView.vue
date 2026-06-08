<template>
  <div class="admin-view">
    <div class="admin-header">
      <div class="header-icon">
        <Shield :size="28" />
      </div>
      <h1 class="page-title">Panel de Administración</h1>
      <p class="page-subtitle">Gestión de usuarios y contenido</p>
    </div>

    <div class="admin-tabs">
      <router-link to="/admin" class="tab">
        <Users :size="18" />
        Usuarios
      </router-link>
      <router-link to="/admin/content" class="tab active">
        <Music :size="18" />
        Contenido
      </router-link>
    </div>

    <div class="content-tabs">
      <button
        class="content-tab"
        :class="{ active: activeTab === 'songs' }"
        @click="activeTab = 'songs'"
      >
        <Music :size="18" />
        Canciones
      </button>
      <button
        class="content-tab"
        :class="{ active: activeTab === 'playlists' }"
        @click="activeTab = 'playlists'"
      >
        <ListMusic :size="18" />
        Playlists
      </button>
    </div>

    <!-- Songs Tab -->
    <div v-if="activeTab === 'songs'" class="table-container">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Artista</th>
            <th>Duración</th>
            <th>Tipo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="song in songs" :key="song.id">
            <td class="title-cell">{{ song.title }}</td>
            <td class="artist-cell">{{ song.artist }}</td>
            <td>{{ formatDuration(song.duration) }}</td>
            <td>
              <span class="type-badge" :class="song.media_type">
                {{ song.media_type }}
              </span>
            </td>
            <td>
              <button class="action-btn delete" @click="confirmDeleteSong(song)" title="Eliminar">
                <Trash2 :size="16" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!songs.length && !loading" class="empty-state">
        <Music :size="48" />
        <p>No hay canciones</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>
    </div>

    <!-- Playlists Tab -->
    <div v-if="activeTab === 'playlists'" class="table-container">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Usuario</th>
            <th>Canciones</th>
            <th>Creada</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="playlist in playlists" :key="playlist.id">
            <td class="title-cell">{{ playlist.name }}</td>
            <td class="artist-cell">{{ playlist.username }}</td>
            <td>{{ playlist.song_count }}</td>
            <td class="date-cell">{{ formatDate(playlist.created_at) }}</td>
            <td>
              <button class="action-btn delete" @click="confirmDeletePlaylist(playlist)" title="Eliminar">
                <Trash2 :size="16" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!playlists.length && !loading" class="empty-state">
        <ListMusic :size="48" />
        <p>No hay playlists</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="deletingItem" class="modal-overlay" @click.self="deletingItem = null">
      <div class="modal-content">
        <h3>Eliminar {{ deletingItem.type }}</h3>
        <p>¿Estás seguro de eliminar <strong>{{ deletingItem.name }}</strong>?</p>
        <p class="text-sm text-[var(--text-secondary)]">Esta acción no se puede deshacer.</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="deletingItem = null">Cancelar</button>
          <button class="btn-danger" @click="executeDelete">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/composables/useApi'
import { Shield, Users, Music, ListMusic, Trash2 } from 'lucide-vue-next'

const activeTab = ref('songs')
const songs = ref([])
const playlists = ref([])
const loading = ref(true)
const deletingItem = ref(null)

onMounted(async () => {
  await loadSongs()
})

watch(activeTab, () => {
  if (activeTab.value === 'songs' && !songs.value.length) loadSongs()
  if (activeTab.value === 'playlists' && !playlists.value.length) loadPlaylists()
})

async function loadSongs() {
  loading.value = true
  try {
    songs.value = await api.adminGetSongs()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadPlaylists() {
  loading.value = true
  try {
    playlists.value = await api.adminGetPlaylists()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' })
}

function confirmDeleteSong(song) {
  deletingItem.value = { type: 'Canción', id: song.id, name: song.title }
}

function confirmDeletePlaylist(playlist) {
  deletingItem.value = { type: 'Playlist', id: playlist.id, name: playlist.name }
}

async function executeDelete() {
  const item = deletingItem.value
  try {
    if (item.type === 'Canción') {
      await api.adminDeleteSong(item.id)
      songs.value = songs.value.filter(s => s.id !== item.id)
    } else {
      await api.adminDeletePlaylist(item.id)
      playlists.value = playlists.value.filter(p => p.id !== item.id)
    }
    deletingItem.value = null
  } catch (e) {
    alert('Error: ' + e.message)
  }
}
</script>

<style scoped>
.admin-view {
  padding: 32px;
  animation: fadeIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.admin-header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 16px;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.page-title {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  color: var(--text-secondary);
}

.admin-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  justify-content: center;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.tab:hover {
  border-color: var(--accent-light);
  color: var(--text-primary);
  transform: translateY(-2px);
}

.tab.active {
  background: var(--accent-gradient);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.content-tabs {
  display: flex;
  gap: 8px;
  margin: 24px 0;
  justify-content: center;
}

.content-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.content-tab:hover {
  border-color: var(--accent-light);
  color: var(--text-primary);
  transform: translateY(-2px);
}

.content-tab.active {
  background: linear-gradient(135deg, rgba(177, 156, 217, 0.3) 0%, rgba(135, 206, 235, 0.3) 100%);
  color: var(--secondary);
  border-color: var(--secondary);
  box-shadow: 0 2px 10px var(--secondary-glow);
}

.table-container {
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th {
  padding: 16px 20px;
  text-align: left;
  font-family: 'Nunito', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  border-bottom: 2px solid var(--border);
}

.admin-table td {
  padding: 14px 20px;
  font-family: 'Nunito', sans-serif;
  font-size: 0.9rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
}

.admin-table tr:last-child td {
  border-bottom: none;
}

.admin-table tr:hover td {
  background: rgba(255, 158, 187, 0.08);
}

.title-cell {
  font-weight: 600;
}

.artist-cell {
  color: var(--text-secondary);
}

.date-cell {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.type-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.type-badge.audio {
  background: rgba(152, 251, 152, 0.15);
  color: var(--success);
  border: 1px solid rgba(152, 251, 152, 0.3);
}

.type-badge.video {
  background: rgba(135, 206, 235, 0.15);
  color: var(--blue-accent);
  border: 1px solid rgba(135, 206, 235, 0.3);
}

.action-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 2px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  transform: scale(1.1);
}

.action-btn.delete:hover {
  background: rgba(255, 107, 138, 0.15);
  color: var(--danger);
  border-color: rgba(255, 107, 138, 0.3);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-state p {
  margin-top: 12px;
  font-family: 'Nunito', sans-serif;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  padding: 32px;
  width: 90%;
  max-width: 460px;
  box-shadow: var(--shadow-lg);
}

.modal-content h3 {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  font-size: 1.3rem;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-secondary {
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border);
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  border-color: var(--accent-light);
  transform: scale(1.05);
}

.btn-danger {
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--danger) 0%, #ff4d6d 100%);
  color: white;
  border: none;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-danger:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px var(--danger-glow);
}

@media (max-width: 768px) {
  .admin-view {
    padding: 20px 16px;
  }
  .page-title {
    font-size: 1.5rem;
  }
  .admin-table th,
  .admin-table td {
    padding: 10px 12px;
    font-size: 0.8rem;
  }
  .date-cell {
    display: none;
  }
}
</style>