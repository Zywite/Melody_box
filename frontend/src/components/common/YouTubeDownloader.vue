<template>
  <div class="youtube-downloader">
    <YouTubeSearch
      :query="searchQuery"
      :is-searching="isSearching"
      :results="searchResults"
      :filtered="filteredResults.length"
      :duration="durationFilter"
      :sort="sortBy"
      :has-searched="hasSearched"
      @search="searchYouTube"
      @update:query="searchQuery = $event"
      @update:duration="durationFilter = $event"
      @update:sort="sortBy = $event"
    >
      <div class="results-grid">
        <VideoCard
          v-for="video in filteredResults"
          :key="video.video_id"
          :video="video"
          :selected="selectedVideo?.video_id === video.video_id"
          @select="selectVideo(video)"
        />
      </div>
    </YouTubeSearch>

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
import { usePolling } from '@/composables/usePolling'
import api from '@/composables/useApi'
import YouTubeSearch from '@/components/common/YouTubeSearch.vue'
import VideoCard from '@/components/common/VideoCard.vue'
import { Download, CheckCircle, AlertCircle } from 'lucide-vue-next'

const emit = defineEmits(['downloaded'])

const playerStore = usePlayerStore()
const libraryStore = useLibraryStore()
const toast = useToast()

const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const hasSearched = ref(false)

// Filters
const durationFilter = ref('all')
const sortBy = ref('relevance')

// Filtered results
const filteredResults = computed(() => {
  let results = [...searchResults.value]
  
  // Duration filter
  if (durationFilter.value !== 'all') {
    results = results.filter(video => {
      const duration = video.duration || 0
      if (durationFilter.value === 'short') return duration < 240
      if (durationFilter.value === 'medium') return duration >= 240 && duration < 600
      if (durationFilter.value === 'long') return duration >= 600
      return true
    })
  }
  
  // Sort
  if (sortBy.value === 'views') {
    results.sort((a, b) => (b.views || 0) - (a.views || 0))
  } else if (sortBy.value === 'date') {
    results.sort((a, b) => {
      const dateA = new Date(a.upload_date || '1970-01-01')
      const dateB = new Date(b.upload_date || '1970-01-01')
      return dateB - dateA
    })
  }
  // relevance - keep original order
  
  return results
})

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

const { startPolling, stopPolling } = usePolling()

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

async function downloadVideo() {
  if (!selectedVideo.value) return

  isDownloading.value = true
  downloadStatus.value = 'Iniciando descarga...'
  downloadProgress.value = 10
  downloadError.value = null
  downloadComplete.value = false

  try {
    downloadStatus.value = 'Enviando solicitud...'
    downloadProgress.value = 15

    const response = await api.youtubeDownload(
      selectedVideo.value.video_id,
      selectedFormat.value,
      selectedQuality.value,
      customTitle.value || null,
      customArtist.value || null
    )

    if (response.task_id) {
      downloadStatus.value = 'Descarga en cola...'
      downloadProgress.value = 20

      const taskResult = await startPolling({
        taskId: response.task_id,
        fetchTask: (id) => api.get(`/tasks/${id}`),
        interval: 2000,
        maxAttempts: 120,
        onProgress: (status, attempts) => {
          downloadStatus.value = status === 'processing' ? 'Descargando...' : 'En cola...'
          downloadProgress.value = Math.min(70, 20 + attempts * 2)
        },
        onDone: () => {
          downloadProgress.value = 80
          downloadStatus.value = 'Procesado!'
        },
      })

      const songId = taskResult?.song_id
      downloadedSong.value = songId ? await api.get(`/songs/${songId}`) : null
    } else {
      downloadedSong.value = response
    }

    downloadStatus.value = 'Guardando en biblioteca...'
    downloadProgress.value = 90

    downloadComplete.value = true
    downloadProgress.value = 100
    downloadStatus.value = 'Completado!'

    await libraryStore.fetchSongs()

    toast.success('Descargado', `"${downloadedSong.value?.title || ''}" agregado a tu biblioteca`)

    emit('downloaded', downloadedSong.value)

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

.results-grid {
  @apply grid gap-4;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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