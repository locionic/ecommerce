import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from "axios";
import '@/assets/global.scss';

// axios.defaults.baseURL = "http://127.0.0.1:8000"
axios.defaults.baseURL = "https://ecommerce-x3n5.onrender.com"
const app = createApp(App)

app.config.globalProperties.$filters = {
  yyyymmddthhmmsszToNormal(val) {
    const date = new Date(val)
    return `${date.getDate()}/${date.getMonth() +1 }/${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`
  },
  timeAgo(input) {
    const date = (input instanceof Date) ? input : new Date(input);
    const formatter = new Intl.RelativeTimeFormat('en');
    const ranges = {
      years: 3600 * 24 * 365,
      months: 3600 * 24 * 30,
      weeks: 3600 * 24 * 7,
      days: 3600 * 24,
      hours: 3600,
      minutes: 60,
      seconds: 1
    };
    const secondsElapsed = (date.getTime() - Date.now()) / 1000;
    for (let key in ranges) {
      if (ranges[key] < Math.abs(secondsElapsed)) {
        const delta = secondsElapsed / ranges[key];
        return formatter.format(Math.round(delta), key);
      }
    }
    return 'newly added'
  }
}

app.use(store).use(router).mount('#app')

