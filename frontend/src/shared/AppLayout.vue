!-- src/shared/components/AppLayout.vue -->

<template>
  <div class="app-container d-flex flex-column min-vh-100">
    <!-- Header -->
    <header class="bg-dark text-white shadow-sm">
      <div class="container">
        <nav class="navbar navbar-expand-lg navbar-dark">
          <div class="container-fluid px-0">
            <router-link class="navbar-brand d-flex align-items-center" to="/">
              <i class="bi bi-flower1 me-2 fs-4"></i>
              <span class="fw-bold">Garden</span>
            </router-link>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
              <ul class="navbar-nav me-auto">
                <li class="nav-item" v-if="isLoggedIn">
                  <router-link class="nav-link" to="/dashboard">Дашборд</router-link>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">База растений</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">Вопросы и ответы</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" href="#">Вебинары</a>
                </li>
              </ul>
              
              <div class="d-flex">
                <template v-if="isLoggedIn">
                  <div class="dropdown">
                    <button class="btn btn-dark dropdown-toggle" type="button" id="profileDropdown"
                            data-bs-toggle="dropdown" aria-expanded="false">
                      <i class="bi bi-person-circle me-1"></i>
                      {{ username }}
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="profileDropdown">
                      <li><router-link class="dropdown-item" to="/dashboard">Профиль</router-link></li>
                      <li><a class="dropdown-item" href="#">Настройки</a></li>
                      <li><hr class="dropdown-divider"></li>
                      <li><a class="dropdown-item text-danger" href="#" @click.prevent="logout">Выйти</a></li>
                    </ul>
                  </div>
                </template>
                <template v-else>
                  <router-link to="/login" class="btn btn-outline-light me-2">Вход</router-link>
                  <router-link to="/register" class="btn btn-primary">Регистрация</router-link>
                </template>
              </div>
            </div>
          </div>
        </nav>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="flex-grow-1">
      <slot></slot>
    </main>
    
    <!-- Footer -->
    <footer class="bg-dark text-white py-4 mt-5">
      <div class="container">
        <div class="row">
          <div class="col-md-4 mb-3 mb-md-0">
            <h5 class="mb-3">Garden</h5>
            <p class="text-muted mb-0">Приложение для садоводов, которое поможет вам выращивать растения и общаться с единомышленниками.</p>
          </div>
          
          <div class="col-md-4 mb-3 mb-md-0">
            <h5 class="mb-3">Ссылки</h5>
            <ul class="list-unstyled">
              <li><a href="#" class="text-reset">О нас</a></li>
              <li><a href="#" class="text-reset">Блог</a></li>
              <li><a href="#" class="text-reset">Контакты</a></li>
              <li><a href="#" class="text-reset">Помощь</a></li>
            </ul>
          </div>
          
          <div class="col-md-4">
            <h5 class="mb-3">Контакты</h5>
            <ul class="list-unstyled text-muted">
              <li><i class="bi bi-envelope me-1"></i> support@garden-app.com</li>
              <li><i class="bi bi-telephone me-1"></i> +7 (123) 456-7890</li>
              <li><i class="bi bi-geo-alt me-1"></i> Москва, Россия</li>
            </ul>
          </div>
        </div>
        
        <hr class="my-4">
        
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-center">
          <p class="mb-2 mb-md-0">© {{ currentYear }} Garden. Все права защищены.</p>
          <div class="social-links">
            <a href="#" class="me-3 text-reset"><i class="bi bi-facebook"></i></a>
            <a href="#" class="me-3 text-reset"><i class="bi bi-twitter-x"></i></a>
            <a href="#" class="me-3 text-reset"><i class="bi bi-instagram"></i></a>
            <a href="#" class="text-reset"><i class="bi bi-telegram"></i></a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '../../features/auth/store/authStore';

const auth = useAuthStore();
const currentYear = computed(() => new Date().getFullYear());

const isLoggedIn = computed(() => auth.isLoggedIn);
const username = computed(() => auth.authUser?.username || 'Пользователь');

function logout() {
  auth.logout();
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

/* Стилизация ссылок в футере */
footer a {
  text-decoration: none;
  transition: color 0.2s;
}

footer a:hover {
  color: white !important;
}

.social-links a {
  font-size: 1.25rem;
}

/* Анимация при наведении на элементы навигации */
.nav-link {
  position: relative;
  transition: color 0.3s;
}

.nav-link:after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: var(--bs-primary);
  transition: width 0.3s;
}

.nav-link:hover:after,
.nav-link.active:after {
  width: 100%;
}
</style>