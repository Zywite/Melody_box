<template>
  <div class="fft-analyzer">
    <div class="header">
      <h1>Análisis de Audio FFT</h1>
      <p class="subtitle">Análisis de frecuencias de audio</p>
    </div>
    
    <div class="song-selector">
      <h3>Seleccionar Canción</h3>
      <div class="selector-row">
        <select v-model="selectedSongId" class="song-select">
          <option value="">-- Selecciona una canción --</option>
          <option v-for="song in songs" :key="song.id" :value="song.id">
            {{ song.title }} - {{ song.artist }}
          </option>
        </select>
        <button @click="analyzeSong" :disabled="!selectedSongId || isAnalyzing" class="btn-analyze">
          {{ isAnalyzing ? 'Analizando...' : '🔍 Analizar' }}
        </button>
      </div>
    </div>
    
    <div v-if="result" class="results">
      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-label">Duración</span>
          <span class="stat-value">{{ formatTime(result.duration) }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">Sample Rate</span>
          <span class="stat-value">{{ result.sampleRate }} Hz</span>
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
        <canvas ref="canvas"></canvas>
      </div>
      
      <h3 class="section-title">Espectrograma</h3>
      <div class="canvas-container spectrogram">
        <canvas ref="specCanvas"></canvas>
      </div>
      
      <div class="info-cards">
        <div class="info-card bass">
          <h4>Graves (20-250 Hz)</h4>
          <p class="info-value">{{ result.bassPower.toFixed(1) }}%</p>
          <p class="info-desc">Bajos, bombo, bajo eléctrico</p>
        </div>
        <div class="info-card mid">
          <h4>Medios (250-2k Hz)</h4>
          <p class="info-value">{{ result.midPower.toFixed(1) }}%</p>
          <p class="info-desc">Voces,guitarras,sintetizadores</p>
        </div>
        <div class="info-card treble">
          <h4>Agudos (2k-20k Hz)</h4>
          <p class="info-value">{{ result.treblePower.toFixed(1) }}%</p>
          <p class="info-desc">Brillantes, platillos, aire</p>
        </div>
      </div>
    </div>
    
    <div v-else class="placeholder">
      <p>Selecciona una canción y presiona "Analizar" para ver el espectro de frecuencias</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLibraryStore } from '@/stores/library'
import api from '@/composables/useApi'

const route = useRoute()
const libraryStore = useLibraryStore()

const selectedSongId = ref('')
const isAnalyzing = ref(false)
const result = ref(null)
const canvas = ref(null)
const specCanvas = ref(null)

