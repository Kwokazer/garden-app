<!-- frontend/src/features/questions/components/QuestionCard.vue -->
<template>
  <div class="question-card card h-100 border-0 shadow-sm">
    <div class="card-body d-flex">
      <!-- Панель голосования -->
      <div class="voting-section me-3">
        <VotingButtons
          type="question"
          :item-id="question.id"
          :votes-up="question.votes_up"
          :votes-down="question.votes_down"
          :user-vote="question.user_vote"
          :is-loading="isVoting"
          :author-id="question.author_id"
          @vote="handleVote"
        />
      </div>
      
      <!-- Основное содержимое вопроса -->
      <div class="question-content flex-grow-1">
        <!-- Заголовок и статус -->
        <div class="d-flex justify-content-between align-items-start mb-2">
          <router-link 
            :to="{ name: 'QuestionDetails', params: { id: question.id } }"
            class="question-title-link"
          >
            <h5 class="question-title mb-1">{{ question.title }}</h5>
          </router-link>
          
          <!-- Статус решения -->
          <span 
            v-if="question.is_solved" 
            class="badge bg-success ms-2"
            title="Вопрос решен"
          >
            <i class="bi bi-check-circle me-1"></i>
            Решен
          </span>
        </div>
        
        <!-- Превью содержимого -->
        <p class="question-preview text-muted mb-3">
          {{ getQuestionPreview(question.body) }}
        </p>
        
        <!-- Метаинформация -->
        <div class="question-meta d-flex flex-wrap align-items-center">
          <!-- Связанное растение -->
          <router-link
            v-if="question.plant && question.plant.id"
            :to="{ name: 'PlantDetails', params: { id: question.plant.id } }"
            class="plant-link me-3 mb-2"
          >
            <span class="badge bg-primary">
              <i class="bi bi-flower1 me-1"></i>
              {{ question.plant.name || 'Растение' }}
            </span>
          </router-link>
          
          <!-- Количество ответов -->
          <span class="answers-count me-3 mb-2">
            <i class="bi bi-chat-dots me-1"></i>
            {{ question.answers_count || 0 }} 
            {{ getAnswersText(question.answers_count || 0) }}
          </span>
          
          <!-- Количество просмотров -->
          <span class="views-count me-3 mb-2 text-muted">
            <i class="bi bi-eye me-1"></i>
            {{ question.view_count || 0 }} 
            {{ getViewsText(question.view_count || 0) }}
          </span>
          
          <!-- Автор и дата -->
          <div class="author-info d-flex align-items-center mb-2">
            <small class="text-muted">
              Автор: 
              <span class="author-name">{{ question.author?.username || 'Неизвестно' }}</span>
              <span class="mx-1">•</span>
              <time :datetime="question.created_at" :title="getFullDate(question.created_at)">
                {{ getRelativeTime(question.created_at) }}
              </time>
            </small>
          </div>
        </div>
        
        <!-- Действия (показываются только для автора) -->
        <div v-if="canEdit" class="question-actions mt-3">
          <div class="btn-group" role="group">
            <router-link
              :to="{ name: 'EditQuestion', params: { id: question.id } }"
              class="btn btn-outline-secondary btn-sm"
            >
              <i class="bi bi-pencil me-1"></i>
              Редактировать
            </router-link>
            <button
              class="btn btn-outline-danger btn-sm"
              @click="handleDelete"
              :disabled="isDeleting"
            >
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              <i v-else class="bi bi-trash me-1"></i>
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '../../auth/store/authStore';
import { useQuestionsStore } from '../store/questionsStore';
import VotingButtons from './VotingButtons.vue';

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['vote', 'delete']);

const authStore = useAuthStore();
const questionsStore = useQuestionsStore();

// Состояние компонента
const isVoting = ref(false);
const isDeleting = ref(false);
const isLoading = ref(false);

// Вычисляемые свойства
const canEdit = computed(() => {
  return props.showActions && 
         authStore.isLoggedIn && 
         authStore.user && 
         authStore.user.id === props.question.author_id;
});

// Методы
function getQuestionPreview(body, maxLength = 150) {
  if (!body) return '';
  if (body.length <= maxLength) return body;
  return body.substring(0, maxLength) + '...';
}

function getAnswersText(count) {
  if (count === 0) return 'ответов';
  if (count === 1) return 'ответ';
  if (count >= 2 && count <= 4) return 'ответа';
  return 'ответов';
}

function getViewsText(count) {
  if (count === 0) return 'просмотров';
  if (count === 1) return 'просмотр';
  if (count >= 2 && count <= 4) return 'просмотра';
  return 'просмотров';
}

function getRelativeTime(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now - date;
  const diffInSeconds = Math.floor(diffInMs / 1000);
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);
  
  if (diffInDays > 7) {
    return date.toLocaleDateString('ru-RU');
  } else if (diffInDays > 0) {
    return `${diffInDays} ${diffInDays === 1 ? 'день' : diffInDays <= 4 ? 'дня' : 'дней'} назад`;
  } else if (diffInHours > 0) {
    return `${diffInHours} ${diffInHours === 1 ? 'час' : diffInHours <= 4 ? 'часа' : 'часов'} назад`;
  } else if (diffInMinutes > 0) {
    return `${diffInMinutes} ${diffInMinutes === 1 ? 'минуту' : diffInMinutes <= 4 ? 'минуты' : 'минут'} назад`;
  } else {
    return 'только что';
  }
}

function getFullDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('ru-RU');
}

// Обработка голосования для ВОПРОСОВ
async function handleVote(voteData) {
  isVoting.value = true;
  
  try {
    await questionsStore.voteForQuestion(voteData.itemId, voteData.voteType);
    emit('vote', voteData);
  } catch (error) {
    console.error('Error voting for question:', error);
    alert('Ошибка при голосовании: ' + error.message);
  } finally {
    isVoting.value = false;
  }
}

async function handleDelete() {
  if (isDeleting.value) return;
  
  const confirmed = confirm('Вы уверены, что хотите удалить этот вопрос? Это действие нельзя отменить.');
  if (!confirmed) return;
  
  isDeleting.value = true;
  
  try {
    await questionsStore.deleteQuestion(props.question.id);
    emit('delete', props.question.id);
  } catch (error) {
    console.error('Error deleting question:', error);
    alert('Ошибка при удалении вопроса: ' + error.message);
  } finally {
    isDeleting.value = false;
  }
}
</script>

<style scoped>
.question-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

.voting-section {
  flex-shrink: 0;
}

.question-content {
  min-width: 0;
}

.question-title {
  color: var(--bs-dark);
  margin-bottom: 0;
}

.question-title-link {
  text-decoration: none;
}

.question-title-link:hover .question-title {
  color: var(--bs-primary);
}

.question-preview {
  font-size: 0.95rem;
  line-height: 1.5;
}

.question-meta {
  font-size: 0.875rem;
}

.plant-link {
  text-decoration: none;
}

.plant-link:hover .badge {
  background-color: var(--bs-success) !important;
}

.author-name {
  font-weight: 500;
  color: var(--bs-primary);
}

.question-actions .btn {
  font-size: 0.875rem;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* Мобильная адаптивность */
@media (max-width: 768px) {
  .card-body .d-flex {
    flex-direction: column;
  }
  
  .voting-section {
    align-self: stretch;
    margin-bottom: 1rem;
    margin-right: 0;
  }
  
  .voting-section .voting-buttons {
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }
  
  .question-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .question-actions {
    align-self: stretch;
  }
  
  .question-actions .btn-group {
    width: 100%;
  }
  
  .question-actions .btn {
    flex: 1;
  }
}
</style>