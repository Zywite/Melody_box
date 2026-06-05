<template>
  <div class="library-view">
    <header class="page-header">
      <h1 class="header-title">Tu biblioteca</h1>
      <p class="header-subtitle">Gestiona tu colección de música</p>
    </header>

    <div class="library-tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'songs' }]"
        @click="activeTab = 'songs'"
      >
        Canciones
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'playlists' }]"
        @click="activeTab = 'playlists'"
      >
        Playlists
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'favorites' }]"
        @click="activeTab = 'favorites'"
      >
        Favoritas
      </button>
    </div>

    <div v-if="activeTab === 'songs'">
      <div class="filter-row">
        <button 
          :class="['filter-btn', { active: songFilter === 'all' }]"
          @click="songFilter = 'all'"
        >
          Todo
        </button>
        <button 
          :class="['filter-btn', { active: songFilter === 'audio' }]"
          @click="songFilter = 'audio'"
        >
          <Music :size="16" />
          Audio
        </button>
        <button 
          :class="['filter-btn', { active: songFilter === 'video' }]"
          @click="songFilter = 'video'"
        >
          <Video :size="16" />
          Video
        </button>
      </div>
      
      <div v-if="filteredSongs.length" class="song-list mt-4">
        <SongCard
          v-for="song in filteredSongs"
          :key="song.id"
          v-memo="[song.id, isSongFavorite(song.id)]"
          :song="song"
          :show-artist="true"
          :is-favorite="isSongFavorite(song.id)"
          @play="playSong"
          @add-to-playlist="showAddToPlaylist"
          @toggle-favorite="toggleFavorite"
        />
      </div>
      <div v-if="hasMoreSongs && !isLoading" class="load-more-container">
        <button @click="loadMore" class="load-more-btn">
          <Plus :size="18" />
          Cargar más
        </button>
      </div>
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
      </div>
      <div v-else class="empty-state">
        <Music :size="48" class="opacity-30" />
        <h3 class="text-xl font-semibold mt-4">Sin canciones</h3>
        <p class="text-[var(--text-secondary)]">Sube tu primera canción</p>
        <router-link to="/upload" class="btn-primary mt-4">Subir música</router-link>
      </div>
    </div>

    <div v-else-if="activeTab === 'playlists'">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold">Tus playlists</h2>
        <button @click="showCreatePlaylist = true" class="btn-new-playlist">
          <Plus :size="16" />
          <span>Crear</span>
        </button>
      </div>
      
      <div v-if="playlistsStore.playlists.length" class="playlist-list">
        <div
          v-for="playlist in playlistsStore.playlists"
          :key="playlist.id"
          class="playlist-item"
          @click="goToPlaylist(playlist.id)"
        >
          <div class="playlist-cover">
            <ListMusic :size="24" />
          </div>
          <div class="playlist-info">
            <p class="playlist-name">{{ playlist.name }}</p>
            <p class="playlist-meta">{{ playlist.songs?.length || 0 }} canciones</p>
          </div>
          <button class="playlist-menu-btn" @click.stop>
            <MoreHorizontal :size="18" />
          </button>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <div class="empty-icon">
          <ListMusic :size="48" />
        </div>
        <h3 class="text-xl font-semibold">Sin playlists</h3>
        <p class="text-[var(--text-secondary)]">Crea tu primera playlist</p>
        <button @click="showCreatePlaylist = true" class="btn-primary mt-4">Crear playlist</button>
      </div>
    </div>

    <div v-else-if="activeTab === 'favorites'">
      <div v-if="favorites.length" class="song-list mt-4">
        <SongCard
          v-for="song in favorites"
          :key="song.id"
          v-memo="[song.id]"
          :song="song"
          :show-artist="true"
          :is-favorite="true"
          @play="playSong"
          @toggle-favorite="toggleFavorite"
        />
      </div>
      <div v-else class="empty-state">
        <Heart :size="48" class="opacity-30" />
        <h3 class="text-xl font-semibold mt-4">Sin favoritos</h3>
        <p class="text-[var(--text-secondary)]">Marca canciones como favoritas</p>
      </div>
    </div>

    <CreatePlaylistModal v-if="showCreatePlaylist" @close="showCreatePlaylist = false" @created="onPlaylistCreated" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSongsStore } from '@/stores/songs'
