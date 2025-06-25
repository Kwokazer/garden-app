<template>
  <div class="webinars-list">
    <!-- Фильтры -->
    <div class="webinars-list__filters">
      <div class="filters-row">
        <div class="filter-group">
          <label for="title-search">Поиск по названию:</label>
          <input
            id="title-search"
            v-model="filters.title"
            type="text"
            placeholder="Введите название вебинара..."
            class="filter-input"
            @input="debouncedSearch"
          />
        </div>
        
        <div class="filter-group">
          <label for="status-filter">Статус:</label>
          <select id="status-filter" v-model="filters.status" class="filter-select" @change="applyFilters">
            <option value="">Все статусы</option>
            <option value="SCHEDULED">Запланированные</option>
            <option value="LIVE">В эфире</option>
            <option value="ENDED">Завершенные</option>
            <option value="CANCELLED">Отмененные</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="public-filter">Доступность:</label>
          <select id="public-filter" v-model="filters.is_public" class="filter-select" @change="applyFilters">
            <option value="">Все</option>
            <option :value="true">Публичные</option>
            <option :value="false">Приватные</option>
          </select>
        </div>
        
        <button @click="clearFilters" class="btn btn--outline">
          Очистить фильтры
        </button>
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка вебинаров...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadWebinars" class="btn btn--primary">
        Попробовать снова
      </button>
    </div>

    <!-- Пустой список -->
    <div v-else-if="webinars.length === 0" class="empty-state">
      <div class="empty-icon">📺</div>
      <h3>Вебинары не найдены</h3>
      <p>Попробуйте изменить параметры поиска или создайте новый вебинар</p>
      <router-link 
        v-if="canCreateWebinar" 
        to="/webinars/create" 
        class="btn btn--primary"
      >
        Создать вебинар
      </router-link>
    </div>

    <!-- Список вебинаров -->
    <div v-else class="webinars-grid">
      <WebinarCard
        v-for="webinar in webinars"
        :key="webinar.id"
        :webinar="webinar"
        :is-loading="isLoading"
        @join="handleJoinWebinar"
        @register="handleRegisterWebinar"
        @unregister="handleUnregisterWebinar"
        @edit="handleEditWebinar"
        @delete="handleDeleteWebinar"
      />
    </div>

    <!-- Пагинация -->
    <div v-if="pagination.total_pages > 1" class="pagination">
      <button
        @click="goToPage(pagination.page - 1)"
        :disabled="pagination.page <= 1"
        class="pagination__btn"
      >
        ← Предыдущая
      </button>
      
      <div class="pagination__info">
        Страница {{ pagination.page }} из {{ pagination.total_pages }}
        ({{ pagination.total_items }} вебинаров)
      </div>
      
      <button
        @click="goToPage(pagination.page + 1)"
        :disabled="pagination.page >= pagination.total_pages"
        class="pagination__btn"
      >
        Следующая →
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useWebinarsStore } from '../store/webinarsStore'
import { useAuthStore } from '@/features/auth/store/authStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { useConfirm } from '@/composables/useConfirm'
import WebinarCard from './WebinarCard.vue'

