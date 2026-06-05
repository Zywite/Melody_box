import { ref, onUnmounted } from 'vue'

export function usePolling() {
  let pollInterval = null

  function startPolling({ taskId, fetchTask, onDone, onProgress, interval = 2000, maxAttempts = 60 }) {
    return new Promise((resolve, reject) => {
      let attempts = 0

      pollInterval = setInterval(async () => {
        attempts++

        try {
          const task = await fetchTask(taskId)

          if (task.status === 'done') {
            stopPolling()
            if (onDone) onDone(task.result)
            resolve(task.result)
          } else if (task.status === 'failed') {
            stopPolling()
            reject(new Error(task.error || 'Task failed'))
          } else {
            if (onProgress) onProgress(task.status, attempts)
          }
        } catch (err) {
          if (attempts >= maxAttempts) {
            stopPolling()
            reject(new Error('Task timeout'))
          }
        }
      }, interval)
    })
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  onUnmounted(() => stopPolling())

  return { startPolling, stopPolling }
}
