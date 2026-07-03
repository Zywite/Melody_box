<template>
  <div class="fft-view">
    <header class="page-header">
      <div class="header-content">
        <h1 class="header-title">🔊 Análisis de Audio FFT</h1>
        <p class="header-subtitle">Visualización de frecuencias y espectrogramas</p>
      </div>
    </header>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <Music :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ analyzedCount }}</p>
            <p class="stat-label">Analizadas</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending">
            <Activity :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ pendingCount }}</p>
            <p class="stat-label">Pendientes</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <ListMusic :size="20" />
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ songs.length }}</p>
            <p class="stat-label">Total</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Analyze All Button -->
    <div v-if="pendingCount > 0" class="analyze-all-section">
      <button @click="analyzeAllPending" :disabled="isAnalyzingAll" class="btn-analyze-all">
        <RefreshCw :size="18" :class="{ 'spin': isAnalyzingAll }" />
        {{ isAnalyzingAll ? `Analizando... (${analyzeProgress}/${pendingCount})` : `Analizar todas las faltantes (${pendingCount})` }}
      </button>
    </div>

    <!-- Song List with FFT Status -->
    <FFTSongList
      :songs="songs"
      :selected-song-id="selectedSongId"
      :is-analyzing="isAnalyzing"
      :analyzing-song-id="analyzingSongId"
      @select-song="selectSong"
      @analyze-song="analyzeSingleSong"
    />

    <!-- FFT Results -->
    <div v-if="result" class="results-section">
      <div class="results-header">
        <h2 class="section-title">Resultados: {{ selectedSongTitle }}</h2>
        <button @click="clearResults" class="btn-clear">✕</button>
      </div>
      <FFTCanvas :result="result" />
    </div>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">Analizando audio con FFT...</p>
      <p class="loading-subtext">Esto puede tardar unos segundos</p>
    </div>
    
    <!-- Analyzing FFT State (song selected but pending) -->
    <div v-if="isAnalyzingFFT" class="analyzing-state">
      <div class="analyzing-spinner"></div>
      <p class="analyzing-text">Analizando FFT para "{{ selectedSongTitle }}"...</p>
      <p class="analyzing-subtext">Esto puede tardar unos segundos</p>
      <div class="analyzing-progress">
        <div class="analyzing-dots">
          <span class="dot" :style="{ animationDelay: '0s' }">.</span>
          <span class="dot" :style="{ animationDelay: '0.2s' }">.</span>
          <span class="dot" :style="{ animationDelay: '0.4s' }">.</span>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="!result && !isLoading && !selectedSongId" class="empty-state">
      <p>Selecciona una canción de la lista para ver su análisis FFT</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import { usePolling } from '@/composables/usePolling'
import { formatTime } from '@/utils/format'
import api from '@/composables/useApi'
import { Music, Activity, ListMusic, RefreshCw } from 'lucide-vue-next'
import FFTCanvas from '@/components/fft/FFTCanvas.vue'
import FFTSongList from '@/components/fft/FFTSongList.vue'

const route = useRoute()
const libraryStore = useLibraryStore()
const toast = useToast()
const { startPolling } = usePolling()

const songs = computed(() => libraryStore.songs || [])
const selectedSongId = ref('')
const selectedSongTitle = ref('')
const result = ref(null)
const isLoading = ref(false)
const isAnalyzing = ref(false)
const isAnalyzingAll = ref(false)
const analyzeProgress = ref(0)
const analyzingSongId = ref(null)
const isAnalyzingFFT = ref(false)

const analyzedCount = computed(() => songs.value.filter(s => s.has_fft).length)
const pendingCount = computed(() => songs.value.filter(s => !s.has_fft).length)

function selectSong(song) {
  selectedSongId.value = song.id
  selectedSongTitle.value = `${song.title} - ${song.artist}`
  isAnalyzingFFT.value = false
  result.value = null
  if (song.has_fft) loadFFTData(song.id)
}

async function loadFFTData(songId) {
  isLoading.value = true
  result.value = null
  try {
    const response = await api.get(`/songs/${songId}/fft`)
    if (response.task_id) {
      isLoading.value = false
      await waitForFFT(songId)
      return
    }
    result.value = response
  } catch (err) {
    toast.error('Error al cargar FFT', err.message)
  } finally {
    isLoading.value = false
  }
}

