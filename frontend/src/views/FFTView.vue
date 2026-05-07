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
    <section class="song-list-section">
      <h2 class="section-title">Canciones</h2>
      
      <div class="song-list">
        <div 
          v-for="song in songsWithStatus" 
          :key="song.id"
          @click="selectSong(song)"
          class="song-item"
          :class="{ active: selectedSongId === song.id }"
        >
          <div class="song-status">
            <CheckCircle v-if="song.has_fft" :size="18" class="status-done" />
            <Clock v-else :size="18" class="status-pending" />
          </div>
          <div class="song-info">
            <p class="song-title">{{ song.title }}</p>
            <p class="song-artist">{{ song.artist }}</p>
          </div>
          <div class="song-actions">
            <button 
              v-if="!song.has_fft" 
              @click.stop="analyzeSingleSong(song)"
              :disabled="isAnalyzing"
              class="btn-analyze-single"
            >
              {{ analyzingSongId === song.id ? '...' : '🔍' }}
            </button>
            <span v-else class="fft-badge">FFT ✓</span>
          </div>
        </div>
      </div>
    </section>

    <!-- FFT Results -->
    <div v-if="result" class="results-section">
      <div class="results-header">
        <h2 class="section-title">Resultados: {{ selectedSongTitle }}</h2>
        <button @click="clearResults" class="btn-clear">✕</button>
      </div>
      
      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-label">Duración</span>
          <span class="stat-value">{{ formatTime(result.duration) }}</span>
        </div>
<div class="stat-box">
          <span class="stat-label">Sample Rate</span>
          <span class="stat-value">{{ result.sample_rate }} Hz</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Canales</span>
          <span class="stat-value">{{ result.channels }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Bins FFT</span>
          <span class="stat-value">{{ result.bins.length }}</span>
        </div>
      </div>
      
      <div class="canvas-container">
        <h3 class="canvas-title">Espectro de Frecuencias</h3>
        <canvas ref="canvas"></canvas>
      </div>
      
      <div class="canvas-container spectrogram">
        <h3 class="canvas-title">Espectrograma</h3>
        <canvas ref="specCanvas"></canvas>
      </div>
      
      <div class="info-cards">
        <div class="info-card bass">
          <div class="card-icon">🔊</div>
          <h4>Graves (20-250 Hz)</h4>
          <p class="info-value">{{ result.bass_power.toFixed(1) }}%</p>
          <p class="info-desc">Bajos, bombo, bajo eléctrico</p>
        </div>
        <div class="info-card mid">
          <div class="card-icon">🎸</div>
          <h4>Medios (250-2k Hz)</h4>
          <p class="info-value">{{ result.mid_power.toFixed(1) }}%</p>
          <p class="info-desc">Voces, guitarras, sintetizadores</p>
        </div>
        <div class="info-card treble">
          <div class="card-icon">✨</div>
          <h4>Agudos (2k-20k Hz)</h4>
          <p class="info-value">{{ result.treble_power.toFixed(1) }}%</p>
          <p class="info-desc">Brillantes, platillos, aire</p>
        </div>
      </div>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useLibraryStore } from '@/stores/library'
import api from '@/composables/useApi'
import { Music, Activity, ListMusic, CheckCircle, Clock, RefreshCw } from 'lucide-vue-next'

const route = useRoute()
const libraryStore = useLibraryStore()

const songs = computed(() => libraryStore.songs || [])
const selectedSongId = ref('')
const selectedSongTitle = ref('')
const result = ref(null)
const canvas = ref(null)
const specCanvas = ref(null)
const isLoading = ref(false)
const isAnalyzing = ref(false)
const isAnalyzingAll = ref(false)
const analyzeProgress = ref(0)
const analyzingSongId = ref(null)
const isAnalyzingFFT = ref(false) // For pending analysis display
let pollInterval = null
  
const analyzedCount = computed(() => songs.value.filter(s => s.has_fft).length)
const pendingCount = computed(() => songs.value.filter(s => !s.has_fft).length)
const songsWithStatus = computed(() => songs.value)

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function selectSong(song) {
  selectedSongId.value = song.id
  selectedSongTitle.value = `${song.title} - ${song.artist}`
  isAnalyzingFFT.value = false
  
  if (song.has_fft) {
    loadFFTData(song.id)
  } else {
    result.value = null
  }
}

async function loadFFTData(songId) {
  isLoading.value = true
  result.value = null
  
  try {
    console.log(`[FFTView] Loading FFT data for song ${songId}...`)
    const response = await api.get(`/songs/${songId}/fft`)
    result.value = response
    await nextTick()
    drawCanvas()
    drawSpectrogram()
    console.log(`[FFTView] FFT data loaded successfully`)
  } catch (err) {
    console.error('[FFTView] Error loading FFT:', err)
  } finally {
    isLoading.value = false
  }
}

