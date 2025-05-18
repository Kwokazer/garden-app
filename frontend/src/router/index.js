// src/router/index.js (обновленный)

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../features/auth/store/authStore';

// Импорт аутентификационных компонентов
import LoginPage from '../features/auth/views/LoginPage.vue';
import RegisterPage from '../features/auth/views/RegisterPage.vue';
import DashboardPage from '../features/auth/views/DashboardPage.vue';

// Импорт компонентов растений
import PlantsListPage from '../features/plants/views/PlantsListPage.vue';
import PlantDetailsPage from '../features/plants/views/PlantDetailsPage.vue';

/**
 * Функция проверки аутентификации для защищенных маршрутов
 */
const authGuard = (to, from, next) => {
  // Проверяем наличие токена в localStorage
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

// Импорт компонента домашней страницы
import HomePage from '../views/HomePage.vue';

// Определение маршрутов
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: {
      title: 'Garden - приложение для садоводов'
    }
  },
  // Аутентификационные маршруты
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
  // Маршруты растений
  {
    path: '/plants',
    name: 'PlantsList',
    component: PlantsListPage,
    meta: { 
      title: 'База знаний растений - Garden' 
    }
  },
  {
    path: '/plants/:id',
    name: 'PlantDetails',
    component: PlantDetailsPage,
    meta: { 
      title: 'Информация о растении - Garden' 
    },
    // Динамическое название страницы на основе имени растения
    beforeEnter: (to, from, next) => {
      // Загружаем название растения для заголовка страницы
      const plantsStore = window.hasOwnProperty('__pinia') ? 
        window.__pinia.state.value.plants?.currentPlant?.name : null;
      
      if (plantsStore) {
        to.meta.title = `${plantsStore} - Garden`;
      }
      
      next();
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