async function waitForFFT(songId, maxAttempts = 60) {
  isAnalyzingFFT.value = true
  let taskId = null
  try {
    const fftResponse = await api.get(`/songs/${songId}/fft`)
    if (fftResponse.task_id) {
      taskId = fftResponse.task_id
    } else if (fftResponse.bins) {
      isAnalyzingFFT.value = false
      result.value = fftResponse
      const song = songs.value.find(s => s.id === songId)
      if (song) song.has_fft = true
      return
    }
  } catch (err) {
    toast.error('Error al iniciar análisis FFT', err.message)
    isAnalyzingFFT.value = false
    return
  }

  if (!taskId) {
    isAnalyzingFFT.value = false
    return
  }

  try {
    await startPolling({
      taskId,
      fetchTask: (id) => api.get(`/tasks/${id}`),
      interval: 2000,
      maxAttempts,
      onDone: (taskResult) => {
        result.value = taskResult
        selectedSongId.value = songId
        const song = songs.value.find(s => s.id === songId)
        if (song) {
          song.has_fft = true
          selectedSongTitle.value = `${song.title} - ${song.artist}`
        }
      },
    })
  } catch {
    // handled by composable
  } finally {
    isAnalyzingFFT.value = false
  }
}

async function analyzeSingleSong(song) {
  analyzingSongId.value = song.id
  isAnalyzing.value = true
  try {
    await waitForFFT(song.id)
  } catch (err) {
    toast.error('Error al analizar', err.message || err)
  } finally {
    isAnalyzing.value = false
    analyzingSongId.value = null
  }
}

async function analyzeAllPending() {
  isAnalyzingAll.value = true
  analyzeProgress.value = 0
  const pendingSongs = songs.value.filter(s => !s.has_fft)
  try {
    await api.post('/songs/analyze-all')
    await libraryStore.fetchSongs()
    analyzeProgress.value = pendingSongs.length
  } catch (err) {
    toast.error('Error al analizar todas', err.message)
  } finally {
    isAnalyzingAll.value = false
  }
}

function clearResults() {
  result.value = null
  selectedSongId.value = ''
}

onMounted(async () => {
  if (!libraryStore.songs || libraryStore.songs.length === 0) {
    await libraryStore.fetchSongs()
  }
  const songId = route.query.songId
  if (songId) {
    selectedSongId.value = songId
    const song = songs.value.find(s => s.id === songId)
    if (song) {
      selectedSongTitle.value = `${song.title} - ${song.artist}`
      if (song.has_fft) {
        await loadFFTData(songId)
      } else {
        isAnalyzingFFT.value = true
        waitForFFT(songId).catch(err => {
          console.error('[FFTView] Failed to wait for FFT:', err)
          isAnalyzingFFT.value = false
        })
      }
    }
  }
})
</script>

<style scoped>
.fft-view {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 28px;
}

.header-content {
  animation: fadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
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

/* Stats Section */
.stats-section {
  margin-bottom: 28px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--accent-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-icon.pending {
  background: linear-gradient(135deg, var(--warning) 0%, var(--danger) 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

/* Analyze All Section */
.analyze-all-section {
  margin-bottom: 28px;
}

.btn-analyze-all {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 1rem;
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow);
}

.btn-analyze-all:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: var(--shadow-glow);
}

.btn-analyze-all:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Results Section */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.btn-clear {
  background: var(--danger);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.btn-clear:hover {
  transform: scale(1.1);
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.loading-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 8px;
}

.loading-subtext {
  font-size: 0.9rem;
  color: var(--text-muted);
}

/* Analyzing State */
.analyzing-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
  animation: fadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.analyzing-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.analyzing-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 8px;
}

.analyzing-subtext {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.analyzing-progress {
  margin-top: 16px;
}

.analyzing-dots {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.dot {
  font-size: 2rem;
  color: var(--accent);
  animation: dotPulse 1.4s infinite;
}

@keyframes dotPulse {
  0%, 20% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
  80%, 100% {
    opacity: 0.2;
  }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .stats-grid,
  .info-cards {
    grid-template-columns: 1fr;
  }
}
</style>
