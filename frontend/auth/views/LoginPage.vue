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
              <div v-if="auth.getError.value" class="alert alert-danger" role="alert">
                {{ auth.getError.value }}
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required :disabled="auth.getIsLoading.value">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Пароль</label>
                <input type="password" class="form-control" id="password" v-model="password" required :disabled="auth.getIsLoading.value">
              </div>
              <button type="submit" class="btn btn-primary" :disabled="auth.getIsLoading.value">
                <span v-if="auth.getIsLoading.value" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ auth.getIsLoading.value ? 'Вход...' : 'Войти' }}
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
// import { useRouter } from 'vue-router'; // useRouter уже есть в store
import { useAuthStore } from '../store/authStore.js';

const email = ref('test@example.com'); // Предзаполняем для удобства тестирования
const password = ref('password');   // Предзаполняем для удобства тестирования
const auth = useAuthStore();
// const router = useRouter(); // Не нужен, так как store сам управляет редиректом

onMounted(() => {
  auth.clearError(); // Очищаем ошибки при монтировании компонента
});

// Следим за ошибками, чтобы очистить их при изменении полей ввода
watch([email, password], () => {
  if (auth.getError.value) {
    auth.clearError();
  }
});

const handleLoginSubmit = async () => {
  if (!email.value || !password.value) {
    // Можно добавить более специфичную валидацию на клиенте, если нужно
    auth.error.value = 'Email и пароль обязательны.';
    return;
  }
  await auth.login({ email: email.value, password: password.value });
  // Редирект обрабатывается внутри auth.login()
};
</script>

<style scoped>
/* Стили могут быть добавлены здесь */
.alert {
  margin-bottom: 1rem;
}
</style> 