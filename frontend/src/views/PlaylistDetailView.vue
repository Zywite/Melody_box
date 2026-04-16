<template>
  <div class="playlist-detail-view">
    <header class="page-header">
      <div v-if="playlist" class="flex items-center gap-6">
        <div class="playlist-cover">
          <ListMusic :size="48" />
        </div>
        <div>
          <p class="text-sm uppercase tracking-wide text-[var(--text-secondary)]">Playlist</p>
          <h1 class="text-4xl font-bold">{{ playlist.name }}</h1>
          <p v-if="playlist.description" class="text-[var(--text-secondary)] mt-1">{{ playlist.description }}</p>
          <p class="text-sm text-[var(--text-secondary)] mt-2">{{ playlist.songs?.length || 0 }} canciones</p>
        </div>
      </div>
      <div v-else class="loading-state">
        <div class="spinner"></div>
      </div>
    </header>

    <div v-if="playlist" class="mt-6">
      <div class="flex gap-4 mb-6">
        <button @click="playAll" class="btn-primary" :disabled="!playlist.songs?.length">
          <Play :size="20" fill="currentColor" />
          Reproducir todo
        </button>
        <button @click="shuffleAll" class="btn-secondary" :disabled="!playlist.songs?.length">
          <Shuffle :size="18" />
          Aleatorio
        </button>
        <button @click="deletePlaylist" class="btn-danger">
          <Trash2 :size="18" />
        </button>
      </div>

      <div v-if="playlist.songs?.length" class="song-list">
        <SongCard
          v-for="(item, index) in playlist.songs"
          :key="item.song_id"
          :song="getSongData(item.song_id)"
          :show-position="true"
          :position="index + 1"
          :is-favorite="isSongFavorite(item.song_id)"
          @play="playFrom(index)"
          @remove-from-playlist="removeSong(item.song_id)"
          @toggle-favorite="toggleFavorite"
        />
      </div>
      <div v-else class="empty-state">
        <Music :size="48" class="opacity-30" />
        <h3 class="text-xl font-semibold mt-4">Playlist vacía</h3>
        <p class="text-[var(--text-secondary)]">Agrega canciones desde la biblioteca</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLibraryStore } from '@/stores/library'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import SongCard from '@/components/common/SongCard.vue'
import { ListMusic, Play, Shuffle, Trash2, Music } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const toast = useToast()

const playlist = ref(null)
const allSongs = ref([])

onMounted(async () => {
  const playlistId = route.params.id
  try {
    await libraryStore.fetchFavorites()
    playlist.value = await api.getPlaylist(playlistId)
    allSongs.value = await api.getSongs()
  } catch (e) {
    toast.error('Error', e.message)
    router.push('/library')
  }
})

function getSongData(songId) {
  return allSongs.value.find(s => s.id === songId) || { id: songId, title: 'Unknown', artist: 'Unknown' }
}

function playAll() {
  if (!playlist.value.songs?.length) return
  const songs = playlist.value.songs.map(item => getSongData(item.song_id)).filter(s => s.id)
  if (songs.length) playerStore.playSong(songs[0], songs)
}

function shuffleAll() {
  if (!playlist.value.songs?.length) return
  const songs = playlist.value.songs.map(item => getSongData(item.song_id)).filter(s => s.id)
  if (songs.length) {
    for (let i = songs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [songs[i], songs[j]] = [songs[j], songs[i]]
    }
    playerStore.playSong(songs[0], songs)
  }
}

function playFrom(index) {
  if (!playlist.value.songs?.length) return
  const songs = playlist.value.songs.map(item => getSongData(item.song_id)).filter(s => s.id)
  playerStore.playSong(songs[index], songs)
}

async function removeSong(songId) {
  try {
    await api.removeSongFromPlaylist(playlist.value.id, songId)
    playlist.value.songs = playlist.value.songs.filter(s => s.song_id !== songId)
    toast.success('Canción eliminada')
  } catch (e) {
    toast.error('Error', e.message)
  }
}

async function deletePlaylist() {
  if (!confirm('¿Eliminar playlist?')) return
  try {
    await api.deletePlaylist(playlist.value.id)
    toast.success('Playlist eliminada')
    router.push('/library')
  } catch (e) {
    toast.error('Error', e.message)
  }
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