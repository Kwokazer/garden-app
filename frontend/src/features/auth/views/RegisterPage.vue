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
              <div v-if="auth.error" class="alert alert-danger" role="alert">
                {{ auth.error }}
              </div>
              <div class="mb-3">
                <label for="username" class="form-label">Имя пользователя</label>
                <input type="text" class="form-control" id="username" v-model="username" required :disabled="auth.isLoading">
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required :disabled="auth.isLoading">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Пароль</label>
                <input type="password" class="form-control" id="password" v-model="password" required :disabled="auth.isLoading">
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Подтвердите пароль</label>
                <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required :disabled="auth.isLoading">
              </div>
              <button type="submit" class="btn btn-primary" :disabled="auth.isLoading">
                <span v-if="auth.isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ auth.isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
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

onMounted(() => {
  auth.clearError();
});

watch([username, email, password, confirmPassword], () => {
  if (auth.error) {
    auth.clearError();
  }
});

const handleRegisterSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    auth.error = 'Пароли не совпадают!';
    return;
  }
  if (!username.value || !email.value || !password.value) {
    auth.error = 'Все поля обязательны для заполнения.';
    return;
  }
  await auth.register({ 
    username: username.value, 
    email: email.value, 
    password: password.value 
  });
  // Сообщение об успехе (alert) и редирект обрабатываются в authStore
};
</script>

<style scoped>
.alert {
  margin-bottom: 1rem;
}
</style> 