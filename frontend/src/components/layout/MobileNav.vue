<template>
  <nav class="mobile-nav">
    <router-link to="/home" class="mobile-nav-item" :class="{ active: $route.path === '/home' }">
      <Home :size="22" />
      <span>Inicio</span>
    </router-link>
    <router-link to="/search" class="mobile-nav-item" :class="{ active: $route.path === '/search' }">
      <Search :size="22" />
      <span>Buscar</span>
    </router-link>
    <router-link to="/library" class="mobile-nav-item" :class="{ active: $route.path === '/library' }">
      <Library :size="22" />
      <span>Biblioteca</span>
    </router-link>
    <router-link to="/playlists" class="mobile-nav-item" :class="{ active: $route.path.startsWith('/playlists') }">
      <ListMusic :size="22" />
      <span>Playlists</span>
    </router-link>
    <button @click="openUpload" class="mobile-nav-item">
      <Upload :size="22" />
      <span>Subir</span>
    </button>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Home, Search, Library, ListMusic, Upload } from 'lucide-vue-next'

const router = useRouter()

function openUpload() {
  router.push('/upload')
}
</script>

<style scoped>
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(20, 20, 30, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 10px 8px 20px;
  justify-content: space-around;
  z-index: 100;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.3);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 16px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.7rem;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: 'DM Sans', sans-serif;
}

.mobile-nav-item:hover,
.mobile-nav-item.active {
  color: var(--accent-primary);
  background: rgba(225, 29, 72, 0.1);
}

@media (max-width: 768px) {
  .mobile-nav {
    display: flex;
  }
}
</style>