async function waitForFFT(songId, maxAttempts = 30) {
  console.log(`[FFTView] Waiting for FFT analysis to complete for song ${songId}...`)
  isAnalyzingFFT.value = true
  let attempts = 0
  
  return new Promise((resolve, reject) => {
    pollInterval = setInterval(async () => {
      attempts++
      console.log(`[FFTView] Polling FFT status, attempt ${attempts}/${maxAttempts}`)
      
      try {
        const response = await api.get(`/songs/${songId}/fft`)
        
        if (response && response.bins) {
          console.log(`[FFTView] FFT analysis complete!`)
          clearInterval(pollInterval)
          pollInterval = null
          result.value = response
          selectedSongId.value = songId
          const song = songs.value.find(s => s.id === songId)
          if (song) {
            song.has_fft = true
            selectedSongTitle.value = `${song.title} - ${song.artist}`
          }
          await nextTick()
          drawCanvas()
          drawSpectrogram()
          isAnalyzingFFT.value = false
          resolve(response)
        }
      } catch (err) {
        console.error(`[FFTView] Poll attempt ${attempts} failed:`, err)
        
        if (attempts >= maxAttempts) {
          clearInterval(pollInterval)
          pollInterval = null
          isAnalyzingFFT.value = false
          reject(new Error('FFT analysis timeout'))
        }
      }
    }, 2000) // Poll every 2 seconds
  })
}

async function analyzeSingleSong(song) {
  console.log(`[FFT] Analyzing song: ${song.id} - ${song.title}`)
  analyzingSongId.value = song.id
  isAnalyzing.value = true
  isAnalyzingFFT.value = true
  
  try {
    console.log(`[FFT] Calling API for song ${song.id}...`)
    const response = await api.get(`/songs/${song.id}/fft`)
    console.log(`[FFT] Response received:`, response)
    song.has_fft = true
    result.value = response
    selectedSongId.value = song.id
    selectedSongTitle.value = `${song.title} - ${song.artist}`
    await nextTick()
    drawCanvas()
    drawSpectrogram()
    console.log(`[FFT] Analysis complete for ${song.title}`)
  } catch (err) {
    console.error('[FFT] Error analyzing:', err)
    alert('Error al analizar: ' + (err.message || err))
  } finally {
    isAnalyzing.value = false
    analyzingSongId.value = null
    isAnalyzingFFT.value = false
  }
}

async function analyzeAllPending() {
  isAnalyzingAll.value = true
  analyzeProgress.value = 0
  const pendingSongs = songs.value.filter(s => !s.has_fft)
  
  try {
    const response = await api.post('/songs/analyze-all')
    // Reload songs to get updated status
    await libraryStore.fetchSongs()
    analyzeProgress.value = pendingSongs.length
  } catch (err) {
    console.error('Error analyzing all:', err)
  } finally {
    isAnalyzingAll.value = false
  }
}

function clearResults() {
  result.value = null
  selectedSongId.value = ''
}

