<template>
  <div class="admin-view">
    <div class="admin-header">
      <div class="header-icon">
        <Shield :size="28" />
      </div>
      <h1 class="page-title">Panel de Administración</h1>
      <p class="page-subtitle">Gestión de usuarios y contenido</p>
    </div>

    <div class="admin-tabs">
      <router-link to="/admin" class="tab" :class="{ active: $route.path === '/admin' }">
        <Users :size="18" />
        Usuarios
      </router-link>
      <router-link to="/admin/content" class="tab" :class="{ active: $route.path === '/admin/content' }">
        <Music :size="18" />
        Contenido
      </router-link>
    </div>

    <div class="admin-toolbar">
      <div class="search-wrapper">
        <Search :size="18" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar usuarios..."
          class="search-input"
          @input="debouncedSearch"
        />
      </div>
      <div class="stats-badge">
        <span class="stat-label">Total:</span>
        <span class="stat-value">{{ totalUsers }}</span>
      </div>
    </div>

    <div class="table-container">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Registro</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td class="user-cell">
              <div class="user-avatar-sm">{{ user.username.charAt(0).toUpperCase() }}</div>
              <span class="username">{{ user.username }}</span>
            </td>
            <td class="email-cell">{{ user.email }}</td>
            <td>
              <span class="role-badge" :class="user.role === 'admin' ? 'admin' : 'user'">
                {{ user.role }}
              </span>
            </td>
            <td>
              <span class="status-dot" :class="user.is_active ? 'active' : 'inactive'"></span>
              {{ user.is_active ? 'Activo' : 'Inactivo' }}
            </td>
            <td class="date-cell">{{ formatDate(user.created_at) }}</td>
            <td class="actions-cell">
              <button class="action-btn edit" @click="openEditModal(user)" title="Editar">
                <Pen :size="16" />
              </button>
              <button
                class="action-btn toggle"
                :class="user.is_active ? 'warn' : 'success'"
                @click="toggleActive(user)"
                :title="user.is_active ? 'Desactivar' : 'Activar'"
              >
                <ToggleLeft :size="16" v-if="user.is_active" />
                <ToggleRight :size="16" v-else />
              </button>
              <button
                class="action-btn delete"
                @click="confirmDelete(user)"
                title="Eliminar"
                :disabled="user.role === 'admin'"
              >
                <Trash2 :size="16" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!users.length && !loading" class="empty-state">
        <Users :size="48" />
        <p>No se encontraron usuarios</p>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingUser" class="modal-overlay" @click.self="editingUser = null">
      <div class="modal-content">
        <h3>Editar Usuario</h3>
        <div class="form-group">
          <label>Username</label>
          <input v-model="editForm.username" class="form-input" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="editForm.email" class="form-input" type="email" />
        </div>
        <div class="form-group" v-if="editingUser.role !== 'admin'">
          <label>Rol</label>
          <select v-model="editForm.role" class="form-input">
            <option value="user">user</option>
            <option value="admin">admin</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="editingUser = null">Cancelar</button>
          <button class="btn-primary" @click="saveEdit">Guardar</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deletingUser" class="modal-overlay" @click.self="deletingUser = null">
      <div class="modal-content">
        <h3>Eliminar Usuario</h3>
        <p>¿Estás seguro de eliminar a <strong>{{ deletingUser.username }}</strong>?</p>
        <p class="text-sm text-[var(--text-secondary)]">Esta acción no se puede deshacer.</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="deletingUser = null">Cancelar</button>
          <button class="btn-danger" @click="deleteUser">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/useApi'
import { Shield, Users, Music, Search, Pen, Trash2, ToggleLeft, ToggleRight } from 'lucide-vue-next'

const users = ref([])
const totalUsers = ref(0)
const searchQuery = ref('')
const loading = ref(true)
const editingUser = ref(null)
const editForm = ref({ username: '', email: '', role: '' })
const deletingUser = ref(null)
let debounceTimer = null

onMounted(async () => {
  await loadUsers()
  try {
    const res = await api.adminCountUsers()
    totalUsers.value = res.count
  } catch (e) {
    console.error(e)
  }
})

async function loadUsers() {
  loading.value = true
  try {
    users.value = await api.adminGetUsers(searchQuery.value || undefined)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadUsers, 300)
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' })
}

function openEditModal(user) {
  editingUser.value = user
  editForm.value = {
    username: user.username,
    email: user.email,
    role: user.role
  }
}

async function saveEdit() {
  try {
    const data = {}
    if (editForm.value.username !== editingUser.value.username) data.username = editForm.value.username
    if (editForm.value.email !== editingUser.value.email) data.email = editForm.value.email
    if (editForm.value.role !== editingUser.value.role) data.role = editForm.value.role
    if (Object.keys(data).length === 0) {
      editingUser.value = null
      return
    }
    await api.adminUpdateUser(editingUser.value.id, data)
    editingUser.value = null
    await loadUsers()
  } catch (e) {
    alert('Error: ' + e.message)
  }
}