const songs = computed(() => libraryStore.songs || [])

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function analyzeSong(songId) {
  const id = songId || selectedSongId.value
  if (!id || isAnalyzing.value) return
  
  const song = songs.value.find(s => s.id === id)
  if (!song) return
  
  isAnalyzing.value = true
  result.value = null
  
  try {
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'
    
    let audioUrl = song.file || song.file_path || song.url || song.path
    
    if (!audioUrl) {
      throw new Error('La canción no tiene archivo de audio')
    }
    
    if (!audioUrl.startsWith('http') && !audioUrl.startsWith('/')) {
      audioUrl = `${API_BASE_URL}${audioUrl}`
    } else if (audioUrl.startsWith('/')) {
      audioUrl = `${API_BASE_URL}${audioUrl}`
    }
    
    const response = await fetch(audioUrl)
    if (!response.ok) throw new Error('No se pudo cargar el audio')
    
    const arrayBuffer = await response.arrayBuffer()
    
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
    
    const sampleRate = audioBuffer.sampleRate
    const channels = audioBuffer.numberOfChannels
    const duration = audioBuffer.duration
    
    // Use OfflineAudioContext with AnalyserNode for real FFT
    const offlineContext = new OfflineAudioContext(1, audioBuffer.length, sampleRate)
    const source = offlineContext.createBufferSource()
    source.buffer = audioBuffer
    
    const fftSize = 2048
    const offlineAnalyser = offlineContext.createAnalyser()
    offlineAnalyser.fftSize = fftSize
    offlineAnalyser.smoothingTimeConstant = 0
    
    source.connect(offlineAnalyser)
    offlineAnalyser.connect(offlineContext.destination)
    source.start(0)
    
    const bufferLength = offlineAnalyser.frequencyBinCount
    const hopSize = 512
    const numFrames = Math.floor(audioBuffer.length / hopSize)
    
    const spectrogramData = []
    const fullBins = new Float32Array(bufferLength)
    
    // Process each frame
    for (let frame = 0; frame < numFrames; frame++) {
      const frameOffset = frame * hopSize
      
      // Create a short buffer for this frame
      const frameLength = Math.min(hopSize, audioBuffer.length - frameOffset)
      const frameBuffer = offlineContext.createBuffer(1, frameLength, sampleRate)
      const frameData = frameBuffer.getChannelData(0)
      
      for (let i = 0; i < frameLength; i++) {
        frameData[i] = audioBuffer.getChannelData(0)[frameOffset + i] || 0
      }
      
      const frameSource = offlineContext.createBufferSource()
      frameSource.buffer = frameBuffer
      
      const frameAnalyser = offlineContext.createAnalyser()
      frameAnalyser.fftSize = fftSize
      frameAnalyser.smoothingTimeConstant = 0
      
      frameSource.connect(frameAnalyser)
      frameAnalyser.connect(offlineContext.destination)
      frameSource.start(0)
      
      const frameBins = new Uint8Array(bufferLength)
      frameAnalyser.getByteFrequencyData(frameBins)
      
      spectrogramData.push(Array.from(frameBins))
      
      // Accumulate for full FFT
      for (let i = 0; i < bufferLength; i++) {
        fullBins[i] += frameBins[i]
      }
    }
    
    // Average the full FFT
    for (let i = 0; i < bufferLength; i++) {
      fullBins[i] = Math.round(fullBins[i] / numFrames)
    }
    
    const nyquist = sampleRate / 2
    const binWidth = nyquist / bufferLength
    
    const bassEnd = Math.floor(250 / binWidth)
    const midEnd = Math.floor(2000 / binWidth)
    
    let bassSum = 0, midSum = 0, trebleSum = 0
    
    for (let i = 0; i < bufferLength; i++) {
      const val = fullBins[i] / 255
      if (i < bassEnd) {
        bassSum += val
      } else if (i < midEnd) {
        midSum += val
      } else {
        trebleSum += val
      }
    }
    
    result.value = {
      duration,
      sampleRate,
      channels,
      bins: Array.from(fullBins),
      spectrogram: spectrogramData,
      bassPower: bassEnd > 0 ? (bassSum / bassEnd) * 100 : 0,
      midPower: (midEnd - bassEnd) > 0 ? (midSum / (midEnd - bassEnd)) * 100 : 0,
      treblePower: (bufferLength - midEnd) > 0 ? (trebleSum / (bufferLength - midEnd)) * 100 : 0
    }
    
    drawCanvas()
    drawSpectrogram()
    
    audioContext.close()
  } catch (err) {
    console.error('Error analyzing:', err)
    alert('Error al analizar: ' + err.message)
  } finally {
    isAnalyzing.value = false
  }
}

function drawCanvas() {
  if (!result.value || !canvas.value) return
  
  const ctx = canvas.value.getContext('2d')
  const width = canvas.value.width = 800
  const height = canvas.value.height = 300
  
  // Get theme colors from CSS variables
  const style = getComputedStyle(document.documentElement)
  const bgColor = style.getPropertyValue('--bg-secondary').trim() || '#1a1a1a'
  const accentColor = style.getPropertyValue('--accent').trim() || '#ff9ebb'
  const accentLight = style.getPropertyValue('--accent-light').trim() || '#ffb7c5'
  const textColor = style.getPropertyValue('--text-primary').trim() || '#fefefe'
  
  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)
    
  const bins = result.value.bins
  const BAR_COUNT = 64
  const barWidth = (width / BAR_COUNT) - 4
  const barMaxHeight = height * 0.85
    
  const step = Math.max(1, Math.floor(bins.length / BAR_COUNT))
    
  for (let i = 0; i < BAR_COUNT; i++) {
    const binIndex = Math.min(i * step, bins.length - 1)
    const value = bins[binIndex] / 255
    const barHeight = value * barMaxHeight
      
    const x = i * (barWidth + 4)
    const y = height - barHeight
      
    // Create gradient based on frequency (bass=accent, mid=accentLight, treble=textColor)
    const gradient = ctx.createLinearGradient(x, height, x, y)
    if (i < BAR_COUNT / 3) {
      gradient.addColorStop(0, accentColor)
      gradient.addColorStop(1, accentLight)
    } else if (i < 2 * BAR_COUNT / 3) {
      gradient.addColorStop(0, accentLight)
      gradient.addColorStop(1, textColor)
    } else {
      gradient.addColorStop(0, textColor)
      gradient.addColorStop(1, accentColor)
    }
      
    ctx.fillStyle = gradient
    ctx.fillRect(x, y, barWidth, barHeight)
  }
    
  // Draw grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.1)'
  ctx.lineWidth = 1
  for (let i = 0; i <= 10; i++) {
    const y = (height / 10) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }
}

