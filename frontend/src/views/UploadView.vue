<template>
  <div class="upload-view">
    <header class="page-header">
      <h1 class="header-title">Subir música</h1>
      <p class="header-subtitle">Agrega canciones o videos a tu biblioteca</p>
    </header>

    <div class="upload-tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'file' }]"
        @click="activeTab = 'file'"
      >
        <Upload :size="18" />
        Archivo
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'youtube' }]"
        @click="activeTab = 'youtube'"
      >
        <Youtube :size="18" />
        YouTube
      </button>
    </div>

    <div v-if="activeTab === 'file'" class="upload-section">
      <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
        <input
          ref="fileInput"
          type="file"
          accept=".mp3,.wav,.flac,.ogg,.m4a,.mp4,.mkv,.avi,.webm,.mov"
          multiple
          class="hidden"
          @change="handleFileSelect"
        />
        
        <div v-if="!selectedFiles.length" class="upload-placeholder" @click="triggerFileInput">
          <Upload :size="48" class="opacity-50" />
          <h3 class="text-xl font-semibold mt-4">Arrastra archivos aquí</h3>
          <p class="text-[var(--text-secondary)]">o haz clic para seleccionar</p>
          <p class="text-sm text-[var(--text-secondary)] mt-2">
            MP3, WAV, FLAC, OGG, M4A, MP4, MKV, AVI, WebM, MOV
          </p>
        </div>

        <div v-else class="file-list">
          <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
            <div class="file-info">
              <Music :size="20" class="opacity-50" />
              <div class="flex-1">
                <p class="font-medium">{{ file.name }}</p>
                <p class="text-sm text-[var(--text-secondary)]">{{ formatSize(file.size) }}</p>
              </div>
            </div>
            <button @click="removeFile(index)" class="btn-icon">
              <X :size="18" />
            </button>
          </div>

          <div class="form-grid mt-6">
            <div class="form-group">
              <label class="form-label">Título</label>
              <input v-model="uploadData.title" type="text" class="input-field" placeholder="Título de la canción" />
            </div>
            <div class="form-group">
              <label class="form-label">Artista</label>
              <input v-model="uploadData.artist" type="text" class="input-field" placeholder="Nombre del artista" />
            </div>
            <div class="form-group">
              <label class="form-label">Álbum (opcional)</label>
              <input v-model="uploadData.album" type="text" class="input-field" placeholder="Nombre del álbum" />
            </div>
          </div>

          <div class="flex gap-4 mt-6">
            <button @click="uploadFiles" class="btn-primary" :disabled="isUploading">
              <span v-if="isUploading">Subiendo...</span>
              <span v-else>Subir {{ selectedFiles.length }} archivo(s)</span>
            </button>
            <button @click="clearFiles" class="btn-secondary">Cancelar</button>
          </div>
        </div>

        <div v-if="uploadProgress > 0" class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p class="text-sm text-center mt-2 font-semibold" :class="uploadStatus.includes('FFT') ? 'text-[var(--accent)]' : 'text-[var(--text-secondary)]'">{{ uploadStatus || uploadProgress + '%' }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="activeTab === 'youtube'" class="youtube-section">
      <YouTubeDownloader @downloaded="onYouTubeDownloaded" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useLibraryStore } from '@/stores/library'
import { usePlayerStore } from '@/stores/player'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import YouTubeDownloader from '@/components/common/YouTubeDownloader.vue'
import { Upload, Music, X, Youtube } from 'lucide-vue-next'

const router = useRouter()
const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const toast = useToast()

const activeTab = ref('file')
const fileInput = ref(null)
const selectedFiles = ref([])
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')

const uploadData = reactive({
  title: '',
  artist: '',
  album: ''
})

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  addFiles(files)
}

