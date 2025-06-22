<template>
  <div class="webinar-view">
    <!-- Загрузка -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка вебинара...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">❌</div>
      <h2>Вебинар не найден</h2>
      <p>{{ error }}</p>
      <router-link to="/webinars" class="btn btn--primary">
        Вернуться к списку вебинаров
      </router-link>
    </div>

    <!-- Контент вебинара -->
    <div v-else-if="webinar" class="webinar-content">
      <!-- Хлебные крошки -->
      <nav class="breadcrumb">
        <router-link to="/webinars" class="breadcrumb-link">Вебинары</router-link>
        <span class="breadcrumb-separator">→</span>
        <span class="breadcrumb-current">{{ webinar.title }}</span>
      </nav>

      <!-- Заголовок вебинара -->
      <div class="webinar-header">
        <div class="header-main">
          <h1 class="webinar-title">{{ webinar.title }}</h1>
          <div class="webinar-status" :class="`status--${webinar.status.toLowerCase()}`">
            {{ getStatusText(webinar.status) }}
          </div>
        </div>
        
        <div class="webinar-meta">
          <div class="meta-item">
            <span class="meta-label">Ведущий:</span>
            <span class="meta-value">{{ webinar.host.username }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Дата:</span>
            <span class="meta-value">{{ formatDate(webinar.scheduled_at) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Длительность:</span>
            <span class="meta-value">{{ webinar.duration_minutes }} мин</span>
          </div>
          <div class="meta-item" v-if="webinar.participants_count">
            <span class="meta-label">Участников:</span>
            <span class="meta-value">{{ webinar.participants_count }}</span>
          </div>
        </div>

        <div v-if="webinar.description" class="webinar-description">
          <p>{{ webinar.description }}</p>
        </div>

        <div v-if="webinar.plant_topic" class="webinar-topic">
          <span class="topic-label">Тема:</span>
          <span class="topic-value">🌿 {{ webinar.plant_topic.name }}</span>
        </div>
      </div>

      <!-- Действия -->
      <div class="webinar-actions">
        <button
          v-if="canJoin && !isJoined"
          @click="joinWebinar"
          :disabled="isJoining"
          class="btn btn--primary btn--large"
        >
          <span v-if="isJoining" class="loading-spinner"></span>
          {{ webinar.status === 'LIVE' ? 'Присоединиться к вебинару' : 'Подключиться к вебинару' }}
        </button>

        <button
          v-if="isJoined"
          @click="leaveWebinar"
          class="btn btn--danger btn--large"
        >
          Покинуть вебинар
        </button>

        <router-link
          v-if="canEdit"
          :to="`/webinars/${webinar.id}/edit`"
          class="btn btn--secondary"
        >
          Редактировать
        </router-link>

        <button
          v-if="canDelete"
          @click="deleteWebinar"
          class="btn btn--danger"
        >
          Удалить
        </button>
      </div>

      <!-- Jitsi Meet интеграция -->
      <div v-if="isJoined && jitsiConfig && jwtToken" class="jitsi-section">
        <JitsiMeet
          :webinar-id="webinar.id"
          :webinar-title="webinar.title"
          :jitsi-config="jitsiConfig"
          :jwt-token="jwtToken"
          @connected="onJitsiConnected"
          @disconnected="onJitsiDisconnected"
          @error="onJitsiError"
          @leave="leaveWebinar"
        />
      </div>

      <!-- Информация о вебинаре -->
      <div v-if="!isJoined" class="webinar-info">
        <div class="info-section">
          <h3>О вебинаре</h3>
          <div class="info-grid">
            <div class="info-item">
              <strong>Статус:</strong>
              <span :class="`status-text--${webinar.status.toLowerCase()}`">
                {{ getStatusText(webinar.status) }}
              </span>
            </div>
            <div class="info-item">
              <strong>Доступ:</strong>
              <span>{{ webinar.is_public ? 'Публичный' : 'Приватный' }}</span>
            </div>
            <div class="info-item" v-if="webinar.max_participants">
              <strong>Макс. участников:</strong>
              <span>{{ webinar.max_participants }}</span>
            </div>
            <div class="info-item">
              <strong>Создан:</strong>
              <span>{{ formatDate(webinar.created_at) }}</span>
            </div>
          </div>
        </div>

        <div v-if="webinar.participants.length > 0" class="participants-section">
          <h3>Участники ({{ webinar.participants.length }})</h3>
          <div class="participants-list">
            <div
              v-for="participant in webinar.participants"
              :key="participant.id"
              class="participant-item"
            >
              <span class="participant-name">{{ participant.user.username }}</span>
              <span class="participant-role" :class="`role--${participant.role.toLowerCase()}`">
                {{ getRoleText(participant.role) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWebinarsStore } from '../store/webinarsStore'
import { useAuthStore } from '@/features/auth/store/authStore'
import JitsiMeet from '../components/JitsiMeet.vue'

export default {
  name: 'WebinarView',
  components: {
    JitsiMeet
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const webinarsStore = useWebinarsStore()
    const authStore = useAuthStore()
    
    const isLoading = ref(true)
    const error = ref(null)
    const isJoining = ref(false)
    const isJoined = ref(false)
    const jitsiConfig = ref(null)
    const jwtToken = ref(null)
    
    // Computed properties
    const webinar = computed(() => webinarsStore.getCurrentWebinar)
    const user = computed(() => authStore.getUser)
    
    const canJoin = computed(() => {
      if (!webinar.value || !user.value) return false
      return webinar.value.status === 'SCHEDULED' || webinar.value.status === 'LIVE'
    })
    
    const canEdit = computed(() => {
      if (!webinar.value || !user.value) return false
      return user.value.id === webinar.value.host_id || 
             user.value.roles?.some(role => role.name === 'admin')
    })
    
    const canDelete = computed(() => {
      if (!webinar.value || !user.value) return false
      return user.value.id === webinar.value.host_id || 
             user.value.roles?.some(role => role.name === 'admin')
    })
    
    // Methods
    const loadWebinar = async () => {
      const webinarId = route.params.id
      if (!webinarId) {
        error.value = 'ID вебинара не указан'
        isLoading.value = false
        return
      }
      
      try {
        await webinarsStore.loadWebinarById(webinarId)
        if (!webinarsStore.getCurrentWebinar) {
          error.value = 'Вебинар не найден'
        }
      } catch (err) {
        console.error('Error loading webinar:', err)
        error.value = err.message || 'Ошибка загрузки вебинара'
      } finally {
        isLoading.value = false
      }
    }
    
    const joinWebinar = async () => {
      if (!webinar.value || !user.value) return
      
      isJoining.value = true
      try {
        // Получаем данные для подключения к Jitsi
        const connectionData = await webinarsStore.joinWebinar(webinar.value.id)
        
        // Получаем конфигурацию Jitsi
        const config = await webinarsStore.getJitsiConfig(webinar.value.id)
        
        jitsiConfig.value = config
        jwtToken.value = connectionData.jwt_token
        isJoined.value = true
        
      } catch (err) {
        console.error('Error joining webinar:', err)
        alert(err.message || 'Ошибка присоединения к вебинару')
      } finally {
        isJoining.value = false
      }
    }
    
    const leaveWebinar = () => {
      isJoined.value = false
      jitsiConfig.value = null
      jwtToken.value = null
    }
    
    const deleteWebinar = async () => {
      if (!webinar.value) return
      
      if (confirm('Вы уверены, что хотите удалить этот вебинар?')) {
        try {
          await webinarsStore.deleteWebinar(webinar.value.id)
          router.push('/webinars')
        } catch (err) {
          console.error('Error deleting webinar:', err)
          alert(err.message || 'Ошибка удаления вебинара')
        }
      }
    }
    
    const onJitsiConnected = () => {
      console.log('Connected to Jitsi Meet')
    }
    
    const onJitsiDisconnected = () => {
      console.log('Disconnected from Jitsi Meet')
      leaveWebinar()
    }
    
    const onJitsiError = (error) => {
      console.error('Jitsi Meet error:', error)
      alert('Ошибка видеоконференции: ' + error.message)
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        'SCHEDULED': 'Запланирован',
        'LIVE': 'В эфире',
        'ENDED': 'Завершен',
        'CANCELLED': 'Отменен'
      }
      return statusMap[status] || status
    }
    
    const getRoleText = (role) => {
      const roleMap = {
        'HOST': 'Ведущий',
        'MODERATOR': 'Модератор',
        'PARTICIPANT': 'Участник'
      }
      return roleMap[role] || role
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // Lifecycle
    onMounted(() => {
      loadWebinar()
    })
    
    onUnmounted(() => {
      // Очищаем данные при уходе со страницы
      leaveWebinar()
    })
    
    return {
      isLoading,
      error,
      webinar,
      isJoining,
      isJoined,
      jitsiConfig,
      jwtToken,
      canJoin,
      canEdit,
      canDelete,
      joinWebinar,
      leaveWebinar,
      deleteWebinar,
      onJitsiConnected,
      onJitsiDisconnected,
      onJitsiError,
      getStatusText,
      getRoleText,
      formatDate
    }
  }
}
</script>

<style scoped>
.webinar-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-state,
.error-state {
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

.error-icon {
  font-size: 4rem;
  margin-bottom: 16px;
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
}

.breadcrumb-separator {
  color: #a0aec0;
}

.breadcrumb-current {
  color: #4a5568;
  font-weight: 500;
}

.webinar-header {
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.webinar-title {
  color: #1a202c;
  margin: 0;
  flex: 1;
  margin-right: 16px;
}

.webinar-status {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status--scheduled {
  background-color: #e6fffa;
  color: #00695c;
}

.status--live {
  background-color: #ffebee;
  color: #c62828;
  animation: pulse 2s infinite;
}

.status--ended {
  background-color: #f5f5f5;
  color: #757575;
}

.status--cancelled {
  background-color: #fff3e0;
  color: #ef6c00;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.webinar-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-label {
  font-size: 0.875rem;
  color: #718096;
  font-weight: 500;
}

.meta-value {
  color: #2d3748;
  font-weight: 500;
}

.webinar-description {
  margin-bottom: 20px;
  color: #4a5568;
  line-height: 1.6;
}

.webinar-topic {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f0fff4;
  border-radius: 8px;
  border-left: 4px solid #38a169;
}

.topic-label {
  font-weight: 500;
  color: #2f855a;
}

.topic-value {
  color: #38a169;
  font-weight: 500;
}

.webinar-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  flex-wrap: wrap;
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
  gap: 8px;
}

.btn--large {
  padding: 16px 32px;
  font-size: 1.1rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background-color: #4299e1;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: #3182ce;
}

.btn--secondary {
  background-color: #edf2f7;
  color: #4a5568;
}

.btn--secondary:hover {
  background-color: #e2e8f0;
}

.btn--danger {
  background-color: #fed7d7;
  color: #c53030;
}

.btn--danger:hover {
  background-color: #feb2b2;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.jitsi-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 600px;
  margin-bottom: 32px;
}

.webinar-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.info-section,
.participants-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-section h3,
.participants-section h3 {
  color: #1a202c;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.info-item:last-child {
  border-bottom: none;
}

.status-text--live {
  color: #c62828;
  font-weight: 600;
}

.status-text--scheduled {
  color: #00695c;
  font-weight: 600;
}

.participants-list {
  display: grid;
  gap: 8px;
}

.participant-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f7fafc;
  border-radius: 6px;
}

.participant-role {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.role--host {
  background: #fed7d7;
  color: #c53030;
}

.role--moderator {
  background: #bee3f8;
  color: #2b6cb0;
}

.role--participant {
  background: #e6fffa;
  color: #00695c;
}

@media (max-width: 768px) {
  .header-main {
    flex-direction: column;
    gap: 16px;
  }
  
  .webinar-meta {
    grid-template-columns: 1fr;
  }
  
  .webinar-actions {
    flex-direction: column;
  }
  
  .webinar-info {
    grid-template-columns: 1fr;
  }
  
  .jitsi-section {
    height: 400px;
  }
}
</style>
