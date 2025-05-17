// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../features/auth/store/authStore';

// Импорт компонентов для маршрутов
import LoginPage from '../features/auth/views/LoginPage.vue';
import RegisterPage from '../features/auth/views/RegisterPage.vue';
import DashboardPage from '../features/auth/views/DashboardPage.vue';

/**
 * Функция проверки аутентификации для защищенных маршрутов
 * @param {Object} to - маршрут назначения
 * @param {Object} from - исходный маршрут
 * @param {Function} next - функция для продолжения навигации
 */
const authGuard = (to, from, next) => {
  // Проверяем наличие токена в localStorage (для случаев, когда хранилище еще не проинициализировано)
  const accessToken = localStorage.getItem('accessToken');
  
  // Пытаемся получить состояние аутентификации из хранилища
  let isAuthenticated = !!accessToken;
  
  // Если хранилище инициализировано, используем его
  if (window.hasOwnProperty('__pinia')) {
    try {
      const authStore = useAuthStore();
      isAuthenticated = authStore.isLoggedIn;
    } catch (error) {
      console.warn('Ошибка доступа к хранилищу аутентификации:', error);
      // Продолжаем использовать результат проверки localStorage
    }
  }

  // Проверяем тип маршрута и состояние аутентификации
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Если маршрут требует аутентификации, но пользователь не авторизован
    next({ 
      path: '/login', 
      query: { redirect: to.fullPath } // Сохраняем адрес для редиректа после входа
    });
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // Если маршрут только для гостей (login, register), но пользователь уже авторизован
    next({ path: '/dashboard' });
  } else {
    // В остальных случаях разрешаем переход
    next();
  }
};

// Определение маршрутов
const routes = [
  {
    path: '/',
    redirect: () => {
      // Если есть токен, перенаправляем на дашборд, иначе на страницу входа
      return localStorage.getItem('accessToken') ? '/dashboard' : '/login';
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { 
      requiresGuest: true,
      title: 'Вход - Garden' 
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { 
      requiresGuest: true,
      title: 'Регистрация - Garden' 
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { 
      requiresAuth: true,
      title: 'Личный кабинет - Garden' 
    }
  },
  // Маршрут для всех остальных адресов (404)
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

// Создание экземпляра маршрутизатора
const router = createRouter({
  history: createWebHistory(),
  routes,
  // Плавная прокрутка при переходе между маршрутами
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' };
  }
});

// Регистрация навигационного guard
router.beforeEach(authGuard);

// Изменение заголовка страницы при навигации
router.afterEach((to) => {
  document.title = to.meta.title || 'Garden - приложение для садоводов';
});

export default router;