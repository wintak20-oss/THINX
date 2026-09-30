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

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  const user = localStorage.getItem('user')
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !user) {
    // Redirect to login if route requires auth and user is not logged in
    next('/login')
  } else if (!requiresAuth && user && (to.name === 'Login' || to.name === 'Register')) {
    // Redirect to home if user is logged in and trying to access login/register
    next('/')
  } else {
    next()
  }
})

export default router
