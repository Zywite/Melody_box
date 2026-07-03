<template>
  <div>
    <div v-if="favorites.length" class="song-list mt-4">
      <SongCard
        v-for="song in favorites"
        :key="song.id"
        v-memo="[song.id]"
        :song="song"
        :show-artist="true"
        :is-favorite="true"
        @play="$emit('play', song)"
        @toggle-favorite="$emit('toggle-favorite', song)"
      />
    </div>
    <div v-else class="empty-state">
      <Heart :size="48" class="opacity-30" />
      <h3 class="text-xl font-semibold mt-4">Sin favoritos</h3>
      <p class="text-[var(--text-secondary)]">Marca canciones como favoritas</p>
    </div>
  </div>
</template>

<script setup>
import SongCard from '@/components/common/SongCard.vue'
import { Heart } from 'lucide-vue-next'

defineProps({
  favorites: { type: Array, default: () => [] },
})

defineEmits(['play', 'toggle-favorite'])
</script>

<style scoped>
.song-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}
</style>
