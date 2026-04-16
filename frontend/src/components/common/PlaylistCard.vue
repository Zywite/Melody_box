<template>
  <div class="playlist-card" @click="emit('click', playlist)">
    <div class="playlist-cover">
      <img v-if="playlist.cover_url" :src="playlist.cover_url" alt="" class="cover-img" />
      <div v-else class="cover-icon">
        <ListMusic :size="40" />
      </div>
      <div class="play-overlay">
        <Play :size="24" fill="white" />
      </div>
    </div>
    <div class="playlist-info">
      <p class="playlist-name">{{ playlist.name }}</p>
      <p class="playlist-count">{{ playlist.songs?.length || 0 }} canciones</p>
    </div>
  </div>
</template>

<script setup>
import { ListMusic, Play } from 'lucide-vue-next'

defineProps({
  playlist: { type: Object, required: true }
})

const emit = defineEmits(['click'])
</script>

<style scoped>
.playlist-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--bg-secondary);
}

.playlist-card:hover {
  background: rgba(225, 29, 72, 0.1);
  transform: translateY(-4px);
}

.playlist-card:hover .play-overlay {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.playlist-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  background: linear-gradient(135deg, #e11d48 0%, #7c3aed 100%);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-icon {
  color: white;
  opacity: 0.8;
}

.play-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.8);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(225, 29, 72, 0.4);
}

.playlist-info {
  margin-top: 14px;
}

.playlist-name {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'DM Sans', sans-serif;
}

.playlist-count {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 4px;
  font-family: 'DM Sans', sans-serif;
}
</style>