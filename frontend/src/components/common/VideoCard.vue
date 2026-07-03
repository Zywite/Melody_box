<template>
  <div
    class="video-card"
    :class="{ selected }"
    @click="$emit('select')"
  >
    <div class="video-thumbnail">
      <img :src="video.thumbnail" :alt="video.title" loading="lazy" />
      <span class="video-duration">{{ formatTime(video.duration) }}</span>
      <div class="video-play-overlay">
        <Play :size="24" fill="white" />
      </div>
    </div>
    <div class="video-info">
      <p class="video-title">{{ video.title }}</p>
      <p class="video-channel">{{ video.channel }}</p>
      <div class="video-meta">
        <span v-if="video.views">{{ formatViews(video.views) }} vistas</span>
        <span v-if="video.upload_date">• {{ video.upload_date }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatTime } from '@/utils/format'
import { Play } from 'lucide-vue-next'

const props = defineProps({
  video: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

defineEmits(['select'])

function formatViews(views) {
  if (!views) return ''
  if (views >= 1000000) return (views / 1000000).toFixed(1) + 'M'
  if (views >= 1000) return (views / 1000).toFixed(1) + 'K'
  return views.toString()
}
</script>

<style scoped>
.video-card {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  background: var(--bg-secondary);
  border: 2px solid transparent;
}

.video-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-4px);
}

.video-card.selected {
  border-color: var(--accent-primary);
}

.video-thumbnail {
  position: relative;
  aspect-ratio: 16/9;
  background: var(--bg-tertiary);
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
}

.video-play-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.video-card:hover .video-play-overlay {
  opacity: 1;
}

.video-info {
  padding: 12px;
}

.video-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-channel {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.video-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
  display: flex;
  gap: 8px;
}
</style>
