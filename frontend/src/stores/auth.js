import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const username = ref(localStorage.getItem('username') || null)
  const userId = ref(localStorage.getItem('userId') || null)
  const isLoading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    isLoading.value = true
    error.value = null
    try {
      const data = await api.login(email, password)
      token.value = data.access_token
      username.value = data.username
      userId.value = data.user_id
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('userId', data.user_id)
      return data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function register(usernameVal, email, password) {
    isLoading.value = true
    error.value = null
    try {
      await api.register(usernameVal, email, password)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = null
    username.value = null
    userId.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
  }

  function initFromStorage() {
    const storedToken = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    const storedUserId = localStorage.getItem('userId')
    if (storedToken && storedUsername) {
      token.value = storedToken
      username.value = storedUsername
      userId.value = storedUserId
    }
  }

  return {
    token,
    username,
    userId,
    isLoading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    initFromStorage
  }
})