<template>
  <div class="player-info">
    <template v-if="song">
      <div class="track-artwork">
        <img v-if="song.cover_url" :src="song.cover_url" :alt="song.title" />
        <div v-else class="artwork-placeholder">
          <Music2 :size="20" />
        </div>
        <div class="artwork-glow"></div>
      </div>
      <div class="track-meta">
        <p class="track-title">{{ song.title }}</p>
        <p class="track-artist">{{ song.artist }}</p>
      </div>
      <button @click="$emit('toggle-favorite')" class="track-favorite" :class="{ active: isFavorite }">
        <Heart :size="18" :fill="isFavorite ? 'currentColor' : 'none'" />
      </button>
    </template>
    <template v-else>
      <div class="no-track">
        <p class="text-sm">Sin reproducir</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { Heart, Music2 } from 'lucide-vue-next'

defineProps({
  song: { type: Object, default: null },
  isFavorite: { type: Boolean, default: false },
})

defineEmits(['toggle-favorite'])
</script>

<style scoped>
.player-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.track-artwork {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 16px;
  overflow: visible;
  flex-shrink: 0;
}

.track-artwork img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
  border: 2px solid var(--border);
}

.artwork-placeholder {
  width: 100%;
  height: 100%;
  background: var(--bg-tertiary);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  border: 2px solid var(--border);
}

.artwork-glow {
  position: absolute;
  inset: -6px;
  border-radius: 20px;
  background: var(--accent-glow);
  filter: blur(15px);
  opacity: 0;
  transition: opacity var(--transition);
}

.track-meta {
  min-width: 0;
  flex: 1;
}

.track-title {
  font-weight: 500;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
}

.track-artist {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-favorite {
  padding: 8px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.track-favorite:hover {
  color: var(--text-primary);
}

.track-favorite.active {
  color: var(--accent);
}

.no-track {
  color: var(--text-muted);
}
</style>
