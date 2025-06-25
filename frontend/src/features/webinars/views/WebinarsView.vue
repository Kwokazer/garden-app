<template>
  <div class="webinars-view">
    <!-- Заголовок страницы -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">Вебинары</h1>
        <p class="page-subtitle">
          Присоединяйтесь к образовательным вебинарам о растениях и садоводстве
        </p>
      </div>
      
      <div class="header-actions">
        <router-link 
          v-if="canCreateWebinar" 
          to="/webinars/create" 
          class="btn btn--primary"
        >
          <span class="btn-icon">+</span>
          Создать вебинар
        </router-link>
      </div>
    </div>

    <!-- Навигационные табы -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="tab"
        :class="{ 'tab--active': activeTab === tab.key }"
      >
        {{ tab.label }}
        <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Контент табов -->
    <div class="tab-content">
      <!-- Сообщение для неавторизованных пользователей -->
      <div v-if="!user" class="empty-state">
        <div class="empty-icon">🔐</div>
        <h3>Войдите в систему</h3>
        <p>Для просмотра вебинаров необходимо войти в систему</p>
        <router-link to="/login" class="btn btn--primary">
          Войти
        </router-link>
      </div>

      <!-- Все вебинары -->
      <div v-else-if="activeTab === 'all'" class="tab-panel">
        <WebinarsList />
      </div>

      <!-- Мои вебинары (ведущий) -->
      <div v-else-if="activeTab === 'hosted'" class="tab-panel">
        <div v-if="isLoadingHosted" class="loading-state">
          <div class="spinner"></div>
          <p>Загрузка ваших вебинаров...</p>
        </div>
        
        <div v-else-if="hostedWebinars.length === 0" class="empty-state">
          <div class="empty-icon">🎯</div>
          <h3>У вас пока нет вебинаров</h3>
          <p>Создайте свой первый вебинар и поделитесь знаниями с сообществом</p>
          <router-link to="/webinars/create" class="btn btn--primary">
            Создать первый вебинар
          </router-link>
        </div>
        
        <div v-else class="webinars-grid">
          <WebinarCard
            v-for="webinar in hostedWebinars"
            :key="webinar.id"
            :webinar="webinar"
            :is-loading="isLoadingHosted"
            @join="handleJoinWebinar"
            @edit="handleEditWebinar"
            @delete="handleDeleteWebinar"
          />
        </div>
      </div>

      <!-- Участвую -->
      <div v-else-if="activeTab === 'participating'" class="tab-panel">
        <div v-if="isLoadingParticipating" class="loading-state">
          <div class="spinner"></div>
          <p>Загрузка вебинаров...</p>
        </div>
        
        <div v-else-if="participatingWebinars.length === 0" class="empty-state">
          <div class="empty-icon">👥</div>
          <h3>Вы пока не участвуете в вебинарах</h3>
          <p>Найдите интересные вебинары и присоединяйтесь к обучению</p>
        </div>
        
        <div v-else class="webinars-grid">
          <WebinarCard
            v-for="webinar in participatingWebinars"
            :key="webinar.id"
            :webinar="webinar"
            :is-loading="isLoadingParticipating"
            @join="handleJoinWebinar"
            @edit="handleEditWebinar"
            @delete="handleDeleteWebinar"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useWebinarsStore } from '../store/webinarsStore'
import { useAuthStore } from '@/features/auth/store/authStore'
import WebinarsList from '../components/WebinarsList.vue'
import WebinarCard from '../components/WebinarCard.vue'

