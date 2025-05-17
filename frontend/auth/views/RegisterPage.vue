<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            Регистрация
          </div>
          <div class="card-body">
            <form @submit.prevent="handleRegisterSubmit">
              <div v-if="auth.getError.value" class="alert alert-danger" role="alert">
                {{ auth.getError.value }}
              </div>
               <div v-if="registrationMessage" class="alert alert-success" role="alert">
                {{ registrationMessage }}
              </div>
              <div class="mb-3">
                <label for="username" class="form-label">Имя пользователя</label>
                <input type="text" class="form-control" id="username" v-model="username" required :disabled="auth.getIsLoading.value">
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required :disabled="auth.getIsLoading.value">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Пароль</label>
                <input type="password" class="form-control" id="password" v-model="password" required :disabled="auth.getIsLoading.value">
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Подтвердите пароль</label>
                <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required :disabled="auth.getIsLoading.value">
              </div>
              <button type="submit" class="btn btn-primary" :disabled="auth.getIsLoading.value">
                <span v-if="auth.getIsLoading.value" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ auth.getIsLoading.value ? 'Регистрация...' : 'Зарегистрироваться' }}
              </button>
            </form>
            <div class="mt-3 text-center">
              <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from '../store/authStore.js';

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const auth = useAuthStore();
const registrationMessage = ref(''); // Для сообщения об успехе

onMounted(() => {
  auth.clearError();
  registrationMessage.value = '';
});

// Следим за ошибками, чтобы очистить их при изменении полей ввода
watch([username, email, password, confirmPassword], () => {
  if (auth.getError.value) {
    auth.clearError();
  }
  if(registrationMessage.value){
    registrationMessage.value = ''; // Очищаем сообщение об успехе при вводе
  }
});

const handleRegisterSubmit = async () => {
  registrationMessage.value = ''; // Очищаем предыдущее сообщение
  if (password.value !== confirmPassword.value) {
    auth.error.value = 'Пароли не совпадают!'; // Устанавливаем ошибку через store
    return;
  }
  if (!username.value || !email.value || !password.value) {
    auth.error.value = 'Все поля обязательны для заполнения.';
    return;
  }

  await auth.register({ 
    username: username.value, 
    email: email.value, 
    password: password.value 
  });

  // Сообщение об успехе или ошибке будет обработано в store и отображено через getError
  // Если регистрация прошла успешно, store перенаправит на /login
  // Можно добавить локальное сообщение об успехе, если API не возвращает его или store не обрабатывает
  if (!auth.getError.value && auth.router.currentRoute.value.path === '/login') {
      // Это условие может быть ненадёжным, т.к. store перенаправляет
      // Лучше положиться на сообщение из store или API
      // В текущей реализации authStore.register показывает alert и редиректит
  }
};
</script>

<style scoped>
/* Стили могут быть добавлены здесь */
.alert {
  margin-bottom: 1rem;
}
</style> 