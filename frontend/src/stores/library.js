import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from './auth'

export const useLibraryStore = defineStore('library', () => {
  const songs = ref([])
  const playlists = ref([])
  const favorites = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const filterType = ref('all') // all, audio, video

  const authStore = useAuthStore()

  const filteredSongs = computed(() => {
    if (filterType.value === 'all') return songs.value
    return songs.value.filter(s => s.media_type === filterType.value)
  })

  const audioCount = computed(() => songs.value.filter(s => s.media_type !== 'video').length)
  const videoCount = computed(() => songs.value.filter(s => s.media_type === 'video').length)
  const playlistCount = computed(() => playlists.value.length)

  async function fetchSongs() {
    if (!authStore.isAuthenticated) return
    isLoading.value = true
    error.value = null
    try {
      songs.value = await api.getSongs()
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPlaylists() {
    if (!authStore.isAuthenticated) return
    isLoading.value = true
    error.value = null
    try {
      playlists.value = await api.getPlaylists()
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function fetchFavorites() {
    if (!authStore.isAuthenticated) return
    try {
      favorites.value = await api.getFavorites()
    } catch (e) {
      error.value = e.message
    }
  }

  async function addFavorite(songId) {
    await api.addFavorite(songId)
    await fetchFavorites()
  }

  async function removeFavorite(songId) {
    await api.removeFavorite(songId)
    await fetchFavorites()
  }

  async function uploadSong(file, title, artist, album) {
    try {
      await api.uploadSong(file, title, artist, album)
      await fetchSongs()
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function deleteSong(id) {
    try {
      await api.deleteSong(id)
      songs.value = songs.value.filter(s => s.id !== id)
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function searchSongs(query) {
    if (query.length < 2) return []
    try {
      return await api.searchSongs(query)
    } catch (e) {
      error.value = e.message
      return []
    }
  }

  async function createPlaylist(name, description = '') {
    try {
      await api.createPlaylist(name, description)
      await fetchPlaylists()
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function getPlaylist(id) {
    try {
      return await api.getPlaylist(id)
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  function setFilter(type) {
    filterType.value = type
  }

  return {
    songs,
    playlists,
    favorites,
    isLoading,
    error,
    filterType,
    filteredSongs,
    audioCount,
    videoCount,
    playlistCount,
    fetchSongs,
    fetchPlaylists,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    uploadSong,
    deleteSong,
    searchSongs,
    createPlaylist,
    getPlaylist,
    setFilter
  }
})