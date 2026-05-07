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
  inset:0;
  background: rgba(255, 245, 247, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fadeIn {
  from { opacity:0; }
  to { opacity:1; }
}

.modal-content {
  background: var(--bg-secondary);
  border-radius: 28px;
  width: 100%;
  max-width: 460px;
  overflow: hidden;
  border:2px solid var(--border);
  box-shadow:0 20px 60px rgba(255, 158, 187, 0.2);
  animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity:0; }
  to { transform: translateY(0); opacity:1; }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-bottom:2px solid var(--border);
}

.modal-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
}

.close-btn {
  background: var(--bg-tertiary);
  border:2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 12px;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 158, 187, 0.2);
  color: var(--accent);
  border-color: var(--accent-light);
  transform: scale(1.05);
}

.modal-body {
  padding: 28px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
}

.input-field {
  width: 100%;
  padding: 14px 18px;
  background: var(--bg-primary);
  border:2px solid var(--border);
  border-radius: 16px;
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
  transition: all var(--transition-fast);
  font-family: 'Nunito', sans-serif;
}

.input-field:focus {
  border-color: var(--accent);
  box-shadow:0 0 0 4px var(--accent-glow);
  background: var(--bg-secondary);
}

.input-field::placeholder {
  color: var(--text-muted);
  font-style: italic;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top:2px solid var(--border);
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