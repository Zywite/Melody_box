import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from './auth'

export const useSongsStore = defineStore('songs', () => {
  const songs = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const filterType = ref('all')

  const authStore = useAuthStore()

  const filteredSongs = computed(() => {
    if (filterType.value === 'all') return songs.value
    return songs.value.filter(s => s.media_type === filterType.value)
  })

  const audioCount = computed(() => songs.value.filter(s => s.media_type !== 'video').length)
  const videoCount = computed(() => songs.value.filter(s => s.media_type === 'video').length)

  async function fetchSongs(page = 1, limit = 50, append = false) {
    if (!authStore.isAuthenticated) return
    isLoading.value = true
    error.value = null
    try {
      const newSongs = await api.getSongs(page, limit)
      if (append) {
        const existingIds = new Set(songs.value.map(s => s.id))
        const uniqueNewSongs = newSongs.filter(s => !existingIds.has(s.id))
        songs.value = [...songs.value, ...uniqueNewSongs]
      } else {
        songs.value = newSongs
      }
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
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

  function setFilter(type) {
    filterType.value = type
  }

  return {
    songs,
    isLoading,
    error,
    filterType,
    filteredSongs,
    audioCount,
    videoCount,
    fetchSongs,
    deleteSong,
    searchSongs,
    setFilter,
  }
})
