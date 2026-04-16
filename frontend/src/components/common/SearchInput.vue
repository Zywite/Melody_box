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

const props = defineProps({
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