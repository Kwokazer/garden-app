<!-- src/features/auth/views/LoginPage.vue -->
<template>
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow border-0 rounded-3">
            <div class="card-header bg-primary text-white py-3">
              <h4 class="mb-0 text-center">Вход в систему</h4>
            </div>
            <div class="card-body p-4">
              <LoginForm 
                :isLoading="auth.isLoading" 
                :error="auth.error" 
                @submit="handleLogin" 
                @clearError="auth.clearError()"
                @error="setError"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import { useAuthStore } from '../store/authStore.js';
  import LoginForm from '../components/LoginForm.vue';
  
  const route = useRoute();
  const auth = useAuthStore();
  
  onMounted(() => {
    // Очищаем ошибки при монтировании компонента
    auth.clearError();
    
    // Проверяем, есть ли сообщение о необходимости входа
    if (route.query.requiresAuth) {
      auth.error = 'Для доступа к этой странице необходимо войти в систему';
    }
    
    // Проверяем, есть ли сообщение о регистрации
    if (route.query.registered) {
      auth.error = 'Регистрация прошла успешно! Пожалуйста, войдите в систему.';
      auth.error = null; // Это не ошибка, поэтому сразу очищаем
    }
  });
  
  // Устанавливает сообщение об ошибке
  function setError(message) {
    auth.error = message;
  }
  
  // Обрабатывает отправку формы входа
  async function handleLogin(credentials) {
    await auth.login(credentials);
    
    // Редирект происходит в методе login хранилища
    // Если нужно перенаправить на страницу, с которой пользователь пришел, можно использовать:
    // const redirectPath = route.query.redirect || '/dashboard';
    // router.push(redirectPath);
  }
  </script>
  
  <style scoped>
  .card {
    transition: transform 0.3s ease;
  }
  
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
  }
  
  .card-header {
    border-top-left-radius: calc(0.3rem - 1px) !important;
    border-top-right-radius: calc(0.3rem - 1px) !important;
  }
  
  @media (max-width: 576px) {
    .card-body {
      padding: 1.5rem !important;
    }
  }
  </style>