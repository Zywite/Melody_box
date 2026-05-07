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
import { useLibraryStore } from '@/stores/library'
import api from '@/composables/useApi'

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

async function analyzeSong() {
  if (!selectedSongId.value || isAnalyzing.value) return
  
  const song = songs.value.find(s => s.id === selectedSongId.value)
  if (!song) return
  
  isAnalyzing.value = true
  result.value = null
  
  try {
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'
    
    console.log('Song data:', song)
    
    let audioUrl = song.file || song.file_path || song.url || song.path
    
    if (!audioUrl) {
      throw new Error('La canción no tiene archivo de audio')
    }
    
    console.log('audioUrl antes:', audioUrl)
    
    if (!audioUrl.startsWith('http') && !audioUrl.startsWith('/')) {
      audioUrl = `${API_BASE_URL}${audioUrl}`
    } else if (audioUrl.startsWith('/')) {
      audioUrl = `${API_BASE_URL}${audioUrl}`
    }
    
    console.log('audioUrl después:', audioUrl)
    
    const response = await fetch(audioUrl)
    if (!response.ok) throw new Error('No se pudo cargar el audio')
    
    const arrayBuffer = await response.arrayBuffer()
    
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
    
    const channelData = audioBuffer.getChannelData(0)
    const sampleRate = audioBuffer.sampleRate
    const channels = audioBuffer.numberOfChannels
    const duration = audioBuffer.duration
    
    const offlineContext = new OfflineAudioContext(channels, sampleRate * duration, sampleRate)
    const source = offlineContext.createBufferSource()
    source.buffer = audioBuffer
    
    const fftSize = 2048
    const offlineAnalyser = offlineContext.createAnalyser()
    offlineAnalyser.fftSize = fftSize
    offlineAnalyser.fftSize = fftSize
    
    source.connect(offlineAnalyser)
    offlineAnalyser.connect(offlineContext.destination)
    source.start(0)
    
    const renderedBuffer = await offlineContext.startRendering()
    const renderedData = renderedBuffer.getChannelData(0)
    
    const hopSize = 512
    const numFrames = Math.floor((renderedData.length - fftSize) / hopSize)
    const bufferLength = fftSize / 2
    const blockSize = Math.floor(renderedData.length / bufferLength)
    
    const spectrogramData = []
    
    for (let frame = 0; frame < numFrames; frame++) {
      const frameData = new Float32Array(fftSize)
      const offset = frame * hopSize
      
      for (let i = 0; i < fftSize; i++) {
        if (offset + i < renderedData.length) {
          frameData[i] = renderedData[offset + i]
        }
      }
      
      const sums = new Float32Array(bufferLength)
      const specBlockSize = Math.floor(fftSize / bufferLength)
      
      for (let i = 0; i < bufferLength; i++) {
        let sum = 0
        const idx = i * specBlockSize
        for (let j = 0; j < specBlockSize && idx + j < fftSize; j++) {
          sum += Math.abs(frameData[idx + j])
        }
        sums[i] = sum / specBlockSize
      }
      
      const maxVal = Math.max(...sums)
      const framebins = new Uint8Array(bufferLength)
      for (let i = 0; i < bufferLength; i++) {
        framebins[i] = Math.round((sums[i] / maxVal) * 255)
      }
      
      spectrogramData.push(Array.from(framebins))
    }
    
    const fullFFT = spectrogramData.length > 0 ? new Uint8Array(spectrogramData[spectrogramData.length - 1]) : new Uint8Array(bufferLength)
    
    const avgSums = new Float32Array(bufferLength)
    for (let i = 0; i < bufferLength; i++) {
      const start = i * blockSize
      let sum = 0
      for (let j = 0; j < blockSize; j++) {
        if (start + j < renderedData.length) {
          sum += Math.abs(renderedData[start + j])
        }
      }
      avgSums[i] = sum / blockSize
    }
    
    const maxVal = Math.max(...avgSums)
    for (let i = 0; i < bufferLength; i++) {
      fullFFT[i] = (avgSums[i] / maxVal) * 255
    }
    
    const nyquist = sampleRate / 2
    const binWidth = nyquist / bufferLength
    
    const bassEnd = Math.floor(250 / binWidth)
    const midEnd = Math.floor(2000 / binWidth)
    
    let bassSum = 0, midSum = 0, trebleSum = 0
    
    for (let i = 0; i < bufferLength; i++) {
      const val = fullFFT[i] / 255
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
      bins: Array.from(fullFFT),
      spectrogram: spectrogramData,
      bassPower: (bassSum / bassEnd) * 100,
      midPower: (midSum / (midEnd - bassEnd)) * 100,
      treblePower: (trebleSum / (bufferLength - midEnd)) * 100
    }
    
    drawCanvas()
    drawSpectrogram()
    
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
  
  ctx.fillStyle = '#000'
  ctx.fillRect(0, 0, width, height)
  
  const bins = result.value.bins
  const BAR_COUNT = 64
  const barWidth = (width / BAR_COUNT) - 4
  const barMaxHeight = height * 0.85
  
  const step = Math.floor(bins.length / BAR_COUNT)
  
  for (let i = 0; i < BAR_COUNT; i++) {
    let sum = 0
    for (let j = 0; j < step; j++) {
      sum += bins[i * step + j]
    }
    const value = (sum / step) / 255
    const barHeight = value * barMaxHeight
    
    const x = i * (barWidth + 4)
    const y = height - barHeight
    
    let color
    if (i < BAR_COUNT / 3) {
      color = '#1DB954'
    } else if (i < 2 * BAR_COUNT / 3) {
      color = '#1ED760'
    } else {
      color = '#FFFFFF'
    }
    
    ctx.fillStyle = color
    ctx.fillRect(x, y, barWidth, barHeight)
  }
  
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
  
  ctx.fillStyle = '#000'
  ctx.fillRect(0, 0, width, height)
  
  const spectrogram = result.value.spectrogram
  const numFrames = spectrogram.length
  const numFreqBins = spectrogram[0].length
  
  const colsPerFrame = width / numFrames
  
  for (let frame = 0; frame < numFrames; frame++) {
    const x = frame * colsPerFrame
    const bins = spectrogram[frame]
    
    for (let bin = 0; bin < numFreqBins; bin++) {
      const value = bins[bin] / 255
      const y = (bin / numFreqBins) * height
      
      const binHeight = (height / numFreqBins)
      
      const r = Math.round(value * 255)
      const g = Math.round(value * 255)
      const b = Math.round(value * 255)
      
      ctx.fillStyle = `rgb(${r},${g},${b})`
      ctx.fillRect(x, height - y - binHeight, Math.ceil(colsPerFrame), binHeight)
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
})
</script>

<style scoped>
.fft-analyzer {
  min-height: 100vh;
  background: #121212;
  color: #fff;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 2rem;
  margin-bottom: 10px;
}

.subtitle {
  color: #b3b3b3;
}

.song-selector {
  background: #1a1a1a;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.song-selector h3 {
  margin-bottom: 15px;
  color: #1DB954;
}

.selector-row {
  display: flex;
  gap: 10px;
}

.song-select {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: #282828;
  color: #fff;
  font-size: 1rem;
}

.song-select option {
  background: #282828;
}

.btn-analyze {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  background: #1DB954;
  color: #000;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-analyze:hover:not(:disabled) {
  background: #1ed760;
}

.btn-analyze:disabled {
  background: #555;
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
  background: #1a1a1a;
  padding: 15px 25px;
  border-radius: 12px;
  text-align: center;
}

.stat-label {
  display: block;
  color: #b3b3b3;
  font-size: 0.8rem;
}

.stat-value {
  display: block;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1DB954;
}

.canvas-container {
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
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
  color: #1DB954;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.info-card {
  background: #1a1a1a;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.info-card h4 {
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.info-card.bass h4 { color: #1DB954; }
.info-card.mid h4 { color: #1ED760; }
.info-card.treble h4 { color: #fff; }

.info-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.info-desc {
  font-size: 0.8rem;
  color: #b3b3b3;
}

.placeholder {
  text-align: center;
  padding: 60px;
  color: #b3b3b3;
}
</style>