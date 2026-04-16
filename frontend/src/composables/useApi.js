import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response.data,
  error => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        return api(originalRequest).catch(err => {
          if (err.response?.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            localStorage.removeItem('userId')
          }
          return Promise.reject(err)
        })
      }
    }
    
    const message = error.response?.data?.detail || error.message || 'Error de conexión'
    return Promise.reject(new Error(message))
  }
)

export default {
  async register(username, email, password) {
    return api.post('/auth/register', { username, email, password })
  },

  async login(email, password) {
    const data = await api.post('/auth/login', { email, password })
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
    }
    return data
  },

  logout() {
    localStorage.removeItem('token')
  },

  async getSongs() {
    return api.get('/songs')
  },

  async getSong(songId) {
    return api.get(`/songs/${songId}`)
  },

  async searchSongs(query) {
    return api.get(`/songs/search?q=${encodeURIComponent(query)}`)
  },

  async uploadSong(file, title, artist, album = '') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('artist', artist)
    if (album) formData.append('album', album)

    const token = localStorage.getItem('token')
    const response = await axios.post(`${API_BASE_URL}/songs/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    return response.data
  },

  async deleteSong(id) {
    return api.delete(`/songs/${id}`)
  },

  async getPlaylists() {
    return api.get('/playlists')
  },

  async getPlaylist(playlistId) {
    return api.get(`/playlists/${playlistId}`)
  },

  async createPlaylist(name, description = '') {
    return api.post('/playlists', { name, description })
  },

  async addSongToPlaylist(playlistId, songId) {
    return api.post(`/playlists/${playlistId}/songs`, { song_id: songId })
  },

  async removeSongFromPlaylist(playlistId, songId) {
    return api.delete(`/playlists/${playlistId}/songs/${songId}`)
  },

  async deletePlaylist(playlistId) {
    return api.delete(`/playlists/${playlistId}`)
  },

  async getFavorites() {
    return api.get('/favorites')
  },

  async addFavorite(songId) {
    return api.post('/favorites', { song_id: songId })
  },

  async removeFavorite(songId) {
    return api.delete(`/favorites/${songId}`)
  },

  streamUrl(mediaId) {
    return `${API_BASE_URL}/songs/${mediaId}/stream`
  },

  getBaseUrl() {
    return API_BASE_URL
  }
}