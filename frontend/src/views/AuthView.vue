<template>
  <div class="w-full max-w-[440px] mx-auto">
    <div class="glass-panel-strong p-12 w-[90%] relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-50"></div>
      
      <div class="text-center mb-8 animation-[pulse_3s_ease-in-out_infinite]">
        <MelodyLogo class="mx-auto" :size="48" />
      </div>
      
      <div v-if="!showRegister" class="auth-form">
        <h2 class="text-[1.75rem] font-bold text-center mb-1 text-gradient">Bienvenido de vuelta</h2>
        <p class="text-[var(--text-secondary)] text-center mb-7 text-sm">Inicia sesión para continuar</p>
        
        <div class="mb-4">
          <label class="block text-sm font-semibold text-[var(--text-secondary)] mb-2 tracking-wide">Email</label>
          <input v-model="loginForm.email" type="text" class="input-field" placeholder="tu@email.com" />
        </div>
        
        <div class="mb-6">
          <label class="block text-sm font-semibold text-[var(--text-secondary)] mb-2 tracking-wide">Contraseña</label>
          <input v-model="loginForm.password" type="password" class="input-field" placeholder="Tu contraseña" />
        </div>
        
        <button @click="handleLogin" class="btn-primary" :disabled="isLoading">
          <span v-if="isLoading">Cargando...</span>
          <span v-else>Iniciar sesión</span>
        </button>
        
        <p class="text-center mt-6 text-[var(--text-secondary)] text-sm">
          ¿No tienes cuenta? <a @click="showRegister = true" class="text-[var(--accent)] cursor-pointer font-semibold hover:underline">Regístrate gratis</a>
        </p>
      </div>
      
      <div v-else class="auth-form">
        <h2 class="text-[1.75rem] font-bold text-center mb-1 text-gradient">Crear cuenta</h2>
        <p class="text-[var(--text-secondary)] text-center mb-7 text-sm">Únete a MelodyBox</p>
        
        <div class="mb-4">
          <label class="block text-sm font-semibold text-[var(--text-secondary)] mb-2 tracking-wide">Usuario</label>
          <input v-model="registerForm.username" type="text" class="input-field" placeholder="Tu nombre de usuario" />
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-semibold text-[var(--text-secondary)] mb-2 tracking-wide">Email</label>
          <input v-model="registerForm.email" type="email" class="input-field" placeholder="tu@email.com" />
        </div>
        
        <div class="mb-4">
          <label class="block text-sm font-semibold text-[var(--text-secondary)] mb-2 tracking-wide">Contraseña</label>
          <input v-model="registerForm.password" type="password" class="input-field" placeholder="Mínimo 6 caracteres" />
        </div>
        
        <div class="mb-6">
          <label class="block text-sm font-semibold text-[var(--text-secondary)] mb-2 tracking-wide">Confirmar contraseña</label>
          <input v-model="registerForm.confirm" type="password" class="input-field" placeholder="Repite la contraseña" />
        </div>
        
        <button @click="handleRegister" class="btn-primary" :disabled="isLoading">
          <span v-if="isLoading">Cargando...</span>
          <span v-else>Crear cuenta</span>
        </button>
        
        <p class="text-center mt-6 text-[var(--text-secondary)] text-sm">
          ¿Ya tienes cuenta? <a @click="showRegister = false" class="text-[var(--accent)] cursor-pointer font-semibold hover:underline">Inicia sesión</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { Music2 } from 'lucide-vue-next'

const MelodyLogo = Music2

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const showRegister = ref(false)
const isLoading = ref(false)

const loginForm = reactive({ email: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '', confirm: '' })

async function handleLogin() {
  if (!loginForm.email || !loginForm.password) {
    toast.error('Completa todos los campos')
    return
  }
  
  isLoading.value = true
  try {
    await authStore.login(loginForm.email, loginForm.password)
    toast.success('Bienvenido', `Hola ${authStore.username}`)
    router.push('/home')
  } catch (e) {
    toast.error('Error de inicio de sesión', e.message)
  } finally {
    isLoading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.username || !registerForm.email || !registerForm.password || !registerForm.confirm) {
    toast.error('Completa todos los campos')
    return
  }
  
  if (registerForm.password !== registerForm.confirm) {
    toast.error('Las contraseñas no coinciden')
    return
  }
  
  isLoading.value = true
  try {
    await authStore.register(registerForm.username, registerForm.email, registerForm.password)
    toast.success('Registro exitoso', 'Ahora puedes iniciar sesión')
    showRegister.value = false
  } catch (e) {
    toast.error('Error en el registro', e.message)
  } finally {
    isLoading.value = false
  }
}
</script>