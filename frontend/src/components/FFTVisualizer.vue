<template>
  <div v-if="playerStore.showFFT && playerStore.isPlaying" class="fft-visualizer" ref="container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const container = ref(null)
const canvas = ref(null)
let animationId = null
let ctx = null

const BAR_COUNT = 64
const BAR_GAP = 2

onMounted(() => {
  if (canvas.value) {
    ctx = canvas.value.getContext('2d')
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
  }
})

onUnmounted(() => {
  stopAnimation()
  window.removeEventListener('resize', resizeCanvas)
})

function resizeCanvas() {
  if (container.value && canvas.value) {
    canvas.value.width = container.value.clientWidth
    canvas.value.height = container.value.clientHeight
  }
}

function startAnimation() {
  if (!playerStore.analyser || !ctx || !canvas.value) return
  
  const bufferLength = playerStore.analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  
  function draw() {
    if (!playerStore.showFFT || !playerStore.isPlaying) return
    
    animationId = requestAnimationFrame(draw)
    
    playerStore.analyser.getByteFrequencyData(dataArray)
    
    const width = canvas.value.width
    const height = canvas.value.height
    const barWidth = (width / BAR_COUNT) - BAR_GAP
    const barMaxHeight = height * 0.9
    
    ctx.clearRect(0, 0, width, height)
    
    for (let i = 0; i < BAR_COUNT; i++) {
      const dataIndex = Math.floor(i * bufferLength / BAR_COUNT)
      const value = dataArray[dataIndex]
      const barHeight = (value / 255) * barMaxHeight
      
      const x = i * (barWidth + BAR_GAP)
      const y = height - barHeight
      
      const gradient = ctx.createLinearGradient(x, height, x, y)
      gradient.addColorStop(0, '#1DB954')
      gradient.addColorStop(0.5, '#1ED760')
      gradient.addColorStop(1, '#FFFFFF')
      
      ctx.fillStyle = gradient
      ctx.fillRect(x, y, barWidth, barHeight)
    }
  }
  
  draw()
}

function stopAnimation() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
}

watch(() => playerStore.showFFT, (newVal) => {
  if (newVal && playerStore.isPlaying) {
    stopAnimation()
    startAnimation()
  } else {
    stopAnimation()
    if (ctx && canvas.value) {
      ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
    }
  }
})

watch(() => playerStore.isPlaying, (newVal) => {
  if (!newVal) {
    stopAnimation()
    if (ctx && canvas.value) {
      ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
    }
  } else if (playerStore.showFFT) {
    stopAnimation()
    startAnimation()
  }
})
</script>

<style scoped>
.fft-visualizer {
  position: fixed;
  bottom: 80px;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.3));
  padding: 10px 20px;
  z-index: 100;
}

.fft-visualizer canvas {
  width: 100%;
  height: 100%;
}
</style>