<template>
  <div>
    <div class="search-section">
      <div class="search-input-wrapper">
        <Search :size="20" class="search-icon" />
        <input
          :value="query"
          type="text"
          class="search-field"
          placeholder="Buscar videos en YouTube..."
          @input="$emit('update:query', $event.target.value)"
          @keyup.enter="$emit('search')"
        />
        <button v-if="query" @click="$emit('update:query', '')" class="clear-btn">
          <X :size="18" />
        </button>
      </div>
      <button @click="$emit('search')" class="btn-primary" :disabled="isSearching || !query.trim()">
        <Search :size="18" />
        Buscar
      </button>
    </div>

    <div v-if="results.length" class="filters-section">
      <div class="filter-group">
        <label>Duración:</label>
        <select :value="duration" @change="$emit('update:duration', $event.target.value)" class="filter-select">
          <option value="all">Todas</option>
          <option value="short">Corto (&lt; 4 min)</option>
          <option value="medium">Medio (4-10 min)</option>
          <option value="long">Largo (&gt; 10 min)</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Ordenar:</label>
        <select :value="sort" @change="$emit('update:sort', $event.target.value)" class="filter-select">
          <option value="relevance">Relevancia</option>
          <option value="date">Fecha</option>
          <option value="views">Vistas</option>
        </select>
      </div>
      <div class="results-count">
        {{ filtered }} de {{ results.length }} resultados
      </div>
    </div>

    <div v-if="isSearching" class="loading-state">
      <div class="spinner"></div>
      <p>Buscando en YouTube...</p>
    </div>

    <div v-else-if="results.length" class="results-section">
      <h3 class="section-label">Resultados ({{ filtered }})</h3>
      <slot />
    </div>

    <div v-else-if="hasSearched && !results.length" class="empty-state">
      <Youtube :size="48" class="opacity-30" />
      <h3>No se encontraron resultados</h3>
      <p>Intenta con otras palabras clave</p>
    </div>
  </div>
</template>

<script setup>
import { Search, X, Youtube } from 'lucide-vue-next'

defineProps({
  query: { type: String, required: true },
  isSearching: { type: Boolean, default: false },
  results: { type: Array, default: () => [] },
  filtered: { type: Number, default: 0 },
  duration: { type: String, default: 'all' },
  sort: { type: String, default: 'relevance' },
  hasSearched: { type: Boolean, default: false },
})

defineEmits(['search', 'update:query', 'update:duration', 'update:sort'])

defineExpose({})
</script>

<style scoped>
.search-section {
  display: flex;
  gap: 12px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
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
  transition: all 0.3s ease;
}

.search-field:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.clear-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
}

.filters-section {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 12px 0;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.filter-select {
  padding: 6px 12px;
  border-radius: 8px;
  border: 2px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.85rem;
  font-family: 'Nunito', sans-serif;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-select:hover {
  border-color: var(--accent);
}

.results-count {
  margin-left: auto;
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.results-section {
  margin-top: 16px;
}

.section-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
