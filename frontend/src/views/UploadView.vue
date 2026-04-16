<template>
  <div class="upload-view">
    <header class="page-header">
      <h1 class="text-3xl font-bold">Subir música</h1>
      <p class="text-[var(--text-secondary)]">Agrega canciones o videos a tu biblioteca</p>
    </header>

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
        <p class="text-sm text-center mt-2">{{ uploadProgress }}%</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import api from '@/composables/useApi'
import { Upload, Music, X } from 'lucide-vue-next'

const router = useRouter()
const libraryStore = useLibraryStore()
const toast = useToast()

const fileInput = ref(null)
const selectedFiles = ref([])
const isUploading = ref(false)
const uploadProgress = ref(0)

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

  try {
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i]
      await api.uploadSong(file, uploadData.title, uploadData.artist, uploadData.album)
      uploadProgress.value = Math.round(((i + 1) / selectedFiles.value.length) * 100)
    }

    toast.success('Archivos subidos correctamente')
    await libraryStore.fetchSongs()
    clearFiles()
    router.push('/library')
  } catch (e) {
    toast.error('Error al subir', e.message)
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}
</script>