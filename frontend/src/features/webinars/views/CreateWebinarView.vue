<template>
  <div class="create-webinar-view">
    <!-- Хлебные крошки -->
    <nav class="breadcrumb">
      <router-link to="/webinars" class="breadcrumb-link">Вебинары</router-link>
      <span class="breadcrumb-separator">→</span>
      <span class="breadcrumb-current">Создать вебинар</span>
    </nav>

    <!-- Проверка прав доступа -->
    <div v-if="!canCreateWebinar" class="access-denied">
      <div class="access-denied__icon">🚫</div>
      <h2>Доступ запрещен</h2>
      <p>Только администраторы и эксперты по растениям могут создавать вебинары.</p>
      <router-link to="/webinars" class="btn btn--primary">
        Вернуться к вебинарам
      </router-link>
    </div>

    <!-- Форма создания -->
    <div v-else>
      <WebinarForm
        :is-loading="isLoading"
        @submit="handleCreateWebinar"
        @cancel="handleCancel"
      />

      <!-- Сообщение об ошибке -->
      <div v-if="error" class="error-message">
        <div class="error-content">
          <span class="error-icon">⚠️</span>
          <div>
            <h4>Ошибка создания вебинара</h4>
            <p>{{ error }}</p>
          </div>
        </div>
        <button @click="clearError" class="error-close">×</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWebinarsStore } from '../store/webinarsStore'
import { useAuthStore } from '@/features/auth/store/authStore'
import WebinarForm from '../components/WebinarForm.vue'

export default {
  name: 'CreateWebinarView',
  components: {
    WebinarForm
  },
  setup() {
    const router = useRouter()
    const webinarsStore = useWebinarsStore()
    const authStore = useAuthStore()
    
    const isLoading = ref(false)
    const error = ref(null)
    
    // Computed properties
    const user = computed(() => authStore.getUser)
    
    const canCreateWebinar = computed(() => {
      if (!user.value) return false
      return user.value.roles?.some(role => ['admin', 'plant_expert'].includes(role))
    })
    
    // Methods
    const handleCreateWebinar = async (webinarData) => {
      isLoading.value = true
      error.value = null

      try {
        const newWebinar = await webinarsStore.createWebinar(webinarData)

        // Сразу перенаправляем на страницу созданного вебинара
        if (newWebinar && newWebinar.id) {
          router.push(`/webinars/${newWebinar.id}`)
        } else {
          // Если нет ID, перенаправляем на список вебинаров
          router.push('/webinars')
        }
      } catch (err) {
        console.error('Error creating webinar:', err)
        error.value = err.message || 'Произошла ошибка при создании вебинара'
      } finally {
        isLoading.value = false
      }
    }
    
    const handleCancel = () => {
      router.push('/webinars')
    }
    
    const clearError = () => {
      error.value = null
    }
    
    // Lifecycle
    onMounted(() => {
      // Проверяем авторизацию
      if (!user.value) {
        router.push('/auth/login')
        return
      }
      
      // Проверяем права доступа
      if (!canCreateWebinar.value) {
        // Пользователь увидит сообщение об отказе в доступе
        console.warn('User does not have permission to create webinars')
      }
    })
    
    return {
      isLoading,
      error,
      canCreateWebinar,
      handleCreateWebinar,
      handleCancel,
      clearError
    }
  }
}
</script>

<style scoped>
.create-webinar-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: #4299e1;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #3182ce;
}

.breadcrumb-separator {
  color: #a0aec0;
}

.breadcrumb-current {
  color: #4a5568;
  font-weight: 500;
}

.access-denied {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.access-denied__icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.access-denied h2 {
  color: #e53e3e;
  margin-bottom: 12px;
}

.access-denied p {
  color: #718096;
  margin-bottom: 24px;
}

.btn {
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn--primary {
  background-color: #4299e1;
  color: white;
}

.btn--primary:hover {
  background-color: #3182ce;
}

.btn--secondary {
  background-color: #edf2f7;
  color: #4a5568;
}

.btn--secondary:hover {
  background-color: #e2e8f0;
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #fed7d7;
  border: 1px solid #feb2b2;
  border-radius: 8px;
  padding: 16px;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.error-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.error-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.error-content h4 {
  color: #c53030;
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.error-content p {
  color: #9c4221;
  margin: 0;
  font-size: 0.875rem;
}

.error-close {
  position: absolute;
  top: 8px;
  right: 12px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #c53030;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-close:hover {
  background: rgba(197, 48, 48, 0.1);
  border-radius: 4px;
}

@media (max-width: 768px) {
  .error-message {
    position: relative;
    top: auto;
    right: auto;
    margin-bottom: 20px;
    max-width: none;
  }
}
</style>
