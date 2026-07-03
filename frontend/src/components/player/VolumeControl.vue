<template>
  <div class="volume-wrapper">
    <button @click="$emit('toggle-mute')" class="extra-btn">
      <VolumeX v-if="isMuted || volume === 0" :size="18" />
      <Volume2 v-else-if="volume > 0.5" :size="18" />
      <Volume1 v-else :size="18" />
    </button>
    <div class="volume-bar">
      <input
        type="range"
        min="0"
        max="100"
        :value="volume * 100"
        @input="$emit('update:volume', $event.target.value / 100)"
        class="volume-slider"
      />
    </div>
  </div>
</template>

<script setup>
import { VolumeX, Volume2, Volume1 } from 'lucide-vue-next'

defineProps({
  volume: { type: Number, default: 0 },
  isMuted: { type: Boolean, default: false },
})

defineEmits(['toggle-mute', 'update:volume'])
</script>

<style scoped>
.volume-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.extra-btn {
  padding: 8px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.extra-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.volume-bar {
  width: 80px;
}

.volume-slider {
  width: 100%;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-tertiary);
  border-radius: 2px;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: var(--text-primary);
  border-radius: 50%;
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.volume-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}
</style>