import { usePlaylistsStore } from '@/stores/playlists'
import { useFavoritesStore } from '@/stores/favorites'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import { useFavorite } from '@/composables/useFavorite'
import SongCard from '@/components/common/SongCard.vue'
import PlaylistCard from '@/components/common/PlaylistCard.vue'
import CreatePlaylistModal from '@/components/common/CreatePlaylistModal.vue'
import { Music, ListMusic, Heart, Plus, MoreHorizontal, Video } from 'lucide-vue-next'

const router = useRouter()
const songsStore = useSongsStore()
const playlistsStore = usePlaylistsStore()
const favoritesStore = useFavoritesStore()
const playerStore = usePlayerStore()
const toast = useToast()
const { isSongFavorite, toggleFavorite: toggleFav } = useFavorite()

const activeTab = ref('songs')
const showCreatePlaylist = ref(false)
const songFilter = ref('all')
const isLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)

const filteredSongs = computed(() => {
  if (songFilter.value === 'all') {
    return songsStore.songs
  }
  return songsStore.songs.filter(song => song.media_type === songFilter.value)
})

const hasMoreSongs = computed(() => {
  return filteredSongs.value.length >= currentPage.value * pageSize.value
})

async function loadMore() {
  isLoading.value = true
  currentPage.value++
  try {
    await songsStore.fetchSongs(currentPage.value, pageSize.value, true)
  } catch (e) {
    toast.error('Error', 'No se pudieron cargar más canciones')
    currentPage.value--
  } finally {
    isLoading.value = false
  }
}

const favorites = computed(() => {
  return favoritesStore.favorites
    .filter(f => f.song)
    .map(f => ({
      ...f.song,
      is_favorite: true
    }))
})

onMounted(async () => {
  await Promise.all([
    songsStore.fetchSongs(),
    playlistsStore.fetchPlaylists(),
    favoritesStore.fetchFavorites()
  ])
})

function playSong(song) {
  playerStore.playSong(song, songsStore.songs)
}

function goToPlaylist(id) {
  router.push(`/playlists/${id}`)
}

async function toggleFavorite(song) {
  await toggleFav(song, {
    onSuccess: (msg) => toast.success(msg),
    onError: (msg) => toast.error('Error', msg),
  })
}

function showAddToPlaylist(song) {
  // TODO: Implement
}

async function onPlaylistCreated() {
  showCreatePlaylist.value = false
  await playlistsStore.fetchPlaylists()
}
</script>

<style scoped>
.library-view {
  animation: fadeIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.page-header {
  margin-bottom: 24px;
}

.header-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  margin-bottom: 4px;
}

.header-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.library-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: var(--bg-secondary);
  padding: 6px;
  border-radius: 20px;
  width: fit-content;
  border: 2px solid var(--border);
}

.tab-btn {
  padding: 10px 24px;
  border-radius: 16px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.tab-btn.active {
  background: var(--accent-gradient);
  color: white;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.filter-row {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.filter-btn {
  padding: 8px 20px;
  border-radius: 14px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-secondary);
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-btn:hover {
  border-color: var(--accent-light);
  color: var(--text-primary);
  transform: scale(1.03);
}

.filter-btn.active {
  background: var(--accent-gradient);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px var(--accent-glow);
}

.song-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: 16px;
  cursor: pointer;
  transition: all var(--transition);
}

.playlist-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.playlist-cover {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.playlist-info {
  flex: 1;
  min-width: 0;
}

.playlist-name {
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.playlist-meta {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.playlist-menu-btn {
  padding: 8px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.playlist-menu-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.load-more-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: 20px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-primary);
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition);
}

.load-more-btn:hover {
  border-color: var(--accent);
  transform: scale(1.05);
  box-shadow: var(--shadow);
}

.btn-new-playlist {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 16px;
  background: var(--accent-gradient);
  border: none;
  color: white;
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 4px 15px var(--accent-glow);
}

.btn-new-playlist:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px var(--accent-glow);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-state h3 {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  color: var(--text-primary);
  margin-top: 16px;
}

.empty-state p {
  font-family: 'Nunito', sans-serif;
  margin-top: 8px;
}

.empty-icon {
  color: var(--accent-light);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--bg-tertiary);
  border-top: 3px solid var(--accent);
  border-radius: 50%;
  animation: spin-slow 1s linear infinite;
}
</style>