<template>
  <div class="video-player-wrapper" :class="{ fullscreen: isFullscreen }">
    <video
      ref="videoRef"
      class="video-player"
      :src="videoSrc"
      @timeupdate="$emit('timeupdate', videoRef)"
      @loadedmetadata="$emit('loadedmetadata', videoRef)"
      @durationchange="$emit('durationchange', videoRef)"
      @canplay="$emit('canplay', videoRef)"
      @ended="$emit('ended')"
      @play="$emit('play')"
      @pause="$emit('pause')"
      @click.stop
    ></video>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  videoSrc: { type: String, default: '' },
  isFullscreen: { type: Boolean, default: false },
  volume: { type: Number, default: 1 },
})

const emit = defineEmits(['timeupdate', 'loadedmetadata', 'durationchange', 'canplay', 'ended', 'play', 'pause', 'mounted'])

const videoRef = ref(null)

onMounted(() => {
  if (videoRef.value) {
    videoRef.value.volume = props.volume
    emit('mounted', videoRef.value)
  }
})

defineExpose({ videoRef })
</script>

<style scoped>
.video-player-wrapper {
  background: var(--bg-tertiary);
  position: relative;
}

.video-player-wrapper.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  max-width: none;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.video-player {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: block;
  background: var(--bg-tertiary);
}

.fullscreen .video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
  aspect-ratio: auto;
}
</style>