export default {
  name: 'WebinarsView',
  components: {
    WebinarsList,
    WebinarCard
  },
  setup() {
    const router = useRouter()
    const webinarsStore = useWebinarsStore()
    const authStore = useAuthStore()
    
    const isLoadingHosted = ref(false)
    const isLoadingParticipating = ref(false)

    // Computed properties
    const user = computed(() => authStore.getUser)
    const hostedWebinars = computed(() => webinarsStore.getMyHostedWebinars)
    const participatingWebinars = computed(() => webinarsStore.getMyParticipatingWebinars)

    const canCreateWebinar = computed(() => {
      if (!user.value) return false
      return user.value.roles?.some(role => ['admin', 'plant_expert'].includes(role))
    })

    const tabs = computed(() => {
      const baseTabs = []

      if (user.value) {
        // Добавляем вкладку "Все вебинары" для авторизованных пользователей
        baseTabs.push({
          key: 'all',
          label: 'Все вебинары'
        })

        if (canCreateWebinar.value) {
          baseTabs.push({
            key: 'hosted',
            label: 'Мои вебинары',
            count: hostedWebinars.value.length
          })
        }

        baseTabs.push({
          key: 'participating',
          label: 'Участвую',
          count: participatingWebinars.value.length
        })
      }

      return baseTabs
    })

    // Активная вкладка - инициализируем первой доступной
    const activeTab = ref('')

    // Устанавливаем активную вкладку при изменении пользователя
    watch(user, (newUser) => {
      if (newUser && tabs.value.length > 0) {
        activeTab.value = tabs.value[0].key
      }
    }, { immediate: true })
    
    // Methods
    const loadHostedWebinars = async () => {
      if (!canCreateWebinar.value) return
      
      isLoadingHosted.value = true
      try {
        await webinarsStore.loadMyHostedWebinars()
      } catch (error) {
        console.error('Error loading hosted webinars:', error)
      } finally {
        isLoadingHosted.value = false
      }
    }
    
    const loadParticipatingWebinars = async () => {
      if (!user.value) return
      
      isLoadingParticipating.value = true
      try {
        await webinarsStore.loadMyParticipatingWebinars()
      } catch (error) {
        console.error('Error loading participating webinars:', error)
      } finally {
        isLoadingParticipating.value = false
      }
    }
    
    const handleJoinWebinar = async (webinarId) => {
      try {
        await router.push(`/webinars/${webinarId}/join`)
      } catch (error) {
        console.error('Error navigating to webinar:', error)
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
      if (confirm('Вы уверены, что хотите удалить этот вебинар?')) {
        try {
          await webinarsStore.deleteWebinar(webinarId)
          // Обновляем список после удаления
          if (activeTab.value === 'hosted') {
            await loadHostedWebinars()
          }
        } catch (error) {
          console.error('Error deleting webinar:', error)
        }
      }
    }
    
    // Watchers
    watch(activeTab, (newTab) => {
      if (newTab === 'hosted' && hostedWebinars.value.length === 0) {
        loadHostedWebinars()
      } else if (newTab === 'participating' && participatingWebinars.value.length === 0) {
        loadParticipatingWebinars()
      }
    })
    
    // Lifecycle
    onMounted(() => {
      // Загружаем данные для текущего пользователя
      if (user.value) {
        if (canCreateWebinar.value) {
          loadHostedWebinars()
        }
        loadParticipatingWebinars()
      }
    })
    
    return {
      activeTab,
      tabs,
      user,
      canCreateWebinar,
      hostedWebinars,
      participatingWebinars,
      isLoadingHosted,
      isLoadingParticipating,
      handleJoinWebinar,
      handleEditWebinar,
      handleDeleteWebinar
    }
  }
}
</script>

<style scoped>
.webinars-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.header-content h1 {
  color: #1a202c;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #718096;
  margin: 0;
}

.btn {
  padding: 12px 20px;
  border-radius: 6px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn--primary {
  background-color: #28a745;
  color: white;
}

.btn--primary:hover {
  background-color: #218838;
}

.btn-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: #f7fafc;
  padding: 4px;
  border-radius: 8px;
}

.tab {
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #4a5568;
}

.tab:hover {
  background: #edf2f7;
}

.tab--active {
  background: white;
  color: #4299e1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-count {
  background: #e2e8f0;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.tab--active .tab-count {
  background: #bee3f8;
  color: #2b6cb0;
}

.tab-content {
  min-height: 400px;
}

.tab-panel {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-state,
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
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .tabs {
    flex-direction: column;
  }
  
  .webinars-grid {
    grid-template-columns: 1fr;
  }
}
</style>
