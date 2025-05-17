<!-- src/features/auth/views/RegisterPage.vue -->

<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow border-0 rounded-3">
          <div class="card-header bg-success text-white py-3">
            <h4 class="mb-0 text-center">Регистрация нового пользователя</h4>
          </div>
          <div class="card-body p-4">
            <RegisterForm 
              :isLoading="auth.isLoading" 
              :error="auth.error" 
              @submit="handleRegister" 
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
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/authStore.js';
import RegisterForm from '../components/RegisterForm.vue';

const router = useRouter();
const auth = useAuthStore();

onMounted(() => {
  // Очищаем ошибки при монтировании компонента
  auth.clearError();
});

// Устанавливает сообщение об ошибке
function setError(message) {
  auth.error = message;
}

// Обрабатывает отправку формы регистрации
async function handleRegister(userData) {
  const success = await auth.register(userData);
  
  if (success) {
    // Показываем уведомление об успешной регистрации и перенаправляем на страницу входа
    // с параметром, указывающим на успешную регистрацию
    router.push({
      path: '/login',
      query: { registered: 'true' }
    });
  }
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
  .container {
    padding-left: 10px;
    padding-right: 10px;
  }
  
  .card-body {
    padding: 1.5rem !important;
  }
}
</style>