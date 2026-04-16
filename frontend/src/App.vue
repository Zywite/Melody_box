<template>
  <div class="app-background"></div>
  <audio ref="audioRef" @ended="onEnded" @timeupdate="onTimeUpdate" @loadedmetadata="onLoadedMetadata"></audio>
  <div id="app" class="flex flex-col h-full relative">
    <template v-if="authStore.isAuthenticated">
      <div class="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main class="page-container scrollbar-thin">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
      <PlayerBar v-if="playerStore.hasCurrent" />
      <MobileNav />
    </template>
    <template v-else>
      <div class="flex-1 flex items-center justify-center min-h-screen p-4">
        <router-view />
      </div>
    </template>
    <ToastContainer />
    <VideoFlyout v-if="playerStore.showVideoFlyout && playerStore.isVideo && playerStore.currentSong" />
    <ModeSelector v-if="playerStore.showModeSelector" />
    <QueuePanel v-if="playerStore.showQueue" @close="playerStore.toggleQueue" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePlayerStore } from '@/stores/player'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import PlayerBar from '@/components/player/PlayerBar.vue'
import MobileNav from '@/components/layout/MobileNav.vue'
import ToastContainer from '@/components/layout/ToastContainer.vue'
import VideoFlyout from '@/components/player/VideoFlyout.vue'
import ModeSelector from '@/components/player/ModeSelector.vue'
import QueuePanel from '@/components/player/QueuePanel.vue'

const authStore = useAuthStore()
const playerStore = usePlayerStore()
const audioRef = ref(null)

onMounted(() => {
  authStore.initFromStorage()
  if (audioRef.value) {
    playerStore.initAudio(audioRef.value)
  }
})

function onEnded() {
  playerStore.playNext()
}

function onTimeUpdate() {
  playerStore.currentTime = audioRef.value?.currentTime || 0
}

function onLoadedMetadata() {
  playerStore.duration = audioRef.value?.duration || 0
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>