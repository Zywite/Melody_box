import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from './auth'

export const useFavoritesStore = defineStore('favorites', () => {
  const favorites = ref([])
  const error = ref(null)

  const authStore = useAuthStore()

  async function fetchFavorites() {
    if (!authStore.isAuthenticated) return
    try {
      favorites.value = await api.getFavorites()
    } catch (e) {
      error.value = e.message
    }
  }

  async function addFavorite(songId) {
    try {
      await api.addFavorite(songId)
      await fetchFavorites()
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  async function removeFavorite(songId) {
    try {
      await api.removeFavorite(songId)
      await fetchFavorites()
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  return {
    favorites,
    error,
    fetchFavorites,
    addFavorite,
    removeFavorite,
  }
})
