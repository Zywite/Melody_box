<template>
  <div class="sakura-container" v-if="active">
    <div
      v-for="petal in petals"
      :key="petal.id"
      class="sakura-petal"
      :style="{
        left: petal.left + '%',
        animationDelay: petal.delay + 's',
        '--duration': petal.duration + 's',
        '--sway': petal.sway + 's',
        width: petal.size + 'px',
        height: petal.size + 'px',
        opacity: petal.opacity,
      }"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const active = ref(true)
const petals = ref([])
const petalCount = 25

function createPetal(id) {
  return {
    id,
    left: Math.random() * 100,
    delay: Math.random() * 10,
    duration: 8 + Math.random() * 12,
    sway: 2 + Math.random() * 4,
    size: 15 + Math.random() * 20,
    opacity: 0.3 + Math.random() * 0.5,
  }
}

onMounted(() => {
  for (let i = 0; i < petalCount; i++) {
    petals.value.push(createPetal(i))
  }
})
</script>

<style scoped>
.sakura-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9998;
  overflow: hidden;
}

.sakura-petal {
  position: absolute;
  top: -30px;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 183, 197, 0.8) 0%,
    rgba(255, 158, 187, 0.4) 50%,
    transparent 70%
  );
  border-radius: 50% 0 50% 0;
  pointer-events: none;
  animation:
    sakura-fall var(--duration, 10s) linear infinite,
    sakura-sway var(--sway, 3s) ease-in-out infinite;
}

@keyframes sakura-fall {
  0% {
    transform: translateY(-10vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.6;
  }
  90% {
    opacity: 0.4;
  }
  100% {
    transform: translateY(110vh) rotate(720deg);
    opacity: 0;
  }
}

@keyframes sakura-sway {
  0%, 100% {
    transform: translateX(0) rotate(0deg);
  }
  25% {
    transform: translateX(30px) rotate(45deg);
  }
  50% {
    transform: translateX(-20px) rotate(-30deg);
  }
  75% {
    transform: translateX(15px) rotate(60deg);
  }
}
</style>
