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
import { Search, X } from 'lucide-vue-next'

defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Buscar...' }
})

const emit = defineEmits(['update:modelValue', 'search'])

function handleInput(event) {
  emit('update:modelValue', event.target.value)
}

function clearSearch() {
  emit('update:modelValue', '')
  emit('search')
}
</script>

<style scoped>
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: var(--text-secondary);
  pointer-events: none;
}

.search-field {
  width: 100%;
  padding: 14px 44px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: 'DM Sans', sans-serif;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-field::placeholder {
  color: var(--text-muted);
}

.search-field:focus {
  outline: none;
  border-color: var(--accent-primary);
  background: rgba(225, 29, 72, 0.05);
  box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.15);
}

.clear-btn {
  position: absolute;
  right: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: rgba(225, 29, 72, 0.2);
  color: var(--accent-primary);
}
</style>