export default {
  name: 'WebinarsList',
  components: {
    WebinarCard
  },
  setup() {
    const router = useRouter()
    const webinarsStore = useWebinarsStore()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    const { confirmDelete, confirmAction } = useConfirm()
    
    const filters = ref({
      title: '',
      status: '',
      is_public: ''
    })
    
    let searchTimeout = null
    
    // Computed properties
    const webinars = computed(() => webinarsStore.getWebinars)
    const isLoading = computed(() => webinarsStore.getIsLoading)
    const error = computed(() => webinarsStore.getError)
    const pagination = computed(() => webinarsStore.getPagination)
    
    const canCreateWebinar = computed(() => {
      const user = authStore.getUser
      if (!user) return false
      return user.roles?.some(role => ['admin', 'plant_expert'].includes(role))
    })
    
    // Methods
    const loadWebinars = async (page = 1) => {
      await webinarsStore.loadWebinars(page)
    }
    
    const applyFilters = async () => {
      const filterData = {}
      
      if (filters.value.title) filterData.title = filters.value.title
      if (filters.value.status) filterData.status = filters.value.status
      if (filters.value.is_public !== '') filterData.is_public = filters.value.is_public
      
      await webinarsStore.updateFilters(filterData)
    }
    
    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        applyFilters()
      }, 500)
    }
    
    const clearFilters = async () => {
      filters.value = {
        title: '',
        status: '',
        is_public: ''
      }
      await webinarsStore.clearFilters()
    }
    
    const goToPage = async (page) => {
      if (page >= 1 && page <= pagination.value.total_pages) {
        await loadWebinars(page)
      }
    }
    
    const handleJoinWebinar = async (webinarId) => {
      try {
        await router.push(`/webinars/${webinarId}/join`)
      } catch (error) {
        console.error('Error navigating to webinar:', error)
      }
    }

    const handleRegisterWebinar = async (webinarId) => {
      try {
        await webinarsStore.registerForWebinar(webinarId)
        notificationStore.success(
          'Регистрация успешна!',
          'Вы успешно зарегистрированы на вебинар'
        )
      } catch (error) {
        console.error('Error registering for webinar:', error)
        notificationStore.error(
          'Ошибка регистрации',
          error.message || 'Не удалось зарегистрироваться на вебинар'
        )
      }
    }

    const handleUnregisterWebinar = async (webinarId) => {
      const confirmed = await confirmAction(
        'Отменить регистрацию?',
        'Вы уверены, что хотите отменить регистрацию на этот вебинар?',
        'Отменить регистрацию'
      )

      if (confirmed) {
        try {
          await webinarsStore.unregisterFromWebinar(webinarId)
          notificationStore.success(
            'Регистрация отменена',
            'Вы больше не зарегистрированы на этот вебинар'
          )
        } catch (error) {
          console.error('Error unregistering from webinar:', error)
          notificationStore.error(
            'Ошибка отмены регистрации',
            error.message || 'Не удалось отменить регистрацию'
          )
        }
      }
    }

    const handleEditWebinar = async (webinarId) => {
      try {
        await router.push(`/webinars/${webinarId}/edit`)
      } catch (error) {
        console.error('Error navigating to edit webinar:', error)
      }
    }
    
    const handleDeleteWebinar = async (webinarId) => {
      const confirmed = await confirmDelete(
        'Это действие нельзя будет отменить. Все данные вебинара будут удалены.'
      )

      if (confirmed) {
        try {
          await webinarsStore.deleteWebinar(webinarId)
          notificationStore.success(
            'Вебинар удален',
            'Вебинар был успешно удален'
          )
        } catch (error) {
          console.error('Error deleting webinar:', error)
          notificationStore.error(
            'Ошибка удаления',
            error.message || 'Не удалось удалить вебинар'
          )
        }
      }
    }
    
    // Lifecycle
    onMounted(() => {
      loadWebinars()
    })
    
    return {
      filters,
      webinars,
      isLoading,
      error,
      pagination,
      canCreateWebinar,
      loadWebinars,
      applyFilters,
      debouncedSearch,
      clearFilters,
      goToPage,
      handleJoinWebinar,
      handleRegisterWebinar,
      handleUnregisterWebinar,
      handleEditWebinar,
      handleDeleteWebinar
    }
  }
}
</script>

<style scoped>
.webinars-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.webinars-list__filters {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.filters-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 16px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
}

.filter-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: #e53e3e;
}

.empty-state .empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #2d3748;
  margin-bottom: 8px;
}

.empty-state p {
  color: #718096;
  margin-bottom: 24px;
}

.webinars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.pagination__btn {
  padding: 8px 16px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination__btn:hover:not(:disabled) {
  background-color: #3182ce;
}

.pagination__btn:disabled {
  background-color: #e2e8f0;
  color: #a0aec0;
  cursor: not-allowed;
}

.pagination__info {
  color: #4a5568;
  font-size: 0.875rem;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
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
  background-color: #28a745;
  color: white;
}

.btn--primary:hover {
  background-color: #218838;
}

.btn--outline {
  background-color: transparent;
  color: #28a745;
  border: 1px solid #28a745;
}

.btn--outline:hover {
  background-color: #28a745;
  color: white;
}

@media (max-width: 768px) {
  .filters-row {
    grid-template-columns: 1fr;
  }
  
  .webinars-grid {
    grid-template-columns: 1fr;
  }
  
  .pagination {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
