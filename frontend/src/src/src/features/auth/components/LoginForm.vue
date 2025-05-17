<!-- src/features/auth/components/LoginForm.vue -->

<template>
    <form @submit.prevent="handleSubmit" class="auth-form">
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>
      
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input 
          type="email" 
          class="form-control" 
          id="email" 
          v-model="formData.email" 
          required 
          :disabled="isLoading"
          autocomplete="email"
          placeholder="Введите ваш email"
        >
      </div>
      
      <div class="mb-3">
        <label for="password" class="form-label">Пароль</label>
        <div class="input-group">
          <input 
            :type="showPassword ? 'text' : 'password'"
            class="form-control" 
            id="password" 
            v-model="formData.password" 
            required 
            :disabled="isLoading"
            autocomplete="current-password"
            placeholder="Введите ваш пароль"
          >
          <button 
            type="button" 
            class="btn btn-outline-secondary" 
            @click="togglePasswordVisibility"
          >
            <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
          </button>
        </div>
      </div>
      
      <div class="mb-3 d-flex justify-content-between align-items-center">
        <div class="form-check">
          <input 
            type="checkbox" 
            class="form-check-input" 
            id="rememberMe" 
            v-model="formData.rememberMe"
          >
          <label class="form-check-label" for="rememberMe">Запомнить меня</label>
        </div>
        <a href="#" class="text-primary">Забыли пароль?</a>
      </div>
      
      <button type="submit" class="btn btn-primary w-100" :disabled="isLoading">
        <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        {{ isLoading ? 'Вход...' : 'Войти' }}
      </button>
      
      <div class="mt-3 text-center">
        <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
      </div>
    </form>
  </template>
  
  <script setup>
  import { reactive, ref, watch } from 'vue';
  
  const props = defineProps({
    isLoading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    }
  });
  
  const emit = defineEmits(['submit', 'clearError']);
  
  const formData = reactive({
    email: '',  // пустые значения для безопасности
    password: '',
    rememberMe: false
  });
  
  const showPassword = ref(false);
  
  // Следим за изменением ошибки для настройки слежения за полями формы
  watch(() => props.error, (newValue) => {
    if (newValue) {
      // Когда есть ошибка, следим за изменениями в полях формы
      const clearErrorOnInput = watch([formData.email, formData.password], () => {
        emit('clearError');
        // Отписываемся от слежения после первого изменения
        clearErrorOnInput();
      });
    }
  });
  
  // Функция переключения видимости пароля
  function togglePasswordVisibility() {
    showPassword.value = !showPassword.value;
  }
  
  // Обработчик отправки формы
  function handleSubmit() {
    if (!formData.email || !formData.password) {
      emit('clearError'); // Сначала очищаем старую ошибку
      emit('error', 'Email и пароль обязательны.');
      return;
    }
    
    // Отправляем данные формы родительскому компоненту
    emit('submit', { 
      email: formData.email, 
      password: formData.password,
      rememberMe: formData.rememberMe
    });
  }
  </script>
  
  <style scoped>
  .auth-form {
    max-width: 100%;
    margin: 0 auto;
  }
  
  .form-control, .input-group {
    position: relative;
  }
  
  .form-control:focus {
    box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
    border-color: #28a745;
  }
  
  .btn-primary {
    transition: all 0.3s ease;
  }
  
  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  </style>