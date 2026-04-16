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
          :song="song"
          :show-artist="true"
          :is-favorite="isSongFavorite(song.id)"
          @play="playSong"
          @add-to-playlist="showAddToPlaylist"
          @toggle-favorite="toggleFavorite"
        />
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
      
      <div v-if="libraryStore.playlists.length" class="playlist-list">
        <div
          v-for="playlist in libraryStore.playlists"
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
import { useLibraryStore } from '@/stores/library'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import SongCard from '@/components/common/SongCard.vue'
import PlaylistCard from '@/components/common/PlaylistCard.vue'
import CreatePlaylistModal from '@/components/common/CreatePlaylistModal.vue'
import { Music, ListMusic, Heart, Plus, MoreHorizontal, Video } from 'lucide-vue-next'

const router = useRouter()
const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const toast = useToast()

const activeTab = ref('songs')
const showCreatePlaylist = ref(false)
const songFilter = ref('all')

const filteredSongs = computed(() => {
  if (songFilter.value === 'all') {
    return libraryStore.songs
  }
  return libraryStore.songs.filter(song => song.media_type === songFilter.value)
})

const favorites = computed(() => {
  return libraryStore.favorites
    .filter(f => f.song)
    .map(f => ({
      ...f.song,
      is_favorite: true
    }))
})

function isSongFavorite(songId) {
  return libraryStore.favorites.some(f => f.song_id === songId)
}

onMounted(async () => {
  await Promise.all([
    libraryStore.fetchSongs(),
    libraryStore.fetchPlaylists(),
    libraryStore.fetchFavorites()
  ])
})

function playSong(song) {
  playerStore.playSong(song, libraryStore.songs)
}

function goToPlaylist(id) {
  router.push(`/playlists/${id}`)
}

async function toggleFavorite(song) {
  try {
    // El song puede venir de la lista de canciones o de favoritos
    // Verificamos si está en la lista de favoritos
    const isFav = libraryStore.favorites.some(f => f.song_id === song.id)
    if (isFav) {
      await libraryStore.removeFavorite(song.id)
      toast.success('Eliminado de favoritos')
    } else {
      await libraryStore.addFavorite(song.id)
      toast.success('Agregado a favoritos')
    }
  } catch (e) {
    toast.error('Error', e.message)
  }
}

function showAddToPlaylist(song) {
  // TODO: Implement
}

async function onPlaylistCreated() {
  showCreatePlaylist.value = false
  await libraryStore.fetchPlaylists()
}
</script>