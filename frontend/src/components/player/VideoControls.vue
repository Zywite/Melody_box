<template>
  <div class="video-controls">
    <div class="progress-container" @click="handleSeek">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>

    <div class="controls-row">
      <div class="time-display">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</div>

      <div class="control-buttons">
        <button @click="$emit('play-prev')" class="control-btn" title="Anterior">
          <SkipBack :size="20" />
        </button>
        <button @click="$emit('toggle-play')" class="control-btn play-btn" :title="isPlaying ? 'Pausar' : 'Reproducir'">
          <Pause v-if="isPlaying" :size="24" fill="currentColor" />
          <Play v-else :size="24" fill="currentColor" />
        </button>
        <button @click="$emit('play-next')" class="control-btn" title="Siguiente">
          <SkipForward :size="20" />
        </button>
      </div>

      <div class="volume-control">
        <button @click="$emit('toggle-mute')" class="control-btn">
          <VolumeX v-if="isMuted" :size="18" />
          <Volume2 v-else :size="18" />
        </button>
        <input
          type="range"
          min="0"
          max="100"
          :value="volume * 100"
          @input="onVolumeInput"
          class="volume-slider"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatTime } from '@/utils/format'
import { SkipBack, Play, Pause, SkipForward, VolumeX, Volume2 } from 'lucide-vue-next'

const props = defineProps({
  progress: { type: Number, default: 0 },
  currentTime: { type: Number, default: 0 },
  duration: { type: Number, default: 0 },
  isPlaying: { type: Boolean, default: false },
  volume: { type: Number, default: 1 },
  isMuted: { type: Boolean, default: false },
})

const emit = defineEmits(['seek', 'toggle-play', 'play-next', 'play-prev', 'volume', 'toggle-mute'])

function handleSeek(event) {
  if (props.duration) {
    const rect = event.currentTarget.getBoundingClientRect()
    const percent = ((event.clientX - rect.left) / rect.width) * 100
    emit('seek', (percent / 100) * props.duration)
  }
}

function onVolumeInput(event) {
  const val = parseInt(event.target.value) / 100
  emit('volume', val)
}
</script>

<style scoped>
.video-controls {
  padding:16px 24px 20px;
  background: linear-gradient(0deg, rgba(255, 245, 247, 0.6) 0%, transparent 100%);
}

.progress-container {
  margin-bottom:16px;
}

.progress-bar {
  height:8px;
  background: var(--bg-tertiary);
  border-radius:var(--radius-full);
  cursor: pointer;
  overflow: hidden;
  transition: height var(--transition-fast);
}

.progress-bar:hover {
  height:10px;
}

.progress-fill {
  height:100%;
  background: var(--accent-gradient);
  background-size:200% 200%;
  border-radius:var(--radius-full);
  transition: width 0.1s linear;
}

.controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.time-display {
  font-size:0.85rem;
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
  min-width:90px;
  font-family: 'JetBrains Mono', monospace;
}

.control-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding:10px;
  border-radius:50%;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  color: var(--accent);
  transform: scale(1.1);
}

.play-btn {
  width:60px;
  height:60px;
  background: var(--accent-gradient);
  color: white;
  box-shadow:0 8px 24px var(--accent-glow);
}

.play-btn:hover {
  transform: scale(1.1);
  box-shadow:0 12px 32px var(--accent-glow);
}

.control-buttons {
  display: flex;
  align-items: center;
  gap: 20px;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 140px;
}

.volume-slider {
  width:100px;
  height:6px;
  -webkit-appearance: none;
  background: var(--bg-tertiary);
  border-radius:var(--radius-full);
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width:16px;
  height:16px;
  background: var(--accent-gradient);
  border-radius:50%;
  cursor: pointer;
  box-shadow:0 2px 8px var(--accent-glow);
  border:2px solid white;
}

@media (max-width: 768px) {
  .volume-control {
    display: none;
  }
}
</style>
