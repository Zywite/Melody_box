<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">Tus playlists</h2>
      <button @click="$emit('create')" class="btn-new-playlist">
        <Plus :size="16" />
        <span>Crear</span>
      </button>
    </div>

    <div v-if="playlists.length" class="playlist-list">
      <div
        v-for="playlist in playlists"
        :key="playlist.id"
        class="playlist-item"
        @click="$emit('go-to-playlist', playlist.id)"
      >
        <div class="playlist-cover">
          <ListMusic :size="24" />
        </div>
        <div class="playlist-info">
          <p class="playlist-name">{{ playlist.name }}</p>
          <p class="playlist-meta">{{ playlist.songs?.length || 0 }} canciones</p>
        </div>
        <button class="playlist-menu-btn" @click.stop>
          <MoreHorizontal :size="18" />
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-icon">
        <ListMusic :size="48" />
      </div>
      <h3 class="text-xl font-semibold">Sin playlists</h3>
      <p class="text-[var(--text-secondary)]">Crea tu primera playlist</p>
      <button @click="$emit('create')" class="btn-primary mt-4">Crear playlist</button>
    </div>
  </div>
</template>

<script setup>
import { Plus, ListMusic, MoreHorizontal } from 'lucide-vue-next'

defineProps({
  playlists: { type: Array, default: () => [] },
})

defineEmits(['create', 'go-to-playlist'])
</script>

<style scoped>
.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: 16px;
  cursor: pointer;
  transition: all var(--transition);
}

.playlist-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.playlist-cover {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.playlist-info {
  flex: 1;
  min-width: 0;
}

.playlist-name {
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.playlist-meta {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.playlist-menu-btn {
  padding: 8px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.playlist-menu-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.btn-new-playlist {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 16px;
  background: var(--accent-gradient);
  border: none;
  color: white;
  font-weight: 600;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 4px 15px var(--accent-glow);
}

.btn-new-playlist:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px var(--accent-glow);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-icon {
  color: var(--accent-light);
}
</style>
