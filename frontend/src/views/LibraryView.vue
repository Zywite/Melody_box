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

    <SongTab
      v-if="activeTab === 'songs'"
      :has-more-songs="hasMoreSongs"
      :is-loading="isLoading"
      @play="playSong"
      @add-to-playlist="showAddToPlaylist"
      @toggle-favorite="toggleFavorite"
      @load-more="loadMore"
    />
    <PlaylistTab
      v-else-if="activeTab === 'playlists'"
      :playlists="playlistsStore.playlists"
      @create="showCreatePlaylist = true"
      @go-to-playlist="goToPlaylist"
    />
    <FavoritesTab
      v-else-if="activeTab === 'favorites'"
      :favorites="favorites"
      @play="playSong"
      @toggle-favorite="toggleFavorite"
    />

    <CreatePlaylistModal v-if="showCreatePlaylist" @close="showCreatePlaylist = false" @created="onPlaylistCreated" />
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
import { useSongsStore } from '@/stores/songs'
import { usePlaylistsStore } from '@/stores/playlists'
import { useFavoritesStore } from '@/stores/favorites'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import { useFavorite } from '@/composables/useFavorite'
import SongTab from '@/components/library/SongTab.vue'
import PlaylistTab from '@/components/library/PlaylistTab.vue'
import FavoritesTab from '@/components/library/FavoritesTab.vue'
import CreatePlaylistModal from '@/components/common/CreatePlaylistModal.vue'
import AddToPlaylistModal from '@/components/common/AddToPlaylistModal.vue'

const router = useRouter()
const songsStore = useSongsStore()
const playlistsStore = usePlaylistsStore()
const favoritesStore = useFavoritesStore()
const playerStore = usePlayerStore()
const toast = useToast()
const { toggleFavorite: toggleFav } = useFavorite()

const activeTab = ref('songs')
const showCreatePlaylist = ref(false)
const addToPlaylistSong = ref(null)
const isLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)

const hasMoreSongs = computed(() => {
  return songsStore.songs.length >= currentPage.value * pageSize.value
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
  try {
    await Promise.all([
      songsStore.fetchSongs(),
      playlistsStore.fetchPlaylists(),
      favoritesStore.fetchFavorites()
    ])
  } catch (e) {
    toast.error('Error', 'No se pudieron cargar los datos')
  }
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
  addToPlaylistSong.value = song
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
</style>