<template>
  <div class="search-view">
    <header class="page-header">
      <h1 class="text-3xl font-bold">Buscar</h1>
    </header>

    <div class="search-container mt-6">
      <SearchInput v-model="searchQuery" @search="handleSearch" placeholder="Buscar canciones, artistas..." />
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
import { useLibraryStore } from '@/stores/library'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import SongCard from '@/components/common/SongCard.vue'
import SearchInput from '@/components/common/SearchInput.vue'
import { Search } from 'lucide-vue-next'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const toast = useToast()

const searchQuery = ref('')
const results = ref([])
const isLoading = ref(false)

onMounted(async () => {
  await Promise.all([
    libraryStore.fetchSongs(),
    libraryStore.fetchFavorites()
  ])
  results.value = libraryStore.songs.slice(0, 20)
})

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    results.value = libraryStore.songs.slice(0, 20)
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

function isSongFavorite(songId) {
  return libraryStore.favorites.some(f => f.song_id === songId)
}

async function toggleFavorite(song) {
  try {
    const isFav = libraryStore.favorites.some(f => f.song_id === song.id)
    if (isFav) {
      await libraryStore.removeFavorite(song.id)
    } else {
      await libraryStore.addFavorite(song.id)
    }
  } catch (e) {
    console.error('Error toggling favorite:', e)
  }
}
</script>