function drawSpectrogram() {
  if (!result.value || !specCanvas.value || !result.value.spectrogram) return
  
  const ctx = specCanvas.value.getContext('2d')
  const width = specCanvas.value.width = 800
  const height = specCanvas.value.height = 200
  
  // Get theme colors
  const style = getComputedStyle(document.documentElement)
  const bgColor = style.getPropertyValue('--bg-secondary').trim() || '#1a1a1a'
  
  ctx.fillStyle = bgColor
  ctx.fillRect(0, 0, width, height)
  
  const spectrogram = result.value.spectrogram
  const numFrames = spectrogram.length
  if (numFrames === 0) return
  
  const numFreqBins = spectrogram[0].length
  const colsPerFrame = width / numFrames
  
  // Color map function (rainbow: blue -> cyan -> green -> yellow -> red)
  function getColor(value) {
    // value is 0-1
    const v = Math.max(0, Math.min(1, value))
    let r, g, b
    
    if (v < 0.25) {
      // Blue to Cyan
      r = 0
      g = Math.round(v * 4 * 255)
      b = 255
    } else if (v < 0.5) {
      // Cyan to Green
      r = 0
      g = 255
      b = Math.round((1 - (v - 0.25) * 4) * 255)
    } else if (v < 0.75) {
      // Green to Yellow
      r = Math.round((v - 0.5) * 4 * 255)
      g = 255
      b = 0
    } else {
      // Yellow to Red
      r = 255
      g = Math.round((1 - (v - 0.75) * 4) * 255)
      b = 0
    }
    
    return `rgb(${r},${g},${b})`
  }
  
  for (let frame = 0; frame < numFrames; frame++) {
    const x = Math.floor(frame * colsPerFrame)
    const xNext = Math.floor((frame + 1) * colsPerFrame)
    const binWidth = Math.max(1, xNext - x)
    const bins = spectrogram[frame]
    
    for (let bin = 0; bin < numFreqBins; bin++) {
      const value = bins[bin] / 255
      const y = height - ((bin + 1) / numFreqBins) * height
      const binHeight = Math.max(1, height / numFreqBins)
      
      ctx.fillStyle = getColor(value)
      ctx.fillRect(x, y, binWidth, binHeight)
    }
  }
}

async function loadSongs() {
  if (!libraryStore.songs || libraryStore.songs.length === 0) {
    await libraryStore.fetchSongs()
  }
}

onMounted(async () => {
  await loadSongs()
  
  // Check if songId is provided in route query
  const songId = route.query.songId
  if (songId) {
    selectedSongId.value = songId
    // Auto-analyze after a short delay to ensure everything is loaded
    setTimeout(() => {
      analyzeSong(songId)
    }, 500)
  }
})
</script>

<style scoped>
.fft-analyzer {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 2rem;
  margin-bottom: 10px;
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.subtitle {
  color: var(--text-secondary);
}

.song-selector {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--radius);
  margin-bottom: 20px;
  border: 2px solid var(--border);
}

.song-selector h3 {
  margin-bottom: 15px;
  color: var(--accent);
}

.selector-row {
  display: flex;
  gap: 10px;
}

.song-select {
  flex: 1;
  padding: 12px;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-size: 1rem;
  font-family: 'Nunito', sans-serif;
}

.song-select option {
  background: var(--bg-tertiary);
}

.btn-analyze {
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: 'Nunito', sans-serif;
}

.btn-analyze:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: var(--shadow-glow);
}

.btn-analyze:disabled {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  cursor: not-allowed;
}

.results {
  margin-top: 20px;
}

.stats-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-box {
  background: var(--bg-secondary);
  padding: 15px 25px;
  border-radius: var(--radius);
  text-align: center;
  border: 2px solid var(--border);
}

.stat-label {
  display: block;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.stat-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--accent);
}

.canvas-container {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
  border: 2px solid var(--border);
}

.canvas-container canvas {
  width: 100%;
  height: 300px;
  display: block;
}

.canvas-container.spectrogram canvas {
  height: 200px;
}

.section-title {
  margin: 20px 0 10px;
  color: var(--accent);
  font-family: 'Nunito', sans-serif;
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
}

.info-card h4 {
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: var(--accent);
}

.info-card.bass h4 { color: var(--accent); }
.info-card.mid h4 { color: var(--secondary); }
.info-card.treble h4 { color: var(--blue-accent); }

.info-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
  color: var(--text-primary);
}

.info-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.placeholder {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}
</style>