function drawCanvas() {
  if (!result.value || !canvas.value) return
  
  const ctx = canvas.value.getContext('2d')
  const width = canvas.value.width = 800
  const height = canvas.value.height = 300
  
  // Get theme colors
  const bgColor = getComputedStyle(document.documentElement).getPropertyValue('--bg-secondary').trim() || '#ffe4ec'
  const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#7a7a7a'
  const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#ff9ebb'
  const accentLight = getComputedStyle(document.documentElement).getPropertyValue('--accent-light').trim() || '#ffb7c5'
  const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue('--secondary').trim() || '#b19cd9'
  
  // Background
  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)
  
  // Calculate nyquist frequency from sample rate
  const nyquist = result.value.sample_rate / 2
  const bins = result.value.bins
  const BAR_COUNT = 64
  const barWidth = (width - 80) / BAR_COUNT  // Leave space for labels
  const barMaxHeight = height * 0.75
  
  const step = Math.floor(bins.length / BAR_COUNT)
  
  // Draw grid lines
  ctx.strokeStyle = 'rgba(128,128,128,0.2)'
  ctx.lineWidth = 1
  for (let i = 0; i <= 10; i++) {
    const y = (height - 30) * (i / 10)
    ctx.beginPath()
    ctx.moveTo(60, y)
    ctx.lineTo(width - 20, y)
    ctx.stroke()
  }
  
  // dB labels on left
  ctx.fillStyle = textColor
  ctx.font = '10px Nunito'
  ctx.textAlign = 'right'
  const dbLabels = ['0 dB', '-10', '-20', '-30', '-40', '-50', '-60', '-70', '-80', '-90', '-∞']
  for (let i = 0; i <= 10; i++) {
    const y = (height - 30) * (i / 10) + 4
    ctx.fillText(dbLabels[i], 55, y)
  }
  
  // Find peak frequency
  let maxValue = 0
  let maxIndex = 0
  for (let i = 0; i < bins.length; i++) {
    if (bins[i] > maxValue) {
      maxValue = bins[i]
      maxIndex = i
    }
  }
  const peakFreq = (maxIndex / bins.length) * nyquist
  
  // Draw bars
  for (let i = 0; i < BAR_COUNT; i++) {
    let sum = 0
    for (let j = 0; j < step && (i * step + j) < bins.length; j++) {
      sum += bins[i * step + j]
    }
    const value = (sum / step) / 255
    const barHeight = value * barMaxHeight
    
    const x = 60 + i * (barWidth + 2)
    const y = (height - 30) - barHeight
    
    // Create gradient
    const gradient = ctx.createLinearGradient(x, (height - 30), x, y)
    gradient.addColorStop(0, accentColor)
    gradient.addColorStop(0.5, accentLight)
    gradient.addColorStop(1, secondaryColor)
    
    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.roundRect(x, y, barWidth, barHeight, 3)
    ctx.fill()
  }
  
  // Frequency labels at bottom
  ctx.fillStyle = textColor
  ctx.font = '10px Nunito'
  ctx.textAlign = 'center'
  const freqLabels = [
    { freq: 20, label: '20' },
    { freq: 100, label: '100' },
    { freq: 500, label: '500' },
    { freq: 1000, label: '1K' },
    { freq: 5000, label: '5K' },
    { freq: 10000, label: '10K' },
    { freq: 20000, label: '20K' }
  ]
  
  for (const label of freqLabels) {
    const x = 60 + (Math.log10(label.freq / 20) / Math.log10(nyquist / 20)) * (width - 80)
    if (x >= 60 && x <= width - 20) {
      ctx.fillText(label.label, x, height - 10)
    }
  }
  
  // Hz label
  ctx.fillText('Frecuencia (Hz)', width / 2, height - 2)
  
  // Peak indicator
  ctx.fillStyle = accentColor
  ctx.font = 'bold 11px Nunito'
  ctx.textAlign = 'left'
  ctx.fillText(`🔺 Pico: ${Math.round(peakFreq)} Hz`, width - 120, 20)
  
  // Title inside the canvas
  ctx.fillStyle = textColor
  ctx.font = 'bold 12px Nunito'
  ctx.fillText('Espectro de Frecuencias', 70, 15)
}

