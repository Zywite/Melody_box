<template>
  <div class="playlists-view">
    <header class="page-header">
      <h1 class="text-3xl font-bold">Tus playlists</h1>
    </header>

    <div class="flex justify-end mt-6">
      <button @click="showCreateModal = true" class="btn-primary">
        <Plus :size="18" />
        Nueva playlist
      </button>
    </div>

    <div v-if="playlistsStore.playlists.length" class="playlist-grid mt-6">
      <PlaylistCard
        v-for="playlist in playlistsStore.playlists"
        :key="playlist.id"
        :playlist="playlist"
        @click="goToPlaylist(playlist.id)"
      />
    </div>

    <div v-else class="empty-state">
      <ListMusic :size="64" class="opacity-30" />
      <h3 class="text-xl font-semibold mt-4">Sin playlists</h3>
      <p class="text-[var(--text-secondary)]">Crea tu primera playlist</p>
      <button @click="showCreateModal = true" class="btn-primary mt-6">Crear playlist</button>
    </div>

    <CreatePlaylistModal v-if="showCreateModal" @close="showCreateModal = false" @created="onPlaylistCreated" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlaylistsStore } from '@/stores/playlists'
import PlaylistCard from '@/components/common/PlaylistCard.vue'
import CreatePlaylistModal from '@/components/common/CreatePlaylistModal.vue'
import { Plus, ListMusic } from 'lucide-vue-next'

const router = useRouter()
const playlistsStore = usePlaylistsStore()

const showCreateModal = ref(false)

onMounted(async () => {
  await playlistsStore.fetchPlaylists()
})

function goToPlaylist(id) {
  router.push(`/playlists/${id}`)
}

async function onPlaylistCreated() {
  showCreateModal.value = false
  await playlistsStore.fetchPlaylists()
}
</script>