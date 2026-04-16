import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

export function useToast() {
  function showToast(title, message = '', type = 'success') {
    const id = ++toastId
    const toast = { id, title, message, type }
    toasts.value.push(toast)

    setTimeout(() => {
      removeToast(id)
    }, 4000)

    return id
  }

  function removeToast(id) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value[index].exiting = true
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id)
      }, 300)
    }
  }

  function success(title, message = '') {
    return showToast(title, message, 'success')
  }

  function error(title, message = '') {
    return showToast(title, message, 'error')
  }

  function info(title, message = '') {
    return showToast(title, message, 'info')
  }

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    info
  }
}