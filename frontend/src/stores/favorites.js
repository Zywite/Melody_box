import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from './auth'

const FAVORITES_CACHE_KEY = 'melodybox:cache:favorites:v1'
const FAVORITES_STALE_AFTER_MS = 30_000

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref([])
  const error = ref(null)
  const lastFetchedAt = ref(0)
  const isLoading = ref(false)
  const pendingSongIds = ref(new Set())

  const authStore = useAuthStore()

  function _persistCache() {
    try {
      sessionStorage.setItem(FAVORITES_CACHE_KEY, JSON.stringify({
        favorites: favorites.value,
        ts: lastFetchedAt.value,
      }))
    } catch {
      // ignore
    }
  }

  function _restoreCache() {
    try {
      const raw = sessionStorage.getItem(FAVORITES_CACHE_KEY)
      if (!raw) return false
      const parsed = JSON.parse(raw)
      if (!parsed?.favorites) return false
      favorites.value = parsed.favorites
      lastFetchedAt.value = parsed.ts || 0
      return true
    } catch {
      return false
    }
  }

  function isFavorite(songId) {
    return favorites.value.some(f => (f.song_id || f.song?.id) === songId)
  }

  async function fetchFavorites({ force = false } = {}) {
    if (!authStore.isAuthenticated) return

    if (!force && lastFetchedAt.value > 0
        && Date.now() - lastFetchedAt.value < FAVORITES_STALE_AFTER_MS
        && favorites.value.length > 0) {
      return
    }
    if (!force) _restoreCache()

    isLoading.value = true
    try {
      favorites.value = await api.getFavorites()
      lastFetchedAt.value = Date.now()
      _persistCache()
    } catch (e) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  function invalidate() {
    lastFetchedAt.value = 0
    try {
      sessionStorage.removeItem(FAVORITES_CACHE_KEY)
    } catch {
      // ignore
    }
  }

  function _addLocal(songId, song) {
    if (isFavorite(songId)) return
    favorites.value = [
      { song_id: songId, song: song || null },
      ...favorites.value,
    ]
    _persistCache()
  }

  function _removeLocal(songId) {
    favorites.value = favorites.value.filter(
      f => (f.song_id || f.song?.id) !== songId
    )
    _persistCache()
  }

  async function addFavorite(songId, song = null) {
    if (pendingSongIds.value.has(songId)) return
    pendingSongIds.value.add(songId)

    const wasPresent = isFavorite(songId)
    _addLocal(songId, song)

    try {
      await api.addFavorite(songId)
    } catch (e) {
      if (!wasPresent) _removeLocal(songId)
      error.value = e.message
      throw e
    } finally {
      pendingSongIds.value.delete(songId)
    }
  }

  async function removeFavorite(songId) {
    if (pendingSongIds.value.has(songId)) return
    pendingSongIds.value.add(songId)

    const snapshot = favorites.value
    _removeLocal(songId)

    try {
      await api.removeFavorite(songId)
    } catch (e) {
      favorites.value = snapshot
      _persistCache()
      error.value = e.message
      throw e
    } finally {
      pendingSongIds.value.delete(songId)
    }
  }

  async function toggleFavorite(songId, song = null) {
    if (isFavorite(songId)) {
      await removeFavorite(songId)
      return false
    }
    await addFavorite(songId, song)
    return true
  }

  return {
    favorites,
    error,
    isLoading,
    lastFetchedAt,
    isFavorite,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    invalidate,
  }
})
