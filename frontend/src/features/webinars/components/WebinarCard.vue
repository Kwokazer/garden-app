<template>
  <div class="webinar-card">
    <div class="webinar-card__header">
      <h3 class="webinar-card__title">{{ truncateText(webinar.title, 60) }}</h3>
      <div class="webinar-card__status" :class="`status--${webinar.status.toLowerCase()}`">
        {{ getStatusText(webinar.status) }}
      </div>
    </div>
    
    <div class="webinar-card__content">
      <p class="webinar-card__description" v-if="webinar.description">
        {{ truncateText(webinar.description, 150) }}
      </p>
      
      <div class="webinar-card__meta">
        <div class="webinar-card__host">
          <i class="icon-user"></i>
          <span>{{ webinar.host.username }}</span>
        </div>
        
        <div class="webinar-card__date">
          <i class="icon-calendar"></i>
          <span>{{ formatDate(webinar.scheduled_at) }}</span>
        </div>
        
        <div class="webinar-card__duration">
          <i class="icon-clock"></i>
          <span>{{ webinar.duration_minutes }} мин</span>
        </div>
        
        <div class="webinar-card__participants" v-if="webinar.participants_count">
          <i class="icon-users"></i>
          <span>{{ webinar.participants_count }} участников</span>
        </div>
      </div>
      
      <div class="webinar-card__topic" v-if="webinar.plant_topic">
        <i class="icon-leaf"></i>
        <span>{{ webinar.plant_topic.name }}</span>
      </div>
    </div>
    
    <div class="webinar-card__actions">
      <!-- Кнопка регистрации для запланированных вебинаров -->
      <button
        v-if="canRegister && !isUserRegistered"
        @click="$emit('register', webinar.id)"
        class="btn btn--success"
        :disabled="isLoading"
      >
        Зарегистрироваться
      </button>

      <!-- Кнопка отмены регистрации для зарегистрированных пользователей -->
      <button
        v-if="canUnregister && isUserRegistered"
        @click="$emit('unregister', webinar.id)"
        class="btn btn--warning"
        :disabled="isLoading"
      >
        Отменить регистрацию
      </button>

      <!-- Кнопка присоединения для активных вебинаров -->
      <button
        v-if="canJoin"
        @click="$emit('join', webinar.id)"
        class="btn btn--primary"
        :disabled="isLoading"
      >
        Присоединиться
      </button>

      <button
        v-if="canEdit"
        @click="$emit('edit', webinar.id)"
        class="btn btn--secondary"
      >
        Редактировать
      </button>

      <button
        v-if="canDelete"
        @click="$emit('delete', webinar.id)"
        class="btn btn--danger"
      >
        Удалить
      </button>

      <router-link
        :to="`/webinars/${webinar.id}`"
        class="btn btn--outline"
      >
        Подробнее
      </router-link>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/features/auth/store/authStore'

export default {
  name: 'WebinarCard',
  props: {
    webinar: {
      type: Object,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['join', 'register', 'unregister', 'edit', 'delete'],
  setup(props) {
    const authStore = useAuthStore()

    const canJoin = computed(() => {
      return props.webinar.status === 'LIVE'
    })

    const canRegister = computed(() => {
      const user = authStore.getUser
      if (!user) return false

      // Показываем кнопку регистрации только для запланированных вебинаров
      return props.webinar.status === 'SCHEDULED'
    })

    const canUnregister = computed(() => {
      const user = authStore.getUser
      if (!user) return false

      // Показываем кнопку отмены регистрации только для запланированных вебинаров
      return props.webinar.status === 'SCHEDULED'
    })

    const isUserRegistered = computed(() => {
      const user = authStore.getUser
      if (!user || !props.webinar.participants) return false

      // Проверяем, зарегистрирован ли пользователь на вебинар
      return props.webinar.participants.some(participant => participant.user.id === user.id)
    })
    
    const canEdit = computed(() => {
      const user = authStore.getUser
      if (!user) return false

      return user.id === props.webinar.host_id ||
             user.roles?.some(role => role === 'admin')
    })

    const canDelete = computed(() => {
      const user = authStore.getUser
      if (!user) return false

      return user.id === props.webinar.host_id ||
             user.roles?.some(role => role === 'admin')
    })
    
    const getStatusText = (status) => {
      const statusMap = {
        'SCHEDULED': 'Запланирован',
        'LIVE': 'В эфире',
        'ENDED': 'Завершен',
        'CANCELLED': 'Отменен'
      }
      return statusMap[status] || status
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    return {
      canJoin,
      canRegister,
      canUnregister,
      isUserRegistered,
      canEdit,
      canDelete,
      getStatusText,
      formatDate,
      truncateText
    }
  }
}
</script>

<style scoped>
.webinar-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.webinar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.webinar-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.webinar-card__title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
  flex: 1;
  min-width: 0; /* Позволяет элементу сжиматься */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.webinar-card__status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0; /* Статус не сжимается */
  white-space: nowrap; /* Статус не переносится */
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

.webinar-card__content {
  margin-bottom: 20px;
}

.webinar-card__description {
  color: #4a5568;
  line-height: 1.5;
  margin-bottom: 16px;
}

.webinar-card__meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.webinar-card__meta > div {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #718096;
  font-size: 0.875rem;
}

.webinar-card__topic {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #38a169;
  font-size: 0.875rem;
  font-weight: 500;
}

.webinar-card__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background-color: #28a745;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: #218838;
}

.btn--secondary {
  background-color: #edf2f7;
  color: #4a5568;
}

.btn--secondary:hover {
  background-color: #e2e8f0;
}

.btn--success {
  background-color: #38a169;
  color: white;
}

.btn--success:hover:not(:disabled) {
  background-color: #2f855a;
}

.btn--success:disabled {
  background-color: #68d391;
  cursor: default;
}

.btn--warning {
  background-color: #ed8936;
  color: white;
}

.btn--warning:hover:not(:disabled) {
  background-color: #dd6b20;
}

.btn--danger {
  background-color: #fed7d7;
  color: #c53030;
}

.btn--danger:hover {
  background-color: #feb2b2;
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

/* Иконки (можно заменить на Font Awesome или другие) */
.icon-user::before { content: "👤"; }
.icon-calendar::before { content: "📅"; }
.icon-clock::before { content: "⏰"; }
.icon-users::before { content: "👥"; }
.icon-leaf::before { content: "🌿"; }

@media (max-width: 768px) {
  .webinar-card__header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .webinar-card__title {
    white-space: normal; /* Разрешаем перенос на мобильных */
  }

  .webinar-card__status {
    align-self: flex-start; /* Выравниваем статус по левому краю */
  }

  .webinar-card__meta {
    grid-template-columns: 1fr;
  }

  .webinar-card__actions {
    flex-direction: column;
  }
}
</style>
