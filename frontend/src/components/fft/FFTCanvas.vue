<template>
  <div class="results-section">
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
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { formatTime } from '@/utils/format'
import { readThemeColors, drawSpectrumCanvas, drawSpectrogramCanvas } from '@/utils/fftCanvas'

const props = defineProps({
  result: { type: Object, required: true },
})

const canvas = ref(null)
const specCanvas = ref(null)

async function redrawCanvases() {
  const themeColors = readThemeColors()
  drawSpectrumCanvas(canvas.value, props.result, themeColors)
  drawSpectrogramCanvas(specCanvas.value, props.result, themeColors)
}

watch(() => props.result, () => {
  nextTick(redrawCanvases)
}, { immediate: true })
</script>

<style scoped>
.results-section {
  animation: fadeIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
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

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .info-cards {
    grid-template-columns: 1fr;
  }
}
</style>
