<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            Вход
          </div>
          <div class="card-body">
            <form @submit.prevent="handleLoginSubmit">
              <div v-if="auth.error" class="alert alert-danger" role="alert">
                {{ auth.error }}
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required :disabled="auth.isLoading">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Пароль</label>
                <input type="password" class="form-control" id="password" v-model="password" required :disabled="auth.isLoading">
              </div>
              <button type="submit" class="btn btn-primary" :disabled="auth.isLoading">
                <span v-if="auth.isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ auth.isLoading ? 'Вход...' : 'Войти' }}
              </button>
            </form>
            <div class="mt-3 text-center">
              <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
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

const email = ref('test@example.com');
const password = ref('password');
const auth = useAuthStore();

onMounted(() => {
  auth.clearError();
});

watch([email, password], () => {
  if (auth.error) {
    auth.clearError();
  }
});

const handleLoginSubmit = async () => {
  if (!email.value || !password.value) {
    auth.error = 'Email и пароль обязательны.'; // Устанавливаем ошибку напрямую в store
    return;
  }
  await auth.login({ email: email.value, password: password.value });
};
</script>

<style scoped>
.alert {
  margin-bottom: 1rem;
}
</style> 