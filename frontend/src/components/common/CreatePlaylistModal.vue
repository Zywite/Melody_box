<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title">Crear playlist</h2>
        <button @click="emit('close')" class="close-btn">
          <X :size="20" />
        </button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Nombre</label>
          <input
            v-model="name"
            type="text"
            class="input-field"
            placeholder="Mi playlist"
            @keyup.enter="create"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Descripción (opcional)</label>
          <textarea
            v-model="description"
            class="input-field"
            rows="3"
            placeholder="Descripción de la playlist"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="emit('close')" class="btn-secondary">Cancelar</button>
        <button @click="create" class="btn-primary" :disabled="!name.trim() || isLoading">
          <span v-if="isLoading">Creando...</span>
          <span v-else>Crear playlist</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLibraryStore } from '@/stores/library'
import { useToast } from '@/composables/useToast'
import { X } from 'lucide-vue-next'

const emit = defineEmits(['close', 'created'])

const libraryStore = useLibraryStore()
const toast = useToast()

const name = ref('')
const description = ref('')
const isLoading = ref(false)

async function create() {
  if (!name.value.trim()) return

  isLoading.value = true
  try {
    await libraryStore.createPlaylist(name.value, description.value)
    toast.success('Playlist creada')
    emit('created')
  } catch (e) {
    toast.error('Error', e.message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
  transition: all 0.2s ease;
}

.input-field:focus {
  border-color: var(--accent);
}

.input-field::placeholder {
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>