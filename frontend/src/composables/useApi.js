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
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userId')
      localStorage.removeItem('role')
      window.location.href = '/'
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

  async getSongs(page = 1, limit = 50) {
    return api.get(`/songs?skip=${(page - 1) * limit}&limit=${limit}`)
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
    return api.post('/songs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  async uploadMultipleSongs(files, metadataArray) {
    const formData = new FormData()
    for (const file of files) {
      formData.append('files', file)
    }
    formData.append('metadata', JSON.stringify(metadataArray))
    return api.post('/songs/upload-multiple', formData)
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

  async youtubeSearch(query, limit = 10) {
    return api.get(`/youtube/search?q=${encodeURIComponent(query)}&limit=${limit}`)
  },

  async youtubeDownload(videoId, format, quality, title = null, artist = null) {
    return api.post('/youtube/download', {
      video_id: videoId,
      format,
      quality,
      title,
      artist
    })
  },

  getBaseUrl() {
    return API_BASE_URL
  },

  async get(url) {
    return api.get(url)
  },

  // ── Admin API ──────────────────────────────────────────────────────────

  async adminGetUsers(search, skip = 0, limit = 100) {
    const params = { skip, limit }
    if (search) params.search = search
    return api.get('/admin/users', { params })
  },

  async adminCountUsers() {
    return api.get('/admin/users/count')
  },

  async adminUpdateUser(userId, data) {
    return api.patch(`/admin/users/${userId}`, data)
  },

  async adminDeleteUser(userId) {
    return api.delete(`/admin/users/${userId}`)
  },

  async adminToggleUserActive(userId) {
    return api.patch(`/admin/users/${userId}/toggle-active`)
  },

  async adminGetUserStats(userId) {
    return api.get(`/admin/users/${userId}/stats`)
  },

  async adminGetSongs(skip = 0, limit = 100) {
    return api.get('/admin/songs', { params: { skip, limit } })
  },

  async adminDeleteSong(songId) {
    return api.delete(`/admin/songs/${songId}`)
  },

  async adminGetPlaylists(skip = 0, limit = 100) {
    return api.get('/admin/playlists', { params: { skip, limit } })
  },

  async adminDeletePlaylist(playlistId) {
    return api.delete(`/admin/playlists/${playlistId}`)
  },
}