async function toggleActive(user) {
  try {
    await api.adminToggleUserActive(user.id)
    await loadUsers()
  } catch (e) {
    alert('Error: ' + e.message)
  }
}

function confirmDelete(user) {
  deletingUser.value = user
}

async function deleteUser() {
  try {
    await api.adminDeleteUser(deletingUser.value.id)
    deletingUser.value = null
    await loadUsers()
  } catch (e) {
    alert('Error: ' + e.message)
  }
}
</script>

<style scoped>
.admin-view {
  padding: 32px;
  animation: fadeIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.admin-header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 16px;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.page-title {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  color: var(--text-secondary);
}

.admin-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  justify-content: center;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  color: var(--text-secondary);
  font-family: 'Nunito', sans-serif;
  font-weight: 600;
  text-decoration: none;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.tab:hover {
  border-color: var(--accent-light);
  color: var(--text-primary);
  transform: translateY(-2px);
}

.tab.active {
  background: var(--accent-gradient);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.admin-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 16px;
}

.search-wrapper {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border-radius: var(--radius-full);
  border: 2px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.stats-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
  border: 2px solid var(--border);
}

.stats-badge .stat-label {
  font-family: 'Nunito', sans-serif;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.stats-badge .stat-value {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  font-size: 1.1rem;
  color: var(--accent);
}

.table-container {
  background: var(--bg-secondary);
  border: 2px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th {
  padding: 16px 20px;
  text-align: left;
  font-family: 'Nunito', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  border-bottom: 2px solid var(--border);
}

.admin-table td {
  padding: 14px 20px;
  font-family: 'Nunito', sans-serif;
  font-size: 0.9rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
}

.admin-table tr:last-child td {
  border-bottom: none;
}

.admin-table tr:hover td {
  background: rgba(255, 158, 187, 0.08);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-sm {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.username {
  font-weight: 600;
}

.email-cell {
  color: var(--text-secondary);
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.admin {
  background: linear-gradient(135deg, rgba(255, 158, 187, 0.2), rgba(177, 156, 217, 0.2));
  color: var(--accent);
  border: 1px solid var(--accent-light);
}

.role-badge.user {
  background: rgba(135, 206, 235, 0.15);
  color: var(--blue-accent);
  border: 1px solid rgba(135, 206, 235, 0.3);
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.status-dot.active {
  background: var(--success);
  box-shadow: 0 0 8px var(--mint-glow);
}

.status-dot.inactive {
  background: var(--danger);
  box-shadow: 0 0 8px var(--danger-glow);
}

.date-cell {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.actions-cell {
  display: flex;
  gap: 6px;
}

.action-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 2px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  transform: scale(1.1);
}

.action-btn.edit:hover {
  background: rgba(135, 206, 235, 0.15);
  color: var(--blue-accent);
  border-color: rgba(135, 206, 235, 0.3);
}

.action-btn.toggle.warn:hover {
  background: rgba(255, 215, 0, 0.15);
  color: var(--warning);
  border-color: rgba(255, 215, 0, 0.3);
}

.action-btn.toggle.success:hover {
  background: rgba(152, 251, 152, 0.15);
  color: var(--success);
  border-color: rgba(152, 251, 152, 0.3);
}

.action-btn.delete:hover {
  background: rgba(255, 107, 138, 0.15);
  color: var(--danger);
  border-color: rgba(255, 107, 138, 0.3);
}

.action-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-state p {
  margin-top: 12px;
  font-family: 'Nunito', sans-serif;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  padding: 32px;
  width: 90%;
  max-width: 460px;
  box-shadow: var(--shadow-lg);
}

.modal-content h3 {
  font-family: 'Mochiy Pop P One', 'Nunito', sans-serif;
  font-size: 1.3rem;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-family: 'Nunito', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border-radius: var(--radius);
  border: 2px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: 'Nunito', sans-serif;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

select.form-input {
  cursor: pointer;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-primary {
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: var(--accent-gradient);
  color: white;
  border: none;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px var(--accent-glow);
}

.btn-secondary {
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border);
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  border-color: var(--accent-light);
  transform: scale(1.05);
}

.btn-danger {
  padding: 10px 24px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--danger) 0%, #ff4d6d 100%);
  color: white;
  border: none;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-danger:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px var(--danger-glow);
}

@media (max-width: 768px) {
  .admin-view {
    padding: 20px 16px;
  }
  .page-title {
    font-size: 1.5rem;
  }
  .admin-toolbar {
    flex-direction: column;
  }
  .search-wrapper {
    max-width: 100%;
  }
  .admin-table th,
  .admin-table td {
    padding: 10px 12px;
    font-size: 0.8rem;
  }
  .date-cell {
    display: none;
  }
}
</style>