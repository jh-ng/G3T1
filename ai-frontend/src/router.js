import { createRouter, createWebHistory } from 'vue-router'
import TravelForm from './components/TravelForm.vue'
import ItineraryPage from './views/ItineraryPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: TravelForm
  },
  {
    path: '/itinerary',
    name: 'Itinerary',
    component: ItineraryPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 