<template>
  <div
    ref="viewport"
    class="virtual-list"
    @scroll.passive="onScroll"
  >
    <div class="virtual-list-spacer" :style="{ height: `${totalHeight}px` }">
      <div
        class="virtual-list-window"
        :style="{ transform: `translateY(${offsetY}px)` }"
      >
        <div
          v-for="item in visibleItems"
          :key="item.__virtualKey"
          class="virtual-list-item"
          :style="{ height: `${itemHeight}px` }"
        >
          <slot :item="item" :index="item.__virtualIndex" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  itemHeight: { type: Number, required: true },
  overscan: { type: Number, default: 6 },
  keyField: { type: String, default: 'id' },
})

const viewport = ref(null)
const scrollTop = ref(0)
const viewportHeight = ref(0)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleItems = computed(() => {
  if (viewportHeight.value === 0) return []

  const start = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.overscan)
  const visibleCount = Math.ceil(viewportHeight.value / props.itemHeight) + props.overscan * 2
  const end = Math.min(props.items.length, start + visibleCount)

  const result = []
  for (let i = start; i < end; i++) {
    const item = props.items[i]
    if (item) {
      result.push({
        ...item,
        __virtualKey: item[props.keyField] ?? i,
        __virtualIndex: i,
      })
    }
  }
  return result
})

const offsetY = computed(() => {
  const start = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.overscan)
  return start * props.itemHeight
})

function onScroll(e) {
  scrollTop.value = e.target.scrollTop
}

function measureViewport() {
  if (viewport.value) {
    viewportHeight.value = viewport.value.clientHeight
  }
}

let resizeObserver = null

onMounted(() => {
  measureViewport()
  nextTick(measureViewport)

  if (typeof ResizeObserver !== 'undefined' && viewport.value) {
    resizeObserver = new ResizeObserver(measureViewport)
    resizeObserver.observe(viewport.value)
  } else {
    window.addEventListener('resize', measureViewport)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  } else {
    window.removeEventListener('resize', measureViewport)
  }
})

watch(() => props.items.length, () => {
  if (viewport.value && scrollTop.value > totalHeight.value) {
    viewport.value.scrollTop = 0
    scrollTop.value = 0
  }
})
</script>

<style scoped>
.virtual-list {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  contain: strict;
}

.virtual-list-spacer {
  position: relative;
  width: 100%;
}

.virtual-list-window {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  will-change: transform;
}

.virtual-list-item {
  width: 100%;
}
</style>
