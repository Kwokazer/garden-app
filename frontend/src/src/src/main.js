// src/main.js

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import axios from '@/interceptors/axios';

// Импорт стилей Bootstrap
import 'bootstrap/dist/css/bootstrap.css';

// Создание экземпляра приложения
const app = createApp(App);

// Добавление глобальных свойств
app.config.globalProperties.$axios = axios;

// Инициализация Pinia (хранилище) ПЕРЕД роутером
// Это важно для корректной работы навигационных guard'ов
const pinia = createPinia();
app.use(pinia);

// Инициализация маршрутизатора
app.use(router);

// Монтирование приложения
app.mount('#app');

// После монтирования подключаем необходимые скрипты Bootstrap
// для работы интерактивных компонентов (dropdown, modal и т.д.)
import('bootstrap/dist/js/bootstrap.bundle.min.js');