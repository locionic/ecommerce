import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from "axios";
import '@/assets/global.css';

// axios.defaults.baseURL = "http://127.0.0.1:8000"
axios.defaults.baseURL = "https://ecommerce-x3n5.onrender.com"
createApp(App).use(store).use(router).mount('#app')
