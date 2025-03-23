import { createRouter, createWebHistory } from 'vue-router'
import MyHome from '../views/Home.vue'
import Landing from '../views/LandingView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MyHome
  },
  {
    path: '/landing',
    name: 'Landing',
    component: Landing
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
