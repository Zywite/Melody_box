import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from './auth'

export const usePlaylistsStore = defineStore('playlists', () => {
  const playlists = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const authStore = useAuthStore()

  const playlistCount = computed(() => playlists.value.length)

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

  async function addSongToPlaylist(playlistId, songId) {
    try {
      await api.addSongToPlaylist(playlistId, songId)
      await fetchPlaylists()
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return {
    playlists,
    isLoading,
    error,
    playlistCount,
    fetchPlaylists,
    createPlaylist,
    getPlaylist,
    addSongToPlaylist,
  }
})
