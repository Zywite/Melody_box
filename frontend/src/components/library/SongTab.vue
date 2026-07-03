<template>
  <div>
    <div class="filter-row">
      <button 
        :class="['filter-btn', { active: songFilter === 'all' }]"
        @click="songFilter = 'all'"
      >
        Todo
      </button>
      <button 
        :class="['filter-btn', { active: songFilter === 'audio' }]"
        @click="songFilter = 'audio'"
      >
        <Music :size="16" />
        Audio
      </button>
      <button 
        :class="['filter-btn', { active: songFilter === 'video' }]"
        @click="songFilter = 'video'"
      >
        <Video :size="16" />
        Video
      </button>
    </div>

    <div v-if="filteredSongs.length" class="song-list-container mt-4">
      <VirtualList
        :items="filteredSongs"
        :item-height="84"
        :key-field="'id'"
      >
        <template #default="{ item: song, index }">
          <SongCard
            :key="song.id"
            :song="song"
            :show-artist="true"
            :is-favorite="isSongFavorite(song.id)"
            @play="$emit('play', song)"
            @add-to-playlist="$emit('add-to-playlist', song)"
            @toggle-favorite="$emit('toggle-favorite', song)"
          />
        </template>
      </VirtualList>
    </div>

    <div v-if="hasMoreSongs && !isLoading" class="load-more-container">
      <button @click="$emit('load-more')" class="load-more-btn">
        <Plus :size="18" />
        Cargar más
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <div v-if="!filteredSongs.length && !isLoading" class="empty-state">
      <Music :size="48" class="opacity-30" />
      <h3 class="text-xl font-semibold mt-4">Sin canciones</h3>
      <p class="text-[var(--text-secondary)]">Sube tu primera canción</p>
      <router-link to="/upload" class="btn-primary mt-4">Subir música</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSongsStore } from '@/stores/songs'
import { useFavorite } from '@/composables/useFavorite'
import SongCard from '@/components/common/SongCard.vue'
import VirtualList from '@/components/common/VirtualList.vue'
import { Music, Video, Plus } from 'lucide-vue-next'

defineEmits(['play', 'add-to-playlist', 'toggle-favorite', 'load-more'])

const props = defineProps({
  hasMoreSongs: { type: Boolean, default: false },
  isLoading: { type: Boolean, default: false },
})

const songsStore = useSongsStore()
const { isSongFavorite } = useFavorite()

const songFilter = ref('all')

const filteredSongs = computed(() => {
  if (songFilter.value === 'all') {
    return songsStore.songs
  }
  return songsStore.songs.filter(song => song.media_type === songFilter.value)
})
</script>

<style scoped>
.filter-row {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.filter-btn {
  padding: 8px 20px;
  border-radius: 14px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-secondary);
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-btn:hover {
  border-color: var(--accent-light);
  color: var(--text-primary);
  transform: scale(1.03);
}

.filter-btn.active {
  background: var(--accent-gradient);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px var(--accent-glow);
}

.song-list-container {
  height: calc(100vh - 320px);
  min-height: 200px;
  border-radius: 16px;
  overflow: hidden;
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.load-more-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: 20px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-primary);
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition);
}

.load-more-btn:hover {
  border-color: var(--accent);
  transform: scale(1.05);
  box-shadow: var(--shadow);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--bg-tertiary);
  border-top: 3px solid var(--accent);
  border-radius: 50%;
  animation: spin-slow 1s linear infinite;
}
</style>
