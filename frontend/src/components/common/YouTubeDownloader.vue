<template>
  <div class="youtube-downloader">
    <div class="search-section">
      <div class="search-input-wrapper">
        <Search :size="20" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="search-field"
          placeholder="Buscar videos en YouTube..."
          @keyup.enter="searchYouTube"
        />
        <button v-if="searchQuery" @click="searchQuery = ''" class="clear-btn">
          <X :size="18" />
        </button>
      </div>
      <button @click="searchYouTube" class="btn-primary" :disabled="isSearching || !searchQuery.trim()">
        <Search :size="18" />
        Buscar
      </button>
    </div>

    <div v-if="isSearching" class="loading-state">
      <div class="spinner"></div>
      <p>Buscando en YouTube...</p>
    </div>

    <div v-else-if="searchResults.length" class="results-section">
      <h3 class="section-label">Resultados ({{ searchResults.length }})</h3>
      <div class="results-grid">
        <div
          v-for="video in searchResults"
          :key="video.video_id"
          class="video-card"
          :class="{ selected: selectedVideo?.video_id === video.video_id }"
          @click="selectVideo(video)"
        >
          <div class="video-thumbnail">
            <img :src="video.thumbnail" :alt="video.title" />
            <span class="video-duration">{{ formatDuration(video.duration) }}</span>
            <div class="video-play-overlay">
              <Play :size="24" fill="white" />
            </div>
          </div>
          <div class="video-info">
            <p class="video-title">{{ video.title }}</p>
            <p class="video-channel">{{ video.channel }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="hasSearched && !searchResults.length" class="empty-state">
      <Youtube :size="48" class="opacity-30" />
      <h3>No se encontraron resultados</h3>
      <p>Intenta con otras palabras clave</p>
    </div>

    <div v-if="selectedVideo" class="download-section">
      <div class="selected-info">
        <h3 class="section-label">Descargar:</h3>
        <div class="selected-video">
          <img :src="selectedVideo.thumbnail" class="selected-thumb" />
          <div class="selected-details">
            <p class="selected-title">{{ selectedVideo.title }}</p>
            <p class="selected-channel">{{ selectedVideo.channel }}</p>
          </div>
        </div>
      </div>

      <div class="download-options">
        <div class="option-group">
          <label>Formato</label>
          <select v-model="selectedFormat" class="option-select">
            <option value="m4a">M4A (Audio - 320k)</option>
            <option value="mp3">MP3 (Audio - 320k)</option>
            <option value="wav">WAV (Audio - Sin pérdida)</option>
            <option value="flac">FLAC (Audio - Sin pérdida)</option>
            <option value="ogg">OGG (Audio)</option>
            <option value="mp4">MP4 (Video - 1080p)</option>
            <option value="mkv">MKV (Video - 1080p)</option>
          </select>
        </div>

        <div class="option-group">
          <label>Calidad</label>
          <select v-model="selectedQuality" class="option-select">
            <option v-if="isAudioFormat" value="320">320 kbps (Alta)</option>
            <option v-if="isAudioFormat" value="256">256 kbps (Media)</option>
            <option v-if="isAudioFormat" value="128">128 kbps (Baja)</option>
            <option v-if="!isAudioFormat" value="1080p">1080p (Full HD)</option>
            <option v-if="!isAudioFormat" value="720p">720p (HD)</option>
            <option v-if="!isAudioFormat" value="480p">480p (SD)</option>
          </select>
        </div>
      </div>

      <div class="custom-fields">
        <div class="option-group">
          <label>Título (opcional)</label>
          <input
            v-model="customTitle"
            type="text"
            class="option-input"
            :placeholder="selectedVideo.title"
          />
        </div>
        <div class="option-group">
          <label>Artista (opcional)</label>
          <input
            v-model="customArtist"
            type="text"
            class="option-input"
            :placeholder="selectedVideo.channel"
          />
        </div>
      </div>

      <div v-if="isDownloading" class="download-progress">
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: downloadProgress + '%' }"></div>
          </div>
          <span class="progress-text">{{ downloadStatus }}</span>
        </div>
      </div>

      <button
        @click="downloadVideo"
        class="btn-primary download-btn"
        :disabled="isDownloading"
      >
        <Download :size="18" />
        {{ isDownloading ? 'Descargando...' : 'Descargar' }}
      </button>

      <div v-if="downloadComplete" class="download-success">
        <CheckCircle :size="20" />
        <span>¡Descargado exitosamente!</span>
        <button @click="playDownloaded" class="btn-play">
          <Play :size="16" fill="currentColor" />
          Reproducir
        </button>
      </div>

      <div v-if="downloadError" class="download-error">
        <AlertCircle :size="20" />
        <span>{{ downloadError }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import { Search, X, Play, Youtube, Download, CheckCircle, AlertCircle } from 'lucide-vue-next'

const emit = defineEmits(['downloaded'])

const playerStore = usePlayerStore()
const libraryStore = useLibraryStore()
const toast = useToast()

const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const hasSearched = ref(false)

const selectedVideo = ref(null)
const selectedFormat = ref('m4a')
const selectedQuality = ref('320')
const customTitle = ref('')
const customArtist = ref('')

const isDownloading = ref(false)
const downloadProgress = ref(0)
const downloadStatus = ref('')
const downloadComplete = ref(false)
const downloadError = ref(null)
const downloadedSong = ref(null)

const isAudioFormat = computed(() => {
  return ['m4a', 'mp3', 'wav', 'flac', 'ogg'].includes(selectedFormat.value)
})

async function searchYouTube() {
  if (!searchQuery.value.trim()) return

  isSearching.value = true
  hasSearched.value = true
  searchResults.value = []
  downloadComplete.value = false
  downloadError.value = null

  try {
    const results = await api.youtubeSearch(searchQuery.value)
    searchResults.value = results || []
  } catch (e) {
    toast.error('Error', e.message || 'Error al buscar en YouTube')
  } finally {
    isSearching.value = false
  }
}

function selectVideo(video) {
  selectedVideo.value = video
  downloadComplete.value = false
  downloadError.value = null
  customTitle.value = ''
  customArtist.value = ''
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function downloadVideo() {
  if (!selectedVideo.value) return

  isDownloading.value = true
  downloadStatus.value = 'Iniciando descarga...'
  downloadProgress.value = 10
  downloadError.value = null
  downloadComplete.value = false

  try {
    downloadStatus.value = 'Descargando video...'
    downloadProgress.value = 30

    const song = await api.youtubeDownload(
      selectedVideo.value.video_id,
      selectedFormat.value,
      selectedQuality.value,
      customTitle.value || null,
      customArtist.value || null
    )

    downloadStatus.value = 'Guardando en biblioteca...'
    downloadProgress.value = 90

    downloadedSong.value = song
    downloadComplete.value = true
    downloadProgress.value = 100
    downloadStatus.value = 'Completado!'

    await libraryStore.fetchSongs()

    toast.success('Descargado', `"${song.title}" agregado a tu biblioteca`)

    emit('downloaded', song)

  } catch (e) {
    downloadError.value = e.message || 'Error al descargar el video'
    toast.error('Error', downloadError.value)
  } finally {
    isDownloading.value = false
  }
}

function playDownloaded() {
  if (downloadedSong.value) {
    playerStore.playSong(downloadedSong.value, libraryStore.songs)
  }
}
</script>

<style scoped>
.youtube-downloader {
  @apply flex flex-col gap-6;
}

.search-section {
  @apply flex gap-3;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: var(--text-secondary);
  pointer-events: none;
}

.search-field {
  width: 100%;
  padding: 14px 44px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.3s ease;
}

.search-field:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.clear-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
}

.section-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.results-grid {
  @apply grid gap-4;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

.video-card {
  @apply rounded-xl overflow-hidden cursor-pointer transition-all duration-200;
  background: var(--bg-secondary);
  border: 2px solid transparent;
}

.video-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-4px);
}

