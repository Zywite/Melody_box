<template>
  <div class="mode-selector-overlay" @click.self="close">
    <div class="mode-selector">
      <h3 class="mode-title">¿Cómo quieres reproducir?</h3>
      <p class="mode-subtitle">"{{ playerStore.currentSong?.title }}"</p>
      
      <div class="mode-options">
        <button class="mode-option" @click="playVideo">
          <div class="option-icon">
            <Monitor :size="28" />
          </div>
          <span>Con video</span>
        </button>
        
        <button class="mode-option" @click="playAudio">
          <div class="option-icon">
            <Headphones :size="28" />
          </div>
          <span>Solo audio</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePlayerStore } from '@/stores/player'
import { Monitor, Headphones } from 'lucide-vue-next'

const playerStore = usePlayerStore()

function close() {
  playerStore.closeModeSelector()
}

function playVideo() {
  if (playerStore.currentSong) {
    playerStore.playWithMode(playerStore.currentSong, 'video')
  }
}

function playAudio() {
  if (playerStore.currentSong) {
    playerStore.playWithMode(playerStore.currentSong, 'audio')
  }
}
</script>

<style scoped>
.mode-selector-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.mode-selector {
  background: var(--bg-secondary);
  border-radius: 24px;
  padding: 32px;
  width: 90%;
  max-width: 420px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(225, 29, 72, 0.15);
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.mode-title {
  font-size: 1.4rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

.mode-subtitle {
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 32px;
  font-size: 0.95rem;
  font-family: 'DM Sans', sans-serif;
}

.mode-options {
  display: flex;
  gap: 16px;
}

.mode-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 28px 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-option:hover {
  background: rgba(225, 29, 72, 0.15);
  border-color: var(--accent-primary);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(225, 29, 72, 0.2);
}

.option-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(225, 29, 72, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
}

.mode-option:hover .option-icon {
  background: linear-gradient(135deg, #e11d48 0%, #7c3aed 100%);
  color: white;
}

.mode-option span {
  font-weight: 600;
  font-size: 1rem;
  font-family: 'DM Sans', sans-serif;
}
</style>