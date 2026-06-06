import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from './auth'

const SONGS_STALE_AFTER_MS = 30_000
const SONGS_CACHE_KEY = 'melodybox:cache:songs:v1'

export const useSongsStore = defineStore('songs', () => {
  const songs = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const filterType = ref('all')
  const lastFetchedAt = ref(0)
  const lastFetchParams = ref({ page: 1, limit: 50 })

  const authStore = useAuthStore()

  const filteredSongs = computed(() => {
    if (filterType.value === 'all') return songs.value
    return songs.value.filter(s => s.media_type === filterType.value)
  })

  const audioCount = computed(() => songs.value.filter(s => s.media_type !== 'video').length)
  const videoCount = computed(() => songs.value.filter(s => s.media_type === 'video').length)

  function _isStale(page, limit) {
    if (lastFetchedAt.value === 0) return true
    if (lastFetchParams.value.page !== page || lastFetchParams.value.limit !== limit) return true
    return Date.now() - lastFetchedAt.value > SONGS_STALE_AFTER_MS
  }

  function _persistCache() {
    try {
      sessionStorage.setItem(SONGS_CACHE_KEY, JSON.stringify({
        songs: songs.value,
        ts: lastFetchedAt.value,
        params: lastFetchParams.value,
      }))
    } catch {
      // sessionStorage may be unavailable; ignore.
    }
  }

  function _restoreCache() {
    try {
      const raw = sessionStorage.getItem(SONGS_CACHE_KEY)
      if (!raw) return false
      const parsed = JSON.parse(raw)
      if (!parsed?.songs || !parsed?.ts) return false
      songs.value = parsed.songs
      lastFetchedAt.value = parsed.ts
      lastFetchParams.value = parsed.params || { page: 1, limit: 50 }
      return true
    } catch {
      return false
    }
  }

  async function fetchSongs(page = 1, limit = 50, append = false, { force = false } = {}) {
    if (!authStore.isAuthenticated) return

    if (!append && !force && _isStale(page, limit)) {
      _restoreCache()
    }

    if (!append && !force) {
      const remaining = Date.now() - lastFetchedAt.value
      if (remaining < SONGS_STALE_AFTER_MS
          && lastFetchParams.value.page === page
          && lastFetchParams.value.limit === limit
          && songs.value.length > 0) {
        return
      }
    }

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
        lastFetchedAt.value = Date.now()
        lastFetchParams.value = { page, limit }
        _persistCache()
      }
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  function invalidate() {
    lastFetchedAt.value = 0
    try {
      sessionStorage.removeItem(SONGS_CACHE_KEY)
    } catch {
      // ignore
    }
  }

  function upsertSong(song) {
    const idx = songs.value.findIndex(s => s.id === song.id)
    if (idx >= 0) {
      songs.value[idx] = { ...songs.value[idx], ...song }
    } else {
      songs.value = [song, ...songs.value]
    }
    lastFetchedAt.value = Date.now()
    _persistCache()
  }

  function removeSongLocal(id) {
    songs.value = songs.value.filter(s => s.id !== id)
    _persistCache()
  }

  async function deleteSong(id) {
    try {
      await api.deleteSong(id)
      removeSongLocal(id)
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
    lastFetchedAt,
    fetchSongs,
    deleteSong,
    searchSongs,
    setFilter,
    invalidate,
    upsertSong,
    removeSongLocal,
  }
})
