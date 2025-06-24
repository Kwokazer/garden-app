<!-- Updated App.vue with Questions Navigation Link -->
<template>
  <div class="app-container d-flex flex-column min-vh-100">
    <!-- Верхнее меню -->
    <header class="app-header sticky-top">
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
        <div class="container">
          <!-- Логотип -->
          <router-link class="navbar-brand d-flex align-items-center" to="/">
            <i class="bi bi-flower1 me-2"></i>
            <span class="fw-bold">Garden</span>
          </router-link>
          
          <!-- Кнопка мобильной навигации -->
          <button 
            class="navbar-toggler" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#navbarMain" 
            aria-controls="navbarMain" 
            aria-expanded="false" 
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          
          <!-- Навигационные ссылки -->
          <div class="collapse navbar-collapse" id="navbarMain">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <router-link class="nav-link" to="/dashboard" v-if="isLoggedIn">
                  <i class="bi bi-person-circle me-1"></i> Мой профиль
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/plants">
                  <i class="bi bi-flower3 me-1"></i> Растения
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/questions">
                  <i class="bi bi-question-circle me-1"></i> Вопросы и ответы
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/webinars">
                  <i class="bi bi-camera-video me-1"></i> Вебинары
                </router-link>
              </li>
            </ul>
            
            <!-- Правая часть навигации -->
            <div class="d-flex align-items-center">
              <!-- Для авторизованных пользователей -->
              <div class="dropdown" v-if="isLoggedIn">
                <button 
                  class="btn btn-outline-light dropdown-toggle d-flex align-items-center" 
                  type="button" 
                  id="userMenuButton" 
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                >
                  <i class="bi bi-person-circle me-2"></i>
                  {{ username }}
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuButton">
                  <li>
                    <router-link class="dropdown-item" to="/dashboard">
                      <i class="bi bi-person-circle me-2"></i> Мой профиль
                    </router-link>
                  </li>
                  <li>
                    <a class="dropdown-item" href="#settings">
                      <i class="bi bi-gear me-2"></i> Настройки
                    </a>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <a @click.prevent="logout" class="dropdown-item text-danger" href="#">
                      <i class="bi bi-box-arrow-right me-2"></i> Выйти
                    </a>
                  </li>
                </ul>
              </div>
              
              <!-- Для неавторизованных пользователей -->
              <template v-else>
                <router-link to="/login" class="btn btn-outline-light me-2">
                  <i class="bi bi-box-arrow-in-right me-1"></i> Вход
                </router-link>
                <router-link to="/register" class="btn btn-success">
                  <i class="bi bi-person-plus me-1"></i> Регистрация
                </router-link>
              </template>
            </div>
          </div>
        </div>
      </nav>
    </header>
    
    <!-- Основное содержимое -->
    <main class="app-content flex-grow-1 py-4">
      <router-view />
    </main>
    
    <!-- Подвал сайта -->
    <footer class="app-footer bg-dark text-white py-4 mt-auto">
      <div class="container">
        <div class="row gy-4">
          <div class="col-md-4">
            <h5 class="mb-3 text-success">Garden</h5>
            <p class="text-muted mb-0">Приложение для садоводов, которое поможет вам выращивать растения и общаться с единомышленниками.</p>
          </div>
          
          <div class="col-md-4">
            <h5 class="mb-3 text-success">Ссылки</h5>
            <ul class="list-unstyled">
              <li><a href="#" class="link-light text-decoration-none mb-2 d-inline-block">О нас</a></li>
              <li><a href="#" class="link-light text-decoration-none mb-2 d-inline-block">Блог</a></li>
              <li><a href="#" class="link-light text-decoration-none mb-2 d-inline-block">Помощь</a></li>
              <li><a href="#" class="link-light text-decoration-none d-inline-block">Контакты</a></li>
            </ul>
          </div>
          
          <div class="col-md-4">
            <h5 class="mb-3 text-success">Контакты</h5>
            <ul class="list-unstyled text-muted">
              <li class="mb-2"><i class="bi bi-envelope me-2"></i> support@garden-app.com</li>
              <li class="mb-2"><i class="bi bi-telephone me-2"></i> +7 (123) 456-7890</li>
              <li><i class="bi bi-geo-alt me-2"></i> Москва, Россия</li>
            </ul>
            
            <div class="social-links mt-3">
              <a href="#" class="text-white me-3"><i class="bi bi-facebook"></i></a>
              <a href="#" class="text-white me-3"><i class="bi bi-twitter"></i></a>
              <a href="#" class="text-white me-3"><i class="bi bi-instagram"></i></a>
              <a href="#" class="text-white"><i class="bi bi-telegram"></i></a>
            </div>
          </div>
        </div>
        
        <hr class="my-4 bg-secondary">
        
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center">
          <p class="mb-2 mb-md-0">© {{ currentYear }} Garden. Все права защищены.</p>
          <div>
            <a href="#" class="link-light text-decoration-none me-3">Условия использования</a>
            <a href="#" class="link-light text-decoration-none">Политика конфиденциальности</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from './features/auth/store/authStore';

const auth = useAuthStore();
const currentYear = computed(() => new Date().getFullYear());

// Проверка, авторизован ли пользователь
const isLoggedIn = computed(() => auth.isLoggedIn);

// Имя пользователя для отображения в навигации
const username = computed(() => {
  if (auth.user?.first_name) {
    return auth.user.first_name;
  }
  return auth.user?.username || 'Пользователь';
});

// Функция для выхода из системы
async function logout() {
  await auth.logout();
}
</script>

<style>
/* Импортируем Bootstrap Icons в начале стилей */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css");

:root {
  --bs-primary: #28a745;
  --bs-primary-rgb: 40, 167, 69;
  --bs-success: #218838;
  --bs-success-rgb: 33, 136, 56;
}

body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background-color: #f8f9fa;
  color: #333;
}

/* Кастомизация Bootstrap */
.btn-primary {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}

.btn-primary:hover,
.btn-primary:focus,
.btn-primary:active {
  background-color: var(--bs-success) !important;
  border-color: var(--bs-success) !important;
}

.btn-success {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}

.btn-success:hover,
.btn-success:focus,
.btn-success:active {
  background-color: var(--bs-success) !important;
  border-color: var(--bs-success) !important;
}

.bg-primary {
  background-color: var(--bs-primary) !important;
}

.text-primary {
  color: var(--bs-primary) !important;
}

.text-success {
  color: var(--bs-primary) !important;
}

.border-primary {
  border-color: var(--bs-primary) !important;
}

/* Навигация */
.navbar-dark .navbar-nav .nav-link {
  color: rgba(255, 255, 255, 0.8);
  position: relative;
  padding: 0.5rem 1rem;
}

.navbar-dark .navbar-nav .nav-link:hover {
  color: #fff;
}

.navbar-dark .navbar-nav .nav-link::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0.5rem;
  background-color: var(--bs-primary);
  transition: width 0.3s;
}

.navbar-dark .navbar-nav .nav-link:hover::after,
.navbar-dark .navbar-nav .router-link-active::after {
  width: calc(100% - 1rem);
}

/* Эффекты и переходы */
.btn {
  transition: all 0.3s ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.dropdown-menu {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  border: none;
}

.dropdown-item {
  padding: 0.5rem 1rem;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

.dropdown-item.text-danger:hover {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Социальные иконки */
.social-links a {
  font-size: 1.25rem;
  transition: transform 0.3s;
  display: inline-block;
}

.social-links a:hover {
  transform: translateY(-3px);
}
</style>