.video-card.selected {
  border-color: var(--accent-primary);
}

.video-thumbnail {
  position: relative;
  aspect-ratio: 16/9;
  background: var(--bg-tertiary);
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
}

.video-play-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.video-card:hover .video-play-overlay {
  opacity: 1;
}

.video-info {
  padding: 12px;
}

.video-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-channel {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.download-section {
  @apply mt-6 p-6 rounded-2xl;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
}

.selected-video {
  @apply flex items-center gap-4;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  margin-bottom: 16px;
}

.selected-thumb {
  width: 80px;
  height: 45px;
  object-fit: cover;
  border-radius: 6px;
}

.selected-title {
  font-weight: 600;
  color: var(--text-primary);
}

.selected-channel {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.download-options {
  @apply flex gap-4 mb-4;
}

.option-group {
  flex: 1;
}

.option-group label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.option-select,
.option-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.option-select:focus,
.option-input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.download-progress {
  margin: 16px 0;
}

.progress-bar-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), #7c3aed);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.download-btn {
  width: 100%;
  margin-top: 16px;
}

.download-success {
  @apply flex items-center gap-3 mt-4 p-4 rounded-xl;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid var(--success);
  color: var(--success);
}

.btn-play {
  @apply flex items-center gap-2 px-4 py-2 rounded-full font-medium;
  background: var(--success);
  color: white;
  margin-left: auto;
}

.download-error {
  @apply flex items-center gap-3 mt-4 p-4 rounded-xl;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid var(--danger);
  color: var(--danger);
}

@media (max-width: 640px) {
  .download-options {
    flex-direction: column;
  }
}
</style>