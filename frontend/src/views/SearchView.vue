<template>
  <div class="search-view">
    <header class="page-header">
      <h1 class="header-title">Buscar</h1>
      <p class="header-subtitle">Encuentra tu música favorita</p>
    </header>

    <div class="search-container">
      <SearchInput v-model="searchQuery" @search="handleSearch" placeholder="Buscar canciones, artistas o álbumes..." />
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-else-if="results.length" class="results-section mt-6">
      <h2 class="section-title">Resultados{{ searchQuery ? ` para "${searchQuery}"` : '' }}</h2>
      <div class="song-list">
        <SongCard
          v-for="song in results"
          :key="song.id"
          :song="song"
          :show-artist="true"
          :is-favorite="isSongFavorite(song.id)"
          @play="playSong"
          @add-to-playlist="showAddToPlaylist"
          @toggle-favorite="toggleFavorite"
        />
      </div>
    </div>

    <div v-else class="empty-state">
      <Search :size="48" class="opacity-30" />
      <h3 class="text-xl font-semibold mt-4">Busca tu música</h3>
      <p class="text-[var(--text-secondary)]">Encuentra canciones por título, artista o álbum</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSongsStore } from '@/stores/songs'
import { useFavoritesStore } from '@/stores/favorites'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import { useFavorite } from '@/composables/useFavorite'
import api from '@/composables/useApi'
import SongCard from '@/components/common/SongCard.vue'
import SearchInput from '@/components/common/SearchInput.vue'
import { Search } from 'lucide-vue-next'

const songsStore = useSongsStore()
const favoritesStore = useFavoritesStore()
const playerStore = usePlayerStore()
const toast = useToast()
const { isSongFavorite, toggleFavorite } = useFavorite()

const searchQuery = ref('')
const results = ref([])
const isLoading = ref(false)

onMounted(async () => {
  await Promise.all([
    songsStore.fetchSongs(),
    favoritesStore.fetchFavorites()
  ])
  results.value = songsStore.songs.slice(0, 20)
})

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    results.value = songsStore.songs.slice(0, 20)
    return
  }

  isLoading.value = true
  try {
    results.value = await api.searchSongs(searchQuery.value)
  } catch (e) {
    toast.error('Error en búsqueda', e.message)
  } finally {
    isLoading.value = false
  }
}

function playSong(song) {
  playerStore.playSong(song, results.value)
}

function showAddToPlaylist(song) {
  // TODO: Implement
}

</script>

<style scoped>
.search-view {
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

.search-container {
  max-width: 600px;
  margin: 0 auto 32px;
}

.results-section {
  animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  margin-bottom: 20px;
}

.song-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 60px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--bg-tertiary);
  border-top: 3px solid var(--accent);
  border-radius: 50%;
  animation: spin-slow 1s linear infinite;
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
  color: var(--text-secondary);
}

.empty-state :deep(svg) {
  color: var(--accent-light);
}
</style>