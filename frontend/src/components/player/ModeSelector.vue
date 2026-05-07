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
  inset:0;
  background: rgba(255, 245, 247, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index:1000;
  animation: fadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fadeIn {
  from { opacity:0; }
  to { opacity:1; }
}

.mode-selector {
  background: var(--bg-secondary);
  border-radius: 32px;
  padding: 36px;
  width:90%;
  max-width:440px;
  border:2px solid var(--border);
  box-shadow:0 20px 60px rgba(255, 158, 187, 0.2);
  animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity:0; }
  to { transform: translateY(0); opacity:1; }
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
  font-size:1.5rem;
  font-weight:800;
  text-align: center;
  margin-bottom:8px;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.mode-subtitle {
  color: var(--text-secondary);
  text-align: center;
  margin-bottom:32px;
  font-size:0.95rem;
  font-family: 'Nunito', sans-serif;
  color: var(--accent);
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
  flex:1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap:16px;
  padding:32px 20px;
  background: var(--bg-tertiary);
  border:2px solid var(--border);
  border-radius: 24px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition);
}

.mode-option:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-light);
  transform: translateY(-6px) scale(1.03);
  box-shadow:0 12px 32px var(--accent-glow);
}

.mode-option:hover {
  background: rgba(225, 29, 72, 0.15);
  border-color: var(--accent-primary);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(225, 29, 72, 0.2);
}

.option-icon {
  width:72px;
  height:72px;
  border-radius:20px;
  background: var(--accent-gradient);
  background-size: 200% 200%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow:0 4px 20px var(--accent-glow);
  transition: all var(--transition);
}

.mode-option:hover .option-icon {
  transform: scale(1.1);
  box-shadow:0 8px 30px var(--accent-glow);
}

.mode-option span {
  font-weight:600;
  font-size:1.05rem;
  font-family: 'Nunito', sans-serif;
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