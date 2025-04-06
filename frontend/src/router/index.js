import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/Home.vue'
import MyLogin from '../views/Login.vue'
import MyRegister from '../views/Register.vue'
import authService from '../services/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/login',
    name: 'Login',
    component: MyLogin,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: MyRegister,
    meta: { requiresGuest: true }
  },
  {
    path: '/create-post',
    name: 'CreatePost',
    component: () => import('../views/CreatePost.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: () => import('../views/UserProfile.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/user-preference',
    name: 'UserPreference',
    component: () => import('../views/UserPref.vue'),
    meta: {requiresAuth: true}
  },
  {
    path: '/travel-planner',
    name: 'TravelPlanner',
    component: () => import('../components/TravelForm.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = authService.isAuthenticated();
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next('/');
  } else {
    next();
  }
})

export default router
