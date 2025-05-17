<!-- src/features/auth/components/RegisterForm.vue -->

<template>
    <form @submit.prevent="handleSubmit" class="auth-form">
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>
      
      <div class="mb-3">
        <label for="username" class="form-label">Имя пользователя</label>
        <input 
          type="text" 
          class="form-control" 
          id="username" 
          v-model="formData.username" 
          required 
          :disabled="isLoading"
          autocomplete="username"
          placeholder="Придумайте имя пользователя"
        >
        <small class="form-text text-muted">
          Используйте латинские буквы, цифры, символы _ и -. Длина от 3 до 50 символов.
        </small>
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
            autocomplete="new-password"
            placeholder="Придумайте надежный пароль"
          >
          <button 
            type="button" 
            class="btn btn-outline-secondary" 
            @click="togglePasswordVisibility"
          >
            <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
          </button>
        </div>
        <div class="password-strength mt-2" v-if="formData.password">
          <div class="progress" style="height: 5px;">
            <div 
              class="progress-bar" 
              :class="passwordStrengthClass" 
              :style="{width: passwordStrength.score * 25 + '%'}"
            ></div>
          </div>
          <small class="form-text" :class="{'text-danger': passwordStrength.score < 2, 'text-warning': passwordStrength.score === 2, 'text-success': passwordStrength.score > 2}">
            {{ passwordStrength.message }}
          </small>
        </div>
        <small class="form-text text-muted" v-else>
          Минимум 8 символов, включая буквы, цифры и специальные символы.
        </small>
      </div>
      
      <div class="mb-3">
        <label for="confirmPassword" class="form-label">Подтвердите пароль</label>
        <input 
          :type="showPassword ? 'text' : 'password'"
          class="form-control" 
          id="confirmPassword" 
          v-model="formData.confirmPassword" 
          required 
          :disabled="isLoading"
          autocomplete="new-password"
          placeholder="Повторите пароль"
        >
        <div v-if="formData.password && formData.confirmPassword && formData.password !== formData.confirmPassword" 
             class="text-danger mt-1">
          Пароли не совпадают
        </div>
      </div>
      
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="firstName" class="form-label">Имя (необязательно)</label>
          <input 
            type="text" 
            class="form-control" 
            id="firstName" 
            v-model="formData.firstName" 
            :disabled="isLoading"
            autocomplete="given-name"
            placeholder="Ваше имя"
          >
        </div>
        
        <div class="col-md-6 mb-3">
          <label for="lastName" class="form-label">Фамилия (необязательно)</label>
          <input 
            type="text" 
            class="form-control" 
            id="lastName" 
            v-model="formData.lastName" 
            :disabled="isLoading"
            autocomplete="family-name"
            placeholder="Ваша фамилия"
          >
        </div>
      </div>
      
      <div class="mb-3 form-check">
        <input 
          type="checkbox" 
          class="form-check-input" 
          id="agreeTerms" 
          v-model="formData.agreeTerms"
          required
        >
        <label class="form-check-label" for="agreeTerms">
          Я согласен с <a href="#" target="_blank">условиями использования</a> и <a href="#" target="_blank">политикой конфиденциальности</a>
        </label>
      </div>
      
      <button type="submit" class="btn btn-success w-100" :disabled="isLoading || !isFormValid">
        <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
      
      <div class="mt-3 text-center">
        <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
      </div>
    </form>
  </template>
  
  <script setup>
  import { reactive, ref, computed, watch } from 'vue';
  
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
  
  const emit = defineEmits(['submit', 'clearError', 'error']);
  
  const formData = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    agreeTerms: false
  });
  
  const showPassword = ref(false);
  
  // Валидация пароля
  const passwordStrength = computed(() => {
    const password = formData.password;
    
    if (!password) {
      return { score: 0, message: '' };
    }
    
    let score = 0;
    let message = '';
    
    // Длина
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    
    // Сложность
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    // Максимальный балл - 5, нормализуем до 4
    score = Math.min(4, score);
    
    // Сообщение в зависимости от оценки
    switch (score) {
      case 0:
      case 1:
        message = 'Слишком слабый пароль';
        break;
      case 2:
        message = 'Средний пароль';
        break;
      case 3:
        message = 'Хороший пароль';
        break;
      case 4:
        message = 'Отличный пароль';
        break;
      default:
        message = '';
    }
    
    return { score, message };
  });
  
  // CSS класс для индикатора сложности пароля
  const passwordStrengthClass = computed(() => {
    const score = passwordStrength.value.score;
    
    if (score <= 1) return 'bg-danger';
    if (score === 2) return 'bg-warning';
    if (score === 3) return 'bg-info';
    return 'bg-success';
  });
  
  // Валидация формы
  const isFormValid = computed(() => {
    return (
      formData.username.length >= 3 &&
      formData.email && 
      formData.password.length >= 8 && 
      formData.password === formData.confirmPassword &&
      formData.agreeTerms &&
      passwordStrength.value.score >= 2
    );
  });
  
  // Следим за изменением ошибки для настройки слежения за полями формы
  watch(() => props.error, (newValue) => {
    if (newValue) {
      // Когда есть ошибка, следим за изменениями в полях формы
      const clearErrorOnInput = watch(formData, () => {
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
  
  // Валидация имени пользователя
  function validateUsername(username) {
    // Разрешены только буквы, цифры, - и _
    const regex = /^[a-zA-Z0-9_-]+$/;
    if (!regex.test(username)) {
      return 'Имя пользователя может содержать только латинские буквы, цифры, символы _ и -';
    }
    
    if (username.length < 3 || username.length > 50) {
      return 'Имя пользователя должно содержать от 3 до 50 символов';
    }
    
    return null;
  }
  
  // Обработчик отправки формы
  function handleSubmit() {
    // Проверка заполнения обязательных полей
    if (!formData.username || !formData.email || !formData.password) {
      emit('clearError');
      emit('error', 'Все обязательные поля должны быть заполнены.');
      return;
    }
    
    // Проверка имени пользователя
    const usernameError = validateUsername(formData.username);
    if (usernameError) {
      emit('clearError');
      emit('error', usernameError);
      return;
    }
    
    // Проверка совпадения паролей
    if (formData.password !== formData.confirmPassword) {
      emit('clearError');
      emit('error', 'Пароли не совпадают!');
      return;
    }
    
    // Проверка сложности пароля
    if (passwordStrength.value.score < 2) {
      emit('clearError');
      emit('error', 'Пароль слишком слабый. Используйте буквы, цифры и специальные символы.');
      return;
    }
    
    // Отправляем данные формы родительскому компоненту
    emit('submit', { 
      username: formData.username,
      email: formData.email,
      password: formData.password,
      firstName: formData.firstName,
      lastName: formData.lastName
    });
  }
  </script>
  
<style scoped>
  .auth-form {
    max-width: 100%;
    margin: 0 auto;
  }
  
  .form-control:focus {
    box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
    border-color: #28a745;
  }
  
  .btn-success {
    transition: all 0.3s ease;
  }
  
  .btn-success:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .password-strength {
    font-size: 0.85rem;
  }
  </style>