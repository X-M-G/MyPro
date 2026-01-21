import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('../layouts/DefaultLayout.vue'),
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('../views/HomeView.vue')
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'prompt-assistant',
          name: 'prompt-assistant',
          component: () => import('../views/PromptAssistantView.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('../views/HistoryView.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'credits',
          name: 'credits',
          component: () => import('../views/CreditsView.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'announcements',
          name: 'announcements',
          component: () => import('../views/AnnouncementsView.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: 'faq',
          name: 'faq',
          component: () => import('../views/FaqView.vue'),
          meta: { requiresAuth: true }
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('../views/ResetPasswordView.vue')
    },
    {
      path: '/adym',
      component: () => import('../layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: '/adym/dashboard'
        },
        {
          path: 'dashboard',
          component: () => import('../views/admin/AdminDashboard.vue')
        },
        {
          path: 'users',
          component: () => import('../views/admin/UserManagement.vue')
        },
        {
          path: 'logs',
          component: () => import('../views/admin/AdminLogs.vue')
        },
        {
          path: 'announcements',
          component: () => import('../views/admin/Announcements.vue')
        },
        {
          path: 'faqs',
          component: () => import('../views/admin/FaqManagement.vue')
        }
      ]
    },
    {
      path: '/adym/login',
      name: 'admin-login',
      component: () => import('../views/admin/AdminLogin.vue')
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Try to fetch user if not checked yet
  if (!authStore.isAuthenticated && to.meta.requiresAuth) {
    await authStore.fetchUser()
    if (!authStore.isAuthenticated) {
      if (to.meta.requiresAdmin) {
        next('/adym/login')
      } else {
        next('/login')
      }
      return
    }
  }

  // Check admin permission
  if (to.meta.requiresAdmin && authStore.user && !authStore.user.is_staff && !authStore.user.is_superuser) {
    next('/') // Redirect non-admins to home
    return
  }

  // Redirect logged-in users away from login pages
  if (to.name === 'login' && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }

  if (to.name === 'admin-login' && authStore.isAuthenticated) {
    if (authStore.user.is_staff || authStore.user.is_superuser) {
      next('/adym/dashboard')
      return
    }
  }

  next()
})

// Log visits
import api from '@/utils/api'

router.afterEach((to) => {
  // Only log if authenticated - check local storage or store
  // We can't easily access store here without potential circular dep issues depending on setup,
  // but we can check token validity simply
  const token = localStorage.getItem('auth_token')
  if (token && to.path && !to.path.startsWith('/adym')) {
    // Send log request
    // Use fire-and-forget
    api.post('/adym/log-visit/', { path: to.fullPath }).catch(() => { })
  }
})

export default router
