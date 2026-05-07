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
  bottom:0;
  left:0;
  right:0;
  background: rgba(255, 245, 247, 0.95);
  backdrop-filter: blur(20px);
  border-top:2px solid var(--border);
  padding:12px 8px 24px;
  justify-content: space-around;
  z-index:100;
  box-shadow:0 -10px 40px rgba(255, 158, 187, 0.15);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap:6px;
  padding:10px 18px;
  border-radius: 18px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size:0.75rem;
  background: transparent;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: 'Nunito', sans-serif;
  font-weight:600;
}

.mobile-nav-item:hover {
  color: var(--accent);
  background: rgba(255, 158, 187, 0.15);
  border-color: var(--accent-light);
  transform: translateY(-2px);
}

.mobile-nav-item.active {
  color: white;
  background: var(--accent-gradient);
  box-shadow:0 4px 15px var(--accent-glow);
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