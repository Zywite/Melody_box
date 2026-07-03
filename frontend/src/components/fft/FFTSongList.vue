<template>
  <section class="song-list-section">
    <h2 class="section-title">Canciones</h2>

    <VirtualList
      v-if="songs.length"
      class="song-list"
      :items="songs"
      :item-height="60"
      :key-field="'id'"
    >
      <template #default="{ item: song }">
        <div
          @click="$emit('select-song', song)"
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
              @click.stop="$emit('analyze-song', song)"
              :disabled="isAnalyzing"
              class="btn-analyze-single"
            >
              {{ analyzingSongId === song.id ? '...' : '🔍' }}
            </button>
            <span v-else class="fft-badge">FFT ✓</span>
          </div>
        </div>
      </template>
    </VirtualList>
  </section>
</template>

<script setup>
import { CheckCircle, Clock } from 'lucide-vue-next'
import VirtualList from '@/components/common/VirtualList.vue'

defineProps({
  songs: { type: Array, required: true },
  selectedSongId: { type: String, default: '' },
  isAnalyzing: { type: Boolean, default: false },
  analyzingSongId: { type: String, default: null },
})

defineEmits(['select-song', 'analyze-song'])
</script>

<style scoped>
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
  height: 60vh;
  min-height: 400px;
}

.song-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 18px;
  height: 100%;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-sizing: border-box;
  margin-bottom: 8px;
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
</style>
