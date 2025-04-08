import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // Import your router
import vuetify from './plugins/vuetify';
import '@mdi/font/css/materialdesignicons.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'animate.css';
import '@fortawesome/fontawesome-free/css/all.min.css';



const app = createApp(App);
app.use(router); // Use the router
app.use(vuetify)
app.mount('#app');