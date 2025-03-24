import { createRouter, createWebHistory } from 'vue-router'
import MyHome from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: MyHome
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
