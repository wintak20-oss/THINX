import { createRouter, createWebHistory } from 'vue-router'
import WorkflowManager from '../components/WorkflowManager.vue'
import ConnectionManager from '../components/ConnectionManager.vue'
import DataViewer from '../components/DataViewer.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/',
    name: 'Workflow',
    component: WorkflowManager,
    meta: { requiresAuth: true }
  },
  {
    path: '/connections',
    name: 'ConnectionManager',
    component: ConnectionManager,
    meta: { requiresAuth: true }
  },
  {
    path: '/data',
    name: 'DataViewer',
    component: DataViewer,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import api from '../services/api'

// Validate protected navigation against the backend session.
router.beforeEach(async (to) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthPage = to.name === 'Login' || to.name === 'Register'

  if (!requiresAuth && !isAuthPage) {
    return true
  }

  try {
    const result = await api.getCurrentUser()

    if (!result || !result.success || !result.user) {
      localStorage.removeItem('user')
      return requiresAuth ? { name: 'Login', query: { redirect: to.fullPath } } : true
    }

    // Keep the UI cache synchronized with the authenticated server user.
    localStorage.setItem('user', JSON.stringify(result.user))

    if (isAuthPage) {
      return { name: 'Workflow' }
    }

    return true
  } catch (error) {
    localStorage.removeItem('user')

    if (requiresAuth) {
      return { name: 'Login', query: { redirect: to.fullPath } }
    }

    return true
  }
})

export default router
