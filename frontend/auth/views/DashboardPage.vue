<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card text-center">
          <div class="card-header">
            Добро пожаловать, {{ authUserDisplay }}!
          </div>
          <div class="card-body">
            <h5 class="card-title">Вы успешно вошли в систему.</h5>
            <p class="card-text">Это страница-заглушка. В будущем здесь будет ваш дашборд.</p>
            <p v-if="auth.authUser.value">
              Ваш Email: {{ auth.authUser.value.email }}
            </p>
            <button @click="handleLogoutClick" class="btn btn-danger" :disabled="auth.getIsLoading.value">
              <span v-if="auth.getIsLoading.value" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ auth.getIsLoading.value ? 'Выход...' : 'Выйти' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// import { useRouter } from 'vue-router'; // Не нужен, store управляет редиректом
import { useAuthStore } from '../store/authStore.js';
import { computed } from 'vue';

const auth = useAuthStore();
// const router = useRouter(); // Не нужен

const authUserDisplay = computed(() => {
  return auth.authUser.value?.username || 'Гость';
});

const handleLogoutClick = async () => {
  await auth.logout();
  // Редирект на /login обрабатывается в auth.logout()
};
</script>

<style scoped>
/* Стили могут быть добавлены здесь */
</style> 