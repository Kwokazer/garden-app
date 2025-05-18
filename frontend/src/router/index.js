// src/router/index.js (updated with question routes)

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../features/auth/store/authStore';

// Import authentication components
import LoginPage from '../features/auth/views/LoginPage.vue';
import RegisterPage from '../features/auth/views/RegisterPage.vue';
import DashboardPage from '../features/auth/views/DashboardPage.vue';

// Import plant components
import PlantsListPage from '../features/plants/views/PlantsListPage.vue';
import PlantDetailsPage from '../features/plants/views/PlantDetailsPage.vue';

// Import question components
import QuestionsListPage from '../features/questions/views/QuestionsListPage.vue';
import QuestionDetailsPage from '../features/questions/views/QuestionDetailsPage.vue';
import CreateQuestionPage from '../features/questions/views/CreateQuestionPage.vue';
import EditQuestionPage from '../features/questions/views/EditQuestionPage.vue';

/**
 * Auth guard function for protected routes
 */
const authGuard = (to, from, next) => {
  // Check for token in localStorage
  const accessToken = localStorage.getItem('accessToken');
  
  // Try to get authentication state from store
  let isAuthenticated = !!accessToken;
  
  // If store is initialized, use it
  if (window.hasOwnProperty('__pinia')) {
    try {
      const authStore = useAuthStore();
      isAuthenticated = authStore.isLoggedIn;
    } catch (error) {
      console.warn('Error accessing auth store:', error);
      // Continue using localStorage check result
    }
  }

  // Check route type and auth state
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Route requires auth but user is not authenticated
    next({ 
      path: '/login', 
      query: { redirect: to.fullPath } // Save address for redirect after login
    });
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // Route for guests only (login, register) but user is already authenticated
    next({ path: '/dashboard' });
  } else {
    // In other cases allow navigation
    next();
  }
};

// Import home page component
import HomePage from '../views/HomePage.vue';

// Define routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: {
      title: 'Garden - приложение для садоводов'
    }
  },
  // Auth routes
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
  // Plant routes
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
    // Dynamic page title based on plant name
    beforeEnter: (to, from, next) => {
      // Load plant name for page title
      const plantsStore = window.hasOwnProperty('__pinia') ? 
        window.__pinia.state.value.plants?.currentPlant?.name : null;
      
      if (plantsStore) {
        to.meta.title = `${plantsStore} - Garden`;
      }
      
      next();
    }
  },
  // Question routes
  {
    path: '/questions',
    name: 'QuestionsList',
    component: QuestionsListPage,
    meta: { 
      title: 'Вопросы и ответы - Garden' 
    }
  },
  {
    path: '/questions/:id',
    name: 'QuestionDetails',
    component: QuestionDetailsPage,
    meta: { 
      title: 'Вопрос - Garden' 
    },
    // Dynamic page title based on question title
    beforeEnter: (to, from, next) => {
      // Attempt to load question title for page title
      const questionsStore = window.hasOwnProperty('__pinia') ? 
        window.__pinia.state.value.questions?.currentQuestion?.title : null;
      
      if (questionsStore) {
        to.meta.title = `${questionsStore} - Garden`;
      }
      
      next();
    }
  },
  {
    path: '/questions/ask',
    name: 'CreateQuestion',
    component: CreateQuestionPage,
    meta: { 
      requiresAuth: true,
      title: 'Задать вопрос - Garden' 
    }
  },
  {
    path: '/questions/:id/edit',
    name: 'EditQuestion',
    component: EditQuestionPage,
    meta: { 
      requiresAuth: true,
      title: 'Редактирование вопроса - Garden' 
    }
  },
  // 404 route for all other addresses
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
  // Smooth scrolling on route navigation
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' };
  }
});

// Register navigation guard
router.beforeEach(authGuard);

// Change page title on navigation
router.afterEach((to) => {
  document.title = to.meta.title || 'Garden - приложение для садоводов';
});

export default router;