<template>
  <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'">
    <div class="toggle-track" :class="{ dark: isDark }">
      <div class="toggle-thumb">
        <Sun v-if="!isDark" :size="14" class="icon sun" />
        <Moon v-else :size="14" class="icon moon" />
      </div>
    </div>
  </button>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'

const isDark = ref(false)

onMounted(() => {
  const savedTheme = localStorage.getItem('melodybox-theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  } else if (savedTheme === 'light') {
    isDark.value = false
    document.documentElement.removeAttribute('data-theme')
  } else {
    // Check system preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      isDark.value = true
      document.documentElement.setAttribute('data-theme', 'dark')
    }
  }
})

function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark')
    localStorage.setItem('melodybox-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
    localStorage.setItem('melodybox-theme', 'light')
  }
}
</script>

<style scoped>
.theme-toggle {
  background: transparent;
  border: 2px solid var(--border);
  cursor: pointer;
  padding: 4px;
  border-radius: 20px;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle:hover {
  border-color: var(--accent-light);
  transform: scale(1.05);
  background: var(--bg-tertiary);
}

.toggle-track {
  width: 48px;
  height: 26px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  position: relative;
  transition: all var(--transition);
  border: 2px solid var(--border);
}

.toggle-track.dark {
  background: var(--bg-elevated);
  border-color: var(--accent);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: var(--accent-gradient);
  border-radius: 50%;
  transition: all var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px var(--accent-glow);
}

.toggle-track.dark .toggle-thumb {
  left: 24px;
  transform: rotate(360deg);
}

.icon {
  transition: all var(--transition);
}

.sun {
  color: #ffd700;
}

.moon {
  color: #b19cd9;
}
</style>
