<template>
  <div class="playlist-card" @click="emit('click', playlist)">
    <div class="playlist-cover">
      <img v-if="playlist.cover_url" :src="playlist.cover_url" alt="" class="cover-img" loading="lazy" />
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
  padding: 18px;
  border-radius: 24px;
  cursor: pointer;
  transition: all var(--transition);
  background: var(--bg-secondary);
  border: 2px solid var(--border);
}

.playlist-card:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-light);
  transform: translateY(-6px) scale(1.03);
  box-shadow: var(--shadow);
}

.playlist-card:hover .play-overlay {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.playlist-cover {
  position: relative;
  width:100%;
  aspect-ratio:1;
  border-radius: 18px;
  background: var(--accent-gradient);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px var(--accent-glow);
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
  top:50%;
  left:50%;
  transform: translate(-50%, -50%) scale(0.8);
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity:0;
  transition: all var(--transition);
  box-shadow: 0 8px 30px var(--accent-glow);
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
  font-family: 'Nunito', sans-serif;
  margin-top: 14px;
}

.playlist-count {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 4px;
  font-family: 'Nunito', sans-serif;
}
</style>