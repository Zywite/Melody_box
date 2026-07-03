<template>
  <div class="modal-overlay" @click.self="emit('cancel')">
    <div class="modal-content confirm-modal">
      <div class="modal-header">
        <h2 class="modal-title">{{ title }}</h2>
        <button @click="emit('cancel')" class="close-btn">
          <X :size="20" />
        </button>
      </div>
      <div class="modal-body">
        <p>{{ message }}</p>
      </div>
      <div class="modal-footer">
        <button @click="emit('cancel')" class="btn-cancel">{{ cancelText }}</button>
        <button @click="emit('confirm')" class="btn-danger">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { X } from 'lucide-vue-next'

defineProps({
  title: { type: String, default: 'Confirmar' },
  message: { type: String, required: true },
  confirmText: { type: String, default: 'Eliminar' },
  cancelText: { type: String, default: 'Cancelar' },
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-modal {
  max-width: 400px;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: var(--bg-tertiary, rgba(255, 255, 255, 0.08));
  color: var(--text-primary, #fff);
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
}

.btn-danger {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: #e11d48;
  color: #fff;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
}

.btn-danger:hover {
  background: #be123c;
}
</style>
