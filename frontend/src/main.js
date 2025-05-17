// src/main.js
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import axios from './interceptors/axios';

// Импорт стилей Bootstrap через CDN (или добавить в index.html)
// Импорт CDN происходит в index.html

// Создание экземпляра приложения
const app = createApp(App);

// Добавление глобальных свойств
app.config.globalProperties.$axios = axios;

// Инициализация Pinia (хранилище)
const pinia = createPinia();
app.use(pinia);

// Инициализация маршрутизатора
app.use(router);

// Монтирование приложения
app.mount('#app');