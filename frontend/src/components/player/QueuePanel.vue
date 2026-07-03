<template>
  <div class="queue-overlay" @click.self="close">
    <div class="queue-panel">
      <div class="queue-header">
        <h2 class="queue-title">Cola de reproducción</h2>
        <button @click="close" class="close-btn">
          <X :size="20" />
        </button>
      </div>

      <div class="queue-content">
        <div v-if="playerStore.playlist.length === 0" class="queue-empty">
          <ListMusic :size="32" />
          <p>No hay canciones en la cola</p>
        </div>

        <div v-else class="queue-list">
          <div 
            v-for="(song, index) in playerStore.playlist" 
            :key="song.id"
            class="queue-item"
            :class="{ active: index === playerStore.currentIndex }"
            @click="playFromQueue(index)"
          >
            <div class="queue-item-info">
              <p class="queue-item-title">{{ song.title }}</p>
              <p class="queue-item-artist">{{ song.artist }}</p>
            </div>
            <div class="queue-item-playing" v-if="index === playerStore.currentIndex">
              <div class="playing-bar">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <button v-else @click.stop="removeFromQueue(index)" class="remove-btn">
              <X :size="16" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePlayerStore } from '@/stores/player'
import { ListMusic, X } from 'lucide-vue-next'

const emit = defineEmits(['close'])
const playerStore = usePlayerStore()

function close() {
  emit('close')
}

function playFromQueue(index) {
  playerStore.currentIndex = index
  playerStore.play(playerStore.playlist[index])
}

function removeFromQueue(index) {
  playerStore.removeFromQueue(index)
}
</script>

<style scoped>
.queue-overlay {
  position: fixed;
  inset:0;
  background: rgba(255, 245, 247, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: flex-end;
  z-index:1000;
  animation: fadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.queue-panel {
  width:100%;
  max-width:420px;
  height:100%;
  background: var(--bg-secondary);
  border-left:2px solid var(--border);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: -4px 0 30px rgba(255, 158, 187, 0.15);
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.queue-panel {
  width: 100%;
  max-width: 400px;
  height: 100%;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.queue-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding:20px 24px;
  border-bottom:2px solid var(--border);
}

.queue-title {
  font-size:1.35rem;
  font-weight:700;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.close-btn {
  padding:8px;
  border-radius:12px;
  background: transparent;
  border: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent);
  border-color: var(--accent-light);
  transform: scale(1.05);
}

.queue-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

.close-btn {
  padding: 8px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.queue-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.queue-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
  gap: 12px;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.queue-item {
  display: flex;
  align-items: center;
  gap:12px;
  padding:14px;
  border-radius:14px;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 2px solid transparent;
}

.queue-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--border);
}

.queue-item.active {
  background: rgba(255, 158, 187, 0.15);
  border-color: var(--accent-light);
}

.queue-item:hover {
  background: var(--bg-tertiary);
}

.queue-item.active {
  background: rgba(225, 29, 72, 0.15);
}

.queue-item-info {
  flex: 1;
  min-width: 0;
}

.queue-item-title {
  font-size:0.9rem;
  font-weight:600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Nunito', sans-serif;
}

.queue-item.active .queue-item-title {
  color: var(--accent);
}

.queue-item-artist {
  font-size:0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'Nunito', sans-serif;
}

.queue-item.active .queue-item-title {
  color: var(--accent-primary);
}

.queue-item-artist {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.queue-item-playing {
  display: flex;
  align-items: center;
  justify-content: center;
}

.playing-bar {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 16px;
}

.playing-bar span {
  width:3px;
  background: var(--accent-gradient);
  border-radius:2px;
  animation: playingBar 0.8s ease-in-out infinite;
}

.playing-bar span:nth-child(1) { height: 60%; animation-delay: 0s; }
.playing-bar span:nth-child(2) { height: 100%; animation-delay: 0.2s; }
.playing-bar span:nth-child(3) { height: 40%; animation-delay: 0.4s; }

@keyframes playingBar {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.5); }
}

.remove-btn {
  padding:6px;
  border-radius:50%;
  background: transparent;
  border: 2px solid transparent;
  color: var(--text-muted);
  cursor: pointer;
  opacity:0;
  transition: all var(--transition-fast);
}

.queue-item:hover .remove-btn {
  opacity:1;
}

.remove-btn:hover {
  background: rgba(255, 107, 138, 0.15);
  color: var(--danger);
  border-color: var(--danger);
  transform: scale(1.1);
}

.queue-item:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
}

@media (max-width: 480px) {
  .queue-panel {
    max-width: 100%;
  }
}
</style>