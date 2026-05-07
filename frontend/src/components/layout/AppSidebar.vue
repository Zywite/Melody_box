<template>
  <aside class="app-sidebar">
    <div class="sidebar-header">
      <router-link to="/home" class="logo-link">
        <div class="logo-icon">
          <Music2 :size="24" />
        </div>
        <span class="logo-text">MelodyBox</span>
      </router-link>
    </div>

    <nav class="sidebar-nav">
      <router-link to="/home" class="nav-item" :class="{ active: $route.path === '/home' }">
        <Home :size="20" />
        <span>Inicio</span>
      </router-link>
      <router-link to="/search" class="nav-item" :class="{ active: $route.path === '/search' }">
        <Search :size="20" />
        <span>Buscar</span>
      </router-link>
      <router-link to="/library" class="nav-item" :class="{ active: $route.path === '/library' }">
        <Library :size="20" />
        <span>Biblioteca</span>
      </router-link>
      <router-link to="/playlists" class="nav-item" :class="{ active: $route.path.startsWith('/playlists') }">
        <ListMusic :size="20" />
        <span>Playlists</span>
      </router-link>
      <router-link to="/upload" class="nav-item" :class="{ active: $route.path === '/upload' }">
        <Upload :size="20" />
        <span>Subir</span>
      </router-link>
      <router-link to="/fft" class="nav-item" :class="{ active: $route.path === '/fft' }">
        <Activity :size="20" />
        <span>FFT Audio</span>
      </router-link>
    </nav>

    <div class="sidebar-playlists" v-if="playlists.length">
      <p class="section-title">Tus Playlists</p>
      <div class="playlist-list">
        <router-link 
          v-for="playlist in playlists.slice(0, 5)" 
          :key="playlist.id" 
          :to="`/playlists/${playlist.id}`"
          class="playlist-link"
        >
          {{ playlist.name }}
        </router-link>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          {{ authStore.username?.charAt(0).toUpperCase() }}
        </div>
        <div class="user-details">
          <p class="user-name">{{ authStore.username }}</p>
        </div>
      </div>
      <ThemeToggle />
      <button @click="handleLogout" class="logout-btn" title="Cerrar sesión">
        <LogOut :size="18" />
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/composables/useApi'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import { Music2, Home, Search, Library, ListMusic, Upload, LogOut, Activity } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const playlists = ref([])

async function loadPlaylists() {
  try {
    const data = await api.getPlaylists()
    playlists.value = data || []
  } catch (e) {
    console.error('Failed to load playlists', e)
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}

onMounted(loadPlaylists)
</script>

<style scoped>
.app-sidebar {
  width: 260px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: 2px solid var(--border);
}

.sidebar-header {
  padding: 24px 20px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.logo-text {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.sidebar-nav {
  flex: 1;
  padding: 8px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 16px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition);
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
}

.nav-item:hover {
  background: rgba(255, 158, 187, 0.15);
  color: var(--text-primary);
  transform: scale(1.02);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(255, 183, 197, 0.25) 0%, rgba(177, 156, 217, 0.25) 100%);
  color: var(--accent-primary);
  box-shadow: 0 2px 10px var(--accent-glow);
}

.sidebar-playlists {
  padding: 16px 20px;
  border-top: 2px solid var(--border);
}

.section-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
}

.playlist-link {
  padding: 8px 12px;
  border-radius: 10px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Nunito', sans-serif;
}

.playlist-link:hover {
  background: rgba(255, 158, 187, 0.15);
  color: var(--text-primary);
  transform: translateX(4px);
}

.section-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-family: 'DM Sans', sans-serif;
}

.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.playlist-link {
  padding: 8px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.playlist-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 2px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-family: 'Nunito', sans-serif;
  box-shadow: 0 2px 10px var(--accent-glow);
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
}

.logout-btn {
  padding: 10px;
  border-radius: 12px;
  background: transparent;
  border: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  background: rgba(255, 158, 187, 0.15);
  color: var(--accent);
  border-color: var(--accent-light);
  transform: scale(1.05);
}

@media (max-width: 768px) {
  .app-sidebar {
    display: none;
  }
}
</style>