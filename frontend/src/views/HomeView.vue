<template>
  <div class="home-view">
    <header class="page-header">
      <div class="welcome-section">
        <h1 class="header-title">Bienvenido de nuevo</h1>
        <p class="header-subtitle">{{ authStore.username }}</p>
      </div>
    </header>

    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <Music :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ libraryStore.songs.length }}</p>
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
            <p class="stat-value">{{ libraryStore.playlists.length }}</p>
            <p class="stat-label">Playlists</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon favorite">
            <Heart :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ libraryStore.favorites.length }}</p>
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
          :song="song"
          :is-favorite="isSongFavorite(song.id)"
          @play="playSong"
          @add-to-playlist="showAddToPlaylist"
          @toggle-favorite="toggleFavorite"
        />
      </div>
    </section>

    <section v-if="libraryStore.playlists.length" class="mt-8">
      <h2 class="section-title">Tus playlists</h2>
      <div class="playlist-grid">
        <PlaylistCard
          v-for="playlist in libraryStore.playlists"
          :key="playlist.id"
          :playlist="playlist"
          @click="goToPlaylist(playlist.id)"
        />
      </div>
    </section>

    <div v-if="!recentSongs.length && !libraryStore.playlists.length" class="empty-state">
      <Music2 :size="64" class="opacity-30" />
      <h3 class="text-xl font-semibold mt-4">Comienza a explorar</h3>
      <p class="text-[var(--text-secondary)]">Sube canciones o busca en la biblioteca</p>
      <div class="flex gap-4 mt-6">
        <router-link to="/upload" class="btn-primary">Subir música</router-link>
        <router-link to="/search" class="btn-secondary">Buscar</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLibraryStore } from '@/stores/library'
import { usePlayerStore } from '@/stores/player'
import SongCard from '@/components/common/SongCard.vue'
import PlaylistCard from '@/components/common/PlaylistCard.vue'
import { Music2, Music, Video, ListMusic, Heart } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()

const recentSongs = ref([])

const videoCount = computed(() => {
  return libraryStore.songs.filter(s => s.media_type === 'video').length
})

onMounted(async () => {
  await Promise.all([
    libraryStore.fetchSongs(),
    libraryStore.fetchPlaylists(),
    libraryStore.fetchFavorites()
  ])
  recentSongs.value = libraryStore.filteredSongs.slice(0, 8)
})

function playSong(song) {
  playerStore.playSong(song, libraryStore.songs)
}

function goToPlaylist(id) {
  router.push(`/playlists/${id}`)
}

function showAddToPlaylist(song) {
  // TODO: Implement playlist modal
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