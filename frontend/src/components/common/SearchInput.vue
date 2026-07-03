<template>
  <div class="search-input-wrapper">
    <Search :size="20" class="search-icon" />
    <input
      :value="modelValue"
      type="text"
      class="search-field"
      :placeholder="placeholder"
      @input="handleInput"
      @keyup.enter="emit('search')"
    />
    <button v-if="modelValue" @click="clearSearch" class="clear-btn">
      <X :size="18" />
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, X } from 'lucide-vue-next'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Buscar...' }
})

const emit = defineEmits(['update:modelValue', 'search'])

let debounceTimer = null

function handleInput(event) {
  const value = event.target.value
  emit('update:modelValue', value)

  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('search')
  }, 300)
}

function clearSearch() {
  if (debounceTimer) clearTimeout(debounceTimer)
  emit('update:modelValue', '')
  emit('search')
}
</script>

<style scoped>
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width:100%;
  max-width: 600px;
}

.search-icon {
  position: absolute;
  left: 20px;
  color: var(--accent);
  pointer-events: none;
}

.search-field {
  width:100%;
  padding:16px 48px;
  background: var(--bg-secondary);
  border:2px solid var(--border);
  border-radius: 24px;
  color: var(--text-primary);
  font-size:0.95rem;
  font-family: 'Nunito', sans-serif;
  transition: all var(--transition);
}

.search-field::placeholder {
  color: var(--text-muted);
  font-style: italic;
}

.search-field:focus {
  outline: none;
  border-color: var(--accent);
  background: var(--bg-primary);
  box-shadow:0 0 0 4px var(--accent-glow);
}

.clear-btn {
  position: absolute;
  right:14px;
  background: var(--bg-tertiary);
  border:2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding:6px;
  border-radius:50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.clear-btn:hover {
  background: rgba(255, 158, 187, 0.2);
  color: var(--accent);
  border-color: var(--accent-light);
  transform: scale(1.1);
}
</style>