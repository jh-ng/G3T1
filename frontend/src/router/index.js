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
    component: () => import('../views/TravelPlanner.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/itinerary',
    name: 'Itinerary',
    component: () => import('../views/Itinerary.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/saved-itineraries',
    name: 'SavedItineraries',
    component: () => import('../views/SavedItineraries.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/saved-itineraries/:id',
    name: 'SavedItineraryDetail',
    component: () => import('../views/SavedItineraryDetail.vue'),
    meta: { requiresAuth: true }
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
