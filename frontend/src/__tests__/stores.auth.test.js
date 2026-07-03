import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockApi } = vi.hoisted(() => ({
  mockApi: {
    login: vi.fn(),
    register: vi.fn(),
  },
}))

vi.mock('@/composables/useApi', () => ({
  default: mockApi,
}))

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.clear()
  vi.clearAllMocks()
})

describe('auth store', () => {
  it('starts unauthenticated', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(store.username).toBeNull()
  })

  it('login sets token and user data', async () => {
    mockApi.login.mockResolvedValue({
      access_token: 'abc123',
      username: 'testuser',
      user_id: 1,
      role: 'user',
    })

    const store = useAuthStore()
    await store.login('test@test.com', 'password')

    expect(store.isAuthenticated).toBe(true)
    expect(store.token).toBe('abc123')
    expect(store.username).toBe('testuser')
    expect(store.userId).toBe(1)
    expect(localStorage.getItem('token')).toBe('abc123')
  })

  it('login stores admin role', async () => {
    mockApi.login.mockResolvedValue({
      access_token: 'xyz',
      username: 'admin',
      user_id: 2,
      role: 'admin',
    })

    const store = useAuthStore()
    await store.login('admin@test.com', 'adminpass')

    expect(store.isAdmin).toBe(true)
  })

  it('login throws on error', async () => {
    mockApi.login.mockRejectedValue(new Error('Invalid credentials'))

    const store = useAuthStore()
    await expect(store.login('bad', 'creds')).rejects.toThrow('Invalid credentials')
    expect(store.isAuthenticated).toBe(false)
  })

  it('logout clears everything', () => {
    localStorage.setItem('token', 'abc')
    localStorage.setItem('username', 'testuser')

    const store = useAuthStore()
    store.token = 'abc'
    store.username = 'testuser'
    store.userId = 1
    store.role = 'user'

    store.logout()

    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('register calls api and does not set token', async () => {
    mockApi.register.mockResolvedValue(undefined)

    const store = useAuthStore()
    await store.register('newuser', 'new@test.com', 'password')

    expect(mockApi.register).toHaveBeenCalledWith('newuser', 'new@test.com', 'password')
    expect(store.isAuthenticated).toBe(false)
  })
})