function drawSpectrogram() {
  if (!result.value || !specCanvas.value || !result.value.spectrogram) return
  
  const ctx = specCanvas.value.getContext('2d')
  const width = specCanvas.value.width = 800
  const height = specCanvas.value.height = 200
  
  const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#7a7a7a'
  
  // Background
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--bg-secondary').trim() || '#ffe4ec'
  ctx.fillRect(0, 0, width, height)
  
  const spectrogram = result.value.spectrogram
  const numFrames = spectrogram.length
  const numFreqBins = spectrogram[0].length
  
  // Leave space for labels
  const graphLeft = 50
  const graphTop = 20
  const graphWidth = width - 70
  const graphHeight = height - 40
  
  const colsPerFrame = graphWidth / numFrames
  
  for (let frame = 0; frame < numFrames; frame++) {
    const x = graphLeft + frame * colsPerFrame
    const bins = spectrogram[frame]
    
    for (let bin = 0; bin < numFreqBins; bin++) {
      const value = bins[bin] / 255
      const y = graphTop + (bin / numFreqBins) * graphHeight
      
      const binHeight = Math.max(1, graphHeight / numFreqBins)
      
      ctx.fillStyle = getColor(value)
      ctx.fillRect(x, graphHeight + graphTop - y - binHeight, Math.ceil(colsPerFrame), binHeight)
    }
  }
  
  // Frequency axis (left side)
  ctx.fillStyle = textColor
  ctx.font = '9px Nunito'
  ctx.textAlign = 'right'
  const nyquist = result.value.sample_rate / 2
  const freqLabels = [20, 100, 1000, 10000]
  for (const freq of freqLabels) {
    const y = graphTop + graphHeight - (Math.log10(freq / 20) / Math.log10(nyquist / 20)) * graphHeight
    if (y >= graphTop && y <= graphTop + graphHeight) {
      const label = freq >= 1000 ? `${freq/1000}K` : freq.toString()
      ctx.fillText(label, graphLeft - 5, y + 4)
    }
  }
  
  // Time axis (bottom)
  ctx.textAlign = 'center'
  const timeLabels = ['Inicio', '50%', 'Fin']
  ctx.fillText('Tiempo →', width / 2 + 20, height - 5)
  
  // Frequency label (rotated)
  ctx.save()
  ctx.translate(10, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.fillText('Frecuencia', 0, 0)
  ctx.restore()
  
  // Title
  ctx.fillStyle = textColor
  ctx.font = 'bold 12px Nunito'
  ctx.textAlign = 'left'
  ctx.fillText('Espectrograma (frecuencia vs tiempo)', graphLeft, 12)
  
  // Legend
  ctx.font = '9px Nunito'
  ctx.textAlign = 'left'
  ctx.fillText('🔵 Bajo', width - 80, 15)
  ctx.fillText('🟢 Medio', width - 80, 28)
  ctx.fillText('🔴 Alto', width - 80, 41)
}

function getColor(value) {
  if (value < 0.25) {
    const t = value / 0.25
    return `rgb(0, ${Math.round(t * 255)}, ${Math.round(255 - t * 100)})`
  } else if (value < 0.5) {
    const t = (value - 0.25) / 0.25
    return `rgb(0, ${Math.round(255 - t * 100)}, ${Math.round(155 + t * 100)})`
  } else if (value < 0.75) {
    const t = (value - 0.5) / 0.25
    return `rgb(${Math.round(t * 255)}, ${Math.round(155 + t * 100)}, 0)`
  } else {
    const t = (value - 0.75) / 0.25
    return `rgb(255, ${Math.round(255 - t * 200)}, 0)`
  }
}

function getSpectrogramColor(value) {
  return getColor(value)
}

onMounted(async () => {
  if (!libraryStore.songs || libraryStore.songs.length === 0) {
    await libraryStore.fetchSongs()
  }
  
  // Check if songId is provided in route query
  const songId = route.query.songId
  if (songId) {
    selectedSongId.value = songId
    const song = songs.value.find(s => s.id === songId)
    if (song) {
      selectedSongTitle.value = `${song.title} - ${song.artist}`
      if (song.has_fft) {
        await loadFFTData(songId)
      } else {
        // Wait for FFT analysis to complete (poll backend)
        isAnalyzingFFT.value = true
        waitForFFT(songId).catch(err => {
          console.error('[FFTView] Failed to wait for FFT:', err)
          isAnalyzingFFT.value = false
        })
      }
    }
  }
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
    console.log('[FFTView] Cleaned up poll interval')
  }
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
    console.log('[FFTView] Cleaned up poll interval')
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

/* Song List Section */
.song-list-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
  margin-bottom: 16px;
}

.song-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.song-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.song-item:hover {
  border-color: var(--accent-light);
  transform: translateX(4px);
  box-shadow: var(--shadow);
}

.song-item.active {
  border-color: var(--accent);
  background: var(--bg-tertiary);
}

.song-status {
  flex-shrink: 0;
}

.status-done {
  color: var(--success);
}

.status-pending {
  color: var(--warning);
}

.song-info {
  flex: 1;
}

.song-title {
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
  margin-bottom: 2px;
}

.song-artist {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.song-actions {
  flex-shrink: 0;
}

.btn-analyze-single {
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.btn-analyze-single:hover:not(:disabled) {
  transform: scale(1.1);
}

.fft-badge {
  background: var(--success);
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Results Section */
.results-section {
  animation: fadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

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

.stats-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-box {
  background: var(--bg-secondary);
  padding: 15px 25px;
  border-radius: var(--radius);
  text-align: center;
  border: 2px solid var(--border);
  min-width: 140px;
}

.stat-label {
  display: block;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-family: 'Nunito', sans-serif;
}

.stat-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
}

.canvas-container {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
  border: 2px solid var(--border);
  padding: 16px;
}

.canvas-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
  margin-bottom: 12px;
}

.canvas-container canvas {
  width: 100%;
  height: 300px;
  display: block;
  border-radius: 12px;
}

.canvas-container.spectrogram canvas {
  height: 200px;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.info-card {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--radius);
  text-align: center;
  border: 2px solid var(--border);
  transition: all var(--transition-fast);
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.card-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.info-card h4 {
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
}

.info-card.bass h4 { color: var(--accent); }
.info-card.mid h4 { color: var(--secondary); }
.info-card.treble h4 { color: var(--blue-accent); }

.info-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
}

.info-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
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