function handleDrop(event) {
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

function addFiles(files) {
  const validExtensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.mp4', '.mkv', '.avi', '.webm', '.mov']
  const validFiles = files.filter(f => validExtensions.some(ext => f.name.toLowerCase().endsWith(ext)))
  selectedFiles.value = [...selectedFiles.value, ...validFiles]
  
  if (validFiles.length > 0 && !uploadData.title) {
    const firstFile = validFiles[0]
    const nameWithoutExt = firstFile.name.replace(/\.[^/.]+$/, '')
    uploadData.title = nameWithoutExt
  }
}

function removeFile(index) {
  selectedFiles.value.splice(index, 1)
}

function clearFiles() {
  selectedFiles.value = []
  uploadData.title = ''
  uploadData.artist = ''
  uploadData.album = ''
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function uploadFiles() {
  if (!uploadData.title || !uploadData.artist) {
    toast.error('Completa título y artista')
    return
  }

  isUploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = 'Subiendo archivo...'
  console.log('[Upload] Starting upload...')
  
  let firstSongId = null
  
  try {
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i]
      uploadStatus.value = `Subiendo ${file.name}...`
      console.log(`[Upload] Uploading file ${i+1}/${selectedFiles.value.length}: ${file.name}`)
      
      const result = await api.uploadSong(file, uploadData.title, uploadData.artist, uploadData.album)
      uploadProgress.value = Math.round(((i + 1) / selectedFiles.value.length) * 100)
      
      console.log(`[Upload] Upload complete for ${result.title}, fft_ready: ${result.fft_ready}`)
      
      if (result.fft_ready) {
        toast.success(`"${result.title}" subido y analizado exitosamente`)
      } else {
        toast.warning(`"${result.title}" subido, pero falló el análisis FFT`)
      }
      
      // Save first song ID for redirect
      if (i === 0 && result.id) {
        firstSongId = result.id
      }
    }
    
    uploadStatus.value = 'Analizando FFT...'
    console.log('[Upload] All files uploaded. Redirecting to FFT...')
    toast.info('Redirigiendo a Análisis FFT...')
    await libraryStore.fetchSongs()
    clearFiles()
    
    // Redirect to FFT with the first uploaded song
    if (firstSongId) {
      setTimeout(() => {
        console.log(`[Upload] Redirecting to FFT view with songId=${firstSongId}`)
        router.push(`/fft?songId=${firstSongId}`)
      }, 1000)
    } else {
      router.push('/library')
    }
  } catch (e) {
    console.error('[Upload] Error:', e)
    toast.error('Error al subir', e.message)
  } finally {
    isUploading.value = false
    uploadStatus.value = ''
    uploadProgress.value = 0
  }
}

function onYouTubeDownloaded(song) {
  router.push('/library')
}
</script>

<style scoped>
.page-header {
  margin-bottom: 28px;
}

.header-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  margin-bottom: 4px;
}

.header-subtitle {
  font-size: 1rem;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
}

.upload-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 28px;
  background: var(--bg-secondary);
  padding: 6px;
  border-radius: 20px;
  width: fit-content;
  border: 2px solid var(--border);
}

.upload-tabs .tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 16px;
  background: transparent;
  color: var(--text-secondary);
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-tabs .tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.upload-tabs .tab-btn.active {
  background: var(--accent-gradient);
  color: #fff;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.upload-section,
.youtube-section {
  animation: fadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.upload-area {
  border: 3px dashed var(--border);
  border-radius: 32px;
  padding: 48px 32px;
  text-align: center;
  transition: all var(--transition);
  background: var(--bg-secondary);
  cursor: pointer;
}

.upload-area:hover {
  border-color: var(--accent);
  background: rgba(255, 158, 187, 0.1);
  transform: scale(1.01);
}

.upload-placeholder {
  cursor: pointer;
}

.upload-placeholder h3 {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  color: var(--text-primary);
  margin-top: 16px;
}

.upload-placeholder p {
  font-family: 'Nunito', sans-serif;
  color: var(--text-secondary);
}

.file-list {
  text-align: left;
  margin-top: 24px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-radius: 16px;
  background: var(--bg-secondary);
  margin-bottom: 8px;
  border: 2px solid var(--border);
  transition: all var(--transition-fast);
}

.file-item:hover {
  border-color: var(--accent-light);
  transform: translateX(4px);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-info p {
  font-family: 'Nunito', sans-serif;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
}

.upload-progress {
  margin-top: 24px;
}

.progress-bar {
  height: 10px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  background-size: 200% 200%;
  transition: width 0.3s ease;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>