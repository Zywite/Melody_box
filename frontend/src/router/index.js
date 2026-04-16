import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'auth',
    component: () => import('@/views/AuthView.vue')
  },
  {
    path: '/home',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('@/views/LibraryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/playlists',
    name: 'playlists',
    component: () => import('@/views/PlaylistsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/playlists/:id',
    name: 'playlist-detail',
    component: () => import('@/views/PlaylistDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('@/views/UploadView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/home'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.initFromStorage()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/')
  } else if (to.path === '/' && authStore.isAuthenticated) {
    next('/home')
  } else {
    next()
  }
})

export default router