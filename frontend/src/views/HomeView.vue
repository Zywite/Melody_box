<template>
  <div class="home-view">
    <header class="page-header">
      <div class="welcome-section">
        <h1 class="header-title">Bienvenido de nuevo</h1>
        <p class="header-subtitle">{{ authStore.username }}</p>
      </div>
    </header>

    <section v-if="!loadingError" class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <Music :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ songsStore.songs.length }}</p>
            <p class="stat-label">Canciones</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon video">
            <Video :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ videoCount }}</p>
            <p class="stat-label">Videos</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <ListMusic :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ playlistsStore.playlists.length }}</p>
            <p class="stat-label">Playlists</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon favorite">
            <Heart :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ favoritesStore.favorites.length }}</p>
            <p class="stat-label">Favoritas</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="recentSongs.length" class="mt-8">
      <h2 class="section-title">Reproducidas recientemente</h2>
      <div class="song-grid">
        <SongCard
          v-for="song in recentSongs"
          :key="song.id"
          v-memo="[song.id, isSongFavorite(song.id)]"
          :song="song"
          :is-favorite="isSongFavorite(song.id)"
          @play="playSong"
          @add-to-playlist="showAddToPlaylist"
          @toggle-favorite="toggleFavorite"
        />
      </div>
    </section>

    <section v-if="playlistsStore.playlists.length" class="mt-8">
      <h2 class="section-title">Tus playlists</h2>
      <div class="playlist-grid">
        <PlaylistCard
          v-for="playlist in playlistsStore.playlists"
          :key="playlist.id"
          :playlist="playlist"
          @click="goToPlaylist(playlist.id)"
        />
      </div>
    </section>

    <div v-if="!loadingError && !recentSongs.length && !playlistsStore.playlists.length" class="empty-state">
      <Music2 :size="64" class="opacity-30" />
      <h3 class="text-xl font-semibold mt-4">Comienza a explorar</h3>
      <p class="text-[var(--text-secondary)]">Sube canciones o busca en la biblioteca</p>
      <div class="flex gap-4 mt-6">
        <router-link to="/upload" class="btn-primary">Subir música</router-link>
        <router-link to="/search" class="btn-secondary">Buscar</router-link>
      </div>
    </div>
    <div v-if="loadingError" class="error-state">
      <AlertTriangle :size="48" />
      <h3>Error al cargar</h3>
      <p>No se pudieron cargar los datos. Reintenta más tarde.</p>
      <button class="btn-secondary mt-4" @click="loadData">Reintentar</button>
    </div>

    <AddToPlaylistModal
      v-if="addToPlaylistSong"
      :song="addToPlaylistSong"
      @close="addToPlaylistSong = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSongsStore } from '@/stores/songs'
import { usePlaylistsStore } from '@/stores/playlists'
import { useFavoritesStore } from '@/stores/favorites'
import { usePlayerStore } from '@/stores/player'
import { useFavorite } from '@/composables/useFavorite'
import SongCard from '@/components/common/SongCard.vue'
import PlaylistCard from '@/components/common/PlaylistCard.vue'
import AddToPlaylistModal from '@/components/common/AddToPlaylistModal.vue'
import { Music2, Music, Video, ListMusic, Heart, AlertTriangle } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const authStore = useAuthStore()
const songsStore = useSongsStore()
const playlistsStore = usePlaylistsStore()
const favoritesStore = useFavoritesStore()
const playerStore = usePlayerStore()
const toast = useToast()
const { isSongFavorite, toggleFavorite } = useFavorite()

const recentSongs = ref([])
const addToPlaylistSong = ref(null)
const loadingError = ref(false)

const videoCount = computed(() => {
  return songsStore.songs.filter(s => s.media_type === 'video').length
})

onMounted(loadData)

async function loadData() {
  loadingError.value = false
  try {
    await Promise.all([
      songsStore.fetchSongs(),
      playlistsStore.fetchPlaylists(),
      favoritesStore.fetchFavorites()
    ])
    recentSongs.value = songsStore.filteredSongs.slice(0, 8)
  } catch (e) {
    loadingError.value = true
    toast.error('Error', 'No se pudieron cargar los datos')
  }
}

function playSong(song) {
  playerStore.playSong(song, songsStore.songs)
}

function goToPlaylist(id) {
  router.push(`/playlists/${id}`)
}

function showAddToPlaylist(song) {
  addToPlaylistSong.value = song
}

</script>

<style scoped>
.home-view {
  animation: fadeIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.page-header {
  margin-bottom: 32px;
}

.header-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  margin-bottom: 4px;
}

.header-subtitle {
  font-size: 1.1rem;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: 24px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
}

.stat-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--shadow);
  border-color: var(--accent-light);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.stat-icon.video {
  background: linear-gradient(135deg, var(--blue-accent) 0%, var(--secondary) 100%);
}

.stat-icon.favorite {
  background: linear-gradient(135deg, #ff6b8a 0%, #ff9ebb 100%);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  margin-bottom: 20px;
}

.song-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.playlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-state h3 {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  color: var(--text-primary);
}

.empty-state p {
  font-family: 'Nunito', sans-serif;
  margin-top: 8px;
}

.empty-state :deep(svg) {
  color: var(--accent-light);
}

.error-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.error-state h3 {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  color: var(--text-primary);
  margin-top: 16px;
}

.error-state p {
  font-family: 'Nunito', sans-serif;
  margin-top: 8px;
}

.error-state :deep(svg) {
  color: var(--accent